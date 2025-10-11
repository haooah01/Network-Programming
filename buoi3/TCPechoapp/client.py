#!/usr/bin/env python3
"""TCP Echo Client supporting line and length-prefixed modes."""
from __future__ import annotations

import argparse
import socket
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

EXIT_SOCKET_CREATE = 10
EXIT_CONNECT_FAILURE = 20
EXIT_IO_ERROR = 30
EXIT_PROTOCOL_ERROR = 40
EXIT_UTF8_WARNING = 41

BUFFER_SIZE = 4096


def _now_ts() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


class Logger:
    def __init__(self, debug: bool = False) -> None:
        self.debug = debug

    def info(self, message: str, **extra: object) -> None:
        self._log("INFO", message, extra)

    def error(self, message: str, **extra: object) -> None:
        self._log("ERROR", message, extra)

    def debug_dump(self, label: str, data: bytes) -> None:
        if not self.debug:
            return
        preview = data[:64]
        self._log("DEBUG", f"{label} size={len(data)} hex={preview.hex()}")

    def _log(self, level: str, message: str, extra: Optional[dict[str, object]] = None) -> None:
        suffix = ""
        if extra:
            bits = " ".join(f"{key}={value}" for key, value in extra.items())
            if bits:
                suffix = f" {bits}"
        print(f"{_now_ts()} {level} {message}{suffix}", flush=True)


@dataclass
class ClientConfig:
    host: str
    port: int
    mode: str
    timeout: float
    input_mode: str
    text: Optional[str]
    path: Optional[Path]
    retry_count: int
    retry_backoff: float
    debug: bool


def parse_args(argv: list[str]) -> ClientConfig:
    parser = argparse.ArgumentParser(description="TCP echo client")
    parser.add_argument("--host", default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8080, help="Server port (default: 8080)")
    parser.add_argument("--mode", choices=["line", "len"], default="line", help="Framing mode")
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Socket timeout for connect and I/O in seconds",
    )
    parser.add_argument(
        "--input",
        choices=["inline", "stdin", "file"],
        default="inline",
        help="Input source",
    )
    parser.add_argument("--text", help="Inline text when --input inline")
    parser.add_argument("--path", type=Path, help="File path when --input file")
    parser.add_argument(
        "--retry-count",
        type=int,
        default=3,
        help="Connection retry attempts (default: 3)",
    )
    parser.add_argument(
        "--retry-backoff",
        type=float,
        default=0.3,
        help="Base backoff in seconds between retries (default: 0.3)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable hex previews in logs")
    args = parser.parse_args(argv)

    if args.input == "inline" and args.text is None:
        parser.error("--text is required when --input inline")
    if args.input == "file" and args.path is None:
        parser.error("--path is required when --input file")

    return ClientConfig(
        host=args.host,
        port=args.port,
        mode=args.mode,
        timeout=args.timeout,
        input_mode=args.input,
        text=args.text,
        path=args.path,
        retry_count=max(args.retry_count, 1),
        retry_backoff=max(args.retry_backoff, 0.0),
        debug=args.debug,
    )


def read_inline_payload(config: ClientConfig) -> bytes:
    assert config.text is not None
    return config.text.encode("utf-8")


def read_stdin_payload() -> bytes:
    data = sys.stdin.read()
    return data.encode("utf-8")


def read_file_payload(config: ClientConfig) -> bytes:
    assert config.path is not None
    try:
        text = config.path.read_text(encoding="utf-8")
    except OSError as err:
        print(f"Failed to read file: {err}", file=sys.stderr)
        sys.exit(EXIT_IO_ERROR)
    except UnicodeDecodeError as err:
        print(
            f"File is not valid UTF-8 (offset {err.start}). Provide UTF-8 text for --input file.",
            file=sys.stderr,
        )
        sys.exit(EXIT_PROTOCOL_ERROR)
    return text.encode("utf-8")


def prepare_payload(config: ClientConfig) -> bytes:
    if config.input_mode == "inline":
        payload = read_inline_payload(config)
    elif config.input_mode == "stdin":
        payload = read_stdin_payload()
    else:
        payload = read_file_payload(config)

    if config.mode == "line" and not payload.endswith(b"\n"):
        payload += b"\n"
    return payload


def connect_with_retry(config: ClientConfig, logger: Logger) -> socket.socket:
    attempt = 0
    last_error: Optional[Exception] = None
    while attempt < config.retry_count:
        try:
            logger.info("Connecting", host=config.host, port=config.port, attempt=attempt + 1)
            conn = socket.create_connection((config.host, config.port), timeout=config.timeout)
            conn.settimeout(config.timeout)
            return conn
        except OSError as err:
            last_error = err
            logger.error("Connect failed", error=err)
            attempt += 1
            if attempt < config.retry_count:
                sleep_for = config.retry_backoff * attempt
                time.sleep(sleep_for)
    logger.error("Giving up after retries", attempts=config.retry_count, error=last_error)
    sys.exit(EXIT_CONNECT_FAILURE)


def send_payload(conn: socket.socket, payload: bytes, config: ClientConfig, logger: Logger) -> None:
    if config.mode == "line":
        frame = payload
    else:
        frame = len(payload).to_bytes(4, "big") + payload
    logger.debug_dump("send", frame)
    total_sent = 0
    while total_sent < len(frame):
        try:
            sent = conn.send(frame[total_sent:])
        except socket.timeout as err:
            logger.error("Send timeout", error=err)
            sys.exit(EXIT_IO_ERROR)
        except OSError as err:
            logger.error("Send failed", error=err)
            sys.exit(EXIT_IO_ERROR)
        if sent == 0:
            logger.error("Socket closed during send")
            sys.exit(EXIT_IO_ERROR)
        total_sent += sent
    logger.info("Payload sent", bytes=len(frame))


def recv_line(conn: socket.socket) -> bytes:
    buffer = bytearray()
    while True:
        try:
            chunk = conn.recv(BUFFER_SIZE)
        except socket.timeout as err:
            raise TimeoutError("Receive timeout") from err
        except OSError as err:
            raise ConnectionError("Receive failed") from err
        if not chunk:
            raise ConnectionError("Connection closed before newline")
        buffer.extend(chunk)
        idx = buffer.find(b"\n")
        if idx != -1:
            idx += 1
            return bytes(buffer[:idx])


def recv_length_prefixed(conn: socket.socket) -> bytes:
    header = bytearray()
    while len(header) < 4:
        try:
            chunk = conn.recv(4 - len(header))
        except socket.timeout as err:
            raise TimeoutError("Receive timeout") from err
        except OSError as err:
            raise ConnectionError("Receive failed") from err
        if not chunk:
            raise ConnectionError("Connection closed before length header")
        header.extend(chunk)
    length = int.from_bytes(header, "big")
    if length < 0:
        raise ProtocolError("Negative length announced")
    remaining = length
    payload = bytearray()
    while remaining:
        try:
            chunk = conn.recv(min(BUFFER_SIZE, remaining))
        except socket.timeout as err:
            raise TimeoutError("Receive timeout") from err
        except OSError as err:
            raise ConnectionError("Receive failed") from err
        if not chunk:
            raise ConnectionError("Connection closed before payload completed")
        payload.extend(chunk)
        remaining -= len(chunk)
    return bytes(header + payload)


class ProtocolError(Exception):
    pass


def receive_response(conn: socket.socket, config: ClientConfig, logger: Logger) -> Tuple[bytes, bytes]:
    if config.mode == "line":
        frame = recv_line(conn)
        payload = frame
    else:
        frame = recv_length_prefixed(conn)
        payload = frame[4:]
    logger.debug_dump("recv", frame)
    logger.info("Received response", bytes=len(frame), payload=len(payload))
    return payload, frame


def display_payload(payload: bytes) -> None:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as err:
        preview = payload[:32].hex()
        print(
            f"UTF-8 decode error at byte offset {err.start}; showing hex preview: {preview} (len={len(payload)})",
            file=sys.stderr,
        )
        sys.exit(EXIT_UTF8_WARNING)
    try:
        print(text, end="")
    except UnicodeEncodeError:
        sys.stdout.buffer.write(text.encode("utf-8"))
        sys.stdout.flush()


def main(argv: list[str]) -> None:
    config = parse_args(argv)
    logger = Logger(debug=config.debug)
    payload = prepare_payload(config)

    conn = connect_with_retry(config, logger)
    try:
        send_payload(conn, payload, config, logger)
        echo_payload, _raw = receive_response(conn, config, logger)
    except TimeoutError as err:
        logger.error("Timeout", error=err)
        sys.exit(EXIT_IO_ERROR)
    except ConnectionError as err:
        logger.error("I/O error", error=err)
        sys.exit(EXIT_IO_ERROR)
    except ProtocolError as err:
        logger.error("Protocol error", error=err)
        sys.exit(EXIT_PROTOCOL_ERROR)
    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        conn.close()

    display_payload(echo_payload)


if __name__ == "__main__":
    main(sys.argv[1:])

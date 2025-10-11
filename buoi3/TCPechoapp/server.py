#!/usr/bin/env python3
"""TCP Echo Server fulfilling UTF-8, framing, and error handling requirements."""
from __future__ import annotations

import argparse
import os
import signal
import socket
import sys
import threading
import time
from dataclasses import dataclass
from typing import Optional

EXIT_SOCKET_CREATE = 10
EXIT_BIND_FAILURE = 11
EXIT_LISTEN_ACCEPT_FAILURE = 12
EXIT_CONNECT_FAILURE = 20  # maintained for table consistency
EXIT_IO_ERROR = 30
EXIT_PROTOCOL_ERROR = 40
EXIT_UTF8_WARNING = 41  # informational only for server

BUFFER_SIZE = 4096

def _now_ts() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


class Logger:
    """Thread-safe stdout logger with simple timestamped messages."""

    def __init__(self, debug: bool = False) -> None:
        self._lock = threading.Lock()
        self.debug = debug

    def info(self, message: str, **extra: object) -> None:
        self._log("INFO", message, extra)

    def error(self, message: str, **extra: object) -> None:
        self._log("ERROR", message, extra)

    def debug_dump(self, label: str, data: bytes) -> None:
        if not self.debug:
            return
        preview = data[:64]
        hex_preview = preview.hex()
        self._log("DEBUG", f"{label} size={len(data)} hex={hex_preview}")

    def _log(self, level: str, message: str, extra: Optional[dict[str, object]] = None) -> None:
        suffix = ""
        if extra:
            kv = " ".join(f"{key}={value}" for key, value in extra.items())
            if kv:
                suffix = f" {kv}"
        line = f"{_now_ts()} {level} {message}{suffix}"
        with self._lock:
            print(line, flush=True)


@dataclass
class ServerConfig:
    host: str
    port: int
    mode: str
    timeout: float
    max_bytes: int
    max_clients: Optional[int]
    debug: bool


def parse_args(argv: list[str]) -> ServerConfig:
    parser = argparse.ArgumentParser(description="TCP echo server")
    parser.add_argument("--host", default="0.0.0.0", help="Interface to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind (default: 8080)")
    parser.add_argument("--mode", choices=["line", "len"], default="line", help="Framing mode")
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Socket timeout per client in seconds (default: 30)",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=1_048_576,
        help="Maximum payload per message in bytes (default: 1048576)",
    )
    parser.add_argument(
        "--max-clients",
        type=int,
        default=None,
        help="Limit concurrent clients (optional)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable hex preview logging")
    args = parser.parse_args(argv)
    return ServerConfig(
        host=args.host,
        port=args.port,
        mode=args.mode,
        timeout=args.timeout,
        max_bytes=args.max_bytes,
        max_clients=args.max_clients,
        debug=args.debug,
    )


def create_socket(logger: Logger, config: ServerConfig) -> socket.socket:
    try:
        addrinfo_list = socket.getaddrinfo(
            config.host, config.port, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
        )
    except socket.gaierror as err:
        logger.error("Address resolution failed", host=config.host, port=config.port, error=err)
        sys.exit(EXIT_SOCKET_CREATE)

    sock = None
    last_error: Optional[Exception] = None
    for family, socktype, proto, _canon, sockaddr in addrinfo_list:
        try:
            sock = socket.socket(family, socktype, proto)
            # Reuse address for quick restarts on Unix-like systems.
            if hasattr(socket, "SO_REUSEADDR"):
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(sockaddr)
            sock.listen()
            sock.settimeout(1.0)  # short timeout to allow graceful shutdown checks
            logger.info("Server bound", host=sockaddr[0], port=sockaddr[1])
            return sock
        except OSError as err:
            last_error = err
            if sock is not None:
                sock.close()
            continue

    logger.error("Unable to bind to requested host/port", host=config.host, port=config.port, error=last_error)
    sys.exit(EXIT_BIND_FAILURE)


class ProtocolError(Exception):
    """Raised when the incoming data violates framing or size requirements."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


def send_all(conn: socket.socket, data: bytes) -> None:
    total_sent = 0
    length = len(data)
    while total_sent < length:
        try:
            sent = conn.send(data[total_sent:])
        except socket.timeout as err:
            raise TimeoutError("Send timeout") from err
        except OSError as err:  # includes ConnectionResetError
            raise ConnectionError("Send failed") from err
        if sent == 0:
            raise ConnectionError("Socket connection broken during send")
        total_sent += sent


def read_exact(conn: socket.socket, count: int) -> Optional[bytes]:
    """Read exactly count bytes, returning None if EOF before any bytes were read."""
    chunks: list[bytes] = []
    bytes_read = 0
    while bytes_read < count:
        try:
            chunk = conn.recv(count - bytes_read)
        except socket.timeout as err:
            raise TimeoutError("Receive timeout") from err
        except OSError as err:
            raise ConnectionError("Receive failed") from err
        if not chunk:
            if bytes_read == 0:
                return None
            raise ConnectionError("Connection closed mid-message")
        chunks.append(chunk)
        bytes_read += len(chunk)
    return b"".join(chunks)


def handle_line_mode(conn: socket.socket, config: ServerConfig, logger: Logger, remote: str) -> None:
    buffer = bytearray()
    while True:
        try:
            chunk = conn.recv(BUFFER_SIZE)
        except socket.timeout as err:
            raise TimeoutError("Receive timeout") from err
        except OSError as err:
            raise ConnectionError("Receive failed") from err
        if not chunk:
            if buffer:
                raise ConnectionError("Peer closed connection mid-line")
            return
        buffer.extend(chunk)
        if len(buffer) > config.max_bytes + 1:  # allow newline
            send_error_line_too_long(conn)
            raise ProtocolError("Line exceeds configured max bytes")
        while True:
            idx = buffer.find(b"\n")
            if idx == -1:
                break
            message = bytes(buffer[: idx + 1])
            del buffer[: idx + 1]
            logger.debug_dump("recv", message)
            send_all(conn, message)
            logger.debug_dump("send", message)
            logger.info(
                "Echoed line",
                remote=remote,
                bytes=len(message),
            )


def send_error_line_too_long(conn: socket.socket) -> None:
    try:
        msg = b"ERR 413 Line Too Long\n"
        send_all(conn, msg)
    except Exception:
        # Ignore secondary failures while trying to surface an error.
        pass


def handle_length_prefixed_mode(
    conn: socket.socket, config: ServerConfig, logger: Logger, remote: str
) -> None:
    while True:
        header = read_exact(conn, 4)
        if header is None:
            return
        length = int.from_bytes(header, "big", signed=False)
        if length > config.max_bytes:
            logger.error("Length exceeds max", remote=remote, length=length)
            raise ProtocolError("Length exceeds configured max bytes")
        payload = read_exact(conn, length)
        if payload is None:
            raise ConnectionError("Connection closed before payload was fully received")
        message = header + payload
        logger.debug_dump("recv", message)
        send_all(conn, message)
        logger.debug_dump("send", message)
        logger.info("Echoed frame", remote=remote, bytes=len(message), payload=length)


def handle_client(
    conn: socket.socket,
    addr: tuple[str, int],
    config: ServerConfig,
    logger: Logger,
    semaphore: Optional[threading.Semaphore],
) -> None:
    remote = f"{addr[0]}:{addr[1]}"
    start = time.monotonic()
    try:
        conn.settimeout(config.timeout)
        if config.mode == "line":
            handle_line_mode(conn, config, logger, remote)
        else:
            handle_length_prefixed_mode(conn, config, logger, remote)
    except TimeoutError as err:
        logger.error("Timeout", remote=remote, error=err)
    except ProtocolError as err:
        logger.error("Protocol error", remote=remote, error=err)
    except ConnectionError as err:
        logger.error("Connection error", remote=remote, error=err)
    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        conn.close()
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.info("Connection closed", remote=remote, duration_ms=duration_ms)
        if semaphore is not None:
            semaphore.release()


def serve_forever(config: ServerConfig, logger: Logger) -> None:
    sock = create_socket(logger, config)
    stop_event = threading.Event()
    semaphore = threading.Semaphore(config.max_clients) if config.max_clients else None
    active_threads: list[threading.Thread] = []

    def signal_handler(_sig: int, _frame) -> None:
        logger.info("Received shutdown signal")
        stop_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, signal_handler)

    try:
        while not stop_event.is_set():
            try:
                conn, addr = sock.accept()
            except socket.timeout:
                continue
            except OSError as err:
                logger.error("Accept failed", error=err)
                sys.exit(EXIT_LISTEN_ACCEPT_FAILURE)

            if semaphore is not None:
                semaphore.acquire()

            thread = threading.Thread(
                target=handle_client,
                args=(conn, addr, config, logger, semaphore),
                daemon=True,
            )
            thread.start()
            active_threads.append(thread)
    finally:
        sock.close()
        for thread in active_threads:
            thread.join(timeout=1.0)


def main(argv: list[str]) -> None:
    config = parse_args(argv)
    logger = Logger(debug=config.debug)
    try:
        serve_forever(config, logger)
    except KeyboardInterrupt:
        # Already handled via signal, ensure graceful exit.
        pass


if __name__ == "__main__":
    main(sys.argv[1:])

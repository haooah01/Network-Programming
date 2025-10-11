# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""End-to-end tests for the TCP echo application."""
from __future__ import annotations

import contextlib
import socket
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List

ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = ROOT / "server.py"
CLIENT_PATH = ROOT / "client.py"
PYTHON = sys.executable
EXIT_UTF8_WARNING = 41


@dataclass
class TestResult:
    name: str
    passed: bool
    detail: str = ""


class ServerProcess:
    def __init__(self, mode: str, port: int, timeout: float = 5.0, max_bytes: int = 131072) -> None:
        self.mode = mode
        self.port = port
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.process: subprocess.Popen[str] | None = None
        self.stdout: str = ""
        self.stderr: str = ""

    def __enter__(self) -> "ServerProcess":
        args = [
            PYTHON,
            str(SERVER_PATH),
            "--host",
            "127.0.0.1",
            "--port",
            str(self.port),
            "--mode",
            self.mode,
            "--timeout",
            str(self.timeout),
            "--max-bytes",
            str(self.max_bytes),
        ]
        self.process = subprocess.Popen(
            args,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        wait_for_port("127.0.0.1", self.port, deadline=time.time() + 3.0)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.process is None:
            return
        self.process.terminate()
        try:
            self.stdout, self.stderr = self.process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.stdout, self.stderr = self.process.communicate(timeout=2)


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_for_port(host: str, port: int, deadline: float) -> None:
    while time.time() < deadline:
        with contextlib.suppress(OSError):
            with socket.create_connection((host, port), timeout=0.2):
                return
        time.sleep(0.05)
    raise RuntimeError(f"Server on {host}:{port} did not become ready")


def send_line(host: str, port: int, payload: bytes) -> bytes:
    with socket.create_connection((host, port), timeout=5.0) as conn:
        conn.settimeout(5.0)
        conn.sendall(payload)
        data = bytearray()
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                raise RuntimeError("Connection closed before newline")
            data.extend(chunk)
            idx = data.find(b"\n")
            if idx != -1:
                return bytes(data[: idx + 1])


def send_len(host: str, port: int, payload: bytes) -> bytes:
    frame = len(payload).to_bytes(4, "big") + payload
    with socket.create_connection((host, port), timeout=5.0) as conn:
        conn.settimeout(5.0)
        conn.sendall(frame)
        header = bytearray()
        while len(header) < 4:
            chunk = conn.recv(4 - len(header))
            if not chunk:
                raise RuntimeError("Connection closed before header echoed")
            header.extend(chunk)
        length = int.from_bytes(header, "big")
        data = bytearray()
        remaining = length
        while remaining:
            chunk = conn.recv(min(remaining, 4096))
            if not chunk:
                raise RuntimeError("Connection closed before payload echoed")
            data.extend(chunk)
            remaining -= len(chunk)
    return bytes(header + data)


def run_line_mode_tests() -> Iterable[TestResult]:
    results: List[TestResult] = []
    port = find_free_port()
    with ServerProcess("line", port) as _server:
        try:
            response = send_line("127.0.0.1", port, b"Hello\n")
            results.append(TestResult("line_ascii", response == b"Hello\n"))

            response = send_line("127.0.0.1", port, "Hi TCP 😀!\n".encode("utf-8"))
            results.append(TestResult("line_unicode", response == "Hi TCP 😀!\n".encode("utf-8")))

            response = send_line("127.0.0.1", port, b"\n")
            results.append(TestResult("line_empty", response == b"\n"))

            long_payload = ("A" * 8000 + "\n").encode("utf-8")
            response = send_line("127.0.0.1", port, long_payload)
            results.append(TestResult("line_long", response == long_payload))

            with socket.create_connection(("127.0.0.1", port), timeout=5.0) as conn:
                conn.sendall(b"partial message without newline")
            response = send_line("127.0.0.1", port, b"Ping\n")
            results.append(TestResult("line_recovery", response == b"Ping\n"))
        except Exception as err:  # noqa: BLE001
            results.append(TestResult("line_mode_exception", False, detail=str(err)))
    return results


def run_length_mode_tests() -> Iterable[TestResult]:
    results: List[TestResult] = []
    port = find_free_port()
    with ServerProcess("len", port, max_bytes=262144) as _server:
        try:
            payload = b"Hello length"
            header = len(payload).to_bytes(4, "big")
            response = send_len("127.0.0.1", port, payload)
            results.append(TestResult("len_ascii", response == header + payload))

            payload = "Hi TCP 😀!".encode("utf-8")
            header = len(payload).to_bytes(4, "big")
            response = send_len("127.0.0.1", port, payload)
            results.append(TestResult("len_unicode", response == header + payload))

            payload = b""
            header = len(payload).to_bytes(4, "big")
            response = send_len("127.0.0.1", port, payload)
            results.append(TestResult("len_zero", response == header + payload))

            payload = b"B" * 65536
            header = len(payload).to_bytes(4, "big")
            response = send_len("127.0.0.1", port, payload)
            results.append(TestResult("len_large", response == header + payload))

            payload = bytes([0x80, 0x81, 0x82, 0xFF])
            header = len(payload).to_bytes(4, "big")
            response = send_len("127.0.0.1", port, payload)
            results.append(TestResult("len_invalid_utf8", response == header + payload))

            frame = (300000).to_bytes(4, "big") + b"X" * 10
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=5.0) as conn:
                    conn.settimeout(5.0)
                    try:
                        conn.sendall(frame)
                        conn.shutdown(socket.SHUT_WR)
                        closed = conn.recv(1)
                        success = closed == b""
                        detail = "" if success else "Server kept connection open"
                    except ConnectionResetError:
                        success = True
                        detail = "Connection reset (expected)"
                    except OSError as send_err:
                        success = False
                        detail = str(send_err)
            except Exception as err:  # noqa: BLE001
                results.append(TestResult("len_too_large", False, detail=str(err)))
            else:
                results.append(TestResult("len_too_large", success, detail=detail))
        except Exception as err:
            results.append(TestResult("len_mode_exception", False, detail=str(err)))
    return results


def run_timeout_test() -> Iterable[TestResult]:
    results: List[TestResult] = []
    port = find_free_port()
    with ServerProcess("line", port, timeout=1.0) as _server:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=5.0) as conn:
                conn.sendall(b"no newline yet")
                time.sleep(1.5)
                conn.settimeout(0.5)
                try:
                    data = conn.recv(1)
                    success = data == b""
                    detail = "" if success else "Data still readable"
                except ConnectionResetError:
                    success = True
                    detail = "Connection reset (expected)"
                except socket.timeout:
                    success = False
                    detail = "Socket still open after timeout"
                except OSError as err:
                    success = False
                    detail = str(err)
                results.append(TestResult("timeout_enforced", success, detail=detail))
        except Exception as err:
            results.append(TestResult("timeout_exception", False, detail=str(err)))
    return results


def run_concurrency_test() -> Iterable[TestResult]:
    results: List[TestResult] = []
    port = find_free_port()
    with ServerProcess("line", port, timeout=5.0, max_bytes=65536) as _server:
        errors: List[str] = []

        def worker(idx: int) -> None:
            payload = f"msg-{idx}\n".encode("utf-8")
            try:
                response = send_line("127.0.0.1", port, payload)
                if response != payload:
                    errors.append(f"Mismatch for worker {idx}")
            except Exception as err:  # noqa: BLE001
                errors.append(f"Worker {idx} error: {err}")

        threads = [threading.Thread(target=worker, args=(i,), daemon=True) for i in range(16)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        results.append(TestResult("concurrency", not errors, detail=", ".join(errors)))
    return results


def run_client_hex_preview_test() -> Iterable[TestResult]:
    results: List[TestResult] = []
    port = find_free_port()
    stop_event = threading.Event()

    def invalid_utf8_server() -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("127.0.0.1", port))
            srv.listen()
            srv.settimeout(0.5)
            while not stop_event.is_set():
                try:
                    conn, _addr = srv.accept()
                except socket.timeout:
                    continue
                with conn:
                    conn.settimeout(2.0)
                    with contextlib.suppress(Exception):
                        conn.recv(4096)
                        frame = b"\x00\x00\x00\x04" + b"\xff\xfe\xfd\xfc"
                        conn.sendall(frame)

    thread = threading.Thread(target=invalid_utf8_server, daemon=True)
    thread.start()
    wait_for_port("127.0.0.1", port, deadline=time.time() + 2.0)

    try:
        result = subprocess.run(
            [
                PYTHON,
                str(CLIENT_PATH),
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--mode",
                "len",
                "--input",
                "inline",
                "--text",
                "trigger",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        condition = result.returncode == EXIT_UTF8_WARNING and "UTF-8 decode error" in result.stderr
        detail = result.stderr.strip()
        results.append(TestResult("client_hex_preview", condition, detail=detail))
    finally:
        stop_event.set()
        thread.join(timeout=1.0)

    return results


TEST_GROUPS: List[Callable[[], Iterable[TestResult]]] = [
    run_line_mode_tests,
    run_length_mode_tests,
    run_timeout_test,
    run_concurrency_test,
    run_client_hex_preview_test,
]


def main() -> None:
    results: List[TestResult] = []
    for group in TEST_GROUPS:
        results.extend(group())

    failed = [r for r in results if not r.passed]
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        detail = f" ({result.detail})" if result.detail else ""
        print(f"[{status}] {result.name}{detail}")

    if failed:
        print(f"Test failures: {len(failed)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Simple benchmark load generator for the TCP echo server."""
from __future__ import annotations

import argparse
import socket
import threading
import time
from statistics import mean

BUFFER_SIZE = 4096


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Echo server benchmark")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--mode", choices=["line", "len"], default="line")
    parser.add_argument("--count", type=int, default=1000, help="Total requests to send")
    parser.add_argument("--concurrency", type=int, default=10, help="Parallel client workers")
    parser.add_argument("--payload", default="benchmark", help="Message to send")
    parser.add_argument("--timeout", type=float, default=5.0)
    return parser.parse_args()


def send_line(host: str, port: int, payload: bytes, timeout: float) -> float:
    start = time.perf_counter()
    with socket.create_connection((host, port), timeout=timeout) as conn:
        conn.settimeout(timeout)
        message = payload if payload.endswith(b"\n") else payload + b"\n"
        conn.sendall(message)
        data = bytearray()
        while True:
            chunk = conn.recv(BUFFER_SIZE)
            if not chunk:
                raise RuntimeError("Connection closed before newline")
            data.extend(chunk)
            if b"\n" in chunk:
                break
    return time.perf_counter() - start


def send_len(host: str, port: int, payload: bytes, timeout: float) -> float:
    frame = len(payload).to_bytes(4, "big") + payload
    start = time.perf_counter()
    with socket.create_connection((host, port), timeout=timeout) as conn:
        conn.settimeout(timeout)
        conn.sendall(frame)
        header = bytearray()
        while len(header) < 4:
            chunk = conn.recv(4 - len(header))
            if not chunk:
                raise RuntimeError("Connection closed before header")
            header.extend(chunk)
        remaining = int.from_bytes(header, "big")
        while remaining:
            chunk = conn.recv(min(BUFFER_SIZE, remaining))
            if not chunk:
                raise RuntimeError("Connection closed before payload")
            remaining -= len(chunk)
    return time.perf_counter() - start


def worker(
    host: str,
    port: int,
    mode: str,
    payload: bytes,
    timeout: float,
    iterations: int,
    latencies: list[float],
    latency_lock: threading.Lock,
    errors: list[str],
    error_lock: threading.Lock,
) -> None:
    send_fn = send_line if mode == "line" else send_len
    for _ in range(iterations):
        try:
            latency = send_fn(host, port, payload, timeout)
            with latency_lock:
                latencies.append(latency)
        except Exception as err:  # noqa: BLE001 - collect error text
            with error_lock:
                errors.append(str(err))


def main() -> None:
    args = parse_args()
    total = max(1, args.count)
    concurrency = max(1, args.concurrency)
    per_worker = total // concurrency
    remainder = total % concurrency
    payload = args.payload.encode("utf-8")

    latencies: list[float] = []
    errors: list[str] = []
    latency_lock = threading.Lock()
    error_lock = threading.Lock()
    threads: list[threading.Thread] = []

    for idx in range(concurrency):
        iterations = per_worker + (1 if idx < remainder else 0)
        if iterations == 0:
            continue
        thread = threading.Thread(
            target=worker,
            args=(
                args.host,
                args.port,
                args.mode,
                payload,
                args.timeout,
                iterations,
                latencies,
                latency_lock,
                errors,
                error_lock,
            ),
            daemon=True,
        )
        threads.append(thread)

    start = time.perf_counter()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    duration = time.perf_counter() - start

    completed = len(latencies)
    if latencies:
        avg_ms = mean(latencies) * 1000
        p95_index = max(0, int(len(latencies) * 0.95) - 1)
        p95_ms = sorted(latencies)[p95_index] * 1000
    else:
        avg_ms = 0.0
        p95_ms = 0.0

    print(f"Completed {completed}/{total} requests in {duration:.2f}s")
    print(f"Average latency: {avg_ms:.2f} ms | p95: {p95_ms:.2f} ms")
    print(f"Errors: {len(errors)}")
    if errors:
        for err in errors[:5]:
            print(f"  - {err}")


if __name__ == "__main__":
    main()

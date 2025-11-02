#!/usr/bin/env python3
"""
run_with_local_server.py

Start a simple TCP sink server locally and run tcp_optimizer.py against it.
This script is intended for quick verification on a single machine.
"""
from __future__ import annotations

import socket
import threading
import time
import subprocess
import sys
import os


def start_sink_server(host: str, port: int) -> threading.Thread:
    stop_event = threading.Event()

    def server_thread() -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((host, port))
            srv.listen()
            srv.settimeout(1.0)
            print(f"Sink server listening on {host}:{port}")
            while not stop_event.is_set():
                try:
                    conn, addr = srv.accept()
                except socket.timeout:
                    continue
                except Exception:
                    break

                threading.Thread(target=handle_conn, args=(conn, addr), daemon=True).start()

    def handle_conn(conn: socket.socket, addr) -> None:
        with conn:
            try:
                while True:
                    data = conn.recv(64 * 1024)
                    if not data:
                        break
            except Exception:
                pass

    t = threading.Thread(target=server_thread, daemon=True)
    t.start()

    # attach stop_event to thread object for convenience
    t.stop_event = stop_event  # type: ignore[attr-defined]
    return t


def main() -> None:
    host = '127.0.0.1'
    port = 7000

    t = start_sink_server(host, port)

    # Run optimizer as subprocess with a short test
    script = os.path.join(os.path.dirname(__file__), 'tcp_optimizer.py')
    out = os.path.join(os.path.dirname(__file__), 'tcp_optimizer_results.json')

    cmd = [sys.executable, script, '--host', host, '--port', str(port), '--duration', '1', '--sndbufs', '65536', '--rcvbufs', '65536', '--out', out]
    print('Running:', ' '.join(cmd))
    proc = subprocess.run(cmd)

    # Give subprocess a moment to flush
    time.sleep(0.2)

    # Stop server
    t.stop_event.set()  # type: ignore[attr-defined]
    print('Sink server stopped')

    if proc.returncode == 0:
        print('Optimizer finished successfully')
        print('Results path:', out)
    else:
        print('Optimizer exited with code', proc.returncode)


if __name__ == '__main__':
    main()

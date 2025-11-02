#!/usr/bin/env python3
"""
tcp_optimizer.py

Simple, single-file TCP optimizer (adaptive tuner) for socket-level tuning.

What it does:
- Connects to a TCP server and, for each candidate configuration (send/recv
  buffer sizes and TCP_NODELAY on/off), it sends continuous payload for a
  short duration and measures achieved throughput (Mbps).
- Saves detailed results to a JSON file and prints a short summary.

Usage (example):
  python tcp_optimizer.py --host 127.0.0.1 --port 7000 --duration 5

Notes:
- This is a user-space helper to tune socket options (SO_SNDBUF, SO_RCVBUF,
  and TCP_NODELAY). It does NOT implement a new TCP congestion-control
  algorithm. For meaningful results you must run an appropriate server
  (e.g., the project's echo/throughput server) on the target host:port.
"""

from __future__ import annotations

import argparse
import json
import socket
import time
import os
from typing import List, Dict, Any


def run_trial(host: str, port: int, sndbuf: int, rcvbuf: int, no_delay: bool, duration: float, chunk: int) -> Dict[str, Any]:
    """Run a single throughput trial.

    Connects to host:port, sets socket options, and sends payload for
    approximately `duration` seconds. Returns measurement dictionary.
    """
    result: Dict[str, Any] = {
        'host': host,
        'port': port,
        'sndbuf_requested': sndbuf,
        'rcvbuf_requested': rcvbuf,
        'tcp_nodelay_requested': bool(no_delay),
        'duration_target': duration,
    }

    payload = b'X' * chunk

    try:
        with socket.create_connection((host, port), timeout=5) as s:
            # Apply socket options (guarded by availability)
            try:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, sndbuf)
            except Exception as e:
                result['sndbuf_set_error'] = str(e)

            try:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, rcvbuf)
            except Exception as e:
                result['rcvbuf_set_error'] = str(e)

            # TCP_NODELAY
            try:
                if hasattr(socket, 'TCP_NODELAY'):
                    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1 if no_delay else 0)
            except Exception as e:
                result['nodelay_set_error'] = str(e)

            # Read back actual values where possible
            try:
                result['sndbuf_actual'] = s.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
            except Exception:
                result['sndbuf_actual'] = None

            try:
                result['rcvbuf_actual'] = s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
            except Exception:
                result['rcvbuf_actual'] = None

            try:
                if hasattr(socket, 'TCP_NODELAY'):
                    result['tcp_nodelay_actual'] = bool(s.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY))
            except Exception:
                result['tcp_nodelay_actual'] = None

            # Warmup small pause
            time.sleep(0.05)

            # Sending loop for duration seconds
            sent = 0
            t0 = time.time()
            end = t0 + duration
            while time.time() < end:
                try:
                    s.sendall(payload)
                    sent += len(payload)
                except Exception as e:
                    result['send_error'] = str(e)
                    break

            t1 = time.time()
            actual_duration = max(1e-6, t1 - t0)
            mbps = (sent * 8) / 1_000_000 / actual_duration

            result.update({
                'bytes_sent': sent,
                'duration_seconds': actual_duration,
                'throughput_mbps': mbps,
                'chunk_size': chunk,
            })

            return result

    except ConnectionRefusedError:
        return {'error': 'connection_refused', 'host': host, 'port': port}
    except socket.timeout:
        return {'error': 'timeout', 'host': host, 'port': port}
    except Exception as e:
        return {'error': 'exception', 'message': str(e), 'host': host, 'port': port}


def parse_int_list(s: str) -> List[int]:
    parts = [p.strip() for p in s.split(',') if p.strip()]
    return [int(p) for p in parts]


def main() -> None:
    p = argparse.ArgumentParser(description='TCP socket-level optimizer (single-file)')
    p.add_argument('--host', default='127.0.0.1', help='Target server host')
    p.add_argument('--port', type=int, default=7000, help='Target server port')
    p.add_argument('--duration', type=float, default=5.0, help='Seconds per trial (float)')
    p.add_argument('--chunk', type=int, default=64*1024, help='Chunk size in bytes (default 64KB)')
    p.add_argument('--sndbufs', default='16384,32768,65536,131072', help='Comma-separated send buffer sizes to try')
    p.add_argument('--rcvbufs', default='16384,32768,65536,131072', help='Comma-separated recv buffer sizes to try')
    p.add_argument('--test-nodelay', action='store_true', help='If set, also test TCP_NODELAY on/off (else uses system default only)')
    p.add_argument('--out', default='tcp_optimizer_results.json', help='Output JSON file')

    args = p.parse_args()

    sndbufs = parse_int_list(args.sndbufs)
    rcvbufs = parse_int_list(args.rcvbufs)

    combos = []
    for s in sndbufs:
        for r in rcvbufs:
            if args.test_nodelay:
                combos.append((s, r, False))
                combos.append((s, r, True))
            else:
                combos.append((s, r, None))

    print(f"Running {len(combos)} trials against {args.host}:{args.port} (~{args.duration}s each)")

    results: List[Dict[str, Any]] = []
    best = None

    for idx, (s, r, nd) in enumerate(combos, start=1):
        label = f"snd={s//1024}KB rcv={r//1024}KB"
        if nd is True:
            label += ' nodelay=on'
        elif nd is False:
            label += ' nodelay=off'
        else:
            label += ' nodelay=default'

        print(f"[{idx}/{len(combos)}] Testing {label} ... ", end='', flush=True)

        if nd is None:
            # do not explicitly set nodelay; use system default
            trial = run_trial(args.host, args.port, s, r, False, args.duration, args.chunk)
            # indicate we didn't explicitly toggle nodelay
            trial['tcp_nodelay_requested'] = 'system_default'
        else:
            trial = run_trial(args.host, args.port, s, r, nd, args.duration, args.chunk)

        results.append(trial)

        if 'throughput_mbps' in trial:
            print(f"{trial['throughput_mbps']:.2f} Mbps")
            if best is None or trial['throughput_mbps'] > best['throughput_mbps']:
                best = trial
        else:
            print(f"ERROR: {trial.get('error', trial.get('send_error', 'unknown'))}")

    summary = {
        'host': args.host,
        'port': args.port,
        'trials': len(results),
        'best': best,
        'results': results,
        'generated_at': time.time()
    }

    # Write output to file
    outpath = os.path.abspath(args.out)
    try:
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        print(f"\nResults written to: {outpath}")
    except Exception as e:
        print(f"Failed to write results: {e}")

    if best:
        print('\nBest configuration:')
        print(json.dumps({
            'sndbuf_requested': best.get('sndbuf_requested'),
            'rcvbuf_requested': best.get('rcvbuf_requested'),
            'tcp_nodelay_requested': best.get('tcp_nodelay_requested'),
            'throughput_mbps': best.get('throughput_mbps')
        }, indent=2))
    else:
        print('\nNo successful trial recorded; check server availability and firewall settings.')


if __name__ == '__main__':
    main()

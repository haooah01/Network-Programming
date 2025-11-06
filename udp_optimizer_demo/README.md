# UDP Optimization Demo — Baseline, ARQ and Simple FEC

This demo implements a small, self-contained simulator to illustrate a few UDP-level
optimizations and reliability techniques. It is intended for learning and experimenting
— not for production use.

Supported techniques
- Baseline UDP (no reliability): send datagrams and count what arrives.
- ARQ (selective retransmissions): sender retransmits packets that were not acknowledged.
- Simple FEC (XOR parity): group `k` data packets and send one parity packet; the receiver
  can recover any single lost packet per group by XORing the others.

Why this demo
- Shows how each technique behaves under packet loss and variable delay.
- Measures delivered packets, retransmissions, goodput and FEC recovery ratio.

How it works (high level)
- The demo runs entirely in-process using asyncio. A lightweight `Emulator` models the
  network: it applies packet loss probability and random delay.
- Sender and Receiver exchange messages through the emulator. ACKs are also passed via
  the emulator (so they can be lost/delayed).
- An `experiment` runner runs a single trial and outputs a JSON summary.

Files
- `experiment.py` — main demo. Run with Python to execute experiments.
- `requirements.txt` — minimal; the demo uses only the Python standard library.

Quick start

1. Ensure you have Python 3.8+ installed.
2. From the repo root run:

```powershell
python "./udp_optimizer_demo/experiment.py" --mode fec --loss 0.1 --packets 100
```

Examples
- Baseline (no reliability):
  python experiment.py --mode baseline --loss 0.10 --packets 1000
- ARQ: selective retransmit with timeout and retries:
  python experiment.py --mode arq --loss 0.10 --packets 1000 --timeout 0.2
- FEC (XOR parity) with group size 4:
  python experiment.py --mode fec --loss 0.10 --packets 1000 --fec-group 4

Outputs
- The demo prints a JSON summary at the end with metrics such as:
  - sent_packets, data_packets (useful payload), retransmissions, fec_recoveries,
    delivered_packets, goodput_bytes_per_sec, duration_sec

Design notes and limitations
- The FEC used here is a simple XOR parity per group — it can recover at most 1 lost
  packet per group. This matches the parity example in the provided attachment.
- The emulator is simplistic and intended for demonstration. For more realistic
  experiments consider network simulators (ns-3, Mininet) or using raw sockets.

Extensions
- Add Reed-Solomon FEC using a library to handle multiple losses per group.
- Implement more sophisticated congestion-aware rate control for UDP.
- Visualize results (matplotlib) for multiple runs and loss points.

License: MIT (follow repository license)

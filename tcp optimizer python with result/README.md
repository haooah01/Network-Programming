# TCP Optimizer — quick, human-friendly guide

This small utility helps you experiment with socket-level tuning for TCP connections. It is intended as a simple, practical tool to measure how changing socket options (send/receive buffer sizes and TCP_NODELAY) affects measured throughput in your environment.

Important: this tool tunes socket options from user-space. It does NOT implement or replace kernel TCP congestion-control algorithms (NewReno, BBR, etc.). For realistic network measurements, run client and server on different machines or use a network emulator.

## What you get

- `tcp_optimizer.py` — grid-sweep tester that connects to a server and, for each combination of settings, sends traffic for a short duration and reports throughput. Results are saved to JSON.
- `run_with_local_server.py` — convenience helper that starts a minimal local sink server (accepts and drops data) then runs the optimizer. Use this for quick local verification.
- `tcp_optimizer_results.json` — sample results produced by a test run.

## Quick start (local test)

1. From the project root, run the helper which starts a local sink server and runs a 1-second trial:

```powershell
python "d:\Documents-D\VS Code\network programming\tcp optimizer\run_with_local_server.py"
```

This produces `tcp_optimizer_results.json` in the same folder.

## Example: run against the repo's echo server

1. Start the repo's echo/throughput server (example):

```powershell
python "d:\Documents-D\VS Code\network programming\buoi3\TCPechoapp\server.py" --port 7000 --mode len
```

2. In another terminal run the optimizer with a grid sweep and longer trials:

```powershell
python "d:\Documents-D\VS Code\network programming\tcp optimizer\tcp_optimizer.py" \
  --host 127.0.0.1 --port 7000 \
  --duration 10 --test-nodelay \
  --sndbufs "32768,65536,131072" --rcvbufs "32768,65536,131072" \
  --out "d:\\Documents-D\\VS Code\\network programming\\tcp optimizer\\tcp_optimizer_results.json"
```

Adjust `--host` and `--port` to point to the receiving server. Use `--duration` long enough (5–20s) for stable measurements.

## How to read results

The output JSON contains:

- `results`: array of per-trial objects with fields like `sndbuf_requested`, `rcvbuf_requested`, `tcp_nodelay_actual`, `bytes_sent`, `duration_seconds`, `throughput_mbps`.
- `best`: the trial with highest `throughput_mbps` found during the run.

Tips:

- Compare `throughput_mbps` across trials to find the best buffer sizes and whether TCP_NODELAY helped in your environment.
- Check `sndbuf_actual` and `rcvbuf_actual` because the OS may adjust your requested sizes.
- Use longer durations and repeat runs to reduce noise.

## Limitations & notes

- Localhost tests show very high throughput and are not representative of real networks.
- Windows may not expose some socket-level metrics that are available on Linux (e.g., `TCP_INFO`).
- For production-grade tuning consider measuring RTT and packet loss, and run tests across machines or with network emulation (tc/netem on Linux).

## Next steps (ideas)

- Add an adaptive hill-climbing tuner to search the parameter space automatically.
- Produce CSV summary and graphs (throughput vs buffer size).
- Add TCP_INFO (Linux only) to correlate cwnd/rtt with throughput.

If you want any of the above (adaptive tuner, CSV export, longer automatic sweep), tell me which one and I will implement it.

---

Path: `tcp optimizer/` (project root)

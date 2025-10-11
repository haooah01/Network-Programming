# TCP Echo Application

Python 3 implementation of a TCP echo server and client with configurable framing (line-based or length-prefixed), UTF-8 aware display, robust error handling, and cross-platform tooling.

## Requirements

- Python 3.10 or newer (Windows, Linux, macOS)
- No external dependencies

## Project Layout

```
server.py               # Echo server entry point
client.py               # Echo client CLI
scripts/run_local.sh    # Quick demo script for POSIX shells
scripts/run_local.ps1   # Quick demo script for PowerShell
scripts/bench.py        # Simple benchmark driver
tests/e2e_echo_runner.py# Automated test harness
tests/test_matrix.md    # Acceptance test matrix
Makefile                # Convenience targets (optional)
```

## Server Usage

```bash
python server.py --host 0.0.0.0 --port 8080 --mode line \
    --timeout 30 --max-bytes 1048576 --max-clients 32 --debug
```

Key options:

- `--mode <line|len>`: framing selection (`line` newline-delimited, `len` 4-byte big-endian length prefix).
- `--timeout <seconds>`: per-client I/O timeout (timeout closes just that connection).
- `--max-bytes <n>`: reject messages larger than `n` bytes (Line Too Long / invalid length ? protocol error 40).
- `--max-clients <n>`: limit concurrent client handlers (thread-per-connection with semaphore guard).
- `--debug`: log hex previews (first 64 bytes) for received/sent frames.

The server logs INFO/ERROR entries with timestamps, remote endpoint, byte counts, and duration (ms). `SIGINT`/`CTRL+C` triggers a graceful shutdown. Fatal lifecycle errors exit with codes:

| Code | Meaning |
|------|---------|
| 10   | Socket creation / address resolution failure |
| 11   | Bind failure (port in use / insufficient privileges) |
| 12   | Listen/accept failure that prevents operation |
| 30   | Send/receive failure (connection closed mid-message) |
| 40   | Protocol violation (line too long, invalid length) |

## Client Usage

```bash
python client.py --host 127.0.0.1 --port 8080 --mode len \
    --input inline --text "Hi TCP 😀!" --retry-count 3 --retry-backoff 0.3
```

Options:

- `--input <inline|stdin|file>`: choose message source (`--text` or `--path` supply the payload).
- For `line` mode, the client appends `\n` if missing.
- Retries: configurable count/backoff for transient connection failures.
- On receive, the client tries strict UTF-8 decode; decode failures trigger exit code **41** with a hex preview while preserving raw bytes on the wire.
- Exit codes mirror the spec (20 connect errors, 30 I/O, 40 protocol, 41 UTF-8 display warning).

## Cross-Platform Notes

- **Windows**: `python` invokes the interpreter; PowerShell helper `scripts/run_local.ps1` automates a quick end-to-end demo.
- **Linux/macOS**: use `python3`; `scripts/run_local.sh` demonstrates server+client. Mark executable via `chmod +x scripts/run_local.sh`.
- `Makefile` targets (`make run-server`, `make run-client`, `make test`, `make bench`) simplify repetitive commands on Unix-like systems.

## Tests

1. Automated suite: `python tests/e2e_echo_runner.py`
   - Covers ASCII/Unicode echoes, empty payloads, long messages, zero-length frames, oversize length rejection, invalid UTF-8 roundtrip, timeout handling, concurrency, and client hex preview fallback (see `tests/test_matrix.md`).
2. Smoke test: `scripts/run_local.[sh|ps1]`
3. Manual exploration with `nc` / `telnet` for line mode or a hex editor for length mode.

## Benchmark

Run a simple throughput test:

```bash
python scripts/bench.py --mode line --count 10000 --concurrency 50
```

Outputs aggregate duration, average latency, p95 latency, and any connection errors.

## Sample Workflows

### Start server (line mode) & client inline
```powershell
# Windows
python server.py --mode line --port 8080
# In another shell
python client.py --mode line --text "Hello" --input inline
```

### Length-prefixed round trip from file
```bash
python server.py --mode len --port 9000
python client.py --mode len --input file --path sample.txt --port 9000
```

### Run tests
```bash
python tests/e2e_echo_runner.py
```

### Quick demo script (POSIX)
```bash
./scripts/run_local.sh
```

## Graceful Shutdown & Resilience Checklist

- Echoes exact bytes (line + length modes) without altering payload.
- Handles partial I/O through send/recv loops.
- Enforces max message size and length validation.
- Applies per-client timeouts; closes sockets in `finally` blocks.
- Logs remote endpoint, message sizes, errors, and durations.
- Client surfaces UTF-8 display issues with hex preview (exit 41).

Refer to `tests/test_matrix.md` for the acceptance criteria mapping.

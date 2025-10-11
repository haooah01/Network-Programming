# Echo TCP Test Matrix

| ID | Scenario | Mode | Purpose |
|----|----------|------|---------|
| T1 | ASCII echo (`Hello`) | line | Baseline functionality |
| T2 | Unicode echo (`Hi TCP 😀!`) | line/len | Validate UTF-8 round-trip |
| T3 | Empty message | line | Ensure newline-only messages are supported |
| T4 | Long payload (~8 KiB) | line | Verify buffered partial recv handling |
| T5 | Large payload (~64 KiB) | len | Validate multi-chunk payload handling |
| T6 | Zero-length frame | len | Ensure zero-length payloads are permitted |
| T7 | Invalid UTF-8 payload | len | Server must echo bytes without alteration |
| T8 | Oversized length prefix | len | Server rejects protocol violation (exit 40) |
| T9 | Abrupt client disconnect mid-message | line | Server robustness |
| T10 | I/O timeout | line | Enforce configurable timeouts |
| T11 | Parallel clients (16 workers) | line | Concurrency safety |
| T12 | Client UTF-8 decode failure reporting | len | Verify hex preview fallback |

The automated runner (`tests/e2e_echo_runner.py`) covers T1�T12. Manual spot checks using `nc` / `telnet` can exercise additional exploratory scenarios if desired.

# SyncAsync Chat & File Transfer

A robust TCP-based chat and file transfer application supporting both synchronous (blocking) and asynchronous (non-blocking) modes with the same protocol.

## Features
- **Chat**: Real-time messaging with rooms and users.
- **File Transfer**: Chunked transfer with SHA-256 integrity checks.
- **Modes**: Synchronous (thread-per-client) and Asynchronous (asyncio event loop).
- **Protocol**: Length-prefixed JSON messages over TCP.
- **Security**: Optional token authentication, path sanitization.
- **Reliability**: Heartbeat, error handling, backpressure.

## Project Structure
```
buoi5/
├── app/
│   ├── __init__.py
│   ├── main.py           # Unified entry point
│   ├── common.py         # Framing, JSON codec, protocol builders
│   ├── sync_server.py   # Sync chat server
│   ├── sync_client.py    # Sync chat client
│   ├── sync_file_sender.py
│   ├── sync_file_receiver.py
│   ├── async_server.py  # Async chat server
│   ├── async_client.py   # Async chat client
│   ├── async_file_sender.py
│   └── async_file_receiver.py
└── tests/
    ├── __init__.py
    ├── test_common.py    # Unit tests
    ├── test_integration.py
    └── test_load.py
```

## Setup
1. Install Python 3.11+
2. Create venv: `python -m venv .venv`
3. Activate: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux/Mac)
4. Install pytest: `pip install pytest`

## Runbooks

### Start Sync Chat Server
```bash
python app/main.py sync-server --port 5050
```

### Start Async Chat Server
```bash
python app/main.py async-server --port 5050
```

### Connect Sync Client
```bash
python app/main.py sync-client --host 127.0.0.1 --port 5050 --name alice
```

### Connect Async Client
```bash
python app/main.py async-client --host 127.0.0.1 --port 5050 --name bob
```

### Send File (Sync)
```bash
python app/main.py sync-file-send --path ./file.txt --host 127.0.0.1 --port 5050
```

### Receive File (Sync)
```bash
python app/main.py sync-file-recv --port 5050
```

### GUI Client
```bash
python app/gui_client.py
```
(Requires tkinter, usually included in Python)

## Testing
- Unit tests: `pytest tests/test_common.py`
- Integration: `pytest tests/test_integration.py` (requires server running)
- Load: `pytest tests/test_load.py` (requires server running)

## Protocol Details
- Framing: 4-byte big-endian length + UTF-8 JSON payload
- Max message: 1 MiB
- Heartbeat: Ping every 20s, timeout after 40s
- File chunks: 64 KiB max, base64 encoded

## Acceptance Criteria
- Chat latency <100ms on LAN
- File transfer with SHA-256 match
- Survives network chaos
- Cross-mode interoperability

## Extensions (Optional)
- Rooms and private messaging
- User presence
- Resume file transfer
- TLS support
- WebSocket gateway

## Error Handling
See error_matrix in project spec for detailed fixes.

---
**Author**: haooah01
**Version**: 1.0
**License**: MIT
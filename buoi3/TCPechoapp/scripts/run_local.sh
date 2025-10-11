#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python3}"
PORT="${PORT:-8080}"
MODE="${MODE:-line}"

cleanup() {
  if [[ -n "${SERVER_PID:-}" ]]; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT

"$PYTHON" "$ROOT/server.py" --host 127.0.0.1 --port "$PORT" --mode "$MODE" --timeout 5 --debug &
SERVER_PID=$!

sleep 1

"$PYTHON" "$ROOT/client.py" --host 127.0.0.1 --port "$PORT" --mode "$MODE" --input inline --text "Hi TCP ??"

import json
import struct
import socket
import time
import uuid

# Constants
LEN_BYTES = 4
MAX_MESSAGE = 1_048_576  # 1 MiB

def send_msg(sock, obj):
    """Send a JSON object over the socket with length prefix."""
    payload = json.dumps(obj, ensure_ascii=False).encode('utf-8')
    if len(payload) > MAX_MESSAGE:
        raise ValueError(f"Message too large: {len(payload)} > {MAX_MESSAGE}")
    length = struct.pack('>I', len(payload))  # big-endian unsigned 32-bit
    sock.sendall(length + payload)

def recv_msg(sock):
    """Receive a JSON object from the socket with length prefix."""
    length_bytes = sock.recv(LEN_BYTES)
    if len(length_bytes) != LEN_BYTES:
        raise ConnectionError("Incomplete length header")
    length = struct.unpack('>I', length_bytes)[0]
    if length > MAX_MESSAGE:
        raise ValueError(f"Message too large: {length} > {MAX_MESSAGE}")
    payload = b''
    while len(payload) < length:
        chunk = sock.recv(length - len(payload))
        if not chunk:
            raise ConnectionError("Incomplete payload")
        payload += chunk
    return json.loads(payload.decode('utf-8'))

# Protocol helpers
def build_chat(text, from_user, room='default', corr_id=None):
    return {
        'type': 'chat',
        'ts': time.time(),
        'from': from_user,
        'room': room,
        'corr_id': corr_id or str(uuid.uuid4()),
        'text': text
    }

def build_file_meta(name, size, sha256, from_user, room='default', corr_id=None):
    return {
        'type': 'file_meta',
        'ts': time.time(),
        'from': from_user,
        'room': room,
        'corr_id': corr_id or str(uuid.uuid4()),
        'name': name,
        'size': size,
        'sha256': sha256
    }

def build_file_chunk(offset, bytes_b64, from_user, room='default', corr_id=None):
    return {
        'type': 'file_chunk',
        'ts': time.time(),
        'from': from_user,
        'room': room,
        'corr_id': corr_id or str(uuid.uuid4()),
        'offset': offset,
        'bytes_b64': bytes_b64
    }

def build_ack(ok, corr_id, error=None, from_user=None, room='default'):
    return {
        'type': 'ack',
        'ts': time.time(),
        'from': from_user,
        'room': room,
        'corr_id': corr_id,
        'ok': ok,
        'error': error
    }

def build_ping(from_user, room='default'):
    return {
        'type': 'ping',
        'ts': time.time(),
        'from': from_user,
        'room': room,
        'corr_id': str(uuid.uuid4())
    }

def build_pong(from_user, room='default'):
    return {
        'type': 'pong',
        'ts': time.time(),
        'from': from_user,
        'room': room,
        'corr_id': str(uuid.uuid4())
    }
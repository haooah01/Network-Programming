import socket
import os
import hashlib
import base64
from common import *

MAX_CHUNK_BYTES = 65536

def send_file(sock, filepath, name, from_user, room):
    """Send a file over the socket."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    size = os.path.getsize(filepath)
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        data = f.read()
        sha256.update(data)
    sha256_hex = sha256.hexdigest()

    meta = build_file_meta(name, size, sha256_hex, from_user, room)
    send_msg(sock, meta)

    # Wait for ACK
    ack = recv_msg(sock)
    if not ack.get('ok', False):
        raise Exception(f"Meta not acknowledged: {ack.get('error', 'Unknown error')}")

    # Send chunks
    with open(filepath, 'rb') as f:
        offset = 0
        while offset < size:
            chunk = f.read(MAX_CHUNK_BYTES)
            if not chunk:
                break
            chunk_b64 = base64.b64encode(chunk).decode('ascii')
            chunk_msg = build_file_chunk(offset, chunk_b64, from_user, room, meta['corr_id'])
            send_msg(sock, chunk_msg)
            offset += len(chunk)

    # Wait for final ACK
    final_ack = recv_msg(sock)
    if not final_ack.get('ok', False):
        raise Exception(f"File transfer failed: {final_ack.get('error', 'Unknown error')}")

def main(host='127.0.0.1', port=5050, filepath='', name='sender', room='default'):
    """Main sender function."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    filename = os.path.basename(filepath)
    print(f"Sending file {filename} to {host}:{port}")
    send_file(sock, filepath, filename, name, room)
    print("File sent successfully")
    sock.close()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=5050)
    parser.add_argument('--path', required=True, help='Path to file to send')
    parser.add_argument('--name', default='sender')
    parser.add_argument('--room', default='default')
    args = parser.parse_args()
    main(args.host, args.port, args.path, args.name, args.room)
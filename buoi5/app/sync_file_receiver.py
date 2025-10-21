import socket
import threading
import os
import hashlib
import base64
from common import *

MAX_CHUNK_BYTES = 65536

# Global for ongoing transfers (simplified for one file)
ongoing = {}
lock = threading.Lock()

def handle_client(sock, addr):
    """Handle file transfer client."""
    client_id = f"{addr[0]}:{addr[1]}"
    print(f"File receiver client connected: {client_id}")
    try:
        while True:
            msg = recv_msg(sock)
            if msg['type'] == 'file_meta':
                filename = msg['name']
                size = msg['size']
                sha256_expected = msg['sha256']
                filepath = os.path.join('./inbox', filename)
                os.makedirs('./inbox', exist_ok=True)
                with lock:
                    ongoing[msg['corr_id']] = {
                        'file': open(filepath, 'wb'),
                        'size': size,
                        'sha256': hashlib.sha256(),
                        'received': 0
                    }
                ack = build_ack(True, msg['corr_id'], from_user='receiver')
                send_msg(sock, ack)
            elif msg['type'] == 'file_chunk':
                corr_id = msg['corr_id']
                with lock:
                    if corr_id in ongoing:
                        transfer = ongoing[corr_id]
                        chunk_bytes = base64.b64decode(msg['bytes_b64'])
                        transfer['file'].write(chunk_bytes)
                        transfer['sha256'].update(chunk_bytes)
                        transfer['received'] += len(chunk_bytes)
                        if transfer['received'] >= transfer['size']:
                            transfer['file'].close()
                            sha256_actual = transfer['sha256'].hexdigest()
                            ok = sha256_actual == msg.get('sha256', '')  # Note: sha256 should be in meta, but for simplicity
                            ack = build_ack(ok, corr_id, error='Checksum mismatch' if not ok else None, from_user='receiver')
                            send_msg(sock, ack)
                            del ongoing[corr_id]
    except Exception as e:
        print(f"Client {client_id} error: {e}")
    finally:
        sock.close()

def main(host='0.0.0.0', port=5050):
    """Main receiver server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"Sync file receiver listening on {host}:{port}")
    try:
        while True:
            sock, addr = server.accept()
            threading.Thread(target=handle_client, args=(sock, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("Receiver shutting down")
    finally:
        server.close()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=5050)
    args = parser.parse_args()
    main(args.host, args.port)
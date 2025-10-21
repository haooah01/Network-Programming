import socket
import threading
from common import *
import hashlib
import base64

# Global registry
clients = {}
lock = threading.Lock()

def broadcast(msg, exclude_sock=None):
    """Broadcast message to all clients except the sender."""
    with lock:
        for sock in list(clients.values()):
            if sock != exclude_sock:
                try:
                    send_msg(sock, msg)
                except Exception as e:
                    print(f"Broadcast error: {e}")

def handle_client(sock, addr):
    """Handle a single client connection."""
    client_id = f"{addr[0]}:{addr[1]}"
    with lock:
        clients[client_id] = sock
    print(f"Client connected: {client_id}")
    try:
        while True:
            msg = recv_msg(sock)
            if msg['type'] == 'chat':
                broadcast(msg, sock)
            elif msg['type'] == 'ping':
                pong = build_pong(msg['from'], msg['room'])
                send_msg(sock, pong)
            elif msg['type'] == 'file_meta':
                print(f"Receiving file: {msg['filename']} from {msg['from']}")
                # Send ACK
                ack = build_ack(True, '', msg['corr_id'])
                send_msg(sock, ack)
                # Receive chunks
                file_data = b''
                expected_size = msg['size']
                while len(file_data) < expected_size:
                    chunk_msg = recv_msg(sock)
                    if chunk_msg['type'] == 'file_chunk':
                        chunk_data = base64.b64decode(chunk_msg['data'])
                        file_data += chunk_data
                        progress = (len(file_data) / expected_size) * 100
                        print(f"Receiving {msg['filename']}: {progress:.1f}%")
                    else:
                        print(f"Unexpected message: {chunk_msg}")
                        break
                # Verify hash
                sha256 = hashlib.sha256(file_data).hexdigest()
                if sha256 == msg['sha256']:
                    # Save file
                    with open(msg['filename'], 'wb') as f:
                        f.write(file_data)
                    print(f"File {msg['filename']} received and saved successfully")
                    # Send final ACK
                    final_ack = build_ack(True, '', msg['corr_id'])
                    send_msg(sock, final_ack)
                else:
                    print(f"File {msg['filename']} hash mismatch")
                    final_ack = build_ack(False, 'Hash mismatch', msg['corr_id'])
                    send_msg(sock, final_ack)
            # Add more message types as needed
    except Exception as e:
        print(f"Client {client_id} error: {e}")
    finally:
        with lock:
            if client_id in clients:
                del clients[client_id]
        sock.close()
        print(f"Client disconnected: {client_id}")

def main(host='0.0.0.0', port=5050):
    """Main server loop."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"Sync server listening on {host}:{port}")
    try:
        while True:
            sock, addr = server.accept()
            threading.Thread(target=handle_client, args=(sock, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("Server shutting down")
    finally:
        server.close()

if __name__ == '__main__':
    main()
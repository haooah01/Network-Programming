import socket
import threading
import sys
from common import *

def reader(sock):
    """Thread to read and print messages from server."""
    while True:
        try:
            msg = recv_msg(sock)
            if msg['type'] == 'chat':
                print(f"[{msg['from']}]: {msg['text']}")
            elif msg['type'] == 'ack':
                print(f"ACK: {msg}")
            elif msg['type'] == 'pong':
                pass  # Ignore pongs
            # Handle other message types
        except Exception as e:
            print(f"Reader error: {e}")
            break

def sender(sock, name, room):
    """Thread to read from stdin and send chat messages."""
    while True:
        try:
            text = input()
            if text.lower() == 'quit':
                break
            msg = build_chat(text, name, room)
            send_msg(sock, msg)
        except Exception as e:
            print(f"Sender error: {e}")
            break

def main(host='127.0.0.1', port=5050, name='user', room='default'):
    """Main client function."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(f"Connected to {host}:{port} as {name} in room {room}")

    reader_thread = threading.Thread(target=reader, args=(sock,), daemon=True)
    sender_thread = threading.Thread(target=sender, args=(sock, name, room), daemon=True)

    reader_thread.start()
    sender_thread.start()

    try:
        reader_thread.join()
        sender_thread.join()
    except KeyboardInterrupt:
        print("Client shutting down")
    finally:
        sock.close()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=5050)
    parser.add_argument('--name', default='user')
    parser.add_argument('--room', default='default')
    args = parser.parse_args()
    main(args.host, args.port, args.name, args.room)
import socket

def encode_message(msg):
    return ''.join(chr(ord(c)+1) for c in msg)

HOST = input("Enter server IP: ") or '127.0.0.1'
PORT = int(input("Enter server port: ") or 13004)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST, PORT))
    while True:
        message = input("Enter your message (0 to quit): ")
        encoded = encode_message(message)
        client.sendall(encoded.encode())
        reply = client.recv(1024)
        decoded = ''.join(chr(ord(c)-1) for c in reply.decode())
        print(f"Server replied: {decoded}")
        if message == "0":
            break

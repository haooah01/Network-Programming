import socket

def decode_message(msg):
    return ''.join(chr(ord(c)-1) for c in msg)

HOST = '127.0.0.1'
PORT = 13004

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"TCP Chat Encode Server listening on {HOST}:{PORT}")
    conn, addr = server.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            encoded = data.decode()
            if encoded == "0":
                conn.sendall(b"Chat ended by client.")
                break
            decoded = decode_message(encoded)
            print(f"Decoded message: {decoded}")
            reply = ''.join(chr(ord(c)+1) for c in decoded)
            conn.sendall(reply.encode())
        print("Connection closed.")

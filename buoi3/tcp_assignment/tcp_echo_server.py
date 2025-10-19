import socket

HOST = '127.0.0.1'
PORT = 13000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"TCP Echo Server listening on {HOST}:{PORT}")
    conn, addr = server.accept()
    with conn:
        print(f"Connected by {addr}")
        data = conn.recv(1024)
        if data:
            message = data.decode()
            print(f"Received: {message}")
            reply = f"Received: {message}"
            conn.sendall(reply.encode())
        print("Connection closed.")

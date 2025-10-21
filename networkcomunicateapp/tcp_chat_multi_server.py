import socket

HOST = '127.0.0.1'
PORT = 13003

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"TCP Multi-Message Chat Server listening on {HOST}:{PORT}")
    conn, addr = server.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode()
            print(f"Received: {message}")
            if message == "0":
                conn.sendall(b"Chat ended by client.")
                break
            reply = f"Message received: {message}"
            conn.sendall(reply.encode())
        print("Connection closed.")

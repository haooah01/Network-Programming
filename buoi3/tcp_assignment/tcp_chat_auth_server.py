import socket

PASSWORD = "secret123"
HOST = '127.0.0.1'
PORT = 13005

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"TCP Chat Auth Server listening on {HOST}:{PORT}")
    conn, addr = server.accept()
    with conn:
        print(f"Connected by {addr}")
        auth = conn.recv(1024).decode()
        if auth != PASSWORD:
            conn.sendall(b"Authentication failed.")
            print("Authentication failed.")
        else:
            conn.sendall(b"Authentication successful. You can chat now.")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                message = data.decode()
                if message == "0":
                    conn.sendall(b"Chat ended by client.")
                    break
                reply = f"Message received: {message}"
                conn.sendall(reply.encode())
        print("Connection closed.")

import socket

HOST = '127.0.0.1'
PORT = 13008

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"TCP Chat Exception Server listening on {HOST}:{PORT}")
    try:
        conn, addr = server.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    message = data.decode()
                    if message == "0":
                        conn.sendall(b"Chat ended by client.")
                        break
                    reply = f"Message received: {message}"
                    conn.sendall(reply.encode())
                except Exception as e:
                    conn.sendall(f"Error: {str(e)}".encode())
            print("Connection closed.")
    except Exception as e:
        print(f"Server error: {str(e)}")

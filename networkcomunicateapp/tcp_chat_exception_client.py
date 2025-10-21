import socket

HOST = input("Enter server IP: ") or '127.0.0.1'
PORT = int(input("Enter server port: ") or 13008)

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        while True:
            try:
                message = input("Enter your message (0 to quit): ")
                client.sendall(message.encode())
                reply = client.recv(1024)
                print(f"Server replied: {reply.decode()}")
                if message == "0":
                    break
            except Exception as e:
                print(f"Client error: {str(e)}")
except Exception as e:
    print(f"Connection error: {str(e)}")

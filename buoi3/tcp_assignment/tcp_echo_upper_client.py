import socket

HOST = '127.0.0.1'
PORT = 13001

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST, PORT))
    message = "Hello World"
    client.sendall(message.encode())
    reply = client.recv(1024)
    print(f"Server replied: {reply.decode()}")

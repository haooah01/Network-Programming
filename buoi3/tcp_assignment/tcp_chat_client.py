import socket

HOST = '127.0.0.1'
PORT = 13002

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST, PORT))
    message = input("Enter your message: ")
    client.sendall(message.encode())
    reply = client.recv(1024)
    print(f"Server replied: {reply.decode()}")

import socket

HOST = input("Enter server IP: ") or '127.0.0.1'
PORT = int(input("Enter server port: ") or 13007)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST, PORT))
    while True:
        message = input("Enter a number (1-10) or 'Quit' to exit: ")
        client.sendall(message.encode())
        reply = client.recv(1024)
        print(f"Server replied: {reply.decode()}")
        if message.lower() == "quit":
            break

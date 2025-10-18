import socket

HOST = ""
PORT = 12000
BUF = 2048

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
    server.bind((HOST, PORT))
    print("The server is ready to receive")
    while True:
        data, addr = server.recvfrom(BUF)
        text = data.decode(errors="replace")
        reply = text.upper().encode()
        server.sendto(reply, addr)
import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12000
BUF = 2048

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as c:
    msg = input("Nhập thông điệp: ")
    c.sendto(msg.encode(), (SERVER_IP, SERVER_PORT))
    data, _ = c.recvfrom(BUF)
    print("Phản hồi:", data.decode())
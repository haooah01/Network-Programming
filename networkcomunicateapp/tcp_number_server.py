import socket
import time

NUMBERS = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
    6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"
}
HOST = '127.0.0.1'
PORT = 13006

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"TCP Number Server listening on {HOST}:{PORT}")
    conn, addr = server.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode().strip()
            if message.lower() == "quit":
                conn.sendall(b"Connection closed by client.")
                break
            try:
                num = int(message)
                if 1 <= num <= 10:
                    conn.sendall(NUMBERS[num].encode())
                else:
                    conn.sendall(b"Number out of range.")
            except Exception:
                conn.sendall(b"Invalid input.")
        print("Connection closed.")

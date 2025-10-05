import socket
import sys

host = '127.0.0.1'
port = 9093

# invalid UTF-8 bytes with newline for line mode
b = b'\xff\xfe\xff\n'
print('Sending bytes:', b)
try:
    with socket.create_connection((host, port), timeout=5) as s:
        s.settimeout(5)
        s.sendall(b)
        data = bytearray()
        while True:
            chunk = s.recv(1024)
            if not chunk:
                break
            data.extend(chunk)
            if b'\n' in chunk:
                break
        received = bytes(data)
        print('Received repr:', received)
        try:
            text = received.decode('utf-8')
            print('Decoded text:', text)
        except UnicodeDecodeError as e:
            print('UnicodeDecodeError at', e.start, 'len', len(received))
            print('Hex preview:', received[:32].hex())
            sys.exit(41)
except Exception as exc:
    print('Test failed:', exc)
    sys.exit(1)

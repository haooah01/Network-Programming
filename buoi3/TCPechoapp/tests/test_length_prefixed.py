import socket
import sys

host = '127.0.0.1'
port = 9094

# Test 1: valid UTF-8 payload
payload1 = 'Hello length mode \u2713'.encode('utf-8')
frame1 = len(payload1).to_bytes(4, 'big') + payload1

# Test 2: invalid UTF-8 payload (raw bytes)
payload2 = b'\xff\xfe\xff'
frame2 = len(payload2).to_bytes(4, 'big') + payload2

for i, frame in enumerate((frame1, frame2), start=1):
    try:
        with socket.create_connection((host, port), timeout=5) as s:
            s.settimeout(5)
            print(f'Test {i}: sending frame (len={len(frame)-4})')
            s.sendall(frame)
            # receive 4-byte header then payload of announced length
            header = s.recv(4)
            if len(header) < 4:
                raise RuntimeError('Short header received')
            length = int.from_bytes(header, 'big')
            data = bytearray()
            while len(data) < length:
                chunk = s.recv(length - len(data))
                if not chunk:
                    raise RuntimeError('Short payload received')
                data.extend(chunk)
            received = bytes(header + data)
            print('Received frame repr:', received)
            payload = received[4:]
            try:
                text = payload.decode('utf-8')
                print('Decoded payload:', text)
            except UnicodeDecodeError as e:
                print('UnicodeDecodeError at', e.start, 'len', len(payload))
                print('Hex preview:', payload[:32].hex())
    except Exception as exc:
        print('Test', i, 'failed:', exc)
        sys.exit(1)

print('Length-prefixed tests completed')

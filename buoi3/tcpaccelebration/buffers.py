import socket
import time
import argparse
import json

p = argparse.ArgumentParser()
p.add_argument('--host', default='127.0.0.1')
p.add_argument('--port', type=int, default=7000)
p.add_argument('--sndbuf', type=int, default=65536)
p.add_argument('--rcvbuf', type=int, default=65536)
p.add_argument('--mb', type=int, default=256)
a = p.parse_args()

size = a.mb * 1024 * 1024
chunk = 64 * 1024

with socket.create_connection((a.host, a.port)) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, a.sndbuf)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, a.rcvbuf)
    
    payload = b'X' * chunk
    sent = 0
    t0 = time.time()
    
    while sent < size:
        s.sendall(payload)
        sent += len(payload)
    
    t1 = time.time()
    mbps = (size * 8 / 1_000_000) / (t1 - t0)
    
    print(json.dumps({
        'sndbuf': a.sndbuf,
        'rcvbuf': a.rcvbuf,
        'throughput_mbps': mbps
    }))
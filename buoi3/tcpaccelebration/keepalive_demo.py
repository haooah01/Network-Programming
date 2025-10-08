import socket
import sys
import time
import json

host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
port = int(sys.argv[2] if len(sys.argv) > 2 else 7000)
IDLE, INTVL, CNT = 30, 10, 5

with socket.create_connection((host, port)) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    
    try:
        s.setsockopt(socket.IPPROTO_TCP, getattr(socket, 'TCP_KEEPIDLE', 4), IDLE)
        s.setsockopt(socket.IPPROTO_TCP, getattr(socket, 'TCP_KEEPINTVL', 5), INTVL)
        s.setsockopt(socket.IPPROTO_TCP, getattr(socket, 'TCP_KEEPCNT', 6), CNT)
    except Exception as e:
        print(json.dumps({
            'warn': 'platform may not support keepalive tunables',
            'error': str(e)
        }))
    
    print(json.dumps({
        'keepalive': True,
        'idle': IDLE,
        'intvl': INTVL,
        'cnt': CNT
    }))
    
    t0 = time.time()
    try:
        while True:
            time.sleep(5)
            try:
                s.send(b'')
            except Exception as e:
                print(json.dumps({
                    'event': 'disconnect_detected',
                    't': time.time() - t0,
                    'error': str(e)
                }))
                break
    except KeyboardInterrupt:
        pass
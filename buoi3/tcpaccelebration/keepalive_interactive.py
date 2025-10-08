import socket
import sys
import time
import json
import threading

host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
port = int(sys.argv[2] if len(sys.argv) > 2 else 7000)

# Keep-alive settings (reduced for demo)
IDLE = 10   # Start probing after 10 seconds of inactivity
INTVL = 3   # Send probe every 3 seconds
CNT = 3     # Send 3 probes before giving up

print(json.dumps({
    'action': 'connecting',
    'host': host,
    'port': port,
    'keepalive_config': {'idle': IDLE, 'intvl': INTVL, 'cnt': CNT}
}))

try:
    with socket.create_connection((host, port), timeout=5) as s:
        # Enable keep-alive
        s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        
        # Try to set keep-alive parameters (platform dependent)
        try:
            s.setsockopt(socket.IPPROTO_TCP, getattr(socket, 'TCP_KEEPIDLE', 4), IDLE)
            s.setsockopt(socket.IPPROTO_TCP, getattr(socket, 'TCP_KEEPINTVL', 5), INTVL)
            s.setsockopt(socket.IPPROTO_TCP, getattr(socket, 'TCP_KEEPCNT', 6), CNT)
            print(json.dumps({'action': 'keepalive_configured', 'success': True}))
        except Exception as e:
            print(json.dumps({
                'action': 'keepalive_config_warning',
                'message': 'Platform may not support all keepalive tunables',
                'error': str(e)
            }))
        
        print(json.dumps({
            'action': 'connected',
            'message': 'Connection established. Monitoring for disconnection...',
            'detection_time_max': IDLE + (INTVL * CNT)
        }))
        
        start_time = time.time()
        last_heartbeat = start_time
        
        try:
            while True:
                current_time = time.time()
                
                # Send heartbeat every 30 seconds
                if current_time - last_heartbeat >= 30:
                    try:
                        s.send(b'heartbeat')
                        print(json.dumps({
                            'action': 'heartbeat_sent',
                            'time': current_time - start_time
                        }))
                        last_heartbeat = current_time
                    except Exception as e:
                        print(json.dumps({
                            'action': 'heartbeat_failed',
                            'time': current_time - start_time,
                            'error': str(e)
                        }))
                        break
                
                # Try to send empty data to test connection
                try:
                    s.send(b'')
                    time.sleep(1)
                except Exception as e:
                    print(json.dumps({
                        'action': 'disconnect_detected',
                        'time': current_time - start_time,
                        'error': str(e),
                        'message': 'Connection lost - keep-alive or send failed'
                    }))
                    break
                    
        except KeyboardInterrupt:
            print(json.dumps({
                'action': 'user_interrupted',
                'time': time.time() - start_time
            }))
            
except Exception as e:
    print(json.dumps({
        'action': 'connection_failed',
        'error': str(e)
    }))
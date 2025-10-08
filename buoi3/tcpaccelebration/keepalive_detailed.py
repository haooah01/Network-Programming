# =============================================================================
# TCP KEEP-ALIVE DETAILED DEMO
# =============================================================================

import socket
import sys
import time
import json
import threading
import signal

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print(json.dumps({
        'action': 'user_interrupted',
        'message': 'Nhận tín hiệu ngắt từ user',
        'time': time.time() - start_time
    }))
    sys.exit(0)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

print("🔬 TCP Keep-Alive Detailed Demo")
print("="*40)

# Parse command line arguments
host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
port = int(sys.argv[2] if len(sys.argv) > 2 else 7000)

# Keep-alive configuration (rút ngắn cho demo)
IDLE = 5    # Bắt đầu gửi probe sau 5 giây idle
INTVL = 2   # Gửi probe mỗi 2 giây  
CNT = 3     # Gửi tối đa 3 probes trước khi bỏ cuộc

print(f"📋 Cấu hình Keep-Alive:")
print(f"   🎯 Target: {host}:{port}")
print(f"   ⏰ TCP_KEEPIDLE: {IDLE} seconds (idle time trước khi gửi probe)")
print(f"   📡 TCP_KEEPINTVL: {INTVL} seconds (interval giữa các probes)")
print(f"   🔄 TCP_KEEPCNT: {CNT} probes (số probe tối đa)")
print(f"   ⏱️  Max detection time: ~{IDLE + (INTVL * CNT)} seconds")

start_time = time.time()

print(json.dumps({
    'action': 'demo_started',
    'config': {
        'host': host,
        'port': port,
        'keepidle': IDLE,
        'keepintvl': INTVL,
        'keepcnt': CNT,
        'max_detection_time': IDLE + (INTVL * CNT)
    },
    'time': 0
}))

try:
    print(f"\n🔌 Đang kết nối đến {host}:{port}...")
    
    # Tạo connection với timeout
    with socket.create_connection((host, port), timeout=10) as s:
        current_time = time.time() - start_time
        print(json.dumps({
            'action': 'connected',
            'message': f'Kết nối thành công đến {host}:{port}',
            'time': current_time
        }))
        
        # *** QUAN TRỌNG: Cấu hình Keep-Alive ***
        print(f"\n🔧 Đang cấu hình TCP Keep-Alive...")
        
        # Bật keep-alive
        s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        keepalive_enabled = s.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
        print(f"   ✅ SO_KEEPALIVE: {'Enabled' if keepalive_enabled else 'Disabled'}")
        
        # Cấu hình keep-alive parameters (platform-dependent)
        config_success = []
        try:
            # TCP_KEEPIDLE: Thời gian idle trước khi gửi probe đầu tiên
            if hasattr(socket, 'TCP_KEEPIDLE'):
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, IDLE)
                config_success.append(f"TCP_KEEPIDLE={IDLE}s")
            elif hasattr(socket, 'TCP_KEEPALIVE'):  # macOS
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPALIVE, IDLE)
                config_success.append(f"TCP_KEEPALIVE={IDLE}s")
            
            # TCP_KEEPINTVL: Khoảng cách giữa các probes
            if hasattr(socket, 'TCP_KEEPINTVL'):
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, INTVL)
                config_success.append(f"TCP_KEEPINTVL={INTVL}s")
            
            # TCP_KEEPCNT: Số probes tối đa
            if hasattr(socket, 'TCP_KEEPCNT'):
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, CNT)
                config_success.append(f"TCP_KEEPCNT={CNT}")
                
        except Exception as e:
            print(json.dumps({
                'action': 'keepalive_config_partial',
                'message': 'Một số tham số keep-alive không được hỗ trợ trên platform này',
                'error': str(e),
                'time': time.time() - start_time
            }))
        
        if config_success:
            print(f"   ✅ Configured: {', '.join(config_success)}")
        
        print(json.dumps({
            'action': 'keepalive_configured',
            'params': {
                'idle': IDLE,
                'intvl': INTVL, 
                'cnt': CNT
            },
            'platform_support': config_success,
            'time': time.time() - start_time
        }))
        
        print(f"\n🎮 Demo scenarios:")
        print(f"   1️⃣  Connection sẽ idle để trigger keep-alive probes")
        print(f"   2️⃣  Sau {IDLE} giây, TCP stack sẽ gửi probe packets")
        print(f"   3️⃣  Nếu server không phản hồi, connection sẽ bị đóng")
        print(f"   4️⃣  Bạn có thể kill server để test disconnect detection")
        
        print(f"\n💡 Commands để test:")
        print(f"   • Kill server process để simulate network failure")
        print(f"   • Disconnect network để test keep-alive")
        print(f"   • Hoặc đợi để xem normal keep-alive behavior")
        
        print(f"\n🔄 Monitoring connection... (Ctrl+C để thoát)")
        
        last_activity = time.time()
        heartbeat_interval = 30  # Send heartbeat every 30 seconds
        
        while True:
            current_time = time.time()
            elapsed = current_time - start_time
            
            # Gửi heartbeat mỗi 30 giây để test connection
            if current_time - last_activity >= heartbeat_interval:
                try:
                    # Gửi small heartbeat message
                    heartbeat_msg = b'ping'
                    s.send(heartbeat_msg)
                    
                    print(json.dumps({
                        'action': 'heartbeat_sent',
                        'message': f'Gửi heartbeat ({len(heartbeat_msg)} bytes)',
                        'time': elapsed
                    }))
                    
                    last_activity = current_time
                    
                except socket.error as e:
                    print(json.dumps({
                        'action': 'heartbeat_failed',
                        'message': 'Heartbeat thất bại - connection có thể đã bị đóng',
                        'error': str(e),
                        'time': elapsed
                    }))
                    break
            
            # Test connection bằng cách gửi empty data
            try:
                s.send(b'')  # Gửi empty packet để test connection
                time.sleep(1)  # Sleep 1 giây trước khi test tiếp
                
            except socket.error as e:
                print(json.dumps({
                    'action': 'disconnect_detected',
                    'message': 'Phát hiện connection bị ngắt',
                    'error': str(e),
                    'time': elapsed,
                    'detection_method': 'send_failed'
                }))
                break
            
            # Log status mỗi 10 giây
            if int(elapsed) % 10 == 0 and elapsed > 0:
                print(json.dumps({
                    'action': 'status_update',
                    'message': f'Connection đang hoạt động, elapsed: {elapsed:.1f}s',
                    'time': elapsed
                }))
                time.sleep(1)  # Tránh spam log
                
except socket.timeout:
    print(json.dumps({
        'action': 'connection_timeout',
        'message': 'Connection timeout',
        'time': time.time() - start_time
    }))
except ConnectionRefusedError:
    print(json.dumps({
        'action': 'connection_refused',
        'message': 'Server từ chối kết nối - đảm bảo server đang chạy',
        'time': time.time() - start_time
    }))
except Exception as e:
    print(json.dumps({
        'action': 'unexpected_error',
        'message': f'Lỗi bất ngờ: {str(e)}',
        'time': time.time() - start_time
    }))

print(json.dumps({
    'action': 'demo_ended',
    'message': 'Keep-alive demo kết thúc',
    'total_time': time.time() - start_time
}))
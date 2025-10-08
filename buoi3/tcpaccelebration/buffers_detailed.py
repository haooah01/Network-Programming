# =============================================================================
# TCP BUFFER SIZE vs THROUGHPUT TEST
# =============================================================================

import socket
import time
import argparse
import json
import sys

print("🔬 TCP Buffer Size vs Throughput Test")
print("="*50)

# Parse command line arguments
p = argparse.ArgumentParser(description='Test throughput với different socket buffer sizes')
p.add_argument('--host', default='127.0.0.1', help='Server hostname/IP')
p.add_argument('--port', type=int, default=7000, help='Server port')
p.add_argument('--sndbuf', type=int, default=65536, help='Send buffer size (bytes)')
p.add_argument('--rcvbuf', type=int, default=65536, help='Receive buffer size (bytes)')
p.add_argument('--mb', type=int, default=256, help='Total data to send (MB)')

args = p.parse_args()

print(f"📋 Cấu hình test:")
print(f"   🎯 Target: {args.host}:{args.port}")
print(f"   📤 Send Buffer: {args.sndbuf:,} bytes ({args.sndbuf/1024:.1f} KB)")
print(f"   📥 Recv Buffer: {args.rcvbuf:,} bytes ({args.rcvbuf/1024:.1f} KB)")
print(f"   📊 Total Data: {args.mb} MB ({args.mb * 1024 * 1024:,} bytes)")

# Tính toán kích thước data
size = args.mb * 1024 * 1024  # Total bytes to send
chunk = 64 * 1024             # 64KB per chunk

print(f"   📦 Chunk Size: {chunk:,} bytes ({chunk/1024:.1f} KB)")
print(f"   🔄 Total Chunks: {size // chunk:,}")

print(f"\n🔌 Đang kết nối đến {args.host}:{args.port}...")

try:
    # Tạo connection đến server
    with socket.create_connection((args.host, args.port), timeout=10) as s:
        print("✅ Kết nối thành công!")
        
        # *** QUAN TRỌNG: Thiết lập socket buffer sizes ***
        print(f"\n🔧 Đang cấu hình socket buffers...")
        
        # Lưu buffer sizes gốc để so sánh
        original_sndbuf = s.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
        original_rcvbuf = s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        
        print(f"   📤 Send Buffer hiện tại: {original_sndbuf:,} bytes")
        print(f"   📥 Recv Buffer hiện tại: {original_rcvbuf:,} bytes")
        
        # Thiết lập buffer sizes mới
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, args.sndbuf)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, args.rcvbuf)
        
        # Kiểm tra buffer sizes sau khi set
        actual_sndbuf = s.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
        actual_rcvbuf = s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        
        print(f"   📤 Send Buffer sau khi set: {actual_sndbuf:,} bytes")
        print(f"   📥 Recv Buffer sau khi set: {actual_rcvbuf:,} bytes")
        
        if actual_sndbuf != args.sndbuf:
            print(f"   ⚠️  Hệ thống đã điều chỉnh send buffer: {args.sndbuf:,} → {actual_sndbuf:,}")
        if actual_rcvbuf != args.rcvbuf:
            print(f"   ⚠️  Hệ thống đã điều chỉnh recv buffer: {args.rcvbuf:,} → {actual_rcvbuf:,}")
        
        # Tạo payload cho mỗi chunk
        payload = b'X' * chunk  # 64KB of 'X' characters
        print(f"\n📦 Payload sample: {payload[:20]}... (first 20 bytes)")
        
        sent = 0           # Bytes đã gửi
        chunks_sent = 0    # Số chunks đã gửi
        
        print(f"\n🚀 Bắt đầu gửi data...")
        print(f"Progress: [", end="", flush=True)
        
        # Ghi lại thời điểm bắt đầu
        t0 = time.time()
        
        # Gửi data theo chunks
        while sent < size:
            try:
                # sendall() đảm bảo toàn bộ data được gửi
                s.sendall(payload)
                sent += len(payload)
                chunks_sent += 1
                
                # Progress indicator
                progress = sent / size
                if chunks_sent % (size // chunk // 20) == 0:  # Update every 5%
                    print("█", end="", flush=True)
                    
            except socket.error as e:
                print(f"\n❌ Lỗi khi gửi data: {e}")
                sys.exit(1)
        
        # Ghi lại thời điểm kết thúc
        t1 = time.time()
        
        print("] 100%")
        print(f"✅ Hoàn thành gửi {sent:,} bytes trong {chunks_sent:,} chunks")
        
        # Tính toán throughput
        duration = t1 - t0  # Thời gian tính bằng seconds
        bits_sent = size * 8  # Convert bytes to bits
        mbps = (bits_sent / 1_000_000) / duration  # Megabits per second
        
        print(f"\n📊 Kết quả throughput:")
        print(f"   ⏱️  Thời gian: {duration:.3f} seconds")
        print(f"   📈 Throughput: {mbps:.2f} Mbps")
        print(f"   📦 Data rate: {(size / duration / 1024 / 1024):.2f} MB/s")
        print(f"   📊 Avg chunk time: {(duration / chunks_sent * 1000):.3f} ms/chunk")
        
        # Tính efficiency
        max_theoretical_mbps = 1000  # Giả sử localhost có thể đạt 1 Gbps
        efficiency = (mbps / max_theoretical_mbps) * 100
        print(f"   🎯 Efficiency: {efficiency:.1f}% (so với 1 Gbps)")
        
        # Output JSON cho automation
        result = {
            'sndbuf': actual_sndbuf,
            'rcvbuf': actual_rcvbuf,
            'sndbuf_requested': args.sndbuf,
            'rcvbuf_requested': args.rcvbuf,
            'total_bytes': size,
            'chunk_size': chunk,
            'chunks_sent': chunks_sent,
            'duration_seconds': duration,
            'throughput_mbps': mbps,
            'throughput_mbps_theoretical_max': max_theoretical_mbps,
            'efficiency_percent': efficiency
        }
        
        print(f"\n📄 Kết quả JSON:")
        print(json.dumps(result, indent=2))
        
except socket.timeout:
    print("❌ Connection timeout - Server có thể không phản hồi")
    sys.exit(1)
except ConnectionRefusedError:
    print("❌ Connection refused - Đảm bảo server đang chạy")
    print("💡 Chạy: node server.js")
    sys.exit(1)
except Exception as e:
    print(f"❌ Lỗi bất ngờ: {e}")
    sys.exit(1)

print("\n✅ Test hoàn thành!")
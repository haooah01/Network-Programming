#!/usr/bin/env python3
"""
Simple Network Test Client
Test kết nối đến các website phổ biến
"""
import socket
import time

def test_connection(host, port=80, timeout=5):
    """Test kết nối TCP đơn giản"""
    try:
        print(f"🔍 Test kết nối đến {host}:{port}")
        
        # Tạo socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # Thử kết nối
        start_time = time.time()
        result = sock.connect_ex((host, port))
        connect_time = time.time() - start_time
        
        sock.close()
        
        if result == 0:
            print(f"✅ Kết nối thành công! Thời gian: {connect_time:.3f}s")
            return True
        else:
            print(f"❌ Kết nối thất bại! Error: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def send_http_request(host, port=80, path="/"):
    """Gửi HTTP request đơn giản"""
    try:
        print(f"📤 Gửi HTTP request đến {host}{path}")
        
        # Tạo socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        # Kết nối
        sock.connect((host, port))
        
        # Tạo HTTP request
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        
        # Gửi request
        sock.send(request.encode())
        
        # Nhận response
        response = b""
        while True:
            data = sock.recv(1024)
            if not data:
                break
            response += data
            
        sock.close()
        
        # Hiển thị kết quả
        response_text = response.decode('utf-8', errors='ignore')
        lines = response_text.split('\n')
        if lines:
            print(f"📥 Response: {lines[0]}")
            print(f"📊 Size: {len(response)} bytes")
            return True
            
    except Exception as e:
        print(f"❌ HTTP request thất bại: {e}")
        return False

def main():
    """Test nhiều website"""
    print("=" * 50)
    print("🌐 SIMPLE NETWORK CONNECTION TEST")
    print("=" * 50)
    
    # Danh sách website để test
    test_sites = [
        ("google.com", 80),
        ("httpbin.org", 80),
        ("example.com", 80),
        ("ut.edu.vn", 80),
        ("localhost", 8080),  # Local server
    ]
    
    for host, port in test_sites:
        print(f"\n📍 Testing {host}:{port}")
        print("-" * 30)
        
        # Test TCP connection
        tcp_ok = test_connection(host, port)
        
        if tcp_ok:
            # Test HTTP request
            http_ok = send_http_request(host, port)
            if http_ok:
                print(f"✅ {host} - HOÀN TOÀN OK!")
            else:
                print(f"⚠️ {host} - TCP OK, HTTP có vấn đề")
        else:
            print(f"❌ {host} - KHÔNG KẾT NỐI ĐƯỢC")
        
        time.sleep(1)  # Đợi 1 giây giữa các test
    
    print("\n" + "=" * 50)
    print("🏁 HOÀN THÀNH TẤT CẢ TEST")
    print("=" * 50)

if __name__ == "__main__":
    main()
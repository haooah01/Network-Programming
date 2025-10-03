#!/usr/bin/env python3
"""
Fixed UT Client để kết nối thành công với ut.edu.vn
"""
import socket
import time
from datetime import datetime

class FixedUTClient:
    def __init__(self):
        # Thử nhiều cách kết nối
        self.targets = [
            {"host": "ut.edu.vn", "ip": "115.78.73.226", "port": 80},
            {"host": "google.com", "ip": "8.8.8.8", "port": 80},  # Backup test
            {"host": "httpbin.org", "ip": "3.212.43.104", "port": 80}  # Backup test
        ]
        
    def test_basic_connection(self, host, ip, port, timeout=10):
        """Test kết nối TCP cơ bản"""
        try:
            print(f"🔍 Test kết nối TCP đến {host} ({ip}:{port})")
            
            # Tạo socket với timeout
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(timeout)
            
            start_time = time.time()
            result = client_socket.connect_ex((ip, port))
            connect_time = time.time() - start_time
            
            client_socket.close()
            
            if result == 0:
                print(f"✅ Kết nối TCP thành công! Thời gian: {connect_time:.3f}s")
                return True
            else:
                print(f"❌ Kết nối TCP thất bại! Error code: {result}")
                return False
                
        except socket.timeout:
            print(f"❌ Timeout sau {timeout}s")
            return False
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
            return False
            
    def send_http_request(self, host, ip, port, path="/"):
        """Gửi HTTP request"""
        try:
            print(f"📤 Gửi HTTP request đến {host} ({ip}:{port})")
            
            # Tạo socket
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(15)  # 15s timeout
            
            # Kết nối
            start_time = time.time()
            client_socket.connect((ip, port))
            connect_time = time.time() - start_time
            
            print(f"✅ Kết nối thành công! Thời gian: {connect_time:.3f}s")
            
            # Tạo HTTP request đơn giản
            http_request = f"""GET {path} HTTP/1.1\r
Host: {host}\r
User-Agent: Python-Client/1.0\r
Accept: text/html\r
Connection: close\r
\r
"""
            
            print(f"📨 Gửi request: GET {path}")
            
            # Gửi request
            client_socket.send(http_request.encode('utf-8'))
            
            # Nhận response
            response_data = b""
            start_receive = time.time()
            
            while True:
                try:
                    chunk = client_socket.recv(4096)
                    if not chunk:
                        break
                    response_data += chunk
                    
                    # Giới hạn thời gian nhận
                    if time.time() - start_receive > 10:
                        break
                        
                except socket.timeout:
                    break
                    
            client_socket.close()
            
            # Phân tích response
            self.analyze_response(response_data, host)
            
            return True
            
        except socket.timeout:
            print("❌ Timeout khi gửi HTTP request")
            return False
        except ConnectionRefusedError:
            print("❌ Kết nối bị từ chối")
            return False
        except Exception as e:
            print(f"❌ Lỗi HTTP request: {e}")
            return False
            
    def analyze_response(self, response_data, host):
        """Phân tích HTTP response"""
        try:
            if not response_data:
                print("❌ Không nhận được response")
                return
                
            # Decode response
            response_text = response_data.decode('utf-8', errors='ignore')
            
            # Tách header và body
            if '\\r\\n\\r\\n' in response_text:
                headers, body = response_text.split('\\r\\n\\r\\n', 1)
            else:
                headers = response_text[:500]  # Chỉ lấy phần đầu
                body = ""
                
            print(f"📥 Response từ {host}:")
            
            # Phân tích status line
            lines = headers.split('\\r\\n')
            if lines:
                status_line = lines[0]
                print(f"  📊 Status: {status_line}")
                
                # Extract status code
                if 'HTTP' in status_line:
                    parts = status_line.split()
                    if len(parts) >= 2:
                        status_code = parts[1]
                        if status_code.startswith('2'):
                            print("  ✅ Response thành công!")
                        elif status_code.startswith('3'):
                            print("  🔄 Redirect response")
                        else:
                            print(f"  ⚠️ Status code: {status_code}")
                
                # Một số header quan trọng
                for line in lines[1:10]:  # Chỉ lấy 10 header đầu
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        if key in ['content-type', 'content-length', 'server']:
                            print(f"  📋 {key.title()}: {value}")
                            
            print(f"  📦 Tổng kích thước: {len(response_data)} bytes")
            
            # Hiển thị một phần body nếu có
            if body and len(body) > 0:
                body_preview = body[:100].strip()
                if 'html' in body_preview.lower():
                    print("  🌐 Nhận được HTML content")
                else:
                    print(f"  📄 Content preview: {body_preview[:50]}...")
                    
        except Exception as e:
            print(f"❌ Lỗi phân tích response: {e}")
            print(f"📦 Raw data size: {len(response_data)} bytes")
            
    def run_tests(self):
        """Chạy test với tất cả targets"""
        print("=" * 70)
        print("🌐 NETWORK CONNECTION TESTS")
        print("=" * 70)
        print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        success_count = 0
        
        for i, target in enumerate(self.targets, 1):
            print(f"{i}️⃣ TEST {target['host'].upper()}")
            print("-" * 50)
            
            # Test TCP connection
            tcp_success = self.test_basic_connection(
                target['host'], target['ip'], target['port']
            )
            
            if tcp_success:
                # Test HTTP request
                http_success = self.send_http_request(
                    target['host'], target['ip'], target['port']
                )
                
                if http_success:
                    success_count += 1
                    print("🎉 Test thành công!")
                else:
                    print("❌ HTTP request thất bại")
            else:
                print("❌ TCP connection thất bại")
                
            print()
            
        print("=" * 70)
        print(f"📊 KẾT QUẢ: {success_count}/{len(self.targets)} tests thành công")
        if success_count > 0:
            print("✅ Kết nối mạng hoạt động bình thường!")
        else:
            print("❌ Tất cả kết nối đều thất bại - kiểm tra mạng/firewall")
        print("=" * 70)

def main():
    client = FixedUTClient()
    
    try:
        client.run_tests()
    except KeyboardInterrupt:
        print("\\n⏹️ Test bị dừng bởi người dùng")
    except Exception as e:
        print(f"\\n❌ Lỗi: {e}")

if __name__ == "__main__":
    main()
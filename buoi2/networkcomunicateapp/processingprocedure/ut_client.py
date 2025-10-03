#!/usr/bin/env python3
"""
Client để gửi yêu cầu đến website ut.edu.vn
IP: 115.78.73.226, Port: 80
"""
import socket
import time
from datetime import datetime

class UTWebsiteClient:
    def __init__(self):
        # Thử nhiều IP và hostname khác nhau
        self.targets = [
            {"host": "ut.edu.vn", "ip": "115.78.73.226", "port": 80},
            {"host": "google.com", "ip": "8.8.8.8", "port": 80},  # Backup test
            {"host": "httpbin.org", "ip": "", "port": 80}  # HTTP test service
        ]
        self.current_target = self.targets[0]  # Mặc định ut.edu.vn
        
    def send_http_request(self, path="/", target_index=0):
        """Gửi HTTP request đến target website"""
        target = self.targets[target_index]
        
        try:
            # Nếu không có IP, thử resolve hostname
            target_ip = target["ip"]
            if not target_ip:
                import socket
                target_ip = socket.gethostbyname(target["host"])
                print(f"Resolved {target['host']} to {target_ip}")
            
            print(f"Đang kết nối đến {target['host']} ({target_ip}:{target['port']})")
            
            # Tạo socket
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(10)  # Timeout 10 giây
            
            # Kết nối đến server
            start_time = time.time()
            client_socket.connect((target_ip, target["port"]))
            connect_time = time.time() - start_time
            
            print(f"✅ Kết nối thành công! Thời gian: {connect_time:.3f}s")
            
            # Tạo HTTP request
            http_request = f"""GET {path} HTTP/1.1\r
Host: {target['host']}\r
User-Agent: Python-Client/1.0\r
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r
Accept-Language: vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3\r
Accept-Encoding: gzip, deflate\r
Connection: close\r
\r
"""
            
            print(f"📤 Gửi request:")
            print(f"  Path: {path}")
            print(f"  Host: {target['host']}")
            
            # Gửi request
            client_socket.send(http_request.encode('utf-8'))
            
            # Nhận response
            response_data = b""
            while True:
                try:
                    chunk = client_socket.recv(4096)
                    if not chunk:
                        break
                    response_data += chunk
                except socket.timeout:
                    break
                    
            # Đóng kết nối
            client_socket.close()
            
            # Phân tích response
            self.analyze_response(response_data)
            
            return True
            
        except socket.timeout:
            print("❌ Lỗi: Timeout khi kết nối")
            return False
        except socket.gaierror as e:
            print(f"❌ Lỗi DNS: {e}")
            return False
        except ConnectionRefusedError:
            print("❌ Lỗi: Kết nối bị từ chối")
            return False
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return False
            
    def analyze_response(self, response_data):
        """Phân tích HTTP response"""
        try:
            response_text = response_data.decode('utf-8', errors='ignore')
            
            # Tách header và body
            if '\r\n\r\n' in response_text:
                headers, body = response_text.split('\r\n\r\n', 1)
            else:
                headers = response_text
                body = ""
                
            # Phân tích status line
            lines = headers.split('\r\n')
            if lines:
                status_line = lines[0]
                print(f"📥 Response:")
                print(f"  Status: {status_line}")
                
                # Lấy một số header quan trọng
                for line in lines[1:]:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        if key in ['content-type', 'content-length', 'server', 'date']:
                            print(f"  {key.title()}: {value}")
                            
                # Hiển thị một phần body
                if body:
                    body_preview = body[:200].strip()
                    if len(body) > 200:
                        body_preview += "..."
                    print(f"  Body preview: {body_preview}")
                    
                print(f"  Total size: {len(response_data)} bytes")
                
        except Exception as e:
            print(f"❌ Lỗi phân tích response: {e}")
            print(f"Raw data size: {len(response_data)} bytes")
            
    def test_connection(self, target_index=0):
        """Test kết nối cơ bản"""
        target = self.targets[target_index]
        
        try:
            # Nếu không có IP, thử resolve hostname
            target_ip = target["ip"]
            if not target_ip:
                import socket
                target_ip = socket.gethostbyname(target["host"])
            
            print(f"🔍 Test kết nối TCP đến {target_ip}:{target['port']}")
            
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)
            
            start_time = time.time()
            result = client_socket.connect_ex((target_ip, target["port"]))
            connect_time = time.time() - start_time
            
            client_socket.close()
            
            if result == 0:
                print(f"✅ Kết nối TCP thành công! Thời gian: {connect_time:.3f}s")
                return True
            else:
                print(f"❌ Kết nối TCP thất bại! Error code: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi test kết nối: {e}")
            return False
            
    def run_comprehensive_test(self):
        """Chạy test toàn diện"""
        print("=" * 60)
        print("🌐 TEST KẾT NỐI WEBSITE")
        print("=" * 60)
        print(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test từng target
        for i, target in enumerate(self.targets):
            print(f"📍 TARGET {i+1}: {target['host']}")
            print(f"   IP: {target['ip'] if target['ip'] else 'Auto-resolve'}")
            print(f"   Port: {target['port']}")
            print()
            
            # Test 1: Kết nối TCP cơ bản
            print(f"1️⃣ TEST KẾT NỐI TCP - {target['host']}")
            tcp_success = self.test_connection(i)
            print()
            
            if tcp_success:
                # Test 2: HTTP Request cơ bản
                print(f"2️⃣ TEST HTTP REQUEST - {target['host']}")
                http_success = self.send_http_request("/", i)
                print()
                
                if http_success:
                    print(f"✅ {target['host']} - KẾT NỐI THÀNH CÔNG!")
                    break  # Dừng lại khi có một target thành công
            else:
                print(f"❌ {target['host']} - KHÔNG KẾT NỐI ĐƯỢC")
            
            print("-" * 40)
            
        print("=" * 60)
        print("🏁 HOÀN THÀNH TEST")
        print("=" * 60)

def main():
    client = UTWebsiteClient()
    
    try:
        client.run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n⏹️ Test bị dừng bởi người dùng")

if __name__ == "__main__":
    main()
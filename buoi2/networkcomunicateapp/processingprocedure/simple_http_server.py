#!/usr/bin/env python3
"""
Simple HTTP Server - Fixed Version
Tự động tìm port khả dụng
"""
import socket
import threading
import time
from datetime import datetime

class SimpleHTTPServer:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        
    def find_available_port(self):
        """Tìm port khả dụng"""
        ports_to_try = [8080, 3000, 8000, 8888, 9000]
        
        for port in ports_to_try:
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.bind((self.host, port))
                test_socket.close()
                return port
            except OSError:
                continue
        return None
        
    def start(self):
        """Khởi động HTTP server"""
        # Tìm port khả dụng
        available_port = self.find_available_port()
        if available_port is None:
            print("❌ Không tìm thấy port khả dụng!")
            return False
            
        self.port = available_port
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            print(f"✅ HTTP Server đang chạy tại http://{self.host}:{self.port}")
            print("🌐 Mở trình duyệt và truy cập địa chỉ trên để test")
            print("⏹️ Nhấn Ctrl+C để dừng server")
            
            while self.running:
                try:
                    client_socket, client_address = self.socket.accept()
                    print(f"📥 Kết nối từ: {client_address}")
                    
                    # Xử lý request trong thread riêng
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        print(f"❌ Lỗi socket: {e}")
                        
        except Exception as e:
            print(f"❌ Lỗi khởi động server: {e}")
            return False
            
    def handle_client(self, client_socket, client_address):
        """Xử lý yêu cầu từ client"""
        try:
            # Nhận dữ liệu từ client
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                return
                
            print(f"📨 Request từ {client_address[0]}:{client_address[1]}")
            
            # Phân tích HTTP request
            lines = request.split('\\n')
            if lines:
                method_line = lines[0].strip()
                parts = method_line.split()
                if len(parts) >= 2:
                    method = parts[0]
                    path = parts[1]
                    print(f"   {method} {path}")
                    
                    # Tạo response
                    response = self.create_response(method, path, client_address)
                    
                    # Gửi response
                    client_socket.send(response.encode('utf-8'))
                    
        except Exception as e:
            print(f"❌ Lỗi xử lý client {client_address}: {e}")
        finally:
            client_socket.close()
            
    def create_response(self, method, path, client_address):
        """Tạo HTTP response"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>🌐 Network Server Demo</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: #4CAF50; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .success {{ background: #d4edda; border-color: #c3e6cb; color: #155724; }}
        .info {{ background: #cce5ff; border-color: #99d6ff; color: #004085; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Kết Nối Thành Công!</h1>
            <p>HTTP Server đang hoạt động bình thường</p>
        </div>
        
        <div class="section success">
            <h2>✅ Thông Tin Kết Nối</h2>
            <p><strong>Server Port:</strong> {self.port}</p>
            <p><strong>Client IP:</strong> {client_address[0]}</p>
            <p><strong>Client Port:</strong> {client_address[1]}</p>
            <p><strong>Thời gian:</strong> {current_time}</p>
            <p><strong>Method:</strong> {method}</p>
            <p><strong>Path:</strong> {path}</p>
        </div>
        
        <div class="section info">
            <h2>🔗 Test Links</h2>
            <ul>
                <li><a href="/info">Server Info</a></li>
                <li><a href="/test">Test Page</a></li>
                <li><a href="/time">Current Time</a></li>
            </ul>
        </div>
        
        <div class="section">
            <h2>📊 Network Demo</h2>
            <p>Đây là demo về:</p>
            <ul>
                <li>🌐 HTTP Client-Server Communication</li>
                <li>🔌 Socket Programming</li>
                <li>📡 Network Request/Response</li>
                <li>🖥️ Web Server Implementation</li>
            </ul>
        </div>
    </div>
</body>
</html>"""
        
        # Tạo HTTP response header
        response = f"""HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: {len(html_content.encode('utf-8'))}
Connection: close
Server: Python-Simple-HTTP-Server
Date: {current_time}

{html_content}"""
        
        return response
        
    def stop(self):
        """Dừng server"""
        self.running = False
        if self.socket:
            self.socket.close()

def main():
    server = SimpleHTTPServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\\n🛑 Đang dừng server...")
        server.stop()
        print("✅ Server đã dừng.")

if __name__ == "__main__":
    main()
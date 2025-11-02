#!/usr/bin/env python3
"""
HTTP Server Application
Chạy trên port 80 để mô phỏng web server thực tế
"""
import socket
import threading
import time
from datetime import datetime

class HTTPServer:
    def __init__(self, host='localhost', port=80):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = False
        
    def start(self):
        """Khởi động HTTP server"""
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            print(f"HTTP Server đang chạy tại http://{self.host}:{self.port}")
            print("Nhấn Ctrl+C để dừng server")
            
            while self.running:
                try:
                    client_socket, client_address = self.socket.accept()
                    print(f"Kết nối từ: {client_address}")
                    
                    # Xử lý request trong thread riêng
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        print(f"Lỗi socket: {e}")
                        
        except PermissionError:
            print(f"CẢNH BÁO: Không thể bind port {self.port}. Cần quyền Administrator!")
            raise
        except OSError as e:
            if e.errno == 10048:  # Address already in use
                print(f"Port {self.port} đã được sử dụng")
            else:
                print(f"Lỗi bind port {self.port}: {e}")
            raise
        except Exception as e:
            print(f"Lỗi khởi động server: {e}")
            raise
            
    def handle_client(self, client_socket, client_address):
        """Xử lý yêu cầu từ client"""
        try:
            # Nhận dữ liệu từ client
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                return
                
            print(f"\nYêu cầu từ {client_address}:")
            print(request.split('\n')[0])  # Chỉ hiển thị dòng đầu
            
            # Phân tích HTTP request
            lines = request.split('\n')
            if lines:
                method_line = lines[0].strip()
                parts = method_line.split()
                if len(parts) >= 2:
                    method = parts[0]
                    path = parts[1]
                    
                    # Tạo response dựa trên path
                    response = self.create_response(method, path, client_address)
                    
                    # Gửi response
                    client_socket.send(response.encode('utf-8'))
                    
        except Exception as e:
            print(f"Lỗi xử lý client {client_address}: {e}")
        finally:
            client_socket.close()
            
    def create_response(self, method, path, client_address):
        """Tạo HTTP response"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if path == '/':
            # Trang chủ
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>HTTP Server Demo</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                    .info {{ margin: 20px 0; }}
                    .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🌐 HTTP Server Demo</h1>
                    <p>Server đang chạy trên port 80</p>
                </div>
                
                <div class="section">
                    <h2>📊 Thông Tin Kết Nối</h2>
                    <p><strong>Client IP:</strong> {client_address[0]}</p>
                    <p><strong>Client Port:</strong> {client_address[1]}</p>
                    <p><strong>Thời gian:</strong> {current_time}</p>
                    <p><strong>Method:</strong> {method}</p>
                    <p><strong>Path:</strong> {path}</p>
                </div>
                
                <div class="section">
                    <h2>🔗 Các Trang Khác</h2>
                    <ul>
                        <li><a href="/info">Thông tin server</a></li>
                        <li><a href="/test">Test page</a></li>
                        <li><a href="/ut">Kết nối đến ut.edu.vn</a></li>
                    </ul>
                </div>
            </body>
            </html>
            """
            
        elif path == '/info':
            # Trang thông tin server
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Server Info</title>
            </head>
            <body>
                <h1>📋 Thông Tin Server</h1>
                <p><strong>Host:</strong> {self.host}</p>
                <p><strong>Port:</strong> {self.port}</p>
                <p><strong>Thời gian:</strong> {current_time}</p>
                <p><strong>Client:</strong> {client_address[0]}:{client_address[1]}</p>
                <a href="/">← Về trang chủ</a>
            </body>
            </html>
            """
            
        elif path == '/test':
            # Trang test
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Test Page</title>
            </head>
            <body>
                <h1>🧪 Test Page</h1>
                <p>Đây là trang test để kiểm tra HTTP server.</p>
                <p><strong>Request từ:</strong> {client_address[0]}:{client_address[1]}</p>
                <p><strong>Thời gian:</strong> {current_time}</p>
                <a href="/">← Về trang chủ</a>
            </body>
            </html>
            """
            
        elif path == '/ut':
            # Trang test kết nối đến ut.edu.vn
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>UT Connection Test</title>
            </head>
            <body>
                <h1>🌐 Kết Nối Đến ut.edu.vn</h1>
                <p><strong>IP Address:</strong> 115.78.73.226</p>
                <p><strong>Port:</strong> 80</p>
                <p><strong>Thời gian test:</strong> {current_time}</p>
                <p>Sử dụng script riêng để test kết nối đến ut.edu.vn</p>
                <a href="/">← Về trang chủ</a>
            </body>
            </html>
            """
            
        else:
            # Trang 404
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>404 Not Found</title>
            </head>
            <body>
                <h1>❌ 404 - Không Tìm Thấy</h1>
                <p>Trang <strong>{path}</strong> không tồn tại.</p>
                <p><strong>Thời gian:</strong> {current_time}</p>
                <a href="/">← Về trang chủ</a>
            </body>
            </html>
            """
        
        # Tạo HTTP response header
        response = f"""HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: {len(html_content.encode('utf-8'))}
Connection: close
Server: Python-HTTP-Server
Date: {current_time}

{html_content}"""
        
        return response
        
    def stop(self):
        """Dừng server"""
        self.running = False
        self.socket.close()

def main():
    # Thử chạy trên port 80 trước
    server = HTTPServer('localhost', 80)
    
    try:
        result = server.start()
        if result is False:
            # Nếu không chạy được port 80, thử port 8080
            print("\nThử chạy trên port 8080...")
            server.stop()  # Đóng server cũ
            server = HTTPServer('localhost', 8080)
            server.start()
            
    except KeyboardInterrupt:
        print("\nĐang dừng server...")
        server.stop()
        print("Server đã dừng.")

if __name__ == "__main__":
    main()
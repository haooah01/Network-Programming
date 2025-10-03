#!/usr/bin/env python3
"""
Simple HTTP Server - Port 8080
Phiên bản đơn giản chạy được ngay
"""
import socket
import threading
from datetime import datetime

def handle_client(client_socket, client_address):
    """Xử lý client đơn giản"""
    try:
        # Nhận request
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Request từ {client_address}: {request.split()[0:2] if request.split() else 'Invalid'}")
        
        # Tạo response đơn giản
        html = f"""<!DOCTYPE html>
<html>
<head><title>Simple HTTP Server</title></head>
<body>
<h1>🌐 HTTP Server đang hoạt động!</h1>
<p><strong>Thời gian:</strong> {datetime.now()}</p>
<p><strong>Client:</strong> {client_address[0]}:{client_address[1]}</p>
<p><strong>Server:</strong> localhost:8080</p>
<hr>
<p>✅ Kết nối thành công!</p>
</body>
</html>"""
        
        response = f"""HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: {len(html)}
Connection: close

{html}"""
        
        client_socket.send(response.encode('utf-8'))
        
    except Exception as e:
        print(f"Lỗi xử lý client: {e}")
    finally:
        client_socket.close()

def main():
    # Tạo server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Bind và listen
        server.bind(('localhost', 3001))
        server.listen(5)
        
        print("🚀 Simple HTTP Server đang chạy tại http://localhost:3001")
        print("📍 Mở trình duyệt và truy cập để test")
        print("⏹️ Nhấn Ctrl+C để dừng")
        
        while True:
            client_socket, client_address = server.accept()
            # Xử lý trong thread riêng
            client_thread = threading.Thread(
                target=handle_client, 
                args=(client_socket, client_address)
            )
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\n⏹️ Đang dừng server...")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        server.close()
        print("✅ Server đã dừng")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Mail Server Application
Chạy trên port 25 để mô phỏng SMTP server
"""
import socket
import threading
import time
from datetime import datetime

class SMTPServer:
    def __init__(self, host='localhost', port=25):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = False
        self.mail_storage = []  # Lưu trữ email nhận được
        
    def start(self):
        """Khởi động SMTP server"""
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            print(f"SMTP Server đang chạy tại {self.host}:{self.port}")
            print("Nhấn Ctrl+C để dừng server")
            
            while self.running:
                try:
                    client_socket, client_address = self.socket.accept()
                    print(f"SMTP: Kết nối từ {client_address}")
                    
                    # Xử lý SMTP client trong thread riêng
                    client_thread = threading.Thread(
                        target=self.handle_smtp_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        print(f"SMTP Lỗi socket: {e}")
                        
        except PermissionError:
            print("CẢNH BÁO: Không thể bind port 25. Cần quyền Administrator!")
            print("Thử chạy với quyền Administrator hoặc đổi sang port khác (2525)")
            return False
        except Exception as e:
            print(f"Lỗi khởi động SMTP server: {e}")
            return False
            
    def handle_smtp_client(self, client_socket, client_address):
        """Xử lý SMTP session"""
        try:
            # Gửi greeting message
            greeting = "220 Python-SMTP-Server Ready\r\n"
            client_socket.send(greeting.encode('utf-8'))
            
            # Khởi tạo session data
            session_data = {
                'mail_from': '',
                'rcpt_to': [],
                'data': '',
                'state': 'greeting'
            }
            
            while True:
                # Nhận command từ client
                data = client_socket.recv(1024).decode('utf-8').strip()
                if not data:
                    break
                    
                print(f"SMTP Command từ {client_address}: {data}")
                
                # Xử lý SMTP commands
                response = self.process_smtp_command(data, session_data, client_address)
                
                if response:
                    client_socket.send(response.encode('utf-8'))
                    
                # Nếu client gửi QUIT, đóng kết nối
                if data.upper().startswith('QUIT'):
                    break
                    
        except Exception as e:
            print(f"Lỗi xử lý SMTP client {client_address}: {e}")
        finally:
            client_socket.close()
            
    def process_smtp_command(self, command, session_data, client_address):
        """Xử lý các SMTP commands"""
        cmd = command.upper()
        
        if cmd.startswith('HELO') or cmd.startswith('EHLO'):
            return "250 Hello, pleased to meet you\r\n"
            
        elif cmd.startswith('MAIL FROM:'):
            # Lấy địa chỉ sender
            sender = command[10:].strip().strip('<>')
            session_data['mail_from'] = sender
            print(f"  Mail from: {sender}")
            return "250 OK\r\n"
            
        elif cmd.startswith('RCPT TO:'):
            # Lấy địa chỉ recipient
            recipient = command[8:].strip().strip('<>')
            session_data['rcpt_to'].append(recipient)
            print(f"  Rcpt to: {recipient}")
            return "250 OK\r\n"
            
        elif cmd == 'DATA':
            session_data['state'] = 'data'
            return "354 End data with <CR><LF>.<CR><LF>\r\n"
            
        elif session_data['state'] == 'data':
            if command == '.':
                # Kết thúc data, lưu email
                self.store_email(session_data, client_address)
                session_data['state'] = 'greeting'
                return "250 OK: Message accepted\r\n"
            else:
                # Thêm dữ liệu vào email
                session_data['data'] += command + '\n'
                return None  # Không gửi response khi đang nhận data
                
        elif cmd == 'QUIT':
            return "221 Bye\r\n"
            
        elif cmd == 'NOOP':
            return "250 OK\r\n"
            
        elif cmd == 'RSET':
            # Reset session
            session_data['mail_from'] = ''
            session_data['rcpt_to'] = []
            session_data['data'] = ''
            session_data['state'] = 'greeting'
            return "250 OK\r\n"
            
        else:
            return "500 Command not recognized\r\n"
            
    def store_email(self, session_data, client_address):
        """Lưu trữ email nhận được"""
        email = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'from': session_data['mail_from'],
            'to': session_data['rcpt_to'],
            'data': session_data['data'],
            'client_ip': client_address[0]
        }
        
        self.mail_storage.append(email)
        
        print(f"\n📧 Email nhận được:")
        print(f"  Từ: {email['from']}")
        print(f"  Đến: {', '.join(email['to'])}")
        print(f"  Thời gian: {email['timestamp']}")
        print(f"  Client IP: {email['client_ip']}")
        print(f"  Nội dung: {email['data'][:100]}...")
        print()
        
    def get_stored_emails(self):
        """Lấy danh sách email đã lưu"""
        return self.mail_storage
        
    def stop(self):
        """Dừng server"""
        self.running = False
        self.socket.close()

def main():
    # Thử chạy trên port 25 trước
    server = SMTPServer('localhost', 25)
    
    try:
        result = server.start()
        if result is False:
            # Nếu không chạy được port 25, thử port 2525
            print("\nThử chạy trên port 2525...")
            server = SMTPServer('localhost', 2525)
            server.start()
            
    except KeyboardInterrupt:
        print("\nĐang dừng SMTP server...")
        print(f"Tổng cộng nhận được {len(server.mail_storage)} email.")
        server.stop()
        print("SMTP Server đã dừng.")

if __name__ == "__main__":
    main()
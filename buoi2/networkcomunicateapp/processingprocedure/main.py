#!/usr/bin/env python3
"""
Chương trình chính để quản lý và chạy tất cả các server/client
"""
import threading
import time
import sys
import os

# Import các module server/client
from http_server import HTTPServer
from mail_server import SMTPServer
from ut_client import UTWebsiteClient

class NetworkApplicationManager:
    def __init__(self):
        self.http_server = None
        self.smtp_server = None
        self.http_thread = None
        self.smtp_thread = None
        self.running = False
        
    def start_http_server(self, port=80):
        """Khởi động HTTP Server"""
        try:
            self.http_server = HTTPServer('localhost', port)
            self.http_thread = threading.Thread(target=self.http_server.start)
            self.http_thread.daemon = True
            self.http_thread.start()
            time.sleep(1)  # Đợi server khởi động
            return True
        except Exception as e:
            print(f"Lỗi khởi động HTTP server: {e}")
            return False
            
    def start_smtp_server(self, port=25):
        """Khởi động SMTP Server"""
        try:
            self.smtp_server = SMTPServer('localhost', port)
            self.smtp_thread = threading.Thread(target=self.smtp_server.start)
            self.smtp_thread.daemon = True
            self.smtp_thread.start()
            time.sleep(1)  # Đợi server khởi động
            return True
        except Exception as e:
            print(f"Lỗi khởi động SMTP server: {e}")
            return False
            
    def test_ut_website(self):
        """Test kết nối đến ut.edu.vn"""
        client = UTWebsiteClient()
        return client.run_comprehensive_test()
        
    def show_menu(self):
        """Hiển thị menu lựa chọn"""
        print("\n" + "=" * 60)
        print("🌐 NETWORK APPLICATION MANAGER")
        print("=" * 60)
        print("1. Khởi động HTTP Server (port 80)")
        print("2. Khởi động SMTP Server (port 25)")
        print("3. Test kết nối đến ut.edu.vn")
        print("4. Khởi động tất cả server")
        print("5. Dừng tất cả server")
        print("6. Hiển thị trạng thái")
        print("0. Thoát")
        print("=" * 60)
        
    def get_status(self):
        """Hiển thị trạng thái các server"""
        print("\n📊 TRẠNG THÁI HỆ THỐNG:")
        print("-" * 40)
        
        # HTTP Server status
        if self.http_server and self.http_server.running:
            print(f"✅ HTTP Server: Đang chạy (port {self.http_server.port})")
        else:
            print("❌ HTTP Server: Không chạy")
            
        # SMTP Server status
        if self.smtp_server and self.smtp_server.running:
            print(f"✅ SMTP Server: Đang chạy (port {self.smtp_server.port})")
            if hasattr(self.smtp_server, 'mail_storage'):
                print(f"   📧 Emails nhận: {len(self.smtp_server.mail_storage)}")
        else:
            print("❌ SMTP Server: Không chạy")
            
        print("-" * 40)
        
    def stop_all_servers(self):
        """Dừng tất cả server"""
        print("\n🛑 Đang dừng tất cả server...")
        
        if self.http_server:
            self.http_server.stop()
            print("✅ HTTP Server đã dừng")
            
        if self.smtp_server:
            self.smtp_server.stop()
            print("✅ SMTP Server đã dừng")
            
        self.running = False
        
    def start_all_servers(self):
        """Khởi động tất cả server"""
        print("\n🚀 Đang khởi động tất cả server...")
        
        # Thử HTTP server trên port 80, nếu không được thì port 8080
        http_success = self.start_http_server(80)
        if not http_success:
            print("⚠️ Port 80 không khả dụng, thử port 8080...")
            http_success = self.start_http_server(8080)
            
        # Thử SMTP server trên port 25, nếu không được thì port 2525
        smtp_success = self.start_smtp_server(25)
        if not smtp_success:
            print("⚠️ Port 25 không khả dụng, thử port 2525...")
            smtp_success = self.start_smtp_server(2525)
            
        if http_success and smtp_success:
            print("✅ Tất cả server đã khởi động thành công!")
            self.running = True
        else:
            print("⚠️ Một số server không khởi động được")
            
    def run(self):
        """Chạy chương trình chính"""
        print("🌟 Chào mừng đến với Network Application!")
        
        try:
            while True:
                self.show_menu()
                choice = input("Nhập lựa chọn của bạn: ").strip()
                
                if choice == '1':
                    # Khởi động HTTP Server
                    port = input("Nhập port (mặc định 80): ").strip()
                    if not port:
                        port = 80
                    else:
                        port = int(port)
                    self.start_http_server(port)
                    
                elif choice == '2':
                    # Khởi động SMTP Server
                    port = input("Nhập port (mặc định 25): ").strip()
                    if not port:
                        port = 25
                    else:
                        port = int(port)
                    self.start_smtp_server(port)
                    
                elif choice == '3':
                    # Test ut.edu.vn
                    self.test_ut_website()
                    
                elif choice == '4':
                    # Khởi động tất cả
                    self.start_all_servers()
                    
                elif choice == '5':
                    # Dừng tất cả
                    self.stop_all_servers()
                    
                elif choice == '6':
                    # Hiển thị trạng thái
                    self.get_status()
                    
                elif choice == '0':
                    # Thoát
                    self.stop_all_servers()
                    print("👋 Tạm biệt!")
                    break
                    
                else:
                    print("❌ Lựa chọn không hợp lệ!")
                    
                input("\nNhấn Enter để tiếp tục...")
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Chương trình bị dừng")
            self.stop_all_servers()
        except Exception as e:
            print(f"\n❌ Lỗi: {e}")
            self.stop_all_servers()

def main():
    """Hàm main"""
    # Kiểm tra quyền Administrator
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            print("⚠️ CẢNH BÁO: Chương trình không chạy với quyền Administrator")
            print("   Port 80 và 25 có thể không khả dụng")
            print("   Để sử dụng port 80/25, hãy chạy CMD/PowerShell với quyền Administrator")
            print()
    except:
        pass
        
    # Khởi động manager
    manager = NetworkApplicationManager()
    manager.run()

if __name__ == "__main__":
    main()
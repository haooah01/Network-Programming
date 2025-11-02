# Network Processing Procedure Application

## 📋 Mô Tả

Ứng dụng mạng minh họa các khái niệm cơ bản về:
- HTTP Server chạy trên port 80
- SMTP (Mail) Server chạy trên port 25  
- Client gửi yêu cầu đến website ut.edu.vn (IP: 115.78.73.226, Port: 80)

## 🏗️ Cấu Trúc Dự Án

```
processingprocedure/
├── main.py           # Chương trình chính - Menu quản lý
├── http_server.py    # HTTP Server (Port 80)
├── mail_server.py    # SMTP Server (Port 25)
├── ut_client.py      # Client kết nối đến ut.edu.vn
└── README.md         # File này
```

## 🚀 Hướng Dẫn Sử Dụng

### Cách 1: Chạy Chương Trình Chính (Khuyến nghị)

```powershell
# Chạy với quyền Administrator để sử dụng port 80/25
python main.py
```

Menu sẽ hiện ra với các tùy chọn:
1. Khởi động HTTP Server (port 80)
2. Khởi động SMTP Server (port 25)
3. Test kết nối đến ut.edu.vn
4. Khởi động tất cả server
5. Dừng tất cả server
6. Hiển thị trạng thái
0. Thoát

### Cách 2: Chạy Từng Module Riêng

#### HTTP Server:
```powershell
python http_server.py
```
- Truy cập: http://localhost:80 (hoặc http://localhost:8080 nếu port 80 bị chiếm)

#### SMTP Server:
```powershell
python mail_server.py
```
- Server lắng nghe trên port 25 (hoặc 2525)

#### Test ut.edu.vn:
```powershell
python ut_client.py
```

## 🔧 Tính Năng Chi Tiết

### 🌐 HTTP Server (Port 80)

**Endpoints có sẵn:**
- `/` - Trang chủ với thông tin kết nối
- `/info` - Thông tin chi tiết về server
- `/test` - Trang test
- `/ut` - Thông tin về kết nối đến ut.edu.vn

**Tính năng:**
- Xử lý nhiều client đồng thời
- Hiển thị thông tin client (IP, port, thời gian)
- Response HTML đầy đủ
- Log requests

### 📧 SMTP Server (Port 25)

**SMTP Commands hỗ trợ:**
- `HELO/EHLO` - Greeting
- `MAIL FROM:` - Sender address
- `RCPT TO:` - Recipient address
- `DATA` - Email content
- `QUIT` - Disconnect
- `NOOP` - No operation
- `RSET` - Reset session

**Tính năng:**
- Nhận và lưu trữ email
- Hiển thị log emails nhận được
- Hỗ trợ SMTP protocol cơ bản

### 🔗 UT Client (ut.edu.vn)

**Test thực hiện:**
- Kết nối TCP đến 115.78.73.226:80
- Gửi HTTP GET request
- Phân tích HTTP response
- Hiển thị thời gian kết nối
- Test multiple endpoints

## ⚙️ Cấu Hình

### Ports mặc định:
- **HTTP Server**: 80 (fallback: 8080)
- **SMTP Server**: 25 (fallback: 2525)
- **UT Target**: 115.78.73.226:80

### Lưu ý về Ports:
- Port 80 và 25 cần quyền Administrator trên Windows
- Nếu không có quyền Administrator, chương trình sẽ tự động chuyển sang port thay thế
- Port 80 có thể bị chiếm bởi IIS hoặc Apache

## 🧪 Test Scenarios

### Scenario 1: Basic HTTP Test
1. Khởi động HTTP server
2. Mở browser, truy cập http://localhost:80
3. Click các link khác nhau
4. Kiểm tra log trong console

### Scenario 2: SMTP Test
1. Khởi động SMTP server
2. Sử dụng telnet hoặc mail client để gửi email:
```
telnet localhost 25
HELO test.com
MAIL FROM: <test@example.com>
RCPT TO: <user@domain.com>
DATA
Subject: Test Email

This is a test message.
.
QUIT
```

### Scenario 3: UT Website Test
1. Chạy ut_client.py
2. Xem kết quả kết nối đến ut.edu.vn
3. Phân tích response time và content

### Scenario 4: Combined Test
1. Khởi động tất cả servers
2. Test HTTP và SMTP đồng thời
3. Chạy UT client test
4. Kiểm tra trạng thái tất cả services

## 🐛 Troubleshooting

### Lỗi thường gặp:

#### "Permission denied" hoặc "Access denied"
- **Nguyên nhân**: Không có quyền Administrator
- **Giải pháp**: Chạy CMD/PowerShell với "Run as Administrator"

#### "Address already in use"
- **Nguyên nhân**: Port đã được sử dụng
- **Giải pháp**: 
  - Dừng ứng dụng đang sử dụng port
  - Hoặc chương trình sẽ tự động dùng port thay thế

#### "Connection refused" khi test ut.edu.vn
- **Nguyên nhân**: 
  - Không có kết nối internet
  - Firewall chặn
  - Server ut.edu.vn không hoạt động
- **Giải pháp**: Kiểm tra kết nối mạng và firewall

#### HTTP Server không truy cập được từ máy khác
- **Nguyên nhân**: Windows Firewall
- **Giải pháp**: 
  - Cho phép Python qua Windows Firewall
  - Hoặc tạo rule cho port 80/8080

## 📈 Monitoring

### Thông tin được log:
- **HTTP Server**: Client IP, request path, response time
- **SMTP Server**: Email sender, recipients, content preview
- **UT Client**: Connection time, response size, status codes

### Cách xem logs:
- Logs hiển thị real-time trong console
- SMTP emails được lưu trong memory (mail_storage array)

## 🔒 Security Notes

**⚠️ Chú ý bảo mật:**
- Đây là ứng dụng demo, không dùng cho production
- SMTP server không có authentication
- HTTP server không có SSL/TLS
- Không có rate limiting hoặc input validation

## 🚀 Nâng Cao

### Có thể mở rộng:
1. **SSL/TLS** cho HTTPS và SMTPS
2. **Authentication** cho SMTP
3. **Database** lưu trữ emails
4. **Web interface** quản lý emails
5. **Log files** thay vì console
6. **Configuration file** cho settings
7. **API endpoints** cho monitoring

### Tích hợp với các tools khác:
- **Wireshark**: Capture network traffic
- **Postman**: Test HTTP APIs
- **Thunderbird**: Test SMTP server
- **curl**: Command line HTTP testing

## 📚 Kiến Thức Liên Quan

Ứng dụng này minh họa:
- **Socket Programming**: TCP client/server
- **HTTP Protocol**: Request/Response model
- **SMTP Protocol**: Email transmission
- **Network Programming**: Multi-threading, error handling
- **System Administration**: Port management, permissions
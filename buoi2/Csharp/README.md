# TCP Chat System

Đây là hệ thống chat TCP client-server được viết bằng C# và .NET.

## Cấu trúc Project

- **TCPServer**: Server lắng nghe kết nối từ clients và chuyển tiếp tin nhắn
- **TCPClient**: Client kết nối đến server để gửi/nhận tin nhắn
- **ChatTCP.sln**: Solution chứa cả 2 projects

## Cách sử dụng

### 1. Build toàn bộ solution
```bash
dotnet build ChatTCP.sln
```

### 2. Chạy Server
Mở terminal thứ nhất và chạy:
```bash
dotnet run --project TCPServer\TCPServer.csproj
```

Server sẽ khởi động và lắng nghe tại địa chỉ `127.0.0.1:8888`

**Các lệnh server:**
- Nhấn `q` để tắt server

### 3. Chạy Client(s)
Mở terminal thứ hai (hoặc nhiều terminal cho nhiều clients):
```bash
dotnet run --project TCPClient\TCPClient.csproj
```

**Các lệnh client:**
- `/connect <ip> <port>` - Kết nối đến server
  - Ví dụ: `/connect 127.0.0.1 8888`
- `/disconnect` - Ngắt kết nối
- `/quit` - Thoát ứng dụng
- `<tin nhắn>` - Gửi tin nhắn đến chat

## Ví dụ sử dụng

### Terminal 1 (Server):
```
=== TCP Chat Server ===
Press 'q' to quit server
========================
Server started on 127.0.0.1:8888
Waiting for clients...
Client connected: 127.0.0.1
Total clients: 1
[127.0.0.1]: Hello from client 1!
Client connected: 127.0.0.1
Total clients: 2
[127.0.0.1]: Hello from client 2!
```

### Terminal 2 (Client 1):
```
=== TCP Chat Client ===
Commands:
  /connect <ip> <port> - Connect to server
  /disconnect - Disconnect from server
  /quit - Exit application
  <message> - Send message to chat
========================
> /connect 127.0.0.1 8888
Connected to server 127.0.0.1:8888
> Hello from client 1!
[127.0.0.1]: Hello from client 2!
> Nice to meet you!
```

### Terminal 3 (Client 2):
```
=== TCP Chat Client ===
Commands:
  /connect <ip> <port> - Connect to server
  /disconnect - Disconnect from server
  /quit - Exit application
  <message> - Send message to chat
========================
> /connect 127.0.0.1 8888
Connected to server 127.0.0.1:8888
[127.0.0.1]: Hello from client 1!
> Hello from client 2!
[127.0.0.1]: Nice to meet you!
> Great to chat with you!
```

## Tính năng

- **Multi-client support**: Server có thể xử lý nhiều clients đồng thời
- **Real-time messaging**: Tin nhắn được gửi đến tất cả clients khác
- **Connection management**: Tự động xử lý khi client disconnect
- **Simple commands**: Giao diện dòng lệnh đơn giản
- **Error handling**: Xử lý lỗi kết nối và network

## Kiến trúc kỹ thuật

### Server (TCPServer)
- Sử dụng `TcpListener` để lắng nghe kết nối
- Tạo thread riêng cho mỗi client
- Broadcast tin nhắn đến tất cả clients
- Quản lý danh sách clients đang kết nối

### Client (TCPClient)
- Sử dụng `TcpClient` để kết nối đến server
- Thread riêng để nhận tin nhắn từ server
- Giao diện command-line để tương tác
- Xử lý các lệnh kết nối và gửi tin nhắn

## Lưu ý

- Server mặc định chạy trên port 8888
- Có thể kết nối từ nhiều máy khác nhau bằng cách thay đổi IP
- Code có một số warnings về nullable types (không ảnh hưởng đến chức năng)
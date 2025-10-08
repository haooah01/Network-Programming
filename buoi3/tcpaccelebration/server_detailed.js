// =============================================================================
// TCP ECHO SERVER - PHÂN TÍCH CHI TIẾT
// =============================================================================

const net = require('net');  // Import module TCP networking của Node.js

// Lấy port từ environment variable hoặc mặc định 7000
// process.env.PORT cho phép thay đổi port khi deploy
const port = process.env.PORT || 7000;

console.log('🚀 Khởi tạo TCP Echo Server...');
console.log(`📍 Port được cấu hình: ${port}`);

// Tạo TCP server với callback function được gọi mỗi khi có connection mới
const server = net.createServer((socket) => {
    console.log(`🔗 Có client kết nối từ: ${socket.remoteAddress}:${socket.remotePort}`);
    console.log(`📊 Tổng số connections hiện tại: ${server.connections || 'N/A'}`);
    
    // Lắng nghe sự kiện 'data' - khi client gửi dữ liệu đến
    socket.on('data', (data) => {
        console.log(`📥 Nhận được ${data.length} bytes từ ${socket.remoteAddress}`);
        console.log(`📝 Nội dung: "${data.toString().substring(0, 50)}${data.length > 50 ? '...' : ''}"`);
        
        // Echo lại dữ liệu cho client (TCP Echo Server principle)
        socket.write(data);
        console.log(`📤 Đã echo ${data.length} bytes về client`);
    });
    
    // Lắng nghe sự kiện 'error' - khi có lỗi socket
    socket.on('error', (error) => {
        console.error(`❌ Socket error từ ${socket.remoteAddress}: ${error.message}`);
    });
    
    // Lắng nghe sự kiện 'close' - khi client ngắt kết nối
    socket.on('close', (hadError) => {
        console.log(`🔌 Client ${socket.remoteAddress} đã ngắt kết nối ${hadError ? '(có lỗi)' : '(bình thường)'}`);
    });
    
    // Lắng nghe sự kiện 'timeout' - khi connection bị timeout
    socket.on('timeout', () => {
        console.log(`⏰ Connection timeout từ ${socket.remoteAddress}`);
        socket.end();
    });
});

// Lắng nghe trên tất cả interfaces (0.0.0.0) và port đã chỉ định
// Callback được gọi khi server sẵn sàng nhận connections
server.listen(port, '0.0.0.0', () => {
    console.log(`✅ Echo server đang chạy trên port ${port}`);
    console.log(`🌐 Có thể truy cập từ: localhost:${port} hoặc <IP>:${port}`);
    console.log('💡 Server sẽ echo (phản hồi) lại mọi dữ liệu nhận được');
});

// Lắng nghe sự kiện server-level errors
server.on('error', (error) => {
    if (error.code === 'EADDRINUSE') {
        console.error(`❌ Port ${port} đã được sử dụng bởi process khác`);
        console.log('💡 Thử: netstat -ano | findstr :7000  (Windows)');
        console.log('💡 Hoặc: lsof -i :7000  (Linux/Mac)');
    } else {
        console.error(`❌ Server error: ${error.message}`);
    }
    process.exit(1);
});

// Graceful shutdown khi nhận SIGINT (Ctrl+C)
process.on('SIGINT', () => {
    console.log('\n🛑 Đang shutdown server...');
    server.close(() => {
        console.log('✅ Server đã được đóng an toàn');
        process.exit(0);
    });
});
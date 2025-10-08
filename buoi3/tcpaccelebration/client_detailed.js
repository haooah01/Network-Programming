// =============================================================================
// TCP CLIENT - NAGLE vs TCP_NODELAY LATENCY TEST
// =============================================================================

const net = require('net');
const { performance } = require('perf_hooks');  // High-resolution time measurement

console.log('🔬 Khởi tạo TCP Latency Test Client...');

// Parse command line arguments
// process.argv = ['node', 'script.js', '--arg1=value1', '--arg2=value2', ...]
const args = Object.fromEntries(
    process.argv.slice(2).map(kv => {
        const [k, v] = kv.replace(/^--/, '').split('=');
        return [k, v ?? true];  // Nếu không có value, set = true
    })
);

console.log('⚙️ Tham số được truyền vào:', args);

// Cấu hình test parameters
const host = args.host || '127.0.0.1';
const port = parseInt(args.port || '7000', 10);
const nodelay = String(args.nodelay || 'false') === 'true';  // Convert string to boolean
const n = parseInt(args.n || '200', 10);          // Số lần test
const gap = parseInt(args.ms || '10', 10);        // Khoảng cách giữa các requests (ms)
const size = parseInt(args.size || '16', 10);     // Kích thước payload (bytes)

console.log('📋 Cấu hình test:');
console.log(`   🎯 Target: ${host}:${port}`);
console.log(`   🔧 TCP_NODELAY: ${nodelay ? 'ON (Disable Nagle)' : 'OFF (Enable Nagle)'}`);
console.log(`   📊 Số lần test: ${n}`);
console.log(`   ⏱️ Khoảng cách: ${gap}ms`);
console.log(`   📦 Payload size: ${size} bytes`);

// Tạo payload với kích thước xác định
// 0x61 = ASCII 'a', tạo buffer chứa toàn ký tự 'a'
const payload = Buffer.alloc(size, 0x61);
console.log(`📝 Payload sample: "${payload.toString().substring(0, 20)}${size > 20 ? '...' : ''}"`);

const rtts = [];  // Mảng lưu trữ Round Trip Time của mỗi request

console.log('\n🔌 Đang kết nối đến server...');

// Tạo connection đến server
const sock = net.createConnection({ host, port }, () => {
    console.log(`✅ Đã kết nối thành công đến ${host}:${port}`);
    
    // *** QUAN TRỌNG: Thiết lập TCP_NODELAY ***
    // setNoDelay(true) = disable Nagle algorithm
    // setNoDelay(false) = enable Nagle algorithm (default)
    sock.setNoDelay(nodelay);
    console.log(`🔧 TCP_NODELAY được set: ${nodelay}`);
    
    if (nodelay) {
        console.log('   ➤ Nagle algorithm bị VÔ HIỆU HÓA');
        console.log('   ➤ Dữ liệu sẽ được gửi NGAY LẬP TỨC');
        console.log('   ➤ Thích hợp cho ứng dụng real-time, gaming');
    } else {
        console.log('   ➤ Nagle algorithm được KÍCH HOẠT');
        console.log('   ➤ Dữ liệu có thể bị TRÌ HOÃN để gộp gói');
        console.log('   ➤ Tiết kiệm bandwidth nhưng tăng latency');
    }
    
    console.log('\n🚀 Bắt đầu test latency...\n');
    
    let i = 0;  // Counter cho số lần test đã thực hiện
    
    // Hàm đệ quy để gửi từng request
    function sendOne() {
        if (i >= n) {
            // Hoàn thành tất cả test, in kết quả
            console.log(`\n✅ Hoàn thành ${n} lần test!`);
            console.log('📊 Thống kê RTT:');
            
            const avgRTT = rtts.reduce((a, b) => a + b) / rtts.length;
            const minRTT = Math.min(...rtts);
            const maxRTT = Math.max(...rtts);
            
            console.log(`   📈 Trung bình: ${avgRTT.toFixed(3)}ms`);
            console.log(`   📉 Thấp nhất: ${minRTT.toFixed(3)}ms`);
            console.log(`   📊 Cao nhất: ${maxRTT.toFixed(3)}ms`);
            
            // Output JSON để script khác có thể parse
            console.log('\n📄 Kết quả JSON:');
            console.log(JSON.stringify({
                mode: nodelay ? 'tcp_nodelay_on' : 'nagle_on',
                config: { host, port, nodelay, n, gap, size },
                stats: { avg: avgRTT, min: minRTT, max: maxRTT },
                rtts_ms: rtts
            }, null, 2));
            
            sock.end();  // Đóng connection
            return;
        }
        
        // Ghi lại thời điểm bắt đầu gửi request
        const t0 = performance.now();  // High-resolution timestamp
        
        // Đăng ký listener một lần cho response
        sock.once('data', (response) => {
            const t1 = performance.now();  // Thời điểm nhận response
            const rtt = t1 - t0;          // Tính Round Trip Time
            
            rtts.push(rtt);  // Lưu RTT vào mảng
            
            console.log(`[${String(i + 1).padStart(3)}/${n}] RTT: ${rtt.toFixed(3)}ms | Received: ${response.length} bytes`);
            
            // Lên lịch gửi request tiếp theo sau 'gap' milliseconds
            setTimeout(sendOne, gap);
        });
        
        // Gửi payload đến server
        sock.write(payload);
        i++;  // Tăng counter
    }
    
    // Bắt đầu chuỗi test
    sendOne();
});

// Xử lý lỗi connection
sock.on('error', (error) => {
    console.error(`❌ Connection error: ${error.message}`);
    console.log('💡 Đảm bảo server đang chạy trước khi chạy client');
    process.exit(1);
});

sock.on('close', () => {
    console.log('🔌 Connection đã được đóng');
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Đang dừng test...');
    sock.end();
    process.exit(0);
});
Kết quả (tóm tắt)

- Tập tin gốc: `my_results.json`
- Tập tin chú giải: `my_results_annotated.json`
- Lý do lỗi chính: tất cả các trial trả về `connection_refused` — nghĩa là không có server lắng nghe trên `127.0.0.1:7000` tại thời điểm chạy.

Chi tiết và hướng xử lý

1. Kiểm tra xem server đã được start chưa (ví dụ chạy `run_with_local_server.py`):

```powershell
python "d:\\Documents-D\\VS Code\\network programming\\tcp optimizer\\run_with_local_server.py"
```

2. Hoặc khởi động server bằng tay trong một terminal và sau đó chạy optimizer trong terminal khác:

```powershell
# Start server (one window)
python "d:\\Documents-D\\VS Code\\network programming\\tcp optimizer\\run_with_local_server.py"

# Run optimizer (another window) — ví dụ của bạn
python "d:\\Documents-D\\VS Code\\network programming\\tcp optimizer\\tcp_optimizer.py" --host 127.0.0.1 --port 7000 --duration 5 --sndbufs 16384,32768,65536 --rcvbufs 16384,32768,65536 --test-nodelay --out "d:\\Documents-D\\VS Code\\network programming\\tcp optimizer\\my_results.json"
```

3. Nếu vẫn bị `connection_refused`, kiểm tra `netstat -ano | Select-String ":7000"` để thấy process nào (nếu có) đang listen, và dùng `Test-NetConnection -ComputerName 127.0.0.1 -Port 7000` để kiểm tra kết nối TCP.

Ghi chú thêm

- Tôi đã tạo `my_results_annotated.json` với ghi chú cho từng trial (snd/rcv/nodelay và lý do lỗi). Mở file đó để xem từng trial được gán cấu hình nào.
- Nếu bạn muốn, tôi có thể: (A) tự chạy server + optimizer với cấu hình của bạn và đưa ra kết quả mới; (B) chỉnh script để ghi chú trực tiếp vào `my_results.json` thay vì tạo file mới; hoặc (C) chuyển annotation sang định dạng JSONC (có comment) nếu bạn muốn xem comment trực tiếp trong file.

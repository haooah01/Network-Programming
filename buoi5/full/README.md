# FullAsyncDemo

Demo tổng hợp các mẫu async/await trong C#:
- Gọi web không chặn UI
- Xử lý tính toán nặng bằng Task.Run
- Truy vấn dữ liệu song song với Task.WhenAll, LINQ
- Xử lý từng tác vụ khi hoàn thành với Task.WhenAny
- Đếm số lần xuất hiện ".NET" trên nhiều website
- Truy vấn danh sách User

## Cách chạy
```powershell
cd buoi5\full
 dotnet build
 dotnet run
```

## Kết quả
Ứng dụng sẽ in ra kết quả từng bước xử lý bất đồng bộ, truy vấn web, dữ liệu và task song song.

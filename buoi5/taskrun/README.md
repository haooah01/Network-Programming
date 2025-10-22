# TaskRunApp

Demo sử dụng `Task.Run(async () => await GetDataAsync()).GetAwaiter().GetResult()` để thực thi phương thức bất đồng bộ trên thread pool, tránh deadlock.

## Mô tả
- Hàm `GetDataAsync()` trả về chuỗi sau 1 giây.
- Trong hàm `Main`, gọi bất đồng bộ qua `Task.Run` và lấy kết quả bằng `GetAwaiter().GetResult()`.
- Mẫu này giúp tránh deadlock khi gọi async từ context đồng bộ, nhưng có chi phí lên lịch cho thread pool.

## Cách chạy
```powershell
cd buoi5\taskrun
 dotnet build
 dotnet run
```

## Kết quả
Ứng dụng sẽ in ra kết quả trả về từ hàm bất đồng bộ.

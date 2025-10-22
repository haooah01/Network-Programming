# GetAwaiterGetResultApp

Demo sử dụng `Task.GetAwaiter().GetResult()` để lấy kết quả từ một tác vụ bất đồng bộ khi không thể dùng `await`.

## Mô tả
- Hàm `GetDataAsync()` trả về chuỗi sau 1 giây.
- Trong hàm `Main`, gọi bất đồng bộ và lấy kết quả bằng `GetAwaiter().GetResult()`.

## Cách chạy
```powershell
cd buoi5\getawaygetresult
 dotnet build
 dotnet run
```

## Kết quả
Ứng dụng sẽ in ra kết quả trả về từ hàm bất đồng bộ.

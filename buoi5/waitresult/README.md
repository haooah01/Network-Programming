# WaitResultApp

Demo sử dụng `Wait()` và `Result` để lấy kết quả từ một tác vụ bất đồng bộ, minh họa vấn đề với AggregateException.

## Mô tả
- Hàm `GetDataAsync()` trả về chuỗi sau 1 giây hoặc ném lỗi.
- Trong hàm `Main`, gọi bất đồng bộ và lấy kết quả bằng `Wait()` và `Result`.
- Demo lỗi để thấy ngoại lệ được gói trong `AggregateException`.

## Cách chạy
```powershell
cd buoi5\waitresult
 dotnet build
 dotnet run
```

## Kết quả
Ứng dụng sẽ in ra kết quả trả về và demo lỗi với AggregateException.

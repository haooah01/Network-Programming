# ToListApp

Ứng dụng console demo xử lý bất đồng bộ với Task.WhenAny và danh sách Task.

## Mô tả
- Tạo danh sách các userId.
- Khởi tạo các tác vụ lấy thông tin user bất đồng bộ.
- Xử lý từng tác vụ khi hoàn thành (không chờ tuần tự).
- In ra thông tin user đã xử lý.

## Cách chạy
```powershell
cd buoi5\tolistapp
 dotnet build
 dotnet run
```

## Kết quả
Ứng dụng sẽ in ra từng user được xử lý ngay khi tác vụ hoàn thành, cho đến khi hết danh sách.

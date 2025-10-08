# 📝 HƯỚNG DẪN PUSH LÊN GITHUB

## Bước 1: Tạo Repository trên GitHub
1. Truy cập https://github.com
2. Đăng nhập vào tài khoản GitHub của bạn
3. Click vào nút "+" ở góc phải -> "New repository"
4. Đặt tên repository: `tcp-networking-lab` (hoặc tên khác)
5. Thêm description: "Comprehensive TCP networking laboratory with latency, throughput, and keep-alive experiments"
6. Chọn "Public" hoặc "Private" tùy ý
7. KHÔNG tick "Add a README file" (vì chúng ta đã có)
8. Click "Create repository"

## Bước 2: Kết nối local repo với GitHub
Sau khi tạo repo, GitHub sẽ hiển thị commands. Chạy:

```bash
# Thay YOUR_USERNAME bằng username GitHub của bạn
git remote add origin https://github.com/YOUR_USERNAME/tcp-networking-lab.git

# Hoặc nếu dùng SSH:
git remote add origin git@github.com:YOUR_USERNAME/tcp-networking-lab.git
```

## Bước 3: Push code lên GitHub
```bash
git branch -M main
git push -u origin main
```

## Bước 4: Xác minh
- Truy cập repository trên GitHub
- Kiểm tra tất cả files đã được upload
- README.md sẽ hiển thị tự động

## 🎯 Repository URL sẽ là:
https://github.com/YOUR_USERNAME/tcp-networking-lab

## 📊 Thống kê project hiện tại:
- 26 files đã được commit
- 3,956 dòng code
- Bao gồm: Node.js, Python, documentation
- Complete với automation và analysis tools

## 🚀 Sau khi push thành công:
1. Cập nhật URL trong package.json
2. Share repository với classmates
3. Có thể tạo releases với git tags
4. Setup GitHub Actions cho CI/CD (tùy chọn)

==============================================
✅ Project đã sẵn sàng để push lên GitHub!
==============================================
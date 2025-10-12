# Test Certificate Hướng Dẫn

Tài liệu này tóm tắt quy trình tạo và sử dụng chứng chỉ để ký ClickOnce, bao gồm cả phương án dùng chứng chỉ thật từ CA và chứng chỉ tự ký để kiểm thử.

## Mục tiêu

- Loại bỏ cảnh báo “Unknown Publisher” khi phát hành ứng dụng ClickOnce.
- Hiển thị “Verified Publisher: <tên bạn>” thông qua chứng chỉ code signing hợp lệ.

## Chọn nhà cung cấp chứng chỉ (CA)

| Nhà cung cấp         | Đặc điểm nổi bật                                        | Link                                                                      |
| -------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------- |
| **DigiCert**         | Uy tín cao nhất, Microsoft tin dùng cho Windows signing | [digicert.com/code-signing](https://www.digicert.com/code-signing)        |
| **Sectigo (Comodo)** | Giá rẻ hơn, phổ biến với dev indie                      | [sectigo.com/code-signing](https://sectigo.com/code-signing-certificates) |
| **GlobalSign**       | Hỗ trợ doanh nghiệp lớn, EV code signing                | [globalsign.com](https://www.globalsign.com)                              |
| **SSL.com**          | Cung cấp chứng chỉ cá nhân và tổ chức, dễ mua           | [ssl.com/code-signing](https://www.ssl.com/code-signing-certificates)     |

💡 Nếu chỉ kiểm thử hoặc phát hành nội bộ, bạn có thể dùng chứng chỉ tự ký (ví dụ bằng tập lệnh `generate-test-clickonce-cert.ps1` bên dưới).

## Quy trình đăng ký chứng chỉ từ CA

1. **Chuẩn bị hồ sơ**  
   - Cá nhân: CMND/hộ chiếu và xác minh email.  
   - Doanh nghiệp: Giấy phép kinh doanh, email domain, xác minh qua điện thoại.  
   - EV Code Signing: Doanh nghiệp hợp pháp, quy trình xác minh trực tiếp, lưu trên USB token.

2. **Gửi yêu cầu chứng chỉ (CSR)**  
   - Tạo CSR bằng `makecert` hoặc `openssl`.  
   - Điền thông tin: `CN` (tên), `O` (tổ chức), `C` (quốc gia, ví dụ VN).

3. **Nhận và kết hợp chứng chỉ**  
   - CA sẽ gửi `.cer` hoặc `.pfx`.  
   - Nếu nhận `.cer`, dùng `openssl pkcs12 -export -out mycert.pfx -inkey mykey.pem -in mycert.cer` để tạo `.pfx`.

## Ký ClickOnce bằng chứng chỉ

1. **Import chứng chỉ**  
   - `certmgr.msc` → Personal → Certificates → Import `.pfx`.  
   - Hoặc Visual Studio → Project → Properties → Signing → chọn `.pfx`.

2. **Ký manifest**  
   - Visual Studio tự động ký khi publish.  
   - Hoặc dùng Mage:
     ```powershell
     mage -Sign MyApp.application -CertFile mycert.pfx -Password mypassword
     mage -Sign MyApp.exe.manifest -CertFile mycert.pfx -Password mypassword
     ```

3. **Kiểm tra kết quả**  
   - Chuột phải file `.application`/`.exe` → Properties → Digital Signatures.  
   - Cài đặt sẽ hiển thị “Verified Publisher”.

## Tạo chứng chỉ tự ký để kiểm thử

Sử dụng script `generate-test-clickonce-cert.ps1`:

```powershell
.\generate-test-clickonce-cert.ps1 `
    -PublisherName "Demo Publisher" `
    -OutputDirectory "." `
    -ValidYears 1
```

- Script tạo chứng chỉ trong kho CurrentUser\My và xuất `.pfx` + `.cer` trong thư mục hiện tại.  
- Nếu không truyền `-Password`, script sẽ yêu cầu nhập mật khẩu để bảo vệ file `.pfx`.  
- Dùng file `.pfx` này cho mục đích test nội bộ; không dùng để phát hành thương mại.

## Quy trình cũ với MakeCert/PVK2PFX

Các phiên bản Visual Studio/Windows SDK cũ cung cấp bộ đôi `makecert.exe` và `pvk2pfx.exe`. Nếu bạn vẫn còn các công cụ này (nằm trong `C:\Program Files (x86)\Microsoft SDKs\Windows\...\bin\`), bạn có thể tạo chứng chỉ tự ký theo từng bước sau:

1. **Chuẩn bị thư mục tiện dụng**
   ```cmd
   mkdir C:\MakeCert
   copy "C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A\bin\makecert.exe" C:\MakeCert
   copy "C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A\bin\pvk2pfx.exe" C:\MakeCert
   cd /d C:\MakeCert
   ```

2. **Tạo chứng chỉ (`.cer`) và private key (`.pvk`)**
   ```cmd
   makecert -r -pe -n "CN=YourName-InternalTestCert" -b 10/11/2025 -e 10/11/2028 -sky exchange -sv mykey.pvk mycert.cer
   ```
   - `-r`: chứng chỉ tự ký.  
   - `-pe`: cho phép export private key.  
   - `-n`: Common Name hiển thị trong store.  
   - `-b`/`-e`: ngày bắt đầu/kết thúc (mm/dd/yyyy).  
   - `-sky exchange`: tạo khóa exchange.  
   - `-sv`: đường dẫn file private key `.pvk`.  
   - `mycert.cer`: file public key nhận được sau bước này.

3. **Gộp thành `.pfx` sử dụng `pvk2pfx`**
   ```cmd
   pvk2pfx -pvk mykey.pvk -spc mycert.cer -pfx mycert.pfx -po mypassword
   ```
   - `-po mypassword`: mật khẩu bảo vệ file `.pfx`.

4. **Import và sử dụng**
   - Windows: `certmgr.msc` → Personal → Certificates → Import `mycert.pfx`.  
   - Visual Studio: Project → Properties → Signing → Sign the ClickOnce manifests → Select from file → `mycert.pfx`.

5. **Tùy chọn**
   - Xem thông tin: `certutil -dump mycert.cer`.  
   - Xóa chứng chỉ test khỏi store khi không cần: `certmgr.msc` → Personal → Certificates → Delete.

> Lưu ý: các bản Windows SDK mới đã ngừng cung cấp `makecert`. Khi thiếu công cụ, hãy dùng script PowerShell ở trên (`New-SelfSignedCertificate`) để đạt cùng mục đích.

## Lưu ý

- Thời hạn chứng chỉ: 1–3 năm (đối với CA).  
- Khi chứng chỉ hết hạn cần ký lại bản cập nhật.  
- Bảo mật file `.pfx`, không chia sẻ công khai.

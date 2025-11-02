# Hướng dẫn Import Khách hàng từ AGRIBANK

## Cách 1: Import từ Giao diện Web (Khuyến nghị)

### Bước 1: Chuẩn bị dữ liệu
1. Mở hệ thống **AGRIBANK**
2. Tìm và chọn thông tin khách hàng cần export
3. **Copy toàn bộ dữ liệu** (bao gồm cả dòng tiêu đề/header)
   - Sử dụng Ctrl+A để chọn tất cả
   - Hoặc kéo chuột chọn vùng dữ liệu
   - Nhấn Ctrl+C để copy

### Bước 2: Lưu file
1. Mở **Notepad** (hoặc text editor bất kỳ)
2. **Paste** dữ liệu vừa copy (Ctrl+V)
3. Chọn **File → Save As...**
4. Chọn **Encoding: UTF-8**
5. Đặt tên file và lưu với extension:
   - `.tsv` (ví dụ: `khachhang.tsv`)
   - Hoặc `.txt` (ví dụ: `khachhang.txt`)

### Bước 3: Import vào hệ thống
1. Vào trang **Khách hàng** trong hệ thống
2. Nhấn nút **"Import AGRIBANK"** (màu xanh dương, icon ngân hàng)
3. Trong modal hiện ra:
   - Nhấn **"Chọn file"**
   - Chọn file TSV/TXT vừa lưu
   - Nhấn nút **"Import"**
4. Chờ hệ thống xử lý (hiện spinner loading)
5. Xem kết quả:
   - **Khách hàng mới**: Số lượng khách hàng được thêm mới
   - **Đã cập nhật**: Số lượng khách hàng được cập nhật (CMND đã tồn tại)
   - **Lỗi**: Số lượng dòng bị lỗi (nếu có)

### Bước 4: Kiểm tra
1. Nhấn nút **"Tải lại trang"** trong kết quả import
2. Kiểm tra danh sách khách hàng đã được cập nhật
3. Tìm kiếm khách hàng vừa import để xác nhận

## Các trường dữ liệu được import

| Thông tin | Từ AGRIBANK | Ghi chú |
|-----------|-------------|---------|
| Mã khách hàng | custno | |
| Họ và tên | nmloc | Tiếng Việt có dấu |
| Số CMND/CCCD | regno | Bắt buộc |
| Ngày sinh | name_1 | Format: YYYYMMDD → dd/mm/yyyy |
| Giới tính | name_3 | Nam/Nữ |
| Số điện thoại | name_4 | |
| Địa chỉ | addr1loc | |
| Ngày cấp CCCD | issuedt1 | Format: YYYYMMDD → dd/mm/yyyy |
| Nơi cấp CCCD | issueby1 | Tự động map mã → tên |
| Nghề nghiệp | profnm | |
| Email | emailaddr | |

## Lưu ý quan trọng

### ✅ Yêu cầu file
- **Encoding**: UTF-8 (quan trọng cho tiếng Việt)
- **Format**: Tab-separated (TSV)
- **Extension**: .tsv hoặc .txt
- **Header**: Phải có dòng đầu tiên là tiêu đề

### ✅ Duplicate handling
- Nếu số **CMND/CCCD đã tồn tại** → Hệ thống sẽ **cập nhật** thông tin
- Nếu chưa tồn tại → Tạo khách hàng **mới**

### ✅ Định dạng ngày
- AGRIBANK export: `YYYYMMDD` (ví dụ: 19700101)
- Hệ thống tự động convert sang: `dd/mm/yyyy` (01/01/1970)

### ✅ Validation
- **Họ tên**: Bắt buộc
- **Số CMND/CCCD**: Bắt buộc, unique
- **Số điện thoại**: 10 số, bắt đầu bằng 0
- **Ngày sinh**: Không được trong tương lai
- **Ngày cấp CCCD**: Không được trong tương lai

## Xử lý lỗi thường gặp

### Lỗi: "File phải có định dạng .tsv hoặc .txt"
**Giải pháp**: Đổi tên file, đảm bảo có extension .tsv hoặc .txt

### Lỗi: "Thiếu họ tên"
**Giải pháp**: Kiểm tra cột `nmloc` trong file có dữ liệu không

### Lỗi: "Thiếu số CMND/CCCD"
**Giải pháp**: Kiểm tra cột `regno` trong file có dữ liệu không

### Lỗi: "File không có dữ liệu"
**Giải pháp**:
- Đảm bảo file có ít nhất 2 dòng (header + data)
- Kiểm tra lại việc copy/paste từ AGRIBANK

### Lỗi: Tiếng Việt bị lỗi font
**Giải pháp**:
- Khi lưu file trong Notepad, chọn **Encoding: UTF-8**
- Không chọn ANSI hoặc Unicode

## Ví dụ minh họa

### Dữ liệu trong AGRIBANK (sau khi copy):
```
custno	nm	nmloc	name_1	name_3	name_4	regno	issuedt1	issueby1	addr1loc
7202000699174	TRAN NGOC THUY	Trần Ngọc Thủy	19700101	Nữ	0766939319	022189125	20010417	145	P1 Quận 3 TPHCM
```

### Kết quả trong hệ thống:
- **Mã KH**: 7202000699174
- **Họ tên**: Trần Ngọc Thủy
- **Ngày sinh**: 01/01/1970
- **Giới tính**: Nữ
- **SĐT**: 0766939319
- **CMND**: 022189125
- **Ngày cấp**: 17/04/2001
- **Nơi cấp**: Cục Cảnh sát ĐKQL cư trú và DLQG về dân cư
- **Địa chỉ**: P1 Quận 3 TPHCM

## Tips & Tricks

### 💡 Import hàng loạt
- Có thể import nhiều khách hàng cùng lúc
- Chỉ cần chọn/copy tất cả dòng dữ liệu từ AGRIBANK
- Hệ thống tự động xử lý từng dòng

### 💡 Cập nhật thông tin
- Nếu cần cập nhật thông tin khách hàng đã có
- Chỉ cần import lại với cùng số CMND/CCCD
- Hệ thống sẽ tự động cập nhật

### 💡 Kiểm tra trước khi import
- Mở file TSV bằng Excel để xem trước
- Đảm bảo dữ liệu có cột phân tách rõ ràng
- Kiểm tra không có ký tự đặc biệt lạ

## Liên hệ hỗ trợ

Nếu gặp vấn đề:
1. Chụp màn hình lỗi
2. Gửi file TSV mẫu (đã xóa thông tin nhạy cảm)
3. Mô tả chi tiết bước đã thực hiện

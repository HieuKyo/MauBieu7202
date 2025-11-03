# Hướng dẫn Import dữ liệu khách hàng từ AGRIBANK (TSV Format)

## Tổng quan

Hệ thống đã được cập nhật để hỗ trợ import dữ liệu khách hàng từ clipboard AGRIBANK với định dạng TSV (Tab-Separated Values).

## Các thay đổi đã thực hiện

### 1. Model Customer

Đã thêm các trường mới vào model `Customer`:

```python
# Giấy tờ tùy thân
ma_noi_cap_cmnd = models.CharField(max_length=10, blank=True)  # Mã nơi cấp CCCD
so_ho_chieu = models.CharField(max_length=20, blank=True)       # Số hộ chiếu

# Địa chỉ hành chính
ma_tinh = models.CharField(max_length=10, blank=True)           # Mã tỉnh/thành
ma_quan_huyen = models.CharField(max_length=10, blank=True)     # Mã quận/huyện
ma_phuong_xa = models.CharField(max_length=10, blank=True)      # Mã phường/xã

# Quốc tịch và thuế
quoc_tich = models.CharField(max_length=10, blank=True, default='VN')
ma_so_thue = models.CharField(max_length=20, blank=True)
```

### 2. Mapping dữ liệu AGRIBANK

File `templates_app/issueby_mapping.py` chứa bảng mapping mã nơi cấp CCCD:

| Mã  | Nơi cấp |
|-----|---------|
| 145 | Cục Cảnh sát ĐKQL cư trú và DLQG về dân cư |
| 001 | Bộ Công An |
| 002 | Công an TP Hà Nội |
| 003 | Công an TP Hồ Chí Minh |
| ... | ... |

### 3. Mapping các trường dữ liệu

| Trường AGRIBANK | Mô tả | Trường Customer | Ghi chú |
|----------------|-------|-----------------|---------|
| custno | Mã khách hàng | ma_khach_hang, cif | |
| nmloc | Họ tên (tiếng Việt) | ho_ten | |
| name_1 | Ngày sinh (YYYYMMDD) | ngay_sinh | Convert sang YYYY-MM-DD |
| name_3 | Giới tính | gioi_tinh | |
| name_4 | Số điện thoại | so_dien_thoai | |
| regno | Số CMND/CCCD | so_cmnd | |
| passno | Số hộ chiếu | so_ho_chieu | |
| issuedt1 | Ngày cấp (YYYYMMDD) | ngay_cap_cmnd | Convert sang YYYY-MM-DD |
| issueby1 | Nơi cấp (mã) | ma_noi_cap_cmnd, noi_cap_cmnd | Map mã sang tên |
| addr1loc | Địa chỉ | dia_chi | |
| profnm | Nghề nghiệp | nghe_nghiep | |
| emailaddr | Email | email | |
| province | Mã tỉnh | ma_tinh | |
| district | Mã quận/huyện | ma_quan_huyen | |
| commune_ward | Mã phường/xã | ma_phuong_xa | |
| ctrycdnatl | Quốc tịch | quoc_tich | |
| taxno | Mã số thuế | ma_so_thue | |

## Cách sử dụng

### Phương pháp 1: Sử dụng API endpoint

#### Request
```
POST /api/customers/import/tsv/
Content-Type: multipart/form-data
Authorization: required (login)

Body:
- tsv_file: File TSV (hoặc .txt)
```

#### Response (Success)
```json
{
    "success": true,
    "message": "Import thành công: 5 khách hàng mới, 2 cập nhật",
    "imported": 5,
    "updated": 2,
    "errors": 0,
    "error_details": []
}
```

#### Response (Error)
```json
{
    "success": false,
    "error": "Lỗi khi xử lý file TSV: ...",
    "errors": 3,
    "error_details": [
        "Dòng 5: Thiếu họ tên",
        "Dòng 8: Thiếu số CMND/CCCD"
    ]
}
```

### Phương pháp 2: Sử dụng script command line

```bash
python templates_app/import_tsv.py sample_clipboard_data.txt --user admin
```

#### Ví dụ output:
```
================================================================================
IMPORT KHÁCH HÀNG TỪ FILE TSV
================================================================================
File: sample_clipboard_data.txt
User: admin
================================================================================
✓ Đã thêm: Trần Ngọc Thủy (022189125)

================================================================================
KẾT QUẢ IMPORT
================================================================================
✓ Thành công: 1 khách hàng
✗ Lỗi: 0 dòng
================================================================================
```

## Chuẩn bị dữ liệu

### 1. Copy dữ liệu từ AGRIBANK

1. Mở hệ thống AGRIBANK
2. Chọn thông tin khách hàng cần export
3. Copy toàn bộ dữ liệu (bao gồm header)
4. Paste vào file text editor (Notepad, VS Code, etc.)
5. Lưu file với encoding UTF-8
6. Extension: `.tsv` hoặc `.txt`

### 2. Định dạng file TSV

- Dòng đầu tiên: Header (tên các cột, phân cách bằng Tab)
- Các dòng tiếp theo: Dữ liệu khách hàng
- Phân cách giữa các cột: Tab character (\t)
- Encoding: UTF-8

### Ví dụ cấu trúc file:

```
custno	nm	nmloc	name_1	name_3	name_4	regno	issuedt1	issueby1	addr1loc	profnm
7202000699174	TRAN NGOC THUY	Trần Ngọc Thủy	19700101	Nữ	0766939319	022189125	20010417	145	P1 Quận 3 TPHCM	Khác
```

## Validation

Dữ liệu sẽ được validate theo các quy tắc:

1. **Trường bắt buộc:**
   - Họ tên (nmloc)
   - Số CMND/CCCD (regno)

2. **Định dạng ngày:**
   - Input: YYYYMMDD (ví dụ: 19700101)
   - Chuyển đổi sang: YYYY-MM-DD
   - Validation: Ngày sinh không được trong tương lai
   - Validation: Ngày cấp CCCD không được trong tương lai

3. **Số điện thoại:**
   - Định dạng: 10 số, bắt đầu bằng 0
   - Ví dụ: 0766939319

4. **Duplicate handling:**
   - Nếu số CMND/CCCD đã tồn tại → Cập nhật thông tin
   - Nếu chưa tồn tại → Tạo mới

## Migration Database

Sau khi cập nhật model, cần chạy migration:

```bash
python manage.py makemigrations templates_app
python manage.py migrate
```

## Test

### Sử dụng sample data

File `sample_clipboard_data.txt` đã được tạo sẵn để test:

```bash
python templates_app/import_tsv.py sample_clipboard_data.txt --user admin
```

### Phân tích cấu trúc dữ liệu

```bash
python analyze_clipboard.py
```

Output sẽ hiển thị mapping chi tiết của từng trường.

## Lưu ý

1. **Encoding:** File phải được lưu với encoding UTF-8
2. **Separator:** Sử dụng Tab character, không phải space
3. **Header:** Dòng đầu tiên phải là header chính xác từ AGRIBANK
4. **Ngày tháng:** Format YYYYMMDD (8 ký tự số)
5. **Mã nơi cấp:** Nếu không có trong mapping table, sẽ được lưu dạng "Mã XXX"

## Xử lý lỗi

### Lỗi thường gặp:

1. **"Thiếu họ tên"**
   - Kiểm tra cột `nmloc` có dữ liệu không

2. **"Thiếu số CMND/CCCD"**
   - Kiểm tra cột `regno` có dữ liệu không

3. **"File không có dữ liệu"**
   - Đảm bảo file có ít nhất 2 dòng (header + data)

4. **"File phải có định dạng .tsv hoặc .txt"**
   - Đổi tên file extension

## Tích hợp vào giao diện web

Để thêm nút import TSV vào trang Customer List, cần cập nhật `customer_list.html`:

1. Thêm nút "Import từ AGRIBANK"
2. Thêm modal upload file TSV
3. JavaScript xử lý upload và hiển thị kết quả

## Liên hệ hỗ trợ

Nếu gặp vấn đề, vui lòng cung cấp:
- File TSV mẫu
- Log lỗi
- Screenshot nếu có

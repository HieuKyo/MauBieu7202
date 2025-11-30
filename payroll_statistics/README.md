# Payroll Statistics - App Thống Kê Lương & Thu Hộ

## Mô tả

App **Payroll Statistics** được thiết kế để import và thống kê dữ liệu giao dịch lương và thu hộ từ file Excel/CSV. Hệ thống tự động phân loại giao dịch theo 2 chiều:

- **Chi lương**: Đơn vị trả lương → Nhân viên nhận lương
- **Thu hộ/Khoản trừ**: Đơn vị thu hộ ← Nhân viên bị trừ tiền

## Cấu trúc Database

### Model: PayingUnit (Đơn vị)
- `account_number` (PK): Số tài khoản đơn vị
- `name`: Tên đơn vị (có thể cập nhật sau)
- `created_at`: Ngày tạo
- `updated_at`: Ngày cập nhật

### Model: BeneficiaryAccount (Nhân viên/Người hưởng)
- `unit` (FK → PayingUnit): Đơn vị
- `account_number`: Số tài khoản nhân viên
- `remark_ref`: Nội dung giao dịch mẫu
- `created_at`: Ngày tạo
- `updated_at`: Ngày cập nhật
- **Unique together**: (`unit`, `account_number`)

## Logic Import 2 Chiều

### Dữ liệu đầu vào
File Excel/CSV cần có các cột:
- `facno`: Số tài khoản người chuyển
- `tacno`: Số tài khoản người nhận
- `remark`: Nội dung giao dịch
- `rsltremark` (tùy chọn): Số tiền kết quả

### Quy trình xử lý

**Bước 1: Xác định loại giao dịch**

Hệ thống kiểm tra xem giao dịch có phải **Thu hộ/Khoản trừ** không:

- **Điều kiện 1**: `rsltremark` bắt đầu bằng dấu `-`
- **Điều kiện 2**: `remark` chứa một trong các cụm từ (không phân biệt hoa thường):
  - `THU NO`
  - `THU HO`
  - `KHOAN THU`
  - `KHOAN TRU`

Nếu thỏa mãn **1 trong 2 điều kiện** → Là **Thu hộ**
Ngược lại → Là **Chi lương**

**Bước 2: Mapping dữ liệu**

| Loại giao dịch | PayingUnit (Đơn vị) | BeneficiaryAccount (Nhân viên) |
|----------------|---------------------|--------------------------------|
| **Chi lương** | `facno` (Người chuyển) | `tacno` (Người nhận) |
| **Thu hộ** | `tacno` (Người nhận tiền) | `facno` (Người bị trừ) |

**Bước 3: Lưu Database**

1. Lưu/Lấy `PayingUnit` (sử dụng `get_or_create`)
2. Lưu/Lấy `BeneficiaryAccount` gắn với Unit đó
3. Cập nhật `remark_ref` nếu chưa có

## Hướng dẫn sử dụng

### 1. Truy cập Upload
```
URL: http://localhost:8000/payroll/upload/
```

### 2. Upload file
- Chọn file Excel (.xls, .xlsx) hoặc CSV
- File phải có đúng cấu trúc cột như trên
- Click "Upload và Import"

### 3. Xem thống kê
```
URL: http://localhost:8000/payroll/
```

Trang thống kê hiển thị:
- Tổng số đơn vị
- Tổng số nhân viên/người hưởng
- Bảng chi tiết với DataTables (Search, Sort, Filter, Export Excel)

## API Endpoints

| URL | Method | Mô tả |
|-----|--------|-------|
| `/payroll/` | GET | Trang thống kê chính |
| `/payroll/upload/` | GET, POST | Upload file import |
| `/payroll/api/data/` | GET | API trả về dữ liệu JSON cho DataTables |

## Ví dụ dữ liệu

### File import (CSV):
```csv
facno,tacno,remark,rsltremark
7202201001,7202215001,CHI LUONG THANG 11,500000
7202215002,7202201001,THU HO TIEN DIEN,-50000
```

### Kết quả sau khi import:

**Giao dịch 1** (Chi lương):
- PayingUnit: `7202201001`
- BeneficiaryAccount: `7202215001`
- Remark: "CHI LUONG THANG 11"

**Giao dịch 2** (Thu hộ - vì rsltremark = "-50000"):
- PayingUnit: `7202201001` (người nhận tiền thu hộ)
- BeneficiaryAccount: `7202215002` (người bị trừ tiền)
- Remark: "THU HO TIEN DIEN"

## Admin Interface

Truy cập Django Admin để quản lý:
```
URL: http://localhost:8000/admin/
```

- `payroll_statistics.PayingUnit`: Quản lý đơn vị
- `payroll_statistics.BeneficiaryAccount`: Quản lý nhân viên

## Tính năng DataTables

- **Search**: Tìm kiếm theo bất kỳ cột nào
- **Sort**: Sắp xếp theo cột
- **Filter**: Lọc dữ liệu
- **Export**: Xuất ra Excel hoặc In
- **Pagination**: Phân trang 10/25/50/100/Tất cả

## Cài đặt & Migration

```bash
# Thêm app vào INSTALLED_APPS trong settings.py
INSTALLED_APPS = [
    ...
    'payroll_statistics',
]

# Tạo migrations
python manage.py makemigrations payroll_statistics

# Chạy migrations
python manage.py migrate

# Chạy server
python manage.py runserver
```

## Lưu ý kỹ thuật

1. **Xử lý file lớn**: Sử dụng pandas để đọc file Excel/CSV hiệu quả
2. **Unique constraint**: Mỗi cặp (unit, account_number) chỉ tồn tại 1 lần
3. **get_or_create**: Tránh duplicate khi import nhiều lần
4. **Bootstrap 5 + DataTables**: Giao diện responsive, hiện đại

## Tác giả

Developed by Senior Developer Team

# Module Quy đổi Bút toán KPI (Transaction Conversion Tool)

## Tổng quan

Module **KPI Tool** giúp tính toán tự động điểm KPI cho giao dịch viên dựa trên nhật ký giao dịch (.DBF). Hệ thống sẽ:
1. Đọc file DBF chứa nhật ký giao dịch
2. Gom nhóm các bút toán Nợ/Có theo số tham chiếu (REFNO)
3. So khớp với bảng quy tắc quy đổi (hesoquydoi)
4. Tính điểm KPI theo hệ số quy đổi
5. Xuất báo cáo chi tiết Excel

## Cấu trúc

```
kpi_tool/
├── models.py                 # Models: ConversionRule, TellerTransactionBatch, TellerTransactionDetail
├── services.py              # Core logic: DBFProcessor, RuleImporter
├── views.py                 # Views: upload, batch detail, export Excel
├── urls.py                  # URL configuration
├── admin.py                 # Django admin configuration
├── templates/kpi_tool/      # Templates
│   ├── base.html
│   ├── index.html
│   ├── upload.html
│   ├── batch_detail.html
│   ├── batch_list.html
│   ├── import_rules.html
│   └── rule_list.html
└── migrations/              # Database migrations
```

## Cài đặt

### 1. Cài đặt thư viện

```bash
pip install dbfread django-import-export openpyxl
```

### 2. Thêm app vào INSTALLED_APPS

File: `wordgen/settings.py`
```python
INSTALLED_APPS = [
    ...
    "import_export",
    "kpi_tool",
]
```

### 3. Tích hợp URLs

File: `wordgen/urls.py`
```python
urlpatterns = [
    ...
    path("kpi-tool/", include("kpi_tool.urls")),
    ...
]
```

### 4. Chạy migrations

```bash
python manage.py makemigrations kpi_tool
python manage.py migrate
```

## Sử dụng

### 1. Import quy tắc quy đổi

Truy cập: `http://localhost:8000/kpi-tool/import-rules/`

- Upload file `hesoquydoi.BAK` (hoặc file DBF tương tự)
- File cần có cấu trúc:
  - `TKNO`: Tài khoản Nợ (hoặc đầu mã)
  - `TKCO`: Tài khoản Có (hoặc đầu mã)
  - `HESOQUAY1`: Hệ số quy đổi 1
  - `HESOQUAY2`: Hệ số quy đổi 2 (tùy chọn)
  - `CONGTHUC`: Công thức bổ sung (tùy chọn)

### 2. Upload file nhật ký giao dịch

Truy cập: `http://localhost:8000/kpi-tool/upload/`

- Chọn một hoặc nhiều file DBF
- Tên file phải theo format: `[USER_ID][DDMMYYYY].DBF`
  - Ví dụ: `GRATHIEU26092025.DBF`
  - User ID: `GRATHIEU`
  - Ngày: `26/09/2025`
- Nhập tên giao dịch viên (tùy chọn)
- Click "Phân tích và Tính điểm"

### 3. Xem kết quả

- Trang chủ: `http://localhost:8000/kpi-tool/`
- Danh sách lô: `http://localhost:8000/kpi-tool/batches/`
- Chi tiết lô: Click vào lô để xem chi tiết
- Xuất Excel: Click nút "Xuất Excel" trong trang chi tiết

## Cấu trúc file DBF đầu vào

### File nhật ký giao dịch

File DBF cần có các trường:
- `ACCTCD`: Số tài khoản
- `TRDRCR`: Loại giao dịch (D = Debit/Nợ, C = Credit/Có)
- `REFNO`: Số tham chiếu (dùng để gom nhóm bút toán)
- `TRAMT`: Số tiền giao dịch
- `TRDATE`: Ngày giao dịch (tùy chọn)
- `TRTIME`: Thời gian giao dịch (tùy chọn)

### File quy tắc (hesoquydoi.BAK)

File DBF cần có các trường:
- `CODE` hoặc `MALOAI`: Mã nghiệp vụ
- `TKNO`: Tài khoản Nợ hoặc đầu mã (bắt buộc)
- `TKCO`: Tài khoản Có hoặc đầu mã (bắt buộc)
- `HESOQUAY1`: Hệ số quy đổi 1 (bắt buộc)
- `HESOQUAY2`: Hệ số quy đổi 2 (tùy chọn)
- `CONGTHUC`: Công thức bổ sung (tùy chọn)
- `GHICHU` hoặc `MOTA`: Ghi chú (tùy chọn)

## Logic tính điểm

1. **Gom nhóm bút toán**: Hệ thống gom các dòng có cùng `REFNO` thành một bút toán
2. **Xác định Nợ/Có**:
   - Dòng có `TRDRCR='D'` là tài khoản Nợ
   - Dòng có `TRDRCR='C'` là tài khoản Có
3. **So khớp quy tắc**:
   - Tài khoản Nợ phải khớp (exact match hoặc starts with) với `TKNO` trong quy tắc
   - Tài khoản Có phải khớp (exact match hoặc starts with) với `TKCO` trong quy tắc
   - Cả hai điều kiện phải thỏa mãn
4. **Tính điểm**: Nếu khớp, cộng điểm theo `HESOQUAY1` (mặc định)
5. **Tổng hợp**: Tính tổng điểm theo ngày và theo tháng

## Ví dụ

### Ví dụ quy tắc

| CODE | TKNO | TKCO | HESOQUAY1 | Mô tả |
|------|------|------|-----------|-------|
| GD01 | 1011 | 359  | 1.5       | Gửi tiền tiết kiệm |
| GD02 | 1021 | 101  | 2.0       | Rút tiền |
| GD03 | 102  | 359  | 1.0       | Nộp tiền mặt |

### Ví dụ giao dịch

**Giao dịch 1:**
- REFNO: `REF001`
- Dòng 1: TRDRCR=`D`, ACCTCD=`10111234`, TRAMT=`10000000`
- Dòng 2: TRDRCR=`C`, ACCTCD=`35912345`, TRAMT=`10000000`

**Kết quả:**
- TK Nợ: `10111234` (bắt đầu bằng `1011`) ✓
- TK Có: `35912345` (bắt đầu bằng `359`) ✓
- Khớp quy tắc `GD01` → Được **1.5 điểm**

**Giao dịch 2:**
- REFNO: `REF002`
- Dòng 1: TRDRCR=`D`, ACCTCD=`1031`, TRAMT=`5000000`
- Dòng 2: TRDRCR=`C`, ACCTCD=`101`, TRAMT=`5000000`

**Kết quả:**
- TK Nợ: `1031` (không bắt đầu bằng `1011`, `1021`, hoặc `102`) ✗
- Không khớp quy tắc → **0 điểm**

## Django Admin

Truy cập: `http://localhost:8000/admin/kpi_tool/`

Quản lý:
- **Quy tắc quy đổi**: Xem, sửa, kích hoạt/vô hiệu hóa quy tắc
- **Lô giao dịch**: Xem thông tin các lô đã xử lý
- **Chi tiết giao dịch**: Xem chi tiết từng bút toán

## API Models

### ConversionRule
- `code`: Mã nghiệp vụ
- `debit_account_pattern`: Mẫu tài khoản Nợ
- `credit_account_pattern`: Mẫu tài khoản Có
- `score_1`: Hệ số quy đổi 1
- `score_2`: Hệ số quy đổi 2
- `formula`: Công thức bổ sung
- `description`: Mô tả
- `is_active`: Đang kích hoạt

### TellerTransactionBatch
- `teller_id`: Mã giao dịch viên
- `teller_name`: Tên giao dịch viên
- `month`, `year`: Tháng/Năm
- `file_date`: Ngày file
- `total_transactions`: Tổng số giao dịch
- `total_score`: Tổng điểm quy đổi
- `matched_transactions`: Số giao dịch khớp
- `unmatched_transactions`: Số giao dịch không khớp
- `processing_status`: Trạng thái xử lý

### TellerTransactionDetail
- `batch`: Lô giao dịch
- `reference_no`: Số tham chiếu
- `transaction_date`: Ngày giao dịch
- `debit_account`: Tài khoản Nợ
- `credit_account`: Tài khoản Có
- `amount`: Số tiền
- `matched_rule`: Quy tắc khớp
- `score`: Điểm quy đổi
- `is_matched`: Đã khớp quy tắc

## Troubleshooting

### Lỗi khi đọc file DBF

**Vấn đề**: `UnicodeDecodeError` hoặc không đọc được file

**Giải pháp**:
- Thử đổi encoding trong `services.py`:
```python
dbf = DBF(file_path, encoding='cp1252')  # Hoặc 'utf-8', 'latin1'
```

### Không parse được tên file

**Vấn đề**: File không đúng format `[USER_ID][DDMMYYYY].DBF`

**Giải pháp**:
- Đổi tên file theo đúng format
- Ví dụ: `GRATHIEU26092025.DBF`

### Không khớp quy tắc

**Vấn đề**: Tất cả giao dịch đều không khớp quy tắc (0 điểm)

**Giải pháp**:
- Kiểm tra quy tắc đã được import chưa
- Kiểm tra quy tắc có đang kích hoạt không (`is_active=True`)
- Kiểm tra pattern tài khoản có đúng không

## Tác giả

Module được phát triển bởi Claude AI cho Agribank - Hệ thống mẫu biểu.

## License

Internal use only - Agribank

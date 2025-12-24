# Tính năng Tạo Bảng Kê Nộp Thuế (Tax Payment Statement)

## 📖 Mô tả
Module này cung cấp tính năng tạo và xuất Bảng Kê Nộp Thuế với các chức năng:
- Quản lý danh mục Cơ quan thu thuế
- Quản lý danh mục Tiểu mục nộp thuế
- Giao diện nhập liệu với Cascading Dropdown (HTMX)
- Xuất file Word (.docx) sử dụng template

---

## 🚀 Cài đặt

### 1. App đã được đăng ký trong settings.py
```python
INSTALLED_APPS = [
    ...
    'tax_payment',
]
```

### 2. URLs đã được cấu hình
Truy cập tính năng tại:
- **Tạo bảng kê mới**: `http://localhost:8000/tax-payment/`
- **Danh sách bảng kê**: `http://localhost:8000/tax-payment/list/`

### 3. Migrations đã được áp dụng
```bash
python manage.py migrate
```

---

## 📊 Import Dữ liệu

### Bước 1: Chuẩn bị file dữ liệu

**File 1: CO QUAN THU.xlsx**
- Các cột bắt buộc:
  - `Tỉnh`: Tên tỉnh/thành phố
  - `Cơ quan thuế`: Tên cơ quan thuế
  - `Xã`: Tên xã/phường
  - `Mã cơ quan thu`: Mã số cơ quan thu
  - `Tên cơ quan thu`: Tên đầy đủ
  - `KBNN`: Tên kho bạc nhà nước
  - `Mã DB`: Mã địa bàn

**File 2: MA TIEU MUC.xlsx**
- Các cột bắt buộc:
  - `Mã số Tiểu mục`: Mã tiểu mục
  - `TÊN GỌI`: Tên/nội dung kinh tế

### Bước 2: Chạy lệnh import

```bash
# Import Cơ quan thu
python manage.py import_tax_data --locations path/to/CO_QUAN_THU.xlsx

# Import Tiểu mục
python manage.py import_tax_data --subentries path/to/MA_TIEU_MUC.xlsx

# Import cả hai cùng lúc
python manage.py import_tax_data \
    --locations path/to/CO_QUAN_THU.xlsx \
    --subentries path/to/MA_TIEU_MUC.xlsx

# Xóa dữ liệu cũ trước khi import
python manage.py import_tax_data \
    --locations path/to/CO_QUAN_THU.xlsx \
    --clear
```

---

## 🎨 Tạo File Word Template

### Vị trí file template:
```
tax_payment/templates/tax_statement_template.docx
```

### Hướng dẫn chi tiết:
Xem file: `tax_payment/HUONG_DAN_TAGS_WORD_TEMPLATE.md`

### Danh sách Tags cơ bản:

**Thông tin người nộp:**
- `{{ ten_nguoi_nop }}` - Tên người nộp thuế
- `{{ ma_so_thue }}` - Mã số thuế
- `{{ dia_chi }}` - Địa chỉ
- `{{ ngay_lap }}` - Ngày lập bảng kê

**Thông tin cơ quan thu:**
- `{{ tinh }}` - Tỉnh/Thành phố
- `{{ co_quan_thue }}` - Cơ quan thuế
- `{{ xa_phuong }}` - Xã/Phường
- `{{ ma_co_quan_thu }}` - Mã cơ quan thu
- `{{ ten_co_quan_thu }}` - Tên cơ quan thu (đầy đủ)
- `{{ ma_dia_ban }}` - Mã địa bàn
- `{{ kho_bac }}` - Kho bạc nhà nước

**Bảng danh sách tiểu mục:**
```
{%tr for item in items %}
{{ item.stt }} | {{ item.ma_tieu_muc }} | {{ item.noi_dung }} | {{ item.so_tien }}
{%tr endfor %}
```

**Tổng tiền:**
- `{{ tong_so_tien }}` - Tổng số tiền (đã format)

---

## 💻 Sử dụng

### 1. Truy cập giao diện tạo bảng kê
```
http://localhost:8000/tax-payment/
```

### 2. Điền thông tin

**Thông tin người nộp thuế:**
- Tên người nộp (*bắt buộc)
- Mã số thuế
- Địa chỉ
- Ngày lập

**Thông tin cơ quan thu (Cascading Dropdown):**
1. Chọn **Tỉnh/Thành phố** → Tự động load danh sách Cơ quan thuế
2. Chọn **Cơ quan thuế** → Tự động load danh sách Xã/Phường
3. Chọn **Xã/Phường** → Tự động điền:
   - Mã cơ quan thu
   - Tên cơ quan thu
   - Mã địa bàn
   - KBNN

**Danh sách các khoản nộp:**
- Mã tiểu mục: Nhập mã → Tự động điền nội dung (nếu có trong DB)
- Nội dung: Tự động điền hoặc nhập thủ công
- Số tiền: Nhập số tiền nộp
- Nhấn "Thêm dòng" để thêm tiểu mục mới

### 3. Lưu và xuất file Word
Nhấn nút **"Lưu và Xuất File Word"** để:
- Lưu dữ liệu vào database
- Tự động xuất file Word với tên: `Bang_ke_nop_thue_[Tên]_[Ngày].docx`

### 4. Xem danh sách bảng kê đã tạo
```
http://localhost:8000/tax-payment/list/
```

---

## 🗂️ Cấu trúc Dự án

```
tax_payment/
├── __init__.py
├── admin.py                    # Đăng ký models vào Django Admin
├── apps.py
├── models.py                   # 4 Models: TaxLocation, TaxSubEntry, TaxPaymentStatement, TaxPaymentItem
├── views.py                    # Views: create, list, export, AJAX endpoints
├── urls.py                     # URL routing
├── management/
│   └── commands/
│       └── import_tax_data.py  # Management command import Excel
├── migrations/
│   └── 0001_initial.py
├── templates/
│   └── tax_payment/
│       ├── create_statement.html       # Form tạo bảng kê (HTMX)
│       ├── statement_list.html         # Danh sách bảng kê
│       └── tax_statement_template.docx # File Word mẫu (cần tạo)
├── README.md                           # File này
└── HUONG_DAN_TAGS_WORD_TEMPLATE.md    # Hướng dẫn tags Word
```

---

## 📝 Models

### 1. TaxLocation
Lưu trữ thông tin Cơ quan thu thuế
- Fields: tinh, co_quan_thue_group, xa_phuong, ma_co_quan_thu, ten_co_quan_thu, kho_bac, ma_dia_ban
- Indexes: tinh, co_quan_thue_group, xa_phuong

### 2. TaxSubEntry
Lưu trữ danh mục Tiểu mục nộp thuế
- Fields: ma_tieu_muc, ten_tieu_muc

### 3. TaxPaymentStatement
Lưu trữ thông tin Bảng kê nộp thuế
- Fields: ten_nguoi_nop, ma_so_thue, dia_chi, ngay_lap, tong_so_tien, tax_location (FK)

### 4. TaxPaymentItem
Lưu trữ các dòng tiểu mục trong bảng kê
- Fields: statement (FK), ma_tieu_muc, noi_dung, so_tien, stt

---

## 🔧 API Endpoints

### AJAX Endpoints (cho Cascading Dropdown)

**1. Lấy danh sách Cơ quan thuế theo Tỉnh:**
```
GET /tax-payment/ajax/get-co-quan-thue/?tinh=[Tên tỉnh]
Response: {"co_quan_thue": [...]}
```

**2. Lấy danh sách Xã/Phường:**
```
GET /tax-payment/ajax/get-xa-phuong/?tinh=[Tên tỉnh]&co_quan_thue=[Tên cơ quan]
Response: {"xa_phuong": [...]}
```

**3. Lấy chi tiết cơ quan thu (auto-fill):**
```
GET /tax-payment/ajax/get-location-details/?tinh=[...]&co_quan_thue=[...]&xa_phuong=[...]
Response: {
    "ma_co_quan_thu": "...",
    "ten_co_quan_thu": "...",
    "ma_dia_ban": "...",
    "kho_bac": "..."
}
```

**4. Tìm kiếm Tiểu mục:**
```
GET /tax-payment/ajax/search-sub-entry/?ma_tieu_muc=[Mã]
Response: {
    "ma_tieu_muc": "...",
    "ten_tieu_muc": "..."
}
```

---

## 🐛 Troubleshooting

### Lỗi: "Không tìm thấy file mẫu Word"
- Kiểm tra file template tại: `tax_payment/templates/tax_statement_template.docx`
- Đảm bảo file có định dạng `.docx` (không phải `.doc`)

### Cascading Dropdown không hoạt động
- Kiểm tra HTMX đã được load: xem console browser
- Kiểm tra dữ liệu đã được import vào database

### Import dữ liệu bị lỗi
- Kiểm tra tên các cột trong file Excel có chính xác không
- Kiểm tra encoding của file (nên dùng UTF-8)
- Xem log chi tiết khi chạy command import

---

## ✅ Testing

### Test import dữ liệu:
```bash
# Tạo file test nhỏ với 2-3 dòng dữ liệu
python manage.py import_tax_data --locations test_data.xlsx
```

### Test giao diện:
1. Truy cập: `http://localhost:8000/tax-payment/`
2. Chọn Tỉnh → Kiểm tra Cơ quan thuế được load
3. Chọn Cơ quan thuế → Kiểm tra Xã/Phường được load
4. Chọn Xã/Phường → Kiểm tra auto-fill các field
5. Nhập mã tiểu mục → Kiểm tra auto-fill nội dung
6. Submit form → Kiểm tra file Word được tải về

### Test từ Django Admin:
```
http://localhost:8000/admin/
- Vào Tax payment → Tax locations
- Vào Tax payment → Tax sub entries
```

---

## 🎯 Tính năng nâng cao (có thể mở rộng)

1. **Export Excel** (ngoài Word)
2. **Import dữ liệu từ CSV**
3. **Tìm kiếm và lọc** trong danh sách bảng kê
4. **In PDF** trực tiếp
5. **Lưu draft** (bản nháp)
6. **Template Word động** (cho phép user upload template riêng)

---

## 👨‍💻 Developer Notes

### Dependencies mới thêm vào:
- `docxtpl`: Xử lý Word template
- `openpyxl`: Đọc file Excel
- `pandas`: Xử lý dữ liệu từ Excel

### HTMX:
- CDN đã được thêm vào template
- Sử dụng cho cascading dropdown để giảm tải server

---

## 📞 Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. Log Django: `python manage.py runserver`
2. Browser console (F12) cho lỗi JavaScript/HTMX
3. Database: `python manage.py dbshell`

**Chúc bạn sử dụng thành công!** 🚀

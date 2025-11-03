# HƯỚNG DẪN CẬP NHẬT HỆ THỐNG BIẾN MẪU BIỂU

> **Ngày:** 03/11/2025
> **Phiên bản:** 2.0
> **Mục đích:** Tích hợp biến từ hệ thống cũ vào hệ thống mới

---

## 📋 TỔNG QUAN

Hệ thống đã được cập nhật để hỗ trợ **tất cả biến từ chương trình mẫu biểu cũ**.

### Những gì đã thêm:

#### ✅ **Customer Model - Khách hàng (7 trường mới):**
- `ho_ten_tieng_anh` - Họ tên tiếng Anh
- `dan_toc` - Dân tộc (mặc định: Kinh)
- `ho_khau` - Hộ khẩu thường trú
- `so_the_atm` - Số thẻ ATM
- `thoi_han_the` - Thời hạn thẻ
- `ngay_tra_the` - Ngày trả thẻ
- `loai_phi` - Loại phí

#### ✅ **GlobalConfig Model - Cấu hình toàn cục (4 trường mới):**
- `ma_chi_nhanh` - Mã chi nhánh
- `dien_thoai_chi_nhanh` - Số điện thoại chi nhánh
- `so_fax` - Số Fax
- `dia_danh` - Địa danh (Ví dụ: Bạc Liêu, Đồng Tháp)

#### ✅ **File mới:**
- `templates_app/variable_mapping.py` - Ánh xạ biến cũ → biến mới

---

## 🚀 BƯỚC 1: CẬP NHẬT DATABASE

### Trên Windows:

```cmd
# Kích hoạt virtual environment (nếu có)
venv\Scripts\activate

# Tạo migration
python manage.py makemigrations templates_app

# Áp dụng migration
python manage.py migrate

# Khởi động lại server
start.bat
```

### Trên Linux/Mac:

```bash
# Kích hoạt virtual environment
source venv/bin/activate

# Tạo migration
python manage.py makemigrations templates_app

# Áp dụng migration
python manage.py migrate

# Khởi động lại server
python run_waitress.py
```

---

## 📖 BƯỚC 2: CẬP NHẬT CẤU HÌNH CHI NHÁNH

Sau khi chạy migration, vào **Django Admin** để cập nhật thông tin chi nhánh:

1. Truy cập: `http://localhost:8000/admin`
2. Đăng nhập với tài khoản admin
3. Chọn **Cấu hình Toàn cục**
4. Điền các thông tin mới:
   - **Mã chi nhánh:** (VD: `GR`, `BL`, `DT`)
   - **Điện thoại chi nhánh:** (VD: `0291.3829.xxx`)
   - **Số Fax:** (VD: `0291.3829.xxx`)
   - **Địa danh:** (VD: `Bạc Liêu`)
5. Click **Lưu**

---

## 🔄 BƯỚC 3: SỬ DỤNG BIẾN MỚI TRONG TEMPLATE

### A. Ánh xạ biến cũ → mới

| Biến cũ (hệ thống cũ) | Biến mới (hệ thống mới) | Nguồn dữ liệu |
|----------------------|-------------------------|---------------|
| `[ChiNhanh]` | `{{ ten_chi_nhanh }}` | GlobalConfig |
| `[ChiNhanhHOA]` | `{{ ten_chi_nhanh_hoa }}` | GlobalConfig |
| `[DiaChi]` | `{{ dia_chi_chi_nhanh }}` | GlobalConfig |
| `[DienThoai]` | `{{ dien_thoai_chi_nhanh }}` | GlobalConfig ⭐ MỚI |
| `[SoFax]` | `{{ so_fax }}` | GlobalConfig ⭐ MỚI |
| `[DiaDanh]` | `{{ dia_danh }}` | GlobalConfig ⭐ MỚI |
| `[MaSoThue]` | `{{ mst }}` | GlobalConfig |
| `[MaCN]` | `{{ ma_chi_nhanh }}` | GlobalConfig ⭐ MỚI |
| `[HotenKhachhangVN]` | `{{ ho_ten }}` | Customer |
| `[HotenKhachhangE]` | `{{ ho_ten_tieng_anh }}` | Customer ⭐ MỚI |
| `[DanToc]` | `{{ dan_toc }}` | Customer ⭐ MỚI |
| `[HoKhau]` | `{{ ho_khau }}` | Customer ⭐ MỚI |
| `[SoTheATM]` | `{{ so_the_atm }}` | Customer ⭐ MỚI |
| `[ThoiHanThe]` | `{{ thoi_han_the }}` | Customer ⭐ MỚI |
| `[NgayTraThe]` | `{{ ngay_tra_the }}` | Customer ⭐ MỚI |
| `[LoaiPhi]` | `{{ loai_phi }}` | Customer ⭐ MỚI |
| `[Ngay//]` | `{{ ngay_hien_tai }}` | Auto-generated |
| `[NgayThangNam]` | `{{ ngay_thang_nam_text }}` | Auto-generated |

### B. Biến tự động (không cần nhập)

```python
# Các biến này tự động có sẵn trong mọi template:
{{ ngay_hien_tai }}         # 03/11/2025
{{ ngay_thang_nam_text }}   # ngày 03 tháng 11 năm 2025
{{ date_month_year }}       # Date 03 Month 11 Year 2025
{{ nam_hien_tai }}          # 2025
{{ thang_hien_tai }}        # 11
{{ ngay_hien_tai_day }}     # 03
```

### C. Ví dụ sử dụng trong template Word

**Trước đây (hệ thống cũ):**
```
Chi nhánh: [ChiNhanh]
Điện thoại: [DienThoai]
Fax: [SoFax]

Khách hàng: [HotenKhachhangVN]
Dân tộc: [DanToc]
Hộ khẩu: [HoKhau]
```

**Bây giờ (hệ thống mới - Jinja2):**
```jinja2
Chi nhánh: {{ ten_chi_nhanh }}
Điện thoại: {{ dien_thoai_chi_nhanh }}
Fax: {{ so_fax }}

Khách hàng: {{ ho_ten }}
Dân tộc: {{ dan_toc }}
Hộ khẩu: {{ ho_khau }}
```

---

## 🛠️ BƯỚC 4: CHUYỂN ĐỔI TEMPLATE CŨ (Tùy chọn)

Nếu bạn có file Word template cũ sử dụng cú pháp `[TenBien]`, sử dụng script sau để chuyển đổi:

### Cách 1: Thủ công (Find & Replace trong Word)

1. Mở file Word template
2. Ctrl+H (Find & Replace)
3. Thay thế từng biến:
   - Find: `[ChiNhanh]` → Replace: `{{ ten_chi_nhanh }}`
   - Find: `[DienThoai]` → Replace: `{{ dien_thoai_chi_nhanh }}`
   - v.v.

### Cách 2: Tự động (Python script)

```python
from templates_app.variable_mapping import convert_template_content

# Đọc nội dung template cũ
with open('template_cu.txt', 'r', encoding='utf-8') as f:
    old_content = f.read()

# Chuyển đổi
new_content = convert_template_content(old_content)

# Lưu template mới
with open('template_moi.txt', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Chuyển đổi hoàn tất!")
```

---

## 📊 DANH SÁCH ĐẦY ĐỦ CÁC BIẾN

### 🏢 Biến Chi nhánh (GlobalConfig)

| Biến mới | Mô tả | Ví dụ |
|----------|-------|-------|
| `ten_chi_nhanh` | Tên chi nhánh | Chi nhánh Giá Rai Bạc Liêu |
| `ten_chi_nhanh_hoa` | Tên chi nhánh IN HOA | CHI NHÁNH GIÁ RAI BẠC LIÊU |
| `ma_chi_nhanh` | Mã chi nhánh | GR |
| `mst` | Mã số thuế | 0100000000 |
| `dia_chi_chi_nhanh` | Địa chỉ chi nhánh | 123 Đường ABC, Phường XYZ |
| `dien_thoai_chi_nhanh` | Số điện thoại | 0291.3829.xxx |
| `so_fax` | Số Fax | 0291.3829.xxx |
| `dia_danh` | Địa danh | Bạc Liêu |
| `giao_dich_vien` | Tên giao dịch viên | Nguyễn Văn A |
| `kiem_soat_vien` | Tên kiểm soát viên | Trần Thị B |
| `giam_doc` | Tên giám đốc | Lê Văn C |

### 👤 Biến Khách hàng (Customer)

| Biến mới | Mô tả | Ví dụ |
|----------|-------|-------|
| `ho_ten` | Họ và tên | Nguyễn Văn A |
| `ho_ten_tieng_anh` | Họ tên tiếng Anh | NGUYEN VAN A |
| `ngay_sinh` | Ngày sinh | 01/01/1990 |
| `gioi_tinh` | Giới tính | Nam / Nữ |
| `dan_toc` | Dân tộc | Kinh |
| `so_cmnd` | Số CMND/CCCD | 001234567890 |
| `ngay_cap_cmnd` | Ngày cấp CMND | 01/01/2015 |
| `ngay_het_han_cmnd` | Ngày hết hạn CMND | 01/01/2035 |
| `noi_cap_cmnd` | Nơi cấp CMND | Cục Cảnh sát ĐKQL... |
| `dia_chi` | Địa chỉ thường trú | 123 Đường ABC |
| `ho_khau` | Hộ khẩu thường trú | 456 Đường XYZ |
| `so_dien_thoai` | Số điện thoại | 0901234567 |
| `email` | Email | example@gmail.com |
| `ma_khach_hang` | Mã khách hàng (CIF) | 7202000699174 |
| `so_tai_khoan` | Số tài khoản | 1234567890 |
| `so_the_atm` | Số thẻ ATM | 9704123456789012 |
| `loai_the` | Loại thẻ | Thẻ Visa |
| `thoi_han_the` | Thời hạn thẻ | 5 năm |
| `ngay_tra_the` | Ngày trả thẻ | 03/11/2025 |
| `loai_phi` | Loại phí | Phí phát hành |

---

## 🔍 KIỂM TRA SAU KHI CẬP NHẬT

### Checklist:

- [ ] Migration đã chạy thành công (`python manage.py migrate`)
- [ ] Không có lỗi khi khởi động server
- [ ] Vào Django Admin, thấy các trường mới trong:
  - Customer (ho_ten_tieng_anh, dan_toc, ho_khau, so_the_atm, ...)
  - GlobalConfig (ma_chi_nhanh, dien_thoai_chi_nhanh, so_fax, dia_danh)
- [ ] Tạo thử 1 mẫu biểu với biến mới → File Word hiển thị đúng
- [ ] Các mẫu biểu cũ vẫn hoạt động bình thường

---

## ❓ CÂU HỎI THƯỜNG GẶP

### Q1: Migration báo lỗi "duplicate column name"?

**A:** Database đã có sẵn cột này. Bỏ qua hoặc xóa migration và tạo lại:
```bash
# Xóa file migration mới nhất trong templates_app/migrations/
# Sau đó chạy lại:
python manage.py makemigrations templates_app
python manage.py migrate
```

### Q2: Biến mới không hiển thị trong template?

**A:** Kiểm tra:
1. Migration đã chạy chưa? (`python manage.py migrate`)
2. Dữ liệu đã điền vào chưa? (Django Admin)
3. Tên biến có đúng không? (xem file `variable_mapping.py`)

### Q3: Làm sao biết biến thuộc loại nào (Customer hay GlobalConfig)?

**A:** Sử dụng script:
```python
from templates_app.variable_mapping import get_variable_category

category = get_variable_category('dien_thoai_chi_nhanh')
print(category)  # Output: global_config
```

### Q4: Tôi muốn thêm biến tùy chỉnh riêng?

**A:** Có 2 cách:
1. **Biến chung (cho tất cả mẫu biểu):** Thêm vào GlobalConfig → `custom_variables` (JSON field)
2. **Biến riêng:** Tạo Variable mới trong Django Admin

---

## 📚 TÀI LIỆU THAM KHẢO

- `variable_mapping.py` - File ánh xạ đầy đủ biến cũ → mới
- `TINH_NANG_UU_TIEN.md` - Các tính năng sắp phát triển
- `README.md` - Hướng dẫn chung về hệ thống

---

## 🆘 HỖ TRỢ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra log lỗi: `python manage.py runserver` (xem terminal)
2. Kiểm tra database: `python manage.py dbshell`
3. Liên hệ hỗ trợ kỹ thuật

---

**Cập nhật lần cuối:** 03/11/2025
**Phiên bản hệ thống:** 2.0

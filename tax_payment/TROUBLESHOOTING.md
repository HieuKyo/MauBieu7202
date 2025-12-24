# TROUBLESHOOTING - Tax Payment Feature

## 📋 Mục lục

1. [Biến trong Variable Library không hiển thị](#1-biến-trong-variable-library-không-hiển-thị)
2. [Xã/Phường không hiển thị với một số Cơ quan thuế](#2-xãphường-không-hiển-thị-với-một-số-cơ-quan-thuế)
3. [Import dữ liệu bị lỗi](#3-import-dữ-liệu-bị-lỗi)

---

## 1. Biến trong Variable Library không hiển thị

### ❓ Vấn đề
Truy cập `http://localhost:8000/variable-library/` nhưng không thấy các biến mới cho Tax Payment.

### ✅ Giải pháp

**Bước 1: Kiểm tra xem đã chạy command chưa**
```bash
python manage.py add_tax_variables
```

**Bước 2: Xác nhận biến đã được tạo**
```bash
python check_all_tax_vars.py
```

Kết quả mong đợi:
```
Tìm thấy: 15/15
```

**Bước 3: Truy cập Variable Library**
```
http://localhost:8000/variable-library/
```

hoặc qua Admin:
```
http://localhost:8000/admin/templates_app/variable/
```

### 📝 Danh sách 15 biến đã tạo

| Tên biến | Nhãn hiển thị | Kiểu |
|----------|--------------|------|
| `ten_nguoi_nop_thue` | Tên người nộp thuế | text |
| `ma_so_thue` | Mã số thuế | text |
| `dia_chi_nguoi_nop_thue` | Địa chỉ người nộp thuế | textarea |
| `ngay_lap_bang_ke` | Ngày lập bảng kê thuế | date |
| `tinh_thanh_pho` | Tỉnh/Thành phố (Cơ quan thu) | text |
| `co_quan_thue` | Cơ quan thuế | text |
| `xa_phuong_nop_thue` | Xã/Phường (Cơ quan thu) | text |
| `ma_co_quan_thu` | Mã cơ quan thu | text |
| `ten_co_quan_thu` | Tên cơ quan thu (đầy đủ) | textarea |
| `ma_dia_ban` | Mã địa bàn hành chính | text |
| `kho_bac_nha_nuoc` | Kho bạc nhà nước (KBNN) | text |
| `tong_so_tien_nop_thue` | Tổng số tiền nộp thuế | number |
| `ma_tieu_muc_thue` | Mã tiểu mục thuế | text |
| `noi_dung_tieu_muc` | Nội dung tiểu mục thuế | textarea |
| `so_tien_tieu_muc` | Số tiền tiểu mục | number |

---

## 2. Xã/Phường không hiển thị với một số Cơ quan thuế

### ❓ Vấn đề
- Chọn Tỉnh: OK
- Chọn Cơ quan thuế: OK
- Chọn Xã/Phường: **KHÔNG HIỂN THỊ** hoặc dropdown trống

### 🔍 Nguyên nhân

#### A. Chưa có dữ liệu trong database
```bash
python check_tax_data.py
```

Nếu hiển thị:
```
TaxLocation (Cơ quan thu): 0 records  ⚠️
```

→ **Chưa import dữ liệu!**

#### B. Dữ liệu không khớp (tên Cơ quan thuế khác nhau)

**Ví dụ vấn đề:**
- Trong database: `"Thuế cơ sở 7 tỉnh Cà Mau"` (có khoảng trắng thừa)
- Người dùng chọn: `"Thuế cơ sở 7 tỉnh Cà Mau"` (chuẩn)
- → **KHÔNG KHỚP** → Không có Xã/Phường

#### C. Lỗi distinct() trong Django Query

**Lỗi trước đây:**
```python
# ❌ SAI - distinct() sau order_by()
.values_list().distinct().order_by()
```

**Đã sửa:**
```python
# ✅ ĐÚNG - order_by() trước distinct()
.order_by().values_list().distinct()
```

### ✅ Giải pháp

#### Giải pháp 1: Import dữ liệu

**Cách 1: Qua Django Admin (Khuyến nghị)**
```
1. Vào: http://localhost:8000/admin/tax_payment/taxlocation/
2. Nhấn: "Import từ Excel"
3. Chọn file: CO QUAN THU.xlsx
4. Upload
```

**Cách 2: Qua Command Line**
```bash
python manage.py import_tax_data --locations path/to/CO_QUAN_THU.xlsx
```

**Cách 3: Import sample data để test**
```bash
python manage.py import_tax_data \
    --locations data/sample_co_quan_thu.csv \
    --subentries data/sample_tieu_muc.csv
```

#### Giải pháp 2: Kiểm tra dữ liệu

**Debug script:**
```bash
python debug_tax_locations.py
```

Kiểm tra:
- Có khoảng trắng thừa không?
- Tên Cơ quan thuế có chính xác không?
- Có ký tự đặc biệt không?

#### Giải pháp 3: Clean dữ liệu

Nếu phát hiện khoảng trắng thừa, chạy:
```python
from tax_payment.models import TaxLocation

# Clean tất cả khoảng trắng thừa
for loc in TaxLocation.objects.all():
    loc.co_quan_thue_group = loc.co_quan_thue_group.strip()
    loc.tinh = loc.tinh.strip()
    loc.xa_phuong = loc.xa_phuong.strip()
    loc.save()
```

### 🧪 Test sau khi sửa

```bash
python test_views.py
```

Kết quả mong đợi:
```
Test 1: Get Cơ quan thuế cho Tỉnh = "Cà Mau"
Kết quả: 3 cơ quan thuế  ✅
  - "Thuế cơ sở 1 tỉnh Cà Mau"
  - "Thuế cơ sở 6 tỉnh Cà Mau"
  - "Thuế cơ sở 7 tỉnh Cà Mau"

Test 2: Get Xã/Phường cho "Thuế cơ sở 1 tỉnh Cà Mau"
Kết quả: 3 xã/phường  ✅

Test 3: Get Xã/Phường cho "Thuế cơ sở 7 tỉnh Cà Mau"
Kết quả: 3 xã/phường  ✅
```

---

## 3. Import dữ liệu bị lỗi

### ❓ Lỗi: "Thiếu các cột"

**Nguyên nhân:**
Tên cột trong Excel không khớp với yêu cầu.

**Giải pháp:**
Đảm bảo file Excel có đúng tên cột:

**File CO QUAN THU.xlsx:**
```
| Tỉnh | Cơ quan thuế | Xã | Mã cơ quan thu | Tên cơ quan thu | KBNN | Mã DB |
```

**File MA TIEU MUC.xlsx:**
```
| Mã số Tiểu mục | TÊN GỌI |
```

### ❓ Lỗi: "Encoding error"

**Giải pháp:**
Lưu file CSV với encoding UTF-8:
- Excel: Save As → CSV UTF-8 (Comma delimited)
- Google Sheets: Download → CSV

### ❓ Lỗi: "Duplicate key"

**Nguyên nhân:**
Mã cơ quan thu hoặc Mã tiểu mục bị trùng.

**Giải pháp:**
- Kiểm tra file Excel có dòng bị duplicate không
- Hoặc sử dụng flag `--clear` để xóa dữ liệu cũ trước khi import:
```bash
python manage.py import_tax_data --locations file.xlsx --clear
```

---

## 🔧 Debug Tools

### Script kiểm tra nhanh

**1. Check biến:**
```bash
python check_all_tax_vars.py
```

**2. Check dữ liệu:**
```bash
python check_tax_data.py
```

**3. Debug cascading dropdown:**
```bash
python debug_tax_locations.py
```

**4. Test views:**
```bash
python test_views.py
```

### Django Shell

```bash
python manage.py shell
```

```python
from tax_payment.models import TaxLocation, TaxSubEntry
from templates_app.models import Variable

# Kiểm tra số lượng
print(f'TaxLocation: {TaxLocation.objects.count()}')
print(f'TaxSubEntry: {TaxSubEntry.objects.count()}')
print(f'Variables: {Variable.objects.filter(name__contains="thue").count()}')

# Xem dữ liệu mẫu
TaxLocation.objects.first()
```

---

## 📞 Support

Nếu vẫn gặp vấn đề sau khi thử các giải pháp trên:

1. Kiểm tra Django console log:
```bash
python manage.py runserver
```

2. Kiểm tra Browser console (F12):
- Network tab → Xem AJAX requests
- Console tab → Xem JavaScript errors

3. Chạy tất cả debug scripts:
```bash
python check_all_tax_vars.py
python check_tax_data.py
python test_views.py
```

4. Gửi kết quả các script trên khi báo lỗi.

---

## ✅ Checklist Hoàn chỉnh

- [ ] Đã chạy: `python manage.py add_tax_variables`
- [ ] Đã chạy: `python manage.py migrate`
- [ ] Đã import dữ liệu Cơ quan thu
- [ ] Đã import dữ liệu Tiểu mục
- [ ] Đã test cascading dropdown
- [ ] Tất cả các script debug đều pass
- [ ] Giao diện hoạt động bình thường

---

**Last updated:** 2024-12-24

# HƯỚNG DẪN CHUYỂN ĐỔI TEMPLATE WORD

> **Chuyển đổi biến từ format cũ `[BienCu]` sang format mới `{{ bien_moi }}`**

---

## 📋 MỤC LỤC

1. [Chuẩn bị](#chuẩn-bị)
2. [Cách 1: Thủ công (Word Find & Replace)](#cách-1-thủ-công)
3. [Cách 2: Tự động (Python Script)](#cách-2-tự-động)
4. [Kiểm tra kết quả](#kiểm-tra-kết-quả)
5. [Troubleshooting](#troubleshooting)

---

## 🛠️ CHUẨN BỊ

### Yêu cầu:

- ✅ Python đã cài đặt
- ✅ Virtual environment đã kích hoạt
- ✅ Thư viện `python-docx` đã cài:

```cmd
pip install python-docx
```

### Sao lưu file gốc:

```cmd
# Tạo folder backup
mkdir backup_templates
copy templates_cu\*.docx backup_templates\
```

---

## 📝 CÁCH 1: THỦ CÔNG (Khuyến nghị cho ít file)

### Khi nào dùng:
- Có ít hơn 10 file template
- Muốn kiểm soát từng thay đổi
- File template có format phức tạp

### Các bước:

#### Bước 1: Mở file Word template

#### Bước 2: Ctrl + H (Find & Replace)

#### Bước 3: Thay thế từng biến

**QUAN TRỌNG:** Phải thay thế **CHÍNH XÁC** cả dấu ngoặc!

| Find (Biến cũ) | Replace with (Biến mới) |
|----------------|-------------------------|
| `[HotenKhachhangVN]` | `{{ ho_ten }}` |
| `[HotenKhachhangE]` | `{{ ho_ten_tieng_anh }}` |
| `[ChiNhanh]` | `{{ ten_chi_nhanh }}` |
| `[ChiNhanhHOA]` | `{{ ten_chi_nhanh_hoa }}` |
| `[MaCN]` | `{{ ma_chi_nhanh }}` |
| `[DienThoai]` | `{{ dien_thoai_chi_nhanh }}` |
| `[SoFax]` | `{{ so_fax }}` |
| `[DiaDanh]` | `{{ dia_danh }}` |
| `[DanToc]` | `{{ dan_toc }}` |
| `[HoKhau]` | `{{ ho_khau }}` |
| `[SoCMT]` | `{{ so_cmnd }}` |
| `[NgayCMT]` | `{{ ngay_cap_cmnd }}` |
| `[NoiCapCMT]` | `{{ noi_cap_cmnd }}` |
| `[NgayHetHan]` | `{{ ngay_het_han_cmnd }}` |
| `[SoTheATM]` | `{{ so_the_atm }}` |
| `[ThoiHanThe]` | `{{ thoi_han_the }}` |
| `[LoaiPhi]` | `{{ loai_phi }}` |
| `[Ngay//]` | `{{ ngay_hien_tai }}` |
| `[NgayThangNam]` | `{{ ngay_thang_nam_text }}` |

📖 **Xem danh sách đầy đủ trong:** `HUONG_DAN_CAP_NHAT_BIEN.md`

#### Bước 4: Lưu file với tên mới

```
Ví dụ:
  mau_phat_hanh_the_CU.docx → mau_phat_hanh_the_MOI.docx
```

---

## 🚀 CÁCH 2: TỰ ĐỘNG (Khuyến nghị cho nhiều file)

### Khi nào dùng:
- Có nhiều hơn 10 file template
- Muốn tiết kiệm thời gian
- Các file có cấu trúc đơn giản

### Script: `convert_old_templates.py`

---

### **A. Convert 1 file duy nhất:**

```cmd
python convert_old_templates.py input.docx output.docx
```

**Ví dụ:**
```cmd
python convert_old_templates.py templates_cu\mau_phat_hanh_the.docx templates_moi\mau_phat_hanh_the.docx
```

**Output:**
```
============================================================
Converting: templates_cu\mau_phat_hanh_the.docx
Output to: templates_moi\mau_phat_hanh_the.docx
============================================================

Converting paragraphs...
  ✓ Converted: [HotenKhachhangVN] → {{ ho_ten }}
  ✓ Converted: [ChiNhanh] → {{ ten_chi_nhanh }}
  ✓ Converted: [DienThoai] → {{ dien_thoai_chi_nhanh }}
  ...

Converting tables...
  ✓ Converted: [SoCMT] → {{ so_cmnd }}
  ✓ Converted: [NgayCMT] → {{ ngay_cap_cmnd }}
  ...

Converting headers...
  ✓ Converted: [ChiNhanhHOA] → {{ ten_chi_nhanh_hoa }}

============================================================
✅ SUCCESS!
Total conversions: 18
Output saved to: templates_moi\mau_phat_hanh_the.docx
============================================================
```

---

### **B. Convert toàn bộ folder (Batch):**

```cmd
python convert_old_templates.py folder_cu\ folder_moi\
```

**Ví dụ:**
```cmd
python convert_old_templates.py templates_cu\ templates_moi\
```

**Output:**
```
Found 15 .docx files
Input folder: templates_cu\
Output folder: templates_moi\

[1/15] Processing: mau_1.docx
============================================================
Converting: templates_cu\mau_1.docx
...
✅ SUCCESS! Total conversions: 12

[2/15] Processing: mau_2.docx
...

[15/15] Processing: mau_15.docx
...

============================================================
BATCH CONVERSION COMPLETE
============================================================
✅ Success: 15 files
❌ Failed: 0 files
============================================================
```

---

### **C. Workflow đầy đủ:**

```cmd
# Bước 1: Chuẩn bị
mkdir templates_cu
mkdir templates_moi

# Bước 2: Copy file cũ vào templates_cu
copy C:\path\to\old\*.docx templates_cu\

# Bước 3: Kích hoạt virtual environment
venv\Scripts\activate

# Bước 4: Cài python-docx (nếu chưa có)
pip install python-docx

# Bước 5: Chạy script chuyển đổi
python convert_old_templates.py templates_cu\ templates_moi\

# Bước 6: Kiểm tra kết quả
dir templates_moi\
```

---

## ✅ KIỂM TRA KẾT QUẢ

### Bước 1: Mở file Word đã convert

```cmd
start templates_moi\mau_phat_hanh_the.docx
```

### Bước 2: Kiểm tra biến đã thay đổi

**Trước (cũ):**
```
Khách hàng: [HotenKhachhangVN]
Chi nhánh: [ChiNhanh]
```

**Sau (mới):**
```
Khách hàng: {{ ho_ten }}
Chi nhánh: {{ ten_chi_nhanh }}
```

### Bước 3: Test trong hệ thống

1. Upload file mới vào Django Admin
2. Tạo thử 1 mẫu biểu
3. Kiểm tra output:
   - Biến có được thay thế đúng không?
   - Format có bị lỗi không?

---

## 🔧 TROUBLESHOOTING

### ❌ Lỗi: "No module named 'docx'"

**Nguyên nhân:** Chưa cài `python-docx`

**Giải pháp:**
```cmd
pip install python-docx
```

---

### ❌ Lỗi: "No module named 'templates_app'"

**Nguyên nhân:** Chạy script ngoài folder project

**Giải pháp:**
```cmd
# Phải chạy trong folder MauBieu7202
cd C:\path\to\MauBieu7202
python convert_old_templates.py ...
```

---

### ❌ Lỗi: "File not found"

**Nguyên nhân:** Đường dẫn sai hoặc file không tồn tại

**Giải pháp:**
```cmd
# Kiểm tra file có tồn tại không
dir templates_cu\mau_1.docx

# Dùng đường dẫn tuyệt đối
python convert_old_templates.py C:\full\path\to\input.docx C:\full\path\to\output.docx
```

---

### ⚠️ Biến không được thay thế

**Nguyên nhân:** Biến không có trong mapping

**Giải pháp:**

1. Kiểm tra file `templates_app/variable_mapping.py`
2. Nếu thiếu biến, thêm vào `OLD_TO_NEW_MAPPING`:

```python
OLD_TO_NEW_MAPPING = {
    # ... existing mappings
    '[BienMoi]': 'bien_moi_trong_he_thong',  # Thêm dòng này
}
```

3. Chạy lại script

---

### ⚠️ Format bị lỗi sau khi convert

**Nguyên nhân:** File Word có cấu trúc phức tạp (textbox, shapes, etc.)

**Giải pháp:** Dùng cách thủ công (Find & Replace trong Word)

---

## 📊 SO SÁNH 2 CÁCH

| Tiêu chí | Thủ công (Word) | Tự động (Script) |
|----------|-----------------|------------------|
| Số file | < 10 files | > 10 files |
| Thời gian | Lâu (5-10p/file) | Nhanh (< 1p/file) |
| Độ chính xác | 100% | 95-98% |
| Format giữ nguyên | ✅ Tốt nhất | ⚠️ Có thể bị lỗi |
| Kiểm soát | ✅ Hoàn toàn | ⚠️ Tự động |
| Khuyến nghị | File phức tạp | File đơn giản, số lượng nhiều |

---

## 📝 CHECKLIST SAU KHI CHUYỂN ĐỔI

- [ ] Backup file gốc
- [ ] Convert tất cả file cần thiết
- [ ] Kiểm tra từng file đã convert:
  - [ ] Biến đã đúng format {{ }}
  - [ ] Không còn biến cũ [...]
  - [ ] Format không bị lỗi
- [ ] Upload file mới vào hệ thống
- [ ] Test tạo mẫu biểu
- [ ] Xóa file cũ (sau khi test xong)

---

## 💡 MẸO HAY

### 1. Convert thử 1 file trước

Đừng convert hết ngay lần đầu! Test với 1 file trước:

```cmd
python convert_old_templates.py templates_cu\mau_test.docx templates_moi\mau_test.docx
```

### 2. So sánh trước/sau

Dùng Word Compare:

```
Word → Review → Compare → Compare Two Versions
```

### 3. Tạo template mapping riêng

Nếu có nhiều biến custom, tạo file `my_mapping.py`:

```python
MY_CUSTOM_MAPPING = {
    '[BienRieng1]': 'bien_rieng_1',
    '[BienRieng2]': 'bien_rieng_2',
}
```

### 4. Batch rename files

```cmd
# Thêm suffix "_new" cho tất cả file
for %f in (templates_moi\*.docx) do ren "%f" "%~nf_new%~xf"
```

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề:

1. Kiểm tra log lỗi
2. Đọc lại hướng dẫn
3. Thử với file khác xem có lỗi tương tự không
4. Liên hệ kỹ thuật với thông tin:
   - File gốc
   - Lỗi chính xác
   - Output của script

---

**Ngày cập nhật:** 03/11/2025
**Phiên bản:** 1.0

# VÍ DỤ CHUYỂN ĐỔI TEMPLATE VỚI CẤU TRÚC THƯ MỤC

## 🎯 Tình huống: Bạn có cấu trúc thư mục như sau

```
templates_cu/
├── mau_mo_tai_khoan.docx
├── mau_dong_tai_khoan.docx
├── the_atm/
│   ├── mau_dang_ky_the_ATM.docx
│   └── mau_huy_the_ATM.docx
├── tiet_kiem/
│   ├── mau_gui_tiet_kiem.docx
│   ├── mau_rut_tiet_kiem.docx
│   └── sao_ke/
│       └── mau_sao_ke_tiet_kiem.docx
└── vay_von/
    ├── mau_dang_ky_vay.docx
    └── mau_tra_no.docx
```

## ✅ Kết quả sau khi chạy script

### Lệnh chạy:

```bash
python convert_old_templates.py ./templates_cu ./templates_moi
```

### Output trên console:

```
************************************************************
  CÔNG CỤ CHUYỂN ĐỔI MẪU BIỂU TỰ ĐỘNG
  Agribank - Chi nhánh Giá Rai Bạc Liêu
************************************************************

Folder input:  /path/to/templates_cu
Folder output: /path/to/templates_moi
Cấu trúc thư mục: GIỮ NGUYÊN (subfolder sẽ được tạo tự động)

⚠️  LƯU Ý:
  - Script sẽ xử lý TẤT CẢ file .docx trong folder (bao gồm subfolder)
  - File backup sẽ bị bỏ qua (file có '_backup_' trong tên)
  - Cấu trúc thư mục gốc sẽ được GIỮ NGUYÊN trong folder output

Nhấn Enter để bắt đầu, hoặc Ctrl+C để hủy...

============================================================
Tìm thấy 9 file .docx
============================================================

[1/9] Đang xử lý: mau_mo_tai_khoan.docx
  ✓ Đã thay thế 12 biến text
  ✓ Đã thay thế 3 checkbox tags

[2/9] Đang xử lý: mau_dong_tai_khoan.docx
  ✓ Đã thay thế 8 biến text

[3/9] Đang xử lý: the_atm/mau_dang_ky_the_ATM.docx
  ✓ Đã thay thế 15 biến text
  ✓ Đã thay thế 8 checkbox tags

[4/9] Đang xử lý: the_atm/mau_huy_the_ATM.docx
  ✓ Đã thay thế 7 biến text

[5/9] Đang xử lý: tiet_kiem/mau_gui_tiet_kiem.docx
  ✓ Đã thay thế 10 biến text

[6/9] Đang xử lý: tiet_kiem/mau_rut_tiet_kiem.docx
  ✓ Đã thay thế 9 biến text

[7/9] Đang xử lý: tiet_kiem/sao_ke/mau_sao_ke_tiet_kiem.docx
  ✓ Đã thay thế 6 biến text

[8/9] Đang xử lý: vay_von/mau_dang_ky_vay.docx
  ✓ Đã thay thế 20 biến text
  ✓ Đã thay thế 2 checkbox tags

[9/9] Đang xử lý: vay_von/mau_tra_no.docx
  ✓ Đã thay thế 14 biến text

============================================================
KẾT QUẢ CHUYỂN ĐỔI
============================================================
✓ Thành công: 9 file

CHI TIẾT BIẾN TEXT ĐÃ THAY THẾ:
--------------------------------------------------------------------------------
  [HotenKhachhangVN]             → {{ ho_ten }}                      (9 lần)
  [SoCMT]                        → {{ so_cmnd }}                     (7 lần)
  [SoTaiKhoan]                   → {{ so_tai_khoan }}                (6 lần)
  ...

CHI TIẾT CHECKBOX TAGS ĐÃ THAY THẾ:
--------------------------------------------------------------------------------
  Check_Nam                      → gioi_tinh_nam                     (6 lần)
  Check_Nu                       → gioi_tinh_nu                      (6 lần)
  Check_C                        → the_hang_chuan                    (1 lần)
  ...

============================================================

✅ HOÀN THÀNH!
```

### Cấu trúc thư mục sau khi convert:

```
templates_moi/
├── mau_mo_tai_khoan.docx           ← Đã convert
├── mau_dong_tai_khoan.docx         ← Đã convert
├── the_atm/                         ← Thư mục được tạo tự động
│   ├── mau_dang_ky_the_ATM.docx    ← Đã convert
│   └── mau_huy_the_ATM.docx        ← Đã convert
├── tiet_kiem/                       ← Thư mục được tạo tự động
│   ├── mau_gui_tiet_kiem.docx      ← Đã convert
│   ├── mau_rut_tiet_kiem.docx      ← Đã convert
│   └── sao_ke/                      ← Thư mục lồng được tạo tự động
│       └── mau_sao_ke_tiet_kiem.docx ← Đã convert
└── vay_von/                         ← Thư mục được tạo tự động
    ├── mau_dang_ky_vay.docx        ← Đã convert
    └── mau_tra_no.docx             ← Đã convert
```

**File gốc trong `templates_cu/` KHÔNG thay đổi!**

---

## 🔥 Tình huống 2: Ghi đè file gốc (có backup)

### Lệnh chạy:

```bash
python convert_old_templates.py ./templates_cu
```

### Kết quả:

```
templates_cu/
├── mau_mo_tai_khoan.docx                           ← File gốc bị GHI ĐÈ (đã convert)
├── mau_mo_tai_khoan_backup_20251109_143025.docx   ← Backup tự động
├── mau_dong_tai_khoan.docx                         ← File gốc bị GHI ĐÈ (đã convert)
├── mau_dong_tai_khoan_backup_20251109_143026.docx ← Backup tự động
├── the_atm/
│   ├── mau_dang_ky_the_ATM.docx                         ← File gốc bị GHI ĐÈ (đã convert)
│   ├── mau_dang_ky_the_ATM_backup_20251109_143027.docx  ← Backup tự động
│   ├── mau_huy_the_ATM.docx                             ← File gốc bị GHI ĐÈ (đã convert)
│   └── mau_huy_the_ATM_backup_20251109_143028.docx      ← Backup tự động
...
```

---

## 💡 MẸO HAY

### 1. Convert thử với 1 folder nhỏ trước

```bash
# Tạo folder test
mkdir test_convert
cp -r templates_cu/the_atm test_convert/

# Convert thử
python convert_old_templates.py test_convert/ test_output/

# Kiểm tra kết quả
ls -R test_output/
```

### 2. Bỏ qua file backup khi chạy lại

File có `_backup_` trong tên sẽ tự động bị bỏ qua. Bạn có thể chạy lại script nhiều lần mà không lo file backup bị convert nhầm.

### 3. Giữ an toàn với option output folder

**Khuyến nghị cho lần đầu:**
```bash
python convert_old_templates.py ./templates_cu ./templates_moi
```

Sau khi kiểm tra OK, có thể ghi đè:
```bash
python convert_old_templates.py ./templates_cu
```

---

## ❓ Câu hỏi thường gặp

### Q: Subfolder có cần tạo trước không?

**A:** KHÔNG. Script tự động tạo tất cả subfolder cần thiết.

### Q: Nếu file đã convert rồi, chạy lại có sao không?

**A:** Không sao. Script sẽ thông báo "Không tìm thấy biến cũ nào" và bỏ qua file đó.

### Q: File backup nằm ở đâu?

**A:**
- **Nếu ghi đè:** Backup nằm cùng folder với file gốc
- **Nếu dùng output folder:** KHÔNG tạo backup (vì file gốc vẫn còn)

### Q: Có thể undo không?

**A:** Có:
- **Option 1 (ghi đè):** Rename file backup, xóa file đã convert
- **Option 2 (output folder):** Xóa folder output, file gốc vẫn còn

---

## 🎯 KẾT LUẬN

Script `convert_old_templates.py` đã được cải tiến để:

✅ **Giữ nguyên cấu trúc thư mục gốc**
✅ **Tự động tạo subfolder trong output**
✅ **Bỏ qua file backup khi scan**
✅ **Xử lý cả thư mục lồng nhiều cấp**

**Khuyến nghị:** Luôn chạy với output folder riêng cho lần đầu để an toàn!

  # HƯỚNG DẪN CHUYỂN ĐỔI MẪU BIỂU TỰ ĐỘNG

## Tổng quan

Script `convert_old_templates.py` giúp bạn **tự động chuyển đổi hàng loạt** mẫu biểu Word từ định dạng cũ `[TenBien]` sang định dạng mới `{{ ten_bien }}`.

**Lợi ích:**
- ✅ Xử lý hàng loạt nhiều file cùng lúc
- ✅ Tự động backup file gốc
- ✅ Báo cáo chi tiết những gì đã thay đổi
- ✅ An toàn - không làm mất dữ liệu

---

## Bảng Mapping Biến

### 📋 Thông tin cá nhân

| Biến cũ | Biến mới | Mô tả |
|---------|----------|-------|
| `[HotenKhachhangVN]` | `{{ ho_ten }}` | Họ và tên khách hàng |
| `[HoTenKhachHang]` | `{{ ho_ten }}` | Họ và tên khách hàng (alias) |
| `[TenKhachHang]` | `{{ ho_ten }}` | Họ và tên khách hàng (alias) |
| `[NgaySinh]` | `{{ ngay_sinh }}` | Ngày sinh |
| `[GioiTinh]` | `{{ gioi_tinh }}` | Giới tính |

### 📋 Giấy tờ tùy thân

| Biến cũ | Biến mới | Mô tả |
|---------|----------|-------|
| `[SoCMT]` | `{{ so_cmnd }}` | Số CMND/CCCD |
| `[SoCMND]` | `{{ so_cmnd }}` | Số CMND/CCCD (alias) |
| `[SoCCCD]` | `{{ so_cmnd }}` | Số CMND/CCCD (alias) |
| `[NgayCMT]` | `{{ ngay_cap_cmnd }}` | Ngày cấp |
| `[NgayCapCMT]` | `{{ ngay_cap_cmnd }}` | Ngày cấp (alias) |
| `[NoiCapCMT]` | `{{ noi_cap_cmnd }}` | Nơi cấp |
| `[NgayHetHanCMT]` | `{{ ngay_het_han_cmnd }}` | Ngày hết hạn |

### 📋 Thông tin liên hệ

| Biến cũ | Biến mới | Mô tả |
|---------|----------|-------|
| `[DiaChiKhachHang]` | `{{ dia_chi }}` | Địa chỉ thường trú |
| `[DiaChi]` | `{{ dia_chi }}` | Địa chỉ (alias) |
| `[SoDienThoai]` | `{{ so_dien_thoai }}` | Số điện thoại |
| `[DienThoai]` | `{{ so_dien_thoai }}` | Số điện thoại (alias) |
| `[Email]` | `{{ email }}` | Email |

### 📋 Thông tin tài khoản & thẻ

| Biến cũ | Biến mới | Mô tả |
|---------|----------|-------|
| `[SoTaiKhoan]` | `{{ so_tai_khoan }}` | Số tài khoản |
| `[STK]` | `{{ so_tai_khoan }}` | Số tài khoản (alias) |
| `[LoaiTaiKhoan]` | `{{ loai_tai_khoan }}` | Loại tài khoản |
| `[LoaiThe]` | `{{ loai_the }}` | Loại thẻ |
| `[HangThe]` | `{{ hang_the }}` | Hạng thẻ |

### 📋 Thông tin chi nhánh

| Biến cũ | Biến mới | Mô tả |
|---------|----------|-------|
| `[TenChiNhanh]` | `{{ ten_chi_nhanh }}` | Tên chi nhánh |
| `[TenChiNhanhHoa]` | `{{ ten_chi_nhanh_hoa }}` | Tên chi nhánh (IN HOA) |
| `[GiaoDichVien]` | `{{ giao_dich_vien }}` | Giao dịch viên |
| `[KiemSoatVien]` | `{{ kiem_soat_vien }}` | Kiểm soát viên |
| `[GiamDoc]` | `{{ giam_doc }}` | Giám đốc |

### 📋 Biến ngày tháng (từng chữ số)

| Biến cũ | Biến mới | Mô tả |
|---------|----------|-------|
| `[d1]`, `[d2]` | `{{ d1 }}`, `{{ d2 }}` | Ngày sinh (2 chữ số) |
| `[m1]`, `[m2]` | `{{ m1 }}`, `{{ m2 }}` | Tháng sinh (2 chữ số) |
| `[y1]`, `[y2]`, `[y3]`, `[y4]` | `{{ y1 }}`, `{{ y2 }}`, `{{ y3 }}`, `{{ y4 }}` | Năm sinh (4 chữ số) |
| `[dcc1]`, `[dcc2]` | `{{ dcc1 }}`, `{{ dcc2 }}` | Ngày cấp CCCD (2 chữ số) |
| `[mcc1]`, `[mcc2]` | `{{ mcc1 }}`, `{{ mcc2 }}` | Tháng cấp CCCD (2 chữ số) |
| `[ycc1]`, `[ycc2]`, `[ycc3]`, `[ycc4]` | `{{ ycc1 }}`, `{{ ycc2 }}`, `{{ ycc3 }}`, `{{ ycc4 }}` | Năm cấp CCCD (4 chữ số) |

---

## Cách sử dụng Script

### Yêu cầu

- Python 3.x đã cài đặt
- Package `python-docx` đã cài (có sẵn trong requirements.txt)

### Cách 1: Ghi đè file gốc (có backup)

**Tình huống:** Bạn muốn thay thế trực tiếp file gốc, script sẽ tự động backup file cũ.

```bash
python convert_old_templates.py ./mau_bieu_cu
```

**Kết quả:**
- File gốc: `mau_1.docx` → bị ghi đè bằng phiên bản mới
- File backup: `mau_1_backup_20251103_143025.docx` (tự động tạo)

### Cách 2: Lưu vào folder mới

**Tình huống:** Bạn muốn giữ nguyên file gốc, tạo file mới trong folder khác.

```bash
python convert_old_templates.py ./mau_bieu_cu ./mau_bieu_moi
```

**Kết quả:**
- File gốc: `./mau_bieu_cu/mau_1.docx` → KHÔNG thay đổi
- File mới: `./mau_bieu_moi/mau_1.docx` → đã convert

---

## Ví dụ thực tế

### Ví dụ 1: Convert tất cả file trong folder

**Cấu trúc folder:**
```
mau_bieu_cu/
├── mau_mo_tai_khoan.docx
├── mau_dang_ky_the.docx
├── mau_dong_tai_khoan.docx
└── sub_folder/
    └── mau_khac.docx
```

**Chạy lệnh:**
```bash
python convert_old_templates.py ./mau_bieu_cu
```

**Output:**
```
************************************************************
  CÔNG CỤ CHUYỂN ĐỔI MẪU BIỂU TỰ ĐỘNG
  Agribank - Chi nhánh Giá Rai Bạc Liêu
************************************************************

Folder input:  /path/to/mau_bieu_cu
Folder output: GHI ĐÈ FILE GỐC (có backup)

Nhấn Enter để bắt đầu, hoặc Ctrl+C để hủy...

============================================================
Tìm thấy 4 file .docx
============================================================

[1/4] Đang xử lý: mau_mo_tai_khoan.docx
  ✓ Đã backup: mau_mo_tai_khoan_backup_20251103_143025.docx
  ✓ Đã thay thế 15 biến

[2/4] Đang xử lý: mau_dang_ky_the.docx
  ✓ Đã backup: mau_dang_ky_the_backup_20251103_143026.docx
  ✓ Đã thay thế 23 biến

[3/4] Đang xử lý: mau_dong_tai_khoan.docx
  ✓ Đã backup: mau_dong_tai_khoan_backup_20251103_143027.docx
  ✓ Đã thay thế 8 biến

[4/4] Đang xử lý: mau_khac.docx
  ✓ Đã backup: mau_khac_backup_20251103_143028.docx
  ✓ Đã thay thế 12 biến

============================================================
KẾT QUẢ CHUYỂN ĐỔI
============================================================
✓ Thành công: 4 file

CHI TIẾT CÁC BIẾN ĐÃ THAY THẾ:
------------------------------------------------------------
  [HotenKhachhangVN]             → {{ ho_ten }}               (12 lần)
  [SoCMT]                        → {{ so_cmnd }}              (8 lần)
  [DiaChiKhachHang]              → {{ dia_chi }}              (7 lần)
  [SoDienThoai]                  → {{ so_dien_thoai }}        (6 lần)
  [SoTaiKhoan]                   → {{ so_tai_khoan }}         (5 lần)
  [NgayCMT]                      → {{ ngay_cap_cmnd }}        (4 lần)
  [TenChiNhanh]                  → {{ ten_chi_nhanh }}        (4 lần)
  [GiaoDichVien]                 → {{ giao_dich_vien }}       (3 lần)
  ...
============================================================

✅ HOÀN THÀNH!
```

### Ví dụ 2: Xem bảng mapping trước khi convert

```bash
python convert_old_templates.py --mapping
```

Sẽ hiển thị toàn bộ bảng mapping để bạn tham khảo.

---

## Quy trình làm việc đề xuất

### Bước 1: Chuẩn bị

1. **Sao lưu toàn bộ** folder mẫu biểu cũ ra nơi an toàn
2. Copy folder mẫu biểu vào folder làm việc
3. Đặt script `convert_old_templates.py` vào folder project

### Bước 2: Chạy thử nghiệm

Chọn **1-2 file mẫu** để test trước:

```bash
# Tạo folder test
mkdir test_convert
cp mau_bieu_cu/mau_test.docx test_convert/

# Convert folder test
python convert_old_templates.py test_convert
```

Mở file đã convert, kiểm tra xem các biến đã được thay thế đúng chưa.

### Bước 3: Convert toàn bộ

Khi đã hài lòng với kết quả test:

```bash
# Option A: Ghi đè file gốc (có backup)
python convert_old_templates.py ./mau_bieu_cu

# Option B: Tạo folder mới
python convert_old_templates.py ./mau_bieu_cu ./mau_bieu_moi
```

### Bước 4: Kiểm tra kết quả

1. Mở một số file đã convert
2. Kiểm tra các biến đã đúng định dạng `{{ ten_bien }}`
3. Kiểm tra formatting Word không bị hỏng
4. Upload lên hệ thống và test generate document

### Bước 5: Upload lên hệ thống

Upload các file đã convert vào hệ thống như bình thường.

---

## Xử lý trường hợp đặc biệt

### Trường hợp 1: File có biến custom chưa có trong mapping

**Tình huống:** File của bạn có biến `[TenNganHang]` nhưng chưa có trong mapping.

**Giải pháp:**

1. Mở file `convert_old_templates.py`
2. Thêm vào `VARIABLE_MAPPING`:
   ```python
   VARIABLE_MAPPING = {
       # ... các biến có sẵn ...
       '[TenNganHang]': '{{ ten_ngan_hang }}',  # ← Thêm dòng này
   }
   ```
3. Lưu file và chạy lại script

### Trường hợp 2: Muốn convert nhưng KHÔNG backup

**Giải pháp:** Sửa dòng này trong script (line ~242):

```python
# Thay đổi từ
process_folder(input_folder, output_folder, backup=True)

# Thành
process_folder(input_folder, output_folder, backup=False)
```

**⚠️ CẢNH BÁO:** Không khuyến khích, dễ mất dữ liệu!

### Trường hợp 3: Có file lỗi, không convert được

Script sẽ bỏ qua file lỗi và tiếp tục xử lý các file khác. Xem log để biết file nào bị lỗi:

```
[5/10] Đang xử lý: mau_loi.docx
  ❌ Lỗi: Document is corrupted
```

**Giải pháp:**
- Mở file bằng Word, Save As để sửa lỗi
- Hoặc bỏ qua file đó, convert thủ công sau

---

## Câu hỏi thường gặp (FAQ)

### ❓ Script có làm mất formatting của Word không?

**Trả lời:** Không. Script chỉ thay thế text, giữ nguyên tất cả formatting (font, màu sắc, bảng, hình ảnh, v.v.).

### ❓ Tôi có thể undo nếu convert sai?

**Trả lời:** Có.
- **Cách 1 (ghi đè):** Dùng file backup được tạo tự động
- **Cách 2 (folder mới):** File gốc vẫn còn nguyên

### ❓ Script có xử lý được file trong sub-folder không?

**Trả lời:** Có. Script tự động quét tất cả sub-folder và convert tất cả file `.docx` tìm thấy.

### ❓ Tôi có thể thêm biến mới vào mapping không?

**Trả lời:** Có. Chỉnh sửa dictionary `VARIABLE_MAPPING` trong script (từ dòng 20).

### ❓ Script có convert file đang mở trong Word không?

**Trả lời:** Không. Đóng tất cả file Word trước khi chạy script.

### ❓ Làm sao biết biến nào đã được thay thế?

**Trả lời:** Xem phần "CHI TIẾT CÁC BIẾN ĐÃ THAY THẾ" trong output của script.

---

## Lưu ý quan trọng

### ✅ NÊN

- ✅ Backup toàn bộ folder gốc trước khi convert
- ✅ Test với 1-2 file trước khi convert hàng loạt
- ✅ Đóng tất cả file Word trước khi chạy script
- ✅ Kiểm tra kết quả sau khi convert
- ✅ Upload file đã convert lên hệ thống để test

### ❌ KHÔNG NÊN

- ❌ Convert trực tiếp trên folder production mà không backup
- ❌ Chạy script khi file đang mở trong Word
- ❌ Bỏ qua bước test trước khi convert hàng loạt
- ❌ Xóa file backup ngay sau khi convert

---

## Hỗ trợ

Nếu gặp vấn đề:

1. Kiểm tra log output của script
2. Đảm bảo Python và python-docx đã cài đúng
3. Kiểm tra quyền đọc/ghi file
4. Thử convert 1 file đơn lẻ để test

---

**Phiên bản:** 1.0
**Ngày tạo:** 2025-11-03
**Tác giả:** Hệ thống Mẫu biểu Agribank

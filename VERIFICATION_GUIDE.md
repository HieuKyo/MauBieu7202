# Hướng dẫn Kiểm tra - Verification Guide

## Trạng thái hiện tại / Current Status

Tất cả các sửa lỗi đã được thực hiện và commit vào branch `claude/print-preview-highlight-edit-011CV4nabLadRxGEJYnQ3EtZ`.

All fixes have been implemented and committed to branch `claude/print-preview-highlight-edit-011CV4nabLadRxGEJYnQ3EtZ`.

---

## Các tính năng đã hoàn thành / Completed Features

### 1. ✅ Print Preview với Highlight và Inline Editing
- **File**: `templates_app/templates/templates_app/print_preview.html`
- **Chức năng**:
  - Xem trước mẫu biểu với HTML
  - Highlight các trường đã điền (màu vàng)
  - Chế độ chỉnh sửa inline (Ctrl+E)
  - Lưu thay đổi (Ctrl+S)
  - In (Ctrl+P)
  - Tải Word

### 2. ✅ Loại bỏ "Biến" và "Biến mẫu biểu" khỏi Admin
- **File**: `templates_app/admin.py`
- **Thay đổi**:
  - Comment out Variable admin (lines 89-160)
  - Comment out TemplateVariable admin (lines 300-309)
  - Removed TemplateVariableInline from TemplateAdmin

---

## Các lỗi đã sửa / Fixed Bugs

### 3. ✅ Logic so_tai_khoan_yc (Số TK theo yêu cầu)
- **File**: `templates_app/models.py` (lines 747-758)
- **Logic**:
  ```python
  if self.loai_tai_khoan == 'Tài khoản số theo yêu cầu' and self.so_tai_khoan_yc:
      data['so_tai_khoan_yc'] = self.so_tai_khoan_yc  # Hiển thị số
  else:
      data['so_tai_khoan_yc'] = '.................'  # Hiển thị dấu chấm
  ```
- **Test**: Khi KHÔNG chọn "Tài khoản số theo yêu cầu", biến {{so_tai_khoan_yc}} sẽ hiển thị "................."

### 4. ✅ Checkbox CCCD/Căn cước (ngày cấp)
- **File**: `templates_app/models.py` (lines 536-564)
- **Logic**:
  - CMND: 9 chữ số → check {{cmnd}}
  - CCCD: 12 chữ số, ngày cấp ≤ 01/07/2024 → check {{cccd}}
  - Căn cước: 12 chữ số, ngày cấp > 01/07/2024 → check {{cancuoc}}
- **Test**: Ngày cấp 11/2025 (tháng 11 năm 2025) > 01/07/2024 → phải check {{cancuoc}}

### 5. ✅ Checkbox nghề nghiệp
- **File**: `templates_app/models.py` (lines 570-580)
- **Mapping**:
  - nghe_nghiep_cong_chuc → "Công chức viên chức"
  - nghe_nghiep_nong_dan → "Nông dân"
  - nghe_nghiep_giao_vien_bac_si → "Giáo viên/Bác Sĩ"
  - nghe_nghiep_cong_nhan → "Công nhân"
  - nghe_nghiep_kinh_doanh → "Kinh doanh tự do"
  - nghe_nghiep_hoc_sinh_sinh_vien → "Học sinh/Sinh viên"
  - nghe_nghiep_noi_tro → "Nội trợ"
  - nghe_nghiep_cong_an_bo_doi → "Công an/Bộ đội"
  - nghe_nghiep_ky_su → "Kỹ sư"
  - nghe_nghiep_khac → "Khác"

### 6. ✅ E-Mobile Banking checkbox
- **File**: `templates_app/models.py` (lines 663-664)
- **Logic**:
  ```python
  'dv_e_mobile': checkbox(self.dv_e_mobile),
  'dv_vidientu': checkbox(self.dv_e_mobile),  # Alias
  ```
- **Test**: Checkbox tag {{dv_e_mobile}} và {{dv_vidientu}} đều map với field dv_e_mobile

### 7. ✅ Bảng tên thẻ (Card Name Table)
- **File**: `templates_app/utils.py` (lines 385-400, 773-786)
- **Logic**:
  - Duyệt qua từng cell trong bảng
  - Điền ký tự tên thẻ vào cell
  - Xóa các cell còn lại (set text = '')
- **Test**: Không còn cell trống thừa trong bảng tên thẻ

### 8. ✅ Biến dv_abic và ngay_tra_the
- **File**: `templates_app/models.py` (line 721, 632)
- **Logic**:
  ```python
  'dv_abic': checkbox(self.dv_abic),
  'ngay_tra_the': self.ngay_tra_the.strftime('%d/%m/%Y') if self.ngay_tra_the else '',
  ```
- **Test**: Nếu hiển thị là {{dv_abic}} hoặc {{ngay_tra_the}}, kiểm tra Word template có đúng syntax {{variable}} hay không

---

## Cách kiểm tra / How to Verify

### Bước 1: Pull code mới nhất
```bash
git pull origin claude/print-preview-highlight-edit-011CV4nabLadRxGEJYnQ3EtZ
```

### Bước 2: Cài đặt dependencies (nếu cần)
```bash
pip install mammoth==1.8.0
```

### Bước 3: Khởi động lại server
```bash
python manage.py runserver
```

### Bước 4: Test với dữ liệu thực
1. Truy cập admin: http://localhost:8000/admin/
2. Tạo/sửa Customer với:
   - so_cmnd: 12 chữ số
   - ngay_cap_cmnd: 15/11/2025 (hoặc bất kỳ ngày nào sau 01/07/2024)
   - nghe_nghiep: Chọn một trong 10 lựa chọn
   - loai_tai_khoan: Chọn "Tài khoản ngẫu nhiên" (KHÔNG chọn "Tài khoản số theo yêu cầu")
   - dv_e_mobile: Check
   - dv_abic: Check
3. Chọn một Template và điền form
4. Nhấn "Xem trước"
5. Kiểm tra:
   - ✓ {{cancuoc}} được check (vì ngày cấp > 01/07/2024)
   - ✓ {{nghe_nghiep_xxx}} được check đúng nghề đã chọn
   - ✓ {{so_tai_khoan_yc}} hiển thị "................." (vì không chọn TK theo yêu cầu)
   - ✓ {{dv_e_mobile}} được check
   - ✓ {{dv_abic}} được check
   - ✓ {{ngay_tra_the}} hiển thị ngày đúng định dạng
   - ✓ Bảng tên thẻ không có cell trống thừa

### Bước 5: Test Print Preview Features
1. Nhấn nút "Xem trước" (Preview)
2. Kiểm tra:
   - ✓ Các trường đã điền được highlight màu vàng
   - ✓ Nhấn "Chế độ chỉnh sửa" → có thể edit inline
   - ✓ Nhấn "Lưu thay đổi" → lưu được
   - ✓ Nhấn "In" → in được
   - ✓ Nhấn "Tải Word" → tải file .docx

---

## Lưu ý quan trọng / Important Notes

### Nếu biến vẫn hiển thị dạng {{variable}}:

1. **Kiểm tra Word template**:
   - Mở file .docx template
   - Tìm kiếm {{variable}} (ví dụ: {{dv_abic}})
   - Đảm bảo syntax là: `{{variable}}` không có khoảng trắng thừa
   - **KHÔNG DÙNG**: `{{ variable }}` hoặc `[variable]`

2. **Kiểm tra Content Control Tag**:
   - Mở Word → Developer tab → Design Mode
   - Click vào checkbox/textbox
   - Properties → Tag phải khớp với tên biến (không có {{ }})
   - Ví dụ: Tag là `dv_abic`, biến là `{{dv_abic}}`

3. **Kiểm tra dữ liệu Customer**:
   - Đảm bảo field có giá trị (không null/empty)
   - Chạy script test:
     ```bash
     python test_customer_data.py
     ```

### Nếu checkbox không được check:

1. **Tag không khớp**: Tag trong Word phải giống tên biến trong code
2. **Dữ liệu không khớp**: Giá trị trong Customer phải khớp CHÍNH XÁC với điều kiện
   - Ví dụ: nghe_nghiep = "Công chức viên chức" (không phải "Công chức")
3. **Checkbox character**: Đảm bảo Word template sử dụng checkbox character ☑ (U+2611)

---

## Debug Script

Chạy script test để xem tất cả biến được tạo ra:

```bash
python test_customer_data.py
```

Script này sẽ hiển thị:
- Thông tin cơ bản của Customer
- Tất cả checkbox variables (cmnd, cccd, cancuoc, nghề nghiệp, dịch vụ, v.v.)
- Các biến đặc biệt (so_tai_khoan_yc, ngay_tra_the, ten_the_1, v.v.)

---

## File đã thay đổi / Changed Files

1. `requirements.txt` - Thêm mammoth==1.8.0
2. `templates_app/models.py` - Sửa logic get_data_dict()
3. `templates_app/utils.py` - Sửa _render_card_name_tables()
4. `templates_app/views.py` - Thêm print_preview_view(), update_preview_data()
5. `templates_app/urls.py` - Thêm routes cho preview
6. `templates_app/admin.py` - Comment out Variable/TemplateVariable admin
7. `templates_app/templates/templates_app/print_preview.html` - NEW FILE
8. `templates_app/templates/templates_app/template_form.html` - Thêm nút "Xem trước"
9. `test_customer_data.py` - NEW FILE (debug script)

---

## Liên hệ / Contact

Nếu vẫn gặp vấn đề, vui lòng cung cấp:
1. Screenshot Word template (Developer mode ON)
2. Output của script test_customer_data.py
3. Screenshot file Word được generate ra
4. Django debug log (nếu có lỗi)

---

**Cập nhật lần cuối**: 2025-01-13
**Branch**: claude/print-preview-highlight-edit-011CV4nabLadRxGEJYnQ3EtZ

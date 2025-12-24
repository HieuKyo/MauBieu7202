# 📋 BẢNG MAPPING TAGS CHO FILE WORD MẪU

## 📌 Hướng dẫn tạo file Word Template

### Vị trí file:
```
tax_payment/templates/tax_statement_template.docx
```

---

## 🏷️ DANH SÁCH ĐẦY ĐỦ CÁC JINJA2 TAGS

### 1️⃣ THÔNG TIN NGƯỜI NỘP THUẾ

| Thông tin trên Bảng kê | Tên biến (Tag) trong Word | Kiểu dữ liệu | Ví dụ dữ liệu |
| :--- | :--- | :--- | :--- |
| Tên người nộp thuế | `{{ ten_nguoi_nop }}` | String | Nguyễn Văn A |
| Mã số thuế | `{{ ma_so_thue }}` | String | 0123456789 |
| Địa chỉ | `{{ dia_chi }}` | String | 123 Đường ABC, Quận 1, TP.HCM |
| Ngày lập bảng kê | `{{ ngay_lap }}` | Date (dd/mm/yyyy) | 24/12/2024 |

**Cách dùng trong Word:**
```
Kính gửi: Cơ quan thuế
Người nộp thuế: {{ ten_nguoi_nop }}
Mã số thuế: {{ ma_so_thue }}
Địa chỉ: {{ dia_chi }}
Ngày lập: {{ ngay_lap }}
```

---

### 2️⃣ THÔNG TIN CƠ QUAN THU

| Thông tin trên Bảng kê | Tên biến (Tag) trong Word | Kiểu dữ liệu | Ví dụ dữ liệu |
| :--- | :--- | :--- | :--- |
| Tỉnh/Thành phố | `{{ tinh }}` | String | Hồ Chí Minh |
| Cơ quan thuế (nhóm) | `{{ co_quan_thue }}` | String | Cục Thuế TP. Hồ Chí Minh |
| Xã/Phường | `{{ xa_phuong }}` | String | Phường Bến Nghé |
| Mã cơ quan thu | `{{ ma_co_quan_thu }}` | String | 1139446 |
| Tên cơ quan thu (đầy đủ) | `{{ ten_co_quan_thu }}` | String | Chi cục Thuế Quận 1 - TP. Hồ Chí Minh |
| Mã địa bàn | `{{ ma_dia_ban }}` | String | 31957 |
| Kho bạc nhà nước (KBNN) | `{{ kho_bac }}` | String | Kho bạc Nhà nước Quận 1 |

**Cách dùng trong Word:**
```
Kính gửi: {{ ten_co_quan_thu }}
Mã cơ quan thu: {{ ma_co_quan_thu }}
Mã địa bàn: {{ ma_dia_ban }}

Địa điểm nộp:
- Tỉnh/TP: {{ tinh }}
- Quận/Huyện: {{ co_quan_thue }}
- Phường/Xã: {{ xa_phuong }}

Nộp tại: {{ kho_bac }}
```

---

### 3️⃣ THÔNG TIN TỔNG HỢP

| Thông tin trên Bảng kê | Tên biến (Tag) trong Word | Kiểu dữ liệu | Ví dụ dữ liệu |
| :--- | :--- | :--- | :--- |
| Tổng số tiền (đã format) | `{{ tong_so_tien }}` | String (formatted) | 15.500.000 |

**Cách dùng trong Word:**
```
TỔNG CỘNG: {{ tong_so_tien }} VNĐ

Bằng chữ: ....................................
```

---

### 4️⃣ DANH SÁCH CÁC KHOẢN NỘP (BẢNG - TABLE LOOP)

**⚠️ QUAN TRỌNG:** Đây là phần dữ liệu động - hiển thị nhiều dòng trong bảng

#### Cấu trúc dữ liệu mỗi dòng (item):

| Cột trong bảng | Tên biến (Tag) | Kiểu dữ liệu | Ví dụ dữ liệu |
| :--- | :--- | :--- | :--- |
| Số thứ tự | `{{ item.stt }}` | Integer | 1, 2, 3, 4... |
| Mã tiểu mục | `{{ item.ma_tieu_muc }}` | String | 1001 |
| Nội dung kinh tế | `{{ item.noi_dung }}` | String | Thuế thu nhập cá nhân |
| Số tiền (đã format) | `{{ item.so_tien }}` | String (formatted) | 5.000.000 |

---

## 🔄 HƯỚNG DẪN TẠO VÒNG LẶP TRONG BẢNG WORD

### Cú pháp Jinja2 cho Table Row Loop:
```jinja2
{%tr for item in items %}
    Nội dung lặp lại ở đây
{%tr endfor %}
```

### Ví dụ chi tiết:

**Cấu trúc bảng trong Word:**

| STT | Mã tiểu mục | Nội dung | Số tiền (VNĐ) |
| --- | --- | --- | --- |
| **← Dòng 1: Header (Tiêu đề bảng)** |
| {%tr for item in items %} |
| **← Dòng 2: Bắt đầu vòng lặp (merge tất cả các cột hoặc đặt trong 1 ô)** |
| {{ item.stt }} | {{ item.ma_tieu_muc }} | {{ item.noi_dung }} | {{ item.so_tien }} |
| **← Dòng 3: Template cho mỗi dòng dữ liệu** |
| {%tr endfor %} |
| **← Dòng 4: Kết thúc vòng lặp (merge tất cả các cột hoặc đặt trong 1 ô)** |

---

## 📝 HƯỚNG DẪN CỤ THỂ TỪNG BƯỚC

### Bước 1: Tạo Bảng trong Word

1. Mở Microsoft Word
2. Insert → Table → Chọn 4 cột
3. Tạo ít nhất 4 dòng:
   - Dòng 1: Header
   - Dòng 2: Tag bắt đầu loop
   - Dòng 3: Nội dung template
   - Dòng 4: Tag kết thúc loop

### Bước 2: Định dạng Header

**Dòng 1 (Header):**
| STT | Mã tiểu mục | Nội dung | Số tiền (VNĐ) |

Format:
- Font: Bold
- Alignment: Center
- Background: Light gray (tùy chọn)

### Bước 3: Đặt Tag bắt đầu vòng lặp

**Dòng 2:**
- Merge tất cả 4 cột thành 1 ô
- Hoặc chỉ đặt trong cột đầu tiên
- Nhập: `{%tr for item in items %}`

### Bước 4: Đặt Template cho dữ liệu

**Dòng 3:** (4 ô riêng biệt)
| {{ item.stt }} | {{ item.ma_tieu_muc }} | {{ item.noi_dung }} | {{ item.so_tien }} |

Lưu ý:
- Mỗi tag trong một ô riêng
- Có thể định dạng (font, alignment) cho từng ô
- Số tiền nên align right

### Bước 5: Đặt Tag kết thúc vòng lặp

**Dòng 4:**
- Merge tất cả 4 cột thành 1 ô
- Hoặc chỉ đặt trong cột đầu tiên
- Nhập: `{%tr endfor %}`

---

## 🎨 MẪU TEMPLATE WORD HOÀN CHỈNH

```
╔═══════════════════════════════════════════════════════════════╗
║                  BẢNG KÊ NỘP THUẾ                             ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Kính gửi: {{ ten_co_quan_thu }}                             ║
║  Mã cơ quan thu: {{ ma_co_quan_thu }}                        ║
║  Mã địa bàn: {{ ma_dia_ban }}                                ║
║                                                               ║
║  Người nộp thuế: {{ ten_nguoi_nop }}                         ║
║  Mã số thuế: {{ ma_so_thue }}                                ║
║  Địa chỉ: {{ dia_chi }}                                      ║
║  Ngày lập: {{ ngay_lap }}                                    ║
║                                                               ║
║  Nộp tại: {{ kho_bac }}                                      ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │ DANH SÁCH CÁC KHOẢN NỘP                                 │ ║
║  ├──────┬──────────────┬─────────────────┬────────────────┤ ║
║  │ STT  │ Mã tiểu mục  │ Nội dung        │ Số tiền (VNĐ)  │ ║
║  ├──────┴──────────────┴─────────────────┴────────────────┤ ║
║  │ {%tr for item in items %}                               │ ║
║  ├──────┬──────────────┬─────────────────┬────────────────┤ ║
║  │{{item.stt}}│{{item.ma_tieu_muc}}│{{item.noi_dung}}│{{item.so_tien}}│
║  ├──────┴──────────────┴─────────────────┴────────────────┤ ║
║  │ {%tr endfor %}                                          │ ║
║  └─────────────────────────────────────────────────────────┘ ║
║                                                               ║
║  TỔNG CỘNG: {{ tong_so_tien }} VNĐ                           ║
║                                                               ║
║  Bằng chữ: ..............................................    ║
║                                                               ║
║                                                               ║
║             Người lập bảng kê                                 ║
║          (Ký, ghi rõ họ tên)                                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## ⚙️ LƯU Ý QUAN TRỌNG

### 1. Format File
- ✅ Sử dụng `.docx` (Word 2007+)
- ❌ KHÔNG dùng `.doc` (Word 97-2003)

### 2. Encoding
- Sử dụng font Unicode: Arial, Times New Roman
- Đảm bảo tiếng Việt hiển thị đúng

### 3. Cú pháp Jinja2
- Biến đơn: `{{ ten_bien }}`
- Vòng lặp trong bảng: `{%tr for ... %}...{%tr endfor %}`
- Dấu ngoặc: PHẢI dùng `{{` và `}}` (2 dấu ngoặc)

### 4. Format số tiền
- Số tiền đã được format sẵn: `15.500.000`
- Dấu chấm (`.`) ngăn cách hàng nghìn
- KHÔNG cần format thêm trong template

### 5. Kiểm tra Template

Checklist trước khi sử dụng:
- [ ] Tất cả tags có dấu `{{ }}` hoặc `{% %}` đúng
- [ ] Vòng lặp có `{%tr for %}` và `{%tr endfor %}`
- [ ] Không có lỗi chính tả trong tên biến
- [ ] File lưu ở đúng vị trí: `tax_payment/templates/tax_statement_template.docx`

---

## 🔍 DEBUG TEMPLATE

Nếu template không hoạt động:

1. **Kiểm tra cú pháp:**
   - Mở file `.docx` bằng Word
   - Tìm kiếm `{{` hoặc `{%` để tìm tất cả tags
   - Đảm bảo tất cả tags đều đóng đúng

2. **Kiểm tra table loop:**
   - Vòng lặp PHẢI dùng `{%tr` không phải `{%`
   - Tag phải nằm trong table cell

3. **Test với dữ liệu đơn giản:**
   - Tạo bảng kê test với 1-2 dòng
   - Kiểm tra output Word có đúng không

4. **Xem Django log:**
   ```bash
   python manage.py runserver
   # Xem console để biết lỗi chi tiết
   ```

---

## 📖 TÀI LIỆU THAM KHẢO

- **docxtpl Documentation**: https://docxtpl.readthedocs.io/
- **Jinja2 Syntax**: https://jinja.palletsprojects.com/

---

## ✅ VÍ DỤ THỰC TẾ

### Input (Dữ liệu từ form):
```python
ten_nguoi_nop = "Nguyễn Văn A"
ma_so_thue = "0123456789"
items = [
    {"stt": 1, "ma_tieu_muc": "1001", "noi_dung": "Thuế TNCN", "so_tien": "5.000.000"},
    {"stt": 2, "ma_tieu_muc": "1002", "noi_dung": "Thuế VAT", "so_tien": "10.500.000"}
]
tong_so_tien = "15.500.000"
```

### Output (Kết quả trong Word):
```
Người nộp thuế: Nguyễn Văn A
Mã số thuế: 0123456789

┌────┬──────────────┬─────────────┬───────────────┐
│ STT│ Mã tiểu mục  │ Nội dung    │ Số tiền (VNĐ) │
├────┼──────────────┼─────────────┼───────────────┤
│ 1  │ 1001         │ Thuế TNCN   │ 5.000.000     │
│ 2  │ 1002         │ Thuế VAT    │ 10.500.000    │
└────┴──────────────┴─────────────┴───────────────┘

TỔNG CỘNG: 15.500.000 VNĐ
```

---

## 🎯 TIPS & TRICKS

### 1. Alignment trong bảng:
- STT: Center align
- Mã tiểu mục: Left align
- Nội dung: Left align
- Số tiền: Right align

### 2. Formatting:
- Header: Bold, Background màu nhạt
- Số tiền: Font bold hoặc màu xanh
- Tổng cộng: Font to, bold, màu đỏ

### 3. Multi-line content:
Nếu nội dung dài, cho phép wrap text trong cell:
- Right-click cell → Table Properties → Cell → Options → Wrap text

### 4. Copy template:
Để tạo nhiều template khác nhau:
- Copy file `tax_statement_template.docx`
- Đổi tên: `tax_statement_template_v2.docx`
- Chỉnh sửa code view để chọn template

---

**Chúc bạn thành công với template Word!** 🎉

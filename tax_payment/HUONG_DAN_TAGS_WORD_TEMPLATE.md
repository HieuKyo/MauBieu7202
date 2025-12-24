# HƯỚNG DẪN TẠO FILE WORD MẪU CHO BẢNG KÊ NỘP THUẾ

## 📋 Mục đích
Tài liệu này hướng dẫn cách tạo file Word mẫu (template) để xuất Bảng Kê Nộp Thuế sử dụng thư viện `docxtpl`.

---

## 📍 Vị trí File Template
Đặt file template Word tại đường dẫn:
```
tax_payment/templates/tax_statement_template.docx
```

---

## 🏷️ DANH SÁCH CÁC TAGS (JINJA2 VARIABLES)

### 1. Thông tin Người Nộp Thuế

| Thông tin trên Bảng kê | Tên biến (Tag) trong Word | Ví dụ dữ liệu |
| :--- | :--- | :--- |
| Tên người nộp thuế | `{{ ten_nguoi_nop }}` | Nguyễn Văn A |
| Mã số thuế | `{{ ma_so_thue }}` | 0123456789 |
| Địa chỉ | `{{ dia_chi }}` | 123 Đường ABC, Quận 1, TP.HCM |
| Ngày lập bảng kê | `{{ ngay_lap }}` | 24/12/2024 |

**Cách sử dụng trong Word:**
```
Tên người nộp: {{ ten_nguoi_nop }}
Mã số thuế: {{ ma_so_thue }}
Địa chỉ: {{ dia_chi }}
Ngày lập: {{ ngay_lap }}
```

---

### 2. Thông tin Cơ Quan Thu

| Thông tin trên Bảng kê | Tên biến (Tag) trong Word | Ví dụ dữ liệu |
| :--- | :--- | :--- |
| Tỉnh/Thành phố | `{{ tinh }}` | Hồ Chí Minh |
| Cơ quan thuế | `{{ co_quan_thue }}` | Cục Thuế TP. Hồ Chí Minh |
| Xã/Phường | `{{ xa_phuong }}` | Phường Bến Nghé |
| Mã cơ quan thu | `{{ ma_co_quan_thu }}` | 1139446 |
| Tên cơ quan thu (đầy đủ) | `{{ ten_co_quan_thu }}` | Chi cục Thuế Quận 1 - TP. Hồ Chí Minh |
| Mã địa bàn | `{{ ma_dia_ban }}` | 31957 |
| Kho bạc nhà nước (KBNN) | `{{ kho_bac }}` | Kho bạc Nhà nước Quận 1 |

**Cách sử dụng trong Word:**
```
Kính gửi: {{ ten_co_quan_thu }}
Mã cơ quan thu: {{ ma_co_quan_thu }}
Mã địa bàn: {{ ma_dia_ban }}
Nộp tại: {{ kho_bac }}
```

---

### 3. Thông tin Tổng hợp

| Thông tin trên Bảng kê | Tên biến (Tag) trong Word | Ví dụ dữ liệu |
| :--- | :--- | :--- |
| Tổng số tiền (đã format) | `{{ tong_so_tien }}` | 15.500.000 |

**Cách sử dụng trong Word:**
```
TỔNG CỘNG: {{ tong_so_tien }} VNĐ
```

---

### 4. Danh sách Các Khoản Nộp (Bảng - Table Loop)

Đây là phần QUAN TRỌNG NHẤT - hiển thị nhiều dòng tiểu mục trong bảng.

#### Các biến trong mỗi dòng:

| Cột trong bảng | Tên biến (Tag) | Ví dụ dữ liệu |
| :--- | :--- | :--- |
| Số thứ tự | `{{ item.stt }}` | 1, 2, 3,... |
| Mã tiểu mục | `{{ item.ma_tieu_muc }}` | 1001 |
| Nội dung kinh tế | `{{ item.noi_dung }}` | Thuế thu nhập cá nhân |
| Số tiền (đã format) | `{{ item.so_tien }}` | 5.000.000 |

---

## 📝 HƯỚNG DẪN TẠO VÒNG LẶP TRONG WORD

### Bước 1: Tạo Bảng trong Word

Tạo một bảng với các cột như sau:

| STT | Mã tiểu mục | Nội dung | Số tiền (VNĐ) |
| --- | --- | --- | --- |
| {%tr for item in items %} | | | |
| {{ item.stt }} | {{ item.ma_tieu_muc }} | {{ item.noi_dung }} | {{ item.so_tien }} |
| {%tr endfor %} | | | |

### Bước 2: Cú pháp Jinja2 cho Vòng lặp trong Bảng

**QUAN TRỌNG:** Sử dụng `{%tr for ... %}` và `{%tr endfor %}` cho vòng lặp trong bảng Word.

```
{%tr for item in items %}
{{ item.stt }} | {{ item.ma_tieu_muc }} | {{ item.noi_dung }} | {{ item.so_tien }}
{%tr endfor %}
```

### Bước 3: Cách đặt Tag trong Word

1. **Tạo bảng** với 4 cột: STT, Mã tiểu mục, Nội dung, Số tiền
2. Ở **dòng đầu tiên** (header): Đặt tiêu đề bảng
3. Ở **dòng thứ hai**: Đặt tag `{%tr for item in items %}`
   - Lưu ý: Đặt trong một ô riêng, hoặc merge toàn bộ dòng
4. Ở **dòng thứ ba**: Đặt các biến hiển thị
   - Ô 1: `{{ item.stt }}`
   - Ô 2: `{{ item.ma_tieu_muc }}`
   - Ô 3: `{{ item.noi_dung }}`
   - Ô 4: `{{ item.so_tien }}`
5. Ở **dòng thứ tư**: Đặt tag `{%tr endfor %}`
   - Tương tự như dòng 2, có thể merge cells

---

## 🎨 MẪU TEMPLATE WORD HOÀN CHỈNH

```
┌────────────────────────────────────────────────────────────┐
│             BẢNG KÊ NỘP THUẾ                               │
│                                                            │
│ Người nộp: {{ ten_nguoi_nop }}                            │
│ Mã số thuế: {{ ma_so_thue }}                              │
│ Địa chỉ: {{ dia_chi }}                                    │
│ Ngày lập: {{ ngay_lap }}                                  │
│                                                            │
│ Kính gửi: {{ ten_co_quan_thu }}                           │
│ Mã cơ quan thu: {{ ma_co_quan_thu }}                      │
│ Mã địa bàn: {{ ma_dia_ban }}                              │
│ Nộp tại KBNN: {{ kho_bac }}                               │
│                                                            │
│ ┌──────┬────────────┬──────────────┬──────────────┐       │
│ │ STT  │ Mã tiểu mục│ Nội dung     │ Số tiền      │       │
│ ├──────┴────────────┴──────────────┴──────────────┤       │
│ │ {%tr for item in items %}                        │       │
│ ├──────┬────────────┬──────────────┬──────────────┤       │
│ │{{item.stt}}│{{item.ma_tieu_muc}}│{{item.noi_dung}}│{{item.so_tien}}│
│ ├──────┴────────────┴──────────────┴──────────────┤       │
│ │ {%tr endfor %}                                   │       │
│ └──────────────────────────────────────────────────┘       │
│                                                            │
│ TỔNG CỘNG: {{ tong_so_tien }} VNĐ                         │
│                                                            │
│              Người lập                                     │
│          (Ký, ghi rõ họ tên)                              │
└────────────────────────────────────────────────────────────┘
```

---

## ⚙️ LƯU Ý QUAN TRỌNG

### 1. Encoding và Format
- File Word phải ở định dạng `.docx` (không phải `.doc`)
- Sử dụng font Unicode (Arial, Times New Roman, v.v.)
- Đảm bảo tiếng Việt hiển thị chính xác

### 2. Cú pháp Jinja2
- Biến đơn: `{{ ten_bien }}`
- Vòng lặp trong bảng: `{%tr for item in items %}...{%tr endfor %}`
- Vòng lặp thông thường (ngoài bảng): `{% for item in items %}...{% endfor %}`

### 3. Format số tiền
- Số tiền đã được format tự động: `5.000.000` (dấu chấm ngăn cách hàng nghìn)
- Không cần format thêm trong Word template

### 4. Kiểm tra Template
Sau khi tạo xong template, kiểm tra:
- Tất cả các tag đều có dấu ngoặc nhọn đúng
- Vòng lặp có `{%tr for %}` và `{%tr endfor %}`
- Không có lỗi chính tả trong tên biến

---

## 🚀 SỬ DỤNG

Sau khi tạo file template:
1. Đặt file tại: `tax_payment/templates/tax_statement_template.docx`
2. Vào giao diện web, tạo bảng kê mới
3. Nhấn "Lưu và Xuất File Word"
4. File Word sẽ được tạo với dữ liệu đã điền

---

## 📞 HỖ TRỢ

Nếu có vấn đề với template, kiểm tra:
- Đường dẫn file có đúng không
- Cú pháp Jinja2 có chính xác không
- Log lỗi trong console Django

**Chúc bạn thành công!** 🎉

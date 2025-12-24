# SỬA LỖI: Vòng lặp ngang (Horizontal Loop) trong Word Template

## ❌ VẤN ĐỀ

Khi sử dụng `{% for %}...{% endfor %}` trong bảng Word, docxtpl sẽ tạo **vòng lặp ngang** (thêm cột) thay vì **vòng lặp dọc** (thêm dòng).

**Kết quả sai:**
```
| STT | Mã | Nội dung | Số tiền | STT | Mã | Nội dung | Số tiền | ...
| 1   | 1001 | Thuế TNCN | 5.000.000 | 2 | 1002 | Thuế VAT | 10.000.000 | ...
```
→ Dữ liệu chạy sang phải thay vì xuống dòng!

---

## ✅ GIẢI PHÁP

Sử dụng **{%tr for %}** thay vì **{% for %}** để tạo vòng lặp theo dòng (table row loop).

---

## 📝 HƯỚNG DẪN TỪ BƯỚC 1

### Bước 1: Tạo bảng trong Word (QUAN TRỌNG!)

**LƯU Ý:** Không được "thêm cột thủ công" sau khi tạo bảng!

1. **Insert → Table**
2. **Chọn đúng số cột ngay từ đầu:** 4 cột (STT, Mã tiểu mục, Nội dung, Số tiền)
3. **Không được:**
   - Copy/paste cột
   - Thêm cột bằng cách kéo thả
   - Merge rồi split lại

   → Tất cả đều làm vỡ cấu trúc XML!

**Cách đúng:**
```
Insert → Table → Table Grid: 4 columns x 4 rows
```

---

### Bước 2: Cấu trúc bảng chính xác

**Tạo bảng 4 cột, 4 dòng:**

| Dòng | Mục đích | Nội dung |
|------|----------|----------|
| Dòng 1 | Header | STT \| Mã tiểu mục \| Nội dung \| Số tiền (VNĐ) |
| Dòng 2 | Start loop | `{%tr for item in items %}` (merge 4 cột) |
| Dòng 3 | Template | `{{ item.stt }}` \| `{{ item.ma_tieu_muc }}` \| `{{ item.noi_dung }}` \| `{{ item.so_tien }}` |
| Dòng 4 | End loop | `{%tr endfor %}` (merge 4 cột) |

---

### Bước 3: Đặt tags chính xác

#### **Dòng 1 - Header (Format: Bold, Center)**
```
┌──────┬──────────────┬─────────────────┬────────────────┐
│ STT  │ Mã tiểu mục  │ Nội dung        │ Số tiền (VNĐ)  │
└──────┴──────────────┴─────────────────┴────────────────┘
```

#### **Dòng 2 - Bắt đầu vòng lặp**
```
┌────────────────────────────────────────────────────────┐
│ {%tr for item in items %}                              │
└────────────────────────────────────────────────────────┘
```
**Cách làm:**
- Chọn 4 ô của dòng 2
- Right-click → Merge Cells
- Gõ: `{%tr for item in items %}`

**⚠️ CHÚ Ý:** Phải gõ chính xác `{%tr` không phải `{%`!

#### **Dòng 3 - Template cho mỗi item (4 ô riêng biệt)**
```
┌──────────┬──────────────────┬─────────────────┬──────────────┐
│ {{item.stt}} │ {{item.ma_tieu_muc}} │ {{item.noi_dung}} │ {{item.so_tien}} │
└──────────┴──────────────────┴─────────────────┴──────────────┘
```
**Cách làm:**
- **KHÔNG merge** các ô
- Mỗi ô gõ 1 tag riêng:
  - Ô 1: `{{ item.stt }}`
  - Ô 2: `{{ item.ma_tieu_muc }}`
  - Ô 3: `{{ item.noi_dung }}`
  - Ô 4: `{{ item.so_tien }}`

#### **Dòng 4 - Kết thúc vòng lặp**
```
┌────────────────────────────────────────────────────────┐
│ {%tr endfor %}                                         │
└────────────────────────────────────────────────────────┘
```
**Cách làm:**
- Chọn 4 ô của dòng 4
- Right-click → Merge Cells
- Gõ: `{%tr endfor %}`

**⚠️ CHÚ Ý:** Phải gõ chính xác `{%tr` không phải `{%`!

---

### Bước 4: Hoàn thiện template

**File Word hoàn chỉnh:**

```
═══════════════════════════════════════════════════════
           BẢNG KÊ NỘP THUẾ
═══════════════════════════════════════════════════════

Người nộp thuế: {{ ten_nguoi_nop }}
Mã số thuế: {{ ma_so_thue }}
Địa chỉ: {{ dia_chi }}
Ngày lập: {{ ngay_lap }}

Kính gửi: {{ ten_co_quan_thu }}
Mã cơ quan thu: {{ ma_co_quan_thu }}
Mã địa bàn: {{ ma_dia_ban }}
Nộp tại: {{ kho_bac }}

┌──────┬──────────────┬─────────────────┬────────────────┐
│ STT  │ Mã tiểu mục  │ Nội dung        │ Số tiền (VNĐ)  │
├──────┴──────────────┴─────────────────┴────────────────┤
│ {%tr for item in items %}                              │
├──────┬──────────────┬─────────────────┬────────────────┤
│ {{item.stt}} │ {{item.ma_tieu_muc}} │ {{item.noi_dung}} │ {{item.so_tien}} │
├──────┴──────────────┴─────────────────┴────────────────┤
│ {%tr endfor %}                                         │
└────────────────────────────────────────────────────────┘

TỔNG CỘNG: {{ tong_so_tien }} VNĐ

Bằng chữ: ...................................


              Người lập
          (Ký, ghi rõ họ tên)
```

---

## 🔧 CÁCH SỬA FILE CŨ (Nếu đã tạo sai)

### Cách 1: Tạo lại bảng (Khuyến nghị)

1. **Xóa bảng cũ**
2. **Insert → Table → 4 columns x 4 rows**
3. **Làm theo Bước 2-4 ở trên**

### Cách 2: Sửa file hiện tại

1. **Mở file Word**
2. **Tìm dòng có `{% for item in items %}`**
3. **Thay thế:**
   - `{% for item in items %}` → `{%tr for item in items %}`
   - `{% endfor %}` → `{%tr endfor %}`
4. **Đảm bảo:**
   - Dòng `{%tr for %}` và `{%tr endfor %}` được merge cells
   - Dòng template (dòng 3) KHÔNG merge, mỗi tag ở 1 ô riêng

---

## ⚙️ CÚ PHÁP DOCXTPL CHO BẢNG

### 1. Vòng lặp ngang (Horizontal - KHÔNG DÙNG cho bảng dọc)
```
{% for item in items %}
    {{ item.name }}
{% endfor %}
```
→ Kết quả: `Item1 Item2 Item3` (ngang)

### 2. Vòng lặp dọc - Table Row (ĐÚNG cho bảng)
```
{%tr for item in items %}
    {{ item.name }}
{%tr endfor %}
```
→ Kết quả:
```
Item1
Item2
Item3
```

### 3. Vòng lặp cột - Table Column (KHÔNG DÙNG)
```
{%tc for item in items %}
    {{ item.name }}
{%tc endfor %}
```

---

## 🎯 SO SÁNH CÚ PHÁP

| Cú pháp | Loại vòng lặp | Kết quả | Dùng cho |
|---------|---------------|---------|----------|
| `{% for %}` | Horizontal | Ngang | Text thường |
| `{%tr for %}` | Table Row | Dọc (thêm dòng) | ✅ Bảng |
| `{%tc for %}` | Table Column | Ngang (thêm cột) | ❌ Không dùng |

---

## ✅ CHECKLIST HOÀN THÀNH

- [ ] Tạo bảng đúng số cột ngay từ đầu (4 cột)
- [ ] KHÔNG thêm/xóa/merge cột thủ công
- [ ] Dòng 1: Header (bold, center)
- [ ] Dòng 2: `{%tr for item in items %}` (merge 4 cột)
- [ ] Dòng 3: Template với 4 ô riêng biệt
- [ ] Dòng 4: `{%tr endfor %}` (merge 4 cột)
- [ ] Đã test với dữ liệu mẫu
- [ ] Kết quả xuất file Word đúng (dữ liệu xuống dòng)

---

## 🧪 TEST TEMPLATE

Sau khi tạo xong template, test ngay:

1. **Lưu file:** `tax_statement_template.docx`
2. **Đặt tại:** `tax_payment/templates/tax_statement_template.docx`
3. **Vào giao diện:** `http://localhost:8000/tax-payment/`
4. **Tạo bảng kê mẫu:**
   - Người nộp: Test User
   - Chọn địa điểm
   - Thêm 3 dòng tiểu mục
   - Xuất Word

5. **Kiểm tra file Word:**
   - Dữ liệu có xuống dòng không? ✅
   - Có 3 dòng trong bảng không? ✅
   - Format có đúng không? ✅

---

## 🆘 NẾU VẪN BỊ LỖI

### Lỗi 1: Vẫn chạy ngang
→ Kiểm tra lại đã dùng `{%tr` chưa (không phải `{%`)

### Lỗi 2: Lỗi "TemplateSyntaxError"
→ Kiểm tra đóng/mở tag đúng: `{%tr for %}` và `{%tr endfor %}`

### Lỗi 3: Bảng bị vỡ
→ Xóa bảng cũ, tạo lại từ đầu (Insert → Table)

### Lỗi 4: Merge cells không đúng
→ Dòng 2 và 4 phải merge 4 cột, Dòng 3 KHÔNG merge

---

## 📞 GỢI Ý THÊM

### Formatting nâng cao

**Căn chỉnh trong bảng:**
- STT: Center align
- Mã tiểu mục: Left align
- Nội dung: Left align
- Số tiền: Right align

**Borders:**
- Header: Border bold
- Data rows: Border normal
- Total row: Border double (dòng dưới cùng)

**Font:**
- Header: Bold, 11pt
- Data: Regular, 11pt
- Numbers: Monospace font (Consolas, Courier New)

---

**Chúc bạn thành công!** 🎉

Nếu vẫn gặp vấn đề, hãy gửi file Word cho tôi để kiểm tra cấu trúc XML.

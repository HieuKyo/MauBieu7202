# HƯỚNG DẪN SỬ DỤNG CHECKBOX/BOOLEAN TRONG MẪU BIỂU WORD

## 📋 MỤC LỤC
1. [Tổng quan 2 phương pháp](#tổng-quan)
2. [Phương pháp 1: Ký tự Unicode ☑ ☐ (Đang dùng)](#phương-pháp-1)
3. [Phương pháp 2: Content Control Checkbox (Word Developer)](#phương-pháp-2)
4. [So sánh ưu/nhược điểm](#so-sánh)
5. [Khuyến nghị](#khuyến-nghị)

---

## 📌 TỔNG QUAN 2 PHƯƠNG PHÁP {#tổng-quan}

### **Phương pháp 1: Ký tự Unicode** ⭐ (ĐANG DÙNG)
- Sử dụng ký tự: **☑** (checked) và **☐** (unchecked)
- Thay thế trực tiếp trong text như biến thường
- **Đơn giản**, không cần Developer Tab

### **Phương pháp 2: Content Control Checkbox**
- Sử dụng Word Developer Tab → Insert Checkbox
- Gắn Title/Tag cho checkbox
- Cần code đặc biệt để xử lý

---

## ✅ PHƯƠNG PHÁP 1: KÝ TỰ UNICODE (ĐANG DÙNG) {#phương-pháp-1}

### 🔹 **Nguyên lý hoạt động**

Chương trình tự động convert boolean → ký tự:
```python
def checkbox(value):
    return '☑' if value else '☐'
```

### 🔹 **Các biến checkbox có sẵn**

#### **1. Giới tính (Nam/Nữ)**

**Trong template Word:**
```
☐ Nam     ☐ Nữ
```

**Cách dùng biến Jinja2:**
```jinja
{% if gioi_tinh == "Nam" %}☑{% else %}☐{% endif %} Nam
{% if gioi_tinh == "Nữ" %}☑{% else %}☐{% endif %} Nữ
```

**Hoặc đơn giản hơn (tạo biến checkbox riêng):**
```jinja
{{ gioi_tinh_nam }} Nam     {{ gioi_tinh_nu }} Nữ
```
*Lưu ý: Cần thêm biến `gioi_tinh_nam`, `gioi_tinh_nu` vào code (xem phần Tùy chỉnh)*

---

#### **2. Nghề nghiệp**

**Template Word:**
```
☐ Nông dân          ☐ Công nhân viên chức
☐ Kinh doanh        ☐ Học sinh/Sinh viên
☐ Hưu trí           ☐ Khác: ______________
```

**Cách dùng Jinja2 (Cách 1 - Đơn giản):**
```jinja
{% if nghe_nghiep == "Nông dân" %}☑{% else %}☐{% endif %} Nông dân
{% if nghe_nghiep == "Công nhân viên chức" %}☑{% else %}☐{% endif %} Công nhân viên chức
{% if nghe_nghiep == "Kinh doanh" %}☑{% else %}☐{% endif %} Kinh doanh
{% if nghe_nghiep == "Học sinh/Sinh viên" %}☑{% else %}☐{% endif %} Học sinh/Sinh viên
{% if nghe_nghiep == "Hưu trí" %}☑{% else %}☐{% endif %} Hưu trí
{% if nghe_nghiep == "Khác" %}☑{% else %}☐{% endif %} Khác: _______________
```

**Cách 2 - Clean Code (Khuyến nghị) ⭐:**
```jinja
{# Định nghĩa danh sách nghề nghiệp chuẩn #}
{% set known_jobs = ["Nông dân", "Công nhân viên chức", "Kinh doanh", "Học sinh/Sinh viên", "Hưu trí"] %}

{% if nghe_nghiep == "Nông dân" %}☑{% else %}☐{% endif %} Nông dân
{% if nghe_nghiep == "Công nhân viên chức" %}☑{% else %}☐{% endif %} Công nhân viên chức
{% if nghe_nghiep == "Kinh doanh" %}☑{% else %}☐{% endif %} Kinh doanh
{% if nghe_nghiep == "Học sinh/Sinh viên" %}☑{% else %}☐{% endif %} Học sinh/Sinh viên
{% if nghe_nghiep == "Hưu trí" %}☑{% else %}☐{% endif %} Hưu trí

{# Kiểm tra nghề nghiệp khác #}
{% set is_other_job = nghe_nghiep not in known_jobs %}
{% if is_other_job %}☑{% else %}☐{% endif %} Khác: {{ nghe_nghiep if is_other_job else "" }}
```

**Cách 3 - Dùng Loop (Ngắn gọn nhất) 🚀:**
```jinja
{% set jobs = [
    "Nông dân",
    "Công nhân viên chức",
    "Kinh doanh",
    "Học sinh/Sinh viên",
    "Hưu trí"
] %}

{% for job in jobs %}
{% if nghe_nghiep == job %}☑{% else %}☐{% endif %} {{ job }}
{% endfor %}

{# Nghề khác #}
{% set is_other = nghe_nghiep not in jobs %}
{% if is_other %}☑{% else %}☐{% endif %} Khác: {{ nghe_nghiep if is_other else "" }}
```

💡 **Lợi ích của Cách 2 và 3:**
- ✅ Dễ bảo trì: Chỉ sửa 1 chỗ khi cần thêm/bớt nghề nghiệp
- ✅ Tránh lặp code: Không lặp lại danh sách nghề nghiệp
- ✅ Dễ đọc: Logic rõ ràng hơn

---

#### **3. Loại tài khoản**

**Biến có sẵn:**
- `tk_ngau_nhien` - Tài khoản ngẫu nhiên
- `tk_theo_yeu_cau` - Tài khoản số theo yêu cầu

**Template Word:**
```
{{ tk_ngau_nhien }} Tài khoản ngẫu nhiên
{{ tk_theo_yeu_cau }} Tài khoản số theo yêu cầu: {{ so_tai_khoan_yc }}
```

---

#### **4. Loại tiền tệ**

**Template Word:**
```jinja
{% if loai_tien_te == "VND" %}☑{% else %}☐{% endif %} VND (Việt Nam Đồng)
{% if loai_tien_te == "USD" %}☑{% else %}☐{% endif %} USD (Đô la Mỹ)
{% if loai_tien_te == "EUR" %}☑{% else %}☐{% endif %} EUR (Euro)
```

---

#### **5. Loại thẻ & Hạng thẻ**

**Biến có sẵn:**
- `the_ghi_no_noi_dia` - Thẻ Ghi nợ nội địa
- `the_hang_chuan` - Hạng chuẩn
- `the_hang_vang` - Hạng vàng

**Template Word:**
```
Loại thẻ:
{{ the_ghi_no_noi_dia }} Thẻ Ghi nợ nội địa

Hạng thẻ:
{{ the_hang_chuan }} Hạng chuẩn     {{ the_hang_vang }} Hạng vàng
```

**Hoặc dùng điều kiện:**
```jinja
{% if loai_the == "Thẻ tín dụng" %}☑{% else %}☐{% endif %} Thẻ tín dụng
{% if loai_the == "Thẻ Ghi nợ nội địa" %}☑{% else %}☐{% endif %} Thẻ Ghi nợ nội địa
{% if loai_the == "Thẻ Ghi nợ quốc tế" %}☑{% else %}☐{% endif %} Thẻ Ghi nợ quốc tế
```

---

#### **6. Dịch vụ ngân hàng điện tử**

**Biến có sẵn:**
- `dv_sms_banking` - SMS Banking
- `dv_e_mobile` - E-Mobile Banking
- `dv_bankplus` - Agribank Plus
- `dv_e_commerce` - E-Commerce
- `dv_soft_otp` - Soft OTP
- `dv_smart_otp` - Smart OTP
- `dv_retail_ebanking` - Retail E-Banking

**Template Word:**
```
ĐĂNG KÝ DỊCH VỤ NGÂN HÀNG ĐIỆN TỬ:

{{ dv_sms_banking }} SMS Banking
{{ dv_e_mobile }} E-Mobile Banking
{{ dv_bankplus }} Agribank Plus
{{ dv_e_commerce }} E-Commerce
{{ dv_soft_otp }} Soft OTP
{{ dv_smart_otp }} Smart OTP
{{ dv_retail_ebanking }} Retail E-Banking
```

---

#### **7. Dịch vụ thu hộ**

**Biến có sẵn:**
- `dv_thu_ho_tien_nuoc` - Thu hộ tiền nước
- `dv_thu_ho_tien_dien` - Thu hộ tiền điện
- `dv_thu_ho_vien_thong` - Thu hộ viễn thông
- `dv_thu_ho_hoc_phi` - Thu hộ học phí
- `dv_thu_ho_bao_hiem` - Thu hộ bảo hiểm

**Template Word:**
```
DỊCH VỤ THU HỘ:

{{ dv_thu_ho_tien_nuoc }} Tiền nước
{{ dv_thu_ho_tien_dien }} Tiền điện
{{ dv_thu_ho_vien_thong }} Viễn thông (điện thoại, internet)
{{ dv_thu_ho_hoc_phi }} Học phí
{{ dv_thu_ho_bao_hiem }} Bảo hiểm
```

---

#### **8. Phát hành thẻ**

**Biến có sẵn:**
- `phat_hanh_lan_dau` - Phát hành lần đầu
- `phat_hanh_lai` - Phát hành lại

**Template Word:**
```
{{ phat_hanh_lan_dau }} Phát hành lần đầu
{{ phat_hanh_lai }} Phát hành lại
```

---

#### **9. Kênh giao dịch**

**Biến có sẵn:**
- `kenh_mobile` - Kênh Mobile
- `kenh_internet` - Kênh Internet Banking

**Template Word:**
```
KÊNH GIAO DỊCH:

{{ kenh_mobile }} Mobile Banking
{{ kenh_internet }} Internet Banking
```

---

### 🔹 **Ưu điểm của phương pháp này**

✅ **Đơn giản**: Không cần Developer Tab, dùng như biến text thường
✅ **Tương thích tốt**: Hoạt động với mọi phiên bản Word
✅ **Dễ debug**: Nhìn trực tiếp thấy ký tự trong template
✅ **Linh hoạt**: Dễ dàng tùy chỉnh logic điều kiện
✅ **In ấn tốt**: In ra giấy hiển thị rõ ràng

---

## 🔧 PHƯƠNG PHÁP 2: CONTENT CONTROL CHECKBOX {#phương-pháp-2}

### 🔹 **Cách tạo trong Word**

1. **Bật Developer Tab:**
   - File → Options → Customize Ribbon
   - Tick vào "Developer"

2. **Insert Checkbox:**
   - Developer Tab → Controls → Check Box Content Control
   - Click để insert ☐

3. **Gán Title/Tag:**
   - Click vào checkbox → Developer Tab → Properties
   - Title: Tên hiển thị (VD: "Nam")
   - Tag: Tên biến (VD: "gioi_tinh_nam")

4. **Trong template có dạng:**
   ```xml
   <w:sdt>
     <w:sdtPr>
       <w:tag w:val="gioi_tinh_nam"/>
       <w:alias w:val="Nam"/>
     </w:sdtPr>
     <w:sdtContent>
       <w:r><w:sym w:font="Wingdings" w:char="F0A3"/></w:r>
     </w:sdtContent>
   </w:sdt>
   ```

### 🔹 **Cách xử lý trong Python**

**Cần thư viện:** `python-docx` (đã có) + code bổ sung

```python
from docx import Document
from docx.oxml import parse_xml

def set_checkbox_value(checkbox_element, is_checked):
    """Set trạng thái checkbox"""
    # Tìm <w:sym> element
    sym_element = checkbox_element.find('.//w:sym', namespaces=NSMAP)
    if sym_element is not None:
        # F0FE = checked, F0A3 = unchecked (Wingdings font)
        sym_element.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}char',
                       'F0FE' if is_checked else 'F0A3')

def render_checkboxes(doc, data):
    """Render tất cả checkboxes trong document"""
    # Tìm tất cả Content Controls
    for sdt in doc.element.findall('.//w:sdt', namespaces=NSMAP):
        # Lấy tag name
        tag_element = sdt.find('.//w:tag', namespaces=NSMAP)
        if tag_element is not None:
            tag = tag_element.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')

            # Kiểm tra tag có trong data không
            if tag in data:
                value = data[tag]
                # Set checkbox state
                set_checkbox_value(sdt, bool(value))
```

**Cập nhật vào utils.py:**
```python
class WordTemplateProcessor:
    def render(self, context):
        # ... existing code ...

        # Render checkboxes (nếu có Content Controls)
        self._render_checkboxes(context)

    def _render_checkboxes(self, context):
        """Render Content Control checkboxes"""
        NSMAP = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }

        for sdt in self.document.element.findall('.//w:sdt', namespaces=NSMAP):
            tag_element = sdt.find('.//w:tag', namespaces=NSMAP)
            if tag_element is None:
                continue

            tag = tag_element.get(f'{{{NSMAP["w"]}}}val')
            if tag not in context:
                continue

            # Tìm checkbox element
            sym_element = sdt.find('.//w:sym', namespaces=NSMAP)
            if sym_element is None:
                continue

            # Set checkbox state
            is_checked = bool(context[tag])
            char_code = 'F0FE' if is_checked else 'F0A3'  # Wingdings
            sym_element.set(f'{{{NSMAP["w"]}}}char', char_code)
```

### 🔹 **Ưu điểm**

✅ **Tương tác được**: Người dùng có thể tick/untick trong Word
✅ **Chính thống**: Cách chuẩn của Microsoft Word
✅ **Dữ liệu có cấu trúc**: Tag name rõ ràng

### 🔹 **Nhược điểm**

❌ **Phức tạp**: Cần code thêm để xử lý XML
❌ **Khó debug**: Không nhìn thấy trực tiếp trong template
❌ **Dễ hỏng**: Người dùng có thể vô tình xóa Content Control
❌ **Không tương thích Jinja2**: Không dùng được logic {% if %}
❌ **In ấn kém**: Đôi khi checkbox bị vỡ khi in PDF

---

## ⚖️ SO SÁNH ƯU/NHƯỢC ĐIỂM {#so-sánh}

| Tiêu chí | Ký tự Unicode ☑☐ | Content Control |
|----------|------------------|-----------------|
| **Độ đơn giản** | ⭐⭐⭐⭐⭐ Rất đơn giản | ⭐⭐ Phức tạp |
| **Tương thích** | ⭐⭐⭐⭐⭐ Mọi Word | ⭐⭐⭐ Word 2007+ |
| **Dễ sửa template** | ⭐⭐⭐⭐⭐ Copy/paste | ⭐⭐ Phải dùng Dev Tab |
| **Hỗ trợ Jinja2** | ⭐⭐⭐⭐⭐ Đầy đủ | ❌ Không |
| **Logic phức tạp** | ⭐⭐⭐⭐⭐ Dễ dàng | ❌ Không được |
| **In ấn/PDF** | ⭐⭐⭐⭐⭐ Rất tốt | ⭐⭐⭐ Đôi khi vỡ |
| **Tương tác** | ❌ Chỉ đọc | ⭐⭐⭐⭐⭐ Tick được |
| **Code cần thêm** | ✅ Không | ❌ Cần nhiều code |

---

## 💡 KHUYẾN NGHỊ {#khuyến-nghị}

### ⭐ **NÊN DÙNG: Ký tự Unicode (Phương pháp 1)**

**Lý do:**
1. ✅ **Đang hoạt động tốt**: Chương trình đã implement sẵn
2. ✅ **Đơn giản cho người dùng**: Không cần Developer Tab
3. ✅ **Dễ bảo trì**: Template dễ sửa, dễ debug
4. ✅ **Linh hoạt**: Kết hợp được với Jinja2 logic
5. ✅ **In ấn tốt**: Không bị vỡ khi xuất PDF

**Khi nào dùng Content Control?**
- ❌ KHÔNG nên, trừ khi có yêu cầu đặc biệt:
  - Cần người dùng tương tác với checkbox TRONG Word file
  - Cần thu thập dữ liệu từ Word form
  - Có yêu cầu từ đối tác/cấp trên phải dùng Content Control

---

## 🎯 HƯỚNG DẪN TÙY CHỈNH

### **Thêm biến checkbox mới**

**Ví dụ: Thêm checkbox cho giới tính Nam/Nữ**

**1. Cập nhật Customer.get_data_dict() (models.py):**
```python
def get_data_dict(self):
    # ... existing code ...

    # Checkbox cho giới tính
    gioi_tinh_nam = checkbox(self.gioi_tinh == 'Nam')
    gioi_tinh_nu = checkbox(self.gioi_tinh == 'Nữ')

    data = {
        # ... existing variables ...
        'gioi_tinh_nam': gioi_tinh_nam,
        'gioi_tinh_nu': gioi_tinh_nu,
    }
```

**2. Cập nhật generate_document_direct() (views.py):**
```python
# Checkbox giới tính
data['gioi_tinh_nam'] = checkbox(data['gioi_tinh'] == 'Nam')
data['gioi_tinh_nu'] = checkbox(data['gioi_tinh'] == 'Nữ')
```

**3. Sử dụng trong template Word:**
```
{{ gioi_tinh_nam }} Nam     {{ gioi_tinh_nu }} Nữ
```

---

## 📚 VÍ DỤ MẪU BIỂU HOÀN CHỈNH

### **Form đăng ký tài khoản + thẻ ATM**

```
PHẦN I: THÔNG TIN CÁ NHÂN

Họ và tên: {{ ho_ten }}
Giới tính: {{ gioi_tinh_nam }} Nam     {{ gioi_tinh_nu }} Nữ
Ngày sinh: {{ ngay_sinh }}

Nghề nghiệp:
{% set jobs = ["Nông dân", "Công nhân viên chức", "Kinh doanh", "Học sinh/Sinh viên", "Hưu trí"] %}
{% for job in jobs %}
{% if nghe_nghiep == job %}☑{% else %}☐{% endif %} {{ job }}
{% endfor %}
{% set is_other = nghe_nghiep not in jobs %}
{% if is_other %}☑{% else %}☐{% endif %} Khác: {{ nghe_nghiep if is_other else "" }}

---

PHẦN II: ĐĂNG KÝ TÀI KHOẢN

Loại tài khoản:
{{ tk_ngau_nhien }} Tài khoản ngẫu nhiên
{{ tk_theo_yeu_cau }} Tài khoản số theo yêu cầu: {{ so_tai_khoan_yc }}

Loại tiền tệ:
{% if loai_tien_te == "VND" %}☑{% else %}☐{% endif %} VND
{% if loai_tien_te == "USD" %}☑{% else %}☐{% endif %} USD

---

PHẦN III: ĐĂNG KÝ THẺ

Loại thẻ:
{{ the_ghi_no_noi_dia }} Thẻ Ghi nợ nội địa

Hạng thẻ:
{{ the_hang_chuan }} Hạng chuẩn     {{ the_hang_vang }} Hạng vàng

Phát hành:
{{ phat_hanh_lan_dau }} Lần đầu     {{ phat_hanh_lai }} Phát hành lại

---

PHẦN IV: DỊCH VỤ NGÂN HÀNG ĐIỆN TỬ

{{ dv_sms_banking }} SMS Banking
{{ dv_e_mobile }} E-Mobile Banking
{{ dv_bankplus }} Agribank Plus
{{ dv_soft_otp }} Soft OTP

---

PHẦN V: DỊCH VỤ THU HỘ

{{ dv_thu_ho_tien_nuoc }} Tiền nước
{{ dv_thu_ho_tien_dien }} Tiền điện
{{ dv_thu_ho_vien_thong }} Viễn thông
{{ dv_thu_ho_hoc_phi }} Học phí
```

---

## 🔍 TROUBLESHOOTING

### **Vấn đề 1: Checkbox không hiển thị**
**Nguyên nhân:** Font không hỗ trợ ký tự ☑ ☐
**Giải pháp:** Dùng font Times New Roman, Arial, Calibri

### **Vấn đề 2: Checkbox bị vỡ khi in**
**Nguyên nhân:** Font size quá nhỏ
**Giải pháp:** Dùng font size >= 11pt

### **Vấn đề 3: Muốn checkbox lớn hơn**
**Giải pháp:** Tăng font size của ký tự ☑ ☐ lên 14-16pt

### **Vấn đề 4: Muốn dùng ký tự khác**
**Lựa chọn khác:**
- ✓ và ○ (checkmark và circle)
- ■ và □ (filled và empty square)
- ● và ○ (filled và empty circle)

**Cập nhật trong code:**
```python
def checkbox(value):
    return '■' if value else '□'  # Hoặc ký tự khác
```

---

## 🎨 BEST PRACTICES - KỸ THUẬT VIẾT CODE JINJA2 CLEAN

### **1. Tránh lặp lại danh sách** ⭐

**❌ Không tốt:**
```jinja
{% if nghe_nghiep == "Nông dân" %}☑{% else %}☐{% endif %} Nông dân
{% if nghe_nghiep == "Công nhân viên chức" %}☑{% else %}☐{% endif %} Công nhân viên chức
{% if nghe_nghiep not in ["Nông dân", "Công nhân viên chức", ...] %}☑{% else %}☐{% endif %} Khác
```

**✅ Tốt:**
```jinja
{% set known_jobs = ["Nông dân", "Công nhân viên chức", "Kinh doanh"] %}
{% for job in known_jobs %}
{% if nghe_nghiep == job %}☑{% else %}☐{% endif %} {{ job }}
{% endfor %}
{% if nghe_nghiep not in known_jobs %}☑{% else %}☐{% endif %} Khác
```

---

### **2. Dùng biến trung gian cho logic phức tạp** ⭐

**❌ Không tốt:**
```jinja
{% if nghe_nghiep not in ["Nông dân", "Công nhân viên chức", "Kinh doanh"] %}☑{% else %}☐{% endif %} Khác: {{ nghe_nghiep if nghe_nghiep not in ["Nông dân", "Công nhân viên chức", "Kinh doanh"] else "" }}
```

**✅ Tốt:**
```jinja
{% set known_jobs = ["Nông dân", "Công nhân viên chức", "Kinh doanh"] %}
{% set is_other = nghe_nghiep not in known_jobs %}
{% if is_other %}☑{% else %}☐{% endif %} Khác: {{ nghe_nghiep if is_other else "" }}
```

---

### **3. Sử dụng comment để giải thích** ⭐

**✅ Tốt:**
```jinja
{# Định nghĩa danh sách loại tiền tệ hỗ trợ #}
{% set currencies = ["VND", "USD", "EUR", "JPY"] %}

{# Render checkbox cho từng loại tiền #}
{% for currency in currencies %}
{% if loai_tien_te == currency %}☑{% else %}☐{% endif %} {{ currency }}
{% endfor %}
```

---

### **4. Tạo macro cho code lặp lại nhiều lần** 🚀

**Nếu dùng nhiều checkbox tương tự:**

```jinja
{# Macro để tạo checkbox #}
{% macro checkbox_for_value(current_value, expected_value, label) %}
{% if current_value == expected_value %}☑{% else %}☐{% endif %} {{ label }}
{% endmacro %}

{# Sử dụng macro #}
{{ checkbox_for_value(gioi_tinh, "Nam", "Nam") }}
{{ checkbox_for_value(gioi_tinh, "Nữ", "Nữ") }}

{{ checkbox_for_value(loai_tien_te, "VND", "VND") }}
{{ checkbox_for_value(loai_tien_te, "USD", "USD") }}
```

---

### **5. Định nghĩa biến ở đầu template** ⭐

**✅ Tốt:**
```jinja
{# ==================== ĐỊNH NGHĨA BIẾN ==================== #}
{% set jobs = ["Nông dân", "Công nhân viên chức", "Kinh doanh"] %}
{% set currencies = ["VND", "USD", "EUR"] %}
{% set card_types = ["Thẻ tín dụng", "Thẻ Ghi nợ nội địa", "Thẻ Ghi nợ quốc tế"] %}

{# ==================== NỘI DUNG TEMPLATE ==================== #}
Nghề nghiệp:
{% for job in jobs %}
{% if nghe_nghiep == job %}☑{% else %}☐{% endif %} {{ job }}
{% endfor %}

Loại tiền:
{% for currency in currencies %}
{% if loai_tien_te == currency %}☑{% else %}☐{% endif %} {{ currency }}
{% endfor %}
```

---

### **6. Tách logic phức tạp thành nhiều bước** ⭐

**❌ Khó đọc:**
```jinja
{% if (nghe_nghiep != "Nông dân" and nghe_nghiep != "Công nhân viên chức" and nghe_nghiep != "Kinh doanh") %}☑{% else %}☐{% endif %}
```

**✅ Dễ đọc:**
```jinja
{% set standard_jobs = ["Nông dân", "Công nhân viên chức", "Kinh doanh"] %}
{% set is_custom_job = nghe_nghiep not in standard_jobs %}
{% if is_custom_job %}☑{% else %}☐{% endif %} Khác: {{ nghe_nghiep if is_custom_job else "" }}
```

---

### **7. Sử dụng dictionary cho mapping phức tạp** 🚀

**Ví dụ: Map nghề nghiệp sang mã số**

```jinja
{% set job_codes = {
    "Nông dân": "ND",
    "Công nhân viên chức": "CNVC",
    "Kinh doanh": "KD",
    "Học sinh/Sinh viên": "HS",
    "Hưu trí": "HT"
} %}

Nghề nghiệp:
{% for job, code in job_codes.items() %}
{% if nghe_nghiep == job %}☑{% else %}☐{% endif %} {{ job }} ({{ code }})
{% endfor %}
```

---

### **8. Format code Jinja2 đúng cách** ⭐

**✅ Tốt - Có indent và spacing:**
```jinja
{% set jobs = [
    "Nông dân",
    "Công nhân viên chức",
    "Kinh doanh"
] %}

{% for job in jobs %}
    {% if nghe_nghiep == job %}☑{% else %}☐{% endif %} {{ job }}
{% endfor %}
```

**❌ Không tốt - Khó đọc:**
```jinja
{% set jobs=["Nông dân","Công nhân viên chức","Kinh doanh"]%}{% for job in jobs%}{%if nghe_nghiep==job%}☑{%else%}☐{%endif%} {{job}}{%endfor%}
```

---

### **9. Tổng hợp: Template mẫu hoàn chỉnh** 🎯

```jinja
{# ==================== CẤU HÌNH ==================== #}
{% set jobs = ["Nông dân", "Công nhân viên chức", "Kinh doanh", "Học sinh/Sinh viên", "Hưu trí"] %}
{% set currencies = ["VND", "USD", "EUR"] %}
{% set card_ranks = {"Hạng chuẩn": "the_hang_chuan", "Hạng vàng": "the_hang_vang"} %}

{# ==================== MACRO ==================== #}
{% macro checkbox(condition) %}{% if condition %}☑{% else %}☐{% endif %}{% endmacro %}

{# ==================== NỘI DUNG ==================== #}
PHẦN I: THÔNG TIN CÁ NHÂN

Họ tên: {{ ho_ten }}
Giới tính: {{ checkbox(gioi_tinh == "Nam") }} Nam   {{ checkbox(gioi_tinh == "Nữ") }} Nữ

Nghề nghiệp:
{% for job in jobs %}
{{ checkbox(nghe_nghiep == job) }} {{ job }}
{% endfor %}
{% set is_other = nghe_nghiep not in jobs %}
{{ checkbox(is_other) }} Khác: {{ nghe_nghiep if is_other else "" }}

---

PHẦN II: TÀI KHOẢN & DỊCH VỤ

Loại tiền tệ:
{% for currency in currencies %}
{{ checkbox(loai_tien_te == currency) }} {{ currency }}
{% endfor %}

Hạng thẻ:
{% for rank, var_name in card_ranks.items() %}
{{ checkbox(hang_the == rank) }} {{ rank }}
{% endfor %}
```

---

### **💡 Lợi ích của Clean Code:**

1. **Dễ bảo trì**: Chỉ sửa 1 chỗ khi cần thay đổi
2. **Tránh lỗi**: Không lặp lại logic → ít bug
3. **Dễ đọc**: Người khác hiểu code nhanh hơn
4. **Mở rộng dễ**: Thêm option mới chỉ cần sửa list
5. **Performance tốt**: Jinja2 optimize code clean tốt hơn

---

## 🎓 VÍ DỤ THỰC TẾ HOÀN CHỈNH

### **Kịch bản: Khách hàng Nguyễn Văn A đăng ký tài khoản + thẻ ATM tại AGRIBANK Bạc Liêu**

---

### **📋 BƯỚC 1: Dữ liệu mẫu (Sample Input Data)**

```python
# Dữ liệu khách hàng nhập vào hệ thống
customer_data = {
    'ho_ten': 'NGUYỄN VĂN A',
    'gioi_tinh': 'Nam',
    'ngay_sinh': '15/03/1985',
    'cmnd': '123456789',
    'dien_thoai': '0912345678',
    'email': 'nguyenvana@gmail.com',
    'nghe_nghiep': 'Kinh doanh',
    'dia_chi': 'Số 123, Đường Trần Hưng Đạo, TP. Bạc Liêu',

    # Thông tin tài khoản
    'loai_tai_khoan': 'Tài khoản theo yêu cầu',
    'so_tai_khoan_yc': '1234567890',
    'loai_tien_te': 'VND',

    # Thông tin thẻ
    'loai_the': 'Thẻ Ghi nợ nội địa',
    'hang_the': 'Hạng vàng',
    'phat_hanh': 'Phát hành lần đầu',

    # Dịch vụ ngân hàng điện tử
    'dv_sms_banking': True,
    'dv_e_mobile': True,
    'dv_bankplus': False,
    'dv_soft_otp': True,

    # Dịch vụ thu hộ
    'dv_thu_ho_tien_dien': True,
    'dv_thu_ho_tien_nuoc': True,
    'dv_thu_ho_vien_thong': False,
}

# Biến toàn cục (GlobalConfig)
branch_data = {
    'ten_chi_nhanh': 'AGRIBANK CHI NHÁNH BẠC LIÊU',
    'dia_danh': 'Bạc Liêu',
    'dia_chi_chi_nhanh': 'Số 456, Đường Trần Phú, TP. Bạc Liêu',
    'dien_thoai_chi_nhanh': '0291.3822.079',
    'ngay_hien_tai': '06/11/2025',
}
```

---

### **📄 BƯỚC 2: Template Word (Jinja2)**

```jinja
{# ==================== CẤU HÌNH ==================== #}
{% set jobs = ["Nông dân", "Công nhân viên chức", "Kinh doanh", "Học sinh/Sinh viên", "Hưu trí"] %}
{% set currencies = ["VND", "USD", "EUR"] %}

{# ==================== MACRO ==================== #}
{% macro cb(condition) %}{% if condition %}☑{% else %}☐{% endif %}{% endmacro %}

{# ==================== NỘI DUNG ==================== #}

                    NGÂN HÀNG NÔNG NGHIỆP VÀ PHÁT TRIỂN NÔNG THÔN VIỆT NAM
                           {{ ten_chi_nhanh }}
             ------------------------------------------

                  ĐƠN ĐĂNG KÝ TÀI KHOẢN VÀ THẺ ATM

{{ dia_danh }}, ngày {{ ngay_hien_tai }}

════════════════════════════════════════════════════════════════════

PHẦN I: THÔNG TIN KHÁCH HÀNG

Họ và tên: {{ ho_ten }}                                CMND/CCCD: {{ cmnd }}
Ngày sinh: {{ ngay_sinh }}                              Giới tính: {{ cb(gioi_tinh == "Nam") }} Nam   {{ cb(gioi_tinh == "Nữ") }} Nữ

Điện thoại: {{ dien_thoai }}                            Email: {{ email }}

Địa chỉ thường trú: {{ dia_chi }}

Nghề nghiệp:
{% for job in jobs %}
  {{ cb(nghe_nghiep == job) }} {{ job }}
{% endfor %}
{% set is_other = nghe_nghiep not in jobs %}
  {{ cb(is_other) }} Khác: {{ nghe_nghiep if is_other else "_________________" }}

════════════════════════════════════════════════════════════════════

PHẦN II: ĐĂNG KÝ TÀI KHOẢN THANH TOÁN

Loại tài khoản:
  {{ cb(loai_tai_khoan == "Tài khoản ngẫu nhiên") }} Tài khoản ngẫu nhiên (do ngân hàng cấp)
  {{ cb(loai_tai_khoan == "Tài khoản theo yêu cầu") }} Tài khoản theo yêu cầu: {{ so_tai_khoan_yc if loai_tai_khoan == "Tài khoản theo yêu cầu" else "_________________" }}

Loại tiền tệ:
{% for currency in currencies %}
  {{ cb(loai_tien_te == currency) }} {{ currency }}
{% endfor %}

════════════════════════════════════════════════════════════════════

PHẦN III: ĐĂNG KÝ THẺ ATM

Loại thẻ:
  {{ cb(loai_the == "Thẻ tín dụng") }} Thẻ tín dụng
  {{ cb(loai_the == "Thẻ Ghi nợ nội địa") }} Thẻ Ghi nợ nội địa (ATM)
  {{ cb(loai_the == "Thẻ Ghi nợ quốc tế") }} Thẻ Ghi nợ quốc tế (Visa/Mastercard)

Hạng thẻ:
  {{ cb(hang_the == "Hạng chuẩn") }} Hạng chuẩn (Standard)       {{ cb(hang_the == "Hạng vàng") }} Hạng vàng (Gold)       {{ cb(hang_the == "Hạng bạch kim") }} Hạng bạch kim (Platinum)

Hình thức phát hành:
  {{ cb(phat_hanh == "Phát hành lần đầu") }} Phát hành lần đầu       {{ cb(phat_hanh == "Phát hành lại") }} Phát hành lại (do mất/hỏng)

════════════════════════════════════════════════════════════════════

PHẦN IV: ĐĂNG KÝ DỊCH VỤ NGÂN HÀNG ĐIỆN TỬ

Kính đề nghị Ngân hàng đăng ký các dịch vụ sau:

  {{ cb(dv_sms_banking) }} SMS Banking (Thông báo số dư, giao dịch qua SMS)
  {{ cb(dv_e_mobile) }} E-Mobile Banking (Ứng dụng di động)
  {{ cb(dv_bankplus) }} Agribank Plus (Thanh toán không tiếp xúc)
  {{ cb(dv_e_commerce) }} E-Commerce (Thanh toán trực tuyến)
  {{ cb(dv_soft_otp) }} Soft OTP (Mã xác thực qua ứng dụng)
  {{ cb(dv_smart_otp) }} Smart OTP (Thiết bị tạo mã)
  {{ cb(dv_retail_ebanking) }} Internet Banking (Giao dịch qua web)

════════════════════════════════════════════════════════════════════

PHẦN V: ĐĂNG KÝ DỊCH VỤ THU HỘ TỰ ĐỘNG

Tôi đồng ý cho Ngân hàng tự động trích tài khoản để thanh toán:

  {{ cb(dv_thu_ho_tien_dien) }} Tiền điện (EVN)
  {{ cb(dv_thu_ho_tien_nuoc) }} Tiền nước
  {{ cb(dv_thu_ho_vien_thong) }} Cước viễn thông (điện thoại, internet)
  {{ cb(dv_thu_ho_hoc_phi) }} Học phí
  {{ cb(dv_thu_ho_bao_hiem) }} Bảo hiểm

════════════════════════════════════════════════════════════════════

PHẦN VI: CAM KẾT

Tôi xin cam đoan các thông tin trên là đúng sự thật và chịu trách nhiệm trước pháp luật về tính chính xác của các thông tin đã cung cấp.

Tôi đã đọc, hiểu rõ và đồng ý với các điều khoản và điều kiện mở tài khoản, phát hành thẻ và sử dụng dịch vụ của AGRIBANK.


                                                    Ngày {{ ngay_hien_tai }}
                                                  Người đề nghị
                                                 (Ký và ghi rõ họ tên)




                                                  {{ ho_ten }}

════════════════════════════════════════════════════════════════════

PHẦN DÀNH CHO NGÂN HÀNG (Không điền)

Số tài khoản đã mở: _____________________     Ngày mở: ___________
Số thẻ: _____________________                 Ngày phát hành: ___________

Giao dịch viên                                Kiểm soát viên
(Ký và ghi rõ họ tên)                        (Ký và ghi rõ họ tên)


════════════════════════════════════════════════════════════════════
{{ ten_chi_nhanh }}
Địa chỉ: {{ dia_chi_chi_nhanh }}
Điện thoại: {{ dien_thoai_chi_nhanh }}
```

---

### **✅ BƯỚC 3: Kết quả sinh ra (Generated Output)**

```
                    NGÂN HÀNG NÔNG NGHIỆP VÀ PHÁT TRIỂN NÔNG THÔN VIỆT NAM
                           AGRIBANK CHI NHÁNH BẠC LIÊU
             ------------------------------------------

                  ĐƠN ĐĂNG KÝ TÀI KHOẢN VÀ THẺ ATM

Bạc Liêu, ngày 06/11/2025

════════════════════════════════════════════════════════════════════

PHẦN I: THÔNG TIN KHÁCH HÀNG

Họ và tên: NGUYỄN VĂN A                         CMND/CCCD: 123456789
Ngày sinh: 15/03/1985                            Giới tính: ☑ Nam   ☐ Nữ

Điện thoại: 0912345678                           Email: nguyenvana@gmail.com

Địa chỉ thường trú: Số 123, Đường Trần Hưng Đạo, TP. Bạc Liêu

Nghề nghiệp:
  ☐ Nông dân
  ☐ Công nhân viên chức
  ☑ Kinh doanh
  ☐ Học sinh/Sinh viên
  ☐ Hưu trí
  ☐ Khác: _________________

════════════════════════════════════════════════════════════════════

PHẦN II: ĐĂNG KÝ TÀI KHOẢN THANH TOÁN

Loại tài khoản:
  ☐ Tài khoản ngẫu nhiên (do ngân hàng cấp)
  ☑ Tài khoản theo yêu cầu: 1234567890

Loại tiền tệ:
  ☑ VND
  ☐ USD
  ☐ EUR

════════════════════════════════════════════════════════════════════

PHẦN III: ĐĂNG KÝ THẺ ATM

Loại thẻ:
  ☐ Thẻ tín dụng
  ☑ Thẻ Ghi nợ nội địa (ATM)
  ☐ Thẻ Ghi nợ quốc tế (Visa/Mastercard)

Hạng thẻ:
  ☐ Hạng chuẩn (Standard)       ☑ Hạng vàng (Gold)       ☐ Hạng bạch kim (Platinum)

Hình thức phát hành:
  ☑ Phát hành lần đầu       ☐ Phát hành lại (do mất/hỏng)

════════════════════════════════════════════════════════════════════

PHẦN IV: ĐĂNG KÝ DỊCH VỤ NGÂN HÀNG ĐIỆN TỬ

Kính đề nghị Ngân hàng đăng ký các dịch vụ sau:

  ☑ SMS Banking (Thông báo số dư, giao dịch qua SMS)
  ☑ E-Mobile Banking (Ứng dụng di động)
  ☐ Agribank Plus (Thanh toán không tiếp xúc)
  ☐ E-Commerce (Thanh toán trực tuyến)
  ☑ Soft OTP (Mã xác thực qua ứng dụng)
  ☐ Smart OTP (Thiết bị tạo mã)
  ☐ Internet Banking (Giao dịch qua web)

════════════════════════════════════════════════════════════════════

PHẦN V: ĐĂNG KÝ DỊCH VỤ THU HỘ TỰ ĐỘNG

Tôi đồng ý cho Ngân hàng tự động trích tài khoản để thanh toán:

  ☑ Tiền điện (EVN)
  ☑ Tiền nước
  ☐ Cước viễn thông (điện thoại, internet)
  ☐ Học phí
  ☐ Bảo hiểm

════════════════════════════════════════════════════════════════════

PHẦN VI: CAM KẾT

Tôi xin cam đoan các thông tin trên là đúng sự thật và chịu trách nhiệm trước pháp luật về tính chính xác của các thông tin đã cung cấp.

Tôi đã đọc, hiểu rõ và đồng ý với các điều khoản và điều kiện mở tài khoản, phát hành thẻ và sử dụng dịch vụ của AGRIBANK.


                                                    Ngày 06/11/2025
                                                  Người đề nghị
                                                 (Ký và ghi rõ họ tên)




                                                  NGUYỄN VĂN A

════════════════════════════════════════════════════════════════════

PHẦN DÀNH CHO NGÂN HÀNG (Không điền)

Số tài khoản đã mở: _____________________     Ngày mở: ___________
Số thẻ: _____________________                 Ngày phát hành: ___________

Giao dịch viên                                Kiểm soát viên
(Ký và ghi rõ họ tên)                        (Ký và ghi rõ họ tên)


════════════════════════════════════════════════════════════════════
AGRIBANK CHI NHÁNH BẠC LIÊU
Địa chỉ: Số 456, Đường Trần Phú, TP. Bạc Liêu
Điện thoại: 0291.3822.079
```

---

### **📊 PHÂN TÍCH CHI TIẾT**

#### **1. Checkbox động theo dữ liệu:**

| Trường dữ liệu | Giá trị | Checkbox nào được tích |
|----------------|---------|------------------------|
| `gioi_tinh` | "Nam" | ☑ Nam, ☐ Nữ |
| `nghe_nghiep` | "Kinh doanh" | ☑ Kinh doanh, các nghề khác ☐ |
| `loai_tai_khoan` | "Tài khoản theo yêu cầu" | ☑ Theo yêu cầu, ☐ Ngẫu nhiên |
| `loai_tien_te` | "VND" | ☑ VND, ☐ USD, ☐ EUR |
| `hang_the` | "Hạng vàng" | ☑ Vàng, ☐ Chuẩn, ☐ Bạch kim |

#### **2. Checkbox từ biến boolean:**

| Biến | Giá trị | Hiển thị |
|------|---------|----------|
| `dv_sms_banking` | `True` | ☑ SMS Banking |
| `dv_e_mobile` | `True` | ☑ E-Mobile Banking |
| `dv_bankplus` | `False` | ☐ Agribank Plus |
| `dv_thu_ho_tien_dien` | `True` | ☑ Tiền điện |
| `dv_thu_ho_vien_thong` | `False` | ☐ Cước viễn thông |

#### **3. Logic điều kiện cho "Khác":**

```jinja
{% set is_other = nghe_nghiep not in jobs %}
{{ cb(is_other) }} Khác: {{ nghe_nghiep if is_other else "_________________" }}
```

- Nếu `nghe_nghiep = "Kinh doanh"` (nằm trong danh sách) → ☐ Khác: _______
- Nếu `nghe_nghiep = "Lập trình viên"` (không trong danh sách) → ☑ Khác: Lập trình viên

---

### **💡 ĐIỂM QUAN TRỌNG**

#### **✅ Clean Code được áp dụng:**
1. **Macro `cb()`**: Rút gọn `{% if condition %}☑{% else %}☐{% endif %}` thành `{{ cb(condition) }}`
2. **Biến đầu template**: `jobs`, `currencies` định nghĩa ở đầu
3. **Biến trung gian**: `is_other` để tránh lặp logic
4. **Loop cho danh sách**: Dùng `{% for %}` thay vì lặp lại code

#### **✅ Các kỹ thuật Jinja2 sử dụng:**
- `{{ cb(gioi_tinh == "Nam") }}` - So sánh chuỗi
- `{% for job in jobs %}` - Loop qua danh sách
- `{% set is_other = ... %}` - Định nghĩa biến trung gian
- `{{ nghe_nghiep if is_other else "_____" }}` - Ternary operator
- `{% macro cb(condition) %}` - Định nghĩa macro

#### **✅ Tích hợp với hệ thống:**
- Tất cả biến đều từ `Customer.get_data_dict()` và `GlobalConfig.get_all_variables()`
- Không cần code thêm, chỉ cần tạo template Word với Jinja2
- In ra PDF → checkbox vẫn hiển thị rõ ràng

---

### **🎯 CÁCH SỬ DỤNG VÍ DỤ NÀY**

1. **Copy template Jinja2** từ Bước 2 vào file Word của bạn
2. **Upload template** lên hệ thống (menu "Mẫu biểu")
3. **Nhập dữ liệu khách hàng** vào form
4. **Tích chọn dịch vụ** mong muốn
5. **Nhấn "Tạo mẫu biểu"** → Hệ thống tự động điền checkbox
6. **Kết quả** giống như Bước 3

---

### **🔄 THAY ĐỔI DỮ LIỆU → THAY ĐỔI CHECKBOX**

**Ví dụ: Nếu thay đổi khách hàng:**

```python
# Khách hàng mới
customer_data = {
    'ho_ten': 'TRẦN THỊ B',
    'gioi_tinh': 'Nữ',  # ← Thay đổi
    'nghe_nghiep': 'Học sinh/Sinh viên',  # ← Thay đổi
    'loai_tien_te': 'USD',  # ← Thay đổi
    'hang_the': 'Hạng chuẩn',  # ← Thay đổi
    'dv_sms_banking': False,  # ← Thay đổi
    'dv_bankplus': True,  # ← Thay đổi
    # ... các trường khác ...
}
```

**Kết quả tự động thay đổi:**
- Giới tính: ☐ Nam   ☑ Nữ
- Nghề nghiệp: ☑ Học sinh/Sinh viên
- Loại tiền: ☐ VND   ☑ USD   ☐ EUR
- Hạng thẻ: ☑ Hạng chuẩn   ☐ Hạng vàng
- SMS Banking: ☐ (không tích)
- Agribank Plus: ☑ (tích)

---

## 📞 HỖ TRỢ

Nếu cần thêm biến checkbox mới, liên hệ:
- Email: support@agribank.com.vn
- Hoặc tạo ticket trong hệ thống

---

**Phiên bản:** 2.0
**Ngày cập nhật:** 06/11/2025
**Người viết:** Claude AI Assistant

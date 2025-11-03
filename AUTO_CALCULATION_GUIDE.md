# HƯỚNG DẪN SỬ DỤNG AUTO-CALCULATION (TÍNH TOÁN TỰ ĐỘNG)

## Tổng quan

Hệ thống hỗ trợ **tính toán tự động** trong template Word sử dụng cú pháp Jinja2.
Điều này cho phép bạn:
- Tính tuổi khách hàng tự động
- Kiểm tra thời hạn CCCD còn lại
- Tính phí dựa trên loại thẻ/dịch vụ
- Hiển thị nội dung có điều kiện (if/else)
- Thực hiện các phép tính số học

## Cú pháp Jinja2 cơ bản

### 1. Hiển thị biến

```jinja2
{{ ho_ten }}
{{ ngay_sinh }}
```

### 2. Điều kiện (if/else)

```jinja2
{% if tuoi >= 18 %}
  ✓ Đủ điều kiện mở tài khoản độc lập
{% else %}
  ⚠ Cần sự đồng ý của người giám hộ (dưới {{ tuoi }} tuổi)
{% endif %}
```

### 3. Gán biến (set)

```jinja2
{% set tuoi = ngay_hien_tai|date_diff_years(ngay_sinh_obj) %}
Khách hàng {{ ho_ten }} hiện {{ tuoi }} tuổi.
```

### 4. Vòng lặp (for)

```jinja2
{% for item in danh_sach %}
  - {{ item }}
{% endfor %}
```

## Biến đặc biệt cho tính toán

Hệ thống cung cấp các biến đặc biệt để hỗ trợ tính toán:

| Biến | Kiểu dữ liệu | Mô tả |
|------|--------------|-------|
| `ngay_hien_tai` | Date object | Ngày hiện tại (tự động) |
| `ngay_sinh_obj` | Date object | Ngày sinh khách hàng |
| `ngay_cap_cmnd_obj` | Date object | Ngày cấp CMND/CCCD |
| `ngay_het_han_cmnd_obj` | Date object | Ngày hết hạn CMND/CCCD |
| `ngay_in_obj` | Date object | Ngày in mẫu biểu |

**Lưu ý**: Các biến có hậu tố `_obj` là Date objects dùng cho tính toán. Các biến không có hậu tố là chuỗi đã format (ví dụ: `ngay_sinh` = "15/08/1990").

## Custom Filters (Bộ lọc tùy chỉnh)

### 1. `number_format` - Format số tiền

```jinja2
{{ 165000|number_format }} VND
→ Kết quả: 165,000 VND
```

### 2. `date_diff_years` - Tính số năm giữa 2 ngày

```jinja2
{% set tuoi = ngay_sinh_obj|date_diff_years(ngay_hien_tai) %}
→ Tính tuổi khách hàng
```

### 3. `date_diff_days` - Tính số ngày giữa 2 ngày

```jinja2
{% set ngay_con_lai = ngay_het_han_cmnd_obj|date_diff_days(ngay_hien_tai) %}
→ Tính số ngày CCCD còn hạn
```

## Ví dụ thực tế

### Ví dụ 1: Tính tuổi và kiểm tra điều kiện

```jinja2
THÔNG TIN KHÁCH HÀNG

Họ và tên: {{ ho_ten }}
Ngày sinh: {{ ngay_sinh }}

{% set tuoi = ngay_sinh_obj|date_diff_years(ngay_hien_tai) %}
Tuổi: {{ tuoi }} tuổi

ĐÁNH GIÁ ĐIỀU KIỆN:
{% if tuoi >= 18 %}
  ✓ Đủ điều kiện mở tài khoản độc lập
  ✓ Không cần giấy tờ người giám hộ
{% else %}
  ⚠ CHƯA ĐỦ 18 TUỔI ({{ tuoi }} tuổi)
  ⚠ Cần có sự đồng ý của người giám hộ
  ⚠ Cần bổ sung: Giấy tờ tùy thân của người giám hộ
{% endif %}
```

### Ví dụ 2: Kiểm tra thời hạn CCCD

```jinja2
GIẤY TỜ TÙY THÂN

Số CMND/CCCD: {{ so_cmnd }}
Ngày cấp: {{ ngay_cap_cmnd }}
Ngày hết hạn: {{ ngay_het_han_cmnd }}

{% if ngay_het_han_cmnd_obj %}
  {% set ngay_con_lai = ngay_het_han_cmnd_obj|date_diff_days(ngay_hien_tai) %}

  {% if ngay_con_lai < 0 %}
    ⚠⚠⚠ CCCD ĐÃ HẾT HẠN ({{ ngay_con_lai * -1 }} ngày trước)
    → YÊU CẦU KHÁCH HÀNG LÀM MỚI CCCD
  {% elif ngay_con_lai < 30 %}
    ⚠ CCCD SẮP HẾT HẠN (còn {{ ngay_con_lai }} ngày)
    → Khuyến nghị khách hàng làm mới CCCD
  {% elif ngay_con_lai < 90 %}
    ⓘ CCCD còn {{ ngay_con_lai }} ngày ({{ (ngay_con_lai / 30)|round(1) }} tháng)
  {% else %}
    ✓ CCCD còn hiệu lực ({{ (ngay_con_lai / 365)|round(1) }} năm)
  {% endif %}
{% endif %}
```

### Ví dụ 3: Tính phí dựa trên loại thẻ

```jinja2
PHÍ DỊCH VỤ

Loại thẻ: {{ loai_the }}
{% if loai_the == "Thẻ Visa" or loai_the == "Thẻ MasterCard" %}
  {% set phi_phat_hanh = 165000 %}
  {% set phi_thuong_nien = 82500 %}
{% elif loai_the == "Thẻ Ghi nợ nội địa" %}
  {% if hang_the == "Hạng Vàng" %}
    {% set phi_phat_hanh = 110000 %}
    {% set phi_thuong_nien = 55000 %}
  {% else %}
    {# Hạng Chuẩn #}
    {% set phi_phat_hanh = 55000 %}
    {% set phi_thuong_nien = 27500 %}
  {% endif %}
{% else %}
  {% set phi_phat_hanh = 0 %}
  {% set phi_thuong_nien = 0 %}
{% endif %}

{% if phi_phat_hanh > 0 %}
  Phí phát hành: {{ phi_phat_hanh|number_format }} VND
  Phí thường niên: {{ phi_thuong_nien|number_format }} VND
  ────────────────────────────────────────
  Tổng phí năm đầu: {{ (phi_phat_hanh + phi_thuong_nien)|number_format }} VND
{% endif %}
```

### Ví dụ 4: Tính tổng phí nhiều dịch vụ

```jinja2
BẢNG PHÍ DỊCH VỤ

{% set tong_phi = 0 %}

1. Phí phát hành thẻ:
{% if loai_the == "Thẻ Visa" %}
  {% set phi_the = 165000 %}
  - Thẻ Visa: {{ phi_the|number_format }} VND
  {% set tong_phi = tong_phi + phi_the %}
{% elif loai_the == "Thẻ Ghi nợ nội địa" %}
  {% set phi_the = 55000 %}
  - Thẻ Ghi nợ nội địa: {{ phi_the|number_format }} VND
  {% set tong_phi = tong_phi + phi_the %}
{% endif %}

2. Phí dịch vụ SMS Banking:
{% if dv_sms_banking == "☑" %}
  {% set phi_sms = 11000 %}
  - SMS Banking: {{ phi_sms|number_format }} VND/tháng
  {% set tong_phi = tong_phi + (phi_sms * 12) %}
{% endif %}

3. Phí Agribank Plus:
{% if dv_bankplus == "☑" %}
  {% set phi_ap = 0 %}
  - Agribank Plus: MIỄN PHÍ
{% endif %}

════════════════════════════════════════
TỔNG PHÍ NĂM ĐẦU: {{ tong_phi|number_format }} VND
════════════════════════════════════════
```

### Ví dụ 5: Danh sách dịch vụ đã chọn

```jinja2
CÁC DỊCH VỤ ĐĂNG KÝ:

{% set danh_sach_dv = [] %}
{% if dv_sms_banking == "☑" %}{% set danh_sach_dv = danh_sach_dv + ["SMS Banking"] %}{% endif %}
{% if dv_bankplus == "☑" %}{% set danh_sach_dv = danh_sach_dv + ["Agribank Plus"] %}{% endif %}
{% if dv_e_mobile == "☑" %}{% set danh_sach_dv = danh_sach_dv + ["E-Mobile Banking"] %}{% endif %}

{% if danh_sach_dv|length > 0 %}
  Khách hàng đã đăng ký {{ danh_sach_dv|length }} dịch vụ:
  {% for dv in danh_sach_dv %}
  {{ loop.index }}. {{ dv }}
  {% endfor %}
{% else %}
  Khách hàng chưa đăng ký dịch vụ nào.
{% endif %}
```

## Toán tử và Biểu thức

### Toán tử số học

```jinja2
{% set tong = 100 + 200 %}          {# Cộng: 300 #}
{% set hieu = 500 - 100 %}          {# Trừ: 400 #}
{% set tich = 50 * 3 %}             {# Nhân: 150 #}
{% set thuong = 100 / 4 %}          {# Chia: 25 #}
{% set du = 100 % 3 %}              {# Chia lấy dư: 1 #}
```

### Toán tử so sánh

```jinja2
{% if tuoi >= 18 %}                 {# Lớn hơn hoặc bằng #}
{% if phi < 100000 %}               {# Nhỏ hơn #}
{% if loai_the == "Thẻ Visa" %}    {# Bằng #}
{% if hang_the != "Hạng Vàng" %}   {# Khác #}
```

### Toán tử logic

```jinja2
{% if tuoi >= 18 and ngay_con_lai > 30 %}     {# AND #}
{% if loai_the == "Visa" or loai_the == "MasterCard" %}  {# OR #}
{% if not (tuoi < 18) %}                       {# NOT #}
```

## Các hàm hữu ích

### `round()` - Làm tròn số

```jinja2
{% set so_thang = ngay_con_lai / 30 %}
Còn {{ so_thang|round(1) }} tháng
→ Kết quả: Còn 2.3 tháng
```

### `abs()` - Giá trị tuyệt đối

```jinja2
{% set ngay_qua_han = abs(ngay_con_lai) %}
```

### `length` - Độ dài danh sách/chuỗi

```jinja2
{% if danh_sach|length > 0 %}
  Có {{ danh_sach|length }} items
{% endif %}
```

## Ghi chú và Comment

```jinja2
{# Đây là comment, sẽ không hiển thị trong output #}

{#
  Comment nhiều dòng
  Dùng để ghi chú
#}
```

## Lưu ý khi sử dụng

### 1. **Kiểm tra giá trị trước khi tính toán**

```jinja2
{# TỐT ✓ #}
{% if ngay_sinh_obj %}
  {% set tuoi = ngay_sinh_obj|date_diff_years(ngay_hien_tai) %}
{% endif %}

{# KHÔNG TỐT ✗ - Có thể lỗi nếu ngay_sinh_obj = None #}
{% set tuoi = ngay_sinh_obj|date_diff_years(ngay_hien_tai) %}
```

### 2. **Formatting trong Word**

- Jinja2 syntax có thể làm mất một phần formatting của Word
- Khuyến nghị: Áp dụng formatting SAU khi đã test template
- Nếu cần giữ formatting phức tạp, sử dụng nhiều text boxes riêng biệt

### 3. **Debug template**

Nếu template không render đúng:
1. Kiểm tra syntax Jinja2 (đóng/mở tag đúng)
2. Check console log trong terminal khi chạy server
3. Sử dụng comment để tạm tắt từng phần và tìm lỗi

```jinja2
{# Tạm tắt phần này để test
{% set tuoi = ngay_sinh_obj|date_diff_years(ngay_hien_tai) %}
#}
```

### 4. **Test với dữ liệu thật**

- Luôn test template với nhiều trường hợp khác nhau
- Test với dữ liệu thiếu (null/empty)
- Test với edge cases (tuổi = 18, CCCD sắp hết hạn, v.v.)

## Ví dụ Template hoàn chỉnh

```jinja2
═══════════════════════════════════════════════════════
          PHIẾU ĐĂNG KÝ MỞ TẦI KHOẢN VÀ PHÁT HÀNH THẺ
═══════════════════════════════════════════════════════

THÔNG TIN KHÁCH HÀNG

Họ và tên: {{ ho_ten }}
Ngày sinh: {{ ngay_sinh }}
{% if ngay_sinh_obj %}
  {% set tuoi = ngay_sinh_obj|date_diff_years(ngay_hien_tai) %}
  Tuổi: {{ tuoi }} tuổi
{% endif %}

Số CMND/CCCD: {{ so_cmnd }}
Ngày cấp: {{ ngay_cap_cmnd }}
Ngày hết hạn: {{ ngay_het_han_cmnd }}

{% if ngay_het_han_cmnd_obj %}
  {% set ngay_con_lai = ngay_het_han_cmnd_obj|date_diff_days(ngay_hien_tai) %}
  {% if ngay_con_lai < 0 %}
    ⚠ CCCD ĐÃ HẾT HẠN - YÊU CẦU LÀM MỚI
  {% elif ngay_con_lai < 30 %}
    ⚠ CCCD sắp hết hạn (còn {{ ngay_con_lai }} ngày)
  {% endif %}
{% endif %}

───────────────────────────────────────────────────────

DỊCH VỤ ĐĂNG KÝ VÀ PHÍ

Loại thẻ: {{ loai_the }} - {{ hang_the }}

{% if loai_the == "Thẻ Ghi nợ nội địa" and hang_the == "Hạng Vàng" %}
  {% set phi_phat_hanh = 110000 %}
  {% set phi_thuong_nien = 55000 %}
{% elif loai_the == "Thẻ Ghi nợ nội địa" %}
  {% set phi_phat_hanh = 55000 %}
  {% set phi_thuong_nien = 27500 %}
{% else %}
  {% set phi_phat_hanh = 0 %}
  {% set phi_thuong_nien = 0 %}
{% endif %}

{% if phi_phat_hanh > 0 %}
Phí phát hành: {{ phi_phat_hanh|number_format }} VND
Phí thường niên: {{ phi_thuong_nien|number_format }} VND
Tổng phí năm đầu: {{ (phi_phat_hanh + phi_thuong_nien)|number_format }} VND
{% endif %}

───────────────────────────────────────────────────────

XÁC NHẬN ĐIỀU KIỆN

{% if ngay_sinh_obj %}
  {% set tuoi = ngay_sinh_obj|date_diff_years(ngay_hien_tai) %}
  {% if tuoi >= 18 %}
    ✓ Khách hàng đủ điều kiện mở tài khoản độc lập
  {% else %}
    ⚠ Khách hàng chưa đủ 18 tuổi
    ⚠ Cần bổ sung giấy tờ người giám hộ
  {% endif %}
{% endif %}

{% if ngay_het_han_cmnd_obj %}
  {% set ngay_con_lai = ngay_het_han_cmnd_obj|date_diff_days(ngay_hien_tai) %}
  {% if ngay_con_lai >= 30 %}
    ✓ CCCD còn hiệu lực
  {% endif %}
{% endif %}

═══════════════════════════════════════════════════════
```

## Hỗ trợ

Nếu cần hỗ trợ thêm về auto-calculation:
1. Xem thêm Variable Library trong hệ thống
2. Tham khảo Jinja2 documentation: https://jinja.palletsprojects.com/
3. Liên hệ quản trị viên hệ thống

---

**Phiên bản:** 1.0
**Ngày cập nhật:** 2025-11-03
**Ngân hàng Agribank - Chi nhánh Giá Rai Bạc Liêu**

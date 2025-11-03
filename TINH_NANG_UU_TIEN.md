# CÁC TÍNH NĂNG ƯU TIÊN NÂNG CẤP

> **Ngày tạo:** 03/11/2025
> **Trạng thái:** Đang lên kế hoạch

---

## 1. AUTO-CALCULATION (Tính toán tự động trong template)

### Mục đích:
Tự động tính toán các giá trị dựa trên dữ liệu khách hàng trong template Word

### Cú pháp Jinja2:
```jinja2
{% set tuoi = (ngay_hien_tai - ngay_sinh).years %}
{% if tuoi < 15 %}
  Cần có sự đồng ý của người giám hộ
{% endif %}
```

### Các trường hợp sử dụng:

#### A. Tính tuổi
```jinja2
{% set tuoi = (ngay_hien_tai - ngay_sinh).years %}

Khách hàng: {{ ho_ten }}
Tuổi: {{ tuoi }} tuổi

{% if tuoi >= 18 %}
  ✓ Đủ điều kiện mở tài khoản độc lập
{% else %}
  ⚠ Cần sự đồng ý của người giám hộ (dưới 18 tuổi)
{% endif %}
```

#### B. Tính thời hạn CCCD còn lại
```jinja2
{% set ngay_con_lai = (ngay_het_han_cmnd - ngay_hien_tai).days %}

{% if ngay_con_lai < 30 %}
  ⚠ CCCD sắp hết hạn (còn {{ ngay_con_lai }} ngày)
  → Yêu cầu khách hàng làm mới CCCD
{% endif %}
```

#### C. Điều kiện phát hành thẻ theo độ tuổi
```jinja2
{% set tuoi = (ngay_hien_tai - ngay_sinh).years %}

{% if tuoi < 15 %}
  Loại thẻ phù hợp: Thẻ Junior (15 tuổi trở xuống)
  Hạn mức: 5,000,000 VND/tháng
  Yêu cầu: Cha/mẹ đồng ký
{% elif tuoi >= 15 and tuoi < 18 %}
  Loại thẻ phù hợp: Thẻ Teen
  Hạn mức: 10,000,000 VND/tháng
  Yêu cầu: Người giám hộ đồng ý
{% else %}
  Loại thẻ phù hợp: Thẻ Standard/Gold/Platinum
  Hạn mức: Theo quy định
{% endif %}
```

#### D. Tính phí dựa trên loại thẻ
```jinja2
{% if loai_the == "Thẻ Visa" %}
  {% set phi_phat_hanh = 50000 %}
  {% set phi_thuong_nien = 300000 %}
{% elif loai_the == "Thẻ MasterCard" %}
  {% set phi_phat_hanh = 55000 %}
  {% set phi_thuong_nien = 350000 %}
{% else %}
  {% set phi_phat_hanh = 30000 %}
  {% set phi_thuong_nien = 200000 %}
{% endif %}

Phí phát hành: {{ phi_phat_hanh | number_format }} VND
Phí thường niên: {{ phi_thuong_nien | number_format }} VND
```

### Kỹ thuật triển khai:

**Backend (views.py):**
```python
from datetime import date
from jinja2 import Environment

def render_template_with_logic(template_content, customer_data):
    # Thêm ngày hiện tại
    customer_data['ngay_hien_tai'] = date.today()

    # Custom filters
    def number_format(value):
        return f"{value:,}".replace(',', '.')

    env = Environment()
    env.filters['number_format'] = number_format

    template = env.from_string(template_content)
    return template.render(**customer_data)
```

**Biến tự động có sẵn:**
- `ngay_hien_tai`: Ngày hôm nay
- `nam_hien_tai`: Năm hiện tại
- `thang_hien_tai`: Tháng hiện tại

---

## 2. PREVIEW MẪU BIỂU (Xem trước file Word)

### Mục đích:
Cho phép người dùng xem trước nội dung mẫu biểu trước khi download, tránh tải file rồi mới phát hiện lỗi

### Tính năng:

#### A. Convert DOCX → HTML
- Hiển thị file Word dạng HTML ngay trên trình duyệt
- Highlight các biến đã được điền (màu xanh lá)
- Hiển thị các biến chưa điền (màu đỏ, warning)

#### B. PDF Preview
- Convert DOCX → PDF tạm thời
- Dùng PDF.js để hiển thị trong iframe

#### C. Quick Edit
- Nút "Edit" ngay trên màn hình preview
- Click → Quay lại form để sửa
- Form giữ nguyên dữ liệu đã nhập

### Giao diện:

```
┌─────────────────────────────────────────────────┐
│  📄 Preview: Giấy đề nghị phát hành thẻ         │
│  ────────────────────────────────────────────   │
│                                                  │
│  Kính gửi: Agribank Chi nhánh Giá Rai           │
│                                                  │
│  Tôi tên là: [Nguyễn Văn A] ✓                   │
│  Số CMND: [001234567890] ✓                      │
│  Ngày sinh: [01/01/1990] ✓                      │
│  Tuổi: [35 tuổi] (tự động tính)                 │
│                                                  │
│  ⚠ Biến chưa điền: noi_lam_viec                 │
│                                                  │
│  [✏️ Sửa lại]  [⬇️ Download Word]  [✖️ Đóng]     │
└─────────────────────────────────────────────────┘
```

### Kỹ thuật triển khai:

**Option 1: Mammoth.js (Client-side)**
```javascript
// Đọc file .docx và convert sang HTML
mammoth.convertToHtml({arrayBuffer: arrayBuf})
    .then(function(result) {
        var html = result.value; // HTML content
        document.getElementById("preview").innerHTML = html;
        highlightVariables(); // Highlight biến đã điền
    })
    .catch(function(err) {
        console.log(err);
    });
```

**Option 2: python-docx + python-docx2html (Server-side)**
```python
from docx import Document
from docx2html import convert

def preview_document(template_path, filled_data):
    doc = Document(template_path)

    # Render với Jinja2
    rendered_doc = render_template(doc, filled_data)

    # Convert to HTML
    html = convert(rendered_doc)

    # Highlight biến
    html = highlight_filled_variables(html, filled_data.keys())

    return html
```

**Option 3: LibreOffice Headless (Best quality)**
```python
import subprocess

def docx_to_pdf(docx_path, pdf_path):
    subprocess.run([
        'libreoffice',
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', os.path.dirname(pdf_path),
        docx_path
    ])
```

### API Endpoint:

**URL:** `/api/templates/<id>/preview/`

**Request:**
```json
{
    "ho_ten": "Nguyễn Văn A",
    "so_cmnd": "001234567890",
    "ngay_sinh": "1990-01-01"
}
```

**Response:**
```json
{
    "status": "success",
    "preview_html": "<div>...</div>",
    "unfilled_variables": ["noi_lam_viec", "email"],
    "filled_count": 15,
    "total_count": 17
}
```

### Validation trước khi download:
```javascript
// Kiểm tra trước khi cho download
if (unfilledVariables.length > 0) {
    showWarning(`Còn ${unfilledVariables.length} trường chưa điền:\n`
                + unfilledVariables.join(', '));
    // Vẫn cho download nhưng có cảnh báo
}
```

---

## 3. BATCH PROCESSING (Xử lý hàng loạt)

### Mục đích:
Tạo nhiều mẫu biểu cùng lúc cho nhiều khách hàng, giảm thời gian xử lý từ hàng giờ xuống còn vài phút

### Use Case:

**Tình huống:** Ngân hàng tổ chức sự kiện "Ngày hội mở thẻ" tại trường học, có 100 học sinh đăng ký cùng lúc.

**Cách làm cũ (thủ công):**
1. Nhập thông tin từng học sinh (5 phút/người)
2. Tạo mẫu biểu cho từng người
3. Download từng file
→ **Tổng thời gian: 100 × 5 phút = 500 phút (8+ giờ)**

**Cách làm mới (batch):**
1. Download template Excel
2. Điền thông tin 100 học sinh vào Excel (30 phút)
3. Upload file Excel
4. Chọn mẫu biểu cần tạo
5. Click "Tạo hàng loạt"
6. Hệ thống xử lý (5 phút)
7. Download file ZIP chứa 100 file Word
→ **Tổng thời gian: 40 phút**

### Workflow:

```
┌──────────────────────────────────────────────────┐
│  BƯỚC 1: Download Template Excel                 │
├──────────────────────────────────────────────────┤
│  [⬇️ Tải template mẫu]                           │
│                                                   │
│  File: template_import_khach_hang.xlsx            │
│  Cột: ho_ten | so_cmnd | ngay_sinh | ...         │
└──────────────────────────────────────────────────┘

        ↓

┌──────────────────────────────────────────────────┐
│  BƯỚC 2: Điền thông tin vào Excel                │
├──────────────────────────────────────────────────┤
│  A          B            C           D            │
│  ho_ten     so_cmnd      ngay_sinh  dia_chi      │
│  Nguyễn A   001***890    01/01/1990 Bạc Liêu    │
│  Trần B     002***891    02/02/1991 Cà Mau      │
│  ...        ...          ...        ...          │
└──────────────────────────────────────────────────┘

        ↓

┌──────────────────────────────────────────────────┐
│  BƯỚC 3: Upload & Preview                        │
├──────────────────────────────────────────────────┤
│  📂 Upload file Excel:                           │
│  [Chọn file...]  danh_sach_100_hoc_sinh.xlsx ✓   │
│                                                   │
│  ✓ Đã đọc được 100 dòng                          │
│  ✓ Tất cả dữ liệu hợp lệ                         │
│                                                   │
│  Preview 5 dòng đầu:                             │
│  1. Nguyễn Văn A - 001***890 ✓                   │
│  2. Trần Thị B - 002***891 ✓                     │
│  3. Lê Văn C - 003***892 ✓                       │
│  ...                                              │
│                                                   │
│  [← Quay lại]  [Tiếp tục →]                      │
└──────────────────────────────────────────────────┘

        ↓

┌──────────────────────────────────────────────────┐
│  BƯỚC 4: Chọn mẫu biểu                           │
├──────────────────────────────────────────────────┤
│  Mẫu biểu: [Giấy đề nghị phát hành thẻ ▼]       │
│                                                   │
│  Tùy chọn:                                        │
│  ☑ Lưu khách hàng vào database                   │
│  ☑ Tự động đặt tên file theo: ho_ten_so_cmnd     │
│  ☐ Gửi email cho từng khách hàng                 │
│                                                   │
│  [← Quay lại]  [🚀 Bắt đầu tạo]                  │
└──────────────────────────────────────────────────┘

        ↓

┌──────────────────────────────────────────────────┐
│  BƯỚC 5: Đang xử lý...                           │
├──────────────────────────────────────────────────┤
│  [████████████████░░░░] 80% (80/100)             │
│                                                   │
│  ✓ Đã tạo: 80 file                               │
│  ⏳ Đang xử lý: Nguyễn Văn T                      │
│  ❌ Lỗi: 2 file (xem chi tiết)                   │
│                                                   │
│  Thời gian còn lại: ~1 phút                      │
└──────────────────────────────────────────────────┘

        ↓

┌──────────────────────────────────────────────────┐
│  BƯỚC 6: Hoàn thành! ✓                           │
├──────────────────────────────────────────────────┤
│  ✅ Đã tạo thành công: 98 file                   │
│  ❌ Lỗi: 2 file                                  │
│                                                   │
│  Lỗi chi tiết:                                    │
│  - Dòng 45: Thiếu số CMND                        │
│  - Dòng 67: Ngày sinh không hợp lệ               │
│                                                   │
│  [⬇️ Download ZIP (98 files, 4.5MB)]            │
│  [📄 Download báo cáo lỗi (Excel)]               │
│  [🔄 Tạo lại]                                     │
└──────────────────────────────────────────────────┘
```

### Template Excel mẫu:

**File:** `template_import_khach_hang.xlsx`

| ho_ten | so_cmnd | ngay_sinh | gioi_tinh | dia_chi | so_dien_thoai | email | nghe_nghiep | loai_the | hang_the |
|--------|---------|-----------|-----------|---------|---------------|-------|-------------|----------|----------|
| Nguyễn Văn A | 001234567890 | 01/01/1990 | Nam | Bạc Liêu | 0901234567 | a@gmail.com | Học sinh | Thẻ Visa | Classic |
| Trần Thị B | 002345678901 | 02/02/1991 | Nữ | Cà Mau | 0902345678 | b@gmail.com | Học sinh | Thẻ Visa | Classic |

**Sheet 2: Hướng dẫn**
```
HƯỚNG DẪN SỬ DỤNG:

1. ĐỊNH DẠNG CỘT:
   - ho_ten: Văn bản (tối đa 200 ký tự)
   - so_cmnd: Văn bản (9 hoặc 12 số)
   - ngay_sinh: Ngày tháng (DD/MM/YYYY)
   - gioi_tinh: Nam / Nữ / Khác
   - so_dien_thoai: Văn bản (10 số, bắt đầu bằng 0)
   - email: Email hợp lệ

2. CÁC CỘT BẮT BUỘC (có dấu *):
   - ho_ten *
   - so_cmnd *

3. GHI CHÚ:
   - Không xóa dòng tiêu đề (dòng 1)
   - Tối đa 1000 dòng mỗi lần import
   - File Excel phải có định dạng .xlsx hoặc .xls
```

### Kỹ thuật triển khai:

**Backend: Django + Celery**

```python
# views.py
from celery import shared_task
import openpyxl
import zipfile

@shared_task(bind=True)
def batch_create_documents(self, excel_file_path, template_id, options):
    """
    Background task để tạo nhiều mẫu biểu
    """
    workbook = openpyxl.load_workbook(excel_file_path)
    sheet = workbook.active

    total_rows = sheet.max_row - 1  # Trừ header
    success_count = 0
    error_list = []
    created_files = []

    # Đọc header
    headers = [cell.value for cell in sheet[1]]

    # Xử lý từng dòng
    for idx, row in enumerate(sheet.iter_rows(min_row=2), start=2):
        try:
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': idx - 1,
                    'total': total_rows,
                    'status': f'Đang xử lý: {row[0].value}'
                }
            )

            # Parse dữ liệu
            customer_data = {}
            for col_idx, header in enumerate(headers):
                customer_data[header] = row[col_idx].value

            # Validate
            errors = validate_customer_data(customer_data)
            if errors:
                error_list.append({
                    'row': idx,
                    'errors': errors,
                    'data': customer_data
                })
                continue

            # Lưu khách hàng (nếu chọn)
            if options.get('save_to_db'):
                customer = Customer.objects.create(**customer_data)

            # Tạo file Word
            doc_path = create_document(template_id, customer_data)
            created_files.append(doc_path)
            success_count += 1

        except Exception as e:
            error_list.append({
                'row': idx,
                'errors': [str(e)],
                'data': dict(zip(headers, [c.value for c in row]))
            })

    # Tạo file ZIP
    zip_path = create_zip_file(created_files)

    # Tạo báo cáo lỗi
    error_report_path = create_error_report(error_list)

    return {
        'status': 'completed',
        'success_count': success_count,
        'error_count': len(error_list),
        'zip_path': zip_path,
        'error_report_path': error_report_path
    }

def create_zip_file(file_paths):
    """Tạo file ZIP chứa tất cả file Word"""
    zip_filename = f'batch_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    zip_path = os.path.join(settings.MEDIA_ROOT, 'batch', zip_filename)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            # Đặt tên file trong ZIP
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname)

    return zip_path

def create_error_report(error_list):
    """Tạo file Excel báo cáo lỗi"""
    if not error_list:
        return None

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Lỗi"

    # Header
    ws.append(['Dòng', 'Lỗi', 'Dữ liệu'])

    # Dữ liệu lỗi
    for error in error_list:
        ws.append([
            error['row'],
            ', '.join(error['errors']),
            str(error['data'])
        ])

    error_filename = f'errors_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    error_path = os.path.join(settings.MEDIA_ROOT, 'batch', error_filename)
    wb.save(error_path)

    return error_path
```

**Frontend: JavaScript + WebSocket (Real-time progress)**

```javascript
// batch_processing.js

function startBatchProcessing() {
    const formData = new FormData();
    formData.append('excel_file', fileInput.files[0]);
    formData.append('template_id', selectedTemplateId);
    formData.append('options', JSON.stringify(options));

    fetch('/api/batch/create/', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        const taskId = data.task_id;

        // Poll progress
        checkProgress(taskId);
    });
}

function checkProgress(taskId) {
    const interval = setInterval(() => {
        fetch(`/api/batch/status/${taskId}/`)
            .then(res => res.json())
            .then(data => {
                if (data.state === 'PROGRESS') {
                    // Update progress bar
                    const percent = (data.current / data.total) * 100;
                    updateProgressBar(percent, data.status);
                } else if (data.state === 'SUCCESS') {
                    clearInterval(interval);
                    showCompleteDialog(data.result);
                } else if (data.state === 'FAILURE') {
                    clearInterval(interval);
                    showError(data.error);
                }
            });
    }, 1000); // Check every 1 second
}

function showCompleteDialog(result) {
    const html = `
        <div class="alert alert-success">
            <h4>✅ Hoàn thành!</h4>
            <p>Đã tạo thành công: <strong>${result.success_count}</strong> file</p>
            ${result.error_count > 0 ? `<p class="text-warning">Lỗi: ${result.error_count} file</p>` : ''}
        </div>

        <a href="${result.zip_path}" class="btn btn-success">
            ⬇️ Download ZIP (${result.success_count} files)
        </a>

        ${result.error_report_path ? `
            <a href="${result.error_report_path}" class="btn btn-warning">
                📄 Download báo cáo lỗi
            </a>
        ` : ''}
    `;

    document.getElementById('result-container').innerHTML = html;
}
```

**URLs:**

```python
# urls.py
urlpatterns = [
    # Download template
    path('api/batch/template/download/', views.download_batch_template, name='batch_template'),

    # Upload & Start batch
    path('api/batch/create/', views.batch_create_start, name='batch_create'),

    # Check progress
    path('api/batch/status/<task_id>/', views.batch_status, name='batch_status'),

    # Download result
    path('api/batch/download/<filename>/', views.batch_download, name='batch_download'),
]
```

### Validation & Error Handling:

**Các loại lỗi phổ biến:**

1. **Lỗi định dạng:**
   - Số CMND không đúng (không phải 9 hoặc 12 số)
   - Số điện thoại không đúng (không phải 10 số)
   - Email không hợp lệ
   - Ngày sinh không hợp lệ (format hoặc giá trị)

2. **Lỗi dữ liệu:**
   - Thiếu trường bắt buộc (ho_ten, so_cmnd)
   - CMND bị trùng
   - Tuổi không hợp lệ (< 0 hoặc > 150)

3. **Lỗi hệ thống:**
   - File Excel bị lỗi
   - Template không tồn tại
   - Hết dung lượng lưu trữ

**Chiến lược xử lý:**
- **Soft fail:** Bỏ qua dòng lỗi, tiếp tục xử lý
- **Ghi log:** Lưu tất cả lỗi vào file Excel
- **Notification:** Thông báo cho user sau khi hoàn thành

### Giới hạn & Bảo mật:

```python
# settings.py
BATCH_PROCESSING = {
    'MAX_ROWS_PER_BATCH': 1000,  # Tối đa 1000 dòng
    'MAX_FILE_SIZE': 10 * 1024 * 1024,  # 10MB
    'ALLOWED_EXTENSIONS': ['.xlsx', '.xls'],
    'TIMEOUT': 600,  # 10 phút
}
```

**Quyền hạn:**
- Chỉ user có quyền `batch_create_documents`
- Admin có thể xem lịch sử batch của tất cả user
- User thường chỉ thấy batch của mình

---

## 📋 KẾ HOẠCH TRIỂN KHAI

### Ưu tiên:
1. **Auto-calculation** - Dễ nhất, ảnh hưởng lớn (1-2 ngày)
2. **Preview** - Trung bình, cải thiện UX (3-5 ngày)
3. **Batch Processing** - Khó nhất, cần Celery setup (1-2 tuần)

### Dependencies:
```bash
# Auto-calculation: Không cần thêm thư viện (dùng Jinja2 có sẵn)

# Preview:
pip install mammoth  # DOCX to HTML
pip install pdf2image  # PDF preview
pip install python-docx2html

# Batch Processing:
pip install celery==5.3.4
pip install redis==5.0.1
pip install openpyxl==3.1.2
```

### Môi trường cần thiết:
- **Redis Server** (cho Celery): Cài đặt trên Windows/Linux
- **LibreOffice** (tùy chọn, cho PDF preview chất lượng cao)

---

**Ngày cập nhật:** 03/11/2025
**Người đề xuất:** Hệ thống
**Trạng thái:** Chờ phê duyệt

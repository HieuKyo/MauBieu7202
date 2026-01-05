# Quick Start Guide - KPI Dashboard

## 🚀 Bắt đầu nhanh

### Bước 1: Cài đặt dependencies

```bash
pip install -r ../requirements.txt
```

### Bước 2: Tạo dữ liệu mẫu (tùy chọn)

Nếu bạn muốn test với dữ liệu mẫu:

```bash
python generate_sample_data.py
```

Các file mẫu sẽ được tạo trong thư mục `sample_data/`:
- `sample_kpi_template_01_2024.xlsx` - File KPI mẫu
- `sample_card_data_01_2024.xlsx` - Dữ liệu thẻ
- `sample_sms_data_01_2024.xlsx` - Dữ liệu SMS
- `sample_emobile_data_01_2024.xlsx` - Dữ liệu E-Mobile

### Bước 3: Chạy ứng dụng

#### Trên Linux/Mac:

```bash
streamlit run app.py
```

#### Trên Windows:

```cmd
streamlit run app.py
```

hoặc sử dụng script:

```cmd
run_kpi_dashboard.bat
```

### Bước 4: Sử dụng ứng dụng

1. Mở trình duyệt tại `http://localhost:8501`
2. Chọn tháng/năm và mã GDV tại sidebar
3. Upload các file dữ liệu:
   - File KPI Mẫu (bắt buộc)
   - File dữ liệu Thẻ, SMS, E-Mobile (tùy chọn)
4. Nhấn "Phân tích & Xuất Báo cáo"
5. Tải xuống file báo cáo KPI

## 📝 Lưu ý

- Port mặc định: **8501** (có thể thay đổi bằng cách thêm `--server.port=XXXX`)
- Ứng dụng tự động reload khi có thay đổi code (development mode)
- File output sẽ có tên dạng: `KPI_[USERID]_[MONTH]_[YEAR].xlsx`

## 🔧 Cấu hình nâng cao

### Thay đổi port

```bash
streamlit run app.py --server.port=8502
```

### Chạy ở production mode

```bash
streamlit run app.py --server.headless=true
```

### Cấu hình trong file config

Tạo file `.streamlit/config.toml`:

```toml
[server]
port = 8501
headless = true

[theme]
primaryColor = "#366092"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

## ❓ Troubleshooting

### Lỗi: Module not found

```bash
pip install -r ../requirements.txt --upgrade
```

### Lỗi: Port đã được sử dụng

```bash
streamlit run app.py --server.port=8502
```

### Lỗi: Không tìm thấy file

Đảm bảo bạn đang ở đúng thư mục:

```bash
cd kpi_dashboard
pwd  # Kiểm tra đường dẫn hiện tại
```

## 📞 Liên hệ

Nếu gặp vấn đề, vui lòng kiểm tra file `README.md` để biết thêm chi tiết.

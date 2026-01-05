# Tích hợp KPI Dashboard vào Hệ thống

## Tổng quan

KPI Dashboard đã được tích hợp vào hệ thống mẫu biểu Agribank thông qua menu **Tiện ích**.

## Cách truy cập

Người dùng có thể truy cập KPI Dashboard theo hai cách:

### 1. Từ giao diện web chính

1. Đăng nhập vào hệ thống
2. Click vào menu **"Tiện ích"** trên thanh navigation
3. Chọn **"Dashboard Tính KPI"**
4. Trang hướng dẫn sẽ mở ra với:
   - Hướng dẫn khởi động Streamlit app
   - Kiểm tra trạng thái real-time
   - Link trực tiếp nếu app đang chạy

### 2. Chạy trực tiếp Streamlit app

```bash
cd kpi_dashboard
streamlit run app.py
```

hoặc sử dụng script:

**Windows:**
```cmd
run_kpi_dashboard.bat
```

**Linux/Mac:**
```bash
./run_kpi_dashboard.sh
```

## Các file đã thêm/sửa đổi

### Files mới:

1. **kpi_dashboard/** - Thư mục chứa Streamlit app
   - `app.py` - Main Streamlit application
   - `data_processor.py` - Data processing module
   - `kpi_calculator.py` - KPI calculation module
   - `kpi_views.py` - Django views for integration
   - `README.md` - Hướng dẫn chi tiết
   - `QUICKSTART.md` - Hướng dẫn nhanh

2. **templates_app/kpi_views.py** - Django views cho KPI Dashboard
   - `kpi_dashboard_view()` - Landing page
   - `kpi_dashboard_status()` - API check status
   - `kpi_dashboard_launch()` - API launch info

3. **templates_app/templates/templates_app/kpi_dashboard.html**
   - Template hiển thị trang hướng dẫn
   - Tích hợp kiểm tra trạng thái real-time
   - Link trực tiếp đến Streamlit app

### Files đã sửa đổi:

1. **templates_app/urls.py**
   - Thêm import `from . import kpi_views`
   - Thêm 3 URL patterns cho KPI Dashboard

2. **templates_app/templates/templates_app/base.html**
   - Thêm menu item "Dashboard Tính KPI" vào dropdown Tiện ích

3. **requirements.txt**
   - Thêm `streamlit>=1.28.0`

## Kiến trúc tích hợp

```
┌─────────────────────────────────────┐
│   Django Web Application (Main)    │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Navigation Menu (base.html)  │  │
│  │    └─ Tiện ích               │  │
│  │       └─ Dashboard Tính KPI  │  │
│  └──────────────────────────────┘  │
│                ↓                    │
│  ┌──────────────────────────────┐  │
│  │  kpi_dashboard_view          │  │
│  │  (kpi_views.py)              │  │
│  │  - Hiển thị hướng dẫn        │  │
│  │  - Check status Streamlit    │  │
│  │  - Link trực tiếp            │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
                 ↓
    ┌────────────────────────────┐
    │  Streamlit App (Độc lập)  │
    │  Port: 8501                │
    │                            │
    │  - Upload files            │
    │  - Process data            │
    │  - Calculate KPI           │
    │  - Export Excel            │
    └────────────────────────────┘
```

## Luồng hoạt động

1. **User click menu** → Django view `/kpi-dashboard/`
2. **Landing page** hiển thị:
   - Hướng dẫn sử dụng
   - Tính năng
   - Cách khởi động
3. **JavaScript** check status qua API `/api/kpi-dashboard/status/`
4. **Nếu Streamlit đang chạy** → Hiển thị nút "Mở KPI Dashboard"
5. **Nếu chưa chạy** → Hiển thị hướng dẫn khởi động
6. **User khởi động Streamlit** → App mở tại `localhost:8501`
7. **User sử dụng** Streamlit app để tính KPI

## API Endpoints

### 1. `/kpi-dashboard/`
- **Method:** GET
- **Auth:** Login required
- **Return:** HTML page (landing page)

### 2. `/api/kpi-dashboard/status/`
- **Method:** GET
- **Auth:** Login required
- **Return:** JSON
  ```json
  {
    "running": true,
    "port": 8501,
    "url": "http://localhost:8501"
  }
  ```

### 3. `/api/kpi-dashboard/launch/`
- **Method:** GET
- **Auth:** Login required
- **Return:** JSON with launch instructions

## Lưu ý quan trọng

### 1. Streamlit chạy độc lập
- KPI Dashboard là ứng dụng Streamlit chạy riêng biệt
- Không nhúng trực tiếp vào Django (do kiến trúc khác nhau)
- Cần khởi động manual hoặc tự động

### 2. Port mặc định
- Streamlit: `8501`
- Django: `8000` (hoặc port khác)
- Cần đảm bảo không conflict

### 3. Data security
- Streamlit chạy localhost, không public
- Dữ liệu upload được xử lý local
- File kết quả download về máy user

### 4. Multi-user
- Mỗi user cần chạy Streamlit instance riêng
- Hoặc chạy một instance chung (cần config port)

## Hướng dẫn deployment

### Development (Local)

1. Chạy Django:
   ```bash
   python manage.py runserver
   ```

2. Chạy Streamlit (terminal riêng):
   ```bash
   cd kpi_dashboard
   streamlit run app.py
   ```

### Production

**Option 1: Chạy riêng biệt**
- Django: Deploy như bình thường (Gunicorn, uWSGI, etc.)
- Streamlit: Deploy riêng với subdomain (kpi.agribank.com)

**Option 2: Reverse Proxy**
- Nginx proxy `/kpi/` → Streamlit port 8501
- Django chạy main app

**Option 3: Docker**
```yaml
version: '3'
services:
  django:
    build: .
    ports:
      - "8000:8000"

  streamlit:
    build: ./kpi_dashboard
    ports:
      - "8501:8501"
```

## Troubleshooting

### Lỗi: Module 'kpi_views' not found
**Giải pháp:** Restart Django server sau khi tạo file mới

### Lỗi: Streamlit không kết nối được
**Giải pháp:**
- Check port 8501 có bị chiếm không
- Firewall có block không
- Chạy: `streamlit run app.py --server.port=8502`

### Lỗi: Import error trong Streamlit
**Giải pháp:**
```bash
pip install -r requirements.txt --upgrade
```

## Roadmap

- [ ] Tự động khởi động Streamlit khi access trang
- [ ] Multi-user session management
- [ ] Tích hợp authentication từ Django
- [ ] History tracking và audit log
- [ ] Scheduled KPI calculation
- [ ] Email notification khi có báo cáo mới

## Support

Nếu gặp vấn đề, vui lòng kiểm tra:
1. `kpi_dashboard/README.md` - Hướng dẫn chi tiết
2. `kpi_dashboard/QUICKSTART.md` - Quick start guide
3. Log files của Streamlit
4. Django debug logs

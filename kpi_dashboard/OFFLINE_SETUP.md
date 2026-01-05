# Hướng dẫn Cài đặt KPI Dashboard cho Môi trường LAN Offline

## 📌 Tổng quan

KPI Dashboard **HOÀN TOÀN hoạt động** trong môi trường LAN không có kết nối Internet. Hướng dẫn này sẽ giúp bạn thiết lập và triển khai Dashboard trong mạng nội bộ.

---

## ✅ Xác nhận: Streamlit hoạt động Offline

Streamlit **KHÔNG CẦN Internet** để chạy vì:
- ✅ Tất cả code chạy local trên server
- ✅ Không có API calls bên ngoài
- ✅ Không sử dụng CDN (tất cả assets được bundle)
- ✅ Không có telemetry hay analytics online
- ✅ Xử lý dữ liệu hoàn toàn local

---

## 🔧 Bước 1: Chuẩn bị trên máy có Internet (một lần duy nhất)

### 1.1. Cài đặt Python và Dependencies

Trên máy có Internet, tải về tất cả dependencies:

```bash
# Tạo thư mục cho offline packages
mkdir streamlit_offline_packages
cd streamlit_offline_packages

# Download tất cả packages
pip download -r ../requirements.txt -d ./packages

# Hoặc chỉ download Streamlit và dependencies cần thiết
pip download streamlit pandas openpyxl xlrd xlsxwriter -d ./packages
```

### 1.2. Đóng gói toàn bộ project

```bash
# Nén thư mục project
zip -r kpi_dashboard_offline.zip kpi_dashboard/ streamlit_offline_packages/
```

---

## 📦 Bước 2: Cài đặt trên Server LAN (Offline)

### 2.1. Chuyển file vào server LAN

Sử dụng USB, shared folder, hoặc phương thức phù hợp để copy:
- `kpi_dashboard_offline.zip`

### 2.2. Giải nén và cài đặt

#### **Trên Windows:**

```cmd
# Giải nén
unzip kpi_dashboard_offline.zip

# Cài đặt Python (nếu chưa có)
# Tải Python installer từ python.org trước và copy vào

# Cài đặt packages từ thư mục offline
cd streamlit_offline_packages
pip install --no-index --find-links=./packages -r ../requirements.txt

# Hoặc cài từng package
pip install --no-index --find-links=./packages streamlit pandas openpyxl
```

#### **Trên Linux:**

```bash
# Giải nén
unzip kpi_dashboard_offline.zip

# Cài đặt packages
cd streamlit_offline_packages
pip install --no-index --find-links=./packages -r ../requirements.txt
```

---

## 🌐 Bước 3: Cấu hình cho Mạng LAN

### 3.1. File cấu hình đã có sẵn

File `.streamlit/config.toml` đã được cấu hình sẵn cho LAN:

```toml
[server]
port = 8501
address = "0.0.0.0"  # Cho phép truy cập từ các máy khác trong LAN
headless = true
enableCORS = false
maxUploadSize = 200

[browser]
gatherUsageStats = false  # Tắt telemetry
```

### 3.2. Xác định IP của Server

#### **Windows:**
```cmd
ipconfig
```
Tìm dòng "IPv4 Address", ví dụ: `192.168.1.100`

#### **Linux:**
```bash
ip addr show
# hoặc
ifconfig
```

### 3.3. Chạy Dashboard

```bash
cd kpi_dashboard
streamlit run app.py
```

Hoặc sử dụng script:
- Windows: `run_kpi_dashboard.bat`
- Linux: `./run_kpi_dashboard.sh`

---

## 💻 Bước 4: Truy cập từ các máy Client trong LAN

Từ bất kỳ máy nào trong mạng LAN:

### Cách 1: Truy cập qua IP
```
http://192.168.1.100:8501
```
*(Thay `192.168.1.100` bằng IP thực của server)*

### Cách 2: Truy cập qua hostname
```
http://server-name:8501
```

### Cách 3: Tích hợp vào Django (như hiện tại)
- Truy cập Django app: `http://192.168.1.100:8000`
- Click menu: **Tiện ích → Dashboard Tính KPI**
- Trang landing page sẽ tự động detect và link tới Streamlit

---

## 🔒 Bước 5: Cấu hình Firewall (nếu cần)

### Windows Firewall:

```cmd
# Cho phép port 8501
netsh advfirewall firewall add rule name="Streamlit KPI Dashboard" dir=in action=allow protocol=TCP localport=8501
```

### Linux Firewall (ufw):

```bash
sudo ufw allow 8501/tcp
```

### Linux Firewall (firewalld):

```bash
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload
```

---

## 🚀 Bước 6: Chạy tự động khi khởi động (Tùy chọn)

### Windows - Task Scheduler:

1. Mở **Task Scheduler**
2. Create Basic Task
3. Trigger: **At startup**
4. Action: **Start a program**
   - Program: `C:\path\to\kpi_dashboard\run_kpi_dashboard.bat`

### Linux - systemd service:

Tạo file `/etc/systemd/system/kpi-dashboard.service`:

```ini
[Unit]
Description=KPI Dashboard Streamlit App
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/kpi_dashboard
ExecStart=/usr/bin/streamlit run app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable và start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable kpi-dashboard
sudo systemctl start kpi-dashboard
```

---

## 📋 Checklist Triển khai

- [ ] Python đã cài đặt (3.8+)
- [ ] Dependencies đã cài (streamlit, pandas, openpyxl)
- [ ] File `.streamlit/config.toml` đã có
- [ ] Xác định IP của server
- [ ] Firewall đã mở port 8501 (nếu cần)
- [ ] Test chạy Streamlit: `streamlit run app.py`
- [ ] Test truy cập từ máy khác: `http://SERVER_IP:8501`
- [ ] Tích hợp với Django hoạt động

---

## 🧪 Kiểm tra hoạt động Offline

### Test 1: Chạy Streamlit
```bash
cd kpi_dashboard
streamlit run app.py
```
Kết quả mong đợi:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.1.100:8501
```

### Test 2: Truy cập từ browser
Mở browser và truy cập:
- `http://localhost:8501` (trên server)
- `http://192.168.1.100:8501` (từ máy khác)

### Test 3: Upload và xử lý file
1. Upload file KPI mẫu
2. Upload file dữ liệu
3. Click "Phân tích & Xuất Báo cáo"
4. Download file kết quả

✅ Nếu tất cả hoạt động → **Setup thành công!**

---

## 🔧 Troubleshooting

### Lỗi: "Cannot connect to Streamlit"

**Nguyên nhân:** Port bị block hoặc service chưa chạy

**Giải pháp:**
```bash
# Kiểm tra Streamlit có chạy không
ps aux | grep streamlit  # Linux
tasklist | findstr streamlit  # Windows

# Kiểm tra port
netstat -an | grep 8501  # Linux
netstat -an | findstr 8501  # Windows
```

### Lỗi: "Access denied from other computers"

**Nguyên nhân:** Firewall hoặc config sai

**Giải pháp:**
1. Kiểm tra `.streamlit/config.toml`:
   ```toml
   [server]
   address = "0.0.0.0"  # Phải là 0.0.0.0, không phải localhost
   ```
2. Mở firewall port 8501

### Lỗi: "Module not found"

**Nguyên nhân:** Dependencies chưa cài đặt đầy đủ

**Giải pháp:**
```bash
pip install -r requirements.txt --no-index --find-links=./streamlit_offline_packages/packages
```

---

## 📊 Kiến trúc Mạng LAN

```
┌─────────────────────────────────────────────┐
│           Mạng LAN (192.168.1.x)            │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Server (192.168.1.100)              │  │
│  │                                       │  │
│  │  ┌────────────────────────────────┐  │  │
│  │  │  Django App (Port 8000)        │  │  │
│  │  │  - Web interface               │  │  │
│  │  │  - User authentication         │  │  │
│  │  └────────────────────────────────┘  │  │
│  │                                       │  │
│  │  ┌────────────────────────────────┐  │  │
│  │  │  Streamlit App (Port 8501)     │  │  │
│  │  │  - KPI Dashboard               │  │  │
│  │  │  - File processing             │  │  │
│  │  │  - Excel generation            │  │  │
│  │  └────────────────────────────────┘  │  │
│  └──────────────────────────────────────┘  │
│               ↑         ↑         ↑         │
│               │         │         │         │
│  ┌────────┐  │  ┌──────┴───┐  ┌──┴──────┐  │
│  │ Client │  │  │ Client 2 │  │ Client3 │  │
│  │  .101  │  │  │   .102   │  │  .103   │  │
│  └────────┘  │  └──────────┘  └─────────┘  │
│              │                              │
└──────────────┼──────────────────────────────┘
               │
        KHÔNG CẦN INTERNET
```

---

## 🎯 Lợi ích của Offline Deployment

✅ **Bảo mật:** Dữ liệu không rời khỏi mạng nội bộ
✅ **Tốc độ:** Không bị giới hạn bởi băng thông Internet
✅ **Ổn định:** Không phụ thuộc vào kết nối Internet
✅ **Tuân thủ:** Đáp ứng yêu cầu bảo mật ngân hàng
✅ **Chi phí:** Không tốn băng thông Internet

---

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra log: Terminal chạy Streamlit
2. Kiểm tra config: `.streamlit/config.toml`
3. Kiểm tra network: `ping server-ip`
4. Kiểm tra port: `telnet server-ip 8501`

---

## 📚 Tài liệu tham khảo

- `README.md` - Hướng dẫn tổng quan
- `QUICKSTART.md` - Hướng dẫn nhanh
- `INTEGRATION.md` - Tích hợp với Django
- `OFFLINE_SETUP.md` - File này

---

**✅ KPI Dashboard hoạt động HOÀN TOÀN độc lập, không cần Internet!**

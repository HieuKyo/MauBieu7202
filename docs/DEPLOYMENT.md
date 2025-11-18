# HƯỚNG DẪN TRIỂN KHAI VÀ CẬP NHẬT MAUBIEU7202

## Mục lục
- [Triển khai trên mạng nội bộ](#triển-khai-trên-mạng-nội-bộ)
- [Cập nhật chương trình](#cập-nhật-chương-trình)
- [Backup và khôi phục](#backup-và-khôi-phục)
- [Giám sát hệ thống](#giám-sát-hệ-thống)
- [Xử lý sự cố](#xử-lý-sự-cố)

---

## Triển khai trên mạng nội bộ

### Yêu cầu máy chủ
- **RAM**: Tối thiểu 2GB (khuyến nghị 4GB)
- **CPU**: 2 cores trở lên
- **Ổ cứng**: 10GB trống
- **Hệ điều hành**: Windows 10/11 hoặc Linux
- **Mạng**: IP tĩnh trong mạng LAN

### Bước 1: Chuẩn bị môi trường

1. **Đặt IP tĩnh cho máy chủ**
   - Ví dụ: 192.168.1.100
   - Subnet mask: 255.255.255.0
   - Gateway: 192.168.1.1

2. **Mở port firewall**

   **Windows:**
   ```cmd
   netsh advfirewall firewall add rule name="MauBieu7202" dir=in action=allow protocol=tcp localport=8000
   ```

   **Linux:**
   ```bash
   sudo ufw allow 8000/tcp
   ```

### Bước 2: Cấu hình Production

1. **Chỉnh sửa file `.env`**
   ```env
   # TẮT chế độ debug
   DEBUG=False

   # Tạo SECRET_KEY mới và mạnh
   SECRET_KEY=your-very-long-and-secure-secret-key-here

   # Thêm IP máy chủ và các hostname
   ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100,maubieu.local
   ```

2. **Thu thập static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

### Bước 3: Chạy chương trình Production

**Linux/macOS:**
```bash
# Kích hoạt môi trường ảo
source venv/bin/activate

# Chạy server production
python run_waitress.py
```

**Windows:**
```cmd
:: Lần đầu (chạy setup)
setup.bat

:: Các lần sau
start.bat

:: Hoặc chạy thủ công
venv\Scripts\activate
python run_waitress.py
```

### Bước 4: Chạy như Service (khuyến nghị)

#### Windows - Task Scheduler

1. Mở **Task Scheduler**
2. Tạo **Basic Task** mới
3. Cấu hình:
   - Trigger: **When the computer starts**
   - Action: **Start a program**
   - Program: `C:\path\to\MauBieu7202\start.bat`
   - Start in: `C:\path\to\MauBieu7202\`

#### Linux - Systemd Service

1. **Tạo file service**
   ```bash
   sudo nano /etc/systemd/system/maubieu.service
   ```

2. **Nội dung file:**
   ```ini
   [Unit]
   Description=MauBieu7202 Application
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/path/to/MauBieu7202
   ExecStart=/path/to/MauBieu7202/venv/bin/python run_waitress.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. **Kích hoạt service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable maubieu
   sudo systemctl start maubieu
   ```

4. **Kiểm tra trạng thái**
   ```bash
   sudo systemctl status maubieu
   ```

### Bước 5: Truy cập từ các máy khác

1. **Từ trình duyệt**, nhập địa chỉ:
   ```
   http://192.168.1.100:8000
   ```

2. **Kiểm tra kết nối**
   - Đảm bảo máy client và server cùng mạng LAN
   - Kiểm tra firewall không chặn port 8000
   - Ping thử: `ping 192.168.1.100`

---

## Cập nhật chương trình

### Quy trình cập nhật chuẩn

#### Bước 1: Backup trước khi cập nhật
```bash
# Backup database
cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d)

# Backup media files
cp -r media media_backup_$(date +%Y%m%d)

# Backup cấu hình
cp .env .env.backup
```

#### Bước 2: Dừng chương trình

**Windows:**
- Đóng cửa sổ cmd đang chạy server
- Hoặc dừng Task Scheduler job

**Linux:**
```bash
sudo systemctl stop maubieu
```

#### Bước 3: Cập nhật mã nguồn

**Nếu dùng Git:**
```bash
git pull origin main
```

**Nếu dùng file zip:**
1. Giải nén file mới vào thư mục tạm
2. Sao chép đè các file (trừ `.env`, `db.sqlite3`, `media/`)

#### Bước 4: Cài đặt dependencies mới (nếu có)
```bash
pip install -r requirements.txt
```

#### Bước 5: Cập nhật database
```bash
python manage.py migrate
```

#### Bước 6: Thu thập static files mới
```bash
python manage.py collectstatic --noinput
```

#### Bước 7: Khởi động lại chương trình

**Windows:**
```cmd
start.bat
```

**Linux:**
```bash
sudo systemctl start maubieu
```

### Cập nhật nhanh (chỉ code, không database)

```bash
# 1. Pull code mới
git pull origin main

# 2. Restart service
sudo systemctl restart maubieu   # Linux
# hoặc đóng/mở lại start.bat    # Windows
```

### Cập nhật có thay đổi database

```bash
# 1. Backup
cp db.sqlite3 db.sqlite3.backup

# 2. Pull code
git pull origin main

# 3. Migrate
python manage.py migrate

# 4. Restart
sudo systemctl restart maubieu
```

---

## Backup và khôi phục

### Backup tự động (Linux)

1. **Tạo script backup**
   ```bash
   nano /path/to/backup_maubieu.sh
   ```

2. **Nội dung script:**
   ```bash
   #!/bin/bash

   BACKUP_DIR="/path/to/backups"
   APP_DIR="/path/to/MauBieu7202"
   DATE=$(date +%Y%m%d_%H%M%S)

   # Tạo thư mục backup
   mkdir -p $BACKUP_DIR

   # Backup database
   cp $APP_DIR/db.sqlite3 $BACKUP_DIR/db_$DATE.sqlite3

   # Backup media
   tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C $APP_DIR media

   # Backup cấu hình
   cp $APP_DIR/.env $BACKUP_DIR/env_$DATE

   # Xóa backup cũ hơn 30 ngày
   find $BACKUP_DIR -type f -mtime +30 -delete

   echo "Backup completed: $DATE"
   ```

3. **Cấp quyền thực thi**
   ```bash
   chmod +x /path/to/backup_maubieu.sh
   ```

4. **Thêm vào crontab (chạy hàng ngày 2h sáng)**
   ```bash
   crontab -e
   # Thêm dòng:
   0 2 * * * /path/to/backup_maubieu.sh
   ```

### Backup thủ công

```bash
# Backup database
cp db.sqlite3 backups/db_backup_$(date +%Y%m%d).sqlite3

# Backup toàn bộ
tar -czf maubieu_backup_$(date +%Y%m%d).tar.gz \
    db.sqlite3 \
    media/ \
    .env \
    --exclude='__pycache__' \
    --exclude='*.pyc'
```

### Khôi phục từ backup

```bash
# 1. Dừng chương trình
sudo systemctl stop maubieu

# 2. Khôi phục database
cp backups/db_backup_20241118.sqlite3 db.sqlite3

# 3. Khôi phục media
tar -xzf backups/media_backup_20241118.tar.gz -C .

# 4. Khởi động lại
sudo systemctl start maubieu
```

---

## Giám sát hệ thống

### Kiểm tra logs

**Waitress logs:**
```bash
# Xem log trực tiếp khi chạy
python run_waitress.py

# Linux: Xem journal logs
sudo journalctl -u maubieu -f
```

### Kiểm tra trạng thái

**Linux:**
```bash
# Trạng thái service
sudo systemctl status maubieu

# Kiểm tra port
netstat -tlnp | grep 8000

# Kiểm tra process
ps aux | grep waitress
```

**Windows:**
```cmd
:: Kiểm tra port
netstat -ano | findstr :8000

:: Kiểm tra process
tasklist | findstr python
```

### Kiểm tra dung lượng

```bash
# Dung lượng database
ls -lh db.sqlite3

# Dung lượng media
du -sh media/

# Dung lượng tổng
du -sh /path/to/MauBieu7202/
```

---

## Xử lý sự cố

### Lỗi thường gặp và cách khắc phục

#### 1. Không thể truy cập từ máy khác

**Nguyên nhân & Giải pháp:**
- Kiểm tra IP server: `ipconfig` (Windows) hoặc `ip addr` (Linux)
- Kiểm tra ALLOWED_HOSTS trong `.env`
- Kiểm tra firewall đã mở port 8000
- Ping thử: `ping <server-ip>`

#### 2. Lỗi "DisallowedHost"

**Giải pháp:**
```env
# Thêm host vào .env
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100,ten-may-chu
```

#### 3. Static files không hiển thị

**Giải pháp:**
```bash
python manage.py collectstatic --noinput
```

#### 4. Database bị lock

**Giải pháp:**
```bash
# Dừng tất cả process
sudo systemctl stop maubieu

# Kiểm tra không còn process nào dùng database
fuser db.sqlite3

# Khởi động lại
sudo systemctl start maubieu
```

#### 5. Chương trình chạy chậm

**Giải pháp:**
1. Tăng số threads trong `run_waitress.py`:
   ```python
   threads = 8  # Tăng từ 4 lên 8
   ```
2. Kiểm tra dung lượng database
3. Cân nhắc chuyển sang PostgreSQL nếu dữ liệu lớn

#### 6. Lỗi sau khi cập nhật

**Giải pháp:**
```bash
# Khôi phục database từ backup
cp db.sqlite3.backup db.sqlite3

# Hoặc rollback code
git checkout <previous-commit>

# Khởi động lại
sudo systemctl restart maubieu
```

### Liên hệ hỗ trợ

Nếu gặp vấn đề không thể tự xử lý:
1. Ghi lại thông báo lỗi đầy đủ
2. Ghi lại các bước đã thực hiện
3. Liên hệ bộ phận IT hoặc người phát triển

---

## Checklist triển khai

### Trước khi triển khai
- [ ] Đã cài đặt Python 3.10+
- [ ] Đã tạo virtual environment
- [ ] Đã cài đặt dependencies
- [ ] Đã cấu hình `.env`
- [ ] Đã chạy migrations
- [ ] Đã tạo superuser
- [ ] Đã collectstatic
- [ ] Đã test chạy local

### Khi triển khai
- [ ] Đặt IP tĩnh cho server
- [ ] Mở firewall port 8000
- [ ] Cấu hình ALLOWED_HOSTS
- [ ] Tắt DEBUG mode
- [ ] Đổi SECRET_KEY
- [ ] Chạy với Waitress
- [ ] Test từ máy khác trong LAN

### Sau khi triển khai
- [ ] Cấu hình thông tin chi nhánh
- [ ] Tạo danh mục và mẫu biểu
- [ ] Import danh sách nhân viên
- [ ] Phân quyền người dùng
- [ ] Thiết lập backup tự động
- [ ] Đào tạo người dùng

---

## Thông số kỹ thuật Production

| Thông số | Giá trị mặc định | Ghi chú |
|----------|------------------|---------|
| Host | 0.0.0.0 | Lắng nghe tất cả interfaces |
| Port | 8000 | Có thể đổi nếu cần |
| Threads | 4 | Tăng nếu nhiều người dùng |
| Channel Timeout | 60s | Thời gian chờ request |
| Connection Limit | 1000 | Số kết nối tối đa |

### Chỉnh sửa trong `run_waitress.py`:
```python
host = '0.0.0.0'
port = 8000
threads = 4
channel_timeout = 60
connection_limit = 1000
```

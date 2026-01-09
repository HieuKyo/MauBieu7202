# Hướng dẫn cập nhật dbfread cho KPI Dashboard

## 📢 Thông báo cập nhật

Phiên bản mới của MauBieu7202 yêu cầu thư viện **dbfread >= 2.0.7** để hỗ trợ KPI Dashboard.

## 🔍 Kiểm tra xem bạn đã có dbfread chưa

```bash
python -c "import dbfread; print('Đã cài:', dbfread.__version__)"
```

- **Nếu thành công**: Hiển thị "Đã cài: 2.0.7" → Bạn đã có, không cần làm gì thêm
- **Nếu lỗi**: "No module named 'dbfread'" → Cần cài đặt

---

## 🚀 Cách 1: Cài đặt nhanh (có Internet)

**Nếu máy hiện tại có Internet:**

```bash
pip install dbfread>=2.0.7
```

Xong! Giờ bạn có thể sử dụng KPI Dashboard.

---

## 📦 Cách 2: Cài đặt offline (không có Internet)

### Bước 1: Trên máy có Internet

```bash
# Download packages mới (bao gồm dbfread)
download_packages.bat

# Hoặc chỉ download dbfread
pip download dbfread>=2.0.7 -d packages
```

### Bước 2: Copy sang máy LAN

Copy thư mục `packages` (hoặc file `dbfread-*.whl`) sang máy LAN

### Bước 3: Trên máy LAN

```bash
# Cài đặt từ thư mục packages
pip install --no-index --find-links=packages dbfread

# Hoặc cài trực tiếp từ file .whl
pip install packages\dbfread-2.0.7-py2.py3-none-any.whl
```

---

## 🔄 Cách 3: Cập nhật toàn bộ hệ thống

### Trên máy có Internet:

```bash
# Download tất cả packages mới
download_packages.bat

# Verify đã download đầy đủ
verify_packages.bat
```

### Copy sang máy LAN, sau đó:

```bash
# Chạy lại setup để cài đặt tất cả
setup.bat
```

Script `setup.bat` đã được cập nhật để:
- ✅ Tự động phát hiện thư mục `packages` hoặc `offline_packages`
- ✅ Kiểm tra dbfread sau khi cài đặt
- ✅ Gợi ý cài đặt từ Internet nếu thiếu
- ✅ Hỗ trợ cả workflow cũ và mới

---

## 📝 Scripts mới được thêm vào

| Script | Mục đích | Chạy ở đâu |
|--------|----------|------------|
| `download_packages.bat` | Download packages vào `packages/` | Máy có Internet |
| `download_offline_packages.bat` | Download packages vào `offline_packages/` | Máy có Internet |
| `verify_packages.bat` | Kiểm tra packages đã đầy đủ chưa | Bất kỳ đâu |
| `install_offline.bat` | Cài đặt hoàn toàn offline (workflow mới) | Máy LAN |

---

## ✅ Verify sau khi cài đặt

```bash
# Kiểm tra dbfread
python -c "import dbfread; print('✓ dbfread:', dbfread.__version__)"

# Kiểm tra tất cả packages
verify_packages.bat
```

---

## 🆘 Xử lý lỗi

### Lỗi: "No module named 'dbfread'"

**Nguyên nhân**: Chưa cài đặt dbfread

**Giải pháp**:
1. Nếu có Internet: `pip install dbfread>=2.0.7`
2. Nếu không có Internet: Xem [Cách 2](#-cách-2-cài-đặt-offline-không-có-internet)

### Lỗi: "Could not find a version that satisfies dbfread"

**Nguyên nhân**: Thư mục packages không có dbfread

**Giải pháp**:
```bash
# Trên máy có Internet
pip download dbfread>=2.0.7 -d packages

# Copy packages sang máy LAN và cài lại
pip install --no-index --find-links=packages dbfread
```

### Lỗi khi chạy setup.bat: "Khong the cai dat mot so dependencies"

**Nguyên nhân**: Thiếu một số packages trong thư mục packages

**Giải pháp**:
1. Chạy `verify_packages.bat` để xem thiếu package nào
2. Trên máy có Internet: `download_packages.bat`
3. Copy lại thư mục packages sang máy LAN
4. Chạy lại `setup.bat`

---

## 📊 Kiểm tra KPI Dashboard hoạt động

1. Khởi động server:
   ```bash
   run.bat
   ```

2. Truy cập: http://10.135.7.108:8888/kpi-dashboard/

3. Upload file test:
   - File KPI mẫu (.xlsx)
   - File dữ liệu Thẻ (Excel/CSV hoặc DBF)
   - File dữ liệu SMS (Excel/CSV hoặc DBF)

4. Nếu thành công → dbfread đã hoạt động ✓

---

## 📌 Tổng kết

**Những gì đã thay đổi:**
- ✅ Thêm `dbfread>=2.0.7` vào requirements.txt
- ✅ Cập nhật `setup.bat` hỗ trợ cả `packages` và `offline_packages`
- ✅ Thêm scripts mới: `download_packages.bat`, `verify_packages.bat`
- ✅ Thêm tài liệu: `INSTALL_LAN.md`, `UPDATE_DBFREAD.md`

**Nếu bạn đã cài đặt trước đây:**
- Chỉ cần cài thêm dbfread (Cách 1 hoặc Cách 2)
- Không cần cài lại toàn bộ

**Nếu bạn cài đặt lần đầu:**
- Chạy `download_packages.bat` (máy có Internet)
- Copy `packages` sang máy LAN
- Chạy `setup.bat` (sẽ tự động cài dbfread)

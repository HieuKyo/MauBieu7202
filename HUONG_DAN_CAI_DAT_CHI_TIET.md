# HƯỚNG DẪN CÀI ĐẶT MAUBIEUMOI - TỪNG BƯỚC CHI TIẾT

## 📌 MỤC ĐÍCH
Hướng dẫn này giúp bạn setup hệ thống Hybrid Template Storage để **mẫu biểu không bao giờ hết hạn**.

---

## 🎯 BƯỚC 1: PULL CODE TỪ GITHUB

### **1.1. Mở PowerShell trong VSCode**

**Cách 1: Dùng phím tắt**
- Nhấn `Ctrl + ~` (phím dấu huyền, nằm dưới phím ESC)

**Cách 2: Dùng menu**
- Click menu **Terminal** → **New Terminal**

**Kết quả:** Bạn sẽ thấy cửa sổ Terminal hiện ra ở phía dưới VSCode, dòng đầu tiên kiểu như:
```
PS C:\HIEU\MauBieu7202>
```

---

### **1.2. Xóa file conflict**

Copy lệnh này vào PowerShell, nhấn Enter:

```powershell
Remove-Item "payroll_statistics\migrations\0003_rename_payroll_sta_transac_76d4e5_idx_payroll_sta_transac_691697_idx_and_more.py" -ErrorAction SilentlyContinue
```

**Giải thích:** Lệnh này xóa file migration bị conflict để tránh lỗi khi pull.

**Kết quả:** Không có thông báo gì (bình thường), hoặc hiện "File không tồn tại" (cũng OK).

---

### **1.3. Pull code từ GitHub**

Copy lệnh này vào PowerShell, nhấn Enter:

```powershell
git pull origin claude/django-word-template-generator-011CUfkKT1HZ7HQosuoKML8r
```

**Kết quả mong đợi:**
```
Updating 9dfac83..8314f40
Fast-forward
 GIAI_QUYET_TEMPLATE_HET_HAN.txt     | 218 ++++++
 HUONG_DAN_SETUP_MAUBIEU.md          | 313 +++++++++
 ...
 11 files changed, 1701 insertions(+)
```

✅ **Nếu thấy dòng "Fast-forward" hoặc "Already up to date"** → THÀNH CÔNG!

❌ **Nếu vẫn báo lỗi**, copy toàn bộ lỗi và báo cho tôi.

---

## 🎯 BƯỚC 2: CÀI ĐẶT DEPENDENCIES (Thư viện Python)

### **2.1. Cài đặt tất cả thư viện cần thiết**

Copy lệnh này vào PowerShell:

```powershell
pip install -r requirements.txt
```

**Giải thích:** Lệnh này cài tất cả thư viện Python cần thiết (Django, python-docx, pandas, v.v.)

**Kết quả:**
- Bạn sẽ thấy nhiều dòng "Installing collected packages..."
- Chờ 1-2 phút để cài đặt hoàn tất

**Nếu lỗi "pip: command not found":**
```powershell
python -m pip install -r requirements.txt
```

**Nếu lỗi "python: command not found":**
```powershell
py -m pip install -r requirements.txt
```

---

## 🎯 BƯỚC 3: TẠO FOLDER MAUBIEUMOI

### **3.1. Tạo folder C:\maubieumoi**

Copy lệnh này vào PowerShell:

```powershell
New-Item -ItemType Directory -Path "C:\maubieumoi" -Force
```

**Giải thích:** Tạo folder `C:\maubieumoi` để chứa file template .docx

**Kết quả:**
```
    Directory: C:\

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----        12/11/2025   2:00 PM                maubieumoi
```

✅ **Thấy dòng trên** → Folder đã được tạo thành công!

---

### **3.2. Kiểm tra folder đã tồn tại**

```powershell
Test-Path "C:\maubieumoi"
```

**Kết quả:** Phải hiện `True`

---

### **3.3. Tạo folder media (cache)**

```powershell
New-Item -ItemType Directory -Path "media\templates\docx" -Force
```

**Giải thích:** Tạo folder cache để lưu template sau khi đọc từ maubieumoi

**Kết quả:** Sẽ tạo folder `media/templates/docx/` trong project

---

## 🎯 BƯỚC 4: UPDATE SETTINGS.PY CHO WINDOWS

### **4.1. Mở file settings.py**

Trong VSCode:
1. Click vào **Explorer** (icon folder bên trái)
2. Mở folder **wordgen**
3. Click vào file **settings.py**

---

### **4.2. Tìm dòng cần sửa**

Nhấn `Ctrl+F` để mở Find, gõ: `OFFLINE_TEMPLATE_PATH`

Bạn sẽ thấy dòng:
```python
OFFLINE_TEMPLATE_PATH = '/home/user/maubieumoi'  # Folder chứa templates offline
```

---

### **4.3. Thay thế bằng code mới**

**XÓA** 2 dòng cũ:
```python
OFFLINE_TEMPLATE_PATH = '/home/user/maubieumoi'  # Folder chứa templates offline
TEMPLATE_AUTO_CACHE = True  # Auto-copy từ offline sang media để cache và tăng performance
```

**THAY BẰNG** code mới (copy toàn bộ):

```python
# Template Storage Configuration - Hybrid Fallback Mechanism
# Giải quyết vấn đề template hết hạn sau 1 tuần
import platform

# Auto-detect OS (Windows hoặc Linux)
if platform.system() == 'Windows':
    OFFLINE_TEMPLATE_PATH = r'C:\maubieumoi'
else:
    OFFLINE_TEMPLATE_PATH = '/home/user/maubieumoi'

TEMPLATE_AUTO_CACHE = True  # Auto-copy từ offline sang media để cache và tăng performance
```

---

### **4.4. Lưu file**

Nhấn `Ctrl+S` để lưu file settings.py

✅ **Dấu chấm trắng bên cạnh tên file sẽ biến mất** → Đã lưu thành công!

---

## 🎯 BƯỚC 5: MIGRATE DATABASE

### **5.1. Chạy migrations**

Copy lệnh vào PowerShell:

```powershell
python manage.py migrate
```

**Giải thích:** Tạo/cập nhật database với cấu trúc mới

**Kết quả mong đợi:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, ...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying templates_app.0034_alter_template_file... OK
```

✅ **Thấy nhiều dòng "OK"** → Thành công!

❌ **Nếu lỗi "No module named 'django'":**
```powershell
pip install Django
python manage.py migrate
```

---

## 🎯 BƯỚC 6: COPY TEMPLATES VÀO MAUBIEUMOI

### **6.1. Xác định vị trí templates hiện tại**

Tìm folder chứa các file .docx template hiện tại của bạn.

**Ví dụ:** Có thể ở:
- `C:\HIEU\Templates\`
- `D:\MauBieu\`
- `Desktop\Templates\`
- v.v.

---

### **6.2. Copy templates vào C:\maubieumoi**

**Cách 1: Dùng File Explorer (Dễ nhất)**

1. Mở File Explorer (nhấn `Win + E`)
2. Vào folder chứa templates hiện tại của bạn
3. Chọn tất cả file .docx (`Ctrl+A`)
4. Copy (`Ctrl+C`)
5. Vào folder `C:\maubieumoi`
6. Paste (`Ctrl+V`)

**Cách 2: Dùng PowerShell**

```powershell
# Thay YOUR_PATH bằng đường dẫn thực tế
Copy-Item "D:\MauBieu\*.docx" -Destination "C:\maubieumoi\"
```

**Ví dụ cụ thể:**
```powershell
# Nếu templates ở Desktop
Copy-Item "$env:USERPROFILE\Desktop\Templates\*.docx" -Destination "C:\maubieumoi\"

# Nếu templates ở D:\MauBieu
Copy-Item "D:\MauBieu\*.docx" -Destination "C:\maubieumoi\"
```

---

### **6.3. Kiểm tra đã copy thành công**

```powershell
Get-ChildItem "C:\maubieumoi\*.docx"
```

**Kết quả:** Sẽ liệt kê tất cả file .docx trong folder

**Ví dụ:**
```
    Directory: C:\maubieumoi

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----        12/10/2025   3:15 PM          60992 Mau_1a.docx
-a----        12/10/2025   3:15 PM          52341 Mau_2b.docx
-a----        12/10/2025   3:15 PM          48573 Mau_3c.docx
```

✅ **Thấy danh sách file .docx** → Thành công!

---

## 🎯 BƯỚC 7: VALIDATE TEMPLATES (Kiểm tra templates có bị lỗi không)

### **7.1. Chạy script validate**

```powershell
python validate_templates.py C:\maubieumoi
```

**Kết quả mong đợi:**
```
🔍 Scanning 5 template files in C:\maubieumoi

================================================================================
✅ Mau_1a.docx
   Valid (12 paragraphs, 5 tables, 60,992 bytes)

✅ Mau_2b.docx
   Valid (8 paragraphs, 3 tables, 52,341 bytes)
...

📊 SUMMARY:
   Total files:   5
   ✅ Valid:      5
   ❌ Invalid:    0

✨ All templates are valid!
```

✅ **Thấy "All templates are valid!"** → Hoàn hảo!

❌ **Nếu có templates invalid:**
- File đó bị corrupt/hỏng
- Thay bằng file .docx mới

---

## 🎯 BƯỚC 8: TEST HYBRID STORAGE

### **8.1. Chạy test**

```powershell
python test_hybrid_storage.py
```

**Kết quả mong đợi:**
```
🧪 Testing HybridTemplateStorage

✓ Test 1: Configuration
   Offline path: C:\maubieumoi
   Auto-cache enabled: True

✓ Test 2: Offline folder
   Offline folder exists: True
   Templates found: 5

✓ Test 3: Media folder
   Media folder exists: True

✅ All tests passed!
```

✅ **Thấy "All tests passed!"** → Hệ thống hoạt động tốt!

---

## 🎯 BƯỚC 9: CHẠY SERVER

### **9.1. Chạy Django development server**

```powershell
python manage.py runserver 8000
```

**Kết quả mong đợi:**
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
December 11, 2025 - 14:30:00
Django version 5.2.7, using settings 'wordgen.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

✅ **Thấy "Starting development server"** → Server đã chạy!

---

### **9.2. Mở trình duyệt**

1. Mở trình duyệt (Chrome, Edge, Firefox...)
2. Vào địa chỉ: `http://localhost:8000`

✅ **Thấy trang chủ chương trình** → Thành công hoàn toàn!

---

## 🎯 BƯỚC 10: TEST SỬ DỤNG TEMPLATE

### **10.1. Tạo document từ template**

1. Trong trình duyệt, vào chức năng tạo document
2. Chọn một template
3. Điền thông tin
4. Click "In mẫu biểu" hoặc "Generate"

---

### **10.2. Kiểm tra trong PowerShell**

Khi generate document, bạn sẽ thấy log trong PowerShell:

```
✓ Template found in offline folder: C:\maubieumoi\Mau_1a.docx
✓ Cached to media folder: C:\HIEU\MauBieu7202\media\templates\docx\Mau_1a.docx
```

**Giải thích:**
- Lần đầu: Đọc từ `C:\maubieumoi` → Copy vào `media/` (cache)
- Lần sau: Đọc nhanh từ cache

---

## 🎯 BƯỚC 11: VERIFY CACHE HOẠT ĐỘNG

### **11.1. Kiểm tra folder cache**

```powershell
Get-ChildItem "media\templates\docx"
```

**Kết quả:** Sẽ thấy file .docx đã được cache

---

### **11.2. Test fallback mechanism**

**Test 1: Rename offline folder**
```powershell
# Rename C:\maubieumoi thành C:\maubieumoi_backup
Rename-Item "C:\maubieumoi" "C:\maubieumoi_backup"

# Generate document lại
# → Vẫn hoạt động vì có cache!
```

**Test 2: Restore offline folder**
```powershell
# Rename lại
Rename-Item "C:\maubieumoi_backup" "C:\maubieumoi"
```

✅ **Hệ thống vẫn hoạt động khi mất offline folder** → Fallback thành công!

---

## 📊 TÓM TẮT QUY TRÌNH

```
1. Pull code từ GitHub               ✓
2. Cài dependencies                   ✓
3. Tạo folder C:\maubieumoi          ✓
4. Update settings.py                 ✓
5. Migrate database                   ✓
6. Copy templates vào C:\maubieumoi  ✓
7. Validate templates                 ✓
8. Test hybrid storage                ✓
9. Chạy server                        ✓
10. Test sử dụng template            ✓
```

---

## 🔧 TROUBLESHOOTING (Xử lý lỗi)

### **Lỗi 1: "python: command not found"**

**Giải pháp:**
```powershell
# Thử dùng py thay vì python
py manage.py runserver
```

---

### **Lỗi 2: "Module not found"**

**Giải pháp:**
```powershell
# Cài lại dependencies
pip install -r requirements.txt

# Hoặc cài từng package
pip install Django python-docx openpyxl pandas unidecode
pip install django-import-export whitenoise
```

---

### **Lỗi 3: "Permission denied" khi tạo folder**

**Giải pháp:**
1. Click chuột phải vào PowerShell
2. Chọn "Run as Administrator"
3. Chạy lại lệnh tạo folder

---

### **Lỗi 4: Templates không tìm thấy**

**Kiểm tra:**
```powershell
# Check settings
python -c "from wordgen import settings; print(settings.OFFLINE_TEMPLATE_PATH)"

# Kết quả phải là: C:\maubieumoi

# Check folder tồn tại
Test-Path "C:\maubieumoi"

# Kết quả phải là: True

# Check có templates
Get-ChildItem "C:\maubieumoi\*.docx"
```

---

### **Lỗi 5: File Word bị corrupt khi mở**

**Giải pháp:**
```powershell
# Validate template
python validate_templates.py C:\maubieumoi

# Nếu file corrupt → Thay bằng file .docx mới
```

---

## 📁 CẤU TRÚC THỨ MỤC SAU KHI SETUP

```
C:\HIEU\MauBieu7202\
├── media\
│   └── templates\
│       └── docx\               ← Cache (tự động tạo khi generate)
│           ├── Mau_1a.docx
│           └── Mau_2b.docx
├── templates_app\
│   ├── models.py               ← Đã update với HybridTemplateStorage
│   └── storage.py              ← Custom storage backend
├── wordgen\
│   └── settings.py             ← Đã update OFFLINE_TEMPLATE_PATH
├── manage.py
├── requirements.txt
├── validate_templates.py       ← Script kiểm tra templates
├── test_hybrid_storage.py      ← Script test storage
└── db.sqlite3                  ← Database

C:\maubieumoi\                  ← Offline templates (tạo thủ công)
├── Mau_1a.docx                ← Copy từ folder cũ
├── Mau_2b.docx
├── Mau_3c.docx
└── ...
```

---

## ✅ CHECKLIST HOÀN THÀNH

Đánh dấu ✓ vào mỗi mục sau khi hoàn thành:

- [ ] 1. Pull code thành công (không có lỗi)
- [ ] 2. Cài dependencies (pip install -r requirements.txt)
- [ ] 3. Tạo folder C:\maubieumoi
- [ ] 4. Update settings.py với Windows path
- [ ] 5. Migrate database (thấy nhiều dòng OK)
- [ ] 6. Copy templates vào C:\maubieumoi
- [ ] 7. Validate templates (All templates are valid!)
- [ ] 8. Test hybrid storage (All tests passed!)
- [ ] 9. Chạy server (Starting development server...)
- [ ] 10. Truy cập http://localhost:8000 OK
- [ ] 11. Test tạo document từ template OK

---

## 🎓 GIẢI THÍCH HOẠT ĐỘNG

### **Trước khi setup (Có vấn đề):**
```
User request template
    ↓
Read từ folder tạm (/tmp hoặc session)
    ↓
Sau 1 tuần: Folder tạm bị xóa
    ↓
❌ Template không tìm thấy → Lỗi!
```

### **Sau khi setup (Đã fix):**
```
User request template
    ↓
1. Check C:\maubieumoi (Offline folder)
    ↓
   [CÓ] → Copy vào media\templates\docx (Cache)
   [KHÔNG] → Check cache
    ↓
2. Check media\templates\docx (Cache)
    ↓
   [CÓ] → Dùng cache
   [KHÔNG] → Báo lỗi
    ↓
✅ Template KHÔNG BAO GIỜ hết hạn!
```

---

## 📞 HỖ TRỢ

**Nếu gặp vấn đề:**

1. **Copy toàn bộ lỗi** trong PowerShell
2. **Chụp màn hình** (nếu cần)
3. **Báo cho tôi** để được hỗ trợ

**Kiểm tra logs:**
```powershell
# Chạy server với verbose mode
python manage.py runserver --verbosity 2
```

---

## 🎉 HOÀN TẤT!

Sau khi hoàn thành tất cả các bước trên, hệ thống của bạn sẽ:

✅ **Mẫu biểu không bao giờ hết hạn**
✅ **Tự động cache để tăng performance**
✅ **Fallback khi mất kết nối với offline folder**
✅ **Dễ dàng cập nhật templates** (chỉ cần thay file trong C:\maubieumoi)

---

**Chúc mừng! Hệ thống đã sẵn sàng sử dụng!** 🚀

# HƯỚNG DẪN: Setup Maubieumoi Với Subdirectories

## 📂 Cấu Trúc Thư Mục Của Bạn

```
C:\maubieumoi\
├── ATM\
│   ├── MauATM_01.docx
│   ├── MauATM_02.docx
│   └── BaoCaoATM.docx
├── DICHVU\
│   ├── MauMoThe.docx
│   ├── MauDongThe.docx
│   └── MauNapTien.docx
├── DIENTOAN\
│   ├── BaoCaoHangNgay.docx
│   └── ThongKe.docx
├── KETOAN\
│   ├── TKDV\
│   │   ├── MauBaoCao.docx
│   │   └── MauMoThe.docx
│   └── TKTT\
│       └── MauChuyenTien.docx
└── ... (các folder khác)
```

---

## ✅ **PHƯƠNG ÁN 1: Tự Động Tìm Trong Subdirectories** ⭐ KHUYÊN DÙNG

### **Cách Hoạt Động:**

Hệ thống sẽ **TỰ ĐỘNG** tìm file template trong tất cả thư mục con:

```
User chọn template "MauMoThe"
    ↓
1. Tìm ở root: C:\maubieumoi\MauMoThe.docx
    ↓
   [KHÔNG CÓ]
    ↓
2. Tìm trong subdirectories:
   - C:\maubieumoi\ATM\MauMoThe.docx ❌
   - C:\maubieumoi\DICHVU\MauMoThe.docx ✅ TÌM THẤY!
    ↓
3. Đọc file từ DICHVU\MauMoThe.docx
    ↓
4. Cache vào media\templates\docx\MauMoThe.docx
    ↓
✅ Hoàn tất!
```

---

## 🔧 **SETUP (Rất Đơn Giản):**

### **Bước 1: Pull code mới nhất**

```powershell
git pull origin claude/fix-template-expiration-01Y5u8fTmYHu3bk2Ln9gmPrR
```

**Code đã được update để hỗ trợ recursive search trong subdirectories!**

---

### **Bước 2: Copy toàn bộ folder maubieumoi**

**Cách 1: Dùng File Explorer** (Dễ nhất)

1. Copy toàn bộ folder `maubieumoi` (bao gồm cả subdirectories)
2. Paste vào `C:\`

**Kết quả:**
```
C:\maubieumoi\
├── ATM\
├── DICHVU\
├── DIENTOAN\
└── KETOAN\
    ├── TKDV\
    └── TKTT\
```

**Cách 2: Dùng PowerShell**

```powershell
# Copy toàn bộ folder với subdirectories
Copy-Item "D:\MauBieu\maubieumoi" -Destination "C:\" -Recurse
```

---

### **Bước 3: Verify**

```powershell
# Kiểm tra subdirectories đã copy
Get-ChildItem "C:\maubieumoi" -Directory

# Kết quả mong đợi:
# ATM
# DICHVU
# DIENTOAN
# KETOAN
```

---

### **Bước 4: Kiểm tra templates**

```powershell
# Đếm tất cả file .docx (bao gồm subdirectories)
(Get-ChildItem "C:\maubieumoi" -Filter "*.docx" -Recurse).Count

# List tất cả templates
Get-ChildItem "C:\maubieumoi\*.docx" -Recurse | Select-Object FullName
```

---

### **Bước 5: Test**

```powershell
python test_hybrid_storage.py
```

**Kết quả:**
```
✓ Test 1: Configuration
   Offline path: C:\maubieumoi
   Auto-cache enabled: True

✓ Test 2: Offline folder
   Offline folder exists: True
   Subdirectories found: ATM, DICHVU, DIENTOAN, KETOAN

✓ Test 3: Recursive search
   Templates found (including subdirs): 45

✅ All tests passed!
```

---

## 💡 **Ưu Điểm Phương Án 1:**

### ✅ **1. Tự động tìm kiếm**
Không cần config gì thêm, chỉ cần đặt file vào folder và hệ thống tự tìm.

### ✅ **2. Giữ nguyên cấu trúc**
Bạn giữ nguyên cách tổ chức folder hiện tại.

### ✅ **3. Dễ quản lý**
- ATM templates → Folder ATM
- DICHVU templates → Folder DICHVU
- Rõ ràng, dễ nhớ

### ✅ **4. Dễ thêm/sửa/xóa**
Chỉ cần copy/delete file trong folder tương ứng.

---

## ⚠️ **Lưu Ý Quan Trọng:**

### **1. Tên file phải UNIQUE**

❌ **KHÔNG NÊN:**
```
C:\maubieumoi\
├── DICHVU\
│   └── MauMoThe.docx    ← Trùng tên!
└── KETOAN\TKDV\
    └── MauMoThe.docx    ← Trùng tên!
```

→ Hệ thống sẽ chỉ lấy file tìm thấy **đầu tiên**!

✅ **NÊN:**
```
C:\maubieumoi\
├── DICHVU\
│   └── MauMoThe_DichVu.docx
└── KETOAN\TKDV\
    └── MauMoThe_KeToan.docx
```

---

### **2. Performance**

- Nếu có **quá nhiều** file/folder (hàng nghìn) → Tìm kiếm có thể chậm
- **Giải pháp:** Đặt templates hay dùng ở root folder

---

## 🎯 **Workflow Khi Thêm Template Mới:**

### **Ví dụ: Thêm template "Mở tài khoản thanh toán"**

**Bước 1:** Copy file vào folder phù hợp
```powershell
Copy-Item "MauMoTKTT.docx" -Destination "C:\maubieumoi\KETOAN\TKTT\"
```

**Bước 2:** Tạo Template trong Django Admin
1. Vào: http://localhost:8000/admin
2. Templates → Add Template
3. Tên: "Mở tài khoản thanh toán"
4. File: `MauMoTKTT.docx` (chỉ cần nhập tên file)
5. Save

**Bước 3:** Test
- Generate document từ template mới
- Check logs:
  ```
  ✓ Template found in offline folder: C:\maubieumoi\KETOAN\TKTT\MauMoTKTT.docx
  ✓ Cached to media folder: ...\media\templates\docx\MauMoTKTT.docx
  ```

✅ **Xong!** Không cần config path hay gì cả!

---

## 🆚 **So Sánh Với Phương Án 2:**

| Tiêu chí | Phương án 1 (Auto) | Phương án 2 (Manual Path) |
|----------|-------------------|--------------------------|
| **Setup** | ⭐⭐⭐⭐⭐ Rất dễ | ⭐⭐ Phức tạp |
| **Thêm template mới** | ⭐⭐⭐⭐⭐ Chỉ copy file | ⭐⭐⭐ Phải nhập path |
| **Tên file trùng** | ❌ Conflict | ✅ OK (khác path) |
| **Performance** | ⭐⭐⭐⭐ Tốt | ⭐⭐⭐⭐⭐ Nhanh hơn |
| **Khuyên dùng** | ✅ **YES** | ❌ Chỉ khi cần |

---

## 🔍 **Debug: Tìm Template Đang Ở Đâu**

Nếu template không hoạt động, check path:

```powershell
# Tìm file trong tất cả subdirectories
Get-ChildItem "C:\maubieumoi" -Filter "MauMoThe.docx" -Recurse

# Kết quả:
# C:\maubieumoi\DICHVU\MauMoThe.docx
# C:\maubieumoi\KETOAN\TKDV\MauMoThe.docx  ← Trùng tên!
```

**Giải pháp:** Đổi tên file để unique.

---

## 📋 **Checklist Setup:**

- [ ] Pull code mới nhất
- [ ] Copy folder maubieumoi vào C:\ (bao gồm subdirectories)
- [ ] Verify subdirectories: `Get-ChildItem "C:\maubieumoi" -Directory`
- [ ] Count templates: `(Get-ChildItem "C:\maubieumoi\*.docx" -Recurse).Count`
- [ ] Test: `python test_hybrid_storage.py`
- [ ] Check tên file không trùng
- [ ] Run server: `python manage.py runserver`
- [ ] Test generate document

---

## ✨ **Kết Luận:**

**DÙNG PHƯƠNG ÁN 1** vì:
- ✅ Đơn giản, không cần config
- ✅ Tự động tìm trong subdirectories
- ✅ Giữ nguyên cấu trúc folder hiện tại
- ✅ Dễ thêm/sửa/xóa templates

**Chỉ cần:**
1. Copy folder maubieumoi vào C:\
2. Run server
3. Sử dụng!

---

## 📞 **Nếu Cần Hỗ Trợ:**

Chạy debug script:

```powershell
# Tạo file debug.ps1
@"
Write-Host "=== Debug Maubieumoi Subdirectories ===" -ForegroundColor Cyan

Write-Host "`n1. Checking offline path..." -ForegroundColor Yellow
if (Test-Path "C:\maubieumoi") {
    Write-Host "   ✓ C:\maubieumoi exists" -ForegroundColor Green
} else {
    Write-Host "   ✗ C:\maubieumoi NOT FOUND" -ForegroundColor Red
    exit 1
}

Write-Host "`n2. Listing subdirectories..." -ForegroundColor Yellow
Get-ChildItem "C:\maubieumoi" -Directory | ForEach-Object {
    Write-Host "   - $($_.Name)" -ForegroundColor White
}

Write-Host "`n3. Counting templates (recursive)..." -ForegroundColor Yellow
$count = (Get-ChildItem "C:\maubieumoi\*.docx" -Recurse).Count
Write-Host "   Total templates: $count" -ForegroundColor White

Write-Host "`n4. Listing all templates..." -ForegroundColor Yellow
Get-ChildItem "C:\maubieumoi\*.docx" -Recurse | ForEach-Object {
    $relative = $_.FullName -replace [regex]::Escape("C:\maubieumoi\"), ""
    Write-Host "   - $relative" -ForegroundColor White
}

Write-Host "`n5. Checking for duplicate names..." -ForegroundColor Yellow
$files = Get-ChildItem "C:\maubieumoi\*.docx" -Recurse
$groups = $files | Group-Object Name
$duplicates = $groups | Where-Object { $_.Count -gt 1 }

if ($duplicates) {
    Write-Host "   ⚠ Found duplicate names:" -ForegroundColor Yellow
    foreach ($dup in $duplicates) {
        Write-Host "   - $($dup.Name) ($($dup.Count) copies)" -ForegroundColor Red
        $dup.Group | ForEach-Object {
            $relative = $_.FullName -replace [regex]::Escape("C:\maubieumoi\"), ""
            Write-Host "     → $relative" -ForegroundColor White
        }
    }
} else {
    Write-Host "   ✓ No duplicates found" -ForegroundColor Green
}

Write-Host "`n=== Done ===" -ForegroundColor Cyan
"@ | Out-File -FilePath "debug.ps1" -Encoding UTF8

# Chạy
.\debug.ps1
```

**Copy output và gửi cho tôi nếu cần hỗ trợ!**

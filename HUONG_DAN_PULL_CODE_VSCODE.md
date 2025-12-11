# Hướng Dẫn Pull Code Trong VSCode - Fix Template Expiration

## 🎯 Quick Start (Nhanh Nhất)

### **Option 1: Dùng Terminal trong VSCode**

1. **Mở Terminal trong VSCode:**
   - Nhấn `Ctrl + ~` (phím backtick)
   - Hoặc: Menu → Terminal → New Terminal

2. **Chạy lệnh pull:**
   ```bash
   git pull origin claude/django-word-template-generator-011CUfkKT1HZ7HQosuoKML8r
   ```

3. **Nếu đã up to date:**
   ```
   ✓ Already up to date
   ```

---

### **Option 2: Dùng GUI VSCode**

#### **Bước 1: Mở Source Control**
- Nhấn `Ctrl+Shift+G` (Windows/Linux)
- Hoặc `Cmd+Shift+G` (Mac)
- Hoặc click icon ![Source Control Icon](như cái nhánh cây) ở thanh bên trái

#### **Bước 2: Pull Code**
- Click vào icon `...` (3 chấm) ở góc trên phải Source Control
- Chọn **"Pull"** hoặc **"Pull from..."**
- Nếu chọn "Pull from...", chọn branch `claude/django-word-template-generator-011CUfkKT1HZ7HQosuoKML8r`

---

## 🔴 Xử Lý Lỗi "Untracked Files Would Be Overwritten"

### **Nếu gặp lỗi này:**
```
error: The following untracked working tree files would be overwritten by merge:
	payroll_statistics/migrations/0003_rename_payroll_sta_transac_...
```

### **Giải pháp:**

#### **Cách 1: Dùng Terminal VSCode (KHUYÊN DÙNG)**

```bash
# Stash các thay đổi chưa commit
git stash

# Pull code
git pull origin claude/django-word-template-generator-011CUfkKT1HZ7HQosuoKML8r

# Apply lại stash (nếu cần)
git stash pop
```

#### **Cách 2: Stage và Commit trước khi pull**

**Trong Source Control panel:**
1. Click icon `+` bên cạnh file để Stage
2. Nhập commit message (ví dụ: "WIP: Save current changes")
3. Click ✓ để Commit
4. Sau đó Pull bình thường

**Hoặc dùng Terminal:**
```bash
git add .
git commit -m "WIP: Save current changes"
git pull origin claude/django-word-template-generator-011CUfkKT1HZ7HQosuoKML8r
```

#### **Cách 3: Xóa file conflict và pull lại**

⚠️ **CHỈ làm nếu chắc chắn file không cần thiết**

```bash
rm payroll_statistics/migrations/0003_rename_payroll_sta_transac_*
git pull origin claude/django-word-template-generator-011CUfkKT1HZ7HQosuoKML8r
```

---

## 🎨 Resolve Merge Conflicts trong VSCode

### **Khi có conflict, VSCode sẽ hiện:**

```
<<<<<<< HEAD (Current Change)
[Code hiện tại của bạn]
=======
[Code từ remote]
>>>>>>> branch-name (Incoming Change)
```

### **VSCode cung cấp các nút:**

1. **Accept Current Change** - Giữ code của bạn
2. **Accept Incoming Change** - Lấy code từ remote
3. **Accept Both Changes** - Giữ cả 2
4. **Compare Changes** - Xem diff để quyết định

### **Sau khi resolve:**

1. Lưu file (`Ctrl+S`)
2. Stage changes (click icon `+`)
3. Commit với message: "Merge branch xxx"
4. Done!

---

## 📊 Kiểm Tra Status

### **Trong Source Control Panel:**

- **M** (Modified) - File đã sửa
- **U** (Untracked) - File mới chưa add
- **C** (Conflict) - File có conflict
- **D** (Deleted) - File đã xóa

### **Trong Terminal:**

```bash
# Xem status
git status

# Xem branch hiện tại
git branch

# Xem commits gần đây
git log --oneline -5
```

---

## 🚀 Workflow Hoàn Chỉnh

### **Flow chuẩn để pull code:**

```
1. Stash changes (nếu có thay đổi chưa commit)
   → Ctrl+Shift+P → "Git: Stash"

2. Pull code
   → Source Control → ... → Pull

3. Resolve conflicts (nếu có)
   → Click vào file conflict → Chọn Accept Current/Incoming

4. Apply stash lại (nếu đã stash)
   → Ctrl+Shift+P → "Git: Apply Stash"

5. Verify
   → Xem Source Control panel: Không còn changes
```

---

## 🎯 Shortcuts Hữu Ích Trong VSCode

| Phím tắt | Chức năng |
|----------|-----------|
| `Ctrl+Shift+G` | Mở Source Control |
| `Ctrl+~` | Mở Terminal |
| `Ctrl+Shift+P` | Mở Command Palette |
| `Ctrl+K Ctrl+O` | Mở folder |
| `F5` | Debug/Run |
| `Ctrl+B` | Toggle Sidebar |

---

## 💡 Tips

### **Sync với Remote thường xuyên:**
1. **Fetch** trước khi pull để xem changes:
   ```
   Source Control → ... → Fetch
   ```

2. **Compare changes** trước khi merge:
   ```
   Click vào branch name ở status bar (góc dưới trái)
   → Xem diff với remote branch
   ```

### **Tránh conflicts:**
- Pull thường xuyên trước khi làm việc
- Commit nhỏ và thường xuyên
- Communicate với team về files đang sửa

---

## 🆘 Troubleshooting

### **Pull bị stuck/chậm?**
- Hủy: `Ctrl+C` trong Terminal
- Hoặc: VSCode → Git panel → Click icon "Cancel"

### **Cannot pull: Permission denied?**
- Check SSH keys: `ssh -T git@github.com`
- Hoặc dùng HTTPS thay vì SSH

### **Detached HEAD state?**
```bash
git checkout claude/fix-template-expiration-01Y5u8fTmYHu3bk2Ln9gmPrR
git pull
```

---

## ✅ Trạng Thái Hiện Tại Của Project

```
Branch: claude/fix-template-expiration-01Y5u8fTmYHu3bk2Ln9gmPrR
Status: ✅ Up to date (commit 8314f40)
PR #240: ✅ Merged
```

**Bạn có thể:**
1. Pull về để sync code
2. Chạy server: `python3 manage.py runserver`
3. Test hybrid storage: `python3 test_hybrid_storage.py`

---

**Nếu cần hỗ trợ thêm, hãy cho tôi biết lỗi cụ thể bạn gặp! 😊**

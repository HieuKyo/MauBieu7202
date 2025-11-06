# HƯỚNG DẪN TẠO CHECKBOX BẰNG CONTENT CONTROL TRONG WORD

## 📋 GIỚI THIỆU

Content Control Checkbox cho phép bạn:
- ✅ **Tích trực tiếp trong Word** - Nhìn thấy ngay kết quả
- ✅ **Không cần viết code Jinja2** - Đơn giản hơn nhiều
- ✅ **Chỉnh sửa dễ dàng** - Nhấp chuột để tích/bỏ tích
- ✅ **Tự động cập nhật** - Hệ thống tự động điền checkbox khi tạo mẫu biểu

---

## 🎯 BƯỚC 1: BẬT DEVELOPER TAB TRONG WORD

### **Với Word 2016/2019/2021/365:**

1. Mở Microsoft Word
2. Click **File** (góc trái trên)
3. Click **Options** (cuối danh sách bên trái)
4. Click **Customize Ribbon** (menu bên trái)
5. Ở cột bên phải, tìm và **tích vào ô "Developer"**
6. Click **OK**

Sau khi bật, bạn sẽ thấy tab **Developer** xuất hiện trên ribbon (thanh menu trên cùng)

### **Với Word 2013:**

Tương tự như trên

### **Hình minh họa:**

```
File → Options → Customize Ribbon

┌─────────────────────────────────────┐
│ ☐ Home                              │
│ ☐ Insert                            │
│ ☐ Design                            │
│ ☑ Developer  ← Tích vào đây         │
│ ☐ Mailings                          │
└─────────────────────────────────────┘
```

---

## 🎯 BƯỚC 2: TẠO CHECKBOX TRONG TEMPLATE

### **2.1. Insert Checkbox Content Control**

1. **Mở file template Word** của bạn
2. **Đặt con trỏ** ở vị trí muốn thêm checkbox
3. Click tab **Developer** trên ribbon
4. Trong nhóm **Controls**, click nút **Check Box Content Control**
   - Icon có hình: ☐ (ô vuông)
   - Hoặc tìm text "Check Box Content Control"

→ Một checkbox sẽ xuất hiện: ☐

### **2.2. Gán Tag cho Checkbox**

**Quan trọng:** Tag name phải khớp với tên biến trong database!

1. **Click vào checkbox** vừa tạo (để chọn nó)
2. Trong tab **Developer**, click nút **Properties** (nhóm Controls)
3. Cửa sổ **Content Control Properties** hiện ra:

   ```
   ┌────────────────────────────────────────┐
   │ Content Control Properties             │
   ├────────────────────────────────────────┤
   │ Title: Nam                             │  ← Tên hiển thị
   │ Tag: gioi_tinh_nam                     │  ← TÊN BIẾN (quan trọng!)
   │                                        │
   │ ☑ Content control cannot be deleted   │
   │ ☐ Contents cannot be edited           │
   │                                        │
   │              [OK]    [Cancel]          │
   └────────────────────────────────────────┘
   ```

4. **Nhập thông tin:**
   - **Title**: Tên mô tả (ví dụ: "Nam", "Nông dân", "SMS Banking")
   - **Tag**: Tên biến trong database (ví dụ: `gioi_tinh_nam`, `nghe_nghiep_nong_dan`, `dv_sms_banking`)

5. **Tích vào:** ☑ Content control cannot be deleted (khuyến nghị)
6. Click **OK**

### **2.3. Thêm Label bên cạnh Checkbox**

Sau khi tạo checkbox, gõ text label bên cạnh:

```
☐ Nam     ☐ Nữ
```

**Lưu ý:** Checkbox và label là 2 thành phần riêng biệt

---

## 📝 BƯỚC 3: TÊN BIẾN (TAG) CẦN DÙNG

### **3.1. Giới tính**

| Checkbox Label | Tag Name | Giá trị trong DB |
|----------------|----------|------------------|
| ☐ Nam | `gioi_tinh_nam` | `gioi_tinh == 'Nam'` |
| ☐ Nữ | `gioi_tinh_nu` | `gioi_tinh == 'Nữ'` |

**Cách tạo:**
1. Insert 2 checkbox
2. Checkbox 1: Title = "Nam", Tag = `gioi_tinh_nam`
3. Checkbox 2: Title = "Nữ", Tag = `gioi_tinh_nu`
4. Gõ text "Nam" sau checkbox 1, "Nữ" sau checkbox 2

**Kết quả trong template:**
```
☐ Nam     ☐ Nữ
```

---

### **3.2. Loại tài khoản**

| Checkbox Label | Tag Name |
|----------------|----------|
| ☐ Tài khoản ngẫu nhiên | `tk_ngau_nhien` |
| ☐ Tài khoản theo yêu cầu | `tk_theo_yeu_cau` |

---

### **3.3. Loại thẻ**

| Checkbox Label | Tag Name |
|----------------|----------|
| ☐ Thẻ Ghi nợ nội địa | `the_ghi_no_noi_dia` |
| ☐ Thẻ Ghi nợ quốc tế | `the_ghi_no_quoc_te` |
| ☐ Thẻ tín dụng | `the_tin_dung` |

---

### **3.4. Hạng thẻ**

| Checkbox Label | Tag Name |
|----------------|----------|
| ☐ Hạng chuẩn | `the_hang_chuan` |
| ☐ Hạng vàng | `the_hang_vang` |
| ☐ Hạng bạch kim | `the_hang_bach_kim` |

---

### **3.5. Phát hành thẻ**

| Checkbox Label | Tag Name |
|----------------|----------|
| ☐ Phát hành lần đầu | `phat_hanh_lan_dau` |
| ☐ Phát hành lại | `phat_hanh_lai` |

---

### **3.6. Dịch vụ ngân hàng điện tử**

| Checkbox Label | Tag Name |
|----------------|----------|
| ☐ SMS Banking | `dv_sms_banking` |
| ☐ E-Mobile Banking | `dv_e_mobile` |
| ☐ Agribank Plus | `dv_bankplus` |
| ☐ E-Commerce | `dv_e_commerce` |
| ☐ Soft OTP | `dv_soft_otp` |
| ☐ Smart OTP | `dv_smart_otp` |
| ☐ Internet Banking | `dv_retail_ebanking` |

---

### **3.7. Dịch vụ thu hộ**

| Checkbox Label | Tag Name |
|----------------|----------|
| ☐ Tiền điện | `dv_thu_ho_tien_dien` |
| ☐ Tiền nước | `dv_thu_ho_tien_nuoc` |
| ☐ Viễn thông | `dv_thu_ho_vien_thong` |
| ☐ Học phí | `dv_thu_ho_hoc_phi` |
| ☐ Bảo hiểm | `dv_thu_ho_bao_hiem` |

---

### **3.8. Kênh giao dịch**

| Checkbox Label | Tag Name |
|----------------|----------|
| ☐ Mobile Banking | `kenh_mobile` |
| ☐ Internet Banking | `kenh_internet` |

---

## 🎯 BƯỚC 4: VÍ DỤ THỰC TẾ - TẠO FORM ĐĂNG KÝ

### **Ví dụ 1: Phần giới tính**

**Trong Word template:**

1. Gõ text: "Giới tính: "
2. Insert checkbox, set Tag = `gioi_tinh_nam`, gõ " Nam"
3. Thêm khoảng trắng
4. Insert checkbox, set Tag = `gioi_tinh_nu`, gõ " Nữ"

**Kết quả:**
```
Giới tính: ☐ Nam     ☐ Nữ
```

**Khi generate mẫu biểu:**
- Nếu khách hàng là Nam → ☑ Nam     ☐ Nữ
- Nếu khách hàng là Nữ → ☐ Nam     ☑ Nữ

---

### **Ví dụ 2: Phần dịch vụ**

**Trong Word template:**

```
ĐĂNG KÝ DỊCH VỤ NGÂN HÀNG ĐIỆN TỬ:

☐ SMS Banking
☐ E-Mobile Banking
☐ Agribank Plus
☐ Soft OTP
```

**Cách tạo:**

1. Gõ "ĐĂNG KÝ DỊCH VỤ NGÂN HÀNG ĐIỆN TỬ:"
2. Xuống dòng, insert checkbox, Tag = `dv_sms_banking`, gõ " SMS Banking"
3. Xuống dòng, insert checkbox, Tag = `dv_e_mobile`, gõ " E-Mobile Banking"
4. Xuống dòng, insert checkbox, Tag = `dv_bankplus`, gõ " Agribank Plus"
5. Xuống dòng, insert checkbox, Tag = `dv_soft_otp`, gõ " Soft OTP"

**Khi generate mẫu biểu:**
```
ĐĂNG KÝ DỊCH VỤ NGÂN HÀNG ĐIỆN TỬ:

☑ SMS Banking          ← Khách hàng chọn
☑ E-Mobile Banking     ← Khách hàng chọn
☐ Agribank Plus        ← Khách hàng không chọn
☑ Soft OTP             ← Khách hàng chọn
```

---

## 🔍 BƯỚC 5: KIỂM TRA TAG NAME

### **Cách xem Tag của checkbox:**

1. Click vào checkbox
2. Tab **Developer** → nút **Properties**
3. Xem trường **Tag**

### **Cách sửa Tag nếu nhập sai:**

1. Click vào checkbox
2. Tab **Developer** → nút **Properties**
3. Sửa lại trường **Tag**
4. Click **OK**

---

## ⚙️ BƯỚC 6: HỆ THỐNG TỰ ĐỘNG XỬ LÝ

Khi bạn:
1. ✅ **Upload template** lên hệ thống
2. ✅ **Nhập thông tin khách hàng** vào form
3. ✅ **Tích chọn dịch vụ** mong muốn
4. ✅ **Nhấn "Tạo mẫu biểu"**

→ Hệ thống sẽ **TỰ ĐỘNG**:
- Đọc tất cả checkbox có Tag trong template
- So khớp Tag với dữ liệu khách hàng
- Tích checkbox nếu giá trị = True/đúng
- Bỏ tích checkbox nếu giá trị = False/sai

**Bạn không cần làm gì thêm!**

---

## 🎨 BƯỚC 7: ĐỊNH DẠNG CHECKBOX (TÙY CHỈNH)

### **Thay đổi ký tự checkbox:**

1. Click vào checkbox
2. Tab **Developer** → **Properties**
3. Click nút **Change...** bên cạnh "Checked symbol:"
4. Chọn font và ký tự mong muốn:
   - **Wingdings**: ☑ (mã 254), ☐ (mã 168)
   - **Segoe UI Symbol**: ✓ ✔ ✗ ✘
5. Click **OK**

### **Khuyến nghị:**

Dùng mặc định của Word (checkbox chuẩn) để đảm bảo tương thích tốt nhất.

---

## ⚠️ LƯU Ý QUAN TRỌNG

### **1. Tag name PHẢI KHỚP với biến trong database**

❌ **Sai:**
- Tag = `gioi_tinh` (trong DB không có biến này)
- Tag = `GioiTinhNam` (phải viết thường, dùng underscore)

✅ **Đúng:**
- Tag = `gioi_tinh_nam` (khớp với biến trong Customer model)

### **2. Không xóa Content Control**

Nếu bạn xóa nhầm:
1. Undo (Ctrl+Z)
2. Hoặc tạo lại checkbox mới

### **3. Không chỉnh sửa XML trực tiếp**

Luôn dùng Properties dialog để thay đổi Tag/Title.

### **4. Backup template trước khi chỉnh sửa**

Copy file template sang file khác trước khi thay đổi lớn.

---

## 🐛 TROUBLESHOOTING

### **Vấn đề 1: Checkbox không tự động tích khi generate**

**Nguyên nhân:** Tag name không khớp với biến trong database

**Giải pháp:**
1. Click checkbox → Properties
2. Kiểm tra Tag name
3. So sánh với bảng tên biến ở trên
4. Sửa lại cho đúng

---

### **Vấn đề 2: Không tìm thấy tab Developer**

**Giải pháp:** Xem lại BƯỚC 1 để bật Developer Tab

---

### **Vấn đề 3: Checkbox biến mất sau khi generate**

**Nguyên nhân:** Content Control bị xóa do lỗi template

**Giải pháp:**
1. Mở lại template gốc
2. Kiểm tra checkbox vẫn còn không
3. Tích vào "Content control cannot be deleted" trong Properties
4. Upload lại template

---

### **Vấn đề 4: File Word bị lỗi "cannot open this file"**

**Nguyên nhân:** Template có Jinja2 syntax lỗi

**Giải pháp:**
```bash
# Chạy script validation
python validate_template.py path/to/template.docx
```

Nếu có lỗi, xóa tất cả Jinja2 syntax ({% if %}, {{ }}) trong template và chỉ dùng Content Control.

---

## 📚 VÍ DỤ TEMPLATE HOÀN CHỈNH

### **Template: Đơn đăng ký tài khoản + thẻ ATM**

```
                    NGÂN HÀNG NÔNG NGHIỆP VÀ PHÁT TRIỂN NÔNG THÔN VIỆT NAM
                           {{ ten_chi_nhanh }}
             ------------------------------------------

                  ĐƠN ĐĂNG KÝ TÀI KHOẢN VÀ THẺ ATM

{{ dia_danh }}, ngày {{ ngay_hien_tai }}

════════════════════════════════════════════════════════════════════

PHẦN I: THÔNG TIN KHÁCH HÀNG

Họ và tên: {{ ho_ten }}                                CMND/CCCD: {{ cmnd }}
Ngày sinh: {{ ngay_sinh }}                              Giới tính: ☐ Nam   ☐ Nữ
                                                                    ↑Tag: gioi_tinh_nam
                                                                          ↑Tag: gioi_tinh_nu

Điện thoại: {{ dien_thoai }}                            Email: {{ email }}
Địa chỉ: {{ dia_chi }}

════════════════════════════════════════════════════════════════════

PHẦN II: ĐĂNG KÝ TÀI KHOẢN

Loại tài khoản:
  ☐ Tài khoản ngẫu nhiên            (Tag: tk_ngau_nhien)
  ☐ Tài khoản theo yêu cầu          (Tag: tk_theo_yeu_cau)

════════════════════════════════════════════════════════════════════

PHẦN III: ĐĂNG KÝ THẺ

Loại thẻ:
  ☐ Thẻ Ghi nợ nội địa              (Tag: the_ghi_no_noi_dia)

Hạng thẻ:
  ☐ Hạng chuẩn                      (Tag: the_hang_chuan)
  ☐ Hạng vàng                       (Tag: the_hang_vang)

Phát hành:
  ☐ Lần đầu                         (Tag: phat_hanh_lan_dau)
  ☐ Phát hành lại                   (Tag: phat_hanh_lai)

════════════════════════════════════════════════════════════════════

PHẦN IV: DỊCH VỤ NGÂN HÀNG ĐIỆN TỬ

☐ SMS Banking                       (Tag: dv_sms_banking)
☐ E-Mobile Banking                  (Tag: dv_e_mobile)
☐ Agribank Plus                     (Tag: dv_bankplus)
☐ Soft OTP                          (Tag: dv_soft_otp)

════════════════════════════════════════════════════════════════════

PHẦN V: DỊCH VỤ THU HỘ

☐ Tiền điện                         (Tag: dv_thu_ho_tien_dien)
☐ Tiền nước                         (Tag: dv_thu_ho_tien_nuoc)
☐ Viễn thông                        (Tag: dv_thu_ho_vien_thong)

════════════════════════════════════════════════════════════════════

                                                    Ngày {{ ngay_hien_tai }}
                                                  Người đề nghị
                                                 (Ký và ghi rõ họ tên)




                                                  {{ ho_ten }}
```

---

## 🎯 TÓM TẮT NHANH

1. **Bật Developer Tab**: File → Options → Customize Ribbon → ✓ Developer
2. **Insert Checkbox**: Developer Tab → Check Box Content Control
3. **Set Tag**: Click checkbox → Properties → Nhập Tag name (ví dụ: `gioi_tinh_nam`)
4. **Thêm Label**: Gõ text bên cạnh checkbox (ví dụ: "Nam")
5. **Upload Template**: Lên hệ thống
6. **Tạo mẫu biểu**: Hệ thống tự động tích checkbox

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề:
1. Kiểm tra Tag name có đúng không (xem bảng danh sách Tag)
2. Chạy `python validate_template.py template.docx` để kiểm tra lỗi
3. Liên hệ support nếu cần hỗ trợ thêm

---

**Phiên bản:** 1.0
**Ngày tạo:** 06/11/2025
**Người viết:** Claude AI Assistant

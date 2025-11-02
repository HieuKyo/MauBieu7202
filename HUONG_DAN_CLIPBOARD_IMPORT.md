# ⚡ Hướng dẫn Nhanh: Import từ Clipboard AGRIBANK

## 🎯 Cách NHANH NHẤT (Khuyến nghị)

### Bước 1: Copy dữ liệu từ AGRIBANK

1. Mở hệ thống **AGRIBANK**
2. Tìm thông tin khách hàng cần import
3. **Chọn 2 dòng:**
   - **Dòng 1**: Header (custno, nm, nmloc, shrtnm, ...)
   - **Dòng 2**: Dữ liệu khách hàng
4. **Copy** (Ctrl+C)

```
custno	nm	shrtnm	nicknm	nmloc	shrtnmloc	nicknmloc	custtpcd	custdtltpcd	name_4	name_3	name_2	name_1	bkcd	regno	passno	dlno	telnoctry	telnoarea	telno	telnoextn	addrtpcd	addr1	addr2	addr3	addr1loc	addr2loc	addr3loc	statescd	refno	estno	busno	stscd	issueby1	issuedt1	issueby2	issuedt2	issueby3	issuedt3	issueby4	issuedt4	issueby5	issuedt5	issueby6	issuedt6	taxno	province	district	commune_ward	firstdt	usridop1	incrdt	empno	rltnmngrempno	emailaddr	ctrycdnatl	ctrycdnatl2	profnm
7202000699174	TRAN NGOC THUY	TRAN NGOC THUY		Trần Ngọc Thủy	Trần Ngọc Thủy		Cá nhân	Tư nhân	0766939319	Nữ	1701	19700101		022189125							Nơi ở	P1 Quận 3 TPHCM			P1 Quận 3 TPHCM			  	022189125			Bình thường	145	20010417		        		        		        		        		        		500	50005	5000501		GRATTHAO			        		VN	  	Công chức viên chức
```

### Bước 2: Import vào hệ thống

1. Vào trang **"Khách hàng"**
2. Nhấn nút **"Import AGRIBANK"** (màu xanh dương)
3. Modal hiện ra → Tab **"Paste từ Clipboard"** (đã được chọn sẵn)
4. Click vào **ô textarea** lớn màu trắng
5. **Paste** dữ liệu (Ctrl+V)
6. Nhấn nút **"Import"**
7. Xem kết quả!

### ✅ Đó là tất cả!

Không cần:
- ❌ Lưu file
- ❌ Encoding UTF-8
- ❌ Chọn file
- ❌ Notepad

Chỉ cần:
- ✅ Copy từ AGRIBANK
- ✅ Paste vào textarea
- ✅ Nhấn Import

---

## 📊 Dữ liệu được Import

### Các trường chính:

| Thông tin | Cột AGRIBANK | Vị trí | Ghi chú |
|-----------|--------------|--------|---------|
| Mã KH | custno | Cột 1 | 7202000699174 |
| Họ tên | nmloc | Cột 5 | Trần Ngọc Thủy |
| CMND/CCCD | regno | Cột 15 | 022189125 |
| Ngày sinh | name_1 | Cột 13 | 19700101 |
| Giới tính | name_3 | Cột 11 | Nữ |
| SĐT | name_4 | Cột 10 | 0766939319 |
| Địa chỉ | addr1loc | Cột 26 | P1 Quận 3 TPHCM |
| Ngày cấp | issuedt1 | Cột 35 | 20010417 |
| Nơi cấp (mã) | issueby1 | Cột 34 | 145 |
| **Nghề nghiệp** | **profnm** | **Cột 58** | **Công chức viên chức** |
| Email | emailaddr | Cột 55 | |
| Mã tỉnh | province | Cột 46 | 500 |
| Mã quận | district | Cột 47 | 50005 |
| Mã phường | commune_ward | Cột 48 | 5000501 |
| Quốc tịch | ctrycdnatl | Cột 56 | VN |

---

## ⚠️ Lưu ý quan trọng

### ✅ Phải copy CẢ 2 dòng:

1. **Dòng header** (custno, nm, nmloc, ...)
2. **Dòng dữ liệu** (7202000699174, TRAN NGOC THUY, ...)

### ❌ Không được:

- Copy chỉ 1 dòng (thiếu header)
- Copy nhiều khách hàng nhưng thiếu header
- Copy từ Excel đã format

### ✅ Nên:

- Copy trực tiếp từ AGRIBANK
- Giữ nguyên format Tab-separated
- Copy ít nhất 2 dòng

---

## 🎬 Ví dụ minh họa

### Input (trong textarea sau khi paste):

```
custno	nmloc	regno	name_1	name_3	name_4	issuedt1	issueby1	addr1loc	profnm
7202000699174	Trần Ngọc Thủy	022189125	19700101	Nữ	0766939319	20010417	145	P1 Quận 3 TPHCM	Công chức viên chức
```

### Output (trong hệ thống):

- **Mã KH**: 7202000699174
- **Họ tên**: Trần Ngọc Thủy
- **CMND**: 022189125
- **Ngày sinh**: 01/01/1970
- **Giới tính**: Nữ
- **SĐT**: 0766939319
- **Ngày cấp**: 17/04/2001
- **Nơi cấp**: Cục Cảnh sát ĐKQL cư trú và DLQG về dân cư
- **Địa chỉ**: P1 Quận 3 TPHCM
- **Nghề nghiệp**: Công chức viên chức ✨

---

## 🚨 Xử lý lỗi

### Lỗi: "Dữ liệu phải có ít nhất 2 dòng"

**Nguyên nhân**: Chỉ copy 1 dòng hoặc thiếu header

**Giải pháp**:
1. Quay lại AGRIBANK
2. Chọn từ dòng header đến dòng dữ liệu
3. Copy cả 2 dòng
4. Paste lại

### Lỗi: "Thiếu họ tên"

**Nguyên nhân**: Cột `nmloc` (cột 5) bị trống

**Giải pháp**: Kiểm tra dữ liệu trong AGRIBANK

### Lỗi: "Thiếu số CMND/CCCD"

**Nguyên nhân**: Cột `regno` (cột 15) bị trống

**Giải pháp**: Kiểm tra CMND/CCCD đã được nhập trong AGRIBANK chưa

---

## 💡 Tips & Tricks

### 1. Import nhiều khách hàng

Có thể copy nhiều dòng cùng lúc:

```
custno	nmloc	regno...
7202000699174	Trần Ngọc Thủy	022189125...
7202000699175	Nguyễn Văn A	012345678...
7202000699176	Lê Thị B	098765432...
```

→ Hệ thống sẽ import tất cả!

### 2. Cập nhật thông tin

Nếu CMND đã tồn tại → Hệ thống **tự động cập nhật** thông tin

### 3. Kiểm tra kết quả

Sau khi import thành công:
- Số **Khách hàng mới** (màu xanh)
- Số **Đã cập nhật** (màu xanh dương)
- Số **Lỗi** (màu đỏ)

Nhấn **"Tải lại trang"** để xem danh sách cập nhật

---

## 🆚 So sánh 2 phương thức

| Tính năng | Paste Clipboard ⚡ | Upload File 📁 |
|-----------|-------------------|----------------|
| Số bước | 3 bước | 5 bước |
| Cần lưu file | ❌ Không | ✅ Phải lưu |
| Cần Notepad | ❌ Không | ✅ Cần |
| Encoding UTF-8 | ❌ Tự động | ⚠️ Phải chọn |
| Tốc độ | ⚡ Nhanh nhất | 🐢 Chậm hơn |
| Khuyến nghị | ✅ Dùng cái này! | Khi cần lưu file |

---

## 📱 Sử dụng trên Dashboard

**Lưu ý**: Hiện tại chỉ có trên trang **"Khách hàng"**

Để import từ Dashboard:
1. Nhấn menu → **"Khách hàng"**
2. Làm theo hướng dẫn trên

---

## ✅ Checklist

Trước khi import, kiểm tra:

- [ ] Đã copy **CẢ 2 DÒNG** (header + data)
- [ ] Dữ liệu có phân cách bằng **Tab** (không phải Space)
- [ ] Có cột **custno, nmloc, regno** trong header
- [ ] Đã paste vào **textarea** (không phải file input)
- [ ] Đã nhấn nút **"Import"**

---

## 🎊 Kết luận

**Paste từ Clipboard** là cách **NHANH NHẤT** và **DỄ NHẤT** để import khách hàng từ AGRIBANK!

**Công thức thành công:**
```
Copy (2 dòng) → Paste (vào textarea) → Import (nhấn nút) = ✅ Done!
```

**Không cần**: File, Notepad, UTF-8, lo lắng! 😊

Hãy thử ngay! 🚀

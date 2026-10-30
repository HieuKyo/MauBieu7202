# 📒 Hướng dẫn: Tạo bìa chứng từ

Chức năng in **bìa lưu trữ Nhật ký chứng từ (mẫu M01/LHS)** kèm **nhãn mã QR**. Chức năng này thay cho file `Mau in bia chung tu.xlsb` và việc trộn thư (mail merge) bằng Word.

**Vào chức năng:** Menu **Kế toán Ngân quỹ → Tạo bìa chứng từ**

---

## 👤 Ai được dùng?

| Người dùng | Quyền |
|-----------|-------|
| **Trưởng phòng / Phó phòng** thuộc phòng Kế toán & Ngân quỹ | Dùng toàn bộ chức năng: cấp số, sửa, xoá, nhập số tờ, in, import |
| Tài khoản quản trị (admin) | Như Trưởng/Phó phòng |
| GDV và các cán bộ khác | Không vào được |

Mỗi người chỉ thấy bìa của **đơn vị mình**: Hội sở, PGD Láng Tròn hoặc PGD Phường 1.

---

## ⚙️ Chuẩn bị (làm một lần)

Vào **Hồ sơ nhân viên** và kiểm tra các thông tin sau:

1. **GDV** cần có: Phòng ban là *Kế toán & Ngân quỹ*, Nghiệp vụ là *Giao dịch viên*, và đã khai **Tài khoản IPCAS**. Mã QR dùng IPCAS này, nên GDV chưa khai IPCAS sẽ không được cấp số.
2. **Hậu kiểm viên**: chọn **một người** có Nghiệp vụ là *Hậu kiểm viên*. Đây là vai trò dùng chung cho cả Hội sở và 2 PGD.
3. **Trưởng/Phó phòng** cần đúng Chi nhánh/PGD, Phòng ban *Kế toán & Ngân quỹ*, và Chức vụ *Trưởng phòng* hoặc *Phó phòng*.

> 💡 Danh sách GDV để chọn chỉ lấy người thuộc phòng Kế toán & Ngân quỹ. Cán bộ phòng Khách hàng dù có khai nghiệp vụ "Giao dịch viên" cũng không hiện ra.

---

## 🎯 Công việc hằng ngày

### Bước 1: Cấp số hồ sơ

1. Bấm nút **"Cấp số theo ngày"**.
2. Chọn **Ngày chứng từ**.
3. Nhập **Số bắt đầu**. Ô này để trống, bạn phải tự nhập. Ngay bên dưới có dòng *"Gợi ý: …"*, bấm **"Dùng số gợi ý"** để điền nhanh số tiếp theo.
4. Tích chọn các **GDV có tập chứng từ** trong ngày và nhập **Số tập** của từng người.
5. *(Không bắt buộc)* Nhập **Thứ tự in** để chọn GDV nào đứng trước:
   - Ô để trống thì GDV xếp theo họ tên A→Z.
   - Thứ tự được **nhớ cho các lần sau**. Muốn đổi thì sửa trực tiếp, xoá trống ô để về mặc định.
6. Bấm **"Cấp số hồ sơ"**.

**Ví dụ:** có 4 GDV, trong đó B có 2 tập, số bắt đầu là 30:

| Số hồ sơ | GDV | Tập |
|----------|-----|-----|
| 7202-2026.0030 | A | 1/5 |
| 7202-2026.0031 | B | 2/5 |
| 7202-2026.0032 | B | 3/5 |
| 7202-2026.0033 | C | 4/5 |
| 7202-2026.0034 | D | 5/5 |

> 💡 Nếu cấp thêm trong **cùng một ngày**, tập mới đánh tiếp số (6/6, …) và tổng số tập của cả ngày được cập nhật lại.

### Bước 2: Nhập số tờ

Sau khi cấp số, màn hình chuyển về **Danh sách** của ngày đó. Trên bảng có 2 cột nhập trực tiếp:

| Cột | In ở đâu | Ghi chú |
|-----|----------|---------|
| **Số tờ** | Bìa (trang 1): *"Gồm: 01 tờ (01 quyển)"* | Mặc định là 1 |
| **Tờ của tập** | Nhãn QR (trang 2): *"Chứng từ ngày … (250 tờ)"* | Để trống thì nhãn in *"(…. tờ)"* để hậu kiểm điền tay |

Bấm **"Lưu số tờ"**. Nếu bấm In ngay thì số vừa nhập cũng được lưu luôn.

### Bước 3: In

- **In nhiều bìa:** tích chọn các dòng (hoặc ô tích ở đầu bảng để chọn tất cả), rồi bấm **"In bìa đã chọn (PDF)"**.
- **In một bìa:** bấm nút **In** (biểu tượng máy in) ở cuối dòng.

PDF khổ **A4**, mỗi bìa gồm **2 trang**:

| Trang | Nội dung |
|-------|----------|
| **1. Bìa** | Bìa M01/LHS: Ngày mở, Nhật ký chứng từ ngày … – Tập x/N, Gồm … tờ, Hồ sơ số, Thời hạn bảo quản |
| **2. Nhãn QR** | Mã QR, ngày chứng từ, số tờ của tập, số tập trong ngày, họ tên GDV, chuỗi QR, Tập; **Người hậu kiểm chứng từ** và **Người đóng chứng từ** |

Trên trang 2:
- **Người hậu kiểm chứng từ** là người đang giữ Nghiệp vụ *Hậu kiểm viên* **lúc bấm In**. Đổi nghiệp vụ trong hồ sơ nhân viên thì các bìa in sau sẽ đổi theo.
- **Người đóng chứng từ** là GDV của tập đó.

Bìa đã in hiện nhãn **"Đã in"** trên danh sách. Bìa nào cũng in lại được bao nhiêu lần tuỳ ý.

---

## 🔳 Nội dung mã QR

```
7202-GRANSINH-05/01/2026-2/5-7202-2026.0002
 │      │          │       │        └ Số hồ sơ
 │      │          │       └ Tập / Tổng số tập trong ngày
 │      │          └ Ngày chứng từ
 │      └ UserIPCAS của GDV
 └ Mã chi nhánh
```

---

## 🔢 Số hồ sơ

| Đơn vị | Định dạng | Ví dụ |
|--------|-----------|-------|
| Hội sở | `7202-năm.NNNN` | 7202-2026.0030 |
| PGD Láng Tròn | `7202LT-năm.NNNN` | 7202LT-2026.0001 |
| PGD Phường 1 | `7202P1-năm.NNNN` | 7202P1-2026.0001 |

- Mỗi đơn vị **đánh số riêng**, sang năm mới tự đếm lại từ 0001.
- Trong cùng một đơn vị, số hồ sơ **không được trùng**. Hệ thống sẽ báo lỗi nếu cấp hoặc sửa thành một số đã có.

---

## ✏️ Sửa / Xoá

- **Sửa** (biểu tượng bút chì): sửa được mọi thông tin gồm Số hồ sơ, Ngày, Tập, Tổng số tập, GDV, Số tờ, Số tờ của tập, Đơn vị tính, Thời hạn bảo quản, UserIPCAS.
  - ⚠️ Khi đổi GDV, nhớ sửa luôn ô **UserIPCAS** cho khớp, vì mã QR dùng ô này.
- **Xoá** (biểu tượng thùng rác): có hỏi xác nhận trước khi xoá.

> ⚠️ **Dòng màu vàng "Lệch tập"** nghĩa là các tập trong ngày đó không khớp 1…N (thiếu tập, thừa tập, hoặc tổng N khác nhau). Đây chỉ là cảnh báo, bạn vào **Sửa** để chỉnh lại.

---

## 📥 Import bìa cũ (in bù)

Dùng khi cần in bù các bìa đã làm từ trước, ví dụ file *FILE THANG 01 DEN THANG 7.2026.xlsx*.

### Định dạng file Excel

**Sheet đầu tiên**, **dòng 1 là tiêu đề**. **Mỗi dòng là một tập**: GDV có 2 tập thì ghi 2 dòng.

| Cột | Bắt buộc | Ví dụ |
|-----|----------|-------|
| Số hồ sơ | ✅ | 7202-2026.0002 |
| Tiêu đề hồ sơ | ✅ | Nhật ký chứng từ ngày 05/01/2026 - Tập 2/5 |
| Thời hạn bảo quản | | 20 năm |
| Ngày mở | | 05/01/2026 |
| Ngày công việc kết thúc | | 05/01/2026 |
| Số tờ | | 1 |
| Ghi chú | | Quyển |
| User | | GRANSINH *(IPCAS của GDV)* |
| Số tờ của tập chứng từ | | 250 *(hoặc "…." nếu chưa có)* |

### Các bước

1. Bấm **"Import bìa cũ"**, chọn file, rồi bấm **"Xem trước"**.
2. Kiểm tra cột **Trạng thái**:

| Trạng thái | Ý nghĩa |
|-----------|---------|
| **Tạo mới** | Số hồ sơ chưa có, sẽ được tạo bìa mới |
| **Cập nhật** | Bìa đã có, chỉ cập nhật **User** và **Số tờ của tập** từ file. Các thông tin khác giữ nguyên |
| Đã có (bỏ qua) — chữ xám | Bìa đã có và file không có thông tin mới |
| Dòng đỏ | Lỗi: số hồ sơ trùng trong file, tiêu đề sai dạng, hoặc không tìm thấy GDV có IPCAS ở cột User |

3. Bấm **"Xác nhận import/cập nhật"**. Các dòng lỗi sẽ bị bỏ qua.

> 💡 Dòng **không có cột User** thì mã QR dùng IPCAS của **người import**, nên người import cần đã khai Tài khoản IPCAS.
>
> 💡 Có thể import lại cùng một file nhiều lần, ví dụ sau khi bổ sung cột User hoặc Số tờ của tập. Bìa đã có chỉ được cập nhật, không bị tạo trùng.

---

## ❓ Lỗi thường gặp

| Thông báo | Cách xử lý |
|-----------|-----------|
| *Chỉ Trưởng/Phó phòng Kế toán & Ngân quỹ … mới dùng được* | Kiểm tra Chi nhánh, Phòng ban và Chức vụ trong hồ sơ nhân viên |
| *GDV chưa khai báo Tài khoản IPCAS: …* | Khai IPCAS cho GDV đó trong hồ sơ nhân viên |
| *Chưa nhập Số bắt đầu* | Nhập số, hoặc bấm "Dùng số gợi ý" |
| *Số hồ sơ đã tồn tại: …* | Chọn số bắt đầu khác (xem số gợi ý) |
| *Chưa cấu hình Mã chi nhánh cho đơn vị …* | Admin vào **Cấu hình Chi nhánh** và nhập *Mã chi nhánh* (7202) |
| Trang 2 in **dòng chấm** ở "Người hậu kiểm" | Chưa ai có Nghiệp vụ *Hậu kiểm viên*, cần gán cho một người |
| Trang 2 in **dòng chấm** ở "Người đóng chứng từ" | Bìa chưa gán GDV, vào **Sửa** để chọn GDV |

---

## 🛠️ Ghi chú cho quản trị (cập nhật máy LAN)

Chức năng này cần chạy migrate để tạo bảng mới, gồm các migration `0087_bia_chung_tu`, `0088_bia_thu_tu_in` và `0089_bia_so_to_tap`:

```
python manage.py migrate
```

Không cần cài thêm thư viện nào. Mã QR được tạo bằng `reportlab`, thư viện đã có sẵn trong `packages/`.

# 📊 Hướng dẫn: Phân tích sao kê

Chức năng đọc **file sao kê DPTB18** của một tài khoản, **tự phân loại từng giao dịch** và tìm **tên, số tài khoản, ngân hàng của đối tác** (người chuyển tiền đến / người nhận tiền đi). Kết quả xem trên màn hình hoặc xuất ra Excel.

**Vào chức năng:** Menu **Tiện ích → Phân tích Sao kê**

---

## 📁 Các file cần chuẩn bị

Chỉ **DPTB18 là bắt buộc**. Các file đối soát còn lại không bắt buộc, nhưng có càng đủ thì tên và tài khoản đối tác càng đầy đủ, chính xác.

| File | Bắt buộc | Dùng để |
|------|----------|---------|
| **DPTB18** (sao kê tài khoản) | ✅ Có | Danh sách giao dịch, số tiền, số dư |
| **MSPH02 chiều đến** | Không | Tiền đến qua hệ thống thanh toán tập trung (Payment Hub) |
| **MSPH02 chiều đi** | Không | Tiền đi qua hệ thống thanh toán tập trung |
| **CSP chiều đến** | Không | Tiền đến qua NAPAS (ngân hàng ngoài thanh toán tập trung) |
| **CSP chiều đi** | Không | Tiền đi qua NAPAS |
| **FXIR64** | Không | Tiền đến qua FX: từ chi nhánh Agribank khác (mã `ITL`) và từ ngân hàng khác qua CITAD (mã `ITT`) |
| **FXOR88** | Không | Tiền đi qua FX: sang chi nhánh Agribank khác hoặc ngân hàng khác qua CITAD (mã `OTT`) |

**Lưu ý khi xuất file:**

1. Xuất các file đối soát **cùng khoảng thời gian** với DPTB18. Giao dịch ngoài kỳ sao kê sẽ rơi vào danh sách "Dòng không khớp".
2. **CSP chiều đi:** xuất **toàn bộ** (cả dòng 369 Debit, 91 Credit, 43 Inquiry) và **có cột** `TO_ACCOUNT_REMARK`. Cột này chứa tên người nhận.
3. **FXIR64:** xuất **đủ cả 2 loại** giao dịch đến: `7202ITL…` (từ chi nhánh Agribank khác) và `7202ITT…` (từ ngân hàng khác). Nếu chỉ có ITL thì các khoản tiền đến từ ngân hàng khác sẽ thiếu tên người chuyển.
4. Giữ nguyên file như khi xuất từ hệ thống (.xls hoặc .xlsx), **không mở ra sửa rồi lưu lại**, vì Excel có thể làm mất số 0 đầu của số tài khoản.

---

## 🎯 Các bước thực hiện

### Bước 1: Tải file lên

1. Kéo thả hoặc bấm **"Chọn file"** để chọn file **DPTB18**.
2. *(Không bắt buộc)* Ở khung **File đối soát**, chọn từng file vào đúng ô: MSPH02 chiều đến, MSPH02 chiều đi, CSP chiều đến, CSP chiều đi, FXIR64, FXOR88.
3. Bấm **"Phân tích File"** và chờ đến khi có thông báo, thường vài giây.

Thông báo cho biết số giao dịch đã phân tích, số giao dịch được bổ sung thông tin đối tác từ file đối soát, và số dòng không khớp (nếu có).

> 💡 File tải lên chỉ dùng để phân tích, **xoá ngay sau khi xử lý xong**. Mỗi người chỉ xem được sao kê do **chính mình** tải lên.

### Bước 2: Xem kết quả

Đầu trang có 4 ô tổng: **Tổng số giao dịch, Tổng tiền ghi nợ (ra), Tổng tiền ghi có (vào), Số dư cuối kỳ**, và bảng **Thống kê theo loại giao dịch**.

Bên dưới có các thẻ:

| Thẻ | Nội dung |
|-----|----------|
| **Chi tiết giao dịch** | Từng giao dịch: ngày, tiền ra/vào, số dư, ngân hàng, số TK, tên đối tác, nội dung, loại giao dịch, **nguồn thông tin**. Lọc được theo loại giao dịch. |
| **Thống kê** | Tài khoản **nhận tiền** nhiều lần và tài khoản **chuyển tiền đến** nhiều lần (số lần, tổng tiền). Có ô **Cập nhật tên từ file Excel**. |
| **Dòng không khớp** | Chỉ hiện khi có. Giao dịch **thành công** trong file đối soát nhưng **không tìm thấy** trong DPTB18 → cần kiểm tra lại. |

### Bước 3: Xuất Excel

Bấm **"Xuất Excel"** (góc trên bên phải). File gồm các sheet:

| Sheet | Nội dung |
|-------|----------|
| **Chi tiết** | Toàn bộ giao dịch, có cột **Nguồn** |
| **Thống kê** | Tổng quan, thống kê theo loại giao dịch, **thống kê theo nguồn**, số dòng không khớp |
| **TK giao dịch nhiều lần** | Tài khoản nhận tiền / chuyển tiền đến nhiều lần. Ô **Tên** còn trống được **tô vàng** |
| **Không khớp** | Chỉ có khi có dòng không khớp |

---

## 🔎 Đọc cột "Nguồn"

Cột **Nguồn** cho biết **tên / số TK / ngân hàng đối tác lấy từ đâu**, để biết mức độ tin cậy:

| Nguồn | Ý nghĩa | Tin cậy |
|-------|---------|---------|
| **MSPH02 chiều đến / chiều đi** | Lấy từ file MSPH02 | ✅ Cao |
| **CSP chiều đến / chiều đi** | Lấy từ file CSP | ✅ Cao |
| **FXIR64 chiều đến / FXOR88 chiều đi** | Lấy từ file FX | ✅ Cao |
| **CSP chiều đi (tên từ …)** | Số TK lấy từ CSP, tên tìm được nhờ đối chiếu số TK với file khác | ✅ Cao |
| **Danh bạ** | Tên do người dùng đã điền và xác nhận trước đó | ✅ Cao |
| **Đối chiếu số TK** | Tên lấy từ giao dịch khác **cùng số TK** đã có nguồn tin cậy | ✅ Cao |
| **Nội dung GD (tên chưa xác thực)** | Tên tách từ **nội dung chuyển khoản** do người chuyển tự gõ | ⚠️ Cần kiểm tra |
| **Đối chiếu số TK (chưa xác thực)** | Tên lấy từ giao dịch khác cùng số TK, nhưng tên gốc chưa xác thực | ⚠️ Cần kiểm tra |
| **Nội dung GD** | Không có thông tin đối tác từ file đối soát | — |

> 💡 Với giao dịch nội bộ `MB(…)(…)`, chỉ nhận tên khi nội dung ghi **họ tên từ 2 chữ trở lên**. Nội dung như *"THANH chuyen khoan"* sẽ để trống tên.

---

## ✍️ Bổ sung tên còn thiếu (Danh bạ)

Một số tài khoản không tìm được tên. Bạn có thể tự điền, và tên sẽ được **lưu vào Danh bạ dùng chung** để **tự điền cho các sao kê sau** (của mọi người dùng).

1. Bấm **"Xuất Excel"**.
2. Mở sheet **TK giao dịch nhiều lần**, điền tên vào các **ô tô vàng**. Cột *Tên người* ở sheet **Chi tiết** tự cập nhật theo.
3. **Lưu** file.
4. Trên trang kết quả, mở thẻ **Thống kê** → ô **Cập nhật tên từ file Excel** → chọn file vừa lưu → bấm **"Cập nhật tên"**.

Chương trình báo *"Đã lưu X tên vào danh bạ, cập nhật Y giao dịch"*.

- Chỉ lưu tên **mới điền hoặc đã sửa**. Nếu sửa một tên có sẵn, tên mới thay cho mọi giao dịch của tài khoản đó.
- Tên trong Danh bạ **ghi đè tên chưa xác thực** lấy từ nội dung chuyển khoản.
- Một tài khoản được nhận diện bằng **số TK + ngân hàng**.

> 💡 Điền nhầm? Quản trị viên vào **Trang quản trị → Danh bạ tài khoản** để sửa tên hoặc xoá.

---

## 🏷️ Các loại giao dịch chính

| Loại | Nhận biết |
|------|-----------|
| **Chuyển khoản nội bộ Agribank** / **Nhận chuyển khoản nội bộ Agribank** | Giữa các tài khoản Agribank: dạng `MB(…)(…)`, mã FX `ITL`, FX sang chi nhánh `IKO…`, hoặc tiền ra có **tài khoản nhận** (`toacctno`) |
| **Chuyển khoản đi khác ngân hàng** / **Nhận chuyển khoản liên ngân hàng** | Qua NAPAS, Payment Hub (`xxxxAPI`), CITAD (FX `OTT`/`ITT` có mã ngân hàng 8 số) |
| **Nhận thanh toán MCC** / **Thanh toán qua MCC** | Nội dung có `;MCC;` |
| **Giao dịch OSB** | Hệ sinh thái Agribank, người thực hiện `xxxxOSB` (cả chiều đi và đến) |
| **Nộp thuế / NSNN** | Nội dung bắt đầu bằng `EBAGRTAX`. Phí 11.000đ đi kèm xếp vào *Phí dịch vụ* |
| **Phí dịch vụ** | Phí SMS, OTT, Agribank Plus, quản lý tài khoản, thường niên thẻ… |
| **Rút tiền mặt**, **Nộp tiền tại quầy**, **Nạp tiền điện thoại**, **Thanh toán hóa đơn**, **Trả lãi tiền gửi**… | Theo mã giao dịch và nội dung |

> 💡 **Số tiền** luôn lấy theo DPTB18. Với giao dịch FX, số tiền trong DPTB18 **đã gồm phí chuyển tiền** nên có thể lớn hơn số tiền trong FXOR88. Đây là bình thường.

---

## ❓ Câu hỏi thường gặp

**Có "Dòng không khớp" thì làm gì?**
Kiểm tra lại: file đối soát có cùng kỳ với DPTB18 không, có chọn nhầm ô (ví dụ file chiều đi vào ô chiều đến) không. Dòng CSP chiều đi *"trừ tiền nhưng không chuyển đi"* thường là giao dịch bị hoàn.

**Báo lỗi "File … thiếu cột …"?**
File chọn sai ô hoặc xuất thiếu cột. Xuất lại file từ hệ thống, giữ nguyên định dạng.

**Sau khi chương trình được cập nhật, kết quả cũ có tự đổi không?**
Không. Kết quả được lưu lúc phân tích. Muốn áp dụng cách phân loại mới thì **tải lại file và phân tích lại**.

**Sao kê cũ xem lại ở đâu?**
Trang **Phân tích Sao kê** có mục **Sao kê gần đây** (10 sao kê mới nhất của bạn), bấm vào để xem lại hoặc xuất Excel.

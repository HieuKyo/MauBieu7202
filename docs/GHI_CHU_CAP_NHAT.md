# Ghi chú cập nhật

Mỗi mục là một bản cập nhật (gói `CapNhat_MauBieu_<phiên bản>`), mới nhất ở trên.
Mục "Bản tiếp theo" là các thay đổi chưa đóng gói. Khi chạy `tao_ban_cap_nhat.bat`, tiêu đề này được đổi thành số phiên bản và ngày.

## Bản tiếp theo

### Chức năng mới
- **Kế toán Ngân quỹ → Đối chiếu Hóa đơn điện tử** (phòng KT&NQ, Hậu kiểm, Superuser) — thay cho file macro "DOI CHIEU HDDT.xlsm":
  - Tải file **Einvoice** (xuất từ website / BKCT) và **IPCAS** (GLST30 – Day, SOLD), tên file theo ngày **DDMM** như trước; chọn nhiều ngày cùng lúc để đối chiếu theo lô (ghép cặp theo tên file).
  - Xem trước: **đối chiếu theo user** (Einvoice / Ipcas / Chênh lệch / Số món lệch), **giao dịch IPCAS chưa có hoá đơn**, **lỗi hoá đơn Einvoice** (chưa ký, đảo doanh thu thành tổng thanh toán, sai tỷ giá, DN chưa có MST). Tải **file kết quả** (ketquaDDMMYYYY.xlsx, cùng bố cục file cũ) từng ngày hoặc cả lô (.zip).
  - **Tạo file import HĐĐT** (LOAD DDMM.xlsx): gom chênh lệch — **7202CD → Phí thường niên**; **7202EI → Phí dịch vụ kiều hối** (USD, bắt buộc nhập **tỷ giá quy đổi**, trang nhắc khi có kiều hối); còn lại → **Phí dịch vụ chuyển tiền**. Chọn user đưa vào file (user chênh lệch âm từ 1 triệu trở lên — thường là HĐ lập riêng như đấu giá tài sản — mặc định không gom).
  - **Hoá đơn riêng** khi khách hàng yêu cầu xuất riêng (vd **Thu lãi tiền vay** cho DN): chọn loại, nhập số tiền, thông tin khách hàng; tích "Xuất file riêng" thì tải về .zip gồm file chính + file riêng.
  - Đã đối chiếu lại toàn bộ dữ liệu tháng 11: bảng theo user khớp 448/448 dòng với file kết quả cũ, file import khớp 38/38 dòng.
  - **Kiểm tra lỗi hoá đơn bổ sung:** đơn giá ≠ doanh số chưa thuế, thuế suất khác 10% (trừ hàng không chịu thuế: lãi tiền vay, lãi thấu chi, phí trả nợ trước hạn, bảo lãnh…), tiền GTGT ≠ 10%, tổng thanh toán ≠ đơn giá + VAT, hoá đơn không có user.
  - **Tra Khách hàng 360:** ở hoá đơn riêng gõ CIF bấm tra → tự điền tên, địa chỉ, cá nhân/tổ chức, số TK; tab lỗi hoá đơn gợi ý CIF cho HĐ "DN chưa có MST" (khớp theo Số cif hoặc tên tổ chức). Lưu ý: KH 360 hiện chưa có MST của tổ chức (DP01 không có) — MST vẫn nhập tay.
  - Trang tải file chọn **Cách 1 – GLST30** (như cũ) hoặc **Cách 2 – GLCB06 + GLCB41** (theo cách làm file "DCHD", mỗi lần 1 ngày): 1 file Einvoice + **GLCB41** (bảng cân đối, bắt buộc) + các file **GLCB06 – Transaction List in Account** (mỗi lần search 1 tài khoản ra 1 file: 453101 và TK thu lãi 702…, đủ các loại tiền — chọn nhiều file cùng lúc); GLST30 tuỳ chọn (đơn giá thật). Tạm thời chưa đưa TK 711… vào GLCB06.
    - Khớp theo user + bút toán + số tiền + loại tiền + TK; tổng hợp **theo user – loại tiền** (nguyên tệ / VND); bút toán chưa có HĐ (tô riêng **tiền vay** TK 702…, đánh dấu "Nhập đơn giá" khi VAT lẻ); HĐ không có bút toán bên IPCAS; **cân đối GLCB41** (453101 / 702 / 711 so với tổng hoá đơn gốc).
    - File import: mặc định **kết hợp** — tổ chức (theo KH 360) và lãi vay lập 1 HĐ / bút toán có tên, địa chỉ (RefNo = user-số bút toán), cá nhân gom theo nhóm phí; hoặc chọn lập từng bút toán / gom tất cả. Ngoại tệ nhập tỷ giá theo từng loại tiền.
    - Không cần xuất Msit81 / CMCC01 / DPCOM như file cũ (thông tin KH lấy từ Khách hàng 360). Đã kiểm lại với dữ liệu trong file DCHD: trạng thái 4.173/4.173 bút toán và bảng theo user – loại tiền 14/14 dòng khớp kết quả của file.

### Chỉnh sửa
- **Chứng từ → Giao/Nhận chứng từ – bước Hậu kiểm:** sau khi xác nhận đã nhận (trạng thái *"Hậu kiểm đã nhận – đang kiểm tra"*), Hậu kiểm viên bấm **"Hoàn thành chứng từ"** hoặc **"HKV trả chứng từ để GDV sửa"** (bắt buộc lý do). GDV sửa xong giao lại Hậu kiểm (hoặc giao KSV nếu cần ký lại); thu hồi thì về đúng trạng thái trước khi giao. Tập "HKV trả sửa" được đếm vào số việc của GDV.

### Lưu ý
- Có migration `templates_app/0099_bia_giao_nhan_hau_kiem` (thêm 2 trạng thái giao nhận; không đổi dữ liệu). Các tập đang ở "Hậu kiểm đã nhận" giữ nguyên — Hậu kiểm viên bấm "Hoàn thành chứng từ" để kết thúc.
- Kết quả đối chiếu HĐĐT lưu tạm 24 giờ trong `tmp/hddt` (chỉ người tải xem được, tự xoá), không lưu dữ liệu khách hàng vào cơ sở dữ liệu.

### File
- Thêm: `templates_app/hddt_doi_chieu.py`, `templates_app/hddt_glcb06.py`, `templates_app/hddt_views.py`, `templates_app/test_hddt.py`, `templates_app/templates/templates_app/hddt/` (upload.html, ket_qua.html, ket_qua_glcb06.html, _dong_rieng.html, _dong_xem.html), `templates_app/migrations/0099_bia_giao_nhan_hau_kiem.py`
- Sửa: `templates_app/urls.py`, `templates_app/templates/templates_app/base.html`, `templates_app/models/cash.py`, `templates_app/bia_giao_nhan_views.py`, `templates_app/test_bia_giao_nhan.py`, `templates_app/templates/templates_app/bia_chung_tu/` (giao_nhan.html, _bang_gn.html, _trang_thai_gn.html), `scripts/release/build_update.py`, `tao_ban_cap_nhat.bat`

## 2026.11.26 — 26/11/2026

### Chức năng mới
- **Khách hàng 360 → Việc cần làm** (mọi người dùng; nhân viên chỉ thấy KH của đơn vị mình theo hồ sơ người dùng, cấp quản lý KH 360 và Superuser thấy toàn chi nhánh). 3 danh sách để liên hệ KH, mỗi dòng ghi được **kết quả liên hệ** (Thành công / Chưa quyết định / KH rút – từ chối / Không liên lạc được + ghi chú), có cột **Tiến độ liên hệ** theo cán bộ và xuất Excel:
  - **Sổ đến hạn:** sổ tiết kiệm đến hạn trong 7 / 15 / 30 ngày tới, hoặc đã đến hạn kể từ ngày dữ liệu.
  - **Khoản vay sắp trả:** khoản vay có kỳ trả gốc/lãi tiếp theo trong 7 / 15 / 30 ngày tới (số tiền trả, dư nợ, nhóm nợ, cán bộ tín dụng).
  - **KH chưa dùng dịch vụ:** KH cá nhân có tiền gửi từ ngưỡng chọn (mặc định 10 triệu) nhưng chưa có thẻ, Agribank Plus, SMS Banking, SMS tiền gửi, tiền gửi trực tuyến — để tư vấn bán chéo.
  - Lọc theo PGD, cán bộ, "Chỉ KH của tôi" (khớp họ tên trong hồ sơ người dùng), tình trạng liên hệ, mã/tên KH; bấm mã KH mở hồ sơ KH 360.
- **Kế toán Ngân quỹ → Chứng từ** (đổi tên từ "Tạo bìa chứng từ"), gồm 2 tab:
  - **Tạo bìa chứng từ** (như cũ, Trưởng/Phó phòng KT&NQ) — danh sách có thêm cột trạng thái giao nhận.
  - **Giao/Nhận chứng từ** (mọi người dùng): mỗi bìa đã cấp số là 1 tập chứng từ của GDV. Luồng: **GDV giao KSV** (Trưởng/Phó phòng) → **KSV xác nhận đã nhận** → **KSV ký xong trả GDV** (trạng thái *"KSV trả chứng từ chờ GĐ ký"*) → GDV đem GĐ ký xong **giao Hậu kiểm** → **Hậu kiểm xác nhận đã nhận**. KSV / Hậu kiểm trả lại được (bắt buộc lý do); GDV thu hồi được khi bên nhận chưa nhận. Chọn nhiều tập để xử lý cùng lúc.
  - Mục **Chờ tôi xử lý** (KSV / Hậu kiểm), **Tập chứng từ của tôi** (GDV, có nút chọn nhanh "Chưa giao" / "Chờ GĐ ký"), **Tra cứu** (theo ngày, trạng thái, số hồ sơ, GDV) kèm **lịch sử ngày giờ** từng lần giao / nhận / trả lại. Tab có số đếm việc đang chờ.
  - GDV / Hậu kiểm vào menu "Chứng từ" được chuyển thẳng sang tab Giao/Nhận (không thấy tab Tạo bìa). GDV chỉ tra cứu tập của mình; Trưởng/Phó phòng KT&NQ xem cả đơn vị; Hậu kiểm và Superuser xem tất cả.
  - Bìa đã cấp trước bản này và bìa import (in bù) **không theo dõi** giao nhận; bìa cấp số từ nay tự vào trạng thái "GDV đang giữ". Muốn theo dõi bìa cũ: ở tab Tạo bìa chứng từ chọn bìa → **Đưa vào giao nhận** (GDV sẽ thấy ở "Tập chứng từ của tôi").

### Chỉnh sửa
- **ATM – Bảng kê thanh toán & Giấy đi đường** (trang Công tác phí ATM):
  - **Tách theo giai đoạn Ban:** khi Trưởng ban, Phó ban (Trưởng phòng KTNQ) hoặc Cán bộ phụ trách ATM đổi người trong khoảng ngày đã chọn, trang liệt kê từng giai đoạn (ai giữ chức vụ nào) kèm nút Xem / Bảng kê / Giấy đi đường riêng cho từng giai đoạn.
  - **Kiểm tra dữ liệu Ban trước khi xuất:** cảnh báo nhiệm kỳ 2 người cùng chức vụ chồng ngày, khoảng ngày không có nhiệm kỳ khớp (đang tạm lấy người "Đang hoạt động") hoặc không có ai, người chưa nhập "Hiệu lực từ / đến ngày" khi chức vụ có nhiều người, người được thanh toán chưa có số tài khoản.
  - **Chống thanh toán trùng:** mỗi lần xuất Bảng kê được ghi lại (khoảng ngày, tổng tiền, số người, người xuất — không lưu họ tên / số tài khoản). Khoảng ngày đang xem trùng với lần xuất trước thì hiện cảnh báo đỏ và hỏi lại khi bấm xuất. Có bảng 10 lần xuất gần nhất; xuất nhầm thì xóa bản ghi trong trang quản trị (Lịch sử xuất Bảng kê ATM).
  - **Xem trước từng tờ Giấy đi đường:** tên file, máy ATM, các ngày tiếp quỹ, Trưởng ban / Phó ban / CB phụ trách ATM / tài xế trên tờ.
  - **Chuyến tài xế không được tính tiền** (tài xế trực ngày đó đi tiếp quỹ) hiện thành danh sách để đối chiếu Lịch trực xe.

### Lưu ý
- Có migration `templates_app/0097_atmpaymentexportlog` (bảng lịch sử xuất Bảng kê ATM). Lịch sử bắt đầu ghi từ lúc cập nhật; các lần xuất trước đó không có.
- Có migration `templates_app/0098_bia_giao_nhan` (trạng thái + lịch sử giao nhận bìa chứng từ; bìa cũ đặt về "không theo dõi") và `kh360/0006_lien_he_kh` (kết quả liên hệ Việc cần làm).
- Việc cần làm lọc theo đơn vị trong hồ sơ người dùng (Hội sở / PGD Phường 1 / PGD Láng Tròn): người dùng chưa khai báo đơn vị sẽ không thấy danh sách — Admin cần cập nhật hồ sơ. KH thuộc PGD Tân Phong chỉ cấp quản lý xem được.

### File
- Thêm: `templates_app/migrations/0097_atmpaymentexportlog.py`, `templates_app/migrations/0098_bia_giao_nhan.py`, `templates_app/bia_giao_nhan_views.py`, `templates_app/templatetags/bia_tags.py`, `templates_app/test_bia_giao_nhan.py`, `templates_app/templates/templates_app/bia_chung_tu/` (giao_nhan.html, _bang_gn.html, _trang_thai_gn.html), `kh360/migrations/0006_lien_he_kh.py`, `kh360/viec_can_lam.py`, `kh360/templates/kh360/viec_can_lam.html`, `kh360/templates/kh360/_viec_dong.html`
- Sửa: `templates_app/atm_travel_claim.py`, `templates_app/atm_views.py`, `templates_app/templates/templates_app/atm/travel_claim.html`, `templates_app/models/atm.py`, `templates_app/models/__init__.py`, `templates_app/admin.py`, `templates_app/urls.py`, `templates_app/templates/templates_app/base.html`, `templates_app/models/cash.py`, `templates_app/bia_chung_tu_views.py`, `templates_app/test_bia_chung_tu.py`, `templates_app/templates/templates_app/bia_chung_tu/_nav.html`, `templates_app/templates/templates_app/bia_chung_tu/list.html`, `kh360/models.py`, `kh360/urls.py`, `kh360/templates/kh360/_header.html`

## 2026.11.25 — 25/11/2026

### Chức năng mới
- **So sánh HĐV theo file (theo kỳ)** (mọi người dùng, menu **Kế toán Ngân quỹ**): chọn kiểu so sánh **file DP01 / MSIT81 (file TG) / RT13**, chọn từ 2 file trở lên (.csv, .zip, .xlsx, .xls; tự sắp theo ngày trong tên file) → xem kết quả ngay trên trang và xuất Excel theo bộ lọc. So khớp theo **Mã KH + Loại tiền** (cộng số dư mọi TK của KH — tất toán rồi mở lại sổ sinh số TK mới vẫn tính đúng KH); **ngoại tệ tách riêng** từng loại tiền. Các phần:
  - **Tổng hợp** theo loại tiền (tách Không kỳ hạn / Có kỳ hạn), số KH Mới / Tăng / Giảm / Tất toán / Không đổi; top 5 cán bộ tăng / giảm nhiều nhất.
  - **Cán bộ huy động** (cột EMPLOYEE_NAME) và **PGD**: mỗi cán bộ / PGD tăng hay giảm bao nhiêu (có thanh so sánh), chênh lệch KKH / CKH, số KH mới / tăng / giảm / tất toán.
  - **Loại KH** (cá nhân / tổ chức…), **Chi tiết KH** (lọc theo ngưỡng số tiền, %, trạng thái, cán bộ, PGD, loại KH, tìm mã/tên), **Cần chăm sóc** (KH tất toán / giảm, kèm số điện thoại), **Chuyển CB/PGD** (KH đổi cán bộ hoặc PGD giữa 2 kỳ).
  - Từ 3 file trở lên: **Xu hướng** theo từng kỳ (biểu đồ tổng / KKH / CKH, số dư từng cán bộ qua các kỳ; Excel có thêm số dư từng KH qua các kỳ).
  - Đối chiếu **Đăng ký chỉ tiêu HĐV** (khớp CCCD + loại tiền, ngày dự kiến gửi trong khoảng 2 kỳ): KH tăng có / chưa có đăng ký.
  - Bấm Mã KH mở hồ sơ **Khách hàng 360**.
  - Kết quả lưu tạm 24 giờ trong thư mục `tmp/` (chỉ người tải mới xem được, tự xóa), không lưu dữ liệu khách hàng vào cơ sở dữ liệu.

### Chỉnh sửa
- **ATM – Bảng kê thanh toán & Giấy đi đường: xuất theo Trưởng ban.** Có ô chọn **Trưởng ban**; chọn xong thì khoảng ngày tự điền theo nhiệm kỳ người đó (vẫn sửa được), và Bảng kê / Giấy đi đường chỉ gồm các chuyến trong nhiệm kỳ đó. Tên file có thêm tên Trưởng ban.
- Giấy đi đường: mỗi tờ chỉ có **1 Trưởng ban, 1 Phó ban (Trưởng phòng KTNQ), 1 Cán bộ phụ trách ATM** — đổi người ở bất kỳ chức vụ nào (sang nhiệm kỳ mới) thì tự tách tờ mới (trước đây tờ có thể có 2 Phó ban khi Phó ban đổi giữa kỳ). Nếu khoảng ngày đã chọn có từ 2 nhiệm kỳ trở lên, trang hiện cảnh báo kèm nút xem / xuất riêng cho từng nhiệm kỳ.

### File
- Thêm: `templates_app/hdv_so_sanh.py`, `templates_app/hdv_so_sanh_views.py`, `templates_app/templates/templates_app/hdv/so_sanh_file.html`, `templates_app/templates/templates_app/hdv/so_sanh_ket_qua.html`
- Sửa: `templates_app/atm_views.py`, `templates_app/atm_travel_claim.py`, `templates_app/templates/templates_app/atm/travel_claim.html`, `templates_app/urls.py`, `templates_app/templates/templates_app/base.html`, `templates_app/report_views.py`, `.gitignore`

## 2026.11.24 — 24/11/2026

### Chức năng mới
- **Thống kê truy cập menu** (chỉ Superuser, menu **Tiện ích → Thống kê truy cập**): xem số lượt mở từng menu theo **ngày / tuần / tháng** (chọn số kỳ gần nhất), số người dùng và lần mở cuối của từng menu; bảng theo từng người dùng, lọc xem riêng 1 người. Mặc định chỉ hiện các mục có trên menu; bỏ chọn để xem cả trang con. Lượt truy cập tự xóa sau 400 ngày.

### Lưu ý
- Có migration `templates_app/0096_menu_access_log` (tạo bảng lượt truy cập). Thống kê bắt đầu đếm từ lúc cập nhật, không có số liệu của trước đó.

### Chỉnh sửa
- **Nhận bì thư – mã ghi khoảng ngày** (vd. `EMBND013157202107` = Thẻ ghi nợ nội địa, phát hành từ ngày 13 đến 15, CN 7202): trước đây báo "không phải mã bì thư"; nay nhận được, ô Ngày phát hành điền ngày đầu của khoảng (13), dòng gợi ý dưới ô mã ghi rõ "từ 13 đến 15/MM".
- Mã bì thư dạng EMB… mà không tách được ngày / chi nhánh thì không còn bị từ chối: vẫn điền mã và loại thẻ, báo để người nhận tự nhập ngày phát hành, chi nhánh.

### File
- Sửa: `templates_app/templates/templates_app/reports/mail_envelope_tracking.html`, `templates_app/templates/templates_app/reports/_mail_envelope_huong_dan.html`
- Thêm: `templates_app/middleware.py`, `templates_app/access_log_views.py`, `templates_app/templates/templates_app/access_stats.html`, `templates_app/migrations/0096_menu_access_log.py`, `templates_app/test_access_log.py`
- Sửa: `templates_app/models/system.py`, `templates_app/models/__init__.py`, `templates_app/urls.py`, `templates_app/templates/templates_app/base.html`, `wordgen/settings.py`

## 2026.11.19 — 19/11/2026

### Chỉnh sửa
- **Nhận bì thư – mã có số thứ tự 4 chữ số** (vd. `EMBND041172021302` = Thẻ ghi nợ nội địa, 04/11, CN 7202): trước đây quét được nhưng báo "không phải mã bì thư"; nay nhận đúng. Mã đọc được nhiều cách (có / không có số 0 thừa ở đầu) thì chọn ngày phát hành gần ngày nhận nhất.
- **KH 360 – bảng chi tiết khách hàng:** trên một số máy dùng Google Chrome bản cũ, bảng chi tiết chỉ hiện một khung hẹp giữa màn hình (màn 1280×768…); nay bung đủ rộng như các máy khác.

### File
- Sửa: `templates_app/templates/templates_app/reports/mail_envelope_tracking.html`, `kh360/templates/kh360/_assets.html`

## 2026.11.10 — 10/11/2026

### Chỉnh sửa
- **Nhận bì thư – quét bằng camera:** nút **Bật camera** mở khung camera ngay trên trang và quét liên tục (bật 1 lần, quét lần lượt từng bì thư), thay cho cửa sổ quét QR căn cước. Đọc được **mã vạch** (Code 128) trên bì thư — to và rõ hơn QR nên camera để xa / camera tài liệu (USB Camera) vẫn đọc được — và vẫn đọc QR như trước. Có ô chọn camera khi máy gắn nhiều camera.
- **Nhận bì thư:** ô **Người nhận** mặc định là tài khoản (username) đang đăng nhập; vẫn chọn / sửa sang người khác được.

### File
- Thêm: `templates_app/static/js/zxing.min.js` (thư viện đọc mã vạch ZXing 0.21.3, chạy offline)
- Sửa: `templates_app/report_views.py`, `templates_app/templates/templates_app/reports/mail_envelope_tracking.html`, `templates_app/templates/templates_app/reports/_mail_envelope_huong_dan.html`

## 2026.11.09.3 — 09/11/2026

### Chức năng mới
- **KH 360 – Thống kê sổ tiết kiệm** (Thống kê → tab **Sổ tiết kiệm**): lọc sổ tiết kiệm / tiền gửi có kỳ hạn theo ngày đến hạn (7 ngày tới, 30 ngày tới, tháng này, tháng sau, đã qua hạn, khoảng ngày tự chọn), kỳ hạn (chọn nhiều hoặc từ … tháng trở lên), số tháng đã gửi, số dư sổ, lãi suất, hình thức (trả lãi khi đến hạn / định kỳ / gửi góp), loại và hạng khách hàng, điểm giao dịch, khách đã có / chưa có một dịch vụ. Hiện số sổ, số khách hàng, tổng số dư, lãi suất bình quân; bảng tổng hợp theo kỳ hạn và theo tháng đến hạn; danh sách sổ có số ngày còn lại đến hạn, bấm vào để mở hồ sơ khách hàng; xuất Excel. Có 9 mẫu lọc nhanh (đến hạn trong 7 ngày, đến hạn tháng này mà khách chưa có Agribank Plus…).
- **KH 360 – Thống kê tiền vay** (Thống kê → tab **Tiền vay**): lọc khoản vay theo dư nợ, thời hạn vay (số tháng hoặc nhóm ngắn / trung / dài hạn), số tháng đã vay, ngày giải ngân (7 / 30 ngày qua, tháng này, tháng trước, khoảng ngày), ngày đáo hạn, kỳ trả nợ tiếp theo, nhóm nợ, cho vay / thấu chi, loại vay, mục đích, cán bộ tín dụng, lãi suất, tình trạng (còn dư nợ / đã tất toán), loại và hạng khách hàng, khách đã có / chưa có một dịch vụ. Hiện số món, số khách, tổng dư nợ, lãi suất bình quân, nợ xấu; bảng theo nhóm nợ, theo thời hạn, theo cán bộ tín dụng; danh sách khoản vay (số ngày còn đến đáo hạn, kỳ trả tiếp), bấm vào để mở hồ sơ khách hàng; xuất Excel. 11 mẫu lọc nhanh (giải ngân 30 ngày qua mà khách chưa có Agribank Plus, kỳ trả nợ trong 7 ngày tới, nợ xấu…).
- **KH 360 – Quản lý mẫu nhanh** (cả 3 tab Thống kê): chọn điều kiện rồi bấm **Lưu thành mẫu** để tạo mẫu mới; bấm một mẫu, chỉnh điều kiện rồi bấm **Lưu đè mẫu** để sửa điều kiện; nút **Quản lý mẫu** để đổi tên, đổi thứ tự, xoá, hoặc **Khôi phục mẫu mặc định** (chỉ thêm lại mẫu mặc định đã xoá, mẫu tự tạo vẫn giữ). Mẫu dùng chung cho mọi người xem được Thống kê; người chỉ được Tra cứu thì không sửa được.

### Chỉnh sửa
- **KH 360 – Thống kê theo khách hàng:** tách số dư thành **Tổng số dư tiền gửi** (TK thanh toán + tiết kiệm), **Số dư không kỳ hạn (TK thanh toán)** và **Số dư tiết kiệm / có kỳ hạn** (cộng các sổ) — mỗi loại lọc được từ … đến … ("đến 0" = chưa có sổ tiết kiệm). Bảng kết quả, ô tóm tắt và file Excel có thêm 2 cột tương ứng. Mẫu nhanh mới: TK thanh toán ≥ 50 triệu, chưa có sổ tiết kiệm. Lưu ý: tab này tính theo **khách hàng** (cộng mọi tài khoản của khách), còn tab Sổ tiết kiệm tính theo **từng sổ**, nên số lượng hai bên khác nhau là bình thường.
- **KH 360 – Tổng số dư tiền gửi:** không còn cộng số dư âm của tài khoản thấu chi (211108) vào tổng số dư tiền gửi (khoản thấu chi đã tính ở dư nợ). Tổng số dư của khách có thấu chi và của toàn chi nhánh trước đây bị thấp hơn thực tế; cần **cập nhật lại file DP01** để số liệu đúng. Hồ sơ khách hàng ghi nhãn **Thấu chi** cho các tài khoản này và hiện hình thức gửi của sổ.
- **Quản lý nhân viên:** file **Export Excel** import lại được ngay, không cần sửa tiêu đề hay thêm bớt cột (trước đây báo "Thiếu Username hoặc Mã nhân viên"). Chi nhánh, Phòng ban, Chức vụ, Nghiệp vụ ghi bằng tên (vd. "Phòng Kế toán & Ngân quỹ") hay bằng mã (KE_TOAN) đều nhận; giá trị không có trong danh sách thì báo cảnh báo và giữ giá trị cũ. Dòng trống được bỏ qua.
- Đồng bộ **Người sử dụng** và **Nhân viên**: sửa họ tên nhân viên thì họ tên tài khoản đổi theo; trang sửa Người sử dụng (Admin) hiện luôn hồ sơ nhân viên (chi nhánh, phòng ban, chức vụ, nghiệp vụ…).

### Lưu ý
- Có migration `kh360/0003_hinh_thuc_tien_gui` (thêm cột hình thức tiền gửi). Sau khi cập nhật, nạp lại DP01 để có hình thức gửi và tổng số dư đúng.
- Có migration `kh360/0004_so_du_tach_thoi_han_vay`: thêm số dư không kỳ hạn / có kỳ hạn của khách hàng và thời hạn vay; tự tính từ dữ liệu đã nạp nên không bắt buộc nạp lại file cho phần này.
- Có migration `kh360/0005_mau_thong_ke`: tạo bảng mẫu nhanh và nạp sẵn 29 mẫu mặc định (9 theo khách hàng, 9 sổ tiết kiệm, 11 tiền vay).

### File
- Thêm: `kh360/migrations/0003_hinh_thuc_tien_gui.py`, `kh360/migrations/0004_so_du_tach_thoi_han_vay.py`, `kh360/templates/kh360/thong_ke_so.html`, `kh360/templates/kh360/thong_ke_vay.html`, `kh360/templates/kh360/_thong_ke_nav.html`, `kh360/templates/kh360/_loc_chu.html`, `kh360/templates/kh360/_phan_trang.html`, `kh360/migrations/0005_mau_thong_ke.py`, `kh360/mau_mac_dinh.py`, `kh360/templates/kh360/_mau_nhanh.html`
- Sửa: `kh360/models.py`, `kh360/parsers.py`, `kh360/importer.py`, `kh360/views.py`, `kh360/urls.py`, `kh360/tests.py`, `kh360/templates/kh360/_header.html`, `kh360/templates/kh360/_ho_so.html`, `kh360/templates/kh360/thong_ke.html`, `kh360/templates/kh360/_bang_kh.html`

## 2026.11.09.2 — 09/11/2026

### Chức năng mới
- **Nhận bì thư**: quét QR trên bì thư (webcam, máy quét cầm tay hoặc dán chuỗi) để tự điền mã bì thư, loại thẻ (Visa / Ghi nợ nội địa / Phát hành lại khác CN / Smartform / Emobile), ngày phát hành và chi nhánh gốc. Báo cáo bì thư có thêm 3 cột này.
- Nút **Hướng dẫn** (biểu tượng ?) trên các trang **Khách hàng 360** và **Nhận bì thư / Báo cáo bì thư**: mở cửa sổ hướng dẫn sử dụng. Ở KH 360, phần Thống kê / Biến động / Cập nhật dữ liệu chỉ hiện với người có quyền dùng các chức năng đó.

### Chỉnh sửa
- Trang Nhận bì thư / Báo cáo bì thư bị lỗi trên máy thiếu bảng dữ liệu: tự tạo lại bảng khi cập nhật.
- Lưu xong giữ nguyên ngày nhận và người nhận để nhận tiếp bì thư sau; báo rõ khi bì thư đã được nhận trước đó.

### Lưu ý
- Có migration mới (0094, 0095): cần chạy cập nhật đầy đủ (migrate).

## 2026.11.09 — 09/11/2026

### Chức năng mới
- **Khách hàng 360** (menu **KH 360**, mọi người dùng): tra cứu một khách hàng theo mã KH, tên (gõ không dấu cũng được), CCCD, số điện thoại hoặc số tài khoản. Hồ sơ gồm: thông tin cá nhân, các sản phẩm dịch vụ đã có / chưa có (TKTT, TK số đẹp, thẻ, Agribank Plus, OTT, SMS…), tài khoản tiền gửi, khoản vay (dư nợ, nhóm nợ, kỳ trả tiếp, cán bộ tín dụng), doanh số Loa Thần tài theo từng kỳ, QR code, Ebanking tổ chức và lịch sử biến động của khách hàng.
- **Cập nhật dữ liệu KH 360:** nạp file **CN05** và **DP01** (bắt buộc), kèm **LN01**, **Thống kê doanh số Loa**, **Tổng hợp QR**, **Quản trị khách hàng tổ chức** (không bắt buộc). Có thể cập nhật bất cứ lúc nào. Nhật ký ghi "Đã cập nhật vào ngày … – dữ liệu ngày …". File nào không chọn thì giữ nguyên dữ liệu lần trước.
- **Tra cứu KH 360:** danh sách kết quả 10 dòng mỗi trang, bấm tiêu đề cột để sắp xếp (mã KH, tên, loại, hạng, số dư, dư nợ, điểm GD). Bấm **Xem** (hoặc bấm vào dòng) để mở hồ sơ thành bảng nổi, nền phía sau làm mờ. Hồ sơ chia tab: Hồ sơ 360°, Tiền gửi, Khoản vay, Dịch vụ, Loa & QR, Biến động.
- **Phân hạng khách hàng (BC06 / MSPL09):** nạp thêm file BC06 (không bắt buộc). Hạng (Platinum VIP, Gold VIP, Thân thiết…) hiện cạnh tên khách hàng, kèm điểm xếp hạng chi nhánh, lợi ích mang lại, số dư bình quân tiền gửi có kỳ hạn, tiền gửi thanh toán và tiền vay.
- **Ghi chú khách hàng:** cán bộ ghi chú ngay trong hồ sơ (nhu cầu, lịch hẹn…). Ghi chú lưu tên người sửa và thời gian, không bị mất khi cập nhật lại dữ liệu.
- **Thống kê KH 360:** lọc khách hàng theo tổng số dư tiền gửi (từ … đến …), đang vay / không vay, cá nhân / tổ chức, hạng BC06, điểm giao dịch, tuổi, có / chưa có từng dịch vụ (kết hợp nhiều điều kiện, ví dụ vừa có OTT vừa có SMS Banking), Loa, QR, Ebanking tổ chức. Có 8 mẫu lọc nhanh (tiền gửi ≥ 1 tỷ chưa có Agribank Plus, đang vay chưa có Agribank Plus…). Hiện số khách hàng, tổng số dư, tổng dư nợ; xuất Excel toàn bộ kết quả.
- **Phân quyền KH 360:** Admin dùng toàn bộ (gồm Cập nhật dữ liệu). Ban Giám đốc (Giám đốc, Phó Giám đốc, phòng Ban Giám đốc), Giám đốc / Phó Giám đốc Phòng giao dịch, Trưởng phòng, Phó phòng, Hậu kiểm viên được Tra cứu, Thống kê, Biến động.
- **Giao diện KH 360 theo kích thước màn hình:** màn rộng (1920×1080) hiện đủ cột; màn 1600×900 hoặc màn phóng to 125% ẩn bớt cột Điểm GD; màn đứng và màn nhỏ chỉ giữ Tên, Hạng, Số dư (mã KH hiện dưới tên). Bảng hồ sơ nổi cuộn được trên màn thấp, chiếm toàn màn hình trên màn nhỏ; tab hồ sơ cuộn ngang. Các chức vụ còn lại chỉ được Tra cứu.
- **Biến động KH 360:** sau mỗi lần cập nhật, liệt kê những gì mới và những gì mất so với lần trước: KH mới / mất, TK mở mới / đóng, vay mới giải ngân / tất toán, đăng ký / hủy dịch vụ, Loa mới / mất, QR mới / mất, Ebanking tổ chức mới / mất. Lọc theo kỳ và loại, xuất Excel.

### Chỉnh sửa
- **Thanh menu:** khi có nhiều mục (tài khoản Admin, tên đăng nhập dài), menu tự xuống dòng thay vì tràn ngang làm trang bị cuộn ngang và trắng nền bên phải. Mục **Khách hàng** thành menu thả xuống: Danh sách khách hàng, Khách hàng 360.

### Lưu ý
- Lần đầu nạp mỗi loại file chỉ làm **mốc**, chưa tính biến động. Biến động có từ lần nạp thứ hai.
- File ZIP tải về từ IPCAS có mật khẩu, nên phải giải nén rồi chọn file **.csv** bên trong.
- Ebanking tổ chức được ghép với khách hàng theo **tên** (file không có mã KH). Tổ chức nào không ghép được sẽ hiện ở trang Cập nhật để nhập mã KH một lần; các lần sau hệ thống tự nhớ.
- Có migration `kh360/0001_initial`, `kh360/0002_xep_hang_ghi_chu` (tạo bảng mới, không sửa bảng cũ).

### File
- Thêm: `kh360/` (models, parsers, importer, views, urls, templates, templatetags, tests, `migrations/0001_initial.py`, `migrations/0002_xep_hang_ghi_chu.py`)
- Sửa: `wordgen/settings.py`, `wordgen/urls.py`, `templates_app/templates/templates_app/base.html`

## 2026.11.05.3 — 05/11/2026

### Chức năng mới
- **Đăng ký Loa Thần tài:** nút mới trên trang Đăng ký QR / Loa, nhập Số tài khoản, Họ tên khách hàng, Địa chỉ, Số điện thoại. Sửa, xóa, đánh dấu đã in, tải danh sách (Admin) làm giống bảng QR.
- **Đăng ký bảng QR / Loa Thần tài — ô Đã in:** Admin tích ô "Đã in" sau khi in; tên người đánh dấu và thời gian hiện ở cột Đã in. Cán bộ đăng ký thấy ô này nhưng không tích được. Có thể lọc theo Đã in / Chưa in.

### Chỉnh sửa
- **Đổi tên thành Đăng ký bảng QR / Loa Thần tài; Dashboard QR thành Dashboard QR / Loa Thần tài:** Dashboard thống kê riêng bảng QR và Loa theo ngày, cán bộ, phòng giao dịch. Danh sách có thêm bộ lọc Loại và bộ đếm Loa.
- **Bộ đếm và Dashboard QR / Loa:** đếm số đã đăng ký (gồm cả chưa in) trong tháng và trong năm; Dashboard có thêm biểu đồ 12 tháng trong năm. Biểu đồ theo ngày tính đúng theo giờ Việt Nam.
- **Đăng ký bảng QR:**
  - Admin xem được toàn bộ đăng ký của tất cả các phòng ngay trên trang Đăng ký QR.
  - Bản ghi đã in thì cán bộ không sửa, xóa được nữa (Admin vẫn làm được).
  - File danh sách QR của Admin có thêm cột Trạng thái (Đã in / Chưa in); hướng dẫn sử dụng có thêm mục mới.

### Lưu ý
- Có migration `0091`, `0092`, `0093`: thêm loại đăng ký, địa chỉ, số điện thoại và ô Đã in. Các đăng ký cũ đều là loại Bảng QR, chưa in.

### File
- Thêm: `templates_app/migrations/0091_qr_trang_thai_in.py`, `templates_app/migrations/0092_qr_loa_than_tai.py`, `templates_app/migrations/0093_qr_da_in.py`, `templates_app/test_qr_registration.py`
- Sửa: `templates_app/models/registration.py`, `templates_app/qr_reg_views.py`, `templates_app/urls.py`, `templates_app/templates/templates_app/qr/registration_list.html`, `templates_app/templates/templates_app/qr/dashboard.html`, `templates_app/templates/templates_app/qr/_nav.html`, `templates_app/templates/templates_app/base.html`

## 2026.11.05 — 05/11/2026

### Chức năng mới
- **Bảng LED tỷ giá** (menu Tiện ích, cần quyền `led_board | Tỷ giá | Can change`): nhập tỷ giá mua tiền mặt, mua/bán chuyển khoản, xem lịch sử sửa tỷ giá, nhập và hiện bảng lãi suất của sản phẩm tiết kiệm đã chọn, dòng chữ chạy, ảnh trình chiếu có ngày hiệu lực và số giây riêng, xem trước khung cắt ảnh, nhắc khi chưa nhập tỷ giá, hẹn giờ tắt PC LED. PC nối bảng LED mở trang `/led/`, không cần đăng nhập, tự cập nhật sau tối đa 5 phút.

### Chỉnh sửa
- **Tạo bìa chứng từ:** nhãn QR ở trang 2 chuyển xuống giữa trang.

### File
- Thêm: `led_board/`, `scripts/led/mo_bang_led.bat`
- Sửa: `templates_app/bia_chung_tu_views.py`, `templates_app/test_bia_chung_tu.py`, `templates_app/templates/templates_app/base.html`, `wordgen/settings.py`, `wordgen/urls.py`

## 2026.11.03.2 — 03/11/2026

### Chức năng mới
- **Ghi chú cập nhật** (menu Tiện ích, giữa Cấu hình hệ thống và Quản trị; mọi người dùng đều xem được): xem các bản cập nhật đã cài, mỗi bản ghi file nào thay đổi và chức năng nào được thêm hoặc sửa. Bản máy đang chạy được đánh dấu.

### Chỉnh sửa
- Gói cập nhật tự ghi số phiên bản và ngày vào mục ghi chú của bản đó.

### File
- Thêm: `docs/GHI_CHU_CAP_NHAT.md`, `templates_app/changelog_views.py`, `templates_app/templates/templates_app/ghi_chu_cap_nhat.html`, `templates_app/test_changelog.py`
- Sửa: `templates_app/urls.py`, `templates_app/templates/templates_app/base.html`, `scripts/release/build_update.py`

## 2026.11.03 — 03/11/2026

### Chức năng mới
- **Báo cáo Lãi dự thu trên 6 tháng (GLST80)**, nằm cùng trang với Báo cáo Lãi tồn đọng: lấy các LDS của kỳ hiện tại, so với dư nợ kỳ trước, xuất theo mẫu Excel mới.

### Chỉnh sửa
- **Báo cáo Lãi tồn đọng (GLST07):** phải chọn ngày của 2 kỳ (mặc định cuối tháng trước và cuối tháng trước nữa); khách hàng doanh nghiệp xếp lên trước; cập nhật mẫu Excel.
- **Tạo bìa chứng từ:**
  - Tập trong mã QR và dòng "Tập" trên nhãn đếm riêng từng GDV (GDV có 1 tập là 1/1). "Số tập chứng từ trong ngày" vẫn là tổng của cả phòng.
  - Cập nhật hướng dẫn (.md và .docx).

### File
- Thêm: `packages/mau_lai_du_thu_6_thang.xlsx`
- Sửa: `packages/mau_lai_tondong.xlsx`, `templates_app/report_views.py`, `templates_app/urls.py`, `templates_app/templates/templates_app/base.html`, `templates_app/templates/templates_app/reports/lai_ton_dong.html`, `templates_app/templates/templates_app/reports/report_hub.html`, `templates_app/bia_chung_tu_views.py`, `templates_app/test_bia_chung_tu.py`, `docs/HUONG_DAN_TAO_BIA_CHUNG_TU.md`, `docs/HUONG_DAN_TAO_BIA_CHUNG_TU.docx`

## 2026.10.30 — 30/10/2026

### Chỉnh sửa
- **Theo dõi khoá học (Dashboard e-learning):** sửa lỗi bấm mở khoá học hoặc tích hoàn thành không có tác dụng khi mã khoá học/học viên từ 1000 trở lên (mã bị hiển thị thành "1.000").

### File
- Sửa: `templates_app/templates/templates_app/course_dashboard.html`

## 2026.10.29 — 29/10/2026

### Chỉnh sửa
- Sắp xếp lại mã nguồn: tách các file lớn `views.py`, `models.py`, `report_views.py` thành nhiều file theo từng nhóm chức năng (ATM, sao kê, khách hàng, nhân viên, e-learning, báo cáo…). **Không thay đổi chức năng.**
- Dọn tài liệu cũ, gộp hướng dẫn cài đặt vào `INSTALL_LAN.md`, viết lại `docs/README.md`.

### File
- 82 file: thêm 30, sửa 15, xoá 31, đổi chỗ 6.
- Thêm: `templates_app/models/` (14 file), các file `*_views.py` mới (`atm_views.py`, `bank_statement_views.py`, `customer_views.py`, `employee_views.py`, `elearning_views.py`, `report_*_views.py`, …)
- Sửa: `templates_app/views.py`, `templates_app/report_views.py`, `templates_app/urls.py`, `templates_app/admin.py`, `INSTALL_LAN.md`, `docs/README.md`, …
- Xoá: `templates_app/models.py` (đã tách vào thư mục `models/`), các tài liệu cũ ở thư mục gốc và `docs/`
- Đổi chỗ: các script kiểm tra cũ chuyển vào `scripts/`

## 2026.10.28.4 — 28/10/2026

### Chức năng mới
- **Đăng ký bảng QR:** nút **Hướng dẫn** (xem trên màn hình hoặc tải file Word).
- **Quản lý ATM:** nút **Hướng dẫn sử dụng** (tải file Word).
- **Phân tích sao kê:** nút **Hướng dẫn** (tải file Word).

### File
- Thêm: `docs/HUONG_DAN_PHAN_TICH_SAO_KE.md`, `docs/HUONG_DAN_PHAN_TICH_SAO_KE.docx`
- Sửa: `templates_app/qr_reg_views.py`, `templates_app/views.py`, `templates_app/urls.py`, `templates_app/templates/templates_app/atm/dashboard.html`, `templates_app/templates/templates_app/bank_statement_result.html`, `templates_app/templates/templates_app/bank_statement_upload.html`, `templates_app/templates/templates_app/qr/_nav.html`, `templates_app/test_bank_statement.py`

## 2026.10.28.3 — 28/10/2026

### Chỉnh sửa
- **Tạo bìa chứng từ:** trang bìa luôn ghi "CHI NHÁNH GIÁ RAI BẠC LIÊU"; dòng dưới theo đơn vị: Hội sở là PHÒNG KẾ TOÁN VÀ NGÂN QUỸ, Láng Tròn là PHÒNG GIAO DỊCH LÁNG TRÒN, Phường 1 là PHÒNG GIAO DỊCH PHƯỜNG 1.

### File
- Sửa: `templates_app/bia_chung_tu_views.py`, `templates_app/test_bia_chung_tu.py`

## 2026.10.28.2 — 28/10/2026

### Chức năng mới
- **Tạo bìa chứng từ:** nút **Tải hướng dẫn** (file Word).

### Chỉnh sửa
- **Tạo bìa chứng từ:** trên nhãn QR, "Người hậu kiểm chứng từ" lấy theo người có nghiệp vụ **Hậu kiểm viên** (dùng chung Hội sở và 2 PGD, không ai giữ vai trò này thì in dòng chấm); "Người đóng chứng từ" là GDV của tập đó.

### File
- Thêm: `docs/HUONG_DAN_TAO_BIA_CHUNG_TU.md`, `docs/HUONG_DAN_TAO_BIA_CHUNG_TU.docx`
- Sửa: `templates_app/bia_chung_tu_views.py`, `templates_app/urls.py`, `templates_app/templates/templates_app/bia_chung_tu/_nav.html`, `templates_app/test_bia_chung_tu.py`

## 2026.10.28 — 28/10/2026

### Chỉnh sửa
- **Tạo bìa chứng từ:** số hồ sơ PGD có hậu tố riêng (`7202LT-2026.NNNN`, `7202P1-2026.NNNN`); nhãn QR điền sẵn người hậu kiểm và người đóng chứng từ (là Trưởng/Phó phòng in bìa).
- **Đăng ký bảng QR:** thêm bộ đếm số QR đã phát hành trong tháng và tổng số QR toàn bộ.
- **Phiếu chênh lệch ATM:** Số thẻ, Số trace, ID giao dịch không còn bắt buộc; sửa lỗi phiếu nhiều giao dịch in nhầm tổng tiền ở dòng "KH: …" của giao dịch đầu tiên.

### Lưu ý
- Có thay đổi cơ sở dữ liệu (migration 0090), gói cập nhật tự chạy.

### File
- Thêm: `templates_app/migrations/0090_alter_atmdiscrepancy_card_number_and_more.py`
- Sửa: `templates_app/models.py`, `templates_app/views.py`, `templates_app/qr_reg_views.py`, `templates_app/bia_chung_tu_views.py`, `templates_app/templates/templates_app/qr/registration_list.html`, `templates_app/templates/templates_app/bia_chung_tu/cap_so.html`, `templates_app/test_bia_chung_tu.py`

## 2026.10.27.3 — 27/10/2026

### Chỉnh sửa
- **Tạo bìa chứng từ:** thêm "Số tờ của tập chứng từ" (in ở nhãn QR, để trống thì in "(…. tờ)"); file import có thêm cột **User** (GDV) và **Số tờ của tập chứng từ**; import lại cùng file thì cập nhật bìa đã có.
- **Trang chủ:** bỏ thẻ cảnh báo CCCD khách hàng sắp hết hạn trong mục "Cần chú ý".

### Lưu ý
- Có thay đổi cơ sở dữ liệu (migration 0089), gói cập nhật tự chạy.

### File
- Thêm: `templates_app/migrations/0089_bia_so_to_tap.py`
- Sửa: `templates_app/models.py`, `templates_app/views.py`, `templates_app/bia_chung_tu_views.py`, `templates_app/templates/templates_app/news_feed.html`, `templates_app/templates/templates_app/bia_chung_tu/edit.html`, `templates_app/templates/templates_app/bia_chung_tu/import.html`, `templates_app/templates/templates_app/bia_chung_tu/list.html`, `templates_app/test_bia_chung_tu.py`

## 2026.10.27.2 — 27/10/2026

### Chỉnh sửa
- **Tạo bìa chứng từ:** cột **Thứ tự in** ở màn hình Cấp số theo ngày, tự nhớ cho lần sau; ô Số bắt đầu để trống kèm nút "Dùng số gợi ý".
- **Trang chủ:** bỏ dòng đếm CCCD đã hết hạn.

### Lưu ý
- Có thay đổi cơ sở dữ liệu (migration 0088), gói cập nhật tự chạy.

### File
- Thêm: `templates_app/migrations/0088_bia_thu_tu_in.py`
- Sửa: `templates_app/models.py`, `templates_app/views.py`, `templates_app/bia_chung_tu_views.py`, `templates_app/templates/templates_app/bia_chung_tu/cap_so.html`, `templates_app/templates/templates_app/news_feed.html`, `templates_app/test_bia_chung_tu.py`

## 2026.10.27 — 27/10/2026

### Chức năng mới
- **Tạo bìa chứng từ** (menu Kế toán Ngân quỹ): cấp số hồ sơ theo ngày cho các GDV, import bìa cũ từ Excel, sửa/xoá, in PDF bìa M01/LHS kèm nhãn mã QR. Dành cho Trưởng/Phó phòng Kế toán.
- **Tìm chức năng** (biểu tượng kính lúp trên thanh menu hoặc Ctrl+K): gõ tên để mở nhanh chức năng.
- **Trang chủ:** mục "Cần chú ý" (công việc quá hạn/sắp đến hạn, hồ sơ HĐV chờ duyệt…).
- **Đăng ký bảng QR:** Admin tải được danh sách QR của tất cả cán bộ ra Excel.
- Ghi nhật ký hệ thống vào thư mục `logs/` (phục vụ tra lỗi).

### Lưu ý
- Có thay đổi cơ sở dữ liệu (migration 0087), gói cập nhật tự chạy.

### File
- Thêm: `templates_app/bia_chung_tu_views.py`, `templates_app/migrations/0087_bia_chung_tu.py`, `templates_app/templates/templates_app/bia_chung_tu/` (5 file), `templates_app/test_bia_chung_tu.py`
- Sửa: `.gitignore`, `scripts/release/build_update.py`, `templates_app/models.py`, `templates_app/views.py`, `templates_app/urls.py`, `templates_app/qr_reg_views.py`, `templates_app/td_views.py`, `templates_app/templates/templates_app/base.html`, `templates_app/templates/templates_app/news_feed.html`, `templates_app/templates/templates_app/qr/registration_list.html`, `wordgen/settings.py`
- Xoá: `templates_app/templates/templates_app/test_address_selector.html`

## 2026.10.25 — 25/10/2026

### Chỉnh sửa
- **Phân tích sao kê:** nhận đúng mã và tên ngân hàng chuyển trong file FXIR64; giao dịch chuyển tiền ra TK Agribank khác được ghi là "Chuyển khoản nội bộ Agribank" kèm số TK nhận.

### File
- Sửa: `templates_app/bank_statement_enricher.py`, `templates_app/bank_statement_parser.py`, `templates_app/test_bank_statement.py`

## 2026.10.23.2 — 23/10/2026

### Chức năng mới
- **Phân tích sao kê:** nhận thêm file FX (FXIR64 chiều đến, FXOR88 chiều đi) để bổ sung tên, số TK, ngân hàng đối tác; tra tên ngân hàng theo bảng mã CITAD; nhận diện giao dịch nộp thuế điện tử và phí kèm theo.

### File
- Thêm: `templates_app/data/citad_codes.json`
- Sửa: `templates_app/bank_statement_enricher.py`, `templates_app/bank_statement_parser.py`, `templates_app/views.py`, `templates_app/templates/templates_app/bank_statement_upload.html`, `templates_app/test_bank_statement.py`

## 2026.10.23 — 23/10/2026

### Chỉnh sửa
- **Báo cáo Phát hành thẻ:** chọn theo **tháng** thay cho quý.
- **Chụp chữ ký khách hàng:** khung chữ ký kéo di chuyển và co giãn được (thanh trượt hoặc lăn chuột), máy nhớ cỡ khung cho lần sau.

### File
- Sửa: `templates_app/report_views.py`, `templates_app/urls.py`, `templates_app/static/js/signature_capture.js`, `templates_app/templates/templates_app/customer_list.html`, `templates_app/templates/templates_app/reports/phat_hanh_the.html`

## 2026.10.22.2 — 22/10/2026

### Chỉnh sửa
- **Ngân hàng câu hỏi trắc nghiệm:** sửa lỗi cập nhật dừng giữa chừng khi một câu hỏi bị import 2 lần vào cùng một đề.

### File
- Sửa: `quiz/migrations/0003_question_bank_m2m.py`

## 2026.10.22 — 22/10/2026

### Chức năng mới
- Bản đầu tiên cập nhật bằng USB: chép thư mục cập nhật vào máy, chạy `cap_nhat.bat` (tự sao lưu dữ liệu trước khi cập nhật); `khoi_phuc.bat` để quay lại bản trước. Số phiên bản hiện ở chân trang.

### File
- Gói đầy đủ: toàn bộ mã nguồn.

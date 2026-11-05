# Ghi chú cập nhật

Mỗi mục là một bản cập nhật (gói `CapNhat_MauBieu_<phiên bản>`), mới nhất ở trên.
Mục "Bản tiếp theo" là các thay đổi chưa đóng gói. Khi chạy `tao_ban_cap_nhat.bat`, tiêu đề này được đổi thành số phiên bản và ngày.

## Bản tiếp theo

### Chức năng mới
- **Bảng LED tỷ giá** (menu Tiện ích, cần quyền `led_board | Tỷ giá | Can change`): nhập tỷ giá mua/bán tiền mặt và chuyển khoản, xem lịch sử sửa tỷ giá, nhập và hiện bảng lãi suất của sản phẩm tiết kiệm đã chọn, dòng chữ chạy, ảnh trình chiếu có ngày hiệu lực và số giây riêng, xem trước khung cắt ảnh, nhắc khi chưa nhập tỷ giá, hẹn giờ tắt PC LED. PC nối bảng LED mở trang `/led/`, không cần đăng nhập, tự cập nhật sau tối đa 5 phút.

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

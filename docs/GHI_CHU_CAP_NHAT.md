# Ghi chú cập nhật

Mỗi mục là một bản cập nhật (gói `CapNhat_MauBieu_<phiên bản>`), mới nhất ở trên.
Mục "Bản tiếp theo" là các thay đổi chưa đóng gói. Khi chạy `tao_ban_cap_nhat.bat`, tiêu đề này được đổi thành số phiên bản và ngày.

## Bản tiếp theo

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

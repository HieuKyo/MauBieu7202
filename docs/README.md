# Hệ thống Mẫu biểu - Agribank Chi nhánh Giá Rai Bạc Liêu

Ứng dụng web Django chạy trong mạng LAN nội bộ (offline): tạo file Word từ mẫu có sẵn, quản lý khách hàng, báo cáo nghiệp vụ, kế toán ngân quỹ, ATM, tín dụng...

## Bắt đầu nhanh

```cmd
setup.bat     :: lần đầu: cài thư viện từ packages/, tạo database, thu thập CSS/JS
run.bat       :: chạy server -> http://10.135.7.108:8888
```

Hướng dẫn đầy đủ (cài đặt, cấu hình `.env`, cập nhật bằng gói USB, sao lưu, sửa lỗi): [INSTALL_LAN.md](../INSTALL_LAN.md)

## Tài liệu

### Cài đặt & vận hành (thư mục gốc)

| Tài liệu | Nội dung |
|---|---|
| [INSTALL_LAN.md](../INSTALL_LAN.md) | Cài đặt, chạy, cập nhật, sao lưu, sửa lỗi |
| [HUONG_DAN_CAI_DAT_CHI_TIET.md](../HUONG_DAN_CAI_DAT_CHI_TIET.md) | Thư mục mẫu biểu offline `maubieumoi` (hybrid storage) từng bước |
| [HUONG_DAN_SETUP_MAUBIEU.md](../HUONG_DAN_SETUP_MAUBIEU.md) | Các giải pháp lưu trữ mẫu biểu (vấn đề mẫu "hết hạn") |
| [HUONG_DAN_SUBDIRECTORIES.md](../HUONG_DAN_SUBDIRECTORIES.md) | Tổ chức mẫu biểu theo thư mục con |
| [ATM_DEPLOYMENT_SUMMARY.md](../ATM_DEPLOYMENT_SUMMARY.md) | Triển khai module ATM, dữ liệu ban đầu |

### Soạn mẫu biểu Word

| Tài liệu | Nội dung |
|---|---|
| [HUONG_DAN_CAP_NHAT_BIEN.md](../HUONG_DAN_CAP_NHAT_BIEN.md) | Hệ thống biến trong mẫu biểu |
| [AUTO_CALCULATION_GUIDE.md](../AUTO_CALCULATION_GUIDE.md) | Tính toán tự động bằng Jinja2 |
| [HUONG_DAN_CHECKBOX_WORD.md](../HUONG_DAN_CHECKBOX_WORD.md) | Checkbox trong mẫu (ký tự Unicode và Content Control) |
| [HUONG_DAN_CONTENT_CONTROL_CHECKBOX.md](../HUONG_DAN_CONTENT_CONTROL_CHECKBOX.md) | Tạo checkbox Content Control và bảng tên tag |

### Sử dụng chức năng

| Tài liệu | Nội dung |
|---|---|
| [FEATURES.md](FEATURES.md) | Danh sách chức năng |
| [HUONG_DAN_CLIPBOARD_IMPORT.md](HUONG_DAN_CLIPBOARD_IMPORT.md) | Import khách hàng: dán dữ liệu từ AGRIBANK |
| [HUONG_DAN_IMPORT_AGRIBANK.md](HUONG_DAN_IMPORT_AGRIBANK.md) | Import khách hàng: chọn file TSV/TXT |
| [AGRIBANK_TSV_IMPORT_GUIDE.md](AGRIBANK_TSV_IMPORT_GUIDE.md) | Import TSV cho kỹ thuật: API, script dòng lệnh |
| [HUONG_DAN_PHAN_TICH_SAO_KE.md](HUONG_DAN_PHAN_TICH_SAO_KE.md) | Phân tích sao kê |
| [HUONG_DAN_TAO_BIA_CHUNG_TU.md](HUONG_DAN_TAO_BIA_CHUNG_TU.md) | Tạo bìa chứng từ |
| [tax_payment/TROUBLESHOOTING.md](../tax_payment/TROUBLESHOOTING.md) | Sửa lỗi bảng kê nộp thuế |

### Kỹ thuật

| Tài liệu | Nội dung |
|---|---|
| [CODE_QUALITY_AUDIT_REPORT.md](../CODE_QUALITY_AUDIT_REPORT.md) | Báo cáo rà soát chất lượng mã nguồn |

## Cấu trúc mã nguồn

```
MauBieu7202/
├── setup.bat, run.bat           # cài đặt / chạy server (Waitress, cổng 8888)
├── tao_ban_cap_nhat.bat         # tạo gói cập nhật USB (scripts/release/)
├── download_offline_packages.bat, verify_packages.bat
├── packages/                    # file .whl cài offline
├── wordgen/                     # cấu hình Django (settings.py, urls.py)
├── templates_app/               # app chính
│   ├── models/                  # model chia theo nhóm (template, customer, atm, cash, ...)
│   ├── views.py                 # trang chủ, in mẫu biểu, cấu hình chi nhánh
│   ├── *_views.py               # view theo chức năng (customer_views, atm_views, report_*_views, ...)
│   └── templates/, static/
├── salary/, payroll_statistics/, tax_payment/, kpi_tool/, tasks/,
│   savings_calculator/, quiz/, messaging/, document_registry/   # các app khác
├── scripts/                     # script hỗ trợ (kiểm tra mẫu, chẩn đoán thuế, phát hành)
└── docs/                        # tài liệu sử dụng
```

Nội bộ Agribank Chi nhánh Giá Rai Bạc Liêu.

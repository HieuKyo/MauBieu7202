# Công cụ Tính KPI Tự động - Agribank

## Giới thiệu

Ứng dụng web Streamlit để tự động hóa tính điểm KPI hàng ngày cho Giao dịch viên (GDV) dựa trên file Excel mẫu và các file số liệu chi tiết.

## Tính năng

- ✅ Tự động tính KPI dựa trên dữ liệu Thẻ, SMS, E-Mobile Banking
- ✅ Hỗ trợ nhiều GDV với selectbox
- ✅ Tự động mapping dữ liệu vào file Excel mẫu
- ✅ Tính toán tổng và bút toán quy đổi
- ✅ Xuất báo cáo Excel với định dạng giữ nguyên
- ✅ Giao diện thân thiện, dễ sử dụng

## Cấu trúc File

```
kpi_dashboard/
├── __init__.py              # Package initialization
├── app.py                   # Main Streamlit application
├── data_processor.py        # Module xử lý dữ liệu từ file nguồn
├── kpi_calculator.py        # Module tính toán và cập nhật KPI
├── README.md               # File hướng dẫn này
└── sample_data/            # Thư mục chứa file dữ liệu mẫu (nếu có)
```

## Cài đặt

### 1. Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

### 2. Chạy ứng dụng

```bash
cd kpi_dashboard
streamlit run app.py
```

Ứng dụng sẽ mở tại địa chỉ: `http://localhost:8501`

## Hướng dẫn sử dụng

### Bước 1: Chọn Tháng/Năm và Mã GDV

Tại sidebar bên trái:
- Chọn **Tháng** và **Năm** báo cáo
- Chọn **Mã GDV** từ danh sách dropdown

### Bước 2: Upload Files

Upload các file dữ liệu:

1. **File KPI Mẫu** (bắt buộc):
   - File Excel chứa template KPI cần điền
   - Phải có dòng header chứa các số ngày (1, 2, 3...31)
   - Phải có các dòng KPI với STT hoặc từ khóa tương ứng

2. **File Dữ liệu Thẻ** (tùy chọn):
   - Cột `dlvrydt`: Ngày phát hành (format: dd/mm/yyyy)
   - Cột `dlvryusrid`: User ID
   - Cột `isutycd`: Loại phát hành ("New Issue" hoặc khác)

3. **File Dữ liệu SMS** (tùy chọn):
   - Cột `entydt`: Ngày đăng ký (format: yyyy-mm-dd)
   - Cột `crtusr`: User ID

4. **File Dữ liệu E-Mobile** (tùy chọn):
   - Cột `entydt`: Ngày đăng ký
   - Cột `crtusr`: User ID

### Bước 3: Phân tích và Xuất báo cáo

- Nhấn nút **"🚀 Phân tích & Xuất Báo cáo"**
- Chờ quá trình xử lý hoàn tất
- Xem thống kê tổng hợp
- Nhấn **"⬇️ Tải xuống báo cáo KPI"** để download file Excel kết quả

## Cấu trúc File KPI Mẫu

File Excel mẫu cần có:

### Header Row
Dòng chứa các số ngày từ 1 đến 31 (hoặc số ngày trong tháng)

### Các dòng KPI

Hệ thống tự động tìm các dòng sau:

| STT | Nội dung | Từ khóa tìm kiếm | Nguồn dữ liệu |
|-----|----------|------------------|---------------|
| 1 | Đăng ký TT KH cá nhân (CIF) | "đăng ký tt kh" | Thẻ mới (New Issue) |
| 3 | Quét chữ ký KH | "chữ ký" | New Issue × 2 |
| 4 | GDV lưu trữ HS | "lưu trữ" | Thẻ + SMS + E-Mobile |
| 9 | Đăng ký SMS | "sms" | File SMS |
| 12 | Phát hành thẻ | "phát hành thẻ" | File Thẻ (tất cả) |

### Cột tổng hợp

- **Cộng**: Tổng số lượng (tự động tính)
- **Bút toán quy đổi**: Tổng × Hệ số (tự động tính)

## Hệ số quy đổi mặc định

- Phát hành thẻ: **3.0**
- Quét chữ ký: **3.0**
- Đăng ký SMS: **4.0**
- Lưu trữ hồ sơ: **0.5**
- CIF mới: **3.0**

*Có thể điều chỉnh trong phần "Hệ số KPI" tại sidebar*

## Logic tính toán

Với mỗi ngày trong tháng:

```
Count_Card = Tổng số dòng trong file Thẻ
Count_NewIssue = Số dòng có isutycd = "New Issue"
Count_SMS = Tổng số dòng trong file SMS
Count_EMobile = Tổng số dòng trong file E-Mobile

Phát hành thẻ (STT 12) = Count_Card
Quét chữ ký (STT 3) = Count_NewIssue × 2
CIF mới (STT 1) = Count_NewIssue
Đăng ký SMS (STT 9) = Count_SMS
Lưu trữ HS (STT 4) = Count_Card + Count_SMS + Count_EMobile
```

## Xử lý lỗi

Ứng dụng có xử lý các lỗi phổ biến:

- ❌ Thiếu file KPI mẫu
- ❌ File dữ liệu thiếu cột bắt buộc
- ❌ Không tìm thấy header row trong file mẫu
- ❌ Không tìm thấy các dòng KPI trong file mẫu
- ❌ Lỗi format ngày tháng

## Lưu ý

1. **Format ngày tháng**:
   - File Thẻ: `dd/mm/yyyy` (VD: 15/03/2024)
   - File SMS và E-Mobile: `yyyy-mm-dd` (VD: 2024-03-15)

2. **User ID**: Phải khớp chính xác với danh sách GDV

3. **File mẫu**: Không thay đổi cấu trúc file mẫu (vị trí dòng, cột)

4. **Dữ liệu ngoài tháng**: Các ngày nằm ngoài tháng báo cáo sẽ tự động bị loại bỏ

## Hỗ trợ

Nếu gặp vấn đề, vui lòng kiểm tra:
- Format file dữ liệu đúng chuẩn
- Tên các cột trong file nguồn chính xác
- File mẫu có đầy đủ các dòng KPI cần thiết
- User ID khớp với dữ liệu

## Phiên bản

- **v1.0.0** - Phiên bản đầu tiên (2026-01-05)

## Tác giả

Agribank - Banking KPI Team

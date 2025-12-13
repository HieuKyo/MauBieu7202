# BÁO CÁO ĐỒ ÁN TỐT NGHIỆP

---

## HỆ THỐNG QUẢN LÝ VÀ TẠO MẪU BIỂU TỰ ĐỘNG CHO AGRIBANK

### WORD TEMPLATE MANAGEMENT SYSTEM FOR AGRIBANK

---

**Đơn vị thực hiện:** Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank)
**Chi nhánh:** Giá Rai - Bạc Liêu
**Năm thực hiện:** 2025

---

# MỤC LỤC

**CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI** .......................................................... 1
- 1.1. Đặt vấn đề (Tính cấp thiết của đề tài) ............................................ 1
- 1.2. Mục tiêu của đề tài .................................................................. 2
- 1.3. Đối tượng và phạm vi nghiên cứu .................................................. 3
- 1.4. Phương pháp nghiên cứu ............................................................ 4
- 1.5. Bố cục của báo cáo ................................................................... 5

**CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ PHÂN TÍCH HIỆN TRẠNG** ......................... 6
- 2.1. Cơ sở lý thuyết ......................................................................... 6
- 2.2. Khảo sát và phân tích hiện trạng ................................................. 14
- 2.3. Phân tích yêu cầu hệ thống ........................................................ 16

**CHƯƠNG 3: THIẾT KẾ HỆ THỐNG** ........................................................ 22
- 3.1. Lựa chọn công nghệ .................................................................. 22
- 3.2. Thiết kế kiến trúc hệ thống ........................................................ 25
- 3.3. Thiết kế chức năng (UML) ........................................................... 27
- 3.4. Thiết kế cơ sở dữ liệu ............................................................... 35
- 3.5. Thiết kế giao diện (UI/UX) ......................................................... 42

**CHƯƠNG 4: CÀI ĐẶT VÀ THỬ NGHIỆM** .................................................. 46
- 4.1. Môi trường cài đặt ................................................................... 46
- 4.2. Cài đặt các module chức năng chính ............................................. 47
- 4.3. Kết quả cài đặt (Giao diện chương trình) ...................................... 54
- 4.4. Kiểm thử (Testing) .................................................................... 58

**CHƯƠNG 5: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN** ...................................... 62
- 5.1. Kết luận (Những kết quả đạt được) .............................................. 62
- 5.2. Ưu điểm và Nhược điểm ............................................................. 63
- 5.3. Hướng phát triển tương lai ......................................................... 64

**TÀI LIỆU THAM KHẢO** ....................................................................... 66

**PHỤ LỤC** ........................................................................................ 67

---

# DANH MỤC HÌNH ẢNH

Hình 2.1: Kiến trúc Django MVT Pattern ...................................................... 8
Hình 2.2: Quy trình xử lý template với Jinja2 ............................................... 10
Hình 3.1: Sơ đồ kiến trúc tổng quan hệ thống .............................................. 26
Hình 3.2: Use Case Diagram - Tổng quan hệ thống ........................................ 28
Hình 3.3: Use Case Diagram - Quản lý khách hàng ........................................ 29
Hình 3.4: Sequence Diagram - Tạo mẫu biểu từ template ............................... 31
Hình 3.5: Activity Diagram - Quy trình tạo tài liệu ....................................... 33
Hình 3.6: ERD - Sơ đồ quan hệ thực thể ..................................................... 36
Hình 3.7: Database Schema - Chi tiết các bảng ............................................. 38
Hình 3.8: Wireframe - Trang Dashboard ...................................................... 43
Hình 3.9: Wireframe - Quản lý khách hàng .................................................. 44
Hình 4.1: Giao diện Dashboard - Trang chủ ................................................. 55
Hình 4.2: Giao diện quản lý khách hàng ..................................................... 56
Hình 4.3: Giao diện tạo mẫu biểu .............................................................. 57
Hình 4.4: Kết quả kiểm thử chức năng import AGRIBANK ................................ 60

---

# DANH MỤC BẢNG BIỂU

Bảng 2.1: So sánh các framework Python .................................................... 7
Bảng 2.2: Phân tích yêu cầu chức năng ...................................................... 18
Bảng 2.3: Phân tích yêu cầu phi chức năng ................................................. 20
Bảng 3.1: Technology Stack của hệ thống ................................................... 23
Bảng 3.2: Mô tả chi tiết các Use Case ....................................................... 30
Bảng 3.3: Đặc tả bảng Customer ............................................................... 39
Bảng 3.4: Đặc tả bảng Template ............................................................... 40
Bảng 3.5: Đặc tả bảng GlobalConfig .......................................................... 41
Bảng 4.1: Cấu hình phần cứng và phần mềm ............................................... 46
Bảng 4.2: Test Cases - Chức năng tạo mẫu biểu ........................................... 59
Bảng 4.3: Test Cases - Chức năng import khách hàng .................................... 60
Bảng 4.4: Kết quả kiểm thử tổng hợp ........................................................ 61

---

# DANH MỤC TỪ VIẾT TẮT

| Từ viết tắt | Nghĩa đầy đủ |
|-------------|--------------|
| AGRIBANK | Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam |
| MVT | Model-View-Template |
| MVC | Model-View-Controller |
| ORM | Object-Relational Mapping |
| WSGI | Web Server Gateway Interface |
| API | Application Programming Interface |
| REST | Representational State Transfer |
| CRUD | Create, Read, Update, Delete |
| UI | User Interface |
| UX | User Experience |
| ERD | Entity-Relationship Diagram |
| UML | Unified Modeling Language |
| CCCD | Căn cước công dân |
| CIF | Customer Information File |
| TSV | Tab-Separated Values |
| CSV | Comma-Separated Values |
| PDF | Portable Document Format |
| DOCX | Office Open XML Document |
| HTML | HyperText Markup Language |
| CSS | Cascading Style Sheets |
| JS | JavaScript |

---


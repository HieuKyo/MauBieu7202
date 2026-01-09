# Hướng dẫn Sửa Quy tắc Quy đổi

## Tóm tắt Vấn đề

Sau khi phân tích chi tiết, phát hiện các vấn đề logic nghiêm trọng trong hệ thống chấm điểm:

### ✅ Vấn đề 1: Logic khớp quá rộng - ĐÃ SỬA
**Mô tả**: Giao dịch "Nộp tiền" (101101 - 421101) bị tính thành "Mở tài khoản" do quy tắc chung (101 - 421) khớp trước quy tắc cụ thể.

**Giải pháp**: Đã sửa logic matching trong `services.py` để ưu tiên quy tắc cụ thể hơn:
- Exact match được ưu tiên cao nhất (+10000 điểm)
- Prefix match được ưu tiên theo độ dài pattern (pattern dài hơn = cụ thể hơn)
- Hệ thống bây giờ tìm TẤT CẢ quy tắc khớp và chọn quy tắc cụ thể nhất

### ⚠️ Vấn đề 2: Quy tắc quá chi tiết - CẦN CẬP NHẬT FILE BAK

**Giao dịch**: Nợ 421101 / Có 711022 (Thu phí dịch vụ)

**Quy tắc hiện tại**:
```
FX421 711001 - "Tra soát + thu phí tra soát"
```

**Vấn đề**: Giao dịch có đuôi ...22 nhưng quy tắc cứng là ...01

**Giải pháp**: Sửa file quy tắc `hesoquydoi.BAK`:

| Trước | Sau |
|-------|-----|
| TKCO = `711001` | TKCO = `711` |

**Lý do**: Pattern `711` sẽ bao quát tất cả loại phí (711001, 711022, 711035, v.v.)

**Cách sửa**:
1. Mở file `hesoquydoi.BAK` (hoặc file DBF tương tự)
2. Tìm dòng có `CODE='FX421'` và `TKCO='711001'`
3. Sửa `TKCO` từ `711001` thành `711`
4. Import lại file quy tắc vào hệ thống

### ⚠️ Vấn đề 3: Thiếu quy tắc Rút tiền - CẦN THÊM DÒNG MỚI

**Giao dịch**: Nợ 421101 / Có 101101 (Rút tiền mặt)

**Quy tắc hiện có**: Chỉ có `DP101 421` (Nộp tiền/Mở TK - chiều Nợ 101 / Có 421)

**Vấn đề**: Không có quy tắc cho chiều ngược lại (Rút tiền)

**Giải pháp**: Thêm dòng mới vào file `hesoquydoi.BAK`:

```
CODE      : WD421  (hoặc tên tùy ý, ví dụ: RUT421)
TKNO      : 421
TKCO      : 101
HESOQUAY1 : 1.0    (điều chỉnh điểm theo quy định)
HESOQUAY2 : 0
GHICHU    : Rút tiền mặt từ tài khoản
```

**Lưu ý**:
- `HESOQUAY1` nên được điều chỉnh theo quy định KPI của ngân hàng (có thể khác với điểm nộp tiền)
- Nếu "Rút tiền" không được tính điểm KPI, có thể set `HESOQUAY1 = 0`

### ⚠️ Vấn đề 4: Thiếu quy tắc Agripay Thu tiền - CẦN THÊM DÒNG MỚI

**Giao dịch**: Nợ 101101 / Có 459901 (Thu tiền Agripay)

**Quy tắc hiện có**: Chỉ có `FX459 101101` (Chi tiền - Nợ 459 / Có 101)

**Vấn đề**: Không có quy tắc cho chiều ngược lại (Thu tiền)

**Giải pháp**: Thêm dòng mới vào file `hesoquydoi.BAK`:

```
CODE      : RX459  (hoặc tên tùy ý, ví dụ: AGRIPAY_THU)
TKNO      : 101
TKCO      : 459
HESOQUAY1 : 1.0    (điều chỉnh điểm theo quy định)
HESOQUAY2 : 0
GHICHU    : Thu tiền dịch vụ Agripay
```

**Lưu ý**:
- Pattern `101` và `459` sẽ khớp với tất cả tài khoản bắt đầu bằng số đó
- Nếu cần cụ thể hơn (chỉ Agripay), có thể dùng `101101` và `459901`

## Quy trình Cập nhật Quy tắc

### Bước 1: Sửa file hesoquydoi.BAK

Sử dụng phần mềm chỉnh sửa DBF (ví dụ: DBF Viewer, LibreOffice Base) để:

1. **Sửa quy tắc hiện có** (Vấn đề 2):
   - Tìm dòng `FX421`
   - Sửa `TKCO` từ `711001` thành `711`

2. **Thêm quy tắc mới** (Vấn đề 3 & 4):
   - Thêm dòng cho "Rút tiền": `WD421 | 421 | 101 | 1.0 | 0 | Rút tiền mặt`
   - Thêm dòng cho "Agripay Thu": `RX459 | 101 | 459 | 1.0 | 0 | Thu tiền Agripay`

### Bước 2: Import lại quy tắc

1. Truy cập: `http://localhost:8000/kpi-tool/import-rules/`
2. Upload file `hesoquydoi.BAK` đã sửa
3. Hệ thống sẽ tự động cập nhật quy tắc (update_or_create)

### Bước 3: Xử lý lại file giao dịch (nếu cần)

Nếu cần tính lại điểm cho các file đã upload:

**Option 1**: Upload lại file DBF
- Hệ thống sẽ tạo batch mới với quy tắc mới

**Option 2**: Viết script migration (nâng cao)
- Xóa các batch cũ và xử lý lại từ file gốc
- Hoặc cập nhật lại `matched_rule` và `score` cho các giao dịch hiện có

## Kiểm tra Kết quả

Sau khi cập nhật quy tắc, kiểm tra:

1. **Trang danh sách quy tắc**: `http://localhost:8000/kpi-tool/rules/`
   - Đảm bảo các quy tắc mới đã được import
   - Kiểm tra pattern đúng như mong đợi

2. **Upload file test**:
   - Upload lại file DBF có các giao dịch vấn đề
   - Kiểm tra chi tiết batch để xem các giao dịch đã khớp đúng quy tắc chưa

3. **So sánh kết quả**:
   - Giao dịch "Nộp tiền" (101101-421101) phải khớp quy tắc cụ thể, KHÔNG phải "Mở tài khoản"
   - Giao dịch "Rút tiền" (421101-101101) phải khớp quy tắc "Rút tiền", KHÔNG còn "Không khớp"
   - Giao dịch "Thu phí" (421101-711022) phải khớp quy tắc "Thu phí", KHÔNG còn "Không khớp"
   - Giao dịch "Agripay Thu" (101101-459901) phải khớp quy tắc "Agripay Thu", KHÔNG còn "Không khớp"

## Lưu ý Quan trọng

### Về Điểm KPI

**Trước khi thêm quy tắc mới, hãy xác nhận với bộ phận KPI**:
- "Rút tiền" có được tính điểm KPI không?
- "Thu tiền Agripay" có được tính điểm KPI không?
- Nếu có, mỗi nghiệp vụ được bao nhiêu điểm?

**Ví dụ điều chỉnh điểm**:
```
# Nếu "Rút tiền" được 0.5 điểm
HESOQUAY1 = 0.5

# Nếu "Rút tiền" KHÔNG được tính điểm
HESOQUAY1 = 0
```

### Về Pattern Matching

**Quy tắc thumb**:
- **Dùng pattern ngắn** (ví dụ: `711`, `421`) khi muốn bao quát nhiều tài khoản con
- **Dùng pattern dài** (ví dụ: `711001`, `421101`) khi muốn cụ thể cho 1 tài khoản
- Hệ thống đã được sửa để **tự động ưu tiên quy tắc cụ thể hơn**

**Ví dụ**:
```
# Có 2 quy tắc:
1. CODE=GEN, TKNO=101, TKCO=421, HESOQUAY1=1.0
2. CODE=SPEC, TKNO=101101, TKCO=421101, HESOQUAY1=2.0

# Giao dịch: 101101 - 421101
# Kết quả: Khớp quy tắc SPEC (2.0 điểm) - quy tắc cụ thể hơn

# Giao dịch: 101999 - 421999
# Kết quả: Khớp quy tắc GEN (1.0 điểm) - chỉ quy tắc này khớp
```

## Tổng kết

- ✅ **Vấn đề 1**: Đã sửa code - hệ thống tự động ưu tiên quy tắc cụ thể
- ⚠️ **Vấn đề 2**: Cần sửa file BAK - đổi `711001` thành `711`
- ⚠️ **Vấn đề 3**: Cần thêm quy tắc "Rút tiền" vào file BAK
- ⚠️ **Vấn đề 4**: Cần thêm quy tắc "Agripay Thu" vào file BAK

**Thứ tự ưu tiên**:
1. Sửa logic code (✅ Đã xong)
2. Cập nhật file quy tắc theo hướng dẫn trên
3. Import lại quy tắc
4. Test với file DBF thực tế
5. Xử lý lại các batch cũ nếu cần

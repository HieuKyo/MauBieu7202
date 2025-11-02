#!/usr/bin/env python3
"""
Phân tích cấu trúc dữ liệu clipboard từ hệ thống AGRIBANK
"""

# Đọc file
with open('sample_clipboard_data.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Tách header và data
header = lines[0].strip().split('\t')
data = lines[1].strip().split('\t')

print("=" * 80)
print("PHÂN TÍCH DỮ LIỆU CLIPBOARD AGRIBANK")
print("=" * 80)
print(f"\nTổng số trường: {len(header)}")
print(f"Tổng số giá trị: {len(data)}")
print("\n" + "=" * 80)
print("MAPPING DỮ LIỆU:")
print("=" * 80)

# Mapping với model Customer
mapping = {
    'custno': ('Mã khách hàng', 'ma_khach_hang / cif'),
    'nm': ('Họ tên (tiếng Anh)', 'Không dùng'),
    'nmloc': ('Họ tên (tiếng Việt)', 'ho_ten'),
    'name_4': ('Số điện thoại', 'so_dien_thoai'),
    'name_3': ('Giới tính', 'gioi_tinh'),
    'name_1': ('Ngày sinh (YYYYMMDD)', 'ngay_sinh'),
    'regno': ('Số CMND/CCCD', 'so_cmnd'),
    'passno': ('Số hộ chiếu', 'Thêm mới'),
    'addr1loc': ('Địa chỉ', 'dia_chi'),
    'issueby1': ('Nơi cấp CCCD (mã)', 'noi_cap_cmnd'),
    'issuedt1': ('Ngày cấp (YYYYMMDD)', 'ngay_cap_cmnd'),
    'profnm': ('Nghề nghiệp', 'nghe_nghiep'),
    'province': ('Mã tỉnh/thành', 'Thêm mới'),
    'district': ('Mã quận/huyện', 'Thêm mới'),
    'commune_ward': ('Mã phường/xã', 'Thêm mới'),
    'ctrycdnatl': ('Quốc tịch', 'Thêm mới'),
    'taxno': ('Mã số thuế', 'Thêm mới'),
    'emailaddr': ('Email', 'email'),
}

print(f"\n{'Field':<20} {'Value':<30} {'Description':<30} {'Mapping':<30}")
print("-" * 110)

for i, field_name in enumerate(header):
    value = data[i] if i < len(data) else ''
    # Làm sạch giá trị hiển thị
    display_value = value.strip() if value.strip() else '(trống)'
    if len(display_value) > 28:
        display_value = display_value[:25] + '...'

    if field_name in mapping:
        desc, model_field = mapping[field_name]
        print(f"{field_name:<20} {display_value:<30} {desc:<30} -> {model_field:<30}")

print("\n" + "=" * 80)
print("DỮ LIỆU QUAN TRỌNG CẦN XỬ LÝ:")
print("=" * 80)

important_data = [
    ('custno', 'Mã KH'),
    ('nmloc', 'Họ tên'),
    ('name_1', 'Ngày sinh'),
    ('name_3', 'Giới tính'),
    ('name_4', 'SĐT'),
    ('regno', 'CMND'),
    ('issuedt1', 'Ngày cấp'),
    ('issueby1', 'Nơi cấp'),
    ('addr1loc', 'Địa chỉ'),
    ('profnm', 'Nghề nghiệp'),
]

for field, label in important_data:
    idx = header.index(field)
    value = data[idx] if idx < len(data) else ''
    print(f"{label:<15}: {value}")

# Phân tích định dạng ngày
print("\n" + "=" * 80)
print("PHÂN TÍCH ĐỊNH DẠNG NGÀY:")
print("=" * 80)

name_1_idx = header.index('name_1')
issuedt1_idx = header.index('issuedt1')

birth_date_raw = data[name_1_idx]
issue_date_raw = data[issuedt1_idx]

print(f"Ngày sinh raw: {birth_date_raw} (format: YYYYMMDD)")
if len(birth_date_raw) == 8:
    year = birth_date_raw[:4]
    month = birth_date_raw[4:6]
    day = birth_date_raw[6:8]
    print(f"  -> Converted: {year}-{month}-{day}")

print(f"\nNgày cấp raw: {issue_date_raw} (format: YYYYMMDD)")
if len(issue_date_raw) == 8:
    year = issue_date_raw[:4]
    month = issue_date_raw[4:6]
    day = issue_date_raw[6:8]
    print(f"  -> Converted: {year}-{month}-{day}")

print("\n" + "=" * 80)
print("MÃ NƠI CẤP CCCD:")
print("=" * 80)
issueby1_idx = header.index('issueby1')
issueby1_value = data[issueby1_idx]
print(f"Mã nơi cấp: {issueby1_value}")
print("Cần tạo bảng mapping mã -> tên nơi cấp")
print("Ví dụ: 145 -> 'Cục Cảnh sát ĐKQL cư trú và DLQG về dân cư'")

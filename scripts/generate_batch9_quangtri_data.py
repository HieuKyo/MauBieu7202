#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch 9 - Quảng Trị (mới) province data generation script
Quảng Trị (mới) = Quảng Trị + Quảng Bình
77 items total: 69 xã, 8 phường, 1 đặc khu
1 xã not being restructured: Tân Thành (huyện Minh Hóa)
"""

import json
import os

# Quảng Trị restructuring data
# Format: (huyện, [list of old units], new unit name)
quangtri_restructuring_data = [
    # OLD QUẢNG BÌNH DISTRICTS

    # Huyện Minh Hóa (old Quảng Bình) - items 3-11
    ("Huyện Minh Hóa", ["Xã Trọng Hóa", "Xã Dân Hóa"], "Xã Dân Hóa"),
    ("Huyện Minh Hóa", ["Xã Hóa Sơn", "Xã Hóa Hợp"], "Xã Kim Điền"),
    ("Huyện Minh Hóa", ["Xã Thượng Hóa", "Xã Trung Hóa", "Xã Minh Hóa", "Xã Tân Hóa"], "Xã Kim Phú"),
    ("Huyện Minh Hóa", ["Thị trấn Quy Đạt", "Xã Xuân Hóa", "Xã Yên Hóa", "Xã Hồng Hóa"], "Xã Minh Hóa"),
    ("Huyện Minh Hóa", ["Xã Lâm Hóa", "Xã Thanh Hóa"], "Xã Tuyên Lâm"),
    ("Huyện Minh Hóa", ["Xã Thanh Thạch", "Xã Hương Hóa"], "Xã Tuyên Sơn"),

    # Huyện Tuyên Hóa (old Quảng Bình) - items 9-12
    ("Huyện Tuyên Hóa", ["Thị trấn Đồng Lê", "Xã Kim Hóa", "Xã Lê Hóa", "Xã Thuận Hóa", "Xã Sơn Hóa"], "Xã Đồng Lê"),
    ("Huyện Tuyên Hóa", ["Xã Đồng Hóa", "Xã Thạch Hóa", "Xã Đức Hóa"], "Xã Tuyên Phú"),
    ("Huyện Tuyên Hóa", ["Xã Phong Hóa", "Xã Ngư Hóa", "Xã Mai Hóa"], "Xã Tuyên Bình"),
    ("Huyện Tuyên Hóa", ["Xã Tiến Hóa", "Xã Châu Hóa", "Xã Cao Quảng", "Xã Văn Hóa"], "Xã Tuyên Hóa"),

    # Huyện Quảng Trạch (old Quảng Bình) - items 13-17
    ("Huyện Quảng Trạch", ["Xã Phù Cảnh", "Xã Liên Trường", "Xã Quảng Thanh"], "Xã Tân Gianh"),
    ("Huyện Quảng Trạch", ["Xã Quảng Lưu", "Xã Quảng Thạch", "Xã Quảng Tiến"], "Xã Trung Thuần"),
    ("Huyện Quảng Trạch", ["Xã Quảng Phương", "Xã Quảng Xuân", "Xã Quảng Hưng"], "Xã Quảng Trạch"),
    ("Huyện Quảng Trạch", ["Xã Quảng Châu", "Xã Quảng Tùng", "Xã Cảnh Dương"], "Xã Hòa Trạch"),
    ("Huyện Quảng Trạch", ["Xã Quảng Đông", "Xã Quảng Phú", "Xã Quảng Kim", "Xã Quảng Hợp"], "Xã Phú Trạch"),

    # Thị xã Ba Đồn (old Quảng Bình) - items 1-2, 72-73
    ("Thị xã Ba Đồn", ["Xã Quảng Hòa", "Xã Quảng Lộc", "Xã Quảng Văn", "Xã Quảng Minh"], "Xã Nam Gianh"),
    ("Thị xã Ba Đồn", ["Xã Quảng Tân", "Xã Quảng Trung", "Xã Quảng Tiên", "Xã Quảng Sơn", "Xã Quảng Thủy"], "Xã Nam Ba Đồn"),
    ("Thị xã Ba Đồn", ["Phường Quảng Phong", "Phường Quảng Long", "Phường Ba Đồn", "Xã Quảng Hải"], "Phường Ba Đồn"),
    ("Thị xã Ba Đồn", ["Phường Quảng Phúc", "Phường Quảng Thọ", "Phường Quảng Thuận"], "Phường Bắc Gianh"),

    # Huyện Bố Trạch (old Quảng Bình) - items 18-24
    ("Huyện Bố Trạch", ["Xã Tân Trạch", "Xã Thượng Trạch"], "Xã Thượng Trạch"),
    ("Huyện Bố Trạch", ["Thị trấn Phong Nha", "Xã Lâm Trạch", "Xã Xuân Trạch", "Xã Phúc Trạch"], "Xã Phong Nha"),
    ("Huyện Bố Trạch", ["Xã Thanh Trạch", "Xã Hạ Mỹ", "Xã Liên Trạch", "Xã Bắc Trạch"], "Xã Bắc Trạch"),
    ("Huyện Bố Trạch", ["Xã Hải Phú", "Xã Sơn Lộc", "Xã Đức Trạch", "Xã Đồng Trạch"], "Xã Đông Trạch"),
    ("Huyện Bố Trạch", ["Thị trấn Hoàn Lão", "Xã Trung Trạch", "Xã Đại Trạch", "Xã Tây Trạch", "Xã Hòa Trạch"], "Xã Hoàn Lão"),
    ("Huyện Bố Trạch", ["Xã Hưng Trạch", "Xã Cự Nẫm", "Xã Vạn Trạch", "Xã Phú Định"], "Xã Bố Trạch"),
    ("Huyện Bố Trạch", ["Thị trấn Nông trường Việt Trung", "Xã Nhân Trạch", "Xã Lý Nam"], "Xã Nam Trạch"),

    # Huyện Quảng Ninh (old Quảng Bình) - items 25-28
    ("Huyện Quảng Ninh", ["Thị trấn Quán Hàu", "Xã Vĩnh Ninh", "Xã Võ Ninh", "Xã Hàm Ninh"], "Xã Quảng Ninh"),
    ("Huyện Quảng Ninh", ["Xã Tân Ninh", "Xã Gia Ninh", "Xã Duy Ninh", "Xã Hải Ninh"], "Xã Ninh Châu"),
    ("Huyện Quảng Ninh", ["Xã Vạn Ninh", "Xã An Ninh", "Xã Xuân Ninh", "Xã Hiền Ninh"], "Xã Trường Ninh"),
    ("Huyện Quảng Ninh", ["Xã Trường Xuân", "Xã Trường Sơn"], "Xã Trường Sơn"),

    # Huyện Lệ Thủy (old Quảng Bình) - items 29-35
    ("Huyện Lệ Thủy", ["Thị trấn Kiến Giang", "Xã Liên Thủy", "Xã Xuân Thủy", "Xã An Thủy", "Xã Phong Thủy", "Xã Lộc Thủy"], "Xã Lệ Thủy"),
    ("Huyện Lệ Thủy", ["Xã Cam Thủy", "Xã Thanh Thủy", "Xã Hồng Thủy", "Xã Ngư Thủy Bắc"], "Xã Cam Hồng"),
    ("Huyện Lệ Thủy", ["Xã Hưng Thủy", "Xã Sen Thủy", "Xã Ngư Thủy"], "Xã Sen Ngư"),
    ("Huyện Lệ Thủy", ["Xã Tân Thủy", "Xã Dương Thủy", "Xã Mỹ Thủy", "Xã Thái Thủy"], "Xã Tân Mỹ"),
    ("Huyện Lệ Thủy", ["Xã Trường Thủy", "Xã Mai Thủy", "Xã Phú Thủy"], "Xã Trường Phú"),
    ("Huyện Lệ Thủy", ["Thị trấn Nông trường Lệ Ninh", "Xã Sơn Thủy", "Xã Hoa Thủy"], "Xã Lệ Ninh"),
    ("Huyện Lệ Thủy", ["Xã Kim Thủy", "Xã Ngân Thủy", "Xã Lâm Thủy"], "Xã Kim Ngân"),

    # Thành phố Đồng Hới (old Quảng Bình) - items 69-71
    ("Thành phố Đồng Hới", ["Phường Đức Ninh Đông", "Phường Đồng Hải", "Phường Đồng Phú", "Phường Phú Hải", "Phường Hải Thành", "Phường Nam Lý", "Xã Bảo Ninh", "Xã Đức Ninh"], "Phường Đồng Hới"),
    ("Thành phố Đồng Hới", ["Phường Bắc Lý", "Xã Lộc Ninh", "Xã Quang Phú"], "Phường Đồng Thuận"),
    ("Thành phố Đồng Hới", ["Phường Bắc Nghĩa", "Phường Đồng Sơn", "Xã Nghĩa Ninh", "Xã Thuận Đức"], "Phường Đồng Sơn"),

    # OLD QUẢNG TRỊ DISTRICTS

    # Huyện Vĩnh Linh (old Quảng Trị) - items 36-40
    ("Huyện Vĩnh Linh", ["Thị trấn Hồ Xá", "Xã Vĩnh Long", "Xã Vĩnh Chấp"], "Xã Vĩnh Linh"),
    ("Huyện Vĩnh Linh", ["Thị trấn Cửa Tùng", "Xã Vĩnh Giang", "Xã Hiền Thành", "Xã Kim Thạch"], "Xã Cửa Tùng"),
    ("Huyện Vĩnh Linh", ["Xã Vĩnh Thái", "Xã Trung Nam", "Xã Vĩnh Hòa", "Xã Vĩnh Tú"], "Xã Vĩnh Hoàng"),
    ("Huyện Vĩnh Linh", ["Xã Vĩnh Lâm", "Xã Vĩnh Sơn", "Xã Vĩnh Thủy"], "Xã Vĩnh Thủy"),
    ("Huyện Vĩnh Linh", ["Thị trấn Bến Quan", "Xã Vĩnh Ô", "Xã Vĩnh Hà", "Xã Vĩnh Khê"], "Xã Bến Quan"),

    # Huyện Gio Linh (old Quảng Trị) - items 41-44
    ("Huyện Gio Linh", ["Xã Hải Thái", "Xã Linh Trường", "Xã Gio An", "Xã Gio Sơn"], "Xã Cồn Tiên"),
    ("Huyện Gio Linh", ["Thị trấn Cửa Việt", "Xã Gio Mai", "Xã Gio Hải"], "Xã Cửa Việt"),
    ("Huyện Gio Linh", ["Thị trấn Gio Linh", "Xã Gio Quang", "Xã Gio Mỹ", "Xã Phong Bình"], "Xã Gio Linh"),
    ("Huyện Gio Linh", ["Xã Trung Hải", "Xã Trung Giang", "Xã Trung Sơn"], "Xã Bến Hải"),

    # Huyện Cam Lộ (old Quảng Trị) - items 45-46
    ("Huyện Cam Lộ", ["Thị trấn Cam Lộ", "Xã Cam Thành", "Xã Cam Chính", "Xã Cam Nghĩa"], "Xã Cam Lộ"),
    ("Huyện Cam Lộ", ["Xã Cam Thủy", "Xã Cam Hiếu", "Xã Cam Tuyền", "Xã Thanh An"], "Xã Hiếu Giang"),

    # Huyện Đakrông (old Quảng Trị) - items 47-51
    ("Huyện Đakrông", ["Xã A Bung", "Xã A Ngo"], "Xã La Lay"),
    ("Huyện Đakrông", ["Xã A Vao", "Xã Húc Nghì", "Xã Tà Rụt"], "Xã Tà Rụt"),
    ("Huyện Đakrông", ["Xã Ba Nang", "Xã Tà Long", "Xã Đakrông"], "Xã Đakrông"),
    ("Huyện Đakrông", ["Xã Triệu Nguyên", "Xã Ba Lòng"], "Xã Ba Lòng"),
    ("Huyện Đakrông", ["Thị trấn Krông Klang", "Xã Mò Ó", "Xã Hướng Hiệp"], "Xã Hướng Hiệp"),

    # Huyện Hướng Hóa (old Quảng Trị) - items 52-58
    ("Huyện Hướng Hóa", ["Xã Hướng Việt", "Xã Hướng Lập"], "Xã Hướng Lập"),
    ("Huyện Hướng Hóa", ["Xã Hướng Sơn", "Xã Hướng Linh", "Xã Hướng Phùng"], "Xã Hướng Phùng"),
    ("Huyện Hướng Hóa", ["Thị trấn Khe Sanh", "Xã Tân Hợp", "Xã Húc", "Xã Hướng Tân"], "Xã Khe Sanh"),
    ("Huyện Hướng Hóa", ["Xã Tân Liên", "Xã Hướng Lộc", "Xã Tân Lập"], "Xã Tân Lập"),
    ("Huyện Hướng Hóa", ["Xã Tân Thành", "Xã Tân Long", "Thị trấn Lao Bảo"], "Xã Lao Bảo"),
    ("Huyện Hướng Hóa", ["Xã Thanh", "Xã Thuận", "Xã Lìa"], "Xã Lìa"),
    ("Huyện Hướng Hóa", ["Xã Ba Tầng", "Xã Xy", "Xã A Dơi"], "Xã A Dơi"),

    # Huyện Triệu Phong (old Quảng Trị) - items 59-63
    ("Huyện Triệu Phong", ["Thị trấn Ái Tử", "Xã Triệu Thành", "Xã Triệu Thượng"], "Xã Triệu Phong"),
    ("Huyện Triệu Phong", ["Xã Triệu Ái", "Xã Triệu Giang", "Xã Triệu Long"], "Xã Ái Tử"),
    ("Huyện Triệu Phong", ["Xã Triệu Độ", "Xã Triệu Thuận", "Xã Triệu Hòa", "Xã Triệu Đại"], "Xã Triệu Bình"),
    ("Huyện Triệu Phong", ["Xã Triệu Trung", "Xã Triệu Tài", "Xã Triệu Cơ"], "Xã Triệu Cơ"),
    ("Huyện Triệu Phong", ["Xã Triệu Trạch", "Xã Triệu Phước", "Xã Triệu Tân"], "Xã Nam Cửa Việt"),

    # Huyện Hải Lăng (old Quảng Trị) - items 64-68
    ("Huyện Hải Lăng", ["Thị trấn Diên Sanh", "Xã Hải Trường", "Xã Hải Định"], "Xã Diên Sanh"),
    ("Huyện Hải Lăng", ["Xã Hải Dương", "Xã Hải An", "Xã Hải Khê"], "Xã Mỹ Thủy"),
    ("Huyện Hải Lăng", ["Xã Hải Phú", "Xã Hải Lâm", "Xã Hải Thượng"], "Xã Hải Lăng"),
    ("Huyện Hải Lăng", ["Xã Hải Sơn", "Xã Hải Phong", "Xã Hải Chánh"], "Xã Nam Hải Lăng"),
    ("Huyện Hải Lăng", ["Xã Hải Quy", "Xã Hải Hưng", "Xã Hải Bình"], "Xã Vĩnh Định"),

    # Thành phố Đông Hà (old Quảng Trị) - items 74-75
    ("Thành phố Đông Hà", ["Phường 1", "Phường 3", "Phường 4", "Phường Đông Giang", "Phường Đông Thanh"], "Phường Đông Hà"),
    ("Thành phố Đông Hà", ["Phường 2", "Phường 5", "Phường Đông Lễ", "Phường Đông Lương"], "Phường Nam Đông Hà"),

    # Thị xã Quảng Trị (old Quảng Trị) - item 76
    ("Thị xã Quảng Trị", ["Phường 1", "Phường 2", "Phường 3", "Phường An Đôn", "Xã Hải Lệ"], "Phường Quảng Trị"),

    # Đặc khu Cồn Cỏ - item 77
    ("Đặc khu Cồn Cỏ", ["Huyện Cồn Cỏ"], "Đặc khu Cồn Cỏ"),
]

def generate_dia_danh_entry(tinh_name, data):
    """Generate dia_danh entry for a province"""
    districts = {}

    for huyen, old_units, new_unit in data:
        if huyen not in districts:
            districts[huyen] = []
        if new_unit not in districts[huyen]:
            districts[huyen].append(new_unit)

    # Sort units within each district
    for huyen in districts:
        districts[huyen].sort(key=lambda x: x.replace("Xã ", "").replace("Phường ", "").replace("Thị trấn ", "").replace("Đặc khu ", ""))

    return {tinh_name: districts}

def generate_chuyen_doi_entries(tinh_name, data):
    """Generate chuyen_doi entries for address conversion"""
    entries = {}

    for huyen, old_units, new_unit in data:
        for old_unit in old_units:
            old_key = f", {old_unit}, {huyen}, {tinh_name}"
            new_value = f", {new_unit}, {huyen}, {tinh_name}"
            entries[old_key] = new_value

    return entries

def main():
    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dia_danh_path = os.path.join(base_dir, "templates_app", "static", "data", "dia_danh.json")
    chuyen_doi_path = os.path.join(base_dir, "templates_app", "static", "data", "chuyen_doi.json")

    # Load existing data
    with open(dia_danh_path, 'r', encoding='utf-8') as f:
        dia_danh = json.load(f)

    with open(chuyen_doi_path, 'r', encoding='utf-8') as f:
        chuyen_doi = json.load(f)

    # Process Quảng Trị
    tinh_name = "Tỉnh Quảng Trị"

    print(f"Processing {tinh_name}...")

    # Generate entries
    dia_danh_entry = generate_dia_danh_entry(tinh_name, quangtri_restructuring_data)
    chuyen_doi_entries = generate_chuyen_doi_entries(tinh_name, quangtri_restructuring_data)

    # Update dia_danh
    dia_danh.update(dia_danh_entry)

    # Update chuyen_doi
    chuyen_doi.update(chuyen_doi_entries)

    print(f"  - {len(chuyen_doi_entries)} conversion mappings")

    # Save updated data
    with open(dia_danh_path, 'w', encoding='utf-8') as f:
        json.dump(dia_danh, f, ensure_ascii=False, indent=2)

    with open(chuyen_doi_path, 'w', encoding='utf-8') as f:
        json.dump(chuyen_doi, f, ensure_ascii=False, indent=2)

    # Also save individual province file
    province_file = os.path.join(base_dir, "templates_app", "static", "data", f"{tinh_name.lower().replace(' ', '_')}_dia_danh.json")
    with open(province_file, 'w', encoding='utf-8') as f:
        json.dump(dia_danh_entry, f, ensure_ascii=False, indent=2)

    print(f"\nTotal new mappings: {len(chuyen_doi_entries)}")
    print("\nFinal totals:")
    print(f"  - dia_danh provinces: {len(dia_danh)}")
    print(f"  - chuyen_doi mappings: {len(chuyen_doi)}")

if __name__ == "__main__":
    main()

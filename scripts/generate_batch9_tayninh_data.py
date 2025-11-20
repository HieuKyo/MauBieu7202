#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch 9 - Tây Ninh (mới) province data generation script
Tây Ninh (mới) = Tây Ninh + Long An
96 units total: 82 xã and 14 phường
"""

import json
import os

# Tây Ninh restructuring data
# Format: (huyện, [list of old units], new unit name)
tayninh_restructuring_data = [
    # OLD LONG AN DISTRICTS

    # Huyện Tân Hưng (old Long An) - items 1-4
    ("Huyện Tân Hưng", ["Xã Hưng Hà", "Xã Hưng Điền B", "Xã Hưng Điền"], "Xã Hưng Điền"),
    ("Huyện Tân Hưng", ["Xã Thạnh Hưng", "Xã Vĩnh Châu B", "Xã Hưng Thạnh"], "Xã Vĩnh Thạnh"),
    ("Huyện Tân Hưng", ["Thị trấn Tân Hưng", "Xã Vĩnh Thạnh", "Xã Vĩnh Lợi"], "Xã Tân Hưng"),
    ("Huyện Tân Hưng", ["Xã Vĩnh Đại", "Xã Vĩnh Bửu", "Xã Vĩnh Châu A"], "Xã Vĩnh Châu"),

    # Huyện Vĩnh Hưng (old Long An) - items 5-7
    ("Huyện Vĩnh Hưng", ["Xã Tuyên Bình", "Xã Tuyên Bình Tây", "Xã Vĩnh Bình", "Xã Vĩnh Thuận", "Xã Thái Bình Trung"], "Xã Tuyên Bình"),
    ("Huyện Vĩnh Hưng", ["Thị trấn Vĩnh Hưng", "Xã Vĩnh Trị", "Xã Thái Trị", "Xã Khánh Hưng", "Xã Thái Bình Trung", "Xã Vĩnh Thuận", "Xã Vĩnh Bình"], "Xã Vĩnh Hưng"),
    ("Huyện Vĩnh Hưng", ["Xã Hưng Điền A", "Xã Thái Bình Trung", "Xã Vĩnh Trị", "Xã Thái Trị", "Xã Khánh Hưng"], "Xã Khánh Hưng"),

    # Thị xã Kiến Tường (old Long An) - items 8, 12, 83
    ("Thị xã Kiến Tường", ["Xã Thạnh Hưng", "Xã Tuyên Thạnh", "Xã Bắc Hòa"], "Xã Tuyên Thạnh"),
    ("Thị xã Kiến Tường", ["Xã Hậu Thạnh Đông", "Xã Hậu Thạnh Tây", "Xã Bắc Hòa"], "Xã Hậu Thạnh"),
    ("Thị xã Kiến Tường", ["Phường 1", "Phường 2", "Phường 3"], "Phường Kiến Tường"),

    # Huyện Mộc Hóa (old Long An) - items 9-11
    ("Huyện Mộc Hóa", ["Xã Thạnh Trị", "Xã Bình Tân", "Xã Bình Hòa Tây", "Xã Bình Hiệp"], "Xã Bình Hiệp"),
    ("Huyện Mộc Hóa", ["Xã Bình Thạnh", "Xã Bình Hòa Đông", "Xã Bình Hòa Trung"], "Xã Bình Hòa"),
    ("Huyện Mộc Hóa", ["Xã Tân Thành", "Xã Tân Lập", "Thị trấn Bình Phong Thạnh"], "Xã Mộc Hóa"),

    # Huyện Tân Thạnh (old Long An) - items 13-15
    ("Huyện Tân Thạnh", ["Xã Tân Lập", "Xã Nhơn Hòa", "Xã Nhơn Hòa Lập"], "Xã Nhơn Hòa Lập"),
    ("Huyện Tân Thạnh", ["Xã Tân Thành", "Xã Tân Ninh", "Xã Nhơn Ninh"], "Xã Nhơn Ninh"),
    ("Huyện Tân Thạnh", ["Xã Tân Bình", "Xã Tân Hòa", "Xã Kiến Bình", "Thị trấn Tân Thạnh"], "Xã Tân Thạnh"),

    # Huyện Thạnh Hóa (old Long An) - items 16-19
    ("Huyện Thạnh Hóa", ["Xã Tân Hiệp", "Xã Thuận Bình", "Xã Bình Hòa Hưng"], "Xã Bình Thành"),
    ("Huyện Thạnh Hóa", ["Xã Thuận Nghĩa Hòa", "Xã Thạnh Phú", "Xã Thạnh Phước"], "Xã Thạnh Phước"),
    ("Huyện Thạnh Hóa", ["Thị trấn Thạnh Hóa", "Xã Thủy Tây", "Xã Thạnh An"], "Xã Thạnh Hóa"),
    ("Huyện Thạnh Hóa", ["Xã Tân Đông", "Xã Thủy Đông", "Xã Tân Tây"], "Xã Tân Tây"),

    # Huyện Thủ Thừa (old Long An) - items 20-23
    ("Huyện Thủ Thừa", ["Thị trấn Thủ Thừa", "Xã Bình Thạnh", "Xã Tân Thành", "Xã Nhị Thành"], "Xã Thủ Thừa"),
    ("Huyện Thủ Thừa", ["Xã Mỹ Phú", "Xã Mỹ An"], "Xã Mỹ An"),
    ("Huyện Thủ Thừa", ["Xã Bình An", "Xã Mỹ Lạc", "Xã Mỹ Thạnh", "Xã Tân Thành"], "Xã Mỹ Thạnh"),
    ("Huyện Thủ Thừa", ["Xã Long Thuận", "Xã Long Thạnh", "Xã Tân Long"], "Xã Tân Long"),

    # Huyện Đức Huệ (old Long An) - items 24-26
    ("Huyện Đức Huệ", ["Xã Mỹ Thạnh Bắc", "Xã Mỹ Quý Đông", "Xã Mỹ Quý Tây"], "Xã Mỹ Quý"),
    ("Huyện Đức Huệ", ["Thị trấn Đông Thành", "Xã Mỹ Thạnh Tây", "Xã Mỹ Thạnh Đông", "Xã Mỹ Bình"], "Xã Đông Thành"),
    ("Huyện Đức Huệ", ["Xã Bình Hòa Bắc", "Xã Bình Hòa Nam", "Xã Bình Thành"], "Xã Đức Huệ"),

    # Huyện Đức Hòa (old Long An) - items 27-33
    ("Huyện Đức Hòa", ["Xã Lộc Giang", "Xã An Ninh Đông", "Xã An Ninh Tây"], "Xã An Ninh"),
    ("Huyện Đức Hòa", ["Xã Tân Phú", "Xã Hiệp Hòa", "Thị trấn Hiệp Hòa"], "Xã Hiệp Hòa"),
    ("Huyện Đức Hòa", ["Thị trấn Hậu Nghĩa", "Xã Đức Lập Thượng", "Xã Tân Mỹ"], "Xã Hậu Nghĩa"),
    ("Huyện Đức Hòa", ["Xã Hòa Khánh Tây", "Xã Hòa Khánh Nam", "Xã Hòa Khánh Đông"], "Xã Hòa Khánh"),
    ("Huyện Đức Hòa", ["Xã Đức Lập Hạ", "Xã Mỹ Hạnh Bắc", "Xã Đức Hòa Thượng"], "Xã Đức Lập"),
    ("Huyện Đức Hòa", ["Xã Đức Hòa Đông", "Xã Mỹ Hạnh Nam", "Xã Đức Hòa Thượng"], "Xã Mỹ Hạnh"),
    ("Huyện Đức Hòa", ["Thị trấn Đức Hòa", "Xã Hựu Thạnh", "Xã Đức Hòa Hạ"], "Xã Đức Hòa"),

    # Huyện Bến Lức (old Long An) - items 34-39
    ("Huyện Bến Lức", ["Xã Thạnh Hòa", "Xã Lương Bình", "Xã Thạnh Lợi"], "Xã Thạnh Lợi"),
    ("Huyện Bến Lức", ["Xã Thạnh Đức", "Xã Nhựt Chánh", "Xã Bình Đức"], "Xã Bình Đức"),
    ("Huyện Bến Lức", ["Xã Tân Bửu", "Xã Lương Hòa"], "Xã Lương Hòa"),
    ("Huyện Bến Lức", ["Xã An Thạnh", "Xã Thanh Phú", "Thị trấn Bến Lức"], "Xã Bến Lức"),
    ("Huyện Bến Lức", ["Xã Long Hiệp", "Xã Phước Lợi", "Xã Mỹ Yên"], "Xã Mỹ Yên"),
    ("Huyện Bến Lức", ["Xã Long Định", "Xã Phước Vân", "Xã Long Cang"], "Xã Long Cang"),

    # Huyện Cần Đước (old Long An) - items 40-46
    ("Huyện Cần Đước", ["Xã Long Trạch", "Xã Long Khê", "Xã Long Hòa"], "Xã Rạch Kiến"),
    ("Huyện Cần Đước", ["Xã Tân Trạch", "Xã Long Sơn", "Xã Mỹ Lệ"], "Xã Mỹ Lệ"),
    ("Huyện Cần Đước", ["Xã Phước Đông", "Xã Tân Lân"], "Xã Tân Lân"),
    ("Huyện Cần Đước", ["Thị trấn Cần Đước", "Xã Phước Tuy", "Xã Tân Ân", "Xã Tân Chánh"], "Xã Cần Đước"),
    ("Huyện Cần Đước", ["Xã Long Hựu Đông", "Xã Long Hựu Tây"], "Xã Long Hựu"),
    ("Huyện Cần Đước", ["Xã Long Thượng", "Xã Phước Hậu", "Xã Phước Lý"], "Xã Phước Lý"),
    ("Huyện Cần Đước", ["Xã Phước Lâm", "Xã Thuận Thành", "Xã Mỹ Lộc"], "Xã Mỹ Lộc"),

    # Huyện Cần Giuộc (old Long An) - items 47-50
    ("Huyện Cần Giuộc", ["Thị trấn Cần Giuộc", "Xã Phước Lại", "Xã Long Hậu"], "Xã Cần Giuộc"),
    ("Huyện Cần Giuộc", ["Xã Long An", "Xã Long Phụng", "Xã Phước Vĩnh Tây"], "Xã Phước Vĩnh Tây"),
    ("Huyện Cần Giuộc", ["Xã Đông Thạnh", "Xã Phước Vĩnh Đông", "Xã Tân Tập"], "Xã Tân Tập"),
    ("Huyện Cần Giuộc", ["Xã Tân Phước Tây", "Xã Nhựt Ninh", "Xã Đức Tân"], "Xã Vàm Cỏ"),

    # Huyện Tân Trụ (old Long An) - items 51-53
    ("Huyện Tân Trụ", ["Thị trấn Tân Trụ", "Xã Bình Trinh Đông", "Xã Bình Lãng", "Xã Bình Tịnh"], "Xã Tân Trụ"),
    ("Huyện Tân Trụ", ["Xã Tân Bình", "Xã Quê Mỹ Thạnh", "Xã Lạc Tấn", "Xã Nhị Thành"], "Xã Nhựt Tảo"),
    ("Huyện Tân Trụ", ["Xã Thanh Phú Long", "Xã Thanh Vĩnh Đông", "Xã Thuận Mỹ"], "Xã Thuận Mỹ"),

    # Huyện Châu Thành (old Long An) - items 54-56
    ("Huyện Châu Thành", ["Xã Dương Xuân Hội", "Xã Long Trì", "Xã An Lục Long"], "Xã An Lục Long"),
    ("Huyện Châu Thành", ["Thị trấn Tầm Vu", "Xã Hiệp Thạnh", "Xã Phú Ngãi Trị", "Xã Phước Tân Hưng"], "Xã Tầm Vu"),
    ("Huyện Châu Thành", ["Xã Hòa Phú", "Xã Bình Quới", "Xã Vĩnh Công"], "Xã Vĩnh Công"),

    # Thành phố Tân An (old Long An) - items 84-86
    ("Thành phố Tân An", ["Phường 1", "Phường 3", "Phường 4", "Phường 5", "Phường 6", "Xã Hướng Thọ Phú", "Xã Bình Thạnh"], "Phường Long An"),
    ("Thành phố Tân An", ["Phường 7", "Xã Bình Tâm", "Xã Nhơn Thạnh Trung", "Xã An Vĩnh Ngãi"], "Phường Tân An"),
    ("Thành phố Tân An", ["Phường Tân Khánh", "Phường Khánh Hậu", "Xã Lợi Bình Nhơn"], "Phường Khánh Hậu"),

    # OLD TÂY NINH DISTRICTS

    # Huyện Trảng Bàng (old Tây Ninh) - items 57-58, 93-94
    ("Huyện Trảng Bàng", ["Xã Phước Bình", "Xã Phước Chỉ"], "Xã Phước Chỉ"),
    ("Huyện Trảng Bàng", ["Xã Đôn Thuận", "Xã Hưng Thuận"], "Xã Hưng Thuận"),
    ("Huyện Trảng Bàng", ["Phường An Hòa", "Phường Trảng Bàng"], "Phường Trảng Bàng"),
    ("Huyện Trảng Bàng", ["Phường Lộc Hưng", "Phường An Tịnh"], "Phường An Tịnh"),

    # Huyện Gò Dầu (old Tây Ninh) - items 59-60, 95-96
    ("Huyện Gò Dầu", ["Xã Thạnh Đức", "Xã Cẩm Giang"], "Xã Thạnh Đức"),
    ("Huyện Gò Dầu", ["Xã Hiệp Thạnh", "Xã Phước Trạch", "Xã Phước Thạnh"], "Xã Phước Thạnh"),
    ("Huyện Gò Dầu", ["Phường Gia Bình", "Thị trấn Gò Dầu", "Xã Thanh Phước"], "Phường Gò Dầu"),
    ("Huyện Gò Dầu", ["Xã Phước Đông", "Phường Gia Lộc"], "Phường Gia Lộc"),

    # Huyện Dương Minh Châu (old Tây Ninh) - items 61-64
    ("Huyện Dương Minh Châu", ["Xã Bàu Đồn", "Xã Truông Mít"], "Xã Truông Mít"),
    ("Huyện Dương Minh Châu", ["Xã Bến Củi", "Xã Lộc Ninh", "Xã Phước Minh"], "Xã Lộc Ninh"),
    ("Huyện Dương Minh Châu", ["Xã Phước Ninh", "Xã Cầu Khởi", "Xã Chà Là"], "Xã Cầu Khởi"),
    ("Huyện Dương Minh Châu", ["Thị trấn Dương Minh Châu", "Xã Phan", "Xã Suối Đá", "Xã Phước Minh"], "Xã Dương Minh Châu"),

    # Huyện Tân Châu (old Tây Ninh) - items 65-70
    ("Huyện Tân Châu", ["Xã Tân Đông", "Xã Tân Hà"], "Xã Tân Đông"),
    ("Huyện Tân Châu", ["Thị trấn Tân Châu", "Xã Thạnh Đông", "Xã Tân Phú", "Xã Suối Dây"], "Xã Tân Châu"),
    ("Huyện Tân Châu", ["Xã Tân Hưng", "Xã Mỏ Công", "Xã Trà Vong", "Xã Tân Phong", "Xã Tân Phú"], "Xã Tân Phú"),
    ("Huyện Tân Châu", ["Xã Tân Hiệp", "Xã Tân Hội"], "Xã Tân Hội"),
    ("Huyện Tân Châu", ["Xã Tân Thành", "Xã Suối Dây"], "Xã Tân Thành"),
    ("Huyện Tân Châu", ["Xã Tân Hòa", "Xã Suối Ngô"], "Xã Tân Hòa"),

    # Huyện Tân Biên (old Tây Ninh) - items 71-76
    ("Huyện Tân Biên", ["Xã Tân Lập", "Xã Thạnh Bắc"], "Xã Tân Lập"),
    ("Huyện Tân Biên", ["Xã Tân Bình", "Xã Thạnh Tây", "Thị trấn Tân Biên"], "Xã Tân Biên"),
    ("Huyện Tân Biên", ["Xã Thạnh Bình", "Xã Tân Phong"], "Xã Thạnh Bình"),
    ("Huyện Tân Biên", ["Xã Mỏ Công", "Xã Trà Vong"], "Xã Trà Vong"),
    ("Huyện Tân Biên", ["Xã Hòa Hiệp", "Xã Phước Vinh"], "Xã Phước Vinh"),
    ("Huyện Tân Biên", ["Xã Biên Giới", "Xã Hòa Thạnh", "Xã Hòa Hội"], "Xã Hòa Hội"),

    # Huyện Châu Thành (old Tây Ninh) - items 77-80
    ("Huyện Châu Thành", ["Xã Thành Long", "Xã Ninh Điền"], "Xã Ninh Điền"),
    ("Huyện Châu Thành", ["Thị trấn Châu Thành", "Xã Đồng Khởi", "Xã An Bình", "Xã Thái Bình"], "Xã Châu Thành"),
    ("Huyện Châu Thành", ["Xã An Cơ", "Xã Trí Bình", "Xã Hảo Đước"], "Xã Hảo Đước"),
    ("Huyện Châu Thành", ["Xã Long Vĩnh", "Xã Long Phước", "Xã Long Chữ"], "Xã Long Chữ"),

    # Huyện Bến Cầu (old Tây Ninh) - items 81-82
    ("Huyện Bến Cầu", ["Xã Long Thuận", "Xã Long Giang", "Xã Long Khánh"], "Xã Long Thuận"),
    ("Huyện Bến Cầu", ["Thị trấn Bến Cầu", "Xã An Thạnh", "Xã Tiên Thuận", "Xã Lợi Thuận"], "Xã Bến Cầu"),

    # Thành phố Tây Ninh (old Tây Ninh) - items 87-89
    ("Thành phố Tây Ninh", ["Phường 1", "Phường 2", "Phường 3", "Phường IV", "Phường Hiệp Ninh", "Xã Thái Bình"], "Phường Tân Ninh"),
    ("Thành phố Tây Ninh", ["Phường Ninh Sơn", "Xã Tân Bình", "Xã Bình Minh", "Xã Thạnh Tân", "Xã Suối Đá", "Xã Phan"], "Phường Bình Minh"),
    ("Thành phố Tây Ninh", ["Phường Ninh Thạnh", "Xã Bàu Năng", "Xã Chà Là"], "Phường Ninh Thạnh"),

    # Thị xã Hòa Thành (old Tây Ninh) - items 90-92
    ("Thị xã Hòa Thành", ["Phường Long Thành Bắc", "Phường Long Hoa", "Xã Trường Hòa", "Xã Trường Tây", "Xã Trường Đông"], "Phường Long Hoa"),
    ("Thị xã Hòa Thành", ["Phường Long Thành Trung", "Xã Long Thành Nam"], "Phường Hòa Thành"),
    ("Thị xã Hòa Thành", ["Phường Hiệp Tân", "Xã Thanh Điền"], "Phường Thanh Điền"),
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
        districts[huyen].sort(key=lambda x: x.replace("Xã ", "").replace("Phường ", "").replace("Thị trấn ", ""))

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

    # Process Tây Ninh
    tinh_name = "Tỉnh Tây Ninh"

    print(f"Processing {tinh_name}...")

    # Generate entries
    dia_danh_entry = generate_dia_danh_entry(tinh_name, tayninh_restructuring_data)
    chuyen_doi_entries = generate_chuyen_doi_entries(tinh_name, tayninh_restructuring_data)

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
    print(f"\nFinal totals:")
    print(f"  - dia_danh provinces: {len(dia_danh)}")
    print(f"  - chuyen_doi mappings: {len(chuyen_doi)}")

if __name__ == "__main__":
    main()

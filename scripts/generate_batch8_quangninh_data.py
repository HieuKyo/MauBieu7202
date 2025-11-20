#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch 8 Part 3: Generate Quảng Ninh province data
Province: Tỉnh Quảng Ninh (53 items)
"""

import json
import os

# Quảng Ninh restructuring data - 53 items organized by district
quangninh_restructuring_data = [
    # Thành phố Hạ Long - xã (former Hoành Bồ) - items 1-2
    ("Thành phố Hạ Long", ["Xã Bằng Cả", "Xã Dân Chủ", "Xã Tân Dân", "Xã Quảng La"], "Xã Quảng La"),
    ("Thành phố Hạ Long", ["Xã Vũ Oai", "Xã Hòa Bình", "Xã Thống Nhất", "Xã Đồng Lâm"], "Xã Thống Nhất"),

    # Huyện Tiên Yên - items 3-7
    ("Huyện Tiên Yên", ["Xã Hải Lạng", "Xã Hải Hòa"], "Xã Hải Hòa"),
    ("Huyện Tiên Yên", ["Thị trấn Tiên Yên", "Xã Phong Dụ", "Xã Tiên Lãng", "Xã Yên Than", "Xã Đại Dực", "Xã Đông Ngũ", "Xã Vô Ngại"], "Xã Tiên Yên"),
    ("Huyện Tiên Yên", ["Xã Hà Lâu", "Xã Điền Xá", "Xã Yên Than"], "Xã Điền Xá"),
    ("Huyện Tiên Yên", ["Xã Đông Hải", "Xã Đại Dực", "Xã Đông Ngũ"], "Xã Đông Ngũ"),
    ("Huyện Tiên Yên", ["Xã Đồng Rui", "Xã Hải Lạng", "Xã Hải Hòa"], "Xã Hải Lạng"),

    # Huyện Ba Chẽ - items 8-10
    ("Huyện Ba Chẽ", ["Xã Đồng Sơn", "Xã Lương Minh"], "Xã Lương Minh"),
    ("Huyện Ba Chẽ", ["Xã Thanh Lâm", "Xã Đạp Thanh", "Xã Kỳ Thượng"], "Xã Kỳ Thượng"),
    ("Huyện Ba Chẽ", ["Thị trấn Ba Chẽ", "Xã Thanh Sơn", "Xã Nam Sơn", "Xã Đồn Đạc", "Xã Hải Lạng"], "Xã Ba Chẽ"),

    # Huyện Đầm Hà - items 11-12
    ("Huyện Đầm Hà", ["Xã Quảng An", "Xã Dực Yên", "Xã Quảng Lâm", "Xã Quảng Tân"], "Xã Quảng Tân"),
    ("Huyện Đầm Hà", ["Thị trấn Đầm Hà", "Xã Tân Bình", "Xã Đại Bình", "Xã Tân Lập", "Xã Đầm Hà"], "Xã Đầm Hà"),

    # Huyện Hải Hà - items 13-15
    ("Huyện Hải Hà", ["Thị trấn Quảng Hà", "Xã Quảng Minh", "Xã Quảng Chính", "Xã Quảng Phong", "Xã Quảng Long"], "Xã Quảng Hà"),
    ("Huyện Hải Hà", ["Xã Quảng Sơn", "Xã Đường Hoa", "Xã Quảng Long"], "Xã Đường Hoa"),
    ("Huyện Hải Hà", ["Xã Quảng Thành", "Xã Quảng Thịnh", "Xã Quảng Đức"], "Xã Quảng Đức"),

    # Huyện Bình Liêu - items 16-18
    ("Huyện Bình Liêu", ["Xã Đồng Văn", "Xã Hoành Mô"], "Xã Hoành Mô"),
    ("Huyện Bình Liêu", ["Xã Đồng Tâm", "Xã Lục Hồn"], "Xã Lục Hồn"),
    ("Huyện Bình Liêu", ["Thị trấn Bình Liêu", "Xã Húc Động", "Xã Vô Ngại"], "Xã Bình Liêu"),

    # Thành phố Móng Cái - xã - items 19-21
    ("Thành phố Móng Cái", ["Xã Bắc Sơn", "Xã Hải Sơn"], "Xã Hải Sơn"),
    ("Thành phố Móng Cái", ["Xã Quảng Nghĩa", "Xã Hải Tiến"], "Xã Hải Ninh"),
    ("Thành phố Móng Cái", ["Xã Vĩnh Trung", "Xã Vĩnh Thực"], "Xã Vĩnh Thực"),

    # Thị xã Đông Triều - phường - items 22-26
    ("Thị xã Đông Triều", ["Phường Bình Dương", "Xã An Sinh", "Xã Việt Dân", "Phường Đức Chính"], "Phường An Sinh"),
    ("Thị xã Đông Triều", ["Phường Thủy An", "Phường Hưng Đạo", "Phường Hồng Phong", "Xã Nguyễn Huệ", "Phường Đức Chính"], "Phường Đông Triều"),
    ("Thị xã Đông Triều", ["Phường Tràng An", "Phường Bình Khê", "Xã Tràng Lương"], "Phường Bình Khê"),
    ("Thị xã Đông Triều", ["Phường Xuân Sơn", "Phường Kim Sơn", "Phường Yên Thọ", "Phường Mạo Khê"], "Phường Mạo Khê"),
    ("Thị xã Đông Triều", ["Phường Yên Đức", "Phường Hoàng Quế", "Xã Hồng Thái Tây", "Xã Hồng Thái Đông"], "Phường Hoàng Quế"),

    # Thành phố Uông Bí - phường - items 27-29
    ("Thành phố Uông Bí", ["Phường Phương Đông", "Phường Phương Nam", "Xã Thượng Yên Công"], "Phường Yên Tử"),
    ("Thành phố Uông Bí", ["Phường Bắc Sơn", "Phường Nam Khê", "Phường Vàng Danh", "Phường Trưng Vương"], "Phường Vàng Danh"),
    ("Thành phố Uông Bí", ["Phường Quang Trung", "Phường Thanh Sơn", "Phường Yên Thanh", "Phường Trưng Vương"], "Phường Uông Bí"),

    # Thị xã Quảng Yên - phường - items 30-35
    ("Thị xã Quảng Yên", ["Phường Minh Thành", "Phường Đông Mai"], "Phường Đông Mai"),
    ("Thị xã Quảng Yên", ["Phường Cộng Hòa", "Xã Sông Khoai", "Xã Hiệp Hòa"], "Phường Hiệp Hòa"),
    ("Thị xã Quảng Yên", ["Phường Yên Giang", "Phường Quảng Yên", "Xã Tiền An"], "Phường Quảng Yên"),
    ("Thị xã Quảng Yên", ["Phường Tân An", "Phường Hà An", "Xã Hoàng Tân", "Xã Liên Hòa"], "Phường Hà An"),
    ("Thị xã Quảng Yên", ["Phường Nam Hòa", "Phường Yên Hải", "Phường Phong Cốc", "Xã Cẩm La"], "Phường Phong Cốc"),
    ("Thị xã Quảng Yên", ["Phường Phong Hải", "Xã Liên Vị", "Xã Tiền Phong", "Xã Liên Hòa"], "Phường Liên Hòa"),

    # Thành phố Hạ Long - phường - items 36-44
    ("Thành phố Hạ Long", ["Phường Đại Yên", "Phường Tuần Châu", "Phường Hà Khẩu"], "Phường Tuần Châu"),
    ("Thành phố Hạ Long", ["Phường Giếng Đáy", "Phường Việt Hưng", "Phường Hà Khẩu"], "Phường Việt Hưng"),
    ("Thành phố Hạ Long", ["Phường Hùng Thắng", "Phường Bãi Cháy"], "Phường Bãi Cháy"),
    ("Thành phố Hạ Long", ["Phường Hà Phong", "Phường Hà Tu"], "Phường Hà Tu"),
    ("Thành phố Hạ Long", ["Phường Cao Thắng", "Phường Hà Trung", "Phường Hà Lầm"], "Phường Hà Lầm"),
    ("Thành phố Hạ Long", ["Phường Hà Khánh", "Phường Cao Xanh"], "Phường Cao Xanh"),
    ("Thành phố Hạ Long", ["Phường Bạch Đằng", "Phường Trần Hưng Đạo", "Phường Hồng Gai"], "Phường Hồng Gai"),
    ("Thành phố Hạ Long", ["Phường Hồng Hà", "Phường Hồng Hải"], "Phường Hạ Long"),
    ("Thành phố Hạ Long", ["Phường Hoành Bồ", "Xã Sơn Dương", "Xã Lê Lợi", "Xã Đồng Lâm"], "Phường Hoành Bồ"),

    # Thành phố Cẩm Phả - phường - items 45-48
    ("Thành phố Cẩm Phả", ["Phường Mông Dương", "Xã Dương Huy"], "Phường Mông Dương"),
    ("Thành phố Cẩm Phả", ["Phường Cẩm Thạch", "Phường Cẩm Thủy", "Phường Quang Hanh"], "Phường Quang Hanh"),
    ("Thành phố Cẩm Phả", ["Phường Cẩm Trung", "Phường Cẩm Thành", "Phường Cẩm Bình", "Phường Cẩm Tây", "Phường Cẩm Đông"], "Phường Cẩm Phả"),
    ("Thành phố Cẩm Phả", ["Phường Cẩm Phú", "Phường Cẩm Thịnh", "Phường Cẩm Sơn", "Phường Cửa Ông"], "Phường Cửa Ông"),

    # Thành phố Móng Cái - phường - items 49-51
    ("Thành phố Móng Cái", ["Phường Trần Phú", "Phường Hải Hòa", "Phường Bình Ngọc", "Phường Trà Cổ", "Xã Hải Xuân"], "Phường Móng Cái 1"),
    ("Thành phố Móng Cái", ["Phường Ninh Dương", "Phường Ka Long", "Xã Vạn Ninh"], "Phường Móng Cái 2"),
    ("Thành phố Móng Cái", ["Phường Hải Yên", "Xã Hải Đông"], "Phường Móng Cái 3"),

    # Đặc khu Vân Đồn - item 52
    ("Đặc khu Vân Đồn", ["Thị trấn Cái Rồng", "Xã Bản Sen", "Xã Bình Dân", "Xã Đài Xuyên", "Xã Đoàn Kết", "Xã Đông Xá", "Xã Hạ Long", "Xã Minh Châu", "Xã Ngọc Vừng", "Xã Quan Lạn", "Xã Thắng Lợi", "Xã Vạn Yên"], "Đặc khu Vân Đồn"),

    # Đặc khu Cô Tô - item 53
    ("Đặc khu Cô Tô", ["Thị trấn Cô Tô", "Xã Đồng Tiến", "Xã Thanh Lân"], "Đặc khu Cô Tô"),
]

def generate_province_data(province_name, restructuring_data):
    """Generate dia_danh and chuyen_doi data for a province"""

    # Build hierarchical structure
    dia_danh = {province_name: {}}
    chuyen_doi = {}

    # Group by district
    districts = {}
    for huyen, old_units, new_unit in restructuring_data:
        if huyen not in districts:
            districts[huyen] = {}

        # Add the new unit with all old units as its children
        if new_unit not in districts[huyen]:
            districts[huyen][new_unit] = old_units
        else:
            # Merge if same new unit appears multiple times
            districts[huyen][new_unit].extend(old_units)

    # Build dia_danh structure
    for huyen in sorted(districts.keys()):
        dia_danh[province_name][huyen] = {}
        for new_unit in sorted(districts[huyen].keys()):
            dia_danh[province_name][huyen][new_unit] = sorted(districts[huyen][new_unit])

    # Build chuyen_doi mappings
    for huyen, old_units, new_unit in restructuring_data:
        for old_unit in old_units:
            old_key = f", {old_unit}, {huyen}, {province_name}"
            new_value = f", {new_unit}, {huyen}, {province_name}"
            chuyen_doi[old_key] = new_value

    return dia_danh, chuyen_doi

def main():
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, "templates_app", "static", "data")

    # Load existing data
    dia_danh_path = os.path.join(data_dir, "dia_danh.json")
    chuyen_doi_path = os.path.join(data_dir, "chuyen_doi.json")

    with open(dia_danh_path, 'r', encoding='utf-8') as f:
        dia_danh = json.load(f)

    with open(chuyen_doi_path, 'r', encoding='utf-8') as f:
        chuyen_doi = json.load(f)

    # Process Quảng Ninh
    province_name = "Tỉnh Quảng Ninh"
    province_dia_danh, province_chuyen_doi = generate_province_data(
        province_name, quangninh_restructuring_data
    )

    # Add to main data
    dia_danh.update(province_dia_danh)
    chuyen_doi.update(province_chuyen_doi)

    print(f"Processing {province_name}...")
    print(f"  - {len(province_chuyen_doi)} conversion mappings")

    # Save individual province file
    province_filename = province_name.lower().replace(" ", "_") + "_dia_danh.json"
    province_path = os.path.join(data_dir, province_filename)
    with open(province_path, 'w', encoding='utf-8') as f:
        json.dump(province_dia_danh, f, ensure_ascii=False, indent=2)

    # Save updated main files
    with open(dia_danh_path, 'w', encoding='utf-8') as f:
        json.dump(dia_danh, f, ensure_ascii=False, indent=2)

    with open(chuyen_doi_path, 'w', encoding='utf-8') as f:
        json.dump(chuyen_doi, f, ensure_ascii=False, indent=2)

    print(f"\nTotal new mappings: {len(province_chuyen_doi)}")
    print(f"\nFinal totals:")
    print(f"  - dia_danh provinces: {len(dia_danh)}")
    print(f"  - chuyen_doi mappings: {len(chuyen_doi)}")

if __name__ == "__main__":
    main()

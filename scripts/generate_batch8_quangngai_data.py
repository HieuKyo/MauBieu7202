#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch 8 Part 2: Generate Quảng Ngãi (mới) province data
Province: Tỉnh Quảng Ngãi (91 items)
Note: This is a mega-province combining old Quảng Ngãi + Kon Tum
"""

import json
import os

# Quảng Ngãi restructuring data - 91 items organized by district
quangngai_restructuring_data = [
    # Thành phố Quảng Ngãi (old Quảng Ngãi) - items 1-2
    ("Thành phố Quảng Ngãi", ["Xã Tịnh Kỳ", "Xã Tịnh Châu", "Xã Tịnh Long", "Xã Tịnh Thiện", "Xã Tịnh Khê"], "Xã Tịnh Khê"),
    ("Thành phố Quảng Ngãi", ["Xã Nghĩa Hà", "Xã Nghĩa Dõng", "Xã Nghĩa Dũng", "Xã An Phú"], "Xã An Phú"),

    # Huyện Bình Sơn (old Quảng Ngãi) - items 3-9
    ("Huyện Bình Sơn", ["Xã Phổ Nhơn", "Xã Phổ Phong"], "Xã Nguyễn Nghiêm"),
    ("Huyện Bình Sơn", ["Xã Phổ Khánh", "Xã Phổ Cường"], "Xã Khánh Cường"),
    ("Huyện Bình Sơn", ["Xã Bình Khương", "Xã Bình An", "Xã Bình Minh"], "Xã Bình Minh"),
    ("Huyện Bình Sơn", ["Xã Bình Mỹ", "Xã Bình Chương"], "Xã Bình Chương"),
    ("Huyện Bình Sơn", ["Thị trấn Châu Ổ", "Xã Bình Thạnh", "Xã Bình Chánh", "Xã Bình Dương", "Xã Bình Nguyên", "Xã Bình Trung", "Xã Bình Long"], "Xã Bình Sơn"),
    ("Huyện Bình Sơn", ["Xã Bình Thuận", "Xã Bình Đông", "Xã Bình Trị", "Xã Bình Hải", "Xã Bình Hòa", "Xã Bình Phước"], "Xã Vạn Tường"),
    ("Huyện Bình Sơn", ["Xã Bình Hiệp", "Xã Bình Thanh", "Xã Bình Tân Phú", "Xã Bình Châu", "Xã Tịnh Hòa"], "Xã Đông Sơn"),

    # Huyện Sơn Tịnh (old Quảng Ngãi) - items 10-13
    ("Huyện Sơn Tịnh", ["Xã Tịnh Giang", "Xã Tịnh Đông", "Xã Tịnh Minh"], "Xã Trường Giang"),
    ("Huyện Sơn Tịnh", ["Xã Tịnh Bắc", "Xã Tịnh Hiệp", "Xã Tịnh Trà"], "Xã Ba Gia"),
    ("Huyện Sơn Tịnh", ["Thị trấn Tịnh Hà", "Xã Tịnh Bình", "Xã Tịnh Sơn"], "Xã Sơn Tịnh"),
    ("Huyện Sơn Tịnh", ["Xã Tịnh Phong", "Xã Tịnh Thọ"], "Xã Thọ Phong"),

    # Huyện Tư Nghĩa (old Quảng Ngãi) - items 14-17
    ("Huyện Tư Nghĩa", ["Thị trấn La Hà", "Xã Nghĩa Trung", "Xã Nghĩa Thương", "Xã Nghĩa Hòa"], "Xã Tư Nghĩa"),
    ("Huyện Tư Nghĩa", ["Thị trấn Sông Vệ", "Xã Nghĩa Hiệp", "Xã Nghĩa Phương"], "Xã Vệ Giang"),
    ("Huyện Tư Nghĩa", ["Xã Nghĩa Thuận", "Xã Nghĩa Kỳ", "Xã Nghĩa Điền"], "Xã Nghĩa Giang"),
    ("Huyện Tư Nghĩa", ["Xã Nghĩa Sơn", "Xã Nghĩa Lâm", "Xã Nghĩa Thắng"], "Xã Trà Giang"),

    # Huyện Nghĩa Hành (old Quảng Ngãi) - items 18-21
    ("Huyện Nghĩa Hành", ["Thị trấn Chợ Chùa", "Xã Hành Thuận", "Xã Hành Trung"], "Xã Nghĩa Hành"),
    ("Huyện Nghĩa Hành", ["Xã Hành Đức", "Xã Hành Phước", "Xã Hành Thịnh"], "Xã Đình Cương"),
    ("Huyện Nghĩa Hành", ["Xã Hành Thiện", "Xã Hành Tín Tây", "Xã Hành Tín Đông"], "Xã Thiện Tín"),
    ("Huyện Nghĩa Hành", ["Xã Hành Dũng", "Xã Hành Nhân", "Xã Hành Minh"], "Xã Phước Giang"),

    # Huyện Mộ Đức (old Quảng Ngãi) - items 22-25
    ("Huyện Mộ Đức", ["Xã Thắng Lợi", "Xã Đức Nhuận", "Xã Đức Hiệp"], "Xã Long Phụng"),
    ("Huyện Mộ Đức", ["Xã Đức Chánh", "Xã Đức Thạnh", "Xã Đức Minh"], "Xã Mỏ Cày"),
    ("Huyện Mộ Đức", ["Thị trấn Mộ Đức", "Xã Đức Hòa", "Xã Đức Phú", "Xã Đức Tân"], "Xã Mộ Đức"),
    ("Huyện Mộ Đức", ["Xã Đức Phong", "Xã Đức Lân"], "Xã Lân Phong"),

    # Huyện Trà Bồng (old Quảng Ngãi) - items 26-31
    ("Huyện Trà Bồng", ["Thị trấn Trà Xuân", "Xã Trà Sơn", "Xã Trà Thủy"], "Xã Trà Bồng"),
    ("Huyện Trà Bồng", ["Xã Trà Bình", "Xã Trà Phú", "Xã Trà Giang"], "Xã Đông Trà Bồng"),
    ("Huyện Trà Bồng", ["Xã Sơn Trà", "Xã Trà Phong", "Xã Trà Xinh"], "Xã Tây Trà"),
    ("Huyện Trà Bồng", ["Xã Trà Lâm", "Xã Trà Hiệp", "Xã Trà Thanh"], "Xã Thanh Bồng"),
    ("Huyện Trà Bồng", ["Xã Trà Tân", "Xã Trà Bùi"], "Xã Cà Đam"),
    ("Huyện Trà Bồng", ["Xã Hương Trà", "Xã Trà Tây", "Xã Trà Bùi"], "Xã Tây Trà Bồng"),

    # Huyện Sơn Hà (old Quảng Ngãi) - items 32-39
    ("Huyện Sơn Hà", ["Xã Sơn Thành", "Xã Sơn Nham", "Xã Sơn Hạ"], "Xã Sơn Hạ"),
    ("Huyện Sơn Hà", ["Xã Sơn Giang", "Xã Sơn Cao", "Xã Sơn Linh"], "Xã Sơn Linh"),
    ("Huyện Sơn Hà", ["Thị trấn Di Lăng", "Xã Sơn Bao", "Xã Sơn Thượng"], "Xã Sơn Hà"),
    ("Huyện Sơn Hà", ["Xã Sơn Trung", "Xã Sơn Hải", "Xã Sơn Thủy"], "Xã Sơn Thủy"),
    ("Huyện Sơn Hà", ["Xã Sơn Ba", "Xã Sơn Kỳ"], "Xã Sơn Kỳ"),
    ("Huyện Sơn Hà", ["Xã Sơn Long", "Xã Sơn Tân", "Xã Sơn Dung"], "Xã Sơn Tây"),
    ("Huyện Sơn Hà", ["Xã Sơn Mùa", "Xã Sơn Liên", "Xã Sơn Bua"], "Xã Sơn Tây Thượng"),
    ("Huyện Sơn Hà", ["Xã Sơn Tinh", "Xã Sơn Lập", "Xã Sơn Màu"], "Xã Sơn Tây Hạ"),

    # Huyện Minh Long (old Quảng Ngãi) - items 40-41
    ("Huyện Minh Long", ["Xã Long Hiệp", "Xã Thanh An", "Xã Long Môn"], "Xã Minh Long"),
    ("Huyện Minh Long", ["Xã Long Mai", "Xã Long Sơn"], "Xã Sơn Mai"),

    # Huyện Ba Tơ (old Quảng Ngãi) - items 42-48
    ("Huyện Ba Tơ", ["Xã Ba Tiêu", "Xã Ba Ngạc", "Xã Ba Vì"], "Xã Ba Vì"),
    ("Huyện Ba Tơ", ["Xã Ba Lế", "Xã Ba Nam", "Xã Ba Tô"], "Xã Ba Tô"),
    ("Huyện Ba Tơ", ["Xã Ba Giang", "Xã Ba Dinh"], "Xã Ba Dinh"),
    ("Huyện Ba Tơ", ["Thị trấn Ba Tơ", "Xã Ba Cung", "Xã Ba Bích"], "Xã Ba Tơ"),
    ("Huyện Ba Tơ", ["Xã Ba Điền", "Xã Ba Vinh"], "Xã Ba Vinh"),
    ("Huyện Ba Tơ", ["Xã Ba Liên", "Xã Ba Thành", "Xã Ba Động"], "Xã Ba Động"),
    ("Huyện Ba Tơ", ["Xã Ba Trang", "Xã Ba Khâm"], "Xã Đặng Thùy Trâm"),

    # Thành phố Kon Tum (old Kon Tum) - items 49-51
    ("Thành phố Kon Tum", ["Xã Kroong", "Xã Vinh Quang", "Xã Ngọk Bay"], "Xã Ngọk Bay"),
    ("Thành phố Kon Tum", ["Xã Đoàn Kết", "Xã Đăk Năng", "Xã Ia Chim"], "Xã Ia Chim"),
    ("Thành phố Kon Tum", ["Xã Hòa Bình", "Xã Chư Hreng", "Xã Đăk Blà", "Xã Đăk Rơ Wa"], "Xã Đăk Rơ Wa"),

    # Huyện Đăk Hà (old Kon Tum) - items 52-57
    ("Huyện Đăk Hà", ["Xã Đăk Long", "Xã Đăk Pxi"], "Xã Đăk Pxi"),
    ("Huyện Đăk Hà", ["Xã Đăk Hring", "Xã Đăk Mar"], "Xã Đăk Mar"),
    ("Huyện Đăk Hà", ["Xã Đăk Ngọk", "Xã Đăk Ui"], "Xã Đăk Ui"),
    ("Huyện Đăk Hà", ["Xã Ngọk Wang", "Xã Ngọk Réo"], "Xã Ngọk Réo"),
    ("Huyện Đăk Hà", ["Thị trấn Đăk Hà", "Xã Hà Mòn", "Xã Đăk La"], "Xã Đăk Hà"),
    ("Huyện Đăk Hà", ["Xã Đăk Rơ Nga", "Xã Ngọk Tụ"], "Xã Ngọk Tụ"),

    # Huyện Đăk Tô (old Kon Tum) - items 58-59
    ("Huyện Đăk Tô", ["Thị trấn Đăk Tô", "Xã Tân Cảnh", "Xã Pô Kô", "Xã Diên Bình"], "Xã Đăk Tô"),
    ("Huyện Đăk Tô", ["Xã Văn Lem", "Xã Đăk Trăm", "Xã Kon Đào"], "Xã Kon Đào"),

    # Huyện Tu Mơ Rông (old Kon Tum) - items 60-63
    ("Huyện Tu Mơ Rông", ["Xã Đăk Na", "Xã Đăk Sao"], "Xã Đăk Sao"),
    ("Huyện Tu Mơ Rông", ["Xã Đăk Rơ Ông", "Xã Đăk Tờ Kan"], "Xã Đăk Tờ Kan"),
    ("Huyện Tu Mơ Rông", ["Xã Đăk Hà", "Xã Tu Mơ Rông"], "Xã Tu Mơ Rông"),
    ("Huyện Tu Mơ Rông", ["Xã Ngọk Yêu", "Xã Văn Xuôi", "Xã Tê Xăng", "Xã Ngọk Lây", "Xã Măng Ri"], "Xã Măng Ri"),

    # Huyện Ngọc Hồi (old Kon Tum) - items 64-66
    ("Huyện Ngọc Hồi", ["Thị trấn Plei Kần", "Xã Đăk Xú", "Xã Pờ Y"], "Xã Bờ Y"),
    ("Huyện Ngọc Hồi", ["Xã Đăk Kan", "Xã Sa Loong"], "Xã Sa Loong"),
    ("Huyện Ngọc Hồi", ["Xã Đăk Ang", "Xã Đăk Dục", "Xã Đăk Nông"], "Xã Dục Nông"),

    # Huyện Đăk Glei (old Kon Tum) - items 67-71
    ("Huyện Đăk Glei", ["Xã Đăk Choong", "Xã Xốp"], "Xã Xốp"),
    ("Huyện Đăk Glei", ["Xã Mường Hoong", "Xã Ngọc Linh"], "Xã Ngọc Linh"),
    ("Huyện Đăk Glei", ["Xã Đăk Nhoong", "Xã Đăk Man", "Xã Đăk Plô"], "Xã Đăk Plô"),
    ("Huyện Đăk Glei", ["Thị trấn Đăk Glei", "Xã Đăk Pék"], "Xã Đăk Pék"),
    ("Huyện Đăk Glei", ["Xã Đăk Kroong", "Xã Đăk Môn"], "Xã Đăk Môn"),

    # Huyện Sa Thầy (old Kon Tum) - items 72-75
    ("Huyện Sa Thầy", ["Thị trấn Sa Thầy", "Xã Sa Sơn", "Xã Sa Nhơn"], "Xã Sa Thầy"),
    ("Huyện Sa Thầy", ["Xã Sa Nghĩa", "Xã Hơ Moong", "Xã Sa Bình"], "Xã Sa Bình"),
    ("Huyện Sa Thầy", ["Xã Ya Xiêr", "Xã Ya Tăng", "Xã Ya Ly"], "Xã Ya Ly"),
    ("Huyện Sa Thầy", ["Xã Ia Dom", "Xã Ia Tơi"], "Xã Ia Tơi"),

    # Huyện Kon Rẫy (old Kon Tum) - items 76-78
    ("Huyện Kon Rẫy", ["Xã Đăk Tơ Lung", "Xã Đăk Kôi"], "Xã Đăk Kôi"),
    ("Huyện Kon Rẫy", ["Xã Đăk Tờ Re", "Xã Đăk Ruồng", "Xã Tân Lập"], "Xã Kon Braih"),
    ("Huyện Kon Rẫy", ["Thị trấn Đăk Rve", "Xã Đăk Pne"], "Xã Đăk Rve"),

    # Huyện Kon Plông (old Kon Tum) - items 79-81
    ("Huyện Kon Plông", ["Thị trấn Măng Đen", "Xã Măng Cành", "Xã Đăk Tăng"], "Xã Măng Đen"),
    ("Huyện Kon Plông", ["Xã Đăk Nên", "Xã Đăk Ring", "Xã Măng Bút"], "Xã Măng Bút"),
    ("Huyện Kon Plông", ["Xã Ngọk Tem", "Xã Hiếu", "Xã Pờ Ê"], "Xã Kon Plông"),

    # Thành phố Quảng Ngãi - phường (old Quảng Ngãi) - items 82-84
    ("Thành phố Quảng Ngãi", ["Phường Trương Quang Trọng", "Xã Tịnh Ấn Tây", "Xã Tịnh Ấn Đông", "Xã Tịnh An"], "Phường Trương Quang Trọng"),
    ("Thành phố Quảng Ngãi", ["Phường Nguyễn Nghiêm", "Phường Trần Hưng Đạo", "Phường Nghĩa Chánh", "Phường Chánh Lộ"], "Phường Cẩm Thành"),
    ("Thành phố Quảng Ngãi", ["Phường Lê Hồng Phong", "Phường Trần Phú", "Phường Quảng Phú", "Phường Nghĩa Lộ"], "Phường Nghĩa Lộ"),

    # Thị xã Đức Phổ (old Quảng Ngãi) - items 85-87
    ("Thị xã Đức Phổ", ["Phường Phổ Văn", "Phường Phổ Quang", "Xã Phổ An", "Xã Phổ Thuận"], "Phường Trà Câu"),
    ("Thị xã Đức Phổ", ["Phường Nguyễn Nghiêm", "Phường Phổ Hòa", "Phường Phổ Minh", "Phường Phổ Vinh", "Phường Phổ Ninh"], "Phường Đức Phổ"),
    ("Thị xã Đức Phổ", ["Phường Phổ Thạnh", "Xã Phổ Châu"], "Phường Sa Huỳnh"),

    # Thành phố Kon Tum - phường (old Kon Tum) - items 88-90
    ("Thành phố Kon Tum", ["Phường Quang Trung", "Phường Quyết Thắng", "Phường Thắng Lợi", "Phường Trường Chinh", "Phường Thống Nhất"], "Phường Kon Tum"),
    ("Thành phố Kon Tum", ["Phường Ngô Mây", "Phường Duy Tân", "Xã Đăk Cấm"], "Phường Đăk Cấm"),
    ("Thành phố Kon Tum", ["Phường Trần Hưng Đạo", "Phường Lê Lợi", "Phường Nguyễn Trãi"], "Phường Đăk Bla"),

    # Đặc khu Lý Sơn (old Quảng Ngãi) - item 91
    ("Đặc khu Lý Sơn", ["Huyện Lý Sơn"], "Đặc khu Lý Sơn"),
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

    # Process Quảng Ngãi
    province_name = "Tỉnh Quảng Ngãi"
    province_dia_danh, province_chuyen_doi = generate_province_data(
        province_name, quangngai_restructuring_data
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

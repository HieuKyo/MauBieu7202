#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch 9 - Thái Nguyên (mới) province data generation script
Thái Nguyên (mới) = Thái Nguyên + Bắc Kạn
92 units total: 77 xã and 15 phường
2 xã not being restructured: Sảng Mộc, Thượng Quan
"""

import json
import os

# Thái Nguyên restructuring data
# Format: (huyện, [list of old units], new unit name)
thainguyen_restructuring_data = [
    # OLD THÁI NGUYÊN DISTRICTS

    # Thành phố Thái Nguyên - items 1-3, 76-81
    ("Thành phố Thái Nguyên", ["Xã Thịnh Đức", "Xã Bình Sơn", "Xã Tân Cương"], "Xã Tân Cương"),
    ("Thành phố Thái Nguyên", ["Thị trấn Hùng Sơn", "Xã Phúc Xuân", "Xã Phúc Trìu", "Xã Tân Thái", "Xã Phúc Tân"], "Xã Đại Phúc"),
    ("Thành phố Thái Nguyên", ["Xã Vạn Phái", "Xã Thành Công"], "Xã Thành Công"),
    ("Thành phố Thái Nguyên", ["Phường Trưng Vương", "Phường Túc Duyên", "Phường Đồng Quang", "Phường Quang Trung", "Phường Hoàng Văn Thụ", "Phường Tân Thịnh", "Phường Phan Đình Phùng", "Phường Gia Sàng"], "Phường Phan Đình Phùng"),
    ("Thành phố Thái Nguyên", ["Phường Chùa Hang", "Phường Đồng Bẩm", "Xã Cao Ngạn", "Xã Huống Thượng", "Xã Linh Sơn"], "Phường Linh Sơn"),
    ("Thành phố Thái Nguyên", ["Phường Trung Thành", "Phường Phú Xá", "Phường Tân Thành", "Phường Tân Lập", "Phường Tích Lương", "Phường Cam Giá"], "Phường Tích Lương"),
    ("Thành phố Thái Nguyên", ["Phường Hương Sơn", "Xã Đồng Liên", "Phường Gia Sàng", "Phường Cam Giá"], "Phường Gia Sàng"),
    ("Thành phố Thái Nguyên", ["Phường Thịnh Đán", "Xã Phúc Hà", "Xã Quyết Thắng"], "Phường Quyết Thắng"),
    ("Thành phố Thái Nguyên", ["Phường Tân Long", "Phường Quang Vinh", "Phường Quan Triều", "Xã Sơn Cẩm"], "Phường Quan Triều"),

    # Huyện Định Hóa (old Thái Nguyên) - items 4-11
    ("Huyện Định Hóa", ["Thị trấn Chợ Chu", "Xã Phúc Chu", "Xã Bảo Linh", "Xã Đồng Thịnh"], "Xã Định Hóa"),
    ("Huyện Định Hóa", ["Xã Trung Lương", "Xã Định Biên", "Xã Thanh Định", "Xã Bình Yên"], "Xã Bình Yên"),
    ("Huyện Định Hóa", ["Xã Phú Tiến", "Xã Bộc Nhiêu", "Xã Trung Hội"], "Xã Trung Hội"),
    ("Huyện Định Hóa", ["Xã Tân Dương", "Xã Tân Thịnh", "Xã Phượng Tiến"], "Xã Phượng Tiến"),
    ("Huyện Định Hóa", ["Xã Điềm Mặc", "Xã Phú Đình"], "Xã Phú Đình"),
    ("Huyện Định Hóa", ["Xã Sơn Phú", "Xã Bình Thành"], "Xã Bình Thành"),
    ("Huyện Định Hóa", ["Xã Quy Kỳ", "Xã Kim Phượng"], "Xã Kim Phượng"),
    ("Huyện Định Hóa", ["Xã Linh Thông", "Xã Lam Vỹ"], "Xã Lam Vỹ"),

    # Huyện Võ Nhai (old Thái Nguyên) - items 12-17
    ("Huyện Võ Nhai", ["Thị trấn Đình Cả", "Xã Phú Thượng", "Xã Lâu Thượng"], "Xã Võ Nhai"),
    ("Huyện Võ Nhai", ["Xã Bình Long", "Xã Phương Giao", "Xã Dân Tiến"], "Xã Dân Tiến"),
    ("Huyện Võ Nhai", ["Xã Vũ Chấn", "Xã Nghinh Tường"], "Xã Nghinh Tường"),
    ("Huyện Võ Nhai", ["Xã Thượng Nung", "Xã Thần Xa"], "Xã Thần Sa"),
    ("Huyện Võ Nhai", ["Xã Cúc Đường", "Xã La Hiên"], "Xã La Hiên"),
    ("Huyện Võ Nhai", ["Xã Liên Minh", "Xã Tràng Xá"], "Xã Tràng Xá"),

    # Huyện Phú Lương (old Thái Nguyên) - items 18-21
    ("Huyện Phú Lương", ["Thị trấn Đu", "Thị trấn Giang Tiên", "Xã Yên Lạc", "Xã Động Đạt"], "Xã Phú Lương"),
    ("Huyện Phú Lương", ["Xã Tức Tranh", "Xã Cổ Lũng", "Xã Phú Đô", "Xã Vô Tranh"], "Xã Vô Tranh"),
    ("Huyện Phú Lương", ["Xã Yên Ninh", "Xã Yên Đổ", "Xã Yên Trạch"], "Xã Yên Trạch"),
    ("Huyện Phú Lương", ["Xã Ôn Lương", "Xã Phủ Lý", "Xã Hợp Thành"], "Xã Hợp Thành"),

    # Huyện Đồng Hỷ (old Thái Nguyên) - items 22-27
    ("Huyện Đồng Hỷ", ["Thị trấn Hóa Thượng", "Thị trấn Sông Cầu", "Xã Minh Lập", "Xã Hóa Trung"], "Xã Đồng Hỷ"),
    ("Huyện Đồng Hỷ", ["Xã Tân Long", "Xã Quang Sơn"], "Xã Quang Sơn"),
    ("Huyện Đồng Hỷ", ["Thị trấn Trại Cau", "Xã Hợp Tiến"], "Xã Trại Cau"),
    ("Huyện Đồng Hỷ", ["Xã Cây Thị", "Xã Nam Hòa"], "Xã Nam Hòa"),
    ("Huyện Đồng Hỷ", ["Xã Khe Mo", "Xã Văn Hán"], "Xã Văn Hán"),
    ("Huyện Đồng Hỷ", ["Xã Hòa Bình", "Xã Văn Lăng"], "Xã Văn Lăng"),

    # Huyện Đại Từ (old Thái Nguyên) - items 28-36
    ("Huyện Đại Từ", ["Xã Bình Thuận", "Xã Khôi Kỳ", "Xã Mỹ Yên", "Xã Lục Ba"], "Xã Đại Từ"),
    ("Huyện Đại Từ", ["Xã Minh Tiến", "Xã Phúc Lương", "Xã Đức Lương"], "Xã Đức Lương"),
    ("Huyện Đại Từ", ["Xã Bản Ngoại", "Xã Phú Cường", "Xã Phú Thịnh"], "Xã Phú Thịnh"),
    ("Huyện Đại Từ", ["Xã Hoàng Nông", "Xã Tiên Hội", "Xã La Bằng"], "Xã La Bằng"),
    ("Huyện Đại Từ", ["Xã Phục Linh", "Xã Tân Linh", "Xã Phú Lạc"], "Xã Phú Lạc"),
    ("Huyện Đại Từ", ["Xã Cù Vân", "Xã Hà Thượng", "Xã An Khánh"], "Xã An Khánh"),
    ("Huyện Đại Từ", ["Thị trấn Quân Chu", "Xã Cát Nê"], "Xã Quân Chu"),
    ("Huyện Đại Từ", ["Xã Văn Yên", "Xã Vạn Phú"], "Xã Vạn Phú"),
    ("Huyện Đại Từ", ["Xã Yên Lãng", "Xã Phú Xuyên"], "Xã Phú Xuyên"),

    # Huyện Phú Bình (old Thái Nguyên) - items 37-41
    ("Huyện Phú Bình", ["Thị trấn Hương Sơn", "Xã Xuân Phương", "Xã Úc Kỳ", "Xã Nhã Lộng", "Xã Bảo Lý", "Xã Thượng Đình"], "Xã Phú Bình"),
    ("Huyện Phú Bình", ["Xã Tân Hòa", "Xã Tân Kim", "Xã Tân Thành"], "Xã Tân Thành"),
    ("Huyện Phú Bình", ["Xã Hà Châu", "Xã Nga My", "Xã Điềm Thụy", "Xã Thượng Đình"], "Xã Điềm Thụy"),
    ("Huyện Phú Bình", ["Xã Lương Phú", "Xã Tân Đức", "Xã Thanh Ninh", "Xã Dương Thành", "Xã Kha Sơn"], "Xã Kha Sơn"),
    ("Huyện Phú Bình", ["Xã Bàn Đạt", "Xã Đào Xá", "Xã Tân Khánh"], "Xã Tân Khánh"),

    # Thành phố Sông Công - items 82-84
    ("Thành phố Sông Công", ["Phường Thắng Lợi", "Phường Phố Cò", "Phường Cải Đan"], "Phường Sông Công"),
    ("Thành phố Sông Công", ["Phường Mỏ Chè", "Phường Châu Sơn", "Xã Bá Xuyên"], "Phường Bá Xuyên"),
    ("Thành phố Sông Công", ["Phường Lương Sơn", "Phường Bách Quang", "Xã Tân Quang"], "Phường Bách Quang"),

    # Thành phố Phổ Yên - items 85-88
    ("Thành phố Phổ Yên", ["Phường Ba Hàng", "Phường Hồng Tiến", "Phường Bãi Bông", "Phường Đắc Sơn"], "Phường Phổ Yên"),
    ("Thành phố Phổ Yên", ["Phường Nam Tiến", "Phường Đồng Tiến", "Phường Tân Hương", "Phường Tiên Phong"], "Phường Vạn Xuân"),
    ("Thành phố Phổ Yên", ["Phường Trung Thành", "Phường Đông Cao", "Phường Tân Phú", "Phường Thuận Thành"], "Phường Trung Thành"),
    ("Thành phố Phổ Yên", ["Phường Bắc Sơn", "Xã Minh Đức", "Xã Phúc Thuận"], "Phường Phúc Thuận"),

    # OLD BẮC KẠN DISTRICTS

    # Huyện Pác Nặm (old Bắc Kạn) - items 42-44
    ("Huyện Pác Nặm", ["Xã Bộc Bố", "Xã Nhạn Môn", "Xã Giáo Hiệu", "Xã Bằng Thành"], "Xã Bằng Thành"),
    ("Huyện Pác Nặm", ["Xã Xuân La", "Xã An Thắng", "Xã Nghiên Loan"], "Xã Nghiên Loan"),
    ("Huyện Pác Nặm", ["Xã Công Bằng", "Xã Cổ Linh", "Xã Cao Tân"], "Xã Cao Minh"),

    # Huyện Ba Bể (old Bắc Kạn) - items 45-49
    ("Huyện Ba Bể", ["Xã Cao Thượng", "Xã Nam Mẫu", "Xã Khang Ninh"], "Xã Ba Bể"),
    ("Huyện Ba Bể", ["Thị trấn Chợ Rã", "Xã Thượng Giáo", "Xã Địa Linh"], "Xã Chợ Rã"),
    ("Huyện Ba Bể", ["Xã Bành Trạch", "Xã Hà Hiệu", "Xã Phúc Lộc"], "Xã Phúc Lộc"),
    ("Huyện Ba Bể", ["Xã Yến Dương", "Xã Chu Hương", "Xã Mỹ Phương"], "Xã Thượng Minh"),
    ("Huyện Ba Bể", ["Xã Quảng Khê", "Xã Hoàng Trĩ", "Xã Bằng Phúc", "Xã Đồng Phúc"], "Xã Đồng Phúc"),

    # Huyện Ngân Sơn (old Bắc Kạn) - items 50-55
    ("Huyện Ngân Sơn", ["Xã Thượng Ân", "Xã Bằng Vân"], "Xã Bằng Vân"),
    ("Huyện Ngân Sơn", ["Thị trấn Vân Tùng", "Xã Cốc Đán", "Xã Đức Vân"], "Xã Ngân Sơn"),
    ("Huyện Ngân Sơn", ["Thị trấn Nà Phặc", "Xã Trung Hòa"], "Xã Nà Phặc"),
    ("Huyện Ngân Sơn", ["Xã Thuần Mang", "Xã Hiệp Lực"], "Xã Hiệp Lực"),
    ("Huyện Ngân Sơn", ["Xã Xuân Lạc", "Xã Đồng Lạc", "Xã Nam Cường"], "Xã Nam Cường"),
    ("Huyện Ngân Sơn", ["Xã Tân Lập", "Xã Quảng Bạch"], "Xã Quảng Bạch"),

    # Huyện Chợ Đồn (old Bắc Kạn) - items 56-59
    ("Huyện Chợ Đồn", ["Xã Bản Thi", "Xã Yên Thượng", "Xã Yên Thịnh"], "Xã Yên Thịnh"),
    ("Huyện Chợ Đồn", ["Thị trấn Bằng Lũng", "Xã Ngọc Phái", "Xã Phương Viên", "Xã Bằng Lãng"], "Xã Chợ Đồn"),
    ("Huyện Chợ Đồn", ["Xã Đại Sảo", "Xã Yên Mỹ", "Xã Yên Phong"], "Xã Yên Phong"),
    ("Huyện Chợ Đồn", ["Xã Lương Bằng", "Xã Bình Trung", "Xã Nghĩa Tá"], "Xã Nghĩa Tá"),

    # Huyện Bạch Thông (old Bắc Kạn) - items 60-66
    ("Huyện Bạch Thông", ["Thị trấn Phủ Thông", "Xã Vi Hương", "Xã Tân Tú", "Xã Lục Bình"], "Xã Phủ Thông"),
    ("Huyện Bạch Thông", ["Xã Quân Hà", "Xã Nguyên Phúc", "Xã Mỹ Thanh", "Xã Cẩm Giàng"], "Xã Cẩm Giàng"),
    ("Huyện Bạch Thông", ["Xã Sỹ Bình", "Xã Vũ Muộn", "Xã Cao Sơn"], "Xã Vĩnh Thông"),
    ("Huyện Bạch Thông", ["Xã Đồng Thắng", "Xã Dương Phong", "Xã Quang Thuận"], "Xã Bạch Thông"),
    ("Huyện Bạch Thông", ["Xã Dương Quang", "Xã Đôn Phong"], "Xã Phong Quang"),
    ("Huyện Bạch Thông", ["Xã Kim Hỷ", "Xã Lương Thượng", "Xã Văn Lang"], "Xã Văn Lang"),
    ("Huyện Bạch Thông", ["Xã Văn Vũ", "Xã Cường Lợi"], "Xã Cường Lợi"),

    # Huyện Na Rì (old Bắc Kạn) - items 67-72
    ("Huyện Na Rì", ["Thị trấn Yến Lạc", "Xã Sơn Thành", "Xã Kim Lư"], "Xã Na Rì"),
    ("Huyện Na Rì", ["Xã Văn Minh", "Xã Cư Lễ", "Xã Trần Phú"], "Xã Trần Phú"),
    ("Huyện Na Rì", ["Xã Quang Phong", "Xã Dương Sơn", "Xã Côn Minh"], "Xã Côn Minh"),
    ("Huyện Na Rì", ["Xã Đổng Xá", "Xã Liêm Thủy", "Xã Xuân Dương"], "Xã Xuân Dương"),
    ("Huyện Na Rì", ["Xã Tân Sơn", "Xã Cao Kỳ", "Xã Hòa Mục"], "Xã Tân Kỳ"),
    ("Huyện Na Rì", ["Xã Thanh Vận", "Xã Mai Lạp", "Xã Thanh Mai"], "Xã Thanh Mai"),

    # Huyện Chợ Mới (old Bắc Kạn) - items 73-75
    ("Huyện Chợ Mới", ["Xã Nông Hạ", "Xã Thanh Thịnh"], "Xã Thanh Thịnh"),
    ("Huyện Chợ Mới", ["Thị trấn Đồng Tâm", "Xã Quảng Chu", "Xã Như Cố"], "Xã Chợ Mới"),
    ("Huyện Chợ Mới", ["Xã Yên Cư", "Xã Bình Văn", "Xã Yên Hân"], "Xã Yên Bình"),

    # Thành phố Bắc Kạn (old Bắc Kạn) - items 89-90
    ("Thành phố Bắc Kạn", ["Phường Nguyễn Thị Minh Khai", "Phường Huyền Tụng", "Phường Đức Xuân"], "Phường Đức Xuân"),
    ("Thành phố Bắc Kạn", ["Phường Sông Cầu", "Phường Phùng Chí Kiên", "Phường Xuất Hóa", "Xã Nông Thượng"], "Phường Bắc Kạn"),
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

    # Process Thái Nguyên
    tinh_name = "Tỉnh Thái Nguyên"

    print(f"Processing {tinh_name}...")

    # Generate entries
    dia_danh_entry = generate_dia_danh_entry(tinh_name, thainguyen_restructuring_data)
    chuyen_doi_entries = generate_chuyen_doi_entries(tinh_name, thainguyen_restructuring_data)

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

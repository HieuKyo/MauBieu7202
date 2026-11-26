#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate restructuring data for Tuyên Quang (mới) - Batch 10
Mega-province combining: Tuyên Quang + Hà Giang
111 items, 124 units (117 xã, 7 phường)
"""

import json
import os

# Get the project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
data_dir = os.path.join(project_root, 'templates_app', 'static', 'data')

# Tuyên Quang (mới) restructuring data
# Format: (district, [old units], new unit name)
tuyenquang_restructuring_data = [
    # Huyện Lâm Bình (Tuyên Quang)
    ("Huyện Lâm Bình", ["Xã Khuôn Hà", "Xã Thượng Lâm"], "Xã Thượng Lâm"),
    ("Huyện Lâm Bình", ["Thị trấn Lăng Can", "Xã Phúc Yên", "Xã Xuân Lập"], "Xã Lâm Bình"),

    # Huyện Nà Hang (Tuyên Quang)
    ("Huyện Nà Hang", ["Xã Phúc Sơn", "Xã Hồng Quang", "Xã Minh Quang"], "Xã Minh Quang"),
    ("Huyện Nà Hang", ["Xã Thổ Bình", "Xã Bình An"], "Xã Bình An"),
    ("Huyện Nà Hang", ["Xã Sinh Long", "Xã Côn Lôn"], "Xã Côn Lôn"),
    ("Huyện Nà Hang", ["Xã Khâu Tinh", "Xã Yên Hoa"], "Xã Yên Hoa"),
    ("Huyện Nà Hang", ["Xã Thượng Giáp", "Xã Thượng Nông"], "Xã Thượng Nông"),
    ("Huyện Nà Hang", ["Xã Đà Vị", "Xã Sơn Phú", "Xã Hồng Thái"], "Xã Hồng Thái"),
    ("Huyện Nà Hang", ["Thị trấn Na Hang", "Xã Năng Khả", "Xã Thanh Tương"], "Xã Nà Hang"),

    # Huyện Chiêm Hóa (Tuyên Quang)
    ("Huyện Chiêm Hóa", ["Xã Hùng Mỹ", "Xã Tân Mỹ"], "Xã Tân Mỹ"),
    ("Huyện Chiêm Hóa", ["Xã Bình Phú", "Xã Yên Lập"], "Xã Yên Lập"),
    ("Huyện Chiêm Hóa", ["Xã Hà Lang", "Xã Tân An"], "Xã Tân An"),
    ("Huyện Chiêm Hóa", ["Thị trấn Vĩnh Lộc", "Xã Xuân Quang", "Xã Phúc Thịnh", "Xã Ngọc Hội", "Xã Trung Hòa"], "Xã Chiêm Hóa"),
    ("Huyện Chiêm Hóa", ["Xã Tân Thịnh", "Xã Nhân Lý", "Xã Hòa An"], "Xã Hòa An"),
    ("Huyện Chiêm Hóa", ["Xã Phú Bình", "Xã Kiên Đài"], "Xã Kiên Đài"),
    ("Huyện Chiêm Hóa", ["Xã Linh Phú", "Xã Tri Phú"], "Xã Tri Phú"),
    ("Huyện Chiêm Hóa", ["Xã Vinh Quang", "Xã Bình Nhân", "Xã Kim Bình"], "Xã Kim Bình"),
    ("Huyện Chiêm Hóa", ["Xã Hòa Phú", "Xã Yên Nguyên"], "Xã Yên Nguyên"),

    # Huyện Hàm Yên (Tuyên Quang)
    ("Huyện Hàm Yên", ["Xã Yên Lâm", "Xã Yên Phú"], "Xã Yên Phú"),
    ("Huyện Hàm Yên", ["Xã Yên Thuận", "Xã Minh Khương", "Xã Bạch Xa"], "Xã Bạch Xa"),
    ("Huyện Hàm Yên", ["Xã Minh Dân", "Xã Phù Lưu"], "Xã Phù Lưu"),
    ("Huyện Hàm Yên", ["Thị trấn Tân Yên", "Xã Tân Thành", "Xã Bằng Cốc", "Xã Nhân Mục"], "Xã Hàm Yên"),
    ("Huyện Hàm Yên", ["Xã Minh Hương", "Xã Bình Xa"], "Xã Bình Xa"),
    ("Huyện Hàm Yên", ["Xã Thành Long", "Xã Thái Sơn"], "Xã Thái Sơn"),
    ("Huyện Hàm Yên", ["Xã Đức Ninh", "Xã Thái Hòa"], "Xã Thái Hòa"),

    # Huyện Yên Sơn (Tuyên Quang)
    ("Huyện Yên Sơn", ["Xã Trung Minh", "Xã Hùng Lợi"], "Xã Hùng Lợi"),
    ("Huyện Yên Sơn", ["Xã Đạo Viện", "Xã Công Đa", "Xã Trung Sơn"], "Xã Trung Sơn"),
    ("Huyện Yên Sơn", ["Xã Phú Thịnh", "Xã Tiến Bộ", "Xã Thái Bình"], "Xã Thái Bình"),
    ("Huyện Yên Sơn", ["Xã Tân Tiến", "Xã Tân Long"], "Xã Tân Long"),
    ("Huyện Yên Sơn", ["Xã Trung Trực", "Xã Phúc Ninh", "Xã Xuân Vân"], "Xã Xuân Vân"),
    ("Huyện Yên Sơn", ["Xã Quý Quân", "Xã Chiêu Yên", "Xã Lực Hành"], "Xã Lực Hành"),
    ("Huyện Yên Sơn", ["Thị trấn Yên Sơn", "Xã Tứ Quận", "Xã Lang Quán", "Xã Chân Sơn"], "Xã Yên Sơn"),
    ("Huyện Yên Sơn", ["Xã Nhữ Hán", "Xã Đội Bình", "Xã Nhữ Khê"], "Xã Nhữ Khê"),
    ("Huyện Yên Sơn", ["Xã Kim Quan", "Xã Trung Yên", "Xã Tân Trào"], "Xã Tân Trào"),
    ("Huyện Yên Sơn", ["Xã Bình Yên", "Xã Lương Thiện", "Xã Minh Thanh"], "Xã Minh Thanh"),

    # Huyện Sơn Dương (Tuyên Quang)
    ("Huyện Sơn Dương", ["Thị trấn Sơn Dương", "Xã Hợp Thành", "Xã Phúc Ứng", "Xã Tú Thịnh"], "Xã Sơn Dương"),
    ("Huyện Sơn Dương", ["Xã Thượng Ấm", "Xã Cấp Tiến", "Xã Vĩnh Lợi"], "Xã Bình Ca"),
    ("Huyện Sơn Dương", ["Xã Kháng Nhật", "Xã Hợp Hòa", "Xã Tân Thanh"], "Xã Tân Thanh"),
    ("Huyện Sơn Dương", ["Xã Ninh Lai", "Xã Thiện Kế", "Xã Sơn Nam"], "Xã Sơn Thủy"),
    ("Huyện Sơn Dương", ["Xã Đại Phú", "Xã Tam Đa", "Xã Phú Lương"], "Xã Phú Lương"),
    ("Huyện Sơn Dương", ["Xã Hào Phú", "Xã Đông Lợi", "Xã Trường Sinh"], "Xã Trường Sinh"),
    ("Huyện Sơn Dương", ["Xã Chi Thiết", "Xã Văn Phú", "Xã Hồng Sơn"], "Xã Hồng Sơn"),
    ("Huyện Sơn Dương", ["Xã Đồng Quý", "Xã Quyết Thắng", "Xã Đông Thọ"], "Xã Đông Thọ"),

    # Huyện Đồng Văn (Hà Giang)
    ("Huyện Đồng Văn", ["Xã Má Lé", "Xã Lũng Táo", "Xã Lũng Cú"], "Xã Lũng Cú"),
    ("Huyện Đồng Văn", ["Thị trấn Đồng Văn", "Xã Tả Lủng", "Xã Tả Phìn", "Xã Thài Phìn Tủng", "Xã Pải Lủng"], "Xã Đồng Văn"),
    ("Huyện Đồng Văn", ["Xã Sủng Là", "Xã Sính Lủng", "Xã Sảng Tủng", "Xã Sà Phìn"], "Xã Sà Phìn"),
    ("Huyện Đồng Văn", ["Thị trấn Phố Bảng", "Xã Phố Là", "Xã Phố Cáo", "Xã Lũng Thầu"], "Xã Phố Bảng"),
    ("Huyện Đồng Văn", ["Xã Sủng Trái", "Xã Hố Quáng Phìn", "Xã Lũng Phìn"], "Xã Lũng Phìn"),

    # Huyện Mèo Vạc (Hà Giang)
    ("Huyện Mèo Vạc", ["Xã Lũng Chinh", "Xã Sủng Trà", "Xã Sủng Máng"], "Xã Sủng Máng"),
    ("Huyện Mèo Vạc", ["Xã Thượng Phùng", "Xã Xín Cái", "Xã Sơn Vĩ"], "Xã Sơn Vĩ"),
    ("Huyện Mèo Vạc", ["Thị trấn Mèo Vạc", "Xã Tả Lủng", "Xã Giàng Chu Phìn", "Xã Pả Vi"], "Xã Mèo Vạc"),
    ("Huyện Mèo Vạc", ["Xã Cán Chu Phìn", "Xã Lũng Pù", "Xã Khâu Vai"], "Xã Khâu Vai"),
    ("Huyện Mèo Vạc", ["Xã Niêm Tòng", "Xã Niêm Sơn"], "Xã Niêm Sơn"),
    ("Huyện Mèo Vạc", ["Xã Nậm Ban", "Xã Tát Ngà"], "Xã Tát Ngà"),

    # Huyện Yên Minh (Hà Giang)
    ("Huyện Yên Minh", ["Xã Sủng Cháng", "Xã Sủng Thài", "Xã Thắng Mố"], "Xã Thắng Mố"),
    ("Huyện Yên Minh", ["Xã Phú Lũng", "Xã Na Khê", "Xã Bạch Đích"], "Xã Bạch Đích"),
    ("Huyện Yên Minh", ["Thị trấn Yên Minh", "Xã Lao Và Chải", "Xã Hữu Vinh", "Xã Đông Minh", "Xã Vần Chải"], "Xã Yên Minh"),
    ("Huyện Yên Minh", ["Xã Ngam La", "Xã Mậu Long", "Xã Mậu Duệ"], "Xã Mậu Duệ"),
    ("Huyện Yên Minh", ["Xã Du Tiến", "Xã Du Già"], "Xã Du Già"),
    ("Huyện Yên Minh", ["Xã Lũng Hồ", "Xã Đường Thượng"], "Xã Đường Thượng"),
    ("Huyện Yên Minh", ["Xã Thái An", "Xã Đông Hà", "Xã Lùng Tám"], "Xã Lùng Tám"),

    # Huyện Quản Bạ (Hà Giang)
    ("Huyện Quản Bạ", ["Xã Bát Đại Sơn", "Xã Cán Tỷ"], "Xã Cán Tỷ"),
    ("Huyện Quản Bạ", ["Xã Thanh Vân", "Xã Nghĩa Thuận"], "Xã Nghĩa Thuận"),
    ("Huyện Quản Bạ", ["Thị trấn Tam Sơn", "Xã Quyết Tiến", "Xã Quản Bạ"], "Xã Quản Bạ"),
    ("Huyện Quản Bạ", ["Xã Cao Mã Pờ", "Xã Tả Ván", "Xã Tùng Vài"], "Xã Tùng Vài"),

    # Huyện Bắc Mê (Hà Giang)
    ("Huyện Bắc Mê", ["Xã Phiêng Luông", "Xã Yên Cường"], "Xã Yên Cường"),
    ("Huyện Bắc Mê", ["Xã Đường Âm", "Xã Phú Nam", "Xã Đường Hồng"], "Xã Đường Hồng"),
    ("Huyện Bắc Mê", ["Thị trấn Yên Phú", "Xã Yên Phong", "Xã Lạc Nông"], "Xã Bắc Mê"),
    ("Huyện Bắc Mê", ["Xã Minh Ngọc", "Xã Thượng Tân", "Xã Yên Định"], "Xã Minh Ngọc"),
    ("Huyện Bắc Mê", ["Xã Ngọc Đường", "Xã Yên Định"], "Xã Ngọc Đường"),

    # Huyện Vị Xuyên (Hà Giang)
    ("Huyện Vị Xuyên", ["Xã Xín Chải", "Xã Thanh Đức", "Xã Lao Chải"], "Xã Lao Chải"),
    ("Huyện Vị Xuyên", ["Xã Phương Tiến", "Xã Thanh Thủy"], "Xã Thanh Thủy"),
    ("Huyện Vị Xuyên", ["Xã Kim Thạch", "Xã Kim Linh", "Xã Phú Linh"], "Xã Phú Linh"),
    ("Huyện Vị Xuyên", ["Xã Ngọc Linh", "Xã Trung Thành", "Xã Linh Hồ"], "Xã Linh Hồ"),
    ("Huyện Vị Xuyên", ["Xã Ngọc Minh", "Xã Bạch Ngọc"], "Xã Bạch Ngọc"),
    ("Huyện Vị Xuyên", ["Thị trấn Vị Xuyên", "Thị trấn Nông trường Việt Lâm", "Xã Đạo Đức", "Xã Việt Lâm"], "Xã Vị Xuyên"),
    ("Huyện Vị Xuyên", ["Xã Quảng Ngần", "Xã Việt Lâm"], "Xã Việt Lâm"),

    # Huyện Bắc Quang (Hà Giang)
    ("Huyện Bắc Quang", ["Xã Tân Thành", "Xã Tân Lập", "Xã Tân Quang"], "Xã Tân Quang"),
    ("Huyện Bắc Quang", ["Xã Đồng Tiến", "Xã Thượng Bình", "Xã Đồng Tâm"], "Xã Đồng Tâm"),
    ("Huyện Bắc Quang", ["Xã Hữu Sản", "Xã Đức Xuân", "Xã Liên Hiệp"], "Xã Liên Hiệp"),
    ("Huyện Bắc Quang", ["Xã Kim Ngọc", "Xã Vô Điếm", "Xã Bằng Hành"], "Xã Bằng Hành"),
    ("Huyện Bắc Quang", ["Thị trấn Việt Quang", "Xã Quang Minh", "Xã Việt Vinh"], "Xã Bắc Quang"),
    ("Huyện Bắc Quang", ["Xã Việt Hồng", "Xã Tiên Kiều", "Xã Hùng An"], "Xã Hùng An"),
    ("Huyện Bắc Quang", ["Thị trấn Vĩnh Tuy", "Xã Vĩnh Hảo", "Xã Đông Thành"], "Xã Vĩnh Tuy"),
    ("Huyện Bắc Quang", ["Xã Vĩnh Phúc", "Xã Đồng Yên"], "Xã Đồng Yên"),

    # Huyện Quang Bình (Hà Giang)
    ("Huyện Quang Bình", ["Xã Vĩ Thượng", "Xã Hương Sơn", "Xã Tiên Yên"], "Xã Tiên Yên"),
    ("Huyện Quang Bình", ["Xã Nà Khương", "Xã Xuân Giang"], "Xã Xuân Giang"),
    ("Huyện Quang Bình", ["Xã Yên Hà", "Xã Bằng Lang"], "Xã Bằng Lang"),
    ("Huyện Quang Bình", ["Xã Bản Rịa", "Xã Yên Thành"], "Xã Yên Thành"),
    ("Huyện Quang Bình", ["Thị trấn Yên Bình", "Xã Tân Nam"], "Xã Quang Bình"),
    ("Huyện Quang Bình", ["Xã Tân Bắc", "Xã Tân Trịnh"], "Xã Tân Trịnh"),
    ("Huyện Quang Bình", ["Xã Xuân Minh", "Xã Thông Nguyên"], "Xã Thông Nguyên"),

    # Huyện Hoàng Su Phì (Hà Giang)
    ("Huyện Hoàng Su Phì", ["Xã Nậm Khòa", "Xã Nam Sơn", "Xã Hồ Thầu"], "Xã Hồ Thầu"),
    ("Huyện Hoàng Su Phì", ["Xã Nậm Ty", "Xã Tả Sử Choóng", "Xã Nậm Dịch"], "Xã Nậm Dịch"),
    ("Huyện Hoàng Su Phì", ["Xã Tân Tiến", "Xã Bản Nhùng", "Xã Túng Sán"], "Xã Tân Tiến"),
    ("Huyện Hoàng Su Phì", ["Thị trấn Vinh Quang", "Xã Bản Luốc", "Xã Ngàm Đăng Vài", "Xã Tụ Nhân", "Xã Đản Ván"], "Xã Hoàng Su Phì"),
    ("Huyện Hoàng Su Phì", ["Xã Pố Lồ", "Xã Thèn Chu Phìn", "Xã Thàng Tín"], "Xã Thàng Tín"),
    ("Huyện Hoàng Su Phì", ["Xã Bản Phùng", "Xã Chiến Phố", "Xã Bản Máy"], "Xã Bản Máy"),
    ("Huyện Hoàng Su Phì", ["Xã Sán Sả Hồ", "Xã Nàng Đôn", "Xã Pờ Ly Ngài"], "Xã Pờ Ly Ngài"),

    # Huyện Xín Mần (Hà Giang)
    ("Huyện Xín Mần", ["Xã Thèn Phàng", "Xã Nàn Xỉn", "Xã Bản Díu", "Xã Chí Cà", "Xã Xín Mần"], "Xã Xín Mần"),
    ("Huyện Xín Mần", ["Thị trấn Cốc Pài", "Xã Nàn Ma", "Xã Bản Ngò", "Xã Pà Vầy Sủ"], "Xã Pà Vầy Sủ"),
    ("Huyện Xín Mần", ["Xã Chế Là", "Xã Tả Nhìu", "Xã Nấm Dẩn"], "Xã Nấm Dẩn"),
    ("Huyện Xín Mần", ["Xã Cốc Rế", "Xã Thu Tà", "Xã Trung Thịnh"], "Xã Trung Thịnh"),
    ("Huyện Xín Mần", ["Xã Nà Chì", "Xã Khuôn Lùng"], "Xã Khuôn Lùng"),

    # Thành phố Tuyên Quang (Tuyên Quang)
    ("Thành phố Tuyên Quang", ["Phường Mỹ Lâm", "Xã Mỹ Bằng", "Xã Kim Phú"], "Phường Mỹ Lâm"),
    ("Thành phố Tuyên Quang", ["Phường Ỷ La", "Phường Tân Hà", "Phường Phan Thiết", "Phường Minh Xuân", "Phường Tân Quang", "Xã Trung Môn", "Xã Kim Phú"], "Phường Minh Xuân"),
    ("Thành phố Tuyên Quang", ["Phường Nông Tiến", "Xã Tràng Đà", "Xã Thái Bình"], "Phường Nông Tiến"),
    ("Thành phố Tuyên Quang", ["Phường Hưng Thành", "Phường An Tường", "Xã Lưỡng Vượng", "Xã An Khang", "Xã Hoàng Khai"], "Phường An Tường"),
    ("Thành phố Tuyên Quang", ["Phường Đội Cấn", "Xã Thái Long"], "Phường Bình Thuận"),

    # Thành phố Hà Giang (Hà Giang)
    ("Thành phố Hà Giang", ["Phường Nguyễn Trãi", "Xã Phương Thiện", "Xã Phương Độ", "Phường Quang Trung"], "Phường Hà Giang 1"),
    ("Thành phố Hà Giang", ["Phường Ngọc Hà", "Phường Trần Phú", "Phường Minh Khai", "Phường Quang Trung", "Xã Phong Quang"], "Phường Hà Giang 2"),
]

# Old provinces mapping for mega-province
old_provinces = {
    "Tỉnh Tuyên Quang": [
        "Huyện Lâm Bình", "Huyện Nà Hang", "Huyện Chiêm Hóa", "Huyện Hàm Yên",
        "Huyện Yên Sơn", "Huyện Sơn Dương", "Thành phố Tuyên Quang"
    ],
    "Tỉnh Hà Giang": [
        "Huyện Đồng Văn", "Huyện Mèo Vạc", "Huyện Yên Minh", "Huyện Quản Bạ",
        "Huyện Bắc Mê", "Huyện Vị Xuyên", "Huyện Bắc Quang", "Huyện Quang Bình",
        "Huyện Hoàng Su Phì", "Huyện Xín Mần", "Thành phố Hà Giang"
    ]
}

def get_old_province(district):
    """Get the old province name for a district"""
    for province, districts in old_provinces.items():
        if district in districts:
            return province
    return "Tỉnh Tuyên Quang"  # default

def main():
    # Load existing data
    dia_danh_path = os.path.join(data_dir, 'dia_danh.json')
    chuyen_doi_path = os.path.join(data_dir, 'chuyen_doi.json')

    with open(dia_danh_path, 'r', encoding='utf-8') as f:
        dia_danh = json.load(f)

    with open(chuyen_doi_path, 'r', encoding='utf-8') as f:
        chuyen_doi = json.load(f)

    new_province = "Tỉnh Tuyên Quang"

    # Create province structure
    if new_province not in dia_danh:
        dia_danh[new_province] = {}

    # Process restructuring data
    mappings_count = 0

    for district, old_units, new_unit in tuyenquang_restructuring_data:
        # Add to dia_danh structure
        if district not in dia_danh[new_province]:
            dia_danh[new_province][district] = []

        if new_unit not in dia_danh[new_province][district]:
            dia_danh[new_province][district].append(new_unit)

        # Get old province for this district
        old_province = get_old_province(district)

        # Create conversion mappings
        for old_unit in old_units:
            old_key = f", {old_unit}, {district}, {old_province}"
            new_value = f", {new_unit}, {district}, {new_province}"

            if old_key not in chuyen_doi:
                chuyen_doi[old_key] = new_value
                mappings_count += 1

    # Sort districts and units
    for district in dia_danh[new_province]:
        dia_danh[new_province][district].sort(key=lambda x: x.lower())

    # Save updated data
    with open(dia_danh_path, 'w', encoding='utf-8') as f:
        json.dump(dia_danh, f, ensure_ascii=False, indent=2)

    with open(chuyen_doi_path, 'w', encoding='utf-8') as f:
        json.dump(chuyen_doi, f, ensure_ascii=False, indent=2)

    # Also save individual province file
    province_file = os.path.join(data_dir, 'tỉnh_tuyên_quang_dia_danh.json')
    with open(province_file, 'w', encoding='utf-8') as f:
        json.dump({new_province: dia_danh[new_province]}, f, ensure_ascii=False, indent=2)

    print(f"Processing {new_province}...")
    print(f"  - {mappings_count} conversion mappings")
    print(f"\nTotal new mappings: {mappings_count}")
    print("\nFinal totals:")
    print(f"  - dia_danh provinces: {len(dia_danh)}")
    print(f"  - chuyen_doi mappings: {len(chuyen_doi)}")

if __name__ == '__main__':
    main()

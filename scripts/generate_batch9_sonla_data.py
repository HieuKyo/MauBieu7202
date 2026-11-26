#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch 9 - Sơn La province data generation script
75 units total: 67 xã and 8 phường
7 xã not being restructured: Mường Lạn, Phiêng Khoài, Suối Tọ, Ngọc Chiến, Tân Yên, Mường Bám, Mường Lèo
"""

import json
import os

# Sơn La restructuring data
# Format: (huyện, [list of old units], new unit name)
sonla_restructuring_data = [
    # Thị xã Mộc Châu - items 1-7
    ("Thị xã Mộc Châu", ["Xã Chiềng Chung", "Xã Đoàn Kết"], "Xã Đoàn Kết"),
    ("Thị xã Mộc Châu", ["Xã Chiềng Khừa", "Xã Lóng Sập"], "Xã Lóng Sập"),
    ("Thị xã Mộc Châu", ["Xã Chiềng Xuân", "Xã Chiềng Sơn"], "Xã Chiềng Sơn"),
    ("Thị xã Mộc Châu", ["Xã Lóng Luông", "Xã Chiềng Yên", "Xã Mường Men", "Xã Vân Hồ"], "Xã Vân Hồ"),
    ("Thị xã Mộc Châu", ["Xã Mường Tè", "Xã Liên Hòa", "Xã Quang Minh", "Xã Song Khủa"], "Xã Song Khủa"),
    ("Thị xã Mộc Châu", ["Xã Chiềng Khoa", "Xã Suối Bàng", "Xã Tô Múa"], "Xã Tô Múa"),
    ("Thị xã Mộc Châu", ["Xã Tân Xuân", "Xã Xuân Nha"], "Xã Xuân Nha"),

    # Huyện Quỳnh Nhai - items 8-11
    ("Huyện Quỳnh Nhai", ["Thị trấn Mường Giàng", "Xã Chiềng Bằng", "Xã Chiềng Khoang", "Xã Chiềng Ơn"], "Xã Quỳnh Nhai"),
    ("Huyện Quỳnh Nhai", ["Xã Chiềng Khay", "Xã Cà Nàng", "Xã Mường Chiên"], "Xã Mường Chiên"),
    ("Huyện Quỳnh Nhai", ["Xã Pá Ma Pha Khinh", "Xã Mường Giôn"], "Xã Mường Giôn"),
    ("Huyện Quỳnh Nhai", ["Xã Nặm Ét", "Xã Mường Sại"], "Xã Mường Sại"),

    # Huyện Thuận Châu - items 12-20
    ("Huyện Thuận Châu", ["Thị trấn Thuận Châu", "Xã Phổng Ly", "Xã Thôm Mòn", "Xã Tông Lạnh", "Xã Chiềng Pấc"], "Xã Thuận Châu"),
    ("Huyện Thuận Châu", ["Xã Chiềng Ngàm", "Xã Nong Lay", "Xã Tông Cọ", "Xã Chiềng La"], "Xã Chiềng La"),
    ("Huyện Thuận Châu", ["Xã Chiềng Bôm", "Xã Púng Tra", "Xã Nậm Lầu"], "Xã Nậm Lầu"),
    ("Huyện Thuận Châu", ["Xã Bản Lầm", "Xã Bon Phặng", "Xã Muổi Nọi"], "Xã Muổi Nọi"),
    ("Huyện Thuận Châu", ["Xã Liệp Tè", "Xã Bó Mười", "Xã Mường Khiêng"], "Xã Mường Khiêng"),
    ("Huyện Thuận Châu", ["Xã Co Tòng", "Xã Pá Lông", "Xã Co Mạ"], "Xã Co Mạ"),
    ("Huyện Thuận Châu", ["Xã Phổng Lái", "Xã Chiềng Pha"], "Xã Bình Thuận"),
    ("Huyện Thuận Châu", ["Xã Phổng Lập", "Xã Mường É"], "Xã Mường É"),
    ("Huyện Thuận Châu", ["Xã É Tòng", "Xã Long Hẹ"], "Xã Long Hẹ"),

    # Huyện Mường La - items 21-24
    ("Huyện Mường La", ["Thị trấn Ít Ong", "Xã Nặm Păm", "Xã Chiềng San", "Xã Chiềng Muôn", "Xã Mường Trai", "Xã Pi Toong"], "Xã Mường La"),
    ("Huyện Mường La", ["Xã Nậm Giôn", "Xã Hua Trai", "Xã Chiềng Lao"], "Xã Chiềng Lao"),
    ("Huyện Mường La", ["Xã Mường Chùm", "Xã Tạ Bú", "Xã Mường Bú"], "Xã Mường Bú"),
    ("Huyện Mường La", ["Xã Chiềng Ân", "Xã Chiềng Công", "Xã Chiềng Hoa"], "Xã Chiềng Hoa"),

    # Huyện Bắc Yên - items 25-30
    ("Huyện Bắc Yên", ["Thị trấn Bắc Yên", "Xã Phiêng Ban", "Xã Hồng Ngài", "Xã Song Pe"], "Xã Bắc Yên"),
    ("Huyện Bắc Yên", ["Xã Làng Chếu", "Xã Háng Đồng", "Xã Tà Xùa"], "Xã Tà Xùa"),
    ("Huyện Bắc Yên", ["Xã Mường Khoa", "Xã Hua Nhàn", "Xã Tạ Khoa"], "Xã Tạ Khoa"),
    ("Huyện Bắc Yên", ["Xã Hang Chú", "Xã Xím Vàng"], "Xã Xím Vàng"),
    ("Huyện Bắc Yên", ["Xã Chim Vàn", "Xã Pắc Ngà"], "Xã Pắc Ngà"),
    ("Huyện Bắc Yên", ["Xã Phiêng Côn", "Xã Chiềng Sại"], "Xã Chiềng Sại"),

    # Huyện Phù Yên - items 31-37
    ("Huyện Phù Yên", ["Thị trấn Quang Huy", "Xã Huy Hạ", "Xã Huy Tường", "Xã Huy Tân", "Xã Huy Thượng"], "Xã Phù Yên"),
    ("Huyện Phù Yên", ["Xã Tường Phù", "Xã Suối Bau", "Xã Sập Xa", "Xã Gia Phù"], "Xã Gia Phù"),
    ("Huyện Phù Yên", ["Xã Tường Thượng", "Xã Tường Phong", "Xã Tường Tiến", "Xã Tường Hạ"], "Xã Tường Hạ"),
    ("Huyện Phù Yên", ["Xã Mường Thải", "Xã Tân Lang", "Xã Mường Cơi"], "Xã Mường Cơi"),
    ("Huyện Phù Yên", ["Xã Mường Do", "Xã Mường Lang", "Xã Mường Bang"], "Xã Mường Bang"),
    ("Huyện Phù Yên", ["Xã Bắc Phong", "Xã Nam Phong", "Xã Tân Phong"], "Xã Tân Phong"),
    ("Huyện Phù Yên", ["Xã Đá Đỏ", "Xã Kim Bon"], "Xã Kim Bon"),

    # Huyện Yên Châu - items 38-41
    ("Huyện Yên Châu", ["Thị trấn Yên Châu", "Xã Chiềng Đông", "Xã Chiềng Sàng", "Xã Chiềng Pằn", "Xã Chiềng Khoi", "Xã Sặp Vạt"], "Xã Yên Châu"),
    ("Huyện Yên Châu", ["Xã Tú Nang", "Xã Mường Lựm", "Xã Chiềng Hặc"], "Xã Chiềng Hặc"),
    ("Huyện Yên Châu", ["Xã Chiềng Tương", "Xã Lóng Phiêng"], "Xã Lóng Phiêng"),
    ("Huyện Yên Châu", ["Xã Chiềng On", "Xã Yên Sơn"], "Xã Yên Sơn"),

    # Huyện Mai Sơn - items 42-48
    ("Huyện Mai Sơn", ["Xã Chiềng Ban", "Xã Chiềng Kheo", "Xã Chiềng Dong", "Xã Chiềng Ve", "Xã Chiềng Mai"], "Xã Chiềng Mai"),
    ("Huyện Mai Sơn", ["Thị trấn Hát Lót", "Xã Hát Lót", "Xã Cò Nòi"], "Xã Mai Sơn"),
    ("Huyện Mai Sơn", ["Xã Nà Ớt", "Xã Chiềng Lương", "Xã Phiêng Pằn"], "Xã Phiêng Pằn"),
    ("Huyện Mai Sơn", ["Xã Mường Bằng", "Xã Mường Bon", "Xã Chiềng Mung"], "Xã Chiềng Mung"),
    ("Huyện Mai Sơn", ["Xã Chiềng Nơi", "Xã Phiêng Cằm"], "Xã Phiêng Cằm"),
    ("Huyện Mai Sơn", ["Xã Chiềng Chung", "Xã Mường Chanh"], "Xã Mường Chanh"),
    ("Huyện Mai Sơn", ["Xã Nà Bó", "Xã Tà Hộc"], "Xã Tà Hộc"),

    # Huyện Sông Mã - items 49-58
    ("Huyện Sông Mã", ["Xã Chiềng Chăn", "Xã Chiềng Sung"], "Xã Chiềng Sung"),
    ("Huyện Sông Mã", ["Xã Pú Bẩu", "Xã Chiềng En", "Xã Bó Sinh"], "Xã Bó Sinh"),
    ("Huyện Sông Mã", ["Xã Mường Sai", "Xã Chiềng Khương"], "Xã Chiềng Khương"),
    ("Huyện Sông Mã", ["Xã Chiềng Cang", "Xã Mường Hung"], "Xã Mường Hung"),
    ("Huyện Sông Mã", ["Xã Mường Cai", "Xã Chiềng Khoong"], "Xã Chiềng Khoong"),
    ("Huyện Sông Mã", ["Xã Đứa Mòn", "Xã Mường Lầm"], "Xã Mường Lầm"),
    ("Huyện Sông Mã", ["Xã Chiềng Phung", "Xã Nậm Ty"], "Xã Nậm Ty"),
    ("Huyện Sông Mã", ["Thị trấn Sông Mã", "Xã Nà Nghịu"], "Xã Sông Mã"),
    ("Huyện Sông Mã", ["Xã Nậm Mằn", "Xã Huổi Một"], "Xã Huổi Một"),
    ("Huyện Sông Mã", ["Xã Yên Hưng", "Xã Chiềng Sơ"], "Xã Chiềng Sơ"),

    # Huyện Sốp Cộp - items 59-60
    ("Huyện Sốp Cộp", ["Xã Mường Và", "Xã Nậm Lạnh", "Xã Sốp Cộp"], "Xã Sốp Cộp"),
    ("Huyện Sốp Cộp", ["Xã Dồm Cang", "Xã Sam Kha", "Xã Púng Bánh"], "Xã Púng Bánh"),

    # Thành phố Sơn La - items 61-64
    ("Thành phố Sơn La", ["Phường Quyết Thắng", "Phường Quyết Tâm", "Phường Chiềng Lề", "Phường Tô Hiệu"], "Phường Tô Hiệu"),
    ("Thành phố Sơn La", ["Phường Chiềng An", "Xã Chiềng Xôm", "Xã Chiềng Đen"], "Phường Chiềng An"),
    ("Thành phố Sơn La", ["Phường Chiềng Cơi", "Xã Hua La", "Xã Chiềng Cọ"], "Phường Chiềng Cơi"),
    ("Thành phố Sơn La", ["Phường Chiềng Sinh", "Xã Chiềng Ngần"], "Phường Chiềng Sinh"),

    # Thị xã Mộc Châu (phường) - items 65-68
    ("Thị xã Mộc Châu", ["Phường Mộc Lỵ", "Phường Mường Sang", "Xã Chiềng Hắc"], "Phường Mộc Châu"),
    ("Thị xã Mộc Châu", ["Phường Đông Sang", "Phường Mộc Sơn"], "Phường Mộc Sơn"),
    ("Thị xã Mộc Châu", ["Phường Bình Minh", "Phường Vân Sơn"], "Phường Vân Sơn"),
    ("Thị xã Mộc Châu", ["Phường Cờ Đỏ", "Phường Thảo Nguyên"], "Phường Thảo Nguyên"),
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

    # Process Sơn La
    tinh_name = "Tỉnh Sơn La"

    print(f"Processing {tinh_name}...")

    # Generate entries
    dia_danh_entry = generate_dia_danh_entry(tinh_name, sonla_restructuring_data)
    chuyen_doi_entries = generate_chuyen_doi_entries(tinh_name, sonla_restructuring_data)

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

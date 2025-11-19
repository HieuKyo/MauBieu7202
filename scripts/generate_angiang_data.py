#!/usr/bin/env python3
"""
Script to generate An Giang administrative restructuring data
for dia_danh.json and chuyen_doi.json
"""

import json

# Define the restructuring data
# Format: (huyện, [list of old units], new unit name, new unit type)
restructuring_data = [
    # Huyện An Phú (items 1-5)
    ("Huyện An Phú", ["Thị trấn An Phú", "Xã Vĩnh Hội Đông", "Xã Phú Hội", "Xã Phước Hưng"], "Xã An Phú"),
    ("Huyện An Phú", ["Thị trấn Đa Phước", "Xã Vĩnh Trường", "Xã Vĩnh Hậu"], "Xã Vĩnh Hậu"),
    ("Huyện An Phú", ["Xã Quốc Thái", "Xã Nhơn Hội"], "Xã Nhơn Hội"),
    ("Huyện An Phú", ["Thị trấn Long Bình", "Xã Khánh An", "Xã Khánh Bình"], "Xã Khánh Bình"),
    ("Huyện An Phú", ["Xã Phú Hữu", "Xã Vĩnh Lộc"], "Xã Phú Hữu"),

    # Thị xã Tân Châu (items 6-8)
    ("Thị xã Tân Châu", ["Xã Tân An", "Xã Tân Thạnh", "Xã Long An"], "Xã Tân An"),
    ("Thị xã Tân Châu", ["Xã Phú Vĩnh", "Xã Lê Chánh", "Xã Châu Phong"], "Xã Châu Phong"),
    ("Thị xã Tân Châu", ["Xã Vĩnh Hòa", "Xã Phú Lộc", "Xã Vĩnh Xương"], "Xã Vĩnh Xương"),

    # Huyện Phú Tân (items 9-14)
    ("Huyện Phú Tân", ["Thị trấn Phú Mỹ", "Xã Tân Hòa", "Xã Tân Trung", "Xã Phú Hưng"], "Xã Phú Tân"),
    ("Huyện Phú Tân", ["Xã Phú Thọ", "Xã Phú Xuân", "Xã Phú An"], "Xã Phú An"),
    ("Huyện Phú Tân", ["Xã Hiệp Xương", "Xã Phú Bình", "Xã Bình Thạnh Đông"], "Xã Bình Thạnh Đông"),
    ("Huyện Phú Tân", ["Thị trấn Chợ Vàm", "Xã Phú Thạnh", "Xã Phú Thành"], "Xã Chợ Vàm"),
    ("Huyện Phú Tân", ["Xã Phú Hiệp", "Xã Hòa Lạc"], "Xã Hòa Lạc"),
    ("Huyện Phú Tân", ["Xã Long Hòa", "Xã Phú Long", "Xã Phú Lâm"], "Xã Phú Lâm"),

    # Huyện Châu Phú (items 15-19)
    ("Huyện Châu Phú", ["Thị trấn Cái Dầu", "Xã Bình Long", "Xã Bình Phú"], "Xã Châu Phú"),
    ("Huyện Châu Phú", ["Xã Khánh Hòa", "Xã Mỹ Đức"], "Xã Mỹ Đức"),
    ("Huyện Châu Phú", ["Thị trấn Vĩnh Thạnh Trung", "Xã Mỹ Phú"], "Xã Vĩnh Thạnh Trung"),
    ("Huyện Châu Phú", ["Xã Bình Thủy", "Xã Bình Chánh", "Xã Bình Mỹ"], "Xã Bình Mỹ"),
    ("Huyện Châu Phú", ["Xã Đào Hữu Cảnh", "Xã Ô Long Vĩ", "Xã Thạnh Mỹ Tây"], "Xã Thạnh Mỹ Tây"),

    # Huyện Tịnh Biên (items 20-21)
    ("Huyện Tịnh Biên", ["Xã Văn Giáo", "Xã Vĩnh Trung", "Xã An Cư"], "Xã An Cư"),
    ("Huyện Tịnh Biên", ["Xã Tân Lập", "Xã An Hảo"], "Xã Núi Cấm"),

    # Huyện Tri Tôn (items 22-26)
    ("Huyện Tri Tôn", ["Thị trấn Ba Chúc", "Xã Lạc Quới", "Xã Lê Trì"], "Xã Ba Chúc"),
    ("Huyện Tri Tôn", ["Thị trấn Tri Tôn", "Xã Núi Tô", "Xã Châu Lăng"], "Xã Tri Tôn"),
    ("Huyện Tri Tôn", ["Xã An Tức", "Xã Lương Phi", "Xã Ô Lâm"], "Xã Ô Lâm"),
    ("Huyện Tri Tôn", ["Thị trấn Cô Tô", "Xã Tà Đảnh", "Xã Tân Tuyến"], "Xã Cô Tô"),
    ("Huyện Tri Tôn", ["Xã Vĩnh Phước", "Xã Lương An Trà", "Xã Vĩnh Gia"], "Xã Vĩnh Gia"),

    # Huyện Châu Thành - An Giang (items 27-30)
    ("Huyện Châu Thành", ["Thị trấn An Châu", "Xã Hòa Bình Thạnh", "Xã Vĩnh Thành"], "Xã An Châu"),
    ("Huyện Châu Thành", ["Xã Bình Thạnh", "Xã An Hòa", "Xã Bình Hòa"], "Xã Bình Hòa"),
    ("Huyện Châu Thành", ["Xã Vĩnh Lợi", "Xã Cần Đăng"], "Xã Cần Đăng"),
    ("Huyện Châu Thành", ["Xã Vĩnh Nhuận", "Xã Vĩnh Hanh"], "Xã Vĩnh Hanh"),

    # Huyện Chợ Mới (items 31-37)
    ("Huyện Chợ Mới", ["Thị trấn Vĩnh Bình", "Xã Tân Phú", "Xã Vĩnh An"], "Xã Vĩnh An"),
    ("Huyện Chợ Mới", ["Thị trấn Chợ Mới", "Xã Kiến An", "Xã Kiến Thành"], "Xã Chợ Mới"),
    ("Huyện Chợ Mới", ["Xã Tấn Mỹ", "Xã Mỹ Hiệp", "Xã Bình Phước Xuân"], "Xã Cù Lao Giêng"),
    ("Huyện Chợ Mới", ["Thị trấn Hội An", "Xã Hòa An", "Xã Hòa Bình"], "Xã Hội An"),
    ("Huyện Chợ Mới", ["Thị trấn Mỹ Luông", "Xã Long Điền A", "Xã Long Điền B"], "Xã Long Điền"),
    ("Huyện Chợ Mới", ["Xã Mỹ Hội Đông", "Xã Long Giang", "Xã Nhơn Mỹ"], "Xã Nhơn Mỹ"),
    ("Huyện Chợ Mới", ["Xã An Thạnh Trung", "Xã Mỹ An", "Xã Long Kiến"], "Xã Long Kiến"),

    # Huyện Thoại Sơn (items 38-45)
    ("Huyện Thoại Sơn", ["Thị trấn Núi Sập", "Xã Thoại Giang", "Xã Bình Thành"], "Xã Thoại Sơn"),
    ("Huyện Thoại Sơn", ["Thị trấn Óc Eo", "Xã Vọng Thê", "Xã Vọng Đông"], "Xã Óc Eo"),
    ("Huyện Thoại Sơn", ["Xã Vĩnh Phú", "Xã Định Thành", "Xã Định Mỹ"], "Xã Định Mỹ"),
    ("Huyện Thoại Sơn", ["Thị trấn Phú Hòa", "Xã Phú Thuận", "Xã Vĩnh Chánh"], "Xã Phú Hòa"),
    ("Huyện Thoại Sơn", ["Xã Vĩnh Khánh", "Xã Vĩnh Trạch"], "Xã Vĩnh Trạch"),
    ("Huyện Thoại Sơn", ["Xã An Bình", "Xã Mỹ Phú Đông", "Xã Tây Phú"], "Xã Tây Phú"),
    ("Huyện Thoại Sơn", ["Xã Vĩnh Bình Bắc", "Xã Vĩnh Bình Nam", "Xã Bình Minh"], "Xã Vĩnh Bình"),
    ("Huyện Thoại Sơn", ["Xã Tân Thuận", "Xã Vĩnh Thuận"], "Xã Vĩnh Thuận"),

    # Huyện Vĩnh Thuận (item 46)
    ("Huyện Vĩnh Thuận", ["Thị trấn Vĩnh Thuận", "Xã Phong Đông", "Xã Vĩnh Phong"], "Xã Vĩnh Phong"),

    # Huyện U Minh Thượng (items 47-48)
    ("Huyện U Minh Thượng", ["Xã Vĩnh Hòa", "Xã Thạnh Yên A", "Xã Hòa Chánh", "Xã Thạnh Yên"], "Xã Vĩnh Hòa"),
    ("Huyện U Minh Thượng", ["Xã An Minh Bắc", "Xã Minh Thuận"], "Xã U Minh Thượng"),

    # Huyện An Minh (items 49-53)
    ("Huyện An Minh", ["Xã Đông Thạnh", "Xã Đông Hòa"], "Xã Đông Hòa"),
    ("Huyện An Minh", ["Xã Tân Thạnh", "Xã Thuận Hòa"], "Xã Tân Thạnh"),
    ("Huyện An Minh", ["Xã Vân Khánh Đông", "Xã Đông Hưng A"], "Xã Đông Hưng"),
    ("Huyện An Minh", ["Thị trấn Thứ Mười Một", "Xã Đông Hưng", "Xã Đông Hưng B"], "Xã An Minh"),
    ("Huyện An Minh", ["Xã Vân Khánh Tây", "Xã Vân Khánh"], "Xã Vân Khánh"),

    # Huyện An Biên (items 54-56)
    ("Huyện An Biên", ["Xã Tây Yên A", "Xã Nam Yên", "Xã Tây Yên"], "Xã Tây Yên"),
    ("Huyện An Biên", ["Xã Nam Thái", "Xã Nam Thái A", "Xã Đông Thái"], "Xã Đông Thái"),
    ("Huyện An Biên", ["Thị trấn Thứ Ba", "Xã Đông Yên", "Xã Hưng Yên"], "Xã An Biên"),

    # Huyện Gò Quao (items 57-60)
    ("Huyện Gò Quao", ["Xã Thới Quản", "Xã Thủy Liễu", "Xã Định Hòa"], "Xã Định Hòa"),
    ("Huyện Gò Quao", ["Thị trấn Gò Quao", "Xã Vĩnh Phước B", "Xã Định An"], "Xã Gò Quao"),
    ("Huyện Gò Quao", ["Xã Vĩnh Hòa Hưng Bắc", "Xã Vĩnh Hòa Hưng Nam"], "Xã Vĩnh Hòa Hưng"),
    ("Huyện Gò Quao", ["Xã Vĩnh Thắng", "Xã Vĩnh Phước A", "Xã Vĩnh Tuy"], "Xã Vĩnh Tuy"),

    # Huyện Giồng Riềng (items 61-66)
    ("Huyện Giồng Riềng", ["Thị trấn Giồng Riềng", "Xã Bàn Tân Định", "Xã Thạnh Hòa", "Xã Bàn Thạch", "Xã Thạnh Bình"], "Xã Giồng Riềng"),
    ("Huyện Giồng Riềng", ["Xã Thạnh Lộc", "Xã Thạnh Phước", "Xã Thạnh Hưng"], "Xã Thạnh Hưng"),
    ("Huyện Giồng Riềng", ["Xã Vĩnh Phú", "Xã Vĩnh Thạnh", "Xã Long Thạnh"], "Xã Long Thạnh"),
    ("Huyện Giồng Riềng", ["Xã Hòa An", "Xã Hòa Lợi", "Xã Hòa Hưng"], "Xã Hòa Hưng"),
    ("Huyện Giồng Riềng", ["Xã Ngọc Thuận", "Xã Ngọc Thành", "Xã Ngọc Chúc"], "Xã Ngọc Chúc"),
    ("Huyện Giồng Riềng", ["Xã Ngọc Hòa", "Xã Hòa Thuận"], "Xã Hòa Thuận"),

    # Huyện Tân Hiệp (items 67-69)
    ("Huyện Tân Hiệp", ["Xã Tân Hòa", "Xã Tân An", "Xã Tân Thành", "Xã Tân Hội"], "Xã Tân Hội"),
    ("Huyện Tân Hiệp", ["Thị trấn Tân Hiệp", "Xã Tân Hiệp B", "Xã Thạnh Đông B", "Xã Thạnh Đông"], "Xã Tân Hiệp"),
    ("Huyện Tân Hiệp", ["Xã Tân Hiệp A", "Xã Thạnh Trị", "Xã Thạnh Đông A"], "Xã Thạnh Đông"),

    # Huyện Châu Thành - Kiên Giang (items 70-72)
    ("Huyện Châu Thành KG", ["Xã Thạnh Lộc", "Xã Mong Thọ", "Xã Mong Thọ A", "Xã Mong Thọ B"], "Xã Thạnh Lộc"),
    ("Huyện Châu Thành KG", ["Thị trấn Minh Lương", "Xã Minh Hòa", "Xã Giục Tượng"], "Xã Châu Thành"),
    ("Huyện Châu Thành KG", ["Xã Bình An", "Xã Vĩnh Hòa Hiệp", "Xã Vĩnh Hòa Phú"], "Xã Bình An"),

    # Huyện Hòn Đất (items 73-76)
    ("Huyện Hòn Đất", ["Thị trấn Hòn Đất", "Xã Lình Huỳnh", "Xã Thổ Sơn", "Xã Nam Thái Sơn"], "Xã Hòn Đất"),
    ("Huyện Hòn Đất", ["Xã Sơn Bình", "Xã Mỹ Thái", "Xã Sơn Kiên"], "Xã Sơn Kiên"),
    ("Huyện Hòn Đất", ["Thị trấn Sóc Sơn", "Xã Mỹ Hiệp Sơn", "Xã Mỹ Phước", "Xã Mỹ Thuận"], "Xã Mỹ Thuận"),
    ("Huyện Hòn Đất", ["Xã Kiên Bình", "Xã Hòa Điền"], "Xã Hòa Điền"),

    # Huyện Kiên Lương (item 77)
    ("Huyện Kiên Lương", ["Thị trấn Kiên Lương", "Xã Bình An", "Xã Bình Trị"], "Xã Kiên Lương"),

    # Huyện Giang Thành (items 78-79)
    ("Huyện Giang Thành", ["Xã Tân Khánh Hòa", "Xã Phú Lợi", "Xã Phú Mỹ"], "Xã Giang Thành"),
    ("Huyện Giang Thành", ["Xã Vĩnh Phú", "Xã Vĩnh Điều"], "Xã Vĩnh Điều"),

    # Thành phố Long Xuyên (items 80-82)
    ("Thành phố Long Xuyên", ["Phường Mỹ Bình", "Phường Mỹ Long", "Phường Mỹ Xuyên", "Phường Mỹ Phước", "Phường Mỹ Quý", "Phường Mỹ Hòa"], "Phường Long Xuyên"),
    ("Thành phố Long Xuyên", ["Phường Bình Khánh", "Phường Bình Đức", "Xã Mỹ Khánh"], "Phường Bình Đức"),
    ("Thành phố Long Xuyên", ["Phường Mỹ Thạnh", "Phường Mỹ Thới"], "Phường Mỹ Thới"),

    # Thành phố Châu Đốc (items 83-84)
    ("Thành phố Châu Đốc", ["Phường Vĩnh Nguơn", "Phường Châu Phú A", "Phường Châu Phú B", "Phường Vĩnh Mỹ", "Xã Vĩnh Châu"], "Phường Châu Đốc"),
    ("Thành phố Châu Đốc", ["Phường Núi Sam", "Xã Vĩnh Tế"], "Phường Vĩnh Tế"),

    # Thị xã Tân Châu - Phường (items 85-86)
    ("Thị xã Tân Châu", ["Phường Long Thạnh", "Phường Long Sơn"], "Phường Tân Châu"),
    ("Thị xã Tân Châu", ["Phường Long Hưng", "Phường Long Châu", "Phường Long Phú"], "Phường Long Phú"),

    # Thị xã Tịnh Biên (items 87-89)
    ("Thị xã Tịnh Biên", ["Phường An Phú", "Phường Tịnh Biên", "Xã An Nông"], "Phường Tịnh Biên"),
    ("Thị xã Tịnh Biên", ["Phường Nhơn Hưng", "Phường Nhà Bàng", "Phường Thới Sơn"], "Phường Thới Sơn"),
    ("Thị xã Tịnh Biên", ["Phường Núi Voi", "Phường Chi Lăng", "Xã Tân Lợi"], "Phường Chi Lăng"),

    # Thành phố Rạch Giá (items 90-91)
    ("Thành phố Rạch Giá", ["Phường Vĩnh Thông", "Xã Phi Thông", "Xã Mỹ Lâm"], "Phường Vĩnh Thông"),
    ("Thành phố Rạch Giá", ["Phường Vĩnh Quang", "Phường Vĩnh Thanh", "Phường Vĩnh Thanh Vân", "Phường Vĩnh Lạc", "Phường An Hòa", "Phường Vĩnh Hiệp", "Phường An Bình", "Phường Rạch Sỏi", "Phường Vĩnh Lợi"], "Phường Rạch Giá"),

    # Thành phố Hà Tiên (items 92-93)
    ("Thành phố Hà Tiên", ["Phường Pháo Đài", "Phường Bình San", "Phường Mỹ Đức", "Phường Đông Hồ"], "Phường Hà Tiên"),
    ("Thành phố Hà Tiên", ["Phường Tô Châu", "Xã Thuận Yên", "Xã Dương Hòa"], "Phường Tô Châu"),

    # Đặc khu (items 94-96)
    ("Huyện Kiên Hải", [], "Đặc khu Kiên Hải"),
    ("Huyện Phú Quốc", ["Phường Dương Đông", "Phường An Thới", "Xã Dương Tơ", "Xã Hàm Ninh", "Xã Cửa Dương", "Xã Bãi Thơm", "Xã Gành Dầu", "Xã Cửa Cạn"], "Đặc khu Phú Quốc"),
    ("Huyện Phú Quốc", ["Xã Thổ Châu"], "Đặc khu Thổ Châu"),
]

def generate_dia_danh():
    """Generate the old administrative structure for dia_danh.json"""
    dia_danh = {}

    for huyen, old_units, new_unit in restructuring_data:
        if huyen not in dia_danh:
            dia_danh[huyen] = {}

        for unit in old_units:
            if unit not in dia_danh[huyen]:
                dia_danh[huyen][unit] = []

    return {"Tỉnh An Giang": dia_danh}

def generate_chuyen_doi():
    """Generate the conversion mappings for chuyen_doi.json"""
    chuyen_doi = {}

    for huyen, old_units, new_unit in restructuring_data:
        for unit in old_units:
            old_address = f"{unit}, {huyen}, Tỉnh An Giang"
            new_address = f"{new_unit}, {huyen}, Tỉnh An Giang (mới)"
            chuyen_doi[old_address] = new_address

    return chuyen_doi

if __name__ == "__main__":
    # Generate dia_danh data
    dia_danh = generate_dia_danh()
    print("=== DIA_DANH.JSON ADDITION ===")
    print(json.dumps(dia_danh, ensure_ascii=False, indent=2))

    print("\n" + "="*50 + "\n")

    # Generate chuyen_doi data
    chuyen_doi = generate_chuyen_doi()
    print("=== CHUYEN_DOI.JSON ADDITION ===")
    print(json.dumps(chuyen_doi, ensure_ascii=False, indent=2))

    # Save to files
    with open('/home/user/MauBieu7202/templates_app/static/data/angiang_dia_danh.json', 'w', encoding='utf-8') as f:
        json.dump(dia_danh, f, ensure_ascii=False, indent=2)

    with open('/home/user/MauBieu7202/templates_app/static/data/angiang_chuyen_doi.json', 'w', encoding='utf-8') as f:
        json.dump(chuyen_doi, f, ensure_ascii=False, indent=2)

    print(f"\nGenerated {len(chuyen_doi)} conversion mappings")
    print("Files saved to:")
    print("  - angiang_dia_danh.json")
    print("  - angiang_chuyen_doi.json")

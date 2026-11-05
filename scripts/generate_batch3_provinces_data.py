#!/usr/bin/env python3
"""
Script to generate administrative restructuring data for batch 3 provinces
for dia_danh.json and chuyen_doi.json

Provinces covered:
1. Điện Biên - 45 restructuring items
2. Đồng Nai (mới) - 88 restructuring items (combines Đồng Nai + Bình Phước)
3. Đồng Tháp (mới) - 102 restructuring items (combines Đồng Tháp + Tiền Giang)
"""

import json

# Base path for data files
DATA_PATH = '/home/user/MauBieu7202/templates_app/static/data'

# =============================================================================
# ĐIỆN BIÊN - 45 restructuring items
# =============================================================================

dienbien_restructuring_data = [
    # Huyện Mường Nhé - items 1-6
    ("Huyện Mường Nhé", ["Xã Nậm Vì", "Xã Chung Chải", "Xã Mường Nhé"], "Xã Mường Nhé"),
    ("Huyện Mường Nhé", ["Xã Sen Thượng", "Xã Leng Su Sìn", "Xã Sín Thầu"], "Xã Sín Thầu"),
    ("Huyện Mường Nhé", ["Xã Huổi Lếch", "Xã Mường Toong"], "Xã Mường Toong"),
    ("Huyện Mường Nhé", ["Xã Pá Mỳ", "Xã Nậm Kè"], "Xã Nậm Kè"),
    ("Huyện Mường Nhé", ["Xã Na Cô Sa", "Xã Quảng Lâm"], "Xã Quảng Lâm"),
    ("Huyện Mường Nhé", ["Xã Nà Khoa", "Xã Nậm Nhừ", "Xã Nậm Chua", "Xã Nà Hỳ"], "Xã Nà Hỳ"),

    # Huyện Mường Chà - items 7-15
    ("Huyện Mường Chà", ["Xã Chà Cang", "Xã Chà Nưa", "Xã Nậm Tin", "Xã Pa Tần"], "Xã Mường Chà"),
    ("Huyện Mường Chà", ["Xã Vàng Đán", "Xã Nà Bủng"], "Xã Nà Bủng"),
    ("Huyện Mường Chà", ["Xã Nậm Khăn", "Xã Chà Tở"], "Xã Chà Tở"),
    ("Huyện Mường Chà", ["Xã Phìn Hồ", "Xã Si Pa Phìn"], "Xã Si Pa Phìn"),
    ("Huyện Mường Chà", ["Thị trấn Mường Chà", "Xã Ma Thì Hồ", "Xã Sa Lông", "Xã Na Sang"], "Xã Na Sang"),
    ("Huyện Mường Chà", ["Xã Huổi Lèng", "Xã Mường Tùng"], "Xã Mường Tùng"),
    ("Huyện Mường Chà", ["Xã Hừa Ngài", "Xã Pa Ham"], "Xã Pa Ham"),
    ("Huyện Mường Chà", ["Xã Huổi Mí", "Xã Nậm Nèn"], "Xã Nậm Nèn"),
    ("Huyện Mường Chà", ["Xã Mường Mươn", "Xã Mường Pồn"], "Xã Mường Pồn"),

    # Huyện Tủa Chùa - items 16-20
    ("Huyện Tủa Chùa", ["Thị trấn Tủa Chùa", "Xã Mường Báng", "Xã Nà Tòng"], "Xã Tủa Chùa"),
    ("Huyện Tủa Chùa", ["Xã Tả Sìn Thàng", "Xã Lao Xả Phình", "Xã Sín Chải"], "Xã Sín Chải"),
    ("Huyện Tủa Chùa", ["Xã Trung Thu", "Xã Tả Phìn", "Xã Sính Phình"], "Xã Sính Phình"),
    ("Huyện Tủa Chùa", ["Xã Huổi Só", "Xã Tủa Thàng"], "Xã Tủa Thàng"),
    ("Huyện Tủa Chùa", ["Xã Xá Nhè", "Xã Mường Đun", "Xã Phình Sáng"], "Xã Sáng Nhè"),

    # Huyện Tuần Giáo - items 21-25
    ("Huyện Tuần Giáo", ["Thị trấn Tuần Giáo", "Xã Quài Cang", "Xã Quài Nưa"], "Xã Tuần Giáo"),
    ("Huyện Tuần Giáo", ["Xã Tỏa Tình", "Xã Tênh Phông", "Xã Quài Tở"], "Xã Quài Tở"),
    ("Huyện Tuần Giáo", ["Xã Mùn Chung", "Xã Pú Xi", "Xã Mường Mùn"], "Xã Mường Mùn"),
    ("Huyện Tuần Giáo", ["Xã Rạng Đông", "Xã Ta Ma", "Xã Pú Nhung"], "Xã Pú Nhung"),
    ("Huyện Tuần Giáo", ["Xã Nà Sáy", "Xã Mường Thín", "Xã Mường Khong", "Xã Chiềng Sinh"], "Xã Chiềng Sinh"),

    # Huyện Mường Ảng - items 26-29
    ("Huyện Mường Ảng", ["Thị trấn Mường Ảng", "Xã Ẳng Nưa", "Xã Ẳng Cang"], "Xã Mường Ảng"),
    ("Huyện Mường Ảng", ["Xã Mường Đăng", "Xã Ngối Cáy", "Xã Nà Tấu"], "Xã Nà Tấu"),
    ("Huyện Mường Ảng", ["Xã Ẳng Tở", "Xã Chiềng Đông", "Xã Búng Lao"], "Xã Búng Lao"),
    ("Huyện Mường Ảng", ["Xã Nặm Lịch", "Xã Xuân Lao", "Xã Mường Lạn"], "Xã Mường Lạn"),

    # Huyện Điện Biên - items 30-36
    ("Huyện Điện Biên", ["Xã Nà Nhạn", "Xã Pá Khoang", "Xã Mường Phăng"], "Xã Mường Phăng"),
    ("Huyện Điện Biên", ["Xã Hua Thanh", "Xã Thanh Luông", "Xã Thanh Hưng", "Xã Thanh Chăn", "Xã Thanh Nưa"], "Xã Thanh Nưa"),
    ("Huyện Điện Biên", ["Xã Noong Hẹt", "Xã Sam Mứn", "Xã Thanh An"], "Xã Thanh An"),
    ("Huyện Điện Biên", ["Xã Noong Luống", "Xã Pa Thơm", "Xã Thanh Yên"], "Xã Thanh Yên"),
    ("Huyện Điện Biên", ["Xã Pom Lót", "Xã Na Ư"], "Xã Sam Mứn"),
    ("Huyện Điện Biên", ["Xã Hẹ Muông", "Xã Na Tông", "Xã Núa Ngam"], "Xã Núa Ngam"),
    ("Huyện Điện Biên", ["Xã Mường Lói", "Xã Phu Luông", "Xã Mường Nhà"], "Xã Mường Nhà"),

    # Huyện Điện Biên Đông - items 37-42
    ("Huyện Điện Biên Đông", ["Thị trấn Điện Biên Đông", "Xã Keo Lôm", "Xã Na Son"], "Xã Na Son"),
    ("Huyện Điện Biên Đông", ["Xã Phì Nhừ", "Xã Xa Dung"], "Xã Xa Dung"),
    ("Huyện Điện Biên Đông", ["Xã Nong U", "Xã Pu Nhi"], "Xã Pu Nhi"),
    ("Huyện Điện Biên Đông", ["Xã Chiềng Sơ", "Xã Luân Giói", "Xã Mường Luân"], "Xã Mường Luân"),
    ("Huyện Điện Biên Đông", ["Xã Háng Lìa", "Xã Tìa Dình"], "Xã Tìa Dình"),
    ("Huyện Điện Biên Đông", ["Xã Pú Hồng", "Xã Phình Giàng"], "Xã Phình Giàng"),

    # Thị xã Mường Lay - item 43
    ("Thị xã Mường Lay", ["Phường Sông Đà", "Phường Na Lay", "Xã Lay Nưa", "Xã Sá Tổng"], "Phường Mường Lay"),

    # Thành phố Điện Biên Phủ - items 44-45
    ("Thành phố Điện Biên Phủ", ["Phường Him Lam", "Phường Tân Thanh", "Phường Mường Thanh", "Phường Thanh Bình", "Phường Thanh Trường", "Xã Thanh Minh"], "Phường Điện Biên Phủ"),
    ("Thành phố Điện Biên Phủ", ["Phường Noong Bua", "Phường Nam Thanh", "Xã Thanh Xương"], "Phường Mường Thanh"),
]


# =============================================================================
# ĐỒNG NAI (MỚI) - 88 restructuring items
# Combines Đồng Nai + Bình Phước
# =============================================================================

dongnai_restructuring_data = [
    # Huyện Nhơn Trạch - items 1-3
    ("Huyện Nhơn Trạch", ["Xã Phú Hữu", "Xã Phú Đông", "Xã Phước Khánh", "Xã Đại Phước"], "Xã Đại Phước"),
    ("Huyện Nhơn Trạch", ["Thị trấn Hiệp Phước", "Xã Long Tân", "Xã Phú Thạnh", "Xã Phú Hội", "Xã Phước Thiền"], "Xã Nhơn Trạch"),
    ("Huyện Nhơn Trạch", ["Xã Phước An", "Xã Vĩnh Thanh", "Xã Long Thọ"], "Xã Phước An"),

    # Huyện Long Thành - items 4-9
    ("Huyện Long Thành", ["Xã Tân Hiệp", "Xã Phước Bình", "Xã Phước Thái"], "Xã Phước Thái"),
    ("Huyện Long Thành", ["Xã Bàu Cạn", "Xã Long Phước"], "Xã Long Phước"),
    ("Huyện Long Thành", ["Thị trấn Long Thành", "Xã Lộc An", "Xã Bình Sơn", "Xã Long An"], "Xã Long Thành"),
    ("Huyện Long Thành", ["Xã Long Đức", "Xã Bình An"], "Xã Bình An"),
    ("Huyện Long Thành", ["Xã Tam An", "Xã An Phước"], "Xã An Phước"),
    ("Huyện Long Thành", ["Xã Đồi 61", "Xã An Viễn"], "Xã An Viễn"),

    # Huyện Trảng Bom - items 10-14
    ("Huyện Trảng Bom", ["Xã Bình Minh", "Xã Bắc Sơn"], "Xã Bình Minh"),
    ("Huyện Trảng Bom", ["Thị trấn Trảng Bom", "Xã Quảng Tiến", "Xã Sông Trầu", "Xã Giang Điền"], "Xã Trảng Bom"),
    ("Huyện Trảng Bom", ["Xã Thanh Bình", "Xã Cây Gáo", "Xã Sông Thao", "Xã Bàu Hàm"], "Xã Bàu Hàm"),
    ("Huyện Trảng Bom", ["Xã Đông Hòa", "Xã Tây Hòa", "Xã Trung Hòa", "Xã Hưng Thịnh"], "Xã Hưng Thịnh"),
    ("Huyện Trảng Bom", ["Thị trấn Dầu Giây", "Xã Hưng Lộc", "Xã Bàu Hàm 2", "Xã Lộ 25"], "Xã Dầu Giây"),

    # Huyện Thống Nhất - items 15-16
    ("Huyện Thống Nhất", ["Xã Quang Trung", "Xã Gia Tân 3", "Xã Gia Kiệm"], "Xã Gia Kiệm"),
    ("Huyện Thống Nhất", ["Xã Gia Tân 1", "Xã Gia Tân 2", "Xã Phú Cường", "Xã Phú Túc"], "Xã Thống Nhất"),

    # Huyện Cẩm Mỹ - items 17-20
    ("Huyện Cẩm Mỹ", ["Xã Sông Nhạn", "Xã Xuân Quế"], "Xã Xuân Quế"),
    ("Huyện Cẩm Mỹ", ["Xã Cẩm Đường", "Xã Thừa Đức", "Xã Xuân Đường"], "Xã Xuân Đường"),
    ("Huyện Cẩm Mỹ", ["Thị trấn Long Giao", "Xã Nhân Nghĩa", "Xã Xuân Mỹ", "Xã Bảo Bình"], "Xã Cẩm Mỹ"),
    ("Huyện Cẩm Mỹ", ["Xã Lâm San", "Xã Sông Ray"], "Xã Sông Ray"),

    # Huyện Xuân Lộc - items 21-27
    ("Huyện Xuân Lộc", ["Xã Xuân Tây", "Xã Xuân Đông", "Xã Xuân Tâm"], "Xã Xuân Đông"),
    ("Huyện Xuân Lộc", ["Xã Xuân Bảo", "Xã Bảo Hòa", "Xã Xuân Định"], "Xã Xuân Định"),
    ("Huyện Xuân Lộc", ["Xã Lang Minh", "Xã Xuân Phú"], "Xã Xuân Phú"),
    ("Huyện Xuân Lộc", ["Thị trấn Gia Ray", "Xã Xuân Thọ", "Xã Xuân Trường", "Xã Suối Cát", "Xã Xuân Hiệp"], "Xã Xuân Lộc"),
    ("Huyện Xuân Lộc", ["Xã Xuân Hưng", "Xã Xuân Hòa", "Xã Xuân Tâm"], "Xã Xuân Hòa"),
    ("Huyện Xuân Lộc", ["Xã Suối Cao", "Xã Xuân Thành"], "Xã Xuân Thành"),
    ("Huyện Xuân Lộc", ["Xã Suối Nho", "Xã Xuân Bắc"], "Xã Xuân Bắc"),

    # Huyện Định Quán - items 28-33
    ("Huyện Định Quán", ["Xã Túc Trưng", "Xã La Ngà"], "Xã La Ngà"),
    ("Huyện Định Quán", ["Thị trấn Định Quán", "Xã Phú Ngọc", "Xã Gia Canh", "Xã Ngọc Định"], "Xã Định Quán"),
    ("Huyện Định Quán", ["Xã Phú Tân", "Xã Phú Vinh"], "Xã Phú Vinh"),
    ("Huyện Định Quán", ["Xã Phú Điền", "Xã Phú Lợi", "Xã Phú Hòa"], "Xã Phú Hòa"),
    ("Huyện Định Quán", ["Xã Phú Thịnh", "Xã Phú Lập", "Xã Tà Lài"], "Xã Tà Lài"),
    ("Huyện Định Quán", ["Xã Phú An", "Xã Nam Cát Tiên"], "Xã Nam Cát Tiên"),

    # Huyện Tân Phú - items 34-35
    ("Huyện Tân Phú", ["Thị trấn Tân Phú", "Xã Phú Lộc", "Xã Trà Cổ", "Xã Phú Thanh", "Xã Phú Xuân"], "Xã Tân Phú"),
    ("Huyện Tân Phú", ["Xã Thanh Sơn", "Xã Phú Sơn", "Xã Phú Bình", "Xã Phú Lâm"], "Xã Phú Lâm"),

    # Huyện Vĩnh Cửu - items 36-37
    ("Huyện Vĩnh Cửu", ["Thị trấn Vĩnh An", "Xã Mã Đà", "Xã Trị An"], "Xã Trị An"),
    ("Huyện Vĩnh Cửu", ["Xã Vĩnh Tân", "Xã Tân An"], "Xã Tân An"),

    # Huyện Chơn Thành (Bình Phước) - items 38
    ("Huyện Chơn Thành", ["Xã Minh Thắng", "Xã Minh Lập", "Xã Nha Bích"], "Xã Nha Bích"),

    # Huyện Hớn Quản (Bình Phước) - items 39-42
    ("Huyện Hớn Quản", ["Xã Phước An", "Xã Tân Lợi", "Xã Quang Minh", "Xã Tân Quan"], "Xã Tân Quan"),
    ("Huyện Hớn Quản", ["Xã Tân Hưng", "Xã An Khương", "Xã Thanh An"], "Xã Tân Hưng"),
    ("Huyện Hớn Quản", ["Thị trấn Tân Khai", "Xã Tân Hiệp", "Xã Đồng Nơ"], "Xã Tân Khai"),
    ("Huyện Hớn Quản", ["Xã An Phú", "Xã Minh Tâm", "Xã Minh Đức"], "Xã Minh Đức"),

    # Huyện Lộc Ninh (Bình Phước) - items 43-48
    ("Huyện Lộc Ninh", ["Xã Lộc Thịnh", "Xã Lộc Thành"], "Xã Lộc Thành"),
    ("Huyện Lộc Ninh", ["Thị trấn Lộc Ninh", "Xã Lộc Thái", "Xã Lộc Thuận"], "Xã Lộc Ninh"),
    ("Huyện Lộc Ninh", ["Xã Lộc Khánh", "Xã Lộc Điền", "Xã Lộc Hưng"], "Xã Lộc Hưng"),
    ("Huyện Lộc Ninh", ["Xã Lộc Thiện", "Xã Lộc Tấn"], "Xã Lộc Tấn"),
    ("Huyện Lộc Ninh", ["Xã Lộc Hòa", "Xã Lộc Thạnh"], "Xã Lộc Thạnh"),
    ("Huyện Lộc Ninh", ["Xã Lộc Phú", "Xã Lộc Hiệp", "Xã Lộc Quang"], "Xã Lộc Quang"),

    # Huyện Bù Đốp (Bình Phước) - items 49-51
    ("Huyện Bù Đốp", ["Xã Tân Thành", "Xã Tân Tiến", "Xã Lộc An"], "Xã Tân Tiến"),
    ("Huyện Bù Đốp", ["Thị trấn Thanh Bình", "Xã Thanh Hòa", "Xã Thiện Hưng"], "Xã Thiện Hưng"),
    ("Huyện Bù Đốp", ["Xã Phước Thiện", "Xã Hưng Phước"], "Xã Hưng Phước"),

    # Huyện Bù Gia Mập (Bình Phước) - items 52-53
    ("Huyện Bù Gia Mập", ["Xã Phú Văn", "Xã Đức Hạnh", "Xã Phú Nghĩa"], "Xã Phú Nghĩa"),
    ("Huyện Bù Gia Mập", ["Xã Phước Minh", "Xã Bình Thắng", "Xã Đa Kia"], "Xã Đa Kia"),

    # Huyện Phú Riềng (Bình Phước) - items 54-58
    ("Huyện Phú Riềng", ["Xã Long Hưng", "Xã Long Bình", "Xã Bình Tân"], "Xã Bình Tân"),
    ("Huyện Phú Riềng", ["Xã Long Tân", "Xã Long Hà"], "Xã Long Hà"),
    ("Huyện Phú Riềng", ["Xã Bù Nho", "Xã Phú Riềng"], "Xã Phú Riềng"),
    ("Huyện Phú Riềng", ["Xã Phước Tân", "Xã Phú Trung"], "Xã Phú Trung"),
    ("Huyện Phú Riềng", ["Xã Thuận Phú", "Xã Thuận Lợi"], "Xã Thuận Lợi"),

    # Huyện Đồng Phú (Bình Phước) - items 59-61
    ("Huyện Đồng Phú", ["Xã Đồng Tiến", "Xã Tân Phước", "Xã Đồng Tâm"], "Xã Đồng Tâm"),
    ("Huyện Đồng Phú", ["Xã Tân Hưng", "Xã Tân Lợi", "Xã Tân Hòa"], "Xã Tân Lợi"),
    ("Huyện Đồng Phú", ["Thị trấn Tân Phú", "Xã Tân Tiến", "Xã Tân Lập"], "Xã Đồng Phú"),

    # Huyện Bù Đăng (Bình Phước) - items 62-67
    ("Huyện Bù Đăng", ["Xã Đăng Hà", "Xã Thống Nhất", "Xã Phước Sơn"], "Xã Phước Sơn"),
    ("Huyện Bù Đăng", ["Xã Đức Liễu", "Xã Nghĩa Bình", "Xã Nghĩa Trung"], "Xã Nghĩa Trung"),
    ("Huyện Bù Đăng", ["Thị trấn Đức Phong", "Xã Đoàn Kết", "Xã Minh Hưng"], "Xã Bù Đăng"),
    ("Huyện Bù Đăng", ["Xã Phú Sơn", "Xã Đồng Nai", "Xã Thọ Sơn"], "Xã Thọ Sơn"),
    ("Huyện Bù Đăng", ["Xã Đường 10", "Xã Đak Nhau"], "Xã Đak Nhau"),
    ("Huyện Bù Đăng", ["Xã Bình Minh", "Xã Bom Bo"], "Xã Bom Bo"),

    # Thành phố Biên Hòa - items 68-74
    ("Thành phố Biên Hòa", ["Phường Tân Hạnh", "Phường Hóa An", "Phường Bửu Hòa", "Phường Tân Vạn"], "Phường Biên Hòa"),
    ("Thành phố Biên Hòa", ["Phường Bửu Long", "Phường Quang Vinh", "Phường Trung Dũng", "Phường Thống Nhất", "Phường Hiệp Hòa", "Phường An Bình"], "Phường Trấn Biên"),
    ("Thành phố Biên Hòa", ["Phường Tân Hiệp", "Phường Tân Mai", "Phường Bình Đa", "Phường Tam Hiệp"], "Phường Tam Hiệp"),
    ("Thành phố Biên Hòa", ["Phường Hố Nai", "Phường Tân Biên", "Phường Long Bình"], "Phường Long Bình"),
    ("Thành phố Biên Hòa", ["Phường Trảng Dài", "Xã Thiện Tân"], "Phường Trảng Dài"),
    ("Thành phố Biên Hòa", ["Phường Tân Hòa", "Xã Hố Nai 3"], "Phường Hố Nai"),
    ("Thành phố Biên Hòa", ["Phường Long Bình Tân", "Phường An Hòa", "Xã Long Hưng"], "Phường Long Hưng"),

    # Thành phố Long Khánh - items 75-80
    ("Thành phố Long Khánh", ["Phường Suối Tre", "Xã Xuân Thiện", "Xã Bình Lộc"], "Phường Bình Lộc"),
    ("Thành phố Long Khánh", ["Phường Bảo Vinh", "Xã Bảo Quang"], "Phường Bảo Vinh"),
    ("Thành phố Long Khánh", ["Phường Bàu Sen", "Phường Xuân Lập"], "Phường Xuân Lập"),
    ("Thành phố Long Khánh", ["Phường Xuân An", "Phường Xuân Bình", "Phường Xuân Hòa", "Phường Phú Bình", "Xã Bàu Trâm"], "Phường Long Khánh"),
    ("Thành phố Long Khánh", ["Phường Xuân Tân", "Xã Hàng Gòn"], "Phường Hàng Gòn"),
    ("Thành phố Long Khánh", ["Phường Tân Phong", "Xã Tân Bình", "Xã Bình Lợi", "Xã Thạnh Phú"], "Phường Tân Triều"),

    # Thị xã Chơn Thành (Bình Phước) - items 81-82
    ("Thị xã Chơn Thành", ["Phường Minh Long", "Phường Minh Hưng"], "Phường Minh Hưng"),
    ("Thị xã Chơn Thành", ["Phường Hưng Long", "Phường Thành Tâm", "Phường Minh Thành"], "Phường Chơn Thành"),

    # Thị xã Bình Long (Bình Phước) - items 83-84
    ("Thị xã Bình Long", ["Phường An Lộc", "Phường Hưng Chiến", "Phường Phú Đức", "Xã Thanh Bình"], "Phường Bình Long"),
    ("Thị xã Bình Long", ["Phường Phú Thịnh", "Xã Thanh Phú", "Xã Thanh Lương"], "Phường An Lộc"),

    # Thị xã Phước Long (Bình Phước) - items 85-86
    ("Thị xã Phước Long", ["Phường Long Phước", "Phường Phước Bình", "Xã Bình Sơn", "Xã Long Giang"], "Phường Phước Bình"),
    ("Thị xã Phước Long", ["Phường Long Thủy", "Phường Thác Mơ", "Phường Sơn Giang", "Xã Phước Tín"], "Phường Phước Long"),

    # Thành phố Đồng Xoài (Bình Phước) - items 87-88
    ("Thành phố Đồng Xoài", ["Phường Tiến Thành", "Xã Tân Thành"], "Phường Đồng Xoài"),
    ("Thành phố Đồng Xoài", ["Phường Tân Phú", "Phường Tân Đồng", "Phường Tân Thiện", "Phường Tân Bình", "Phường Tân Xuân", "Xã Tiến Hưng"], "Phường Bình Phước"),
]


# =============================================================================
# ĐỒNG THÁP (MỚI) - 102 restructuring items
# Combines Đồng Tháp + Tiền Giang
# =============================================================================

dongthap_restructuring_data = [
    # Huyện Tân Hồng - items 1-4
    ("Huyện Tân Hồng", ["Thị trấn Sa Rài", "Xã Bình Phú", "Xã Tân Công Chí"], "Xã Tân Hồng"),
    ("Huyện Tân Hồng", ["Xã Thông Bình", "Xã Tân Thành A"], "Xã Tân Thành"),
    ("Huyện Tân Hồng", ["Xã Tân Thành B", "Xã Tân Hộ Cơ"], "Xã Tân Hộ Cơ"),
    ("Huyện Tân Hồng", ["Xã Tân Phước", "Xã An Phước"], "Xã An Phước"),

    # Huyện Hồng Ngự - items 5-7
    ("Huyện Hồng Ngự", ["Thị trấn Thường Thới Tiền", "Xã Thường Phước 1", "Xã Thường Phước 2"], "Xã Thường Phước"),
    ("Huyện Hồng Ngự", ["Xã Long Khánh A", "Xã Long Khánh B"], "Xã Long Khánh"),
    ("Huyện Hồng Ngự", ["Xã Long Thuận", "Xã Phú Thuận A", "Xã Phú Thuận B"], "Xã Long Phú Thuận"),

    # Huyện Tam Nông - items 8-13
    ("Huyện Tam Nông", ["Xã Phú Thành B", "Xã An Hòa"], "Xã An Hòa"),
    ("Huyện Tam Nông", ["Xã Phú Đức", "Xã Phú Hiệp"], "Xã Tam Nông"),
    ("Huyện Tam Nông", ["Xã Phú Thành A", "Xã Phú Thọ"], "Xã Phú Thọ"),
    ("Huyện Tam Nông", ["Thị trấn Tràm Chim", "Xã Tân Công Sính"], "Xã Tràm Chim"),
    ("Huyện Tam Nông", ["Xã Phú Cường", "Xã Hòa Bình", "Xã Gáo Giồng"], "Xã Phú Cường"),
    ("Huyện Tam Nông", ["Xã An Phong", "Xã Phú Ninh", "Xã An Long"], "Xã An Long"),

    # Huyện Thanh Bình - items 14-17
    ("Huyện Thanh Bình", ["Xã Tân Mỹ", "Xã Tân Phú", "Thị trấn Thanh Bình", "Xã Tân Thạnh"], "Xã Thanh Bình"),
    ("Huyện Thanh Bình", ["Xã Phú Lợi", "Xã Tân Thạnh"], "Xã Tân Thạnh"),
    ("Huyện Thanh Bình", ["Xã Bình Thành", "Xã Bình Tấn"], "Xã Bình Thành"),
    ("Huyện Thanh Bình", ["Xã Tân Bình", "Xã Tân Hòa", "Xã Tân Quới", "Xã Tân Huề", "Xã Tân Long", "Xã Phú Thuận B"], "Xã Tân Long"),

    # Huyện Tháp Mười - items 18-25
    ("Huyện Tháp Mười", ["Thị trấn Mỹ An", "Xã Mỹ An", "Xã Mỹ Hòa"], "Xã Tháp Mười"),
    ("Huyện Tháp Mười", ["Xã Phú Điền", "Xã Thanh Mỹ"], "Xã Thanh Mỹ"),
    ("Huyện Tháp Mười", ["Xã Láng Biển", "Xã Mỹ Đông", "Xã Mỹ Quí"], "Xã Mỹ Quí"),
    ("Huyện Tháp Mười", ["Xã Tân Kiều", "Xã Đốc Binh Kiều"], "Xã Đốc Binh Kiều"),
    ("Huyện Tháp Mười", ["Xã Thạnh Lợi", "Xã Trường Xuân"], "Xã Trường Xuân"),
    ("Huyện Tháp Mười", ["Xã Hưng Thạnh", "Xã Phương Thịnh"], "Xã Phương Thịnh"),
    ("Huyện Tháp Mười", ["Xã Phong Mỹ", "Xã Gáo Giồng"], "Xã Phong Mỹ"),
    ("Huyện Tháp Mười", ["Xã Phương Trà", "Xã Ba Sao"], "Xã Ba Sao"),

    # Huyện Cao Lãnh - items 26-28
    ("Huyện Cao Lãnh", ["Thị trấn Mỹ Thọ", "Xã Mỹ Hội", "Xã Mỹ Xương", "Xã Mỹ Thọ"], "Xã Mỹ Thọ"),
    ("Huyện Cao Lãnh", ["Xã Tân Hội Trung", "Xã Bình Hàng Tây", "Xã Bình Hàng Trung"], "Xã Bình Hàng Trung"),
    ("Huyện Cao Lãnh", ["Xã Mỹ Long", "Xã Bình Thạnh", "Xã Mỹ Hiệp"], "Xã Mỹ Hiệp"),

    # Huyện Lấp Vò - items 29-31
    ("Huyện Lấp Vò", ["Xã Tân Mỹ", "Xã Hội An Đông", "Xã Mỹ An Hưng A", "Xã Mỹ An Hưng B"], "Xã Mỹ An Hưng"),
    ("Huyện Lấp Vò", ["Xã Long Hưng A", "Xã Long Hưng B", "Xã Tân Khánh Trung"], "Xã Tân Khánh Trung"),
    ("Huyện Lấp Vò", ["Thị trấn Lấp Vò", "Xã Bình Thành", "Xã Vĩnh Thạnh", "Xã Bình Thạnh Trung"], "Xã Lấp Vò"),

    # Huyện Lai Vung - items 32-35
    ("Huyện Lai Vung", ["Xã Tân Thành", "Xã Tân Phước", "Xã Định An", "Xã Định Yên"], "Xã Lai Vung"),
    ("Huyện Lai Vung", ["Thị trấn Lai Vung", "Xã Long Hậu", "Xã Long Thắng", "Xã Hòa Long"], "Xã Hòa Long"),
    ("Huyện Lai Vung", ["Xã Tân Hòa", "Xã Định Hòa", "Xã Vĩnh Thới", "Xã Phong Hòa"], "Xã Phong Hòa"),
    ("Huyện Lai Vung", ["Xã Tân Phú Đông", "Xã Hòa Thành", "Xã Tân Dương"], "Xã Tân Dương"),

    # Huyện Châu Thành - items 36-38
    ("Huyện Châu Thành", ["Thị trấn Cái Tàu Hạ", "Xã An Phú Thuận", "Xã An Hiệp", "Xã An Nhơn", "Xã Phú Hựu"], "Xã Phú Hựu"),
    ("Huyện Châu Thành", ["Xã Hòa Tân", "Xã An Khánh", "Xã Tân Nhuận Đông"], "Xã Tân Nhuận Đông"),
    ("Huyện Châu Thành", ["Xã Tân Bình", "Xã Tân Phú", "Xã Phú Long", "Xã Tân Phú Trung"], "Xã Tân Phú Trung"),

    # Thị xã Cai Lậy (Tiền Giang) - items 39-42
    ("Thị xã Cai Lậy", ["Xã Tân Hội", "Xã Tân Phú", "Xã Mỹ Hạnh Đông"], "Xã Tân Phú"),
    ("Thị xã Cai Lậy", ["Xã Tân Thanh", "Xã Tân Hưng", "Xã An Thái Trung"], "Xã Thanh Hưng"),
    ("Thị xã Cai Lậy", ["Xã Hòa Hưng", "Xã Mỹ Lương", "Xã An Hữu"], "Xã An Hữu"),
    ("Thị xã Cai Lậy", ["Xã An Thái Đông", "Xã Mỹ Lợi A", "Xã Mỹ Lợi B"], "Xã Mỹ Lợi"),

    # Huyện Cái Bè (Tiền Giang) - items 43-48
    ("Huyện Cái Bè", ["Xã Thiện Trí", "Xã Mỹ Đức Đông", "Xã Mỹ Đức Tây"], "Xã Mỹ Đức Tây"),
    ("Huyện Cái Bè", ["Xã Mỹ Tân", "Xã Mỹ Trung", "Xã Thiện Trung"], "Xã Mỹ Thiện"),
    ("Huyện Cái Bè", ["Xã Hậu Mỹ Bắc A", "Xã Hậu Mỹ Bắc B", "Xã Hậu Mỹ Trinh"], "Xã Hậu Mỹ"),
    ("Huyện Cái Bè", ["Xã Mỹ Hội", "Xã An Cư", "Xã Hậu Thành", "Xã Hậu Mỹ Phú"], "Xã Hội Cư"),
    ("Huyện Cái Bè", ["Thị trấn Cái Bè", "Xã Đông Hòa Hiệp", "Xã Hòa Khánh"], "Xã Cái Bè"),
    ("Huyện Cái Bè", ["Xã Phú Nhuận", "Xã Mỹ Thành Bắc", "Xã Mỹ Thành Nam"], "Xã Mỹ Thành"),

    # Huyện Cai Lậy (Tiền Giang) - items 49-53
    ("Huyện Cai Lậy", ["Xã Phú Cường", "Xã Thạnh Lộc"], "Xã Thạnh Phú"),
    ("Huyện Cai Lậy", ["Thị trấn Bình Phú", "Xã Phú An", "Xã Cẩm Sơn"], "Xã Bình Phú"),
    ("Huyện Cai Lậy", ["Xã Tân Phong", "Xã Hội Xuân", "Xã Hiệp Đức"], "Xã Hiệp Đức"),
    ("Huyện Cai Lậy", ["Xã Mỹ Long", "Xã Long Trung", "Xã Long Tiên"], "Xã Long Tiên"),
    ("Huyện Cai Lậy", ["Xã Tam Bình", "Xã Ngũ Hiệp"], "Xã Ngũ Hiệp"),

    # Huyện Tân Phước (Tiền Giang) - items 54-57
    ("Huyện Tân Phước", ["Thị trấn Mỹ Phước", "Xã Thạnh Mỹ", "Xã Tân Hòa Đông"], "Xã Tân Phước 1"),
    ("Huyện Tân Phước", ["Xã Thạnh Tân", "Xã Thạnh Hòa", "Xã Tân Hòa Tây"], "Xã Tân Phước 2"),
    ("Huyện Tân Phước", ["Xã Phước Lập", "Xã Tân Lập 1", "Xã Tân Lập 2"], "Xã Tân Phước 3"),
    ("Huyện Tân Phước", ["Xã Hưng Thạnh", "Xã Phú Mỹ", "Xã Tân Hòa Thành"], "Xã Hưng Thạnh"),

    # Huyện Châu Thành (Tiền Giang) - items 58-67
    ("Huyện Châu Thành TG", ["Xã Tân Lý Đông", "Xã Tân Hội Đông", "Xã Tân Hương"], "Xã Tân Hương"),
    ("Huyện Châu Thành TG", ["Thị trấn Tân Hiệp", "Xã Thân Cửu Nghĩa", "Xã Long An"], "Xã Châu Thành"),
    ("Huyện Châu Thành TG", ["Xã Tam Hiệp", "Xã Thạnh Phú", "Xã Long Hưng"], "Xã Long Hưng"),
    ("Huyện Châu Thành TG", ["Xã Nhị Bình", "Xã Đông Hòa", "Xã Long Định"], "Xã Long Định"),
    ("Huyện Châu Thành TG", ["Xã Điềm Hy", "Xã Bình Trưng"], "Xã Bình Trưng"),
    ("Huyện Châu Thành TG", ["Xã Phú Phong", "Xã Bàn Long", "Xã Vĩnh Kim"], "Xã Vĩnh Kim"),
    ("Huyện Châu Thành TG", ["Xã Song Thuận", "Xã Bình Đức", "Xã Kim Sơn"], "Xã Kim Sơn"),
    ("Huyện Châu Thành TG", ["Xã Trung Hòa", "Xã Hòa Tịnh", "Xã Tân Bình Thạnh", "Xã Mỹ Tịnh An"], "Xã Mỹ Tịnh An"),
    ("Huyện Châu Thành TG", ["Xã Thanh Bình", "Xã Phú Kiết", "Xã Lương Hòa Lạc"], "Xã Lương Hòa Lạc"),
    ("Huyện Châu Thành TG", ["Xã Đăng Hưng Phước", "Xã Quơn Long", "Xã Tân Thuận Bình"], "Xã Tân Thuận Bình"),

    # Huyện Chợ Gạo (Tiền Giang) - items 68-72
    ("Huyện Chợ Gạo", ["Thị trấn Chợ Gạo", "Xã Long Bình Điền", "Xã Song Bình"], "Xã Chợ Gạo"),
    ("Huyện Chợ Gạo", ["Xã Bình Phan", "Xã Bình Phục Nhứt", "Xã An Thạnh Thủy"], "Xã An Thạnh Thủy"),
    ("Huyện Chợ Gạo", ["Xã Xuân Đông", "Xã Hòa Định", "Xã Bình Ninh"], "Xã Bình Ninh"),
    ("Huyện Chợ Gạo", ["Thị trấn Vĩnh Bình", "Xã Thạnh Nhựt", "Xã Thạnh Trị"], "Xã Vĩnh Bình"),
    ("Huyện Chợ Gạo", ["Xã Bình Nhì", "Xã Đồng Thạnh", "Xã Đồng Sơn"], "Xã Đồng Sơn"),

    # Huyện Gò Công Tây (Tiền Giang) - items 73-75
    ("Huyện Gò Công Tây", ["Xã Bình Phú", "Xã Thành Công", "Xã Yên Luông"], "Xã Phú Thành"),
    ("Huyện Gò Công Tây", ["Xã Bình Tân", "Xã Long Bình"], "Xã Long Bình"),
    ("Huyện Gò Công Tây", ["Xã Long Vĩnh", "Xã Vĩnh Hựu"], "Xã Vĩnh Hựu"),

    # Huyện Gò Công Đông (Tiền Giang) - items 76-80
    ("Huyện Gò Công Đông", ["Xã Tân Thành", "Xã Tăng Hòa"], "Xã Gò Công Đông"),
    ("Huyện Gò Công Đông", ["Xã Bình Ân", "Xã Tân Điền"], "Xã Tân Điền"),
    ("Huyện Gò Công Đông", ["Thị trấn Tân Hòa", "Xã Phước Trung", "Xã Bình Nghị"], "Xã Tân Hòa"),
    ("Huyện Gò Công Đông", ["Xã Tân Phước", "Xã Tân Tây", "Xã Tân Đông"], "Xã Tân Đông"),
    ("Huyện Gò Công Đông", ["Thị trấn Vàm Láng", "Xã Kiểng Phước", "Xã Gia Thuận"], "Xã Gia Thuận"),

    # Huyện Tân Phú Đông (Tiền Giang) - items 81-82
    ("Huyện Tân Phú Đông", ["Xã Tân Phú", "Xã Tân Thạnh", "Xã Tân Thới"], "Xã Tân Thới"),
    ("Huyện Tân Phú Đông", ["Xã Phú Thạnh", "Xã Phú Đông", "Xã Phú Tân"], "Xã Tân Phú Đông"),

    # Thành phố Mỹ Tho (Tiền Giang) - items 83-87
    ("Thành phố Mỹ Tho", ["Phường 1", "Phường 2", "Phường Tân Long"], "Phường Mỹ Tho"),
    ("Thành phố Mỹ Tho", ["Phường 4", "Phường 5", "Xã Đạo Thạnh"], "Phường Đạo Thạnh"),
    ("Thành phố Mỹ Tho", ["Phường 9", "Xã Tân Mỹ Chánh", "Xã Mỹ Phong"], "Phường Mỹ Phong"),
    ("Thành phố Mỹ Tho", ["Phường 6", "Xã Thới Sơn"], "Phường Thới Sơn"),
    ("Thành phố Mỹ Tho", ["Phường 10", "Xã Phước Thạnh", "Xã Trung An"], "Phường Trung An"),

    # Thành phố Gò Công (Tiền Giang) - items 88-91
    ("Thành phố Gò Công", ["Phường 1", "Phường 5", "Phường Long Hòa"], "Phường Gò Công"),
    ("Thành phố Gò Công", ["Phường 2", "Phường Long Thuận"], "Phường Long Thuận"),
    ("Thành phố Gò Công", ["Phường Long Chánh", "Xã Bình Xuân"], "Phường Bình Xuân"),
    ("Thành phố Gò Công", ["Phường Long Hưng", "Xã Tân Trung", "Xã Bình Đông"], "Phường Sơn Qui"),

    # Thành phố Hồng Ngự - items 92-94
    ("Thành phố Hồng Ngự", ["Phường An Lộc", "Phường An Bình A", "Phường An Bình B"], "Phường An Bình"),
    ("Thành phố Hồng Ngự", ["Phường An Thạnh", "Xã Bình Thạnh", "Xã Tân Hội"], "Phường Hồng Ngự"),
    ("Thành phố Hồng Ngự", ["Phường An Lạc", "Xã Thường Thới Hậu A", "Xã Thường Lạc"], "Phường Thường Lạc"),

    # Thành phố Cao Lãnh - items 95-97
    ("Thành phố Cao Lãnh", ["Phường 1", "Phường 3", "Phường 4", "Phường 6", "Phường Hòa Thuận", "Xã Hòa An", "Xã Tịnh Thới", "Xã Tân Thuận Tây", "Xã Tân Thuận Đông"], "Phường Cao Lãnh"),
    ("Thành phố Cao Lãnh", ["Phường Mỹ Ngãi", "Xã Mỹ Tân", "Xã Tân Nghĩa"], "Phường Mỹ Ngãi"),
    ("Thành phố Cao Lãnh", ["Phường Mỹ Phú", "Xã Nhị Mỹ", "Xã An Bình", "Xã Mỹ Trà"], "Phường Mỹ Trà"),

    # Thành phố Sa Đéc - item 98
    ("Thành phố Sa Đéc", ["Phường 1", "Phường 2", "Phường 3", "Phường 4", "Phường An Hòa", "Phường Tân Quy Đông", "Xã Tân Khánh Đông", "Xã Tân Quy Tây"], "Phường Sa Đéc"),

    # Thị xã Cai Lậy (Tiền Giang) - items 99-102
    ("Thị xã Cai Lậy TG", ["Phường 1", "Phường 3", "Xã Mỹ Hạnh Trung", "Xã Mỹ Phước Tây"], "Phường Mỹ Phước Tây"),
    ("Thị xã Cai Lậy TG", ["Phường 2", "Xã Tân Bình", "Xã Thanh Hòa"], "Phường Thanh Hòa"),
    ("Thị xã Cai Lậy TG", ["Phường 4", "Phường 5", "Xã Long Khánh"], "Phường Cai Lậy"),
    ("Thị xã Cai Lậy TG", ["Phường Nhị Mỹ", "Xã Phú Quý", "Xã Nhị Quý"], "Phường Nhị Quý"),
]


def generate_dia_danh(restructuring_data, province_name):
    """Generate the old administrative structure for dia_danh.json"""
    dia_danh = {}

    for huyen, old_units, new_unit in restructuring_data:
        if huyen not in dia_danh:
            dia_danh[huyen] = {}

        for unit in old_units:
            if unit not in dia_danh[huyen]:
                dia_danh[huyen][unit] = []

    return {province_name: dia_danh}


def generate_chuyen_doi(restructuring_data, old_province_name, new_province_name):
    """Generate the conversion mappings for chuyen_doi.json"""
    chuyen_doi = {}

    for huyen, old_units, new_unit in restructuring_data:
        for unit in old_units:
            old_address = f"{unit}, {huyen}, {old_province_name}"
            new_address = f"{new_unit}, {huyen}, {new_province_name}"
            chuyen_doi[old_address] = new_address

    return chuyen_doi


def process_province(restructuring_data, province_name, new_province_suffix=""):
    """Process a province and generate both dia_danh and chuyen_doi data"""
    old_name = province_name
    new_name = f"{province_name} (mới)" if new_province_suffix else province_name

    dia_danh = generate_dia_danh(restructuring_data, old_name)
    chuyen_doi = generate_chuyen_doi(restructuring_data, old_name, new_name)

    return dia_danh, chuyen_doi


def main():
    all_dia_danh = {}
    all_chuyen_doi = {}

    # Process Điện Biên
    print("Processing Tỉnh Điện Biên...")
    dia_danh, chuyen_doi = process_province(dienbien_restructuring_data, "Tỉnh Điện Biên", "")
    all_dia_danh.update(dia_danh)
    all_chuyen_doi.update(chuyen_doi)
    print(f"  - {len(chuyen_doi)} conversion mappings")

    # Process Đồng Nai
    print("Processing Tỉnh Đồng Nai...")
    dia_danh, chuyen_doi = process_province(dongnai_restructuring_data, "Tỉnh Đồng Nai", "(mới)")
    all_dia_danh.update(dia_danh)
    all_chuyen_doi.update(chuyen_doi)
    print(f"  - {len(chuyen_doi)} conversion mappings")

    # Process Đồng Tháp
    print("Processing Tỉnh Đồng Tháp...")
    dia_danh, chuyen_doi = process_province(dongthap_restructuring_data, "Tỉnh Đồng Tháp", "(mới)")
    all_dia_danh.update(dia_danh)
    all_chuyen_doi.update(chuyen_doi)
    print(f"  - {len(chuyen_doi)} conversion mappings")

    # Save intermediate files
    for province_key in all_dia_danh:
        safe_name = province_key.replace(" ", "_").replace("/", "_").lower()

        with open(f'{DATA_PATH}/{safe_name}_dia_danh.json', 'w', encoding='utf-8') as f:
            json.dump({province_key: all_dia_danh[province_key]}, f, ensure_ascii=False, indent=2)

    # Save combined chuyen_doi
    with open(f'{DATA_PATH}/batch3_chuyen_doi.json', 'w', encoding='utf-8') as f:
        json.dump(all_chuyen_doi, f, ensure_ascii=False, indent=2)

    print(f"\nTotal: {len(all_chuyen_doi)} conversion mappings")
    print(f"Provinces: {len(all_dia_danh)}")

    # Load and update main files
    print("\nMerging with main files...")

    with open(f'{DATA_PATH}/dia_danh.json', 'r', encoding='utf-8') as f:
        main_dia_danh = json.load(f)

    with open(f'{DATA_PATH}/chuyen_doi.json', 'r', encoding='utf-8') as f:
        main_chuyen_doi = json.load(f)

    # Merge
    for province, data in all_dia_danh.items():
        main_dia_danh[province] = data

    main_chuyen_doi.update(all_chuyen_doi)

    # Save updated main files
    with open(f'{DATA_PATH}/dia_danh.json', 'w', encoding='utf-8') as f:
        json.dump(main_dia_danh, f, ensure_ascii=False, indent=2)

    with open(f'{DATA_PATH}/chuyen_doi.json', 'w', encoding='utf-8') as f:
        json.dump(main_chuyen_doi, f, ensure_ascii=False, indent=2)

    print("\nFinal totals:")
    print(f"  - dia_danh provinces: {len(main_dia_danh)}")
    print(f"  - chuyen_doi mappings: {len(main_chuyen_doi)}")


if __name__ == "__main__":
    main()

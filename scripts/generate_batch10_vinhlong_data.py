#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate restructuring data for Vĩnh Long (mới) - Batch 10
Mega-province combining: Vĩnh Long + Bến Tre + Trà Vinh
120 items, 124 units (105 xã, 19 phường)
"""

import json
import os

# Get the project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
data_dir = os.path.join(project_root, 'templates_app', 'static', 'data')

# Vĩnh Long (mới) restructuring data
# Format: (district, [old units], new unit name)
vinhlong_restructuring_data = [
    # Huyện Mang Thít (Vĩnh Long)
    ("Huyện Mang Thít", ["Xã An Phước", "Xã Chánh An", "Thị trấn Cái Nhum"], "Xã Cái Nhum"),
    ("Huyện Mang Thít", ["Xã Tân An Hội", "Xã Tân Long", "Xã Tân Long Hội"], "Xã Tân Long Hội"),
    ("Huyện Mang Thít", ["Xã Mỹ An", "Xã Mỹ Phước", "Xã Nhơn Phú"], "Xã Nhơn Phú"),
    ("Huyện Mang Thít", ["Xã Long Mỹ", "Xã Hòa Tịnh", "Xã Bình Phước"], "Xã Bình Phước"),

    # Huyện Long Hồ (Vĩnh Long)
    ("Huyện Long Hồ", ["Xã Hòa Ninh", "Xã Bình Hòa Phước", "Xã Đồng Phú", "Xã An Bình"], "Xã An Bình"),
    ("Huyện Long Hồ", ["Thị trấn Long Hồ", "Xã Long An", "Xã Long Phước"], "Xã Long Hồ"),
    ("Huyện Long Hồ", ["Xã Lộc Hòa", "Xã Hòa Phú", "Xã Thạnh Quới", "Xã Phú Quới"], "Xã Phú Quới"),
    ("Huyện Long Hồ", ["Xã Thanh Bình", "Xã Quới Thiện"], "Xã Quới Thiện"),

    # Huyện Vũng Liêm (Vĩnh Long)
    ("Huyện Vũng Liêm", ["Thị trấn Vũng Liêm", "Xã Trung Hiếu", "Xã Trung Thành"], "Xã Trung Thành"),
    ("Huyện Vũng Liêm", ["Xã Trung Thành Đông", "Xã Trung Nghĩa", "Xã Trung Ngãi"], "Xã Trung Ngãi"),
    ("Huyện Vũng Liêm", ["Xã Trung Thành Tây", "Xã Tân Quới Trung", "Xã Quới An"], "Xã Quới An"),
    ("Huyện Vũng Liêm", ["Xã Tân An Luông", "Xã Trung Chánh", "Xã Trung Hiệp"], "Xã Trung Hiệp"),
    ("Huyện Vũng Liêm", ["Xã Hiếu Thuận", "Xã Trung An", "Xã Hiếu Phụng"], "Xã Hiếu Phụng"),
    ("Huyện Vũng Liêm", ["Xã Hiếu Nhơn", "Xã Hiếu Nghĩa", "Xã Hiếu Thành"], "Xã Hiếu Thành"),

    # Huyện Trà Ôn (Vĩnh Long)
    ("Huyện Trà Ôn", ["Xã Phú Thành", "Xã Lục Sĩ Thành"], "Xã Lục Sĩ Thành"),
    ("Huyện Trà Ôn", ["Xã Tích Thiện", "Thị trấn Trà Ôn"], "Xã Trà Ôn"),
    ("Huyện Trà Ôn", ["Xã Nhơn Bình", "Xã Trà Côn", "Xã Tân Mỹ", "Thị trấn Tam Bình"], "Xã Trà Côn"),
    ("Huyện Trà Ôn", ["Xã Hựu Thành", "Xã Thuận Thới", "Xã Vĩnh Xuân"], "Xã Vĩnh Xuân"),

    # Huyện Tam Bình (Vĩnh Long)
    ("Huyện Tam Bình", ["Xã Xuân Hiệp", "Xã Thới Hòa", "Xã Hòa Bình"], "Xã Hòa Bình"),
    ("Huyện Tam Bình", ["Xã Hòa Thạnh", "Xã Hòa Lộc", "Xã Hòa Hiệp"], "Xã Hòa Hiệp"),
    ("Huyện Tam Bình", ["Xã Mỹ Thạnh Trung", "Thị trấn Tam Bình"], "Xã Tam Bình"),
    ("Huyện Tam Bình", ["Xã Loan Mỹ", "Xã Bình Ninh", "Xã Ngãi Tứ", "Thị trấn Trà Ôn"], "Xã Ngãi Tứ"),
    ("Huyện Tam Bình", ["Xã Tân Phú", "Xã Long Phú", "Xã Phú Thịnh", "Xã Song Phú"], "Xã Song Phú"),
    ("Huyện Tam Bình", ["Xã Mỹ Lộc", "Xã Tân Lộc", "Xã Hậu Lộc", "Xã Phú Lộc"], "Xã Cái Ngang"),

    # Huyện Bình Tân (Vĩnh Long)
    ("Huyện Bình Tân", ["Xã Tân Bình", "Xã Thành Lợi", "Thị trấn Tân Quới"], "Xã Tân Quới"),
    ("Huyện Bình Tân", ["Xã Tân Thành", "Xã Tân An Thạnh", "Xã Tân Lược"], "Xã Tân Lược"),
    ("Huyện Bình Tân", ["Xã Thành Trung", "Xã Nguyễn Văn Thảnh", "Xã Mỹ Thuận"], "Xã Mỹ Thuận"),

    # Huyện Càng Long (Trà Vinh)
    ("Huyện Càng Long", ["Xã Hiệp Thạnh", "Xã Long Hữu"], "Xã Long Hữu"),
    ("Huyện Càng Long", ["Thị trấn Càng Long", "Xã Mỹ Cẩm", "Xã Nhị Long Phú"], "Xã Càng Long"),
    ("Huyện Càng Long", ["Xã Tân Bình", "Xã An Trường A", "Xã An Trường"], "Xã An Trường"),
    ("Huyện Càng Long", ["Xã Huyền Hội", "Xã Tân An"], "Xã Tân An"),
    ("Huyện Càng Long", ["Xã Đại Phước", "Xã Đức Mỹ", "Xã Nhị Long"], "Xã Nhị Long"),
    ("Huyện Càng Long", ["Xã Bình Phú", "Xã Đại Phúc", "Xã Phương Thạnh"], "Xã Bình Phú"),

    # Huyện Châu Thành - Trà Vinh
    ("Huyện Châu Thành", ["Thị trấn Châu Thành", "Xã Mỹ Chánh", "Xã Thanh Mỹ", "Xã Đa Lộc"], "Xã Châu Thành"),
    ("Huyện Châu Thành", ["Xã Lương Hòa", "Xã Lương Hòa A", "Xã Song Lộc"], "Xã Song Lộc"),
    ("Huyện Châu Thành", ["Xã Hòa Lợi", "Xã Phước Hảo", "Xã Hưng Mỹ"], "Xã Hưng Mỹ"),

    # Huyện Cầu Kè (Trà Vinh)
    ("Huyện Cầu Kè", ["Thị trấn Cầu Kè", "Xã Hòa Ân", "Xã Châu Điền"], "Xã Cầu Kè"),
    ("Huyện Cầu Kè", ["Xã Ninh Thới", "Xã Phong Phú", "Xã Phong Thạnh"], "Xã Phong Thạnh"),
    ("Huyện Cầu Kè", ["Xã Hòa Tân", "Xã An Phú Tân"], "Xã An Phú Tân"),
    ("Huyện Cầu Kè", ["Xã Thông Hòa", "Xã Thạnh Phú", "Xã Tam Ngãi"], "Xã Tam Ngãi"),

    # Huyện Tiểu Cần (Trà Vinh)
    ("Huyện Tiểu Cần", ["Thị trấn Tiểu Cần", "Xã Phú Cần", "Xã Hiếu Trung"], "Xã Tiểu Cần"),
    ("Huyện Tiểu Cần", ["Xã Long Thới", "Xã Tân Hòa", "Thị trấn Cầu Quan"], "Xã Tân Hoà"),
    ("Huyện Tiểu Cần", ["Xã Ngãi Hùng", "Xã Tân Hùng", "Xã Hùng Hòa"], "Xã Hùng Hoà"),
    ("Huyện Tiểu Cần", ["Xã Hiếu Tử", "Xã Tập Ngãi"], "Xã Tập Ngãi"),

    # Huyện Cầu Ngang (Trà Vinh)
    ("Huyện Cầu Ngang", ["Xã Mỹ Hòa", "Xã Thuận Hòa", "Thị trấn Cầu Ngang"], "Xã Cầu Ngang"),
    ("Huyện Cầu Ngang", ["Thị trấn Mỹ Long", "Xã Mỹ Long Bắc", "Xã Mỹ Long Nam"], "Xã Mỹ Long"),
    ("Huyện Cầu Ngang", ["Xã Kim Hòa", "Xã Vinh Kim"], "Xã Vinh Kim"),
    ("Huyện Cầu Ngang", ["Xã Hiệp Hòa", "Xã Trường Thọ", "Xã Nhị Trường"], "Xã Nhị Trường"),
    ("Huyện Cầu Ngang", ["Xã Long Sơn", "Xã Hiệp Mỹ Đông", "Xã Hiệp Mỹ Tây"], "Xã Hiệp Mỹ"),

    # Huyện Trà Cú (Trà Vinh)
    ("Huyện Trà Cú", ["Thị trấn Trà Cú", "Xã Ngãi Xuyên", "Xã Thanh Sơn"], "Xã Trà Cú"),
    ("Huyện Trà Cú", ["Thị trấn Định An", "Xã Định An", "Xã Đại An"], "Xã Đại An"),
    ("Huyện Trà Cú", ["Xã An Quảng Hữu", "Xã Lưu Nghiệp Anh"], "Xã Lưu Nghiệp Anh"),
    ("Huyện Trà Cú", ["Xã Hàm Tân", "Xã Kim Sơn", "Xã Hàm Giang"], "Xã Hàm Giang"),
    ("Huyện Trà Cú", ["Xã Ngọc Biên", "Xã Tân Hiệp", "Xã Long Hiệp"], "Xã Long Hiệp"),
    ("Huyện Trà Cú", ["Xã Tân Sơn", "Xã Phước Hưng", "Xã Tập Sơn"], "Xã Tập Sơn"),

    # Huyện Duyên Hải (Trà Vinh)
    ("Huyện Duyên Hải", ["Thị trấn Long Thành", "Xã Long Khánh"], "Xã Long Thành"),
    ("Huyện Duyên Hải", ["Xã Đôn Xuân", "Xã Đôn Châu"], "Xã Đôn Châu"),
    ("Huyện Duyên Hải", ["Xã Thạnh Hòa Sơn", "Xã Ngũ Lạc"], "Xã Ngũ Lạc"),

    # Huyện Châu Thành - Bến Tre
    ("Huyện Châu Thành", ["Thị trấn Châu Thành", "Xã Tân Thạch", "Xã Tường Đa", "Xã Phú Túc"], "Xã Phú Túc"),
    ("Huyện Châu Thành", ["Xã An Phước", "Xã Quới Sơn", "Xã Giao Long"], "Xã Giao Long"),
    ("Huyện Châu Thành", ["Thị trấn Tiên Thủy", "Xã Thành Triệu", "Xã Quới Thành"], "Xã Tiên Thủy"),
    ("Huyện Châu Thành", ["Xã Tân Phú", "Xã Tiên Long", "Xã Phú Đức"], "Xã Tân Phú"),
    ("Huyện Châu Thành", ["Xã Sơn Định", "Xã Vĩnh Bình", "Xã Phú Phụng"], "Xã Phú Phụng"),

    # Huyện Chợ Lách (Bến Tre)
    ("Huyện Chợ Lách", ["Xã Long Thới", "Xã Hòa Nghĩa", "Thị trấn Chợ Lách"], "Xã Chợ Lách"),
    ("Huyện Chợ Lách", ["Xã Phú Sơn", "Xã Tân Thiềng", "Xã Vĩnh Thành"], "Xã Vĩnh Thành"),
    ("Huyện Chợ Lách", ["Xã Vĩnh Hòa", "Xã Hưng Khánh Trung A", "Xã Hưng Khánh Trung B"], "Xã Hưng Khánh Trung"),

    # Huyện Mỏ Cày Bắc (Bến Tre)
    ("Huyện Mỏ Cày Bắc", ["Thị trấn Phước Mỹ Trung", "Xã Phú Mỹ", "Xã Thạnh Ngãi", "Xã Tân Phú Tây"], "Xã Phước Mỹ Trung"),
    ("Huyện Mỏ Cày Bắc", ["Xã Tân Bình", "Xã Thành An", "Xã Hòa Lộc", "Xã Tân Thành Bình"], "Xã Tân Thành Bình"),
    ("Huyện Mỏ Cày Bắc", ["Xã Khánh Thạnh Tân", "Xã Tân Thanh Tây", "Xã Nhuận Phú Tân"], "Xã Nhuận Phú Tân"),

    # Huyện Mỏ Cày Nam (Bến Tre)
    ("Huyện Mỏ Cày Nam", ["Xã Định Thủy", "Xã Phước Hiệp", "Xã Bình Khánh"], "Xã Đồng Khởi"),
    ("Huyện Mỏ Cày Nam", ["Thị trấn Mỏ Cày", "Xã An Thạnh", "Xã Tân Hội", "Xã Đa Phước Hội"], "Xã Mỏ Cày"),
    ("Huyện Mỏ Cày Nam", ["Xã An Thới", "Xã Thành Thới A", "Xã Thành Thới B"], "Xã Thành Thới"),
    ("Huyện Mỏ Cày Nam", ["Xã Tân Trung", "Xã Minh Đức", "Xã An Định"], "Xã An Định"),
    ("Huyện Mỏ Cày Nam", ["Xã Ngãi Đăng", "Xã Cẩm Sơn", "Xã Hương Mỹ"], "Xã Hương Mỹ"),

    # Huyện Thạnh Phú (Bến Tre)
    ("Huyện Thạnh Phú", ["Xã Phú Khánh", "Xã Tân Phong", "Xã Thới Thạnh", "Xã Đại Điền"], "Xã Đại Điền"),
    ("Huyện Thạnh Phú", ["Xã Hòa Lợi", "Xã Mỹ Hưng", "Xã Quới Điền"], "Xã Quới Điền"),
    ("Huyện Thạnh Phú", ["Thị trấn Thạnh Phú", "Xã An Thạnh", "Xã Bình Thạnh", "Xã Mỹ An"], "Xã Thạnh Phú"),
    ("Huyện Thạnh Phú", ["Xã An Thuận", "Xã An Nhơn", "Xã An Qui"], "Xã An Qui"),
    ("Huyện Thạnh Phú", ["Xã An Điền", "Xã Thạnh Hải"], "Xã Thạnh Hải"),
    ("Huyện Thạnh Phú", ["Xã Giao Thạnh", "Xã Thạnh Phong"], "Xã Thạnh Phong"),

    # Huyện Ba Tri (Bến Tre)
    ("Huyện Ba Tri", ["Thị trấn Tiệm Tôm", "Xã An Hòa Tây", "Xã Tân Thủy"], "Xã Tân Thủy"),
    ("Huyện Ba Tri", ["Xã Bảo Thuận", "Xã Bảo Thạnh"], "Xã Bảo Thạnh"),
    ("Huyện Ba Tri", ["Thị trấn Ba Tri", "Xã Vĩnh Hòa", "Xã An Đức", "Xã Vĩnh An", "Xã An Bình Tây"], "Xã Ba Tri"),
    ("Huyện Ba Tri", ["Xã Phú Lễ", "Xã Phước Ngãi", "Xã Tân Xuân"], "Xã Tân Xuân"),
    ("Huyện Ba Tri", ["Xã Mỹ Hòa", "Xã Mỹ Chánh", "Xã Mỹ Nhơn"], "Xã Mỹ Chánh Hòa"),
    ("Huyện Ba Tri", ["Xã Mỹ Thạnh", "Xã An Phú Trung", "Xã An Ngãi Trung"], "Xã An Ngãi Trung"),
    ("Huyện Ba Tri", ["Xã Tân Hưng", "Xã An Ngãi Tây", "Xã An Hiệp"], "Xã An Hiệp"),

    # Huyện Giồng Trôm (Bến Tre)
    ("Huyện Giồng Trôm", ["Xã Tân Thanh", "Xã Hưng Lễ", "Xã Hưng Nhượng"], "Xã Hưng Nhượng"),
    ("Huyện Giồng Trôm", ["Thị trấn Giồng Trôm", "Xã Bình Hòa", "Xã Bình Thành"], "Xã Giồng Trôm"),
    ("Huyện Giồng Trôm", ["Xã Tân Lợi Thạnh", "Xã Thạnh Phú Đông", "Xã Tân Hào"], "Xã Tân Hào"),
    ("Huyện Giồng Trôm", ["Xã Long Mỹ", "Xã Hưng Phong", "Xã Phước Long"], "Xã Phước Long"),
    ("Huyện Giồng Trôm", ["Xã Mỹ Thạnh", "Xã Thuận Điền", "Xã Lương Phú"], "Xã Lương Phú"),
    ("Huyện Giồng Trôm", ["Xã Châu Bình", "Xã Lương Quới", "Xã Châu Hòa"], "Xã Châu Hòa"),
    ("Huyện Giồng Trôm", ["Xã Lương Hòa", "Xã Phong Nẫm"], "Xã Lương Hòa"),

    # Huyện Bình Đại (Bến Tre)
    ("Huyện Bình Đại", ["Xã Thừa Đức", "Xã Thới Thuận"], "Xã Thới Thuận"),
    ("Huyện Bình Đại", ["Xã Đại Hòa Lộc", "Xã Thạnh Phước"], "Xã Thạnh Phước"),
    ("Huyện Bình Đại", ["Thị trấn Bình Đại", "Xã Bình Thới", "Xã Bình Thắng"], "Xã Bình Đại"),
    ("Huyện Bình Đại", ["Xã Định Trung", "Xã Phú Long", "Xã Thạnh Trị"], "Xã Thạnh Trị"),
    ("Huyện Bình Đại", ["Xã Vang Quới Đông", "Xã Vang Quới Tây", "Xã Lộc Thuận"], "Xã Lộc Thuận"),
    ("Huyện Bình Đại", ["Xã Long Hòa", "Xã Thới Lai", "Xã Châu Hưng"], "Xã Châu Hưng"),
    ("Huyện Bình Đại", ["Xã Long Định", "Xã Tam Hiệp", "Xã Phú Thuận"], "Xã Phú Thuận"),

    # Thành phố Vĩnh Long (Vĩnh Long)
    ("Thành phố Vĩnh Long", ["Phường 5", "Xã Thanh Đức"], "Phường Thanh Đức"),
    ("Thành phố Vĩnh Long", ["Phường 1", "Phường 9", "Phường Trường An"], "Phường Long Châu"),
    ("Thành phố Vĩnh Long", ["Phường 3", "Phường 4", "Xã Phước Hậu"], "Phường Phước Hậu"),
    ("Thành phố Vĩnh Long", ["Phường 8", "Xã Tân Hạnh"], "Phường Tân Hạnh"),
    ("Thành phố Vĩnh Long", ["Phường Tân Hòa", "Phường Tân Hội", "Phường Tân Ngãi"], "Phường Tân Ngãi"),

    # Thị xã Bình Minh (Vĩnh Long)
    ("Thị xã Bình Minh", ["Xã Thuận An", "Phường Thành Phước", "Phường Cái Vồn"], "Phường Bình Minh"),
    ("Thị xã Bình Minh", ["Xã Mỹ Hòa", "Xã Ngãi Tứ", "Phường Thành Phước", "Phường Cái Vồn"], "Phường Cái Vồn"),
    ("Thị xã Bình Minh", ["Phường Đông Thuận", "Xã Đông Bình", "Xã Đông Thạnh", "Xã Đông Thành"], "Phường Đông Thành"),

    # Thành phố Trà Vinh (Trà Vinh)
    ("Thành phố Trà Vinh", ["Phường 1", "Phường 3", "Phường 9"], "Phường Trà Vinh"),
    ("Thành phố Trà Vinh", ["Phường 4", "Xã Long Đức"], "Phường Long Đức"),
    ("Thành phố Trà Vinh", ["Phường 7", "Phường 8", "Xã Nguyệt Hóa"], "Phường Nguyệt Hoá"),
    ("Thành phố Trà Vinh", ["Phường 5", "Xã Hòa Thuận"], "Phường Hoà Thuận"),

    # Thị xã Duyên Hải (Trà Vinh)
    ("Thị xã Duyên Hải", ["Phường 1", "Xã Long Toàn", "Xã Dân Thành"], "Phường Duyên Hải"),
    ("Thị xã Duyên Hải", ["Phường 2", "Xã Trường Long Hòa"], "Phường Trường Long Hoà"),

    # Thành phố Bến Tre (Bến Tre)
    ("Thành phố Bến Tre", ["Phường An Hội", "Xã Mỹ Thạnh An", "Xã Phú Nhuận", "Xã Sơn Phú"], "Phường An Hội"),
    ("Thành phố Bến Tre", ["Phường 8", "Phường Phú Khương", "Xã Phú Hưng", "Xã Nhơn Thạnh"], "Phường Phú Khương"),
    ("Thành phố Bến Tre", ["Phường 7", "Xã Bình Phú", "Xã Thanh Tân"], "Phường Bến Tre"),
    ("Thành phố Bến Tre", ["Phường 6", "Xã Sơn Đông", "Xã Tam Phước"], "Phường Sơn Đông"),
    ("Thành phố Bến Tre", ["Phường Phú Tân", "Xã Hữu Định", "Xã Phước Thạnh"], "Phường Phú Tân"),
]

# Old provinces mapping for mega-province
old_provinces = {
    "Tỉnh Vĩnh Long": [
        "Huyện Mang Thít", "Huyện Long Hồ", "Huyện Vũng Liêm", "Huyện Trà Ôn",
        "Huyện Tam Bình", "Huyện Bình Tân", "Thành phố Vĩnh Long", "Thị xã Bình Minh"
    ],
    "Tỉnh Trà Vinh": [
        "Huyện Càng Long", "Huyện Cầu Kè", "Huyện Tiểu Cần", "Huyện Cầu Ngang",
        "Huyện Trà Cú", "Huyện Duyên Hải", "Thành phố Trà Vinh", "Thị xã Duyên Hải"
    ],
    "Tỉnh Bến Tre": [
        "Huyện Chợ Lách", "Huyện Mỏ Cày Bắc", "Huyện Mỏ Cày Nam",
        "Huyện Thạnh Phú", "Huyện Ba Tri", "Huyện Giồng Trôm", "Huyện Bình Đại",
        "Thành phố Bến Tre"
    ]
}

# Handle Châu Thành which exists in both Trà Vinh and Bến Tre
# We need special handling based on the specific units
chau_thanh_travinh_units = ["Thị trấn Châu Thành", "Xã Mỹ Chánh", "Xã Thanh Mỹ", "Xã Đa Lộc",
                            "Xã Lương Hòa", "Xã Lương Hòa A", "Xã Song Lộc",
                            "Xã Hòa Lợi", "Xã Phước Hảo", "Xã Hưng Mỹ"]

def get_old_province(district, old_units):
    """Get the old province name for a district"""
    # Special handling for Châu Thành
    if district == "Huyện Châu Thành":
        # Check if any old unit matches Trà Vinh's Châu Thành
        for unit in old_units:
            if unit in chau_thanh_travinh_units:
                return "Tỉnh Trà Vinh"
        return "Tỉnh Bến Tre"

    for province, districts in old_provinces.items():
        if district in districts:
            return province
    return "Tỉnh Vĩnh Long"  # default

def main():
    # Load existing data
    dia_danh_path = os.path.join(data_dir, 'dia_danh.json')
    chuyen_doi_path = os.path.join(data_dir, 'chuyen_doi.json')

    with open(dia_danh_path, 'r', encoding='utf-8') as f:
        dia_danh = json.load(f)

    with open(chuyen_doi_path, 'r', encoding='utf-8') as f:
        chuyen_doi = json.load(f)

    new_province = "Tỉnh Vĩnh Long"

    # Create province structure
    if new_province not in dia_danh:
        dia_danh[new_province] = {}

    # Process restructuring data
    mappings_count = 0

    for district, old_units, new_unit in vinhlong_restructuring_data:
        # Add to dia_danh structure
        if district not in dia_danh[new_province]:
            dia_danh[new_province][district] = []

        if new_unit not in dia_danh[new_province][district]:
            dia_danh[new_province][district].append(new_unit)

        # Get old province for this district
        old_province = get_old_province(district, old_units)

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
    province_file = os.path.join(data_dir, f'tỉnh_vĩnh_long_dia_danh.json')
    with open(province_file, 'w', encoding='utf-8') as f:
        json.dump({new_province: dia_danh[new_province]}, f, ensure_ascii=False, indent=2)

    print(f"Processing {new_province}...")
    print(f"  - {mappings_count} conversion mappings")
    print(f"\nTotal new mappings: {mappings_count}")
    print(f"\nFinal totals:")
    print(f"  - dia_danh provinces: {len(dia_danh)}")
    print(f"  - chuyen_doi mappings: {len(chuyen_doi)}")

if __name__ == '__main__':
    main()

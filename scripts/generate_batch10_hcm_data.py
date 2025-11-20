#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate restructuring data for TP Hồ Chí Minh (mới) - Batch 10
Mega-province combining: TP Hồ Chí Minh + Bình Dương + Bà Rịa - Vũng Tàu
163 items, 168 units (113 phường, 54 xã, 1 đặc khu)
"""

import json
import os

# Get the project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
data_dir = os.path.join(project_root, 'templates_app', 'static', 'data')

# TP Hồ Chí Minh (mới) restructuring data
# Format: (district, [old units], new unit name)
hcm_restructuring_data = [
    # Quận 1
    ("Quận 1", ["Phường Bến Nghé", "Phường Đa Kao", "Phường Nguyễn Thái Bình"], "Phường Sài Gòn"),
    ("Quận 1", ["Phường Tân Định", "Phường Đa Kao"], "Phường Tân Định"),
    ("Quận 1", ["Phường Bến Thành", "Phường Phạm Ngũ Lão", "Phường Cầu Ông Lãnh", "Phường Nguyễn Thái Bình"], "Phường Bến Thành"),
    ("Quận 1", ["Phường Nguyễn Cư Trinh", "Phường Cầu Kho", "Phường Cô Giang", "Phường Cầu Ông Lãnh"], "Phường Cầu Ông Lãnh"),

    # Quận 3
    ("Quận 3", ["Phường 1", "Phường 2", "Phường 3", "Phường 5", "Phường 4"], "Phường Bàn Cờ"),
    ("Quận 3", ["Phường Võ Thị Sáu", "Phường 4"], "Phường Xuân Hòa"),
    ("Quận 3", ["Phường 9", "Phường 11", "Phường 12", "Phường 14"], "Phường Nhiêu Lộc"),

    # Quận 4
    ("Quận 4", ["Phường 13", "Phường 16", "Phường 18", "Phường 15"], "Phường Xóm Chiếu"),
    ("Quận 4", ["Phường 8", "Phường 9", "Phường 2", "Phường 4", "Phường 15"], "Phường Khánh Hội"),
    ("Quận 4", ["Phường 1", "Phường 3", "Phường 2", "Phường 4"], "Phường Vĩnh Hội"),

    # Quận 5
    ("Quận 5", ["Phường 1", "Phường 2", "Phường 4"], "Phường Chợ Quán"),
    ("Quận 5", ["Phường 5", "Phường 7", "Phường 9"], "Phường An Đông"),
    ("Quận 5", ["Phường 11", "Phường 12", "Phường 13", "Phường 14"], "Phường Chợ Lớn"),

    # Quận 6
    ("Quận 6", ["Phường 2", "Phường 9"], "Phường Bình Tây"),
    ("Quận 6", ["Phường 1", "Phường 7", "Phường 8"], "Phường Bình Tiên"),
    ("Quận 6", ["Phường 10", "Phường 11", "Phường 16"], "Phường Bình Phú"),
    ("Quận 6", ["Phường 12", "Phường 13", "Phường 14"], "Phường Phú Lâm"),

    # Quận 7
    ("Quận 7", ["Phường Bình Thuận", "Phường Tân Thuận Đông", "Phường Tân Thuận Tây"], "Phường Tân Thuận"),
    ("Quận 7", ["Phường Phú Thuận", "Phường Phú Mỹ"], "Phường Phú Thuận"),
    ("Quận 7", ["Phường Tân Phú", "Phường Phú Mỹ"], "Phường Tân Mỹ"),
    ("Quận 7", ["Phường Tân Phong", "Phường Tân Quy", "Phường Tân Kiểng", "Phường Tân Hưng"], "Phường Tân Hưng"),

    # Quận 8
    ("Quận 8", ["Phường 4", "Phường Rạch Ông", "Phường Hưng Phú", "Phường 5"], "Phường Chánh Hưng"),
    ("Quận 8", ["Phường 14", "Phường 15", "Phường Xóm Củi", "Phường 16"], "Phường Phú Định"),
    ("Quận 8", ["Phường 6", "Phường 7", "Xã An Phú Tây", "Phường 5"], "Phường Bình Đông"),

    # Quận 10
    ("Quận 10", ["Phường 6", "Phường 8", "Phường 14"], "Phường Diên Hồng"),
    ("Quận 10", ["Phường 1", "Phường 2", "Phường 4", "Phường 9", "Phường 10"], "Phường Vườn Lài"),
    ("Quận 10", ["Phường 12", "Phường 13", "Phường 15", "Phường 14"], "Phường Hòa Hưng"),

    # Quận 11
    ("Quận 11", ["Phường 1", "Phường 7", "Phường 16"], "Phường Minh Phụng"),
    ("Quận 11", ["Phường 3", "Phường 10", "Phường 8"], "Phường Bình Thới"),
    ("Quận 11", ["Phường 5", "Phường 14"], "Phường Hòa Bình"),
    ("Quận 11", ["Phường 11", "Phường 15", "Phường 8"], "Phường Phú Thọ"),

    # Quận 12
    ("Quận 12", ["Phường Tân Thới Nhất", "Phường Tân Hưng Thuận", "Phường Đông Hưng Thuận"], "Phường Đông Hưng Thuận"),
    ("Quận 12", ["Phường Tân Chánh Hiệp", "Phường Trung Mỹ Tây"], "Phường Trung Mỹ Tây"),
    ("Quận 12", ["Phường Hiệp Thành", "Phường Tân Thới Hiệp"], "Phường Tân Thới Hiệp"),
    ("Quận 12", ["Phường Thạnh Xuân", "Phường Thới An"], "Phường Thới An"),
    ("Quận 12", ["Phường Thạnh Lộc", "Phường An Phú Đông"], "Phường An Phú Đông"),

    # Quận Bình Tân
    ("Quận Bình Tân", ["Phường Bình Trị Đông B", "Phường An Lạc A", "Phường An Lạc"], "Phường An Lạc"),
    ("Quận Bình Tân", ["Phường Bình Hưng Hòa B", "Phường Bình Trị Đông A", "Phường Tân Tạo"], "Phường Bình Tân"),
    ("Quận Bình Tân", ["Phường Tân Tạo A", "Phường Tân Tạo", "Xã Tân Kiên"], "Phường Tân Tạo"),
    ("Quận Bình Tân", ["Phường Bình Trị Đông", "Phường Bình Hưng Hòa A", "Phường Bình Trị Đông A"], "Phường Bình Trị Đông"),
    ("Quận Bình Tân", ["Phường Bình Hưng Hòa", "Phường Sơn Kỳ", "Phường Bình Hưng Hòa A"], "Phường Bình Hưng Hòa"),

    # Quận Bình Thạnh
    ("Quận Bình Thạnh", ["Phường 1", "Phường 2", "Phường 7", "Phường 17"], "Phường Gia Định"),
    ("Quận Bình Thạnh", ["Phường 12", "Phường 14", "Phường 26"], "Phường Bình Thạnh"),
    ("Quận Bình Thạnh", ["Phường 5", "Phường 11", "Phường 13"], "Phường Bình Lợi Trung"),
    ("Quận Bình Thạnh", ["Phường 19", "Phường 22", "Phường 25"], "Phường Thạnh Mỹ Tây"),
    ("Quận Bình Thạnh", ["Phường 27", "Phường 28"], "Phường Bình Quới"),

    # Quận Gò Vấp
    ("Quận Gò Vấp", ["Phường 1", "Phường 3"], "Phường Hạnh Thông"),
    ("Quận Gò Vấp", ["Phường 5", "Phường 6"], "Phường An Nhơn"),
    ("Quận Gò Vấp", ["Phường 10", "Phường 17"], "Phường Gò Vấp"),
    ("Quận Gò Vấp", ["Phường 15", "Phường 16"], "Phường An Hội Đông"),
    ("Quận Gò Vấp", ["Phường 8", "Phường 11"], "Phường Thông Tây Hội"),
    ("Quận Gò Vấp", ["Phường 12", "Phường 14"], "Phường An Hội Tây"),

    # Quận Phú Nhuận
    ("Quận Phú Nhuận", ["Phường 4", "Phường 5", "Phường 9"], "Phường Đức Nhuận"),
    ("Quận Phú Nhuận", ["Phường 1", "Phường 2", "Phường 7", "Phường 15"], "Phường Cầu Kiệu"),
    ("Quận Phú Nhuận", ["Phường 8", "Phường 10", "Phường 11", "Phường 13", "Phường 15"], "Phường Phú Nhuận"),

    # Quận Tân Bình
    ("Quận Tân Bình", ["Phường 1", "Phường 2", "Phường 3"], "Phường Tân Sơn Hòa"),
    ("Quận Tân Bình", ["Phường 4", "Phường 5", "Phường 7"], "Phường Tân Sơn Nhất"),
    ("Quận Tân Bình", ["Phường 6", "Phường 8", "Phường 9"], "Phường Tân Hòa"),
    ("Quận Tân Bình", ["Phường 10", "Phường 11", "Phường 12"], "Phường Bảy Hiền"),
    ("Quận Tân Bình", ["Phường 13", "Phường 14", "Phường 15"], "Phường Tân Bình"),
    ("Quận Tân Bình", ["Phường 15"], "Phường Tân Sơn"),

    # Quận Tân Phú
    ("Quận Tân Phú", ["Phường Tây Thạnh", "Phường Sơn Kỳ"], "Phường Tây Thạnh"),
    ("Quận Tân Phú", ["Phường Tân Sơn Nhì", "Phường Sơn Kỳ", "Phường Tân Quý", "Phường Tân Thành"], "Phường Tân Sơn Nhì"),
    ("Quận Tân Phú", ["Phường Phú Thọ Hòa", "Phường Tân Thành", "Phường Tân Quý"], "Phường Phú Thọ Hòa"),
    ("Quận Tân Phú", ["Phường Phú Trung", "Phường Hòa Thạnh", "Phường Tân Thới Hòa", "Phường Tân Thành"], "Phường Tân Phú"),
    ("Quận Tân Phú", ["Phường Hiệp Tân", "Phường Phú Thạnh", "Phường Tân Thới Hòa"], "Phường Phú Thạnh"),

    # Thành phố Thủ Đức
    ("Thành phố Thủ Đức", ["Phường Hiệp Bình Chánh", "Phường Hiệp Bình Phước", "Phường Linh Đông"], "Phường Hiệp Bình"),
    ("Thành phố Thủ Đức", ["Phường Bình Thọ", "Phường Linh Chiểu", "Phường Trường Thọ", "Phường Linh Tây", "Phường Linh Đông"], "Phường Thủ Đức"),
    ("Thành phố Thủ Đức", ["Phường Bình Chiểu", "Phường Tam Phú", "Phường Tam Bình"], "Phường Tam Bình"),
    ("Thành phố Thủ Đức", ["Phường Linh Trung", "Phường Linh Xuân", "Phường Linh Tây"], "Phường Linh Xuân"),
    ("Thành phố Thủ Đức", ["Phường Tân Phú", "Phường Hiệp Phú", "Phường Tăng Nhơn Phú A", "Phường Tăng Nhơn Phú B", "Phường Long Thạnh Mỹ"], "Phường Tăng Nhơn Phú"),
    ("Thành phố Thủ Đức", ["Phường Long Bình", "Phường Long Thạnh Mỹ"], "Phường Long Bình"),
    ("Thành phố Thủ Đức", ["Phường Trường Thạnh", "Phường Long Phước"], "Phường Long Phước"),
    ("Thành phố Thủ Đức", ["Phường Phú Hữu", "Phường Long Trường"], "Phường Long Trường"),
    ("Thành phố Thủ Đức", ["Phường Thạnh Mỹ Lợi", "Phường Cát Lái"], "Phường Cát Lái"),
    ("Thành phố Thủ Đức", ["Phường Bình Trưng Đông", "Phường Bình Trưng Tây", "Phường An Phú"], "Phường Bình Trưng"),
    ("Thành phố Thủ Đức", ["Phường Phước Bình", "Phường Phước Long A", "Phường Phước Long B"], "Phường Phước Long"),
    ("Thành phố Thủ Đức", ["Phường Thủ Thiêm", "Phường An Lợi Đông", "Phường Thảo Điền", "Phường An Khánh", "Phường An Phú"], "Phường An Khánh"),

    # Thành phố Dĩ An (Bình Dương)
    ("Thành phố Dĩ An", ["Phường Bình An", "Phường Bình Thắng", "Phường Đông Hòa"], "Phường Đông Hòa"),
    ("Thành phố Dĩ An", ["Phường An Bình", "Phường Dĩ An", "Phường Tân Đông Hiệp"], "Phường Dĩ An"),
    ("Thành phố Dĩ An", ["Phường Tân Bình", "Phường Thái Hòa", "Phường Tân Đông Hiệp"], "Phường Tân Đông Hiệp"),

    # Thành phố Thuận An (Bình Dương)
    ("Thành phố Thuận An", ["Phường An Phú", "Phường Bình Chuẩn"], "Phường An Phú"),
    ("Thành phố Thuận An", ["Phường Bình Hòa", "Phường Vĩnh Phú"], "Phường Bình Hòa"),
    ("Thành phố Thuận An", ["Phường Bình Nhâm", "Phường Lái Thiêu", "Phường Vĩnh Phú"], "Phường Lái Thiêu"),
    ("Thành phố Thuận An", ["Phường Hưng Định", "Phường An Thạnh", "Xã An Sơn"], "Phường Thuận An"),
    ("Thành phố Thuận An", ["Phường Thuận Giao", "Phường Bình Chuẩn"], "Phường Thuận Giao"),

    # Thành phố Thủ Dầu Một (Bình Dương)
    ("Thành phố Thủ Dầu Một", ["Phường Phú Cường", "Phường Phú Thọ", "Phường Chánh Nghĩa", "Phường Hiệp Thành", "Phường Chánh Mỹ"], "Phường Thủ Dầu Một"),
    ("Thành phố Thủ Dầu Một", ["Phường Phú Hòa", "Phường Phú Lợi", "Phường Hiệp Thành"], "Phường Phú Lợi"),
    ("Thành phố Thủ Dầu Một", ["Phường Định Hòa", "Phường Tương Bình Hiệp", "Phường Hiệp An", "Phường Chánh Mỹ"], "Phường Chánh Hiệp"),
    ("Thành phố Thủ Dầu Một", ["Phường Phú Mỹ", "Phường Hòa Phú", "Phường Phú Tân", "Phường Phú Chánh"], "Phường Bình Dương"),

    # Thành phố Bến Cát (Bình Dương)
    ("Thành phố Bến Cát", ["Phường Tân Định", "Phường Hòa Lợi"], "Phường Hòa Lợi"),
    ("Thành phố Bến Cát", ["Phường Tân An", "Xã Phú An", "Phường Hiệp An"], "Phường Phú An"),
    ("Thành phố Bến Cát", ["Phường An Tây", "Xã Thanh Tuyền", "Xã An Lập"], "Phường Tây Nam"),
    ("Thành phố Bến Cát", ["Phường An Điền", "Xã Long Nguyên", "Phường Mỹ Phước"], "Phường Long Nguyên"),
    ("Thành phố Bến Cát", ["Xã Tân Hưng", "Xã Lai Hưng", "Phường Mỹ Phước"], "Phường Bến Cát"),
    ("Thành phố Bến Cát", ["Phường Chánh Phú Hòa", "Xã Hưng Hòa"], "Phường Chánh Phú Hòa"),
    ("Thành phố Bến Cát", ["Phường Vĩnh Tân", "Thị trấn Tân Bình"], "Phường Vĩnh Tân"),
    ("Thành phố Bến Cát", ["Xã Bình Mỹ", "Phường Hội Nghĩa"], "Phường Bình Cơ"),

    # Thành phố Tân Uyên (Bình Dương)
    ("Thành phố Tân Uyên", ["Phường Uyên Hưng", "Xã Bạch Đằng", "Xã Tân Lập", "Xã Tân Mỹ"], "Phường Tân Uyên"),
    ("Thành phố Tân Uyên", ["Phường Khánh Bình", "Phường Tân Hiệp"], "Phường Tân Hiệp"),
    ("Thành phố Tân Uyên", ["Phường Thạnh Phước", "Phường Tân Phước Khánh", "Phường Tân Vĩnh Hiệp", "Xã Thạnh Hội", "Phường Thái Hòa"], "Phường Tân Khánh"),

    # Thành phố Vũng Tàu (Bà Rịa - Vũng Tàu)
    ("Thành phố Vũng Tàu", ["Phường 1", "Phường 2", "Phường 3", "Phường 4", "Phường 5", "Phường Thắng Nhì", "Phường Thắng Tam"], "Phường Vũng Tàu"),
    ("Thành phố Vũng Tàu", ["Phường 7", "Phường 8", "Phường 9", "Phường Nguyễn An Ninh"], "Phường Tam Thắng"),
    ("Thành phố Vũng Tàu", ["Phường 10", "Phường Thắng Nhất", "Phường Rạch Dừa"], "Phường Rạch Dừa"),
    ("Thành phố Vũng Tàu", ["Phường 11", "Phường 12"], "Phường Phước Thắng"),

    # Thành phố Bà Rịa (Bà Rịa - Vũng Tàu)
    ("Thành phố Bà Rịa", ["Xã Tân Hưng", "Phường Kim Dinh", "Phường Long Hương"], "Phường Long Hương"),
    ("Thành phố Bà Rịa", ["Phường Phước Trung", "Phường Phước Nguyên", "Phường Long Toàn", "Phường Phước Hưng"], "Phường Bà Rịa"),
    ("Thành phố Bà Rịa", ["Phường Long Tâm", "Xã Hòa Long", "Xã Long Phước"], "Phường Tam Long"),
    ("Thành phố Bà Rịa", ["Phường Tân Hòa", "Phường Tân Hải"], "Phường Tân Hải"),
    ("Thành phố Bà Rịa", ["Phường Phước Hòa", "Phường Tân Phước"], "Phường Tân Phước"),

    # Thành phố Phú Mỹ (Bà Rịa - Vũng Tàu)
    ("Thành phố Phú Mỹ", ["Phường Phú Mỹ", "Phường Mỹ Xuân"], "Phường Phú Mỹ"),
    ("Thành phố Phú Mỹ", ["Phường Hắc Dịch", "Xã Sông Xoài"], "Phường Tân Thành"),

    # Huyện Bình Chánh (TP HCM)
    ("Huyện Bình Chánh", ["Xã Vĩnh Lộc A", "Xã Phạm Văn Hai"], "Xã Vĩnh Lộc"),
    ("Huyện Bình Chánh", ["Xã Vĩnh Lộc B", "Xã Phạm Văn Hai", "Phường Tân Tạo"], "Xã Tân Vĩnh Lộc"),
    ("Huyện Bình Chánh", ["Xã Lê Minh Xuân", "Xã Bình Lợi"], "Xã Bình Lợi"),
    ("Huyện Bình Chánh", ["Thị trấn Tân Túc", "Xã Tân Nhựt", "Phường Tân Tạo A", "Xã Tân Kiên", "Phường 16"], "Xã Tân Nhựt"),
    ("Huyện Bình Chánh", ["Xã Tân Quý Tây", "Xã Bình Chánh", "Xã An Phú Tây"], "Xã Bình Chánh"),
    ("Huyện Bình Chánh", ["Xã Đa Phước", "Xã Qui Đức", "Xã Hưng Long"], "Xã Hưng Long"),
    ("Huyện Bình Chánh", ["Xã Phong Phú", "Xã Bình Hưng", "Phường 7"], "Xã Bình Hưng"),

    # Huyện Cần Giờ (TP HCM)
    ("Huyện Cần Giờ", ["Xã Tam Thôn Hiệp", "Xã Bình Khánh", "Xã An Thới Đông"], "Xã Bình Khánh"),
    ("Huyện Cần Giờ", ["Xã Lý Nhơn", "Xã An Thới Đông"], "Xã An Thới Đông"),
    ("Huyện Cần Giờ", ["Xã Long Hòa", "Thị trấn Cần Thạnh"], "Xã Cần Giờ"),

    # Huyện Củ Chi (TP HCM)
    ("Huyện Củ Chi", ["Xã Tân Phú Trung", "Xã Tân Thông Hội", "Xã Phước Vĩnh An"], "Xã Củ Chi"),
    ("Huyện Củ Chi", ["Thị trấn Củ Chi", "Xã Phước Hiệp", "Xã Tân An Hội"], "Xã Tân An Hội"),
    ("Huyện Củ Chi", ["Xã Trung Lập Thượng", "Xã Phước Thạnh", "Xã Thái Mỹ"], "Xã Thái Mỹ"),
    ("Huyện Củ Chi", ["Xã Phú Mỹ Hưng", "Xã An Phú", "Xã An Nhơn Tây"], "Xã An Nhơn Tây"),
    ("Huyện Củ Chi", ["Xã Phạm Văn Cội", "Xã Trung Lập Hạ", "Xã Nhuận Đức"], "Xã Nhuận Đức"),
    ("Huyện Củ Chi", ["Xã Tân Thạnh Tây", "Xã Tân Thạnh Đông", "Xã Phú Hòa Đông"], "Xã Phú Hòa Đông"),
    ("Huyện Củ Chi", ["Xã Bình Mỹ", "Xã Hòa Phú", "Xã Trung An"], "Xã Bình Mỹ"),

    # Huyện Hóc Môn (TP HCM)
    ("Huyện Hóc Môn", ["Xã Thới Tam Thôn", "Xã Nhị Bình", "Xã Đông Thạnh"], "Xã Đông Thạnh"),
    ("Huyện Hóc Môn", ["Xã Tân Hiệp", "Xã Tân Xuân", "Thị trấn Hóc Môn"], "Xã Hóc Môn"),
    ("Huyện Hóc Môn", ["Xã Tân Thới Nhì", "Xã Xuân Thới Đông", "Xã Xuân Thới Sơn"], "Xã Xuân Thới Sơn"),
    ("Huyện Hóc Môn", ["Xã Xuân Thới Thượng", "Xã Trung Chánh", "Xã Bà Điểm"], "Xã Bà Điểm"),

    # Huyện Nhà Bè (TP HCM)
    ("Huyện Nhà Bè", ["Thị trấn Nhà Bè", "Xã Phú Xuân", "Xã Phước Kiển", "Xã Phước Lộc"], "Xã Nhà Bè"),
    ("Huyện Nhà Bè", ["Xã Nhơn Đức", "Xã Long Thới", "Xã Hiệp Phước"], "Xã Hiệp Phước"),

    # Huyện Bắc Tân Uyên (Bình Dương)
    ("Huyện Bắc Tân Uyên", ["Xã Lạc An", "Xã Hiếu Liêm", "Xã Thường Tân", "Xã Tân Mỹ"], "Xã Thường Tân"),
    ("Huyện Bắc Tân Uyên", ["Thị trấn Tân Thành", "Xã Đất Cuốc", "Xã Tân Định"], "Xã Bắc Tân Uyên"),

    # Huyện Phú Giáo (Bình Dương)
    ("Huyện Phú Giáo", ["Thị trấn Phước Vĩnh", "Xã An Bình", "Xã Tam Lập"], "Xã Phú Giáo"),
    ("Huyện Phú Giáo", ["Xã Vĩnh Hòa", "Xã Phước Hòa", "Xã Tam Lập"], "Xã Phước Hòa"),
    ("Huyện Phú Giáo", ["Xã Tân Hiệp", "Xã An Thái", "Xã Phước Sang"], "Xã Phước Thành"),
    ("Huyện Phú Giáo", ["Xã An Linh", "Xã Tân Long", "Xã An Long"], "Xã An Long"),

    # Huyện Bàu Bàng (Bình Dương)
    ("Huyện Bàu Bàng", ["Xã Trừ Văn Thố", "Xã Cây Trường II", "Thị trấn Lai Uyên"], "Xã Trừ Văn Thố"),
    ("Huyện Bàu Bàng", ["Thị trấn Lai Uyên"], "Xã Bàu Bàng"),

    # Huyện Dầu Tiếng (Bình Dương)
    ("Huyện Dầu Tiếng", ["Xã Long Tân", "Xã Long Hòa", "Xã Minh Tân", "Xã Minh Thạnh"], "Xã Long Hòa"),
    ("Huyện Dầu Tiếng", ["Xã Thanh An", "Xã Định Hiệp", "Xã Thanh Tuyền", "Xã An Lập"], "Xã Thanh An"),
    ("Huyện Dầu Tiếng", ["Thị trấn Dầu Tiếng", "Xã Định An", "Xã Định Thành", "Xã Định Hiệp"], "Xã Dầu Tiếng"),
    ("Huyện Dầu Tiếng", ["Xã Minh Hòa", "Xã Minh Tân", "Xã Minh Thạnh"], "Xã Minh Thạnh"),

    # Thành phố Phú Mỹ - xã (Bà Rịa - Vũng Tàu)
    ("Thành phố Phú Mỹ", ["Xã Tóc Tiên", "Xã Châu Pha"], "Xã Châu Pha"),

    # Huyện Long Điền (Bà Rịa - Vũng Tàu)
    ("Huyện Long Điền", ["Thị trấn Long Hải", "Xã Phước Tỉnh", "Xã Phước Hưng"], "Xã Long Hải"),
    ("Huyện Long Điền", ["Thị trấn Long Điền", "Xã Tam An"], "Xã Long Điền"),
    ("Huyện Long Điền", ["Thị trấn Phước Hải", "Xã Phước Hội"], "Xã Phước Hải"),
    ("Huyện Long Điền", ["Thị trấn Đất Đỏ", "Xã Long Tân", "Xã Láng Dài", "Xã Phước Long Thọ"], "Xã Đất Đỏ"),

    # Huyện Châu Đức (Bà Rịa - Vũng Tàu)
    ("Huyện Châu Đức", ["Xã Đá Bạc", "Xã Nghĩa Thành"], "Xã Nghĩa Thành"),
    ("Huyện Châu Đức", ["Thị trấn Ngãi Giao", "Xã Bình Ba", "Xã Suối Nghệ"], "Xã Ngãi Giao"),
    ("Huyện Châu Đức", ["Thị trấn Kim Long", "Xã Bàu Chinh", "Xã Láng Lớn"], "Xã Kim Long"),
    ("Huyện Châu Đức", ["Xã Cù Bị", "Xã Xà Bang"], "Xã Châu Đức"),
    ("Huyện Châu Đức", ["Xã Bình Trung", "Xã Quảng Thành", "Xã Bình Giã"], "Xã Bình Giã"),
    ("Huyện Châu Đức", ["Xã Suối Rao", "Xã Sơn Bình", "Xã Xuân Sơn"], "Xã Xuân Sơn"),

    # Huyện Xuyên Mộc (Bà Rịa - Vũng Tàu)
    ("Huyện Xuyên Mộc", ["Thị trấn Phước Bửu", "Xã Phước Tân", "Xã Phước Thuận"], "Xã Hồ Tràm"),
    ("Huyện Xuyên Mộc", ["Xã Bông Trang", "Xã Bưng Riềng", "Xã Xuyên Mộc"], "Xã Xuyên Mộc"),
    ("Huyện Xuyên Mộc", ["Xã Hòa Hưng", "Xã Hòa Bình", "Xã Hòa Hội"], "Xã Hòa Hội"),
    ("Huyện Xuyên Mộc", ["Xã Tân Lâm", "Xã Bàu Lâm"], "Xã Bàu Lâm"),

    # Côn Đảo - Đặc khu
    ("Huyện Côn Đảo", ["Huyện Côn Đảo"], "Đặc khu Côn Đảo"),
]

# Old provinces mapping for mega-province
old_provinces = {
    "Thành phố Hồ Chí Minh": [
        "Quận 1", "Quận 3", "Quận 4", "Quận 5", "Quận 6", "Quận 7", "Quận 8",
        "Quận 10", "Quận 11", "Quận 12", "Quận Bình Tân", "Quận Bình Thạnh",
        "Quận Gò Vấp", "Quận Phú Nhuận", "Quận Tân Bình", "Quận Tân Phú",
        "Thành phố Thủ Đức", "Huyện Bình Chánh", "Huyện Cần Giờ",
        "Huyện Củ Chi", "Huyện Hóc Môn", "Huyện Nhà Bè"
    ],
    "Tỉnh Bình Dương": [
        "Thành phố Dĩ An", "Thành phố Thuận An", "Thành phố Thủ Dầu Một",
        "Thành phố Bến Cát", "Thành phố Tân Uyên", "Huyện Bắc Tân Uyên",
        "Huyện Phú Giáo", "Huyện Bàu Bàng", "Huyện Dầu Tiếng"
    ],
    "Tỉnh Bà Rịa - Vũng Tàu": [
        "Thành phố Vũng Tàu", "Thành phố Bà Rịa", "Thành phố Phú Mỹ",
        "Huyện Long Điền", "Huyện Châu Đức", "Huyện Xuyên Mộc", "Huyện Côn Đảo"
    ]
}

def get_old_province(district):
    """Get the old province name for a district"""
    for province, districts in old_provinces.items():
        if district in districts:
            return province
    return "Thành phố Hồ Chí Minh"  # default

def main():
    # Load existing data
    dia_danh_path = os.path.join(data_dir, 'dia_danh.json')
    chuyen_doi_path = os.path.join(data_dir, 'chuyen_doi.json')

    with open(dia_danh_path, 'r', encoding='utf-8') as f:
        dia_danh = json.load(f)

    with open(chuyen_doi_path, 'r', encoding='utf-8') as f:
        chuyen_doi = json.load(f)

    new_province = "Thành phố Hồ Chí Minh"

    # Create province structure
    if new_province not in dia_danh:
        dia_danh[new_province] = {}

    # Process restructuring data
    mappings_count = 0

    for district, old_units, new_unit in hcm_restructuring_data:
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
    province_file = os.path.join(data_dir, f'thành_phố_hồ_chí_minh_dia_danh.json')
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

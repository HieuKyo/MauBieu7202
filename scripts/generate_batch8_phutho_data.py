#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch 8 Part 1: Generate Phú Thọ (mới) province data
Province: Tỉnh Phú Thọ (146 items)
Note: This is a mega-province combining old Phú Thọ + Vĩnh Phúc + Hòa Bình
"""

import json
import os

# Phú Thọ restructuring data - 146 items organized by district
phutho_restructuring_data = [
    # Thành phố Việt Trì (old Phú Thọ) - item 1
    ("Thành phố Việt Trì", ["Xã Thanh Đình", "Xã Chu Hóa", "Xã Hy Cương"], "Xã Hy Cương"),

    # Huyện Lâm Thao (old Phú Thọ) - items 2-5
    ("Huyện Lâm Thao", ["Thị trấn Hùng Sơn", "Thị trấn Lâm Thao", "Xã Thạch Sơn"], "Xã Lâm Thao"),
    ("Huyện Lâm Thao", ["Xã Tiên Kiên", "Xã Xuân Huy", "Xã Xuân Lũng"], "Xã Xuân Lũng"),
    ("Huyện Lâm Thao", ["Xã Tứ Xã", "Xã Sơn Vi", "Xã Phùng Nguyên"], "Xã Phùng Nguyên"),
    ("Huyện Lâm Thao", ["Xã Cao Xá", "Xã Vĩnh Lại", "Xã Bản Nguyên"], "Xã Bản Nguyên"),

    # Huyện Phù Ninh (old Phú Thọ) - items 6-10
    ("Huyện Phù Ninh", ["Thị trấn Phong Châu", "Xã Phú Nham", "Xã Phú Lộc", "Xã Phù Ninh"], "Xã Phù Ninh"),
    ("Huyện Phù Ninh", ["Xã Bảo Thanh", "Xã Trị Quận", "Xã Hạ Giáp", "Xã Gia Thanh"], "Xã Dân Chủ"),
    ("Huyện Phù Ninh", ["Xã Liên Hoa", "Xã Lệ Mỹ", "Xã Phú Mỹ"], "Xã Phú Mỹ"),
    ("Huyện Phù Ninh", ["Xã Tiên Phú", "Xã Trung Giáp", "Xã Trạm Thản"], "Xã Trạm Thản"),
    ("Huyện Phù Ninh", ["Xã Tiên Du", "Xã An Đạo", "Xã Bình Phú"], "Xã Bình Phú"),

    # Huyện Thanh Ba (old Phú Thọ) - items 11-16
    ("Huyện Thanh Ba", ["Thị trấn Thanh Ba", "Xã Đồng Xuân", "Xã Hanh Cù", "Xã Vân Lĩnh"], "Xã Thanh Ba"),
    ("Huyện Thanh Ba", ["Xã Đại An", "Xã Đông Lĩnh", "Xã Quảng Yên"], "Xã Quảng Yên"),
    ("Huyện Thanh Ba", ["Xã Ninh Dân", "Xã Mạn Lạn", "Xã Hoàng Cương"], "Xã Hoàng Cương"),
    ("Huyện Thanh Ba", ["Xã Khải Xuân", "Xã Võ Lao", "Xã Đông Thành"], "Xã Đông Thành"),
    ("Huyện Thanh Ba", ["Xã Sơn Cương", "Xã Thanh Hà", "Xã Chí Tiên"], "Xã Chí Tiên"),
    ("Huyện Thanh Ba", ["Xã Đỗ Sơn", "Xã Đỗ Xuyên", "Xã Lương Lỗ"], "Xã Liên Minh"),

    # Huyện Đoan Hùng (old Phú Thọ) - items 17-21
    ("Huyện Đoan Hùng", ["Thị trấn Đoan Hùng", "Xã Hợp Nhất", "Xã Ngọc Quan"], "Xã Đoan Hùng"),
    ("Huyện Đoan Hùng", ["Xã Phú Lâm", "Xã Ca Đình", "Xã Tây Cốc"], "Xã Tây Cốc"),
    ("Huyện Đoan Hùng", ["Xã Hùng Long", "Xã Yên Kiện", "Xã Chân Mộng"], "Xã Chân Mộng"),
    ("Huyện Đoan Hùng", ["Xã Hùng Xuyên", "Xã Chí Đám"], "Xã Chí Đám"),
    ("Huyện Đoan Hùng", ["Xã Bằng Doãn", "Xã Phúc Lai", "Xã Bằng Luân"], "Xã Bằng Luân"),

    # Huyện Hạ Hòa (old Phú Thọ) - items 22-27
    ("Huyện Hạ Hòa", ["Thị trấn Hạ Hòa", "Xã Minh Hạc", "Xã Ấm Hạ", "Xã Gia Điền"], "Xã Hạ Hòa"),
    ("Huyện Hạ Hòa", ["Xã Tứ Hiệp", "Xã Đại Phạm", "Xã Hà Lương", "Xã Đan Thượng"], "Xã Đan Thượng"),
    ("Huyện Hạ Hòa", ["Xã Hương Xạ", "Xã Phương Viên", "Xã Yên Kỳ"], "Xã Yên Kỳ"),
    ("Huyện Hạ Hòa", ["Xã Lang Sơn", "Xã Yên Luật", "Xã Vĩnh Chân"], "Xã Vĩnh Chân"),
    ("Huyện Hạ Hòa", ["Xã Vô Tranh", "Xã Bằng Giã", "Xã Minh Côi", "Xã Văn Lang"], "Xã Văn Lang"),
    ("Huyện Hạ Hòa", ["Xã Hiền Lương", "Xã Xuân Áng"], "Xã Hiền Lương"),

    # Huyện Cẩm Khê (old Phú Thọ) - items 28-33
    ("Huyện Cẩm Khê", ["Thị trấn Cẩm Khê", "Xã Minh Tân", "Xã Phong Thịnh"], "Xã Cẩm Khê"),
    ("Huyện Cẩm Khê", ["Xã Hương Lung", "Xã Phú Khê"], "Xã Phú Khê"),
    ("Huyện Cẩm Khê", ["Xã Nhật Tiến", "Xã Hùng Việt"], "Xã Hùng Việt"),
    ("Huyện Cẩm Khê", ["Xã Điêu Lương", "Xã Yên Dưỡng", "Xã Đồng Lương"], "Xã Đồng Lương"),
    ("Huyện Cẩm Khê", ["Xã Phượng Vĩ", "Xã Minh Thắng", "Xã Tiên Lương"], "Xã Tiên Lương"),
    ("Huyện Cẩm Khê", ["Xã Tùng Khê", "Xã Tam Sơn", "Xã Văn Bán"], "Xã Vân Bán"),

    # Huyện Tam Nông (old Phú Thọ) - items 34-37
    ("Huyện Tam Nông", ["Thị trấn Hưng Hóa", "Xã Dân Quyền", "Xã Hương Nộn"], "Xã Tam Nông"),
    ("Huyện Tam Nông", ["Xã Dị Nậu", "Xã Tề Lễ", "Xã Thọ Văn"], "Xã Thọ Văn"),
    ("Huyện Tam Nông", ["Xã Quang Húc", "Xã Lam Sơn", "Xã Vạn Xuân"], "Xã Vạn Xuân"),
    ("Huyện Tam Nông", ["Xã Thanh Uyên", "Xã Bắc Sơn", "Xã Hiền Quan"], "Xã Hiền Quan"),

    # Huyện Thanh Thủy (old Phú Thọ) - items 38-40
    ("Huyện Thanh Thủy", ["Xã Sơn Thủy", "Xã Đoan Hạ", "Xã Bảo Yên", "Thị trấn Thanh Thủy"], "Xã Thanh Thủy"),
    ("Huyện Thanh Thủy", ["Xã Xuân Lộc", "Xã Thạch Đồng", "Xã Tân Phương", "Xã Đào Xá"], "Xã Đào Xá"),
    ("Huyện Thanh Thủy", ["Xã Đồng Trung", "Xã Hoàng Xá", "Xã Tu Vũ"], "Xã Tu Vũ"),

    # Huyện Thanh Sơn (old Phú Thọ) - items 41-47
    ("Huyện Thanh Sơn", ["Thị trấn Thanh Sơn", "Xã Sơn Hùng", "Xã Giáp Lai", "Xã Thạch Khoán", "Xã Thục Luyện"], "Xã Thanh Sơn"),
    ("Huyện Thanh Sơn", ["Xã Địch Quả", "Xã Cự Thắng", "Xã Võ Miếu"], "Xã Võ Miếu"),
    ("Huyện Thanh Sơn", ["Xã Tân Lập", "Xã Tân Minh", "Xã Văn Miếu"], "Xã Văn Miếu"),
    ("Huyện Thanh Sơn", ["Xã Tất Thắng", "Xã Thắng Sơn", "Xã Cự Đồng"], "Xã Cự Đồng"),
    ("Huyện Thanh Sơn", ["Xã Yên Lương", "Xã Yên Lãng", "Xã Hương Cần"], "Xã Hương Cần"),
    ("Huyện Thanh Sơn", ["Xã Tinh Nhuệ", "Xã Lương Nha", "Xã Yên Sơn"], "Xã Yên Sơn"),
    ("Huyện Thanh Sơn", ["Xã Đông Cửu", "Xã Thượng Cửu", "Xã Khả Cửu"], "Xã Khả Cửu"),

    # Huyện Tân Sơn (old Phú Thọ) - items 48-52
    ("Huyện Tân Sơn", ["Thị trấn Tân Phú", "Xã Thu Ngạc", "Xã Thạch Kiệt"], "Xã Tân Sơn"),
    ("Huyện Tân Sơn", ["Xã Mỹ Thuận", "Xã Văn Luông", "Xã Minh Đài"], "Xã Minh Đài"),
    ("Huyện Tân Sơn", ["Xã Kiệt Sơn", "Xã Tân Sơn", "Xã Đồng Sơn", "Xã Lai Đồng"], "Xã Lai Đồng"),
    ("Huyện Tân Sơn", ["Xã Kim Thượng", "Xã Xuân Sơn", "Xã Xuân Đài"], "Xã Xuân Đài"),
    ("Huyện Tân Sơn", ["Xã Tam Thanh", "Xã Vinh Tiền", "Xã Long Cốc"], "Xã Long Cốc"),

    # Huyện Yên Lập (old Phú Thọ) - items 53-57
    ("Huyện Yên Lập", ["Thị trấn Yên Lập", "Xã Đồng Thịnh", "Xã Hưng Long", "Xã Đồng Lạc"], "Xã Yên Lập"),
    ("Huyện Yên Lập", ["Xã Phúc Khánh", "Xã Nga Hoàng", "Xã Thượng Long"], "Xã Thượng Long"),
    ("Huyện Yên Lập", ["Xã Mỹ Lương", "Xã Mỹ Lung", "Xã Lương Sơn"], "Xã Sơn Lương"),
    ("Huyện Yên Lập", ["Xã Xuân Thủy", "Xã Xuân An", "Xã Xuân Viên"], "Xã Xuân Viên"),
    ("Huyện Yên Lập", ["Xã Ngọc Lập", "Xã Ngọc Đồng", "Xã Minh Hòa"], "Xã Minh Hòa"),

    # Huyện Sông Lô (old Vĩnh Phúc) - items 58-61
    ("Huyện Sông Lô", ["Xã Tân Lập", "Xã Đồng Quế", "Thị trấn Tam Sơn"], "Xã Tam Sơn"),
    ("Huyện Sông Lô", ["Xã Đồng Thịnh", "Xã Tứ Yên", "Xã Đức Bác", "Xã Yên Thạch"], "Xã Sông Lô"),
    ("Huyện Sông Lô", ["Xã Nhân Đạo", "Xã Đôn Nhân", "Xã Phương Khoan", "Xã Hải Lựu"], "Xã Hải Lựu"),
    ("Huyện Sông Lô", ["Xã Quang Yên", "Xã Lãng Công"], "Xã Yên Lãng"),

    # Huyện Lập Thạch (old Vĩnh Phúc) - items 62-67
    ("Huyện Lập Thạch", ["Thị trấn Lập Thạch", "Xã Xuân Hòa", "Xã Tử Du", "Xã Vân Trục"], "Xã Lập Thạch"),
    ("Huyện Lập Thạch", ["Xã Xuân Lôi", "Xã Văn Quán", "Xã Đồng Ích", "Xã Tiên Lữ"], "Xã Tiên Lữ"),
    ("Huyện Lập Thạch", ["Xã Bắc Bình", "Xã Liễn Sơn", "Xã Thái Hòa"], "Xã Thái Hòa"),
    ("Huyện Lập Thạch", ["Thị trấn Hoa Sơn", "Xã Bàn Giản", "Xã Liên Hòa"], "Xã Liên Hòa"),
    ("Huyện Lập Thạch", ["Xã Ngọc Mỹ", "Xã Quang Sơn", "Xã Hợp Lý"], "Xã Hợp Lý"),
    ("Huyện Lập Thạch", ["Xã Tây Sơn", "Xã Cao Phong", "Xã Sơn Đông"], "Xã Sơn Đông"),

    # Huyện Tam Đảo (old Vĩnh Phúc) - items 68-70
    ("Huyện Tam Đảo", ["Thị trấn Hợp Châu", "Thị trấn Tam Đảo", "Xã Hồ Sơn", "Xã Minh Quang"], "Xã Tam Đảo"),
    ("Huyện Tam Đảo", ["Thị trấn Đại Đình", "Xã Bồ Lý"], "Xã Đại Đình"),
    ("Huyện Tam Đảo", ["Xã Yên Dương", "Xã Đạo Trù"], "Xã Đạo Trù"),

    # Huyện Tam Dương (old Vĩnh Phúc) - items 71-74
    ("Huyện Tam Dương", ["Thị trấn Hợp Hòa", "Thị trấn Kim Long", "Xã Hướng Đạo", "Xã Đạo Tú"], "Xã Tam Dương"),
    ("Huyện Tam Dương", ["Xã Duy Phiên", "Xã Thanh Vân", "Xã Hội Thịnh"], "Xã Hội Thịnh"),
    ("Huyện Tam Dương", ["Xã Hoàng Đan", "Xã Hoàng Lâu", "Xã An Hòa"], "Xã Hoàng An"),
    ("Huyện Tam Dương", ["Xã Đồng Tĩnh", "Xã Hoàng Hoa", "Xã Tam Quan"], "Xã Tam Dương Bắc"),

    # Huyện Vĩnh Tường (old Vĩnh Phúc) - items 75-80
    ("Huyện Vĩnh Tường", ["Thị trấn Vĩnh Tường", "Thị trấn Tứ Trưng", "Xã Lương Điền", "Xã Vũ Di"], "Xã Vĩnh Tường"),
    ("Huyện Vĩnh Tường", ["Thị trấn Thổ Tang", "Xã Thượng Trưng", "Xã Tuân Chính"], "Xã Thổ Tang"),
    ("Huyện Vĩnh Tường", ["Xã Nghĩa Hưng", "Xã Yên Lập", "Xã Đại Đồng"], "Xã Vĩnh Hưng"),
    ("Huyện Vĩnh Tường", ["Xã Kim Xá", "Xã Yên Bình", "Xã Chấn Hưng"], "Xã Vĩnh An"),
    ("Huyện Vĩnh Tường", ["Xã An Nhân", "Xã Vĩnh Thịnh", "Xã Ngũ Kiên", "Xã Vĩnh Phú"], "Xã Vĩnh Phú"),
    ("Huyện Vĩnh Tường", ["Xã Sao Đại Việt", "Xã Lũng Hòa", "Xã Tân Phú"], "Xã Vĩnh Thành"),

    # Huyện Yên Lạc (old Vĩnh Phúc) - items 81-85
    ("Huyện Yên Lạc", ["Thị trấn Yên Lạc", "Xã Bình Định", "Xã Đồng Cương"], "Xã Yên Lạc"),
    ("Huyện Yên Lạc", ["Xã Đồng Văn", "Xã Trung Nguyên", "Xã Tề Lỗ"], "Xã Tề Lỗ"),
    ("Huyện Yên Lạc", ["Xã Đại Tự", "Xã Hồng Châu", "Xã Liên Châu"], "Xã Liên Châu"),
    ("Huyện Yên Lạc", ["Thị trấn Tam Hồng", "Xã Yên Phương", "Xã Yên Đồng"], "Xã Tam Hồng"),
    ("Huyện Yên Lạc", ["Xã Văn Tiến", "Xã Trung Kiên", "Xã Trung Hà", "Xã Nguyệt Đức"], "Xã Nguyệt Đức"),

    # Huyện Bình Xuyên (old Vĩnh Phúc) - items 86-90
    ("Huyện Bình Xuyên", ["Thị trấn Hương Canh", "Xã Tam Hợp", "Xã Quất Lưu", "Xã Sơn Lôi"], "Xã Bình Nguyên"),
    ("Huyện Bình Xuyên", ["Thị trấn Thanh Lãng", "Thị trấn Đạo Đức", "Xã Tân Phong", "Xã Phú Xuân"], "Xã Xuân Lãng"),
    ("Huyện Bình Xuyên", ["Thị trấn Gia Khánh", "Xã Hương Sơn", "Xã Thiện Kế"], "Xã Bình Xuyên"),
    ("Huyện Bình Xuyên", ["Thị trấn Bá Hiến", "Xã Trung Mỹ"], "Xã Bình Tuyền"),
    ("Huyện Bình Xuyên", ["Xã Hợp Thành", "Xã Quang Tiến", "Xã Thịnh Minh"], "Xã Thịnh Minh"),

    # Huyện Cao Phong (old Hòa Bình) - items 91-93
    ("Huyện Cao Phong", ["Thị trấn Cao Phong", "Xã Hợp Phong", "Xã Thu Phong"], "Xã Cao Phong"),
    ("Huyện Cao Phong", ["Xã Dũng Phong", "Xã Nam Phong", "Xã Tây Phong", "Xã Thạch Yên"], "Xã Mường Thàng"),
    ("Huyện Cao Phong", ["Xã Bắc Phong", "Xã Bình Thanh", "Xã Thung Nai"], "Xã Thung Nai"),

    # Huyện Đà Bắc (old Hòa Bình) - items 94-99
    ("Huyện Đà Bắc", ["Thị trấn Đà Bắc", "Xã Hiền Lương", "Xã Toàn Sơn", "Xã Tú Lý"], "Xã Đà Bắc"),
    ("Huyện Đà Bắc", ["Xã Tân Minh", "Xã Cao Sơn"], "Xã Cao Sơn"),
    ("Huyện Đà Bắc", ["Xã Mường Chiềng", "Xã Nánh Nghê"], "Xã Đức Nhàn"),
    ("Huyện Đà Bắc", ["Xã Đoàn Kết", "Xã Đồng Ruộng", "Xã Trung Thành", "Xã Yên Hoà"], "Xã Quy Đức"),
    ("Huyện Đà Bắc", ["Xã Đồng Chum", "Xã Giáp Đắt", "Xã Tân Pheo"], "Xã Tân Pheo"),
    ("Huyện Đà Bắc", ["Xã Tiền Phong", "Xã Vầy Nưa"], "Xã Tiền Phong"),

    # Huyện Kim Bôi (old Hòa Bình) - items 100-104
    ("Huyện Kim Bôi", ["Thị trấn Bo", "Xã Vĩnh Đồng", "Xã Kim Bôi"], "Xã Kim Bôi"),
    ("Huyện Kim Bôi", ["Xã Đông Bắc", "Xã Hợp Tiến", "Xã Tú Sơn", "Xã Vĩnh Tiến"], "Xã Mường Động"),
    ("Huyện Kim Bôi", ["Xã Cuối Hạ", "Xã Mỵ Hòa", "Xã Nuông Dăm"], "Xã Dũng Tiến"),
    ("Huyện Kim Bôi", ["Xã Kim Lập", "Xã Nam Thượng", "Xã Sào Báy"], "Xã Hợp Kim"),
    ("Huyện Kim Bôi", ["Xã Xuân Thủy", "Xã Bình Sơn", "Xã Đú Sáng", "Xã Hùng Sơn"], "Xã Nật Sơn"),

    # Huyện Lạc Sơn (old Hòa Bình) - items 105-112
    ("Huyện Lạc Sơn", ["Thị trấn Vụ Bản", "Xã Hương Nhượng", "Xã Vũ Bình"], "Xã Lạc Sơn"),
    ("Huyện Lạc Sơn", ["Xã Tân Lập", "Xã Quý Hòa", "Xã Tuân Đạo"], "Xã Mường Vang"),
    ("Huyện Lạc Sơn", ["Xã Ân Nghĩa", "Xã Tân Mỹ", "Xã Yên Nghiệp"], "Xã Đại Đồng"),
    ("Huyện Lạc Sơn", ["Xã Ngọc Lâu", "Xã Tự Do", "Xã Ngọc Sơn"], "Xã Ngọc Sơn"),
    ("Huyện Lạc Sơn", ["Xã Mỹ Thành", "Xã Văn Nghĩa", "Xã Nhân Nghĩa"], "Xã Nhân Nghĩa"),
    ("Huyện Lạc Sơn", ["Xã Chí Đạo", "Xã Định Cư", "Xã Quyết Thắng"], "Xã Quyết Thắng"),
    ("Huyện Lạc Sơn", ["Xã Miền Đồi", "Xã Văn Sơn", "Xã Thượng Cốc"], "Xã Thượng Cốc"),
    ("Huyện Lạc Sơn", ["Xã Bình Hẻm", "Xã Xuất Hóa", "Xã Yên Phú"], "Xã Yên Phú"),

    # Huyện Lạc Thủy (old Hòa Bình) - items 113-115
    ("Huyện Lạc Thủy", ["Thị trấn Chi Nê", "Xã Đồng Tâm", "Xã Khoan Dụ", "Xã Yên Bồng"], "Xã Lạc Thủy"),
    ("Huyện Lạc Thủy", ["Xã Hưng Thi", "Xã Thống Nhất", "Xã An Bình"], "Xã An Bình"),
    ("Huyện Lạc Thủy", ["Thị trấn Ba Hàng Đồi", "Xã Phú Nghĩa", "Xã Phú Thành"], "Xã An Nghĩa"),

    # Huyện Lương Sơn (old Hòa Bình) - items 116-118
    ("Huyện Lương Sơn", ["Thị trấn Lương Sơn", "Xã Hòa Sơn", "Xã Lâm Sơn", "Xã Nhuận Trạch", "Xã Tân Vinh", "Xã Cao Sơn"], "Xã Lương Sơn"),
    ("Huyện Lương Sơn", ["Xã Thanh Cao", "Xã Thanh Sơn", "Xã Cao Dương"], "Xã Cao Dương"),
    ("Huyện Lương Sơn", ["Xã Cư Yên", "Xã Liên Sơn", "Xã Cao Sơn"], "Xã Liên Sơn"),

    # Huyện Mai Châu (old Hòa Bình) - items 119-123
    ("Huyện Mai Châu", ["Thị trấn Mai Châu", "Xã Nà Phòn", "Xã Thành Sơn", "Xã Tòng Đậu", "Xã Đồng Tân"], "Xã Mai Châu"),
    ("Huyện Mai Châu", ["Xã Mai Hịch", "Xã Xăm Khòe", "Xã Bao La"], "Xã Bao La"),
    ("Huyện Mai Châu", ["Xã Chiềng Châu", "Xã Vạn Mai", "Xã Mai Hạ"], "Xã Mai Hạ"),
    ("Huyện Mai Châu", ["Xã Cun Pheo", "Xã Hang Kia", "Xã Pà Cò", "Xã Đồng Tân"], "Xã Pà Cò"),
    ("Huyện Mai Châu", ["Xã Sơn Thủy", "Xã Tân Thành"], "Xã Tân Mai"),

    # Huyện Tân Lạc (old Hòa Bình) - items 124-128
    ("Huyện Tân Lạc", ["Thị trấn Mãn Đức", "Xã Ngọc Mỹ", "Xã Đông Lai", "Xã Thanh Hối", "Xã Tử Nê"], "Xã Tân Lạc"),
    ("Huyện Tân Lạc", ["Xã Mỹ Hòa", "Xã Phong Phú", "Xã Phú Cường"], "Xã Mường Bi"),
    ("Huyện Tân Lạc", ["Xã Phú Vinh", "Xã Suối Hoa"], "Xã Mường Hoa"),
    ("Huyện Tân Lạc", ["Xã Gia Mô", "Xã Lỗ Sơn", "Xã Nhân Mỹ"], "Xã Toàn Thắng"),
    ("Huyện Tân Lạc", ["Xã Ngổ Luông", "Xã Quyết Chiến", "Xã Vân Sơn"], "Xã Vân Sơn"),

    # Huyện Yên Thủy (old Hòa Bình) - items 129-131
    ("Huyện Yên Thủy", ["Thị trấn Hàng Trạm", "Xã Lạc Thịnh", "Xã Phú Lai"], "Xã Yên Thủy"),
    ("Huyện Yên Thủy", ["Xã Bảo Hiệu", "Xã Đa Phúc", "Xã Lạc Sỹ", "Xã Lạc Lương"], "Xã Lạc Lương"),
    ("Huyện Yên Thủy", ["Xã Đoàn Kết", "Xã Hữu Lợi", "Xã Ngọc Lương", "Xã Yên Trị"], "Xã Yên Trị"),

    # Thành phố Việt Trì - phường (old Phú Thọ) - items 132-135
    ("Thành phố Việt Trì", ["Phường Tân Dân", "Phường Gia Cẩm", "Phường Minh Nông", "Phường Dữu Lâu", "Xã Trưng Vương"], "Phường Việt Trì"),
    ("Thành phố Việt Trì", ["Phường Minh Phương", "Phường Nông Trang", "Xã Thụy Vân"], "Phường Nông Trang"),
    ("Thành phố Việt Trì", ["Phường Thọ Sơn", "Phường Tiên Cát", "Phường Bạch Hạc", "Phường Thanh Miếu", "Xã Sông Lô"], "Phường Thanh Miếu"),
    ("Thành phố Việt Trì", ["Phường Vân Phú", "Xã Phượng Lâu", "Xã Hùng Lô", "Xã Kim Đức"], "Phường Vân Phú"),

    # Thị xã Phú Thọ (old Phú Thọ) - items 136-138
    ("Thị xã Phú Thọ", ["Phường Hùng Vương", "Xã Văn Lung", "Xã Hà Lộc"], "Phường Phú Thọ"),
    ("Thị xã Phú Thọ", ["Phường Phong Châu", "Xã Phú Hộ", "Xã Hà Thạch"], "Phường Phong Châu"),
    ("Thị xã Phú Thọ", ["Phường Thanh Vinh", "Phường Âu Cơ", "Xã Thanh Minh"], "Phường Âu Cơ"),

    # Thành phố Vĩnh Yên (old Vĩnh Phúc) - items 139-140
    ("Thành phố Vĩnh Yên", ["Phường Định Trung", "Phường Liên Bảo", "Phường Khai Quang", "Phường Ngô Quyền", "Phường Đống Đa"], "Phường Vĩnh Phúc"),
    ("Thành phố Vĩnh Yên", ["Phường Tích Sơn", "Phường Hội Hợp", "Phường Đồng Tâm", "Xã Thanh Trù"], "Phường Vĩnh Yên"),

    # Thành phố Phúc Yên (old Vĩnh Phúc) - items 141-142
    ("Thành phố Phúc Yên", ["Phường Hùng Vương", "Phường Hai Bà Trưng", "Phường Phúc Thắng", "Phường Tiền Châu", "Phường Nam Viêm"], "Phường Phúc Yên"),
    ("Thành phố Phúc Yên", ["Phường Đồng Xuân", "Phường Xuân Hòa", "Xã Cao Minh", "Xã Ngọc Thanh"], "Phường Xuân Hòa"),

    # Thành phố Hòa Bình (old Hòa Bình) - items 143-146
    ("Thành phố Hòa Bình", ["Phường Đồng Tiến", "Phường Hữu Nghị", "Phường Phương Lâm", "Phường Quỳnh Lâm", "Phường Tân Thịnh", "Phường Thịnh Lang", "Phường Trung Minh"], "Phường Hòa Bình"),
    ("Thành phố Hòa Bình", ["Phường Kỳ Sơn", "Xã Độc Lập", "Xã Mông Hóa"], "Phường Kỳ Sơn"),
    ("Thành phố Hòa Bình", ["Phường Tân Hòa", "Xã Hòa Bình", "Xã Yên Mông"], "Phường Tân Hòa"),
    ("Thành phố Hòa Bình", ["Phường Dân Chủ", "Phường Thái Bình", "Phường Thống Nhất", "Xã Vầy Nưa"], "Phường Thống Nhất"),
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

    # Process Phú Thọ
    province_name = "Tỉnh Phú Thọ"
    province_dia_danh, province_chuyen_doi = generate_province_data(
        province_name, phutho_restructuring_data
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
    print("\nFinal totals:")
    print(f"  - dia_danh provinces: {len(dia_danh)}")
    print(f"  - chuyen_doi mappings: {len(chuyen_doi)}")

if __name__ == "__main__":
    main()

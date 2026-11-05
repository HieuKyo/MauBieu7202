#!/usr/bin/env python3
"""
Script to generate administrative restructuring data for multiple provinces
for dia_danh.json and chuyen_doi.json

Provinces covered:
1. An Giang (mới) - combines An Giang + Kiên Giang
2. Cần Thơ (mới) - combines Cần Thơ + Hậu Giang + Sóc Trăng
3. Cao Bằng
4. Đà Nẵng (mới) - combines Đà Nẵng + Quảng Nam
5. Đắk Lắk (mới) - combines Đắk Lắk + Phú Yên
"""

import json

# Base path for data files
DATA_PATH = '/home/user/MauBieu7202/templates_app/static/data'

# =============================================================================
# CẦN THƠ (MỚI) - 95 restructuring items
# Combines Cần Thơ + Hậu Giang + Sóc Trăng
# =============================================================================

cantho_restructuring_data = [
    # Quận Ninh Kiều (Cần Thơ) - items 1-4
    ("Quận Ninh Kiều", ["Phường Tân An", "Phường Thới Bình", "Phường Xuân Khánh"], "Phường Ninh Kiều"),
    ("Quận Ninh Kiều", ["Phường An Hòa", "Phường Cái Khế", "Phường Bùi Hữu Nghĩa"], "Phường Cái Khế"),
    ("Quận Ninh Kiều", ["Phường An Khánh", "Phường Hưng Lợi"], "Phường Tân An"),
    ("Quận Ninh Kiều", ["Phường An Bình", "Xã Mỹ Khánh", "Phường Long Tuyền"], "Phường An Bình"),

    # Quận Bình Thủy (Cần Thơ) - items 5-7
    ("Quận Bình Thủy", ["Phường Trà An", "Phường Trà Nóc", "Phường Thới An Đông"], "Phường Thới An Đông"),
    ("Quận Bình Thủy", ["Phường An Thới", "Phường Bình Thủy", "Phường Bùi Hữu Nghĩa"], "Phường Bình Thủy"),
    ("Quận Bình Thủy", ["Phường Long Hòa", "Phường Long Tuyền"], "Phường Long Tuyền"),

    # Quận Cái Răng (Cần Thơ) - items 8-9
    ("Quận Cái Răng", ["Phường Lê Bình", "Phường Thường Thạnh", "Phường Ba Láng", "Phường Hưng Thạnh"], "Phường Cái Răng"),
    ("Quận Cái Răng", ["Phường Tân Phú", "Phường Phú Thứ", "Phường Hưng Phú"], "Phường Hưng Phú"),

    # Quận Ô Môn (Cần Thơ) - items 10-12
    ("Quận Ô Môn", ["Phường Châu Văn Liêm", "Phường Thới Hòa", "Phường Thới An", "Xã Thới Thạnh"], "Phường Ô Môn"),
    ("Quận Ô Môn", ["Phường Trường Lạc", "Phường Phước Thới"], "Phường Phước Thới"),
    ("Quận Ô Môn", ["Phường Long Hưng", "Phường Tân Hưng", "Phường Thới Long"], "Phường Thới Long"),

    # Quận Thốt Nốt (Cần Thơ) - items 13-15
    ("Quận Thốt Nốt", ["Phường Thạnh Hòa", "Phường Trung Nhứt", "Xã Trung An"], "Phường Trung Nhứt"),
    ("Quận Thốt Nốt", ["Phường Trung Kiên", "Phường Thuận Hưng", "Phường Thốt Nốt"], "Phường Thuận Hưng"),
    ("Quận Thốt Nốt", ["Phường Thuận An", "Phường Thới Thuận", "Phường Thốt Nốt"], "Phường Thốt Nốt"),

    # TP Vị Thanh (Hậu Giang) - items 16-18
    ("Thành phố Vị Thanh", ["Phường I", "Phường III", "Phường VII"], "Phường Vị Thanh"),
    ("Thành phố Vị Thanh", ["Phường IV", "Phường V", "Xã Vị Tân"], "Phường Vị Tân"),
    ("Thành phố Vị Thanh", ["Phường Bình Thạnh", "Phường Vĩnh Tường", "Xã Long Bình"], "Phường Long Bình"),

    # TX Long Mỹ (Hậu Giang) - items 19-21
    ("Thị xã Long Mỹ", ["Phường Thuận An", "Xã Long Trị", "Xã Long Trị A"], "Phường Long Mỹ"),
    ("Thị xã Long Mỹ", ["Phường Trà Lồng", "Xã Tân Phú", "Xã Long Phú"], "Phường Long Phú 1"),
    ("Thị xã Long Mỹ", ["Phường Hiệp Lợi", "Xã Tân Thành", "Xã Đại Thành"], "Phường Đại Thành"),

    # TX Ngã Bảy (Hậu Giang) - item 22
    ("Thị xã Ngã Bảy", ["Phường Lái Hiếu", "Phường Hiệp Thành", "Phường Ngã Bảy"], "Phường Ngã Bảy"),

    # TP Sóc Trăng - items 23-26
    ("Thành phố Sóc Trăng", ["Phường 1", "Phường 2", "Phường 3", "Phường 4"], "Phường Phú Lợi"),
    ("Thành phố Sóc Trăng", ["Phường 5", "Phường 6", "Phường 7", "Phường 8"], "Phường Sóc Trăng"),
    ("Thành phố Sóc Trăng", ["Phường 10", "Thị trấn Mỹ Xuyên", "Xã Đại Tâm"], "Phường Mỹ Xuyên"),
    ("Thành phố Sóc Trăng", ["Phường Vĩnh Phước", "Xã Vĩnh Tân"], "Phường Vĩnh Phước"),

    # TX Vĩnh Châu (Sóc Trăng) - items 27-28
    ("Thị xã Vĩnh Châu", ["Phường 1", "Phường 2", "Xã Lạc Hòa"], "Phường Vĩnh Châu"),
    ("Thị xã Vĩnh Châu", ["Phường Khánh Hòa", "Xã Vĩnh Hiệp", "Xã Hòa Đông"], "Phường Khánh Hòa"),

    # TX Ngã Năm (Sóc Trăng) - items 29-30
    ("Thị xã Ngã Năm", ["Phường 1", "Phường 2", "Xã Vĩnh Quới"], "Phường Ngã Năm"),
    ("Thị xã Ngã Năm", ["Phường 3", "Xã Mỹ Bình", "Xã Mỹ Quới"], "Phường Mỹ Quới"),

    # Huyện Phong Điền (Cần Thơ) - items 31-32
    ("Huyện Phong Điền", ["Thị trấn Phong Điền", "Xã Tân Thới", "Xã Giai Xuân"], "Xã Phong Điền"),
    ("Huyện Phong Điền", ["Xã Nhơn Nghĩa", "Xã Nhơn Ái"], "Xã Nhơn Ái"),

    # Huyện Thới Lai (Cần Thơ) - items 33-36
    ("Huyện Thới Lai", ["Thị trấn Thới Lai", "Xã Thới Tân", "Xã Trường Thắng"], "Xã Thới Lai"),
    ("Huyện Thới Lai", ["Xã Đông Bình", "Xã Đông Thuận"], "Xã Đông Thuận"),
    ("Huyện Thới Lai", ["Xã Trường Xuân A", "Xã Trường Xuân B", "Xã Trường Xuân"], "Xã Trường Xuân"),
    ("Huyện Thới Lai", ["Xã Tân Thạnh", "Xã Định Môn", "Xã Trường Thành"], "Xã Trường Thành"),

    # Huyện Cờ Đỏ (Cần Thơ) - items 37-39
    ("Huyện Cờ Đỏ", ["Thị trấn Cờ Đỏ", "Xã Thới Đông", "Xã Thới Xuân"], "Xã Cờ Đỏ"),
    ("Huyện Cờ Đỏ", ["Xã Đông Thắng", "Xã Xuân Thắng", "Xã Đông Hiệp"], "Xã Đông Hiệp"),
    ("Huyện Cờ Đỏ", ["Xã Trung Thạnh", "Xã Trung Hưng"], "Xã Trung Hưng"),

    # Huyện Vĩnh Thạnh (Cần Thơ) - items 40-43
    ("Huyện Vĩnh Thạnh", ["Thị trấn Vĩnh Thạnh", "Xã Thạnh Lộc", "Xã Thạnh Mỹ"], "Xã Vĩnh Thạnh"),
    ("Huyện Vĩnh Thạnh", ["Xã Vĩnh Bình", "Xã Vĩnh Trinh"], "Xã Vĩnh Trinh"),
    ("Huyện Vĩnh Thạnh", ["Thị trấn Thạnh An", "Xã Thạnh Lợi", "Xã Thạnh Thắng"], "Xã Thạnh An"),
    ("Huyện Vĩnh Thạnh", ["Xã Thạnh Tiến", "Xã Thạnh An", "Xã Thạnh Quới"], "Xã Thạnh Quới"),

    # Huyện Vị Thủy (Hậu Giang) - items 44-48
    ("Huyện Vị Thủy", ["Xã Tân Tiến", "Xã Hỏa Tiến", "Xã Hỏa Lựu"], "Xã Hỏa Lựu"),
    ("Huyện Vị Thủy", ["Thị trấn Nàng Mau", "Xã Vị Thắng", "Xã Vị Trung"], "Xã Vị Thủy"),
    ("Huyện Vị Thủy", ["Xã Vĩnh Thuận Tây", "Xã Vị Thủy", "Xã Vĩnh Thuận Đông"], "Xã Vĩnh Thuận Đông"),
    ("Huyện Vị Thủy", ["Xã Vị Đông", "Xã Vị Bình", "Xã Vị Thanh"], "Xã Vị Thanh 1"),
    ("Huyện Vị Thủy", ["Xã Vĩnh Trung", "Xã Vĩnh Tường"], "Xã Vĩnh Tường"),

    # Huyện Long Mỹ (Hậu Giang) - items 49-54
    ("Huyện Long Mỹ", ["Thị trấn Vĩnh Viễn", "Xã Vĩnh Viễn A"], "Xã Vĩnh Viễn"),
    ("Huyện Long Mỹ", ["Xã Thuận Hòa", "Xã Thuận Hưng", "Xã Xà Phiên"], "Xã Xà Phiên"),
    ("Huyện Long Mỹ", ["Xã Lương Nghĩa", "Xã Lương Tâm"], "Xã Lương Tâm"),
    ("Huyện Long Mỹ", ["Thị trấn Rạch Gòi", "Xã Tân Phú Thạnh", "Xã Thạnh Xuân"], "Xã Thạnh Xuân"),
    ("Huyện Long Mỹ", ["Thị trấn Một Ngàn", "Thị trấn Bảy Ngàn", "Xã Nhơn Nghĩa A", "Xã Tân Hòa"], "Xã Tân Hòa"),
    ("Huyện Long Mỹ", ["Xã Trường Long A", "Xã Trường Long Tây"], "Xã Trường Long Tây"),

    # Huyện Châu Thành A (Hậu Giang) - items 55-58
    ("Huyện Châu Thành A", ["Thị trấn Mái Dầm", "Thị trấn Ngã Sáu", "Xã Đông Phú"], "Xã Châu Thành"),
    ("Huyện Châu Thành A", ["Thị trấn Cái Tắc", "Xã Đông Thạnh", "Xã Đông Phước A"], "Xã Đông Phước"),
    ("Huyện Châu Thành A", ["Xã Phú Tân", "Xã Đông Phước", "Xã Phú Hữu"], "Xã Phú Hữu"),
    ("Huyện Châu Thành A", ["Xã Bình Thành", "Xã Tân Bình"], "Xã Tân Bình"),

    # Huyện Phụng Hiệp (Hậu Giang) - items 59-64
    ("Huyện Phụng Hiệp", ["Thị trấn Kinh Cùng", "Xã Hòa An"], "Xã Hòa An"),
    ("Huyện Phụng Hiệp", ["Xã Phương Phú", "Xã Phương Bình"], "Xã Phương Bình"),
    ("Huyện Phụng Hiệp", ["Thị trấn Búng Tàu", "Xã Tân Phước Hưng"], "Xã Tân Phước Hưng"),
    ("Huyện Phụng Hiệp", ["Thị trấn Cây Dương", "Xã Hiệp Hưng"], "Xã Hiệp Hưng"),
    ("Huyện Phụng Hiệp", ["Xã Hòa Mỹ", "Xã Phụng Hiệp"], "Xã Phụng Hiệp"),
    ("Huyện Phụng Hiệp", ["Xã Long Thạnh", "Xã Tân Long", "Xã Thạnh Hòa"], "Xã Thạnh Hòa"),

    # Huyện Mỹ Xuyên (Sóc Trăng) - items 65-69
    ("Huyện Mỹ Xuyên", ["Xã Hòa Tú 1", "Xã Hòa Tú 2"], "Xã Hòa Tú"),
    ("Huyện Mỹ Xuyên", ["Xã Thạnh Quới", "Xã Gia Hòa 2"], "Xã Gia Hòa"),
    ("Huyện Mỹ Xuyên", ["Xã Thạnh Phú", "Xã Gia Hòa 1"], "Xã Nhu Gia"),
    ("Huyện Mỹ Xuyên", ["Xã Tham Đôn", "Xã Ngọc Đông", "Xã Ngọc Tố"], "Xã Ngọc Tố"),
    ("Huyện Mỹ Xuyên", ["Xã Hậu Thạnh", "Xã Phú Hữu", "Xã Trường Khánh"], "Xã Trường Khánh"),

    # Huyện Long Phú (Sóc Trăng) - items 70-73
    ("Huyện Long Phú", ["Thị trấn Đại Ngãi", "Xã Long Đức"], "Xã Đại Ngãi"),
    ("Huyện Long Phú", ["Xã Tân Hưng", "Xã Châu Khánh", "Xã Tân Thạnh"], "Xã Tân Thạnh"),
    ("Huyện Long Phú", ["Thị trấn Long Phú", "Xã Long Phú"], "Xã Long Phú"),
    ("Huyện Long Phú", ["Xã An Mỹ", "Xã Song Phụng", "Xã Nhơn Mỹ"], "Xã Nhơn Mỹ"),

    # Huyện Kế Sách (Sóc Trăng) - items 74-77
    ("Huyện Kế Sách", ["Thị trấn An Lạc Thôn", "Xã Xuân Hòa", "Xã Trinh Phú"], "Xã An Lạc Thôn"),
    ("Huyện Kế Sách", ["Thị trấn Kế Sách", "Xã Kế An", "Xã Kế Thành"], "Xã Kế Sách"),
    ("Huyện Kế Sách", ["Xã An Lạc Tây", "Xã Thới An Hội"], "Xã Thới An Hội"),
    ("Huyện Kế Sách", ["Xã Ba Trinh", "Xã Đại Hải"], "Xã Đại Hải"),

    # Huyện Châu Thành (Sóc Trăng) - items 78-81
    ("Huyện Châu Thành ST", ["Thị trấn Châu Thành", "Xã Phú Tâm"], "Xã Phú Tâm"),
    ("Huyện Châu Thành ST", ["Xã An Hiệp", "Xã An Ninh"], "Xã An Ninh"),
    ("Huyện Châu Thành ST", ["Xã Thuận Hòa", "Xã Phú Tân"], "Xã Thuận Hòa"),
    ("Huyện Châu Thành ST", ["Xã Thiện Mỹ", "Xã Hồ Đắc Kiện"], "Xã Hồ Đắc Kiện"),

    # Huyện Mỹ Tú (Sóc Trăng) - items 82-85
    ("Huyện Mỹ Tú", ["Thị trấn Huỳnh Hữu Nghĩa", "Xã Mỹ Thuận", "Xã Mỹ Tú"], "Xã Mỹ Tú"),
    ("Huyện Mỹ Tú", ["Xã Hưng Phú", "Xã Long Hưng"], "Xã Long Hưng"),
    ("Huyện Mỹ Tú", ["Xã Thuận Hưng", "Xã Phú Mỹ", "Xã Mỹ Hương"], "Xã Mỹ Hương"),
    ("Huyện Mỹ Tú", ["Xã Thạnh Tân", "Xã Long Bình", "Xã Tân Long"], "Xã Tân Long"),

    # Huyện Thạnh Trị (Sóc Trăng) - items 86-89
    ("Huyện Thạnh Trị", ["Thị trấn Hưng Lợi", "Thị trấn Phú Lộc", "Xã Thạnh Trị"], "Xã Phú Lộc"),
    ("Huyện Thạnh Trị", ["Xã Châu Hưng", "Xã Vĩnh Thành", "Xã Vĩnh Lợi"], "Xã Vĩnh Lợi"),
    ("Huyện Thạnh Trị", ["Xã Tuân Tức", "Xã Lâm Kiết", "Xã Lâm Tân"], "Xã Lâm Tân"),
    ("Huyện Thạnh Trị", ["Xã Thạnh Thới Thuận", "Xã Thạnh Thới An"], "Xã Thạnh Thới An"),

    # Huyện Trần Đề (Sóc Trăng) - items 90-93
    ("Huyện Trần Đề", ["Xã Viên An", "Xã Tài Văn"], "Xã Tài Văn"),
    ("Huyện Trần Đề", ["Xã Viên Bình", "Xã Liêu Tú"], "Xã Liêu Tú"),
    ("Huyện Trần Đề", ["Thị trấn Lịch Hội Thượng", "Xã Lịch Hội Thượng"], "Xã Lịch Hội Thượng"),
    ("Huyện Trần Đề", ["Thị trấn Trần Đề", "Xã Đại Ân 2", "Xã Trung Bình"], "Xã Trần Đề"),

    # Huyện Cù Lao Dung (Sóc Trăng) - items 94-95
    ("Huyện Cù Lao Dung", ["Thị trấn Cù Lao Dung", "Xã An Thạnh 1", "Xã An Thạnh Tây", "Xã An Thạnh Đông"], "Xã An Thạnh"),
    ("Huyện Cù Lao Dung", ["Xã An Thạnh 2", "Xã Đại Ân 1", "Xã An Thạnh 3", "Xã An Thạnh Nam"], "Xã Cù Lao Dung"),
]


# =============================================================================
# CAO BẰNG - 56 restructuring items
# =============================================================================

caobang_restructuring_data = [
    # Huyện Bảo Lâm - items 1-6
    ("Huyện Bảo Lâm", ["Xã Thạch Lâm", "Xã Quảng Lâm"], "Xã Quảng Lâm"),
    ("Huyện Bảo Lâm", ["Xã Nam Cao", "Xã Nam Quang"], "Xã Nam Quang"),
    ("Huyện Bảo Lâm", ["Xã Vĩnh Quang", "Xã Lý Bôn"], "Xã Lý Bôn"),
    ("Huyện Bảo Lâm", ["Thị trấn Pác Miầu", "Xã Mông Ân", "Xã Vĩnh Phong"], "Xã Bảo Lâm"),
    ("Huyện Bảo Lâm", ["Xã Thái Học", "Xã Thái Sơn", "Xã Yên Thổ"], "Xã Yên Thổ"),
    ("Huyện Bảo Lâm", ["Xã Sơn Lập", "Xã Sơn Lộ"], "Xã Sơn Lộ"),

    # Huyện Bảo Lạc - items 7-14
    ("Huyện Bảo Lạc", ["Xã Hưng Thịnh", "Xã Kim Cúc", "Xã Hưng Đạo"], "Xã Hưng Đạo"),
    ("Huyện Bảo Lạc", ["Thị trấn Bảo Lạc", "Xã Bảo Toàn", "Xã Hồng Trị"], "Xã Bảo Lạc"),
    ("Huyện Bảo Lạc", ["Xã Đức Hạnh", "Xã Cốc Pàng"], "Xã Cốc Pàng"),
    ("Huyện Bảo Lạc", ["Xã Thượng Hà", "Xã Cô Ba"], "Xã Cô Ba"),
    ("Huyện Bảo Lạc", ["Xã Phan Thanh", "Xã Khánh Xuân"], "Xã Khánh Xuân"),
    ("Huyện Bảo Lạc", ["Xã Hồng An", "Xã Xuân Trường"], "Xã Xuân Trường"),
    ("Huyện Bảo Lạc", ["Xã Đình Phùng", "Xã Huy Giáp"], "Xã Huy Giáp"),
    ("Huyện Bảo Lạc", ["Xã Yên Lạc", "Xã Ca Thành"], "Xã Ca Thành"),

    # Huyện Nguyên Bình - items 15-20
    ("Huyện Nguyên Bình", ["Xã Phan Thanh", "Xã Mai Long"], "Xã Phan Thanh"),
    ("Huyện Nguyên Bình", ["Xã Quang Thành", "Xã Thành Công"], "Xã Thành Công"),
    ("Huyện Nguyên Bình", ["Xã Hưng Đạo", "Xã Hoa Thám", "Xã Tam Kim"], "Xã Tam Kim"),
    ("Huyện Nguyên Bình", ["Thị trấn Nguyên Bình", "Xã Thể Dục", "Xã Vũ Minh"], "Xã Nguyên Bình"),
    ("Huyện Nguyên Bình", ["Thị trấn Tĩnh Túc", "Xã Triệu Nguyên", "Xã Vũ Nông"], "Xã Tĩnh Túc"),
    ("Huyện Nguyên Bình", ["Xã Trương Lương", "Xã Minh Tâm"], "Xã Minh Tâm"),

    # Huyện Hà Quảng - items 21-27
    ("Huyện Hà Quảng", ["Xã Ngọc Động", "Xã Yên Sơn", "Xã Thanh Long"], "Xã Thanh Long"),
    ("Huyện Hà Quảng", ["Xã Cần Nông", "Xã Lương Thông", "Xã Cần Yên"], "Xã Cần Yên"),
    ("Huyện Hà Quảng", ["Thị trấn Thông Nông", "Xã Đa Thông", "Xã Lương Can"], "Xã Thông Nông"),
    ("Huyện Hà Quảng", ["Thị trấn Xuân Hòa", "Xã Quý Quân", "Xã Sóc Hà", "Xã Trường Hà"], "Xã Trường Hà"),
    ("Huyện Hà Quảng", ["Xã Hồng Sỹ", "Xã Ngọc Đào", "Xã Mã Ba"], "Xã Hà Quảng"),
    ("Huyện Hà Quảng", ["Xã Thượng Thôn", "Xã Lũng Nặm"], "Xã Lũng Nặm"),
    ("Huyện Hà Quảng", ["Xã Nội Thôn", "Xã Cải Viên", "Xã Tổng Cọt"], "Xã Tổng Cọt"),

    # Huyện Hòa An - items 28-34
    ("Huyện Hòa An", ["Xã Đức Long", "Xã Dân Chủ", "Xã Nam Tuấn"], "Xã Nam Tuấn"),
    ("Huyện Hòa An", ["Thị trấn Nước Hai", "Xã Đại Tiến", "Xã Hồng Việt"], "Xã Hòa An"),
    ("Huyện Hòa An", ["Xã Thịnh Vượng", "Xã Bình Dương", "Xã Bạch Đằng"], "Xã Bạch Đằng"),
    ("Huyện Hòa An", ["Xã Quang Trung", "Xã Ngũ Lão", "Xã Nguyễn Huệ"], "Xã Nguyễn Huệ"),
    ("Huyện Hòa An", ["Xã Quang Trọng", "Xã Minh Khai"], "Xã Minh Khai"),
    ("Huyện Hòa An", ["Xã Đức Thông", "Xã Canh Tân"], "Xã Canh Tân"),
    ("Huyện Hòa An", ["Xã Hồng Nam", "Xã Thái Cường", "Xã Kim Đồng"], "Xã Kim Đồng"),

    # Huyện Thạch An - items 35-37
    ("Huyện Thạch An", ["Xã Tiên Thành", "Xã Vân Trình", "Xã Lê Lai"], "Xã Thạch An"),
    ("Huyện Thạch An", ["Thị trấn Đông Khê", "Xã Đức Xuân", "Xã Trọng Con"], "Xã Đông Khê"),
    ("Huyện Thạch An", ["Xã Đức Long", "Xã Thụy Hùng", "Xã Lê Lợi"], "Xã Đức Long"),

    # Huyện Quảng Hòa - items 38-44
    ("Huyện Quảng Hòa", ["Thị trấn Tà Lùng", "Thị trấn Hòa Thuận", "Xã Mỹ Hưng", "Xã Đại Sơn"], "Xã Phục Hòa"),
    ("Huyện Quảng Hòa", ["Xã Hồng Quang", "Xã Cách Linh", "Xã Bế Văn Đàn"], "Xã Bế Văn Đàn"),
    ("Huyện Quảng Hòa", ["Xã Quảng Hưng", "Xã Cai Bộ", "Xã Độc Lập"], "Xã Độc Lập"),
    ("Huyện Quảng Hòa", ["Thị trấn Quảng Uyên", "Xã Phi Hải", "Xã Phúc Sen", "Xã Chí Thảo"], "Xã Quảng Uyên"),
    ("Huyện Quảng Hòa", ["Xã Ngọc Động", "Xã Tự Do", "Xã Hạnh Phúc"], "Xã Hạnh Phúc"),
    ("Huyện Quảng Hòa", ["Xã Quang Vinh", "Xã Quang Hán"], "Xã Quang Hán"),
    ("Huyện Quảng Hòa", ["Thị trấn Trà Lĩnh", "Xã Cao Chương", "Xã Quốc Toản"], "Xã Trà Lĩnh"),

    # Huyện Trùng Khánh - items 45-49
    ("Huyện Trùng Khánh", ["Xã Quang Trung", "Xã Tri Phương", "Xã Xuân Nội"], "Xã Quang Trung"),
    ("Huyện Trùng Khánh", ["Xã Trung Phúc", "Xã Cao Thăng", "Xã Đoài Dương"], "Xã Đoài Dương"),
    ("Huyện Trùng Khánh", ["Thị trấn Trùng Khánh", "Xã Đức Hồng", "Xã Lăng Hiếu", "Xã Khâm Thành"], "Xã Trùng Khánh"),
    ("Huyện Trùng Khánh", ["Xã Chí Viễn", "Xã Phong Châu", "Xã Đàm Thủy"], "Xã Đàm Thủy"),
    ("Huyện Trùng Khánh", ["Xã Ngọc Côn", "Xã Ngọc Khê", "Xã Phong Nặm", "Xã Đình Phong"], "Xã Đình Phong"),

    # Huyện Hạ Lang - items 50-53
    ("Huyện Hạ Lang", ["Thị trấn Thanh Nhật", "Xã Thống Nhất", "Xã Thị Hoa"], "Xã Hạ Lang"),
    ("Huyện Hạ Lang", ["Xã Minh Long", "Xã Đồng Loan", "Xã Lý Quốc"], "Xã Lý Quốc"),
    ("Huyện Hạ Lang", ["Xã Cô Ngân", "Xã An Lạc", "Xã Kim Loan", "Xã Vinh Quý"], "Xã Vinh Quý"),
    ("Huyện Hạ Lang", ["Xã Đức Quang", "Xã Thắng Lợi", "Xã Quang Long"], "Xã Quang Long"),

    # TP Cao Bằng - items 54-56
    ("Thành phố Cao Bằng", ["Phường Sông Hiến", "Phường Đề Thám", "Phường Hợp Giang", "Xã Hưng Đạo", "Xã Hoàng Tung"], "Phường Thục Phán"),
    ("Thành phố Cao Bằng", ["Phường Ngọc Xuân", "Phường Sông Bằng", "Xã Vĩnh Quang"], "Phường Nùng Trí Cao"),
    ("Thành phố Cao Bằng", ["Phường Tân Giang", "Phường Duyệt Trung", "Phường Hòa Chung", "Xã Chu Trinh", "Xã Lê Chung"], "Phường Tân Giang"),
]


# =============================================================================
# ĐÀ NẴNG (MỚI) - 92 restructuring items
# Combines Đà Nẵng + Quảng Nam
# =============================================================================

danang_restructuring_data = [
    # Quận Hải Châu - items 1-2
    ("Quận Hải Châu", ["Phường Thanh Bình", "Phường Thuận Phước", "Phường Thạch Thang", "Phường Phước Ninh", "Phường Hải Châu"], "Phường Hải Châu"),
    ("Quận Hải Châu", ["Phường Bình Thuận", "Phường Hòa Thuận Tây", "Phường Hòa Cường Bắc", "Phường Hòa Cường Nam"], "Phường Hòa Cường"),

    # Quận Thanh Khê - item 3
    ("Quận Thanh Khê", ["Phường Xuân Hà", "Phường Chính Gián", "Phường Thạc Gián", "Phường Thanh Khê Tây", "Phường Thanh Khê Đông"], "Phường Thanh Khê"),

    # Quận Cẩm Lệ - items 4, 11-12
    ("Quận Cẩm Lệ", ["Phường Hòa An", "Phường Hòa Phát", "Phường An Khê"], "Phường An Khê"),
    ("Quận Cẩm Lệ", ["Phường Hòa Thọ Tây", "Phường Hòa Thọ Đông", "Phường Khuê Trung"], "Phường Cẩm Lệ"),
    ("Quận Cẩm Lệ", ["Phường Hòa Xuân", "Xã Hòa Châu", "Xã Hòa Phước"], "Phường Hòa Xuân"),

    # Quận Sơn Trà - items 5-6
    ("Quận Sơn Trà", ["Phường Phước Mỹ", "Phường An Hải Bắc", "Phường An Hải Nam"], "Phường An Hải"),
    ("Quận Sơn Trà", ["Phường Thọ Quang", "Phường Nại Hiên Đông", "Phường Mân Thái"], "Phường Sơn Trà"),

    # Quận Ngũ Hành Sơn - item 7
    ("Quận Ngũ Hành Sơn", ["Phường Mỹ An", "Phường Khuê Mỹ", "Phường Hòa Hải", "Phường Hòa Quý"], "Phường Ngũ Hành Sơn"),

    # Quận Liên Chiểu - items 8-10
    ("Quận Liên Chiểu", ["Phường Hòa Khánh Nam", "Phường Hòa Minh", "Xã Hòa Sơn"], "Phường Hòa Khánh"),
    ("Quận Liên Chiểu", ["Phường Hòa Hiệp Bắc", "Phường Hòa Hiệp Nam", "Xã Hòa Bắc", "Xã Hòa Liên"], "Phường Hải Vân"),
    ("Quận Liên Chiểu", ["Phường Hòa Khánh Bắc", "Xã Hòa Liên"], "Phường Liên Chiểu"),

    # Thành phố Tam Kỳ (Quảng Nam) - items 13-16
    ("Thành phố Tam Kỳ", ["Phường An Mỹ", "Phường An Xuân", "Phường Trường Xuân"], "Phường Tam Kỳ"),
    ("Thành phố Tam Kỳ", ["Phường An Phú", "Xã Tam Thanh", "Xã Tam Phú"], "Phường Quảng Phú"),
    ("Thành phố Tam Kỳ", ["Phường An Sơn", "Phường Hòa Hương", "Xã Tam Ngọc"], "Phường Hương Trà"),
    ("Thành phố Tam Kỳ", ["Phường Tân Thạnh", "Phường Hòa Thuận", "Xã Tam Thăng"], "Phường Bàn Thạch"),

    # Thị xã Điện Bàn (Quảng Nam) - items 17-20, 64-65
    ("Thị xã Điện Bàn", ["Phường Điện Phương", "Phường Điện Minh", "Phường Vĩnh Điện"], "Phường Điện Bàn"),
    ("Thị xã Điện Bàn", ["Phường Điện Nam Đông", "Phường Điện Nam Trung", "Phường Điện Dương", "Phường Điện Ngọc", "Phường Điện Nam Bắc"], "Phường Điện Bàn Đông"),
    ("Thị xã Điện Bàn", ["Phường Điện An", "Phường Điện Thắng Nam", "Phường Điện Thắng Trung"], "Phường An Thắng"),
    ("Thị xã Điện Bàn", ["Phường Điện Thắng Bắc", "Xã Điện Hòa", "Xã Điện Tiến"], "Phường Điện Bàn Bắc"),
    ("Thị xã Điện Bàn", ["Xã Điện Hồng", "Xã Điện Thọ", "Xã Điện Phước"], "Xã Điện Bàn Tây"),
    ("Thị xã Điện Bàn", ["Xã Điện Phong", "Xã Điện Trung", "Xã Điện Quang"], "Xã Gò Nổi"),

    # Thành phố Hội An (Quảng Nam) - items 21-23
    ("Thành phố Hội An", ["Phường Minh An", "Phường Cẩm Phô", "Phường Sơn Phong", "Phường Cẩm Nam", "Xã Cẩm Kim"], "Phường Hội An"),
    ("Thành phố Hội An", ["Phường Cẩm Châu", "Phường Cửa Đại", "Xã Cẩm Thanh"], "Phường Hội An Đông"),
    ("Thành phố Hội An", ["Phường Thanh Hà", "Phường Tân An", "Phường Cẩm An", "Xã Cẩm Hà"], "Phường Hội An Tây"),

    # Huyện Hòa Vang (Đà Nẵng) - items 24-26
    ("Huyện Hòa Vang", ["Xã Hòa Phong", "Xã Hòa Phú"], "Xã Hòa Vang"),
    ("Huyện Hòa Vang", ["Xã Hòa Khương", "Xã Hòa Tiến"], "Xã Hòa Tiến"),
    ("Huyện Hòa Vang", ["Xã Hòa Ninh", "Xã Hòa Nhơn"], "Xã Bà Nà"),

    # Huyện Núi Thành (Quảng Nam) - items 27-31
    ("Huyện Núi Thành", ["Thị trấn Núi Thành", "Xã Tam Quang", "Xã Tam Nghĩa", "Xã Tam Hiệp", "Xã Tam Giang"], "Xã Núi Thành"),
    ("Huyện Núi Thành", ["Xã Tam Mỹ Đông", "Xã Tam Mỹ Tây", "Xã Tam Trà"], "Xã Tam Mỹ"),
    ("Huyện Núi Thành", ["Xã Tam Hòa", "Xã Tam Anh Bắc", "Xã Tam Anh Nam"], "Xã Tam Anh"),
    ("Huyện Núi Thành", ["Xã Tam Sơn", "Xã Tam Thạnh"], "Xã Đức Phú"),
    ("Huyện Núi Thành", ["Xã Tam Xuân I", "Xã Tam Xuân II", "Xã Tam Tiến"], "Xã Tam Xuân"),

    # Huyện Phú Ninh (Quảng Nam) - items 32-34
    ("Huyện Phú Ninh", ["Xã Tam An", "Xã Tam Thành", "Xã Tam Phước", "Xã Tam Lộc"], "Xã Tây Hồ"),
    ("Huyện Phú Ninh", ["Thị trấn Phú Thịnh", "Xã Tam Đàn", "Xã Tam Thái"], "Xã Chiên Đàn"),
    ("Huyện Phú Ninh", ["Xã Tam Dân", "Xã Tam Đại", "Xã Tam Lãnh"], "Xã Phú Ninh"),

    # Huyện Tiên Phước (Quảng Nam) - items 35-38
    ("Huyện Tiên Phước", ["Xã Tiên Lãnh", "Xã Tiên Ngọc", "Xã Tiên Hiệp"], "Xã Lãnh Ngọc"),
    ("Huyện Tiên Phước", ["Thị trấn Tiên Kỳ", "Xã Tiên Mỹ", "Xã Tiên Phong", "Xã Tiên Thọ"], "Xã Tiên Phước"),
    ("Huyện Tiên Phước", ["Xã Tiên Lập", "Xã Tiên Lộc", "Xã Tiên An", "Xã Tiên Cảnh"], "Xã Thạnh Bình"),
    ("Huyện Tiên Phước", ["Xã Tiên Sơn", "Xã Tiên Hà", "Xã Tiên Châu"], "Xã Sơn Cẩm Hà"),

    # Huyện Bắc Trà My (Quảng Nam) - items 39-43
    ("Huyện Bắc Trà My", ["Xã Trà Đông", "Xã Trà Nú", "Xã Trà Kót"], "Xã Trà Liên"),
    ("Huyện Bắc Trà My", ["Xã Trà Ka", "Xã Trà Giáp"], "Xã Trà Giáp"),
    ("Huyện Bắc Trà My", ["Xã Trà Giác", "Xã Trà Tân"], "Xã Trà Tân"),
    ("Huyện Bắc Trà My", ["Xã Trà Bui", "Xã Trà Đốc"], "Xã Trà Đốc"),
    ("Huyện Bắc Trà My", ["Thị trấn Trà My", "Xã Trà Sơn", "Xã Trà Giang", "Xã Trà Dương"], "Xã Trà My"),

    # Huyện Nam Trà My (Quảng Nam) - items 44-48
    ("Huyện Nam Trà My", ["Xã Trà Mai", "Xã Trà Don"], "Xã Nam Trà My"),
    ("Huyện Nam Trà My", ["Xã Trà Cang", "Xã Trà Tập"], "Xã Trà Tập"),
    ("Huyện Nam Trà My", ["Xã Trà Vinh", "Xã Trà Vân"], "Xã Trà Vân"),
    ("Huyện Nam Trà My", ["Xã Trà Nam", "Xã Trà Linh"], "Xã Trà Linh"),
    ("Huyện Nam Trà My", ["Xã Trà Dơn", "Xã Trà Leng"], "Xã Trà Leng"),

    # Huyện Thăng Bình (Quảng Nam) - items 49-54
    ("Huyện Thăng Bình", ["Thị trấn Hà Lam", "Xã Bình Nguyên", "Xã Bình Quý", "Xã Bình Phục"], "Xã Thăng Bình"),
    ("Huyện Thăng Bình", ["Xã Bình Triều", "Xã Bình Giang", "Xã Bình Đào", "Xã Bình Minh", "Xã Bình Dương"], "Xã Thăng An"),
    ("Huyện Thăng Bình", ["Xã Bình Nam", "Xã Bình Hải", "Xã Bình Sa"], "Xã Thăng Trường"),
    ("Huyện Thăng Bình", ["Xã Bình An", "Xã Bình Trung", "Xã Bình Tú"], "Xã Thăng Điền"),
    ("Huyện Thăng Bình", ["Xã Bình Phú", "Xã Bình Quế"], "Xã Thăng Phú"),
    ("Huyện Thăng Bình", ["Xã Bình Lãnh", "Xã Bình Trị", "Xã Bình Định"], "Xã Đồng Dương"),

    # Huyện Quế Sơn (Quảng Nam) - items 55-57
    ("Huyện Quế Sơn", ["Xã Quế Mỹ", "Xã Quế Hiệp", "Xã Quế Thuận", "Xã Quế Châu"], "Xã Quế Sơn Trung"),
    ("Huyện Quế Sơn", ["Thị trấn Đông Phú", "Xã Quế Minh", "Xã Quế An", "Xã Quế Long", "Xã Quế Phong"], "Xã Quế Sơn"),
    ("Huyện Quế Sơn", ["Thị trấn Hương An", "Xã Quế Xuân 1", "Xã Quế Xuân 2", "Xã Quế Phú"], "Xã Xuân Phú"),

    # Huyện Nông Sơn (Quảng Nam) - items 58-59
    ("Huyện Nông Sơn", ["Thị trấn Trung Phước", "Xã Quế Lộc"], "Xã Nông Sơn"),
    ("Huyện Nông Sơn", ["Xã Quế Lâm", "Xã Phước Ninh", "Xã Ninh Phước"], "Xã Quế Phước"),

    # Huyện Duy Xuyên (Quảng Nam) - items 60-63
    ("Huyện Duy Xuyên", ["Xã Duy Thành", "Xã Duy Hải", "Xã Duy Nghĩa"], "Xã Duy Nghĩa"),
    ("Huyện Duy Xuyên", ["Thị trấn Nam Phước", "Xã Duy Phước", "Xã Duy Vinh"], "Xã Nam Phước"),
    ("Huyện Duy Xuyên", ["Xã Duy Trung", "Xã Duy Sơn", "Xã Duy Trinh"], "Xã Duy Xuyên"),
    ("Huyện Duy Xuyên", ["Xã Duy Châu", "Xã Duy Hoà", "Xã Duy Phú", "Xã Duy Tân"], "Xã Thu Bồn"),

    # Huyện Đại Lộc (Quảng Nam) - items 66-70
    ("Huyện Đại Lộc", ["Thị trấn Ái Nghĩa", "Xã Đại Hiệp", "Xã Đại Hòa", "Xã Đại An", "Xã Đại Nghĩa"], "Xã Đại Lộc"),
    ("Huyện Đại Lộc", ["Xã Đại Đồng", "Xã Đại Hồng", "Xã Đại Quang"], "Xã Hà Nha"),
    ("Huyện Đại Lộc", ["Xã Đại Lãnh", "Xã Đại Hưng", "Xã Đại Sơn"], "Xã Thượng Đức"),
    ("Huyện Đại Lộc", ["Xã Đại Phong", "Xã Đại Minh", "Xã Đại Cường"], "Xã Vu Gia"),
    ("Huyện Đại Lộc", ["Xã Đại Tân", "Xã Đại Thắng", "Xã Đại Chánh", "Xã Đại Thạnh"], "Xã Phú Thuận"),

    # Huyện Nam Giang (Quảng Nam) - items 71-76
    ("Huyện Nam Giang", ["Thị trấn Thạnh Mỹ"], "Xã Thạnh Mỹ"),
    ("Huyện Nam Giang", ["Xã Cà Dy", "Xã Tà Bhing", "Xã Tà Pơơ"], "Xã Bến Giằng"),
    ("Huyện Nam Giang", ["Xã Zuôih", "Xã Chà Vàl"], "Xã Nam Giang"),
    ("Huyện Nam Giang", ["Xã Đắc Pre", "Xã Đắc Pring"], "Xã Đắc Pring"),
    ("Huyện Nam Giang", ["Xã Đắc Tôi", "Xã La Dêê"], "Xã La Dêê"),
    ("Huyện Nam Giang", ["Xã Chơ Chun", "Xã La Êê"], "Xã La Êê"),

    # Huyện Đông Giang (Quảng Nam) - items 77-81
    ("Huyện Đông Giang", ["Xã Tư", "Xã Ba"], "Xã Sông Vàng"),
    ("Huyện Đông Giang", ["Xã A Ting", "Xã Jơ Ngây", "Xã Sông Kôn"], "Xã Sông Kôn"),
    ("Huyện Đông Giang", ["Thị trấn Prao", "Xã Tà Lu", "Xã A Rooi", "Xã Zà Hung"], "Xã Đông Giang"),
    ("Huyện Đông Giang", ["Xã Kà Dăng", "Xã Mà Cooih"], "Xã Bến Hiên"),
    ("Huyện Đông Giang", ["Xã Bhalêê", "Xã Avương"], "Xã Avương"),

    # Huyện Tây Giang (Quảng Nam) - items 82-83
    ("Huyện Tây Giang", ["Xã Atiêng", "Xã Dang", "Xã Anông", "Xã Lăng"], "Xã Tây Giang"),
    ("Huyện Tây Giang", ["Xã Ch'ơm", "Xã Gari", "Xã Tr'hy", "Xã Axan"], "Xã Hùng Sơn"),

    # Huyện Hiệp Đức (Quảng Nam) - items 84-86
    ("Huyện Hiệp Đức", ["Thị trấn Tân Bình", "Xã Quế Tân", "Xã Quế Lưu"], "Xã Hiệp Đức"),
    ("Huyện Hiệp Đức", ["Xã Thăng Phước", "Xã Bình Sơn", "Xã Quế Thọ", "Xã Bình Lâm"], "Xã Việt An"),
    ("Huyện Hiệp Đức", ["Xã Sông Trà", "Xã Phước Gia", "Xã Phước Trà"], "Xã Phước Trà"),

    # Huyện Phước Sơn (Quảng Nam) - items 87-91
    ("Huyện Phước Sơn", ["Thị trấn Khâm Đức", "Xã Phước Xuân"], "Xã Khâm Đức"),
    ("Huyện Phước Sơn", ["Xã Phước Đức", "Xã Phước Mỹ", "Xã Phước Năng"], "Xã Phước Năng"),
    ("Huyện Phước Sơn", ["Xã Phước Công", "Xã Phước Chánh"], "Xã Phước Chánh"),
    ("Huyện Phước Sơn", ["Xã Phước Lộc", "Xã Phước Kim", "Xã Phước Thành"], "Xã Phước Thành"),
    ("Huyện Phước Sơn", ["Xã Phước Hòa", "Xã Phước Hiệp"], "Xã Phước Hiệp"),

    # Huyện Hoàng Sa - item 92
    ("Huyện Hoàng Sa", ["Huyện Hoàng Sa"], "Đặc khu Hoàng Sa"),
]


# =============================================================================
# ĐẮK LẮK (MỚI) - 96 restructuring items
# Combines Đắk Lắk + Phú Yên
# =============================================================================

daklak_restructuring_data = [
    # Thành phố Buôn Ma Thuột - items 1, 82-86
    ("Thành phố Buôn Ma Thuột", ["Xã Hòa Phú", "Xã Hòa Xuân", "Xã Hòa Khánh"], "Xã Hòa Phú"),
    ("Thành phố Buôn Ma Thuột", ["Phường Thành Công", "Phường Tân Tiến", "Phường Tân Thành", "Phường Tự An", "Phường Tân Lợi", "Xã Cư Êbur"], "Phường Buôn Ma Thuột"),
    ("Thành phố Buôn Ma Thuột", ["Phường Tân An", "Xã Ea Tu", "Xã Hòa Thuận"], "Phường Tân An"),
    ("Thành phố Buôn Ma Thuột", ["Phường Tân Hòa", "Phường Tân Lập", "Xã Hòa Thắng"], "Phường Tân Lập"),
    ("Thành phố Buôn Ma Thuột", ["Phường Khánh Xuân", "Phường Thành Nhất"], "Phường Thành Nhất"),
    ("Thành phố Buôn Ma Thuột", ["Phường Ea Tam", "Xã Ea Kao"], "Phường Ea Kao"),

    # Thị xã Buôn Hồ - items 2, 87-88
    ("Thị xã Buôn Hồ", ["Xã Ea Siên", "Xã Ea Drông"], "Xã Ea Drông"),
    ("Thị xã Buôn Hồ", ["Phường Đạt Hiếu", "Phường An Bình", "Phường An Lạc", "Phường Thiện An", "Phường Thống Nhất", "Phường Đoàn Kết"], "Phường Buôn Hồ"),
    ("Thị xã Buôn Hồ", ["Phường Bình Tân", "Xã Bình Thuận", "Xã Cư Bao"], "Phường Cư Bao"),

    # Huyện Ea Súp - items 3-5
    ("Huyện Ea Súp", ["Thị trấn Ea Súp", "Xã Cư M'Lan", "Xã Ea Lê"], "Xã Ea Súp"),
    ("Huyện Ea Súp", ["Xã Ia Jlơi", "Xã Cư Kbang", "Xã Ea Rốk"], "Xã Ea Rốk"),
    ("Huyện Ea Súp", ["Xã Ya Tờ Mốt", "Xã Ea Bung"], "Xã Ea Bung"),

    # Huyện Buôn Đôn - items 6-8, 96
    ("Huyện Buôn Đôn", ["Xã Ea Huar", "Xã Tân Hòa", "Xã Ea Wer"], "Xã Ea Wer"),
    ("Huyện Buôn Đôn", ["Xã Ea Bar", "Xã Cuôr Knia", "Xã Ea Nuôl"], "Xã Ea Nuôl"),
    ("Huyện Buôn Đôn", ["Xã Krông Na"], "Xã Buôn Đôn"),

    # Huyện Cư M'gar - items 9-13
    ("Huyện Cư M'gar", ["Xã Ea Kuêh", "Xã Ea Kiết"], "Xã Ea Kiết"),
    ("Huyện Cư M'gar", ["Xã Quảng Hiệp", "Xã Ea M'nang", "Xã Ea M'Droh"], "Xã Ea M'Droh"),
    ("Huyện Cư M'gar", ["Thị trấn Quảng Phú", "Thị trấn Ea Pốk", "Xã Cư Suê", "Xã Quảng Tiến"], "Xã Quảng Phú"),
    ("Huyện Cư M'gar", ["Xã Ea Drơng", "Xã Cuôr Đăng"], "Xã Cuôr Đăng"),
    ("Huyện Cư M'gar", ["Xã Ea H'đing", "Xã Ea Kpam", "Xã Cư M'gar"], "Xã Cư M'gar"),

    # Huyện Krông Búk - items 14-16
    ("Huyện Krông Búk", ["Xã Ea Tar", "Xã Cư Dliê Mnông", "Xã Ea Tul"], "Xã Ea Tul"),
    ("Huyện Krông Búk", ["Thị trấn Pơng Drang", "Xã Ea Ngai", "Xã Tân Lập"], "Xã Pơng Drang"),
    ("Huyện Krông Búk", ["Xã Cư Né", "Xã Chứ Kbô"], "Xã Krông Búk"),

    # Huyện Ea H'leo - items 17-20
    ("Huyện Ea H'leo", ["Xã Ea Sin", "Xã Cư Pơng"], "Xã Cư Pơng"),
    ("Huyện Ea H'leo", ["Xã Ea Nam", "Xã Ea Tir", "Xã Ea Khăl"], "Xã Ea Khăl"),
    ("Huyện Ea H'leo", ["Thị trấn Ea Drăng", "Xã Ea Ral", "Xã Dliê Yang"], "Xã Ea Drăng"),
    ("Huyện Ea H'leo", ["Xã Cư A Mung", "Xã Cư Mốt", "Xã Ea Wy"], "Xã Ea Wy"),

    # Huyện Krông Năng - items 21-24
    ("Huyện Krông Năng", ["Xã Ea Sol", "Xã Ea Hiao"], "Xã Ea Hiao"),
    ("Huyện Krông Năng", ["Thị trấn Krông Năng", "Xã Phú Lộc", "Xã Ea Hồ"], "Xã Krông Năng"),
    ("Huyện Krông Năng", ["Xã Ea Tóh", "Xã Ea Tân", "Xã Dliê Ya"], "Xã Dliê Ya"),
    ("Huyện Krông Năng", ["Xã Ea Tam", "Xã Cư Klông", "Xã Tam Giang"], "Xã Tam Giang"),

    # Huyện Krông Pắc - items 25-29
    ("Huyện Krông Pắc", ["Xã Ea Púk", "Xã Ea Dăh", "Xã Phú Xuân"], "Xã Phú Xuân"),
    ("Huyện Krông Pắc", ["Thị trấn Phước An", "Xã Hòa An", "Xã Ea Yông", "Xã Hòa Tiến"], "Xã Krông Pắc"),
    ("Huyện Krông Pắc", ["Xã Hòa Đông", "Xã Ea Kênh", "Xã Ea Knuếc"], "Xã Ea Knuếc"),
    ("Huyện Krông Pắc", ["Xã Ea Yiêng", "Xã Ea Uy", "Xã Tân Tiến"], "Xã Tân Tiến"),
    ("Huyện Krông Pắc", ["Xã Ea Kuăng", "Xã Ea Hiu", "Xã Ea Phê"], "Xã Ea Phê"),

    # Huyện Ea Kar - items 30-34
    ("Huyện Ea Kar", ["Xã Krông Búk", "Xã Ea Kly"], "Xã Ea Kly"),
    ("Huyện Ea Kar", ["Thị trấn Ea Kar", "Xã Cư Huê", "Xã Ea Đar", "Xã Ea Kmút", "Xã Cư Ni", "Xã Xuân Phú"], "Xã Ea Kar"),
    ("Huyện Ea Kar", ["Xã Cư Elang", "Xã Ea Ô"], "Xã Ea Ô"),
    ("Huyện Ea Kar", ["Thị trấn Ea Knốp", "Xã Ea Tih", "Xã Ea Sô", "Xã Ea Sar"], "Xã Ea Knốp"),
    ("Huyện Ea Kar", ["Xã Cư Bông", "Xã Cư Yang"], "Xã Cư Yang"),

    # Huyện M'Drắk - items 35-39
    ("Huyện M'Drắk", ["Xã Cư Prông", "Xã Ea Păl"], "Xã Ea Păl"),
    ("Huyện M'Drắk", ["Thị trấn M'Drắk", "Xã Krông Jing", "Xã Ea Lai"], "Xã M'Drắk"),
    ("Huyện M'Drắk", ["Xã Ea H'Mlay", "Xã Ea M'Doal", "Xã Ea Riêng"], "Xã Ea Riêng"),
    ("Huyện M'Drắk", ["Xã Cư Króa", "Xã Cư M'ta"], "Xã Cư M'ta"),
    ("Huyện M'Drắk", ["Xã Cư San", "Xã Krông Á"], "Xã Krông Á"),

    # Huyện Krông Bông - items 40-44
    ("Huyện Krông Bông", ["Xã Ea Pil", "Xã Cư Prao"], "Xã Cư Prao"),
    ("Huyện Krông Bông", ["Xã Yang Reh", "Xã Ea Trul", "Xã Hòa Sơn"], "Xã Hòa Sơn"),
    ("Huyện Krông Bông", ["Xã Hòa Thành", "Xã Cư Kty", "Xã Dang Kang"], "Xã Dang Kang"),
    ("Huyện Krông Bông", ["Thị trấn Krông Kmar", "Xã Hòa Lễ", "Xã Khuê Ngọc Điền"], "Xã Krông Bông"),
    ("Huyện Krông Bông", ["Xã Cư Drăm", "Xã Yang Mao"], "Xã Yang Mao"),

    # Huyện Lắk - items 45-49
    ("Huyện Lắk", ["Xã Hòa Phong", "Xã Cư Pui"], "Xã Cư Pui"),
    ("Huyện Lắk", ["Thị trấn Liên Sơn", "Xã Yang Tao", "Xã Bông Krang"], "Xã Liên Sơn Lắk"),
    ("Huyện Lắk", ["Xã Buôn Tría", "Xã Buôn Triết", "Xã Đắk Liêng"], "Xã Đắk Liêng"),
    ("Huyện Lắk", ["Xã Ea Rbin", "Xã Nam Ka"], "Xã Nam Ka"),
    ("Huyện Lắk", ["Xã Đắk Nuê", "Xã Đắk Phơi"], "Xã Đắk Phơi"),

    # Huyện Cư Kuin - items 50-51
    ("Huyện Cư Kuin", ["Xã Cư Êwi", "Xã Ea Hu", "Xã Ea Ning"], "Xã Ea Ning"),
    ("Huyện Cư Kuin", ["Xã Hòa Hiệp", "Xã Dray Bhăng", "Xã Ea Bhốk"], "Xã Dray Bhăng"),

    # Huyện Krông Ana - items 52-54
    ("Huyện Krông Ana", ["Xã Ea Tiêu", "Xã Ea Ktur", "Xã Ea Bhốk"], "Xã Ea Ktur"),
    ("Huyện Krông Ana", ["Thị trấn Buôn Trấp", "Xã Bình Hòa", "Xã Quảng Điền"], "Xã Krông Ana"),
    ("Huyện Krông Ana", ["Xã Băng A Drênh", "Xã Dur Kmăl"], "Xã Dur Kmăl"),

    # Huyện Krông Nô - item 55
    ("Huyện Krông Nô", ["Xã Ea Bông", "Xã Dray Sáp", "Xã Ea Na"], "Xã Ea Na"),

    # Huyện Sông Hinh (Phú Yên) - items 56-58, 74-77
    ("Huyện Sông Hinh", ["Xã Xuân Lâm", "Xã Xuân Thọ 1", "Xã Xuân Thọ 2"], "Xã Xuân Thọ"),
    ("Huyện Sông Hinh", ["Xã Xuân Bình", "Xã Xuân Cảnh"], "Xã Xuân Cảnh"),
    ("Huyện Sông Hinh", ["Xã Xuân Hải", "Xã Xuân Lộc"], "Xã Xuân Lộc"),
    ("Huyện Sông Hinh", ["Xã Ea Lâm", "Xã Ea Ly", "Xã Ea Bar"], "Xã Ea Ly"),
    ("Huyện Sông Hinh", ["Xã Ea Bá", "Xã Ea Bar"], "Xã Ea Bá"),
    ("Huyện Sông Hinh", ["Xã Sơn Giang", "Xã Đức Bình Đông", "Xã Đức Bình Tây", "Xã Ea Bia"], "Xã Đức Bình"),
    ("Huyện Sông Hinh", ["Thị trấn Hai Riêng", "Xã Ea Trol", "Xã Sông Hinh", "Xã Ea Bia"], "Xã Sông Hinh"),

    # Huyện Tuy An (Phú Yên) - items 59-63
    ("Huyện Tuy An", ["Xã Hòa Tâm", "Xã Hòa Xuân Đông", "Xã Hòa Xuân Nam"], "Xã Hòa Xuân"),
    ("Huyện Tuy An", ["Thị trấn Chí Thạnh", "Xã An Dân", "Xã An Định"], "Xã Tuy An Bắc"),
    ("Huyện Tuy An", ["Xã An Ninh Đông", "Xã An Ninh Tây", "Xã An Thạch"], "Xã Tuy An Đông"),
    ("Huyện Tuy An", ["Xã An Hiệp", "Xã An Hòa Hải", "Xã An Cư"], "Xã Ô Loan"),
    ("Huyện Tuy An", ["Xã An Thọ", "Xã An Mỹ", "Xã An Chấn"], "Xã Tuy An Nam"),

    # Huyện Tuy An (Phú Yên) - item 63 continued
    ("Huyện Tuy An", ["Xã An Nghiệp", "Xã An Xuân", "Xã An Lĩnh"], "Xã Tuy An Tây"),

    # Huyện Phú Hòa (Phú Yên) - items 64-65
    ("Huyện Phú Hòa", ["Thị trấn Phú Hòa", "Xã Hòa Thắng", "Xã Hòa Định Đông", "Xã Hòa Định Tây", "Xã Hòa Hội", "Xã Hòa An"], "Xã Phú Hòa 1"),
    ("Huyện Phú Hòa", ["Xã Hòa Quang Nam", "Xã Hòa Quang Bắc", "Xã Hòa Trị"], "Xã Phú Hòa 2"),

    # Huyện Tây Hòa (Phú Yên) - items 66-69
    ("Huyện Tây Hòa", ["Thị trấn Phú Thứ", "Xã Hòa Phong", "Xã Hòa Tân Tây", "Xã Hòa Bình 1"], "Xã Tây Hòa"),
    ("Huyện Tây Hòa", ["Xã Hòa Đồng", "Xã Hòa Thịnh"], "Xã Hòa Thịnh"),
    ("Huyện Tây Hòa", ["Xã Hòa Mỹ Đông", "Xã Hòa Mỹ Tây"], "Xã Hòa Mỹ"),
    ("Huyện Tây Hòa", ["Xã Hòa Phú", "Xã Sơn Thành Đông", "Xã Sơn Thành Tây"], "Xã Sơn Thành"),

    # Huyện Sơn Hòa (Phú Yên) - items 70-73
    ("Huyện Sơn Hòa", ["Thị trấn Củng Sơn", "Xã Suối Bạc", "Xã Sơn Hà", "Xã Sơn Nguyên", "Xã Sơn Phước"], "Xã Sơn Hòa"),
    ("Huyện Sơn Hòa", ["Xã Sơn Long", "Xã Sơn Xuân", "Xã Sơn Định"], "Xã Vân Hòa"),
    ("Huyện Sơn Hòa", ["Xã Sơn Hội", "Xã Cà Lúi", "Xã Phước Tân"], "Xã Tây Sơn"),
    ("Huyện Sơn Hòa", ["Xã Ea Chà Rang", "Xã Krông Pa", "Xã Suối Trai"], "Xã Suối Trai"),

    # Huyện Đồng Xuân (Phú Yên) - items 78-81
    ("Huyện Đồng Xuân", ["Xã Đa Lộc", "Xã Xuân Lãnh"], "Xã Xuân Lãnh"),
    ("Huyện Đồng Xuân", ["Xã Xuân Quang 1", "Xã Phú Mỡ"], "Xã Phú Mỡ"),
    ("Huyện Đồng Xuân", ["Xã Xuân Quang 3", "Xã Xuân Phước"], "Xã Xuân Phước"),
    ("Huyện Đồng Xuân", ["Thị trấn La Hai", "Xã Xuân Sơn Nam", "Xã Xuân Sơn Bắc", "Xã Xuân Long", "Xã Xuân Quang 2"], "Xã Đồng Xuân"),

    # Thị xã Đông Hòa (Phú Yên) - items 89, 94-95
    ("Thị xã Đông Hòa", ["Phường Phú Đông", "Phường Phú Lâm", "Phường Phú Thạnh", "Xã Hòa Thành", "Phường Hòa Hiệp Bắc", "Xã Hòa Bình 1"], "Phường Phú Yên"),
    ("Thị xã Đông Hòa", ["Phường Hòa Vinh", "Phường Hòa Xuân Tây", "Xã Hòa Tân Đông"], "Phường Đông Hòa"),
    ("Thị xã Đông Hòa", ["Phường Hòa Hiệp Trung", "Phường Hòa Hiệp Nam", "Phường Hòa Hiệp Bắc"], "Phường Hòa Hiệp"),

    # Thành phố Tuy Hòa (Phú Yên) - items 90-91
    ("Thành phố Tuy Hòa", ["Phường 1", "Phường 2", "Phường 4", "Phường 5", "Phường 7", "Phường 9", "Xã Hòa An", "Xã Hòa Trị"], "Phường Tuy Hòa"),
    ("Thành phố Tuy Hòa", ["Xã An Phú", "Xã Hòa Kiến", "Xã Bình Kiến", "Phường 9"], "Phường Bình Kiến"),

    # Thị xã Sông Cầu (Phú Yên) - items 92-93
    ("Thị xã Sông Cầu", ["Phường Xuân Thành", "Phường Xuân Đài"], "Phường Xuân Đài"),
    ("Thị xã Sông Cầu", ["Phường Xuân Yên", "Phường Xuân Phú", "Xã Xuân Phương", "Xã Xuân Thịnh"], "Phường Sông Cầu"),
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

    # Process Cần Thơ
    print("Processing Thành phố Cần Thơ...")
    dia_danh, chuyen_doi = process_province(cantho_restructuring_data, "Thành phố Cần Thơ", "(mới)")
    all_dia_danh.update(dia_danh)
    all_chuyen_doi.update(chuyen_doi)
    print(f"  - {len(chuyen_doi)} conversion mappings")

    # Process Cao Bằng
    print("Processing Tỉnh Cao Bằng...")
    dia_danh, chuyen_doi = process_province(caobang_restructuring_data, "Tỉnh Cao Bằng", "")
    all_dia_danh.update(dia_danh)
    all_chuyen_doi.update(chuyen_doi)
    print(f"  - {len(chuyen_doi)} conversion mappings")

    # Process Đà Nẵng
    print("Processing Thành phố Đà Nẵng...")
    dia_danh, chuyen_doi = process_province(danang_restructuring_data, "Thành phố Đà Nẵng", "(mới)")
    all_dia_danh.update(dia_danh)
    all_chuyen_doi.update(chuyen_doi)
    print(f"  - {len(chuyen_doi)} conversion mappings")

    # Process Đắk Lắk
    print("Processing Tỉnh Đắk Lắk...")
    dia_danh, chuyen_doi = process_province(daklak_restructuring_data, "Tỉnh Đắk Lắk", "(mới)")
    all_dia_danh.update(dia_danh)
    all_chuyen_doi.update(chuyen_doi)
    print(f"  - {len(chuyen_doi)} conversion mappings")

    # Save intermediate files
    for province_key in all_dia_danh:
        safe_name = province_key.replace(" ", "_").replace("/", "_").lower()

        with open(f'{DATA_PATH}/{safe_name}_dia_danh.json', 'w', encoding='utf-8') as f:
            json.dump({province_key: all_dia_danh[province_key]}, f, ensure_ascii=False, indent=2)

    # Save combined chuyen_doi
    with open(f'{DATA_PATH}/batch2_chuyen_doi.json', 'w', encoding='utf-8') as f:
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

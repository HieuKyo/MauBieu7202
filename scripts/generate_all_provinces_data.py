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
import os

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

    print(f"\nFinal totals:")
    print(f"  - dia_danh provinces: {len(main_dia_danh)}")
    print(f"  - chuyen_doi mappings: {len(main_chuyen_doi)}")


if __name__ == "__main__":
    main()

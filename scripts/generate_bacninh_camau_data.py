#!/usr/bin/env python3
"""
Script to generate Bắc Ninh (mới) and Cà Mau administrative restructuring data
for dia_danh.json and chuyen_doi.json
"""

import json

# =============================================================================
# BẮC NINH (MỚI) - 98 restructuring items
# Combines old Bắc Ninh + Bắc Giang provinces
# =============================================================================

bacninh_restructuring_data = [
    # Huyện Yên Phong (Bắc Ninh) - items 1-7
    ("Huyện Yên Phong", ["Xã Yên Giả", "Xã Chi Lăng"], "Xã Chi Lăng"),
    ("Huyện Yên Phong", ["Xã Châu Phong", "Xã Đức Long", "Xã Phù Lãng"], "Xã Phù Lãng"),
    ("Huyện Yên Phong", ["Thị trấn Chờ", "Xã Trung Nghĩa", "Xã Long Châu", "Xã Đông Tiến"], "Xã Yên Phong"),
    ("Huyện Yên Phong", ["Xã Yên Phụ", "Xã Đông Thọ", "Xã Văn Môn"], "Xã Văn Môn"),
    ("Huyện Yên Phong", ["Xã Hòa Tiến", "Xã Tam Giang"], "Xã Tam Giang"),
    ("Huyện Yên Phong", ["Xã Dũng Liệt", "Xã Yên Trung"], "Xã Yên Trung"),
    ("Huyện Yên Phong", ["Xã Thụy Hòa", "Xã Đông Phong", "Xã Tam Đa"], "Xã Tam Đa"),

    # Huyện Tiên Du (Bắc Ninh) - items 8-12
    ("Huyện Tiên Du", ["Thị trấn Lim", "Xã Nội Duệ", "Xã Phú Lâm"], "Xã Tiên Du"),
    ("Huyện Tiên Du", ["Xã Hiên Vân", "Xã Việt Đoàn", "Xã Liên Bão"], "Xã Liên Bão"),
    ("Huyện Tiên Du", ["Xã Lạc Vệ", "Xã Tân Chi"], "Xã Tân Chi"),
    ("Huyện Tiên Du", ["Xã Tri Phương", "Xã Hoàn Sơn", "Xã Đại Đồng"], "Xã Đại Đồng"),
    ("Huyện Tiên Du", ["Xã Minh Đạo", "Xã Cảnh Hưng", "Xã Phật Tích"], "Xã Phật Tích"),

    # Huyện Gia Bình (Bắc Ninh) - items 13-17
    ("Huyện Gia Bình", ["Thị trấn Gia Bình", "Xã Xuân Lai", "Xã Quỳnh Phú", "Xã Đại Bái"], "Xã Gia Bình"),
    ("Huyện Gia Bình", ["Thị trấn Nhân Thắng", "Xã Thái Bảo", "Xã Bình Dương"], "Xã Nhân Thắng"),
    ("Huyện Gia Bình", ["Xã Song Giang", "Xã Đại Lai"], "Xã Đại Lai"),
    ("Huyện Gia Bình", ["Xã Vạn Ninh", "Xã Cao Đức"], "Xã Cao Đức"),
    ("Huyện Gia Bình", ["Xã Giang Sơn", "Xã Lãng Ngâm", "Xã Đông Cứu"], "Xã Đông Cứu"),

    # Huyện Lương Tài (Bắc Ninh) - items 18-22
    ("Huyện Lương Tài", ["Thị trấn Thứa", "Xã Phú Hòa", "Xã Tân Lãng"], "Xã Lương Tài"),
    ("Huyện Lương Tài", ["Xã Bình Định", "Xã Quảng Phú", "Xã Lâm Thao"], "Xã Lâm Thao"),
    ("Huyện Lương Tài", ["Xã Phú Lương", "Xã Quang Minh", "Xã Trung Chính"], "Xã Trung Chính"),
    ("Huyện Lương Tài", ["Xã An Thịnh", "Xã An Tập", "Xã Trung Kênh"], "Xã Trung Kênh"),
    ("Huyện Lương Tài", ["Xã Giáo Liêm", "Xã Phúc Sơn", "Xã Đại Sơn"], "Xã Đại Sơn"),

    # Huyện Sơn Động (Bắc Giang) - items 23-28
    ("Huyện Sơn Động", ["Thị trấn An Châu", "Xã An Bá", "Xã Vĩnh An"], "Xã Sơn Động"),
    ("Huyện Sơn Động", ["Thị trấn Tây Yên Tử", "Xã Thanh Luận"], "Xã Tây Yên Tử"),
    ("Huyện Sơn Động", ["Xã Long Sơn", "Xã Dương Hưu"], "Xã Dương Hưu"),
    ("Huyện Sơn Động", ["Xã Cẩm Đàn", "Xã Yên Định"], "Xã Yên Định"),
    ("Huyện Sơn Động", ["Xã Lệ Viễn", "Xã An Lạc"], "Xã An Lạc"),
    ("Huyện Sơn Động", ["Xã Hữu Sản", "Xã Vân Sơn"], "Xã Vân Sơn"),

    # Huyện Lục Ngạn (Bắc Giang) - items 29-40
    ("Huyện Lục Ngạn", ["Thị trấn Biển Động", "Xã Kim Sơn", "Xã Phú Nhuận"], "Xã Biển Động"),
    ("Huyện Lục Ngạn", ["Thị trấn Phì Điền", "Xã Giáp Sơn", "Xã Đồng Cốc", "Xã Tân Hoa", "Xã Tân Quang"], "Xã Lục Ngạn"),
    ("Huyện Lục Ngạn", ["Xã Tân Lập", "Xã Đèo Gia"], "Xã Đèo Gia"),
    ("Huyện Lục Ngạn", ["Xã Hộ Đáp", "Xã Sơn Hải"], "Xã Sơn Hải"),
    ("Huyện Lục Ngạn", ["Xã Cấm Sơn", "Xã Tân Sơn"], "Xã Tân Sơn"),
    ("Huyện Lục Ngạn", ["Xã Phong Vân", "Xã Biên Sơn"], "Xã Biên Sơn"),
    ("Huyện Lục Ngạn", ["Xã Phong Minh", "Xã Sa Lý"], "Xã Sa Lý"),
    ("Huyện Lục Ngạn", ["Xã Tân Mộc", "Xã Nam Dương"], "Xã Nam Dương"),
    ("Huyện Lục Ngạn", ["Xã Kiên Thành", "Xã Kiên Lao"], "Xã Kiên Lao"),
    ("Huyện Lục Ngạn", ["Xã Bình Sơn", "Xã Lục Sơn"], "Xã Lục Sơn"),
    ("Huyện Lục Ngạn", ["Xã Vô Tranh", "Xã Trường Sơn"], "Xã Trường Sơn"),
    ("Huyện Lục Ngạn", ["Xã Đan Hội", "Xã Cẩm Lý"], "Xã Cẩm Lý"),

    # Huyện Lục Nam (Bắc Giang) - items 41-45
    ("Huyện Lục Nam", ["Xã Đông Hưng", "Xã Đông Phú"], "Xã Đông Phú"),
    ("Huyện Lục Nam", ["Xã Trường Giang", "Xã Huyền Sơn", "Xã Nghĩa Phương"], "Xã Nghĩa Phương"),
    ("Huyện Lục Nam", ["Thị trấn Phương Sơn", "Thị trấn Đồi Ngô", "Xã Cương Sơn", "Xã Tiên Nha", "Xã Chu Điện"], "Xã Lục Nam"),
    ("Huyện Lục Nam", ["Xã Yên Sơn", "Xã Lan Mẫu", "Xã Khám Lạng", "Xã Bắc Lũng"], "Xã Bắc Lũng"),
    ("Huyện Lục Nam", ["Xã Bảo Sơn", "Xã Thanh Lâm", "Xã Tam Dị", "Xã Bảo Đài"], "Xã Bảo Đài"),

    # Huyện Lạng Giang (Bắc Giang) - items 46-50
    ("Huyện Lạng Giang", ["Thị trấn Vôi", "Xã Xương Lâm", "Xã Hương Lạc", "Xã Tân Hưng"], "Xã Lạng Giang"),
    ("Huyện Lạng Giang", ["Xã Xuân Hương", "Xã Dương Đức", "Xã Tân Thanh", "Xã Mỹ Thái"], "Xã Mỹ Thái"),
    ("Huyện Lạng Giang", ["Thị trấn Kép", "Xã Quang Thịnh", "Xã Hương Sơn"], "Xã Kép"),
    ("Huyện Lạng Giang", ["Xã Tân Dĩnh", "Xã Thái Đào", "Xã Đại Lâm"], "Xã Tân Dĩnh"),
    ("Huyện Lạng Giang", ["Xã Đào Mỹ", "Xã Nghĩa Hòa", "Xã An Hà", "Xã Nghĩa Hưng", "Xã Tiên Lục"], "Xã Tiên Lục"),

    # Huyện Yên Thế (Bắc Giang) - items 51-55
    ("Huyện Yên Thế", ["Thị trấn Phồn Xương", "Xã Đồng Lạc", "Xã Đồng Tâm", "Xã Tân Hiệp", "Xã Tân Sỏi"], "Xã Yên Thế"),
    ("Huyện Yên Thế", ["Thị trấn Bố Hạ", "Xã Đông Sơn", "Xã Hương Vĩ"], "Xã Bố Hạ"),
    ("Huyện Yên Thế", ["Xã Đồng Hưu", "Xã Đồng Vương", "Xã Đồng Kỳ"], "Xã Đồng Kỳ"),
    ("Huyện Yên Thế", ["Xã Đồng Tiến", "Xã Canh Nậu", "Xã Xuân Lương"], "Xã Xuân Lương"),
    ("Huyện Yên Thế", ["Xã Tiến Thắng", "Xã An Thượng", "Xã Tam Tiến"], "Xã Tam Tiến"),

    # Huyện Tân Yên (Bắc Giang) - items 56-61
    ("Huyện Tân Yên", ["Thị trấn Cao Thượng", "Xã Cao Xá", "Xã Việt Lập", "Xã Ngọc Lý"], "Xã Tân Yên"),
    ("Huyện Tân Yên", ["Xã Song Vân", "Xã Ngọc Châu", "Xã Ngọc Vân", "Xã Việt Ngọc", "Xã Ngọc Thiện"], "Xã Ngọc Thiện"),
    ("Huyện Tân Yên", ["Thị trấn Nhã Nam", "Xã Tân Trung", "Xã Liên Sơn", "Xã An Dương"], "Xã Nhã Nam"),
    ("Huyện Tân Yên", ["Xã Hợp Đức", "Xã Liên Chung", "Xã Phúc Hòa"], "Xã Phúc Hoà"),
    ("Huyện Tân Yên", ["Xã Lam Sơn", "Xã Quang Trung"], "Xã Quang Trung"),
    ("Huyện Tân Yên", ["Xã Thường Thắng", "Xã Mai Trung", "Xã Hùng Thái", "Xã Sơn Thịnh", "Xã Hợp Thịnh"], "Xã Hợp Thịnh"),

    # Huyện Hiệp Hòa (Bắc Giang) - items 62-65
    ("Huyện Hiệp Hòa", ["Thị trấn Thắng", "Xã Đông Lỗ", "Xã Đoan Bái", "Xã Danh Thắng", "Xã Lương Phong"], "Xã Hiệp Hòa"),
    ("Huyện Hiệp Hòa", ["Xã Đồng Tiến", "Xã Toàn Thắng", "Xã Ngọc Sơn", "Xã Hoàng Vân"], "Xã Hoàng Vân"),
    ("Huyện Hiệp Hòa", ["Xã Đức Giang", "Xã Đồng Phúc", "Xã Đồng Việt"], "Xã Đồng Việt"),
    ("Huyện Hiệp Hòa", ["Thị trấn Bắc Lý", "Xã Hương Lâm", "Xã Mai Đình", "Xã Châu Minh", "Xã Xuân Cẩm"], "Xã Xuân Cẩm"),

    # TP Bắc Ninh - items 66-70
    ("Thành phố Bắc Ninh", ["Phường Suối Hoa", "Phường Tiền Ninh Vệ", "Phường Vạn An", "Phường Hòa Long", "Phường Khúc Xuyên", "Phường Kinh Bắc"], "Phường Kinh Bắc"),
    ("Thành phố Bắc Ninh", ["Phường Đại Phúc", "Phường Phong Khê", "Phường Võ Cường"], "Phường Võ Cường"),
    ("Thành phố Bắc Ninh", ["Phường Kim Chân", "Phường Đáp Cầu", "Phường Thị Cầu", "Phường Vũ Ninh"], "Phường Vũ Ninh"),
    ("Thành phố Bắc Ninh", ["Phường Khắc Niệm", "Phường Hạp Lĩnh"], "Phường Hạp Lĩnh"),
    ("Thành phố Bắc Ninh", ["Phường Vân Dương", "Phường Nam Sơn"], "Phường Nam Sơn"),

    # TP Từ Sơn (Bắc Ninh) - items 71-74
    ("Thành phố Từ Sơn", ["Phường Đông Ngàn", "Phường Tân Hồng", "Phường Phù Chẩn", "Phường Đình Bảng"], "Phường Từ Sơn"),
    ("Thành phố Từ Sơn", ["Phường Tương Giang", "Phường Tam Sơn"], "Phường Tam Sơn"),
    ("Thành phố Từ Sơn", ["Phường Trang Hạ", "Phường Đồng Kỵ", "Phường Đồng Nguyên"], "Phường Đồng Nguyên"),
    ("Thành phố Từ Sơn", ["Phường Châu Khê", "Phường Hương Mạc", "Phường Phù Khê"], "Phường Phù Khê"),

    # Thị xã Thuận Thành (Bắc Ninh) - items 75-80
    ("Thị xã Thuận Thành", ["Phường Hồ", "Phường Song Hồ", "Phường Gia Đông", "Xã Đại Đồng Thành"], "Phường Thuận Thành"),
    ("Thị xã Thuận Thành", ["Phường An Bình", "Xã Hoài Thượng", "Xã Mão Điền"], "Phường Mão Điền"),
    ("Thị xã Thuận Thành", ["Phường Trạm Lộ", "Xã Nghĩa Đạo"], "Phường Trạm Lộ"),
    ("Thị xã Thuận Thành", ["Phường Thanh Khương", "Phường Trí Quả", "Xã Đình Tổ"], "Phường Trí Quả"),
    ("Thị xã Thuận Thành", ["Phường Xuân Lâm", "Phường Hà Mãn", "Xã Ngũ Thái", "Xã Song Liễu"], "Phường Song Liễu"),
    ("Thị xã Thuận Thành", ["Phường Ninh Xá", "Xã Nguyệt Đức"], "Phường Ninh Xá"),

    # Thị xã Quế Võ (Bắc Ninh) - items 81-85
    ("Thị xã Quế Võ", ["Phường Phố Mới", "Phường Bằng An", "Phường Việt Hùng", "Phường Quế Tân"], "Phường Quế Võ"),
    ("Thị xã Quế Võ", ["Phường Phượng Mao", "Phường Phương Liễu"], "Phường Phương Liễu"),
    ("Thị xã Quế Võ", ["Phường Đại Xuân", "Phường Nhân Hòa", "Xã Việt Thống"], "Phường Nhân Hòa"),
    ("Thị xã Quế Võ", ["Phường Phù Lương", "Xã Ngọc Xá", "Xã Đào Viên"], "Phường Đào Viên"),
    ("Thị xã Quế Võ", ["Phường Cách Bi", "Phường Bồng Lai", "Xã Mộ Đạo"], "Phường Bồng Lai"),

    # Thị xã Lục Ngạn (Bắc Giang) - items 86-88
    ("Thị xã Lục Ngạn", ["Phường Thanh Hải", "Phường Hồng Giang", "Phường Trù Hựu", "Phường Chũ"], "Phường Chũ"),
    ("Thị xã Lục Ngạn", ["Phường Phượng Sơn", "Xã Quý Sơn", "Xã Mỹ An"], "Phường Phượng Sơn"),
    ("Thị xã Lục Ngạn", ["Phường Tự Lạn", "Xã Việt Tiến", "Xã Thượng Lan", "Xã Hương Mai"], "Phường Tự Lạn"),

    # Thị xã Việt Yên (Bắc Giang) - items 89-91
    ("Thị xã Việt Yên", ["Phường Bích Động", "Phường Hồng Thái", "Xã Minh Đức", "Xã Nghĩa Trung"], "Phường Việt Yên"),
    ("Thị xã Việt Yên", ["Phường Quang Châu", "Phường Vân Trung", "Phường Tăng Tiến", "Phường Nếnh"], "Phường Nếnh"),
    ("Thị xã Việt Yên", ["Phường Ninh Sơn", "Phường Quảng Minh", "Xã Tiên Sơn", "Xã Trung Sơn", "Xã Vân Hà"], "Phường Vân Hà"),

    # TP Bắc Giang - items 92-94
    ("Thành phố Bắc Giang", ["Phường Thọ Xương", "Phường Ngô Quyền", "Phường Xương Giang", "Phường Hoàng Văn Thụ", "Phường Trần Phú", "Phường Dĩnh Kế", "Phường Dĩnh Trì"], "Phường Bắc Giang"),
    ("Thành phố Bắc Giang", ["Phường Tân Mỹ", "Phường Mỹ Độ", "Phường Song Mai", "Phường Đa Mai", "Xã Quế Nham"], "Phường Đa Mai"),
    ("Thành phố Bắc Giang", ["Phường Nội Hoàng", "Phường Song Khê", "Phường Đồng Sơn", "Phường Tiền Phong"], "Phường Tiền Phong"),

    # Thị xã Yên Dũng (Bắc Giang) - items 95-98
    ("Thị xã Yên Dũng", ["Phường Tân An", "Xã Quỳnh Sơn", "Xã Trí Yên", "Xã Lãng Sơn"], "Phường Tân An"),
    ("Thị xã Yên Dũng", ["Phường Tân Liễu", "Phường Nham Biền", "Xã Yên Lư"], "Phường Yên Dũng"),
    ("Thị xã Yên Dũng", ["Phường Hương Gián", "Phường Tân Tiến", "Xã Xuân Phú"], "Phường Tân Tiến"),
    ("Thị xã Yên Dũng", ["Phường Cảnh Thụy", "Xã Tiến Dũng", "Xã Tư Mại"], "Phường Cảnh Thụy"),
]

# =============================================================================
# CÀ MAU - 38 restructuring items (34 xã + 4 phường)
# Items 35-59 belong to Bạc Liêu (already done)
# =============================================================================

camau_restructuring_data = [
    # Huyện Đầm Dơi - items 1-7
    ("Huyện Đầm Dơi", ["Xã Tân Đức", "Xã Tân Thuận"], "Xã Tân Thuận"),
    ("Huyện Đầm Dơi", ["Xã Nguyễn Huân", "Xã Tân Tiến"], "Xã Tân Tiến"),
    ("Huyện Đầm Dơi", ["Xã Tạ An Khương Đông", "Xã Tạ An Khương Nam", "Xã Tạ An Khương"], "Xã Tạ An Khương"),
    ("Huyện Đầm Dơi", ["Xã Tân Trung", "Xã Trần Phán"], "Xã Trần Phán"),
    ("Huyện Đầm Dơi", ["Xã Ngọc Chánh", "Xã Thanh Tùng"], "Xã Thanh Tùng"),
    ("Huyện Đầm Dơi", ["Thị trấn Đầm Dơi", "Xã Tân Duyệt", "Xã Tân Dân", "Xã Tạ An Khương"], "Xã Đầm Dơi"),
    ("Huyện Đầm Dơi", ["Xã Quách Phẩm Bắc", "Xã Quách Phẩm"], "Xã Quách Phẩm"),

    # Huyện U Minh - items 8-11
    ("Huyện U Minh", ["Xã Khánh Tiến", "Xã Khánh Hòa", "Xã Khánh Thuận", "Xã Khánh Lâm"], "Xã U Minh"),
    ("Huyện U Minh", ["Thị trấn U Minh", "Xã Nguyễn Phích", "Xã Khánh Thuận"], "Xã Nguyễn Phích"),
    ("Huyện U Minh", ["Xã Khánh Hội", "Xã Nguyễn Phích", "Xã Khánh Lâm"], "Xã Khánh Lâm"),
    ("Huyện U Minh", ["Xã Khánh An", "Xã Nguyễn Phích"], "Xã Khánh An"),

    # Huyện Ngọc Hiển (Phan Ngọc Hiển) - items 12-14
    ("Huyện Ngọc Hiển", ["Thị trấn Rạch Gốc", "Xã Viên An Đông", "Xã Tân Ân"], "Xã Phan Ngọc Hiển"),
    ("Huyện Ngọc Hiển", ["Xã Đất Mũi", "Xã Viên An", "Xã Tân Ân"], "Xã Đất Mũi"),
    ("Huyện Ngọc Hiển", ["Xã Tam Giang Tây", "Xã Tân Ân Tây"], "Xã Tân Ân"),

    # Huyện Trần Văn Thời - items 15-19
    ("Huyện Trần Văn Thời", ["Xã Khánh Bình Đông", "Xã Khánh Bình"], "Xã Khánh Bình"),
    ("Huyện Trần Văn Thời", ["Xã Khánh Bình Tây", "Xã Khánh Bình Tây Bắc", "Xã Trần Hợi"], "Xã Đá Bạc"),
    ("Huyện Trần Văn Thời", ["Xã Khánh Hải", "Xã Khánh Hưng"], "Xã Khánh Hưng"),
    ("Huyện Trần Văn Thời", ["Thị trấn Sông Đốc", "Xã Phong Điền"], "Xã Sông Đốc"),
    ("Huyện Trần Văn Thời", ["Thị trấn Trần Văn Thời", "Xã Khánh Lộc", "Xã Phong Lạc", "Xã Lợi An", "Xã Trần Hợi", "Xã Phong Điền"], "Xã Trần Văn Thời"),

    # Huyện Thới Bình - items 20-23
    ("Huyện Thới Bình", ["Thị trấn Thới Bình", "Xã Thới Bình"], "Xã Thới Bình"),
    ("Huyện Thới Bình", ["Xã Trí Lực", "Xã Tân Phú", "Xã Trí Phải"], "Xã Trí Phải"),
    ("Huyện Thới Bình", ["Xã Tân Lộc Bắc", "Xã Tân Lộc Đông", "Xã Tân Lộc"], "Xã Tân Lộc"),
    ("Huyện Thới Bình", ["Xã Tân Bằng", "Xã Biển Bạch Đông", "Xã Biển Bạch"], "Xã Biển Bạch"),

    # Huyện Năm Căn - items 24-26
    ("Huyện Năm Căn", ["Xã Lâm Hải", "Xã Đất Mới", "Thị trấn Năm Căn", "Xã Hàm Rồng", "Xã Viên An"], "Xã Đất Mới"),
    ("Huyện Năm Căn", ["Xã Hàng Vịnh", "Thị trấn Năm Căn", "Xã Hàm Rồng"], "Xã Năm Căn"),
    ("Huyện Năm Căn", ["Xã Hiệp Tùng", "Xã Tam Giang Đông", "Xã Tam Giang"], "Xã Tam Giang"),

    # Huyện Phú Tân - items 27-29
    ("Huyện Phú Tân", ["Thị trấn Cái Đôi Vàm", "Xã Nguyễn Việt Khái"], "Xã Cái Đôi Vàm"),
    ("Huyện Phú Tân", ["Xã Tân Hưng Tây", "Xã Rạch Chèo", "Xã Việt Thắng"], "Xã Nguyễn Việt Khái"),
    ("Huyện Phú Tân", ["Xã Tân Hải", "Xã Phú Tân"], "Xã Phú Tân"),

    # Huyện Cái Nước - items 30-34
    ("Huyện Cái Nước", ["Xã Phú Thuận", "Xã Phú Mỹ", "Xã Hòa Mỹ"], "Xã Phú Mỹ"),
    ("Huyện Cái Nước", ["Xã Thạnh Phú", "Xã Phú Hưng", "Xã Lương Thế Trân", "Xã Lợi An"], "Xã Lương Thế Trân"),
    ("Huyện Cái Nước", ["Xã Tân Hưng", "Xã Đông Hưng", "Xã Đông Thới", "Xã Hòa Mỹ"], "Xã Tân Hưng"),
    ("Huyện Cái Nước", ["Xã Hưng Mỹ", "Xã Tân Hưng Đông", "Xã Hòa Mỹ"], "Xã Hưng Mỹ"),
    ("Huyện Cái Nước", ["Thị trấn Cái Nước", "Xã Trần Thới", "Xã Đông Hưng", "Xã Đông Thới", "Xã Tân Hưng Đông"], "Xã Cái Nước"),

    # TP Cà Mau - items 60-63 (phường)
    ("Thành phố Cà Mau", ["Phường 1", "Phường 2", "Phường 9", "Phường Tân Xuyên", "Xã An Xuyên"], "Phường An Xuyên"),
    ("Thành phố Cà Mau", ["Phường 8", "Xã Lý Văn Lâm", "Xã Lợi An"], "Phường Lý Văn Lâm"),
    ("Thành phố Cà Mau", ["Phường 5", "Phường Tân Thành", "Xã Tân Thành", "Phường 7", "Phường 6", "Xã Định Bình", "Xã Tắc Vân"], "Phường Tân Thành"),
    ("Thành phố Cà Mau", ["Xã Hòa Tân", "Xã Hòa Thành", "Phường 7", "Phường 6", "Xã Định Bình", "Xã Tắc Vân"], "Phường Hoà Thành"),
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


if __name__ == "__main__":
    # Generate Bắc Ninh data
    print("=" * 60)
    print("GENERATING BẮC NINH (MỚI) DATA")
    print("=" * 60)

    bacninh_dia_danh = generate_dia_danh(bacninh_restructuring_data, "Tỉnh Bắc Ninh")
    bacninh_chuyen_doi = generate_chuyen_doi(bacninh_restructuring_data, "Tỉnh Bắc Ninh", "Tỉnh Bắc Ninh (mới)")

    print(f"Bắc Ninh: {len(bacninh_chuyen_doi)} conversion mappings")

    # Count units by type
    huyen_count = len(bacninh_dia_danh["Tỉnh Bắc Ninh"])
    xa_count = sum(len(xa_dict) for xa_dict in bacninh_dia_danh["Tỉnh Bắc Ninh"].values())
    print(f"  - {huyen_count} huyện/thị xã/thành phố")
    print(f"  - {xa_count} xã/phường/thị trấn (old)")

    # Generate Cà Mau data
    print("\n" + "=" * 60)
    print("GENERATING CÀ MAU DATA")
    print("=" * 60)

    camau_dia_danh = generate_dia_danh(camau_restructuring_data, "Tỉnh Cà Mau")
    camau_chuyen_doi = generate_chuyen_doi(camau_restructuring_data, "Tỉnh Cà Mau", "Tỉnh Cà Mau (mới)")

    print(f"Cà Mau: {len(camau_chuyen_doi)} conversion mappings")

    # Count units by type
    huyen_count = len(camau_dia_danh["Tỉnh Cà Mau"])
    xa_count = sum(len(xa_dict) for xa_dict in camau_dia_danh["Tỉnh Cà Mau"].values())
    print(f"  - {huyen_count} huyện/thành phố")
    print(f"  - {xa_count} xã/phường/thị trấn (old)")

    # Save to temporary files for review
    with open('/home/user/MauBieu7202/templates_app/static/data/bacninh_dia_danh.json', 'w', encoding='utf-8') as f:
        json.dump(bacninh_dia_danh, f, ensure_ascii=False, indent=2)

    with open('/home/user/MauBieu7202/templates_app/static/data/bacninh_chuyen_doi.json', 'w', encoding='utf-8') as f:
        json.dump(bacninh_chuyen_doi, f, ensure_ascii=False, indent=2)

    with open('/home/user/MauBieu7202/templates_app/static/data/camau_dia_danh.json', 'w', encoding='utf-8') as f:
        json.dump(camau_dia_danh, f, ensure_ascii=False, indent=2)

    with open('/home/user/MauBieu7202/templates_app/static/data/camau_chuyen_doi.json', 'w', encoding='utf-8') as f:
        json.dump(camau_chuyen_doi, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("FILES SAVED")
    print("=" * 60)
    print("  - bacninh_dia_danh.json")
    print("  - bacninh_chuyen_doi.json")
    print("  - camau_dia_danh.json")
    print("  - camau_chuyen_doi.json")
    print("\nNext: Merge these into the main dia_danh.json and chuyen_doi.json files")

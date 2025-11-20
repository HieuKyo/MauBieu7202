#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch 7 Part 2: Generate Ninh Bình (mới) province data
Province: Tỉnh Ninh Bình (129 items)
Note: This is a mega-province combining old Hà Nam + Nam Định + Ninh Bình
"""

import json
import os

# Ninh Bình restructuring data - 129 items organized by district
ninhbinh_restructuring_data = [
    # Huyện Bình Lục (old Hà Nam) - items 1-5
    ("Huyện Bình Lục", ["Xã Bình Nghĩa", "Xã Tràng An", "Xã Đồng Du"], "Xã Bình Lục"),
    ("Huyện Bình Lục", ["Thị trấn Bình Mỹ", "Xã Đồn Xá", "Xã La Sơn"], "Xã Bình Mỹ"),
    ("Huyện Bình Lục", ["Xã Trung Lương", "Xã Ngọc Lũ", "Xã Bình An"], "Xã Bình An"),
    ("Huyện Bình Lục", ["Xã Bồ Đề", "Xã Vũ Bản", "Xã An Ninh"], "Xã Bình Giang"),
    ("Huyện Bình Lục", ["Xã Tiêu Động", "Xã An Lão", "Xã An Đổ"], "Xã Bình Sơn"),

    # Huyện Thanh Liêm (old Hà Nam) - items 6-10
    ("Huyện Thanh Liêm", ["Xã Liêm Phong", "Xã Liêm Cần", "Xã Thanh Hà"], "Xã Liêm Hà"),
    ("Huyện Thanh Liêm", ["Thị trấn Tân Thanh", "Xã Thanh Thủy", "Xã Thanh Phong"], "Xã Tân Thanh"),
    ("Huyện Thanh Liêm", ["Xã Liêm Sơn", "Xã Liêm Thuận", "Xã Liêm Túc"], "Xã Thanh Bình"),
    ("Huyện Thanh Liêm", ["Xã Thanh Nghị", "Xã Thanh Tân", "Xã Thanh Hải"], "Xã Thanh Lâm"),
    ("Huyện Thanh Liêm", ["Xã Thanh Hương", "Xã Thanh Tâm", "Xã Thanh Nguyên"], "Xã Thanh Liêm"),

    # Huyện Lý Nhân (old Hà Nam) - items 11-17
    ("Huyện Lý Nhân", ["Xã Chính Lý", "Xã Hợp Lý", "Xã Văn Lý"], "Xã Lý Nhân"),
    ("Huyện Lý Nhân", ["Xã Công Lý", "Xã Nguyên Lý", "Xã Đức Lý"], "Xã Nam Xang"),
    ("Huyện Lý Nhân", ["Xã Chân Lý", "Xã Đạo Lý", "Xã Bắc Lý"], "Xã Bắc Lý"),
    ("Huyện Lý Nhân", ["Thị trấn Vĩnh Trụ", "Xã Nhân Chính", "Xã Nhân Khang"], "Xã Vĩnh Trụ"),
    ("Huyện Lý Nhân", ["Xã Trần Hưng Đạo", "Xã Nhân Nghĩa", "Xã Nhân Bình"], "Xã Trần Thương"),
    ("Huyện Lý Nhân", ["Xã Nhân Thịnh", "Xã Nhân Mỹ", "Xã Xuân Khê"], "Xã Nhân Hà"),
    ("Huyện Lý Nhân", ["Xã Tiến Thắng", "Xã Phú Phúc", "Xã Hòa Hậu"], "Xã Nam Lý"),

    # Huyện Nam Trực (old Nam Định) - items 18-24
    ("Huyện Nam Trực", ["Thị trấn Nam Giang", "Xã Nam Cường", "Xã Nam Hùng"], "Xã Nam Trực"),
    ("Huyện Nam Trực", ["Xã Nam Dương", "Xã Bình Minh", "Xã Nam Tiến"], "Xã Nam Minh"),
    ("Huyện Nam Trực", ["Xã Đồng Sơn", "Xã Nam Thái"], "Xã Nam Đồng"),
    ("Huyện Nam Trực", ["Xã Nam Hoa", "Xã Nam Lợi", "Xã Nam Hải", "Xã Nam Thanh"], "Xã Nam Ninh"),
    ("Huyện Nam Trực", ["Xã Tân Thịnh", "Xã Nam Thắng", "Xã Nam Hồng"], "Xã Nam Hồng"),
    ("Huyện Nam Trực", ["Xã Cộng Hòa", "Xã Minh Tân"], "Xã Minh Tân"),
    ("Huyện Nam Trực", ["Xã Hợp Hưng", "Xã Trung Thành", "Xã Quang Trung", "Xã Hiển Khánh"], "Xã Hiển Khánh"),

    # Huyện Vụ Bản (old Nam Định) - items 25-26
    ("Huyện Vụ Bản", ["Thị trấn Gôi", "Xã Kim Thái", "Xã Tam Thanh"], "Xã Vụ Bản"),
    ("Huyện Vụ Bản", ["Xã Vĩnh Hào", "Xã Đại Thắng", "Xã Liên Minh"], "Xã Liên Minh"),

    # Huyện Ý Yên (old Nam Định) - items 27-33
    ("Huyện Ý Yên", ["Xã Yên Phong", "Xã Hồng Quang", "Xã Yên Khánh", "Thị trấn Lâm"], "Xã Ý Yên"),
    ("Huyện Ý Yên", ["Xã Yên Đồng", "Xã Yên Trị", "Xã Yên Khang"], "Xã Yên Đồng"),
    ("Huyện Ý Yên", ["Xã Yên Nhân", "Xã Yên Lộc", "Xã Yên Phúc", "Xã Yên Cường"], "Xã Yên Cường"),
    ("Huyện Ý Yên", ["Xã Yên Thắng", "Xã Yên Tiến", "Xã Yên Lương"], "Xã Vạn Thắng"),
    ("Huyện Ý Yên", ["Xã Yên Mỹ", "Xã Yên Bình", "Xã Yên Dương", "Xã Yên Ninh"], "Xã Vũ Dương"),
    ("Huyện Ý Yên", ["Xã Trung Nghĩa", "Xã Tân Minh"], "Xã Tân Minh"),
    ("Huyện Ý Yên", ["Xã Phú Hưng", "Xã Yên Thọ", "Xã Yên Chính"], "Xã Phong Doanh"),

    # Huyện Trực Ninh (old Nam Định) - items 34-40
    ("Huyện Trực Ninh", ["Thị trấn Cổ Lễ", "Xã Trung Đông", "Xã Trực Tuấn"], "Xã Cổ Lễ"),
    ("Huyện Trực Ninh", ["Xã Trực Chính", "Xã Phương Định", "Xã Liêm Hải"], "Xã Ninh Giang"),
    ("Huyện Trực Ninh", ["Thị trấn Cát Thành", "Xã Việt Hùng", "Xã Trực Đạo"], "Xã Cát Thành"),
    ("Huyện Trực Ninh", ["Xã Trực Thanh", "Xã Trực Nội", "Xã Trực Hưng"], "Xã Trực Ninh"),
    ("Huyện Trực Ninh", ["Xã Trực Khang", "Xã Trực Mỹ", "Xã Trực Thuận"], "Xã Quang Hưng"),
    ("Huyện Trực Ninh", ["Xã Trực Đại", "Xã Trực Thái", "Xã Trực Thắng"], "Xã Minh Thái"),
    ("Huyện Trực Ninh", ["Thị trấn Ninh Cường", "Xã Trực Cường", "Xã Trực Hùng"], "Xã Ninh Cường"),

    # Huyện Xuân Trường (old Nam Định) - items 41-44
    ("Huyện Xuân Trường", ["Thị trấn Xuân Trường", "Xã Xuân Phúc", "Xã Xuân Ninh", "Xã Xuân Ngọc"], "Xã Xuân Trường"),
    ("Huyện Xuân Trường", ["Xã Xuân Vinh", "Xã Trà Lũ", "Xã Thọ Nghiệp"], "Xã Xuân Hưng"),
    ("Huyện Xuân Trường", ["Xã Xuân Tân", "Xã Xuân Phú", "Xã Xuân Giang"], "Xã Xuân Giang"),
    ("Huyện Xuân Trường", ["Xã Xuân Châu", "Xã Xuân Thành", "Xã Xuân Thượng", "Xã Xuân Hồng"], "Xã Xuân Hồng"),

    # Huyện Hải Hậu (old Nam Định) - items 45-52
    ("Huyện Hải Hậu", ["Thị trấn Yên Định", "Xã Hải Trung", "Xã Hải Long"], "Xã Hải Hậu"),
    ("Huyện Hải Hậu", ["Xã Hải Minh", "Xã Hải Đường", "Xã Hải Anh"], "Xã Hải Anh"),
    ("Huyện Hải Hậu", ["Thị trấn Cồn", "Xã Hải Sơn", "Xã Hải Tân"], "Xã Hải Tiến"),
    ("Huyện Hải Hậu", ["Xã Hải Nam", "Xã Hải Lộc", "Xã Hải Hưng"], "Xã Hải Hưng"),
    ("Huyện Hải Hậu", ["Xã Hải Phong", "Xã Hải Giang", "Xã Hải An"], "Xã Hải An"),
    ("Huyện Hải Hậu", ["Xã Hải Đông", "Xã Hải Tây", "Xã Hải Quang"], "Xã Hải Quang"),
    ("Huyện Hải Hậu", ["Xã Hải Phú", "Xã Hải Hòa", "Xã Hải Xuân"], "Xã Hải Xuân"),
    ("Huyện Hải Hậu", ["Thị trấn Thịnh Long", "Xã Hải Châu", "Xã Hải Ninh"], "Xã Hải Thịnh"),

    # Huyện Giao Thủy (old Nam Định) - items 53-59
    ("Huyện Giao Thủy", ["Xã Giao Thiện", "Xã Giao Hương", "Xã Giao Thanh"], "Xã Giao Minh"),
    ("Huyện Giao Thủy", ["Xã Hồng Thuận", "Xã Giao An", "Xã Giao Lạc"], "Xã Giao Hòa"),
    ("Huyện Giao Thủy", ["Thị trấn Giao Thủy", "Xã Bình Hòa"], "Xã Giao Thủy"),
    ("Huyện Giao Thủy", ["Xã Giao Xuân", "Xã Giao Hà", "Xã Giao Hải"], "Xã Giao Phúc"),
    ("Huyện Giao Thủy", ["Xã Giao Nhân", "Xã Giao Long", "Xã Giao Châu"], "Xã Giao Hưng"),
    ("Huyện Giao Thủy", ["Xã Giao Yến", "Xã Bạch Long", "Xã Giao Tân"], "Xã Giao Bình"),
    ("Huyện Giao Thủy", ["Thị trấn Quất Lâm", "Xã Giao Phong", "Xã Giao Thịnh"], "Xã Giao Ninh"),

    # Huyện Nghĩa Hưng (old Nam Định) - items 60-66
    ("Huyện Nghĩa Hưng", ["Xã Hoàng Nam", "Xã Đồng Thịnh"], "Xã Đồng Thịnh"),
    ("Huyện Nghĩa Hưng", ["Thị trấn Liễu Đề", "Xã Nghĩa Thái", "Xã Nghĩa Châu", "Xã Nghĩa Trung"], "Xã Nghĩa Hưng"),
    ("Huyện Nghĩa Hưng", ["Xã Nghĩa Lạc", "Xã Nghĩa Sơn"], "Xã Nghĩa Sơn"),
    ("Huyện Nghĩa Hưng", ["Xã Nghĩa Hồng", "Xã Nghĩa Phong", "Xã Nghĩa Phú"], "Xã Hồng Phong"),
    ("Huyện Nghĩa Hưng", ["Thị trấn Quỹ Nhất", "Xã Nghĩa Thành", "Xã Nghĩa Lợi"], "Xã Quỹ Nhất"),
    ("Huyện Nghĩa Hưng", ["Xã Nghĩa Hùng", "Xã Nghĩa Hải", "Xã Nghĩa Lâm"], "Xã Nghĩa Lâm"),
    ("Huyện Nghĩa Hưng", ["Xã Nam Điền", "Xã Phúc Thắng", "Thị trấn Rạng Đông"], "Xã Rạng Đông"),

    # Huyện Gia Viễn (old Ninh Bình) - items 67-72
    ("Huyện Gia Viễn", ["Thị trấn Thịnh Vượng", "Xã Gia Hòa"], "Xã Gia Viễn"),
    ("Huyện Gia Viễn", ["Xã Tiến Thắng", "Xã Gia Phương", "Xã Gia Trung"], "Xã Đại Hoàng"),
    ("Huyện Gia Viễn", ["Xã Liên Sơn", "Xã Gia Phú", "Xã Gia Hưng"], "Xã Gia Hưng"),
    ("Huyện Gia Viễn", ["Xã Gia Lạc", "Xã Gia Minh", "Xã Gia Phong"], "Xã Gia Phong"),
    ("Huyện Gia Viễn", ["Xã Gia Lập", "Xã Gia Vân", "Xã Gia Tân"], "Xã Gia Vân"),
    ("Huyện Gia Viễn", ["Xã Gia Thanh", "Xã Gia Xuân", "Xã Gia Trấn"], "Xã Gia Trấn"),

    # Huyện Nho Quan (old Ninh Bình) - items 73-80
    ("Huyện Nho Quan", ["Thị trấn Nho Quan", "Xã Đồng Phong", "Xã Yên Quang"], "Xã Nho Quan"),
    ("Huyện Nho Quan", ["Xã Gia Sơn", "Xã Xích Thổ", "Xã Gia Lâm"], "Xã Gia Lâm"),
    ("Huyện Nho Quan", ["Xã Gia Thủy", "Xã Đức Long", "Xã Gia Tường"], "Xã Gia Tường"),
    ("Huyện Nho Quan", ["Xã Thạch Bình", "Xã Lạc Vân", "Xã Phú Sơn"], "Xã Phú Sơn"),
    ("Huyện Nho Quan", ["Xã Văn Phương", "Xã Cúc Phương"], "Xã Cúc Phương"),
    ("Huyện Nho Quan", ["Xã Kỳ Phú", "Xã Phú Long"], "Xã Phú Long"),
    ("Huyện Nho Quan", ["Xã Thanh Sơn", "Xã Thượng Hòa", "Xã Văn Phú"], "Xã Thanh Sơn"),
    ("Huyện Nho Quan", ["Xã Phú Lộc", "Xã Quỳnh Lưu"], "Xã Quỳnh Lưu"),

    # Huyện Yên Khánh (old Ninh Bình) - items 81-85
    ("Huyện Yên Khánh", ["Thị trấn Yên Ninh", "Xã Khánh Cư", "Xã Khánh Vân", "Xã Khánh Hải"], "Xã Yên Khánh"),
    ("Huyện Yên Khánh", ["Xã Khánh Hồng", "Xã Khánh Nhạc"], "Xã Khánh Nhạc"),
    ("Huyện Yên Khánh", ["Xã Khánh Cường", "Xã Khánh Lợi", "Xã Khánh Thiện"], "Xã Khánh Thiện"),
    ("Huyện Yên Khánh", ["Xã Khánh Mậu", "Xã Khánh Thủy", "Xã Khánh Hội"], "Xã Khánh Hội"),
    ("Huyện Yên Khánh", ["Xã Khánh Thành", "Xã Khánh Công", "Xã Khánh Trung"], "Xã Khánh Trung"),

    # Huyện Yên Mô (old Ninh Bình) - items 86-90
    ("Huyện Yên Mô", ["Thị trấn Yên Thịnh", "Xã Khánh Dương", "Xã Yên Hòa"], "Xã Yên Mô"),
    ("Huyện Yên Mô", ["Xã Yên Phong", "Xã Yên Nhân", "Xã Yên Từ"], "Xã Yên Từ"),
    ("Huyện Yên Mô", ["Xã Yên Mỹ", "Xã Yên Lâm", "Xã Yên Mạc"], "Xã Yên Mạc"),
    ("Huyện Yên Mô", ["Xã Yên Đồng", "Xã Yên Thành", "Xã Yên Thái"], "Xã Đồng Thái"),
    ("Huyện Yên Mô", ["Xã Xuân Chính", "Xã Hồi Ninh", "Xã Chất Bình"], "Xã Chất Bình"),

    # Huyện Kim Sơn (old Ninh Bình) - items 91-97
    ("Huyện Kim Sơn", ["Xã Kim Định", "Xã Ân Hòa", "Xã Hùng Tiến"], "Xã Kim Sơn"),
    ("Huyện Kim Sơn", ["Xã Như Hòa", "Xã Đồng Hướng", "Xã Quang Thiện"], "Xã Quang Thiện"),
    ("Huyện Kim Sơn", ["Thị trấn Phát Diệm", "Xã Thượng Kiệm", "Xã Kim Chính"], "Xã Phát Diệm"),
    ("Huyện Kim Sơn", ["Xã Yên Lộc", "Xã Tân Thành", "Xã Lai Thành"], "Xã Lai Thành"),
    ("Huyện Kim Sơn", ["Xã Văn Hải", "Xã Kim Tân", "Xã Định Hóa"], "Xã Định Hóa"),
    ("Huyện Kim Sơn", ["Thị trấn Bình Minh", "Xã Cồn Thoi", "Xã Kim Mỹ"], "Xã Bình Minh"),
    ("Huyện Kim Sơn", ["Xã Kim Trung", "Xã Kim Đông"], "Xã Kim Đông"),

    # Thị xã Kim Bảng (old Hà Nam) - items 98-108
    ("Thị xã Kim Bảng", ["Xã Chuyên Ngoại", "Xã Trác Văn", "Xã Yên Nam", "Phường Hòa Mạc"], "Phường Duy Tiên"),
    ("Thị xã Kim Bảng", ["Phường Châu Giang", "Xã Mộc Hoàn", "Phường Hòa Mạc"], "Phường Duy Tân"),
    ("Thị xã Kim Bảng", ["Phường Bạch Thượng", "Phường Yên Bắc", "Phường Đồng Văn"], "Phường Đồng Văn"),
    ("Thị xã Kim Bảng", ["Phường Duy Minh", "Phường Duy Hải", "Phường Hoàng Đông"], "Phường Duy Hà"),
    ("Thị xã Kim Bảng", ["Phường Tiên Sơn", "Phường Tiên Nội", "Xã Tiên Ngoại"], "Phường Tiên Sơn"),
    ("Thị xã Kim Bảng", ["Phường Đại Cương", "Phường Đồng Hoá", "Phường Lê Hồ"], "Phường Lê Hồ"),
    ("Thị xã Kim Bảng", ["Phường Tượng Lĩnh", "Phường Tân Sơn", "Xã Nguyễn Úy"], "Phường Nguyễn Úy"),
    ("Thị xã Kim Bảng", ["Xã Liên Sơn", "Xã Thanh Sơn", "Phường Thi Sơn"], "Phường Lý Thường Kiệt"),
    ("Thị xã Kim Bảng", ["Phường Tân Tựu", "Xã Hoàng Tây"], "Phường Kim Thanh"),
    ("Thị xã Kim Bảng", ["Phường Ba Sao", "Xã Khả Phong", "Xã Thụy Lôi"], "Phường Tam Chúc"),
    ("Thị xã Kim Bảng", ["Phường Quế", "Phường Ngọc Sơn", "Xã Văn Xá"], "Phường Kim Bảng"),

    # Thành phố Phủ Lý (old Hà Nam) - items 109-113
    ("Thành phố Phủ Lý", ["Phường Lam Hạ", "Phường Tân Hiệp", "Phường Quang Trung", "Phường Hoàng Đông", "Phường Tiên Nội", "Xã Tiên Ngoại"], "Phường Hà Nam"),
    ("Thành phố Phủ Lý", ["Phường Lê Hồng Phong", "Xã Kim Bình", "Xã Phù Vân"], "Phường Phù Vân"),
    ("Thành phố Phủ Lý", ["Phường Thanh Tuyền", "Phường Châu Sơn", "Thị trấn Kiện Khê"], "Phường Châu Sơn"),
    ("Thành phố Phủ Lý", ["Phường Châu Cầu", "Phường Thanh Châu", "Phường Liêm Chính", "Phường Quang Trung"], "Phường Phủ Lý"),
    ("Thành phố Phủ Lý", ["Phường Tân Liêm", "Xã Đinh Xá", "Xã Trịnh Xá"], "Phường Liêm Tuyền"),

    # Thành phố Nam Định (old Nam Định) - items 114-121
    ("Thành phố Nam Định", ["Phường Quang Trung", "Phường Vị Xuyên", "Phường Lộc Vượng", "Phường Cửa Bắc", "Phường Trần Hưng Đạo", "Phường Năng Tĩnh", "Phường Cửa Nam", "Xã Mỹ Phúc"], "Phường Nam Định"),
    ("Thành phố Nam Định", ["Phường Lộc Hạ", "Xã Mỹ Tân", "Xã Mỹ Trung"], "Phường Thiên Trường"),
    ("Thành phố Nam Định", ["Phường Lộc Hòa", "Xã Mỹ Thắng", "Xã Mỹ Hà"], "Phường Đông A"),
    ("Thành phố Nam Định", ["Xã Nam Điền", "Phường Nam Phong"], "Phường Vị Khê"),
    ("Thành phố Nam Định", ["Phường Mỹ Xá", "Xã Đại An"], "Phường Thành Nam"),
    ("Thành phố Nam Định", ["Phường Trường Thi", "Xã Thành Lợi"], "Phường Trường Thi"),
    ("Thành phố Nam Định", ["Xã Hồng Quang", "Xã Nghĩa An", "Phường Nam Vân"], "Phường Hồng Quang"),
    ("Thành phố Nam Định", ["Phường Hưng Lộc", "Xã Mỹ Thuận", "Xã Mỹ Lộc"], "Phường Mỹ Lộc"),

    # Thành phố Ninh Bình (old Ninh Bình) - items 122-125
    ("Thành phố Ninh Bình", ["Phường Ninh Giang", "Xã Trường Yên", "Xã Ninh Hòa", "Xã Phúc Sơn", "Xã Gia Sinh", "Xã Gia Tân"], "Phường Tây Hoa Lư"),
    ("Thành phố Ninh Bình", ["Phường Ninh Mỹ", "Phường Ninh Khánh", "Phường Đông Thành", "Phường Tân Thành", "Phường Vân Giang", "Phường Nam Thành", "Phường Nam Bình", "Phường Bích Đào", "Xã Ninh Khang", "Xã Ninh Nhất", "Xã Ninh Tiến"], "Phường Hoa Lư"),
    ("Thành phố Ninh Bình", ["Phường Ninh Phong", "Phường Ninh Sơn", "Xã Ninh Vân", "Xã Ninh An", "Xã Ninh Hải"], "Phường Nam Hoa Lư"),
    ("Thành phố Ninh Bình", ["Phường Ninh Phúc", "Xã Khánh Hòa", "Xã Khánh Phú", "Xã Khánh An"], "Phường Đông Hoa Lư"),

    # Thành phố Tam Điệp (old Ninh Bình) - items 126-129
    ("Thành phố Tam Điệp", ["Phường Bắc Sơn", "Phường Tây Sơn", "Xã Quang Sơn"], "Phường Tam Điệp"),
    ("Thành phố Tam Điệp", ["Phường Tân Bình", "Xã Quảng Lạc", "Xã Yên Sơn"], "Phường Yên Sơn"),
    ("Thành phố Tam Điệp", ["Phường Nam Sơn", "Phường Trung Sơn", "Xã Đông Sơn"], "Phường Trung Sơn"),
    ("Thành phố Tam Điệp", ["Xã Yên Thắng", "Xã Khánh Thượng", "Phường Yên Bình"], "Phường Yên Thắng"),
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

    # Process Ninh Bình
    province_name = "Tỉnh Ninh Bình"
    province_dia_danh, province_chuyen_doi = generate_province_data(
        province_name, ninhbinh_restructuring_data
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
    print(f"\nFinal totals:")
    print(f"  - dia_danh provinces: {len(dia_danh)}")
    print(f"  - chuyen_doi mappings: {len(chuyen_doi)}")

if __name__ == "__main__":
    main()

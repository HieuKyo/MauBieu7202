#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch 10 - Thanh Hóa province data generation script
166 units total: 147 xã and 19 phường
21 xã not being restructured
"""

import json
import os

# Thanh Hóa restructuring data
# Format: (huyện, [list of old units], new unit name)
thanhhoa_restructuring_data = [
    # Huyện Tĩnh Gia (items 1-2)
    ("Huyện Tĩnh Gia", ["Xã Anh Sơn", "Xã Các Sơn"], "Xã Các Sơn"),
    ("Huyện Tĩnh Gia", ["Xã Tân Trường", "Xã Trường Lâm"], "Xã Trường Lâm"),

    # Huyện Hà Trung (items 3-8)
    ("Huyện Hà Trung", ["Xã Hà Đông", "Xã Hà Ngọc", "Xã Yến Sơn", "Thị trấn Hà Trung", "Xã Hà Bình"], "Xã Hà Trung"),
    ("Huyện Hà Trung", ["Thị trấn Hà Lĩnh", "Xã Hà Tiến", "Xã Hà Tân", "Xã Hà Sơn"], "Xã Tống Sơn"),
    ("Huyện Hà Trung", ["Thị trấn Hà Long", "Xã Hà Bắc", "Xã Hà Giang"], "Xã Hà Long"),
    ("Huyện Hà Trung", ["Xã Yên Dương", "Xã Hoạt Giang", "Thị trấn Hà Trung", "Xã Hà Bình"], "Xã Hoạt Giang"),
    ("Huyện Hà Trung", ["Xã Hà Hải", "Xã Hà Châu", "Xã Thái Lai", "Xã Lĩnh Toại"], "Xã Lĩnh Toại"),
    ("Huyện Hà Trung", ["Xã Đại Lộc", "Xã Tiến Lộc", "Xã Triệu Lộc"], "Xã Triệu Lộc"),

    # Huyện Hậu Lộc (items 9-12)
    ("Huyện Hậu Lộc", ["Xã Đồng Lộc", "Xã Thành Lộc", "Xã Cầu Lộc", "Xã Tuy Lộc"], "Xã Đông Thành"),
    ("Huyện Hậu Lộc", ["Thị trấn Hậu Lộc", "Xã Thuần Lộc", "Xã Mỹ Lộc", "Xã Lộc Sơn"], "Xã Hậu Lộc"),
    ("Huyện Hậu Lộc", ["Xã Xuân Lộc", "Xã Liên Lộc", "Xã Quang Lộc", "Xã Phú Lộc", "Xã Hòa Lộc", "Xã Hoa Lộc"], "Xã Hoa Lộc"),
    ("Huyện Hậu Lộc", ["Xã Minh Lộc", "Xã Hải Lộc", "Xã Hưng Lộc", "Xã Ngư Lộc", "Xã Đa Lộc"], "Xã Vạn Lộc"),

    # Huyện Nga Sơn (items 13-18)
    ("Huyện Nga Sơn", ["Thị trấn Nga Sơn", "Xã Nga Yên", "Xã Nga Thanh", "Xã Nga Hiệp", "Xã Nga Thủy"], "Xã Nga Sơn"),
    ("Huyện Nga Sơn", ["Xã Nga Văn", "Xã Nga Phượng", "Xã Nga Thạch", "Xã Nga Thắng"], "Xã Nga Thắng"),
    ("Huyện Nga Sơn", ["Xã Nga Hải", "Xã Nga Thành", "Xã Nga Giáp", "Xã Nga Liên"], "Xã Hồ Vương"),
    ("Huyện Nga Sơn", ["Xã Nga Tiến", "Xã Nga Tân", "Xã Nga Thái"], "Xã Tân Tiến"),
    ("Huyện Nga Sơn", ["Xã Nga Điền", "Xã Nga Phú", "Xã Nga An"], "Xã Nga An"),
    ("Huyện Nga Sơn", ["Xã Nga Vịnh", "Xã Nga Trường", "Xã Nga Thiện", "Xã Ba Đình"], "Xã Ba Đình"),

    # Huyện Hoằng Hóa (items 19-26)
    ("Huyện Hoằng Hóa", ["Thị trấn Bút Sơn", "Xã Hoằng Đức", "Xã Hoằng Đồng", "Xã Hoằng Đạo", "Xã Hoằng Hà", "Xã Hoằng Đạt"], "Xã Hoằng Hóa"),
    ("Huyện Hoằng Hóa", ["Xã Hoằng Yến", "Xã Hoằng Hải", "Xã Hoằng Trường", "Xã Hoằng Tiến"], "Xã Hoằng Tiến"),
    ("Huyện Hoằng Hóa", ["Xã Hoằng Đông", "Xã Hoằng Ngọc", "Xã Hoằng Phụ", "Xã Hoằng Thanh"], "Xã Hoằng Thanh"),
    ("Huyện Hoằng Hóa", ["Xã Hoằng Thịnh", "Xã Hoằng Thái", "Xã Hoằng Thành", "Xã Hoằng Trạch", "Xã Hoằng Tân", "Xã Hoằng Lộc"], "Xã Hoằng Lộc"),
    ("Huyện Hoằng Hóa", ["Xã Hoằng Thắng", "Xã Hoằng Phong", "Xã Hoằng Lưu", "Xã Hoằng Châu"], "Xã Hoằng Châu"),
    ("Huyện Hoằng Hóa", ["Xã Hoằng Trinh", "Xã Hoằng Xuyên", "Xã Hoằng Cát", "Xã Hoằng Sơn"], "Xã Hoằng Sơn"),
    ("Huyện Hoằng Hóa", ["Xã Hoằng Quý", "Xã Hoằng Kim", "Xã Hoằng Trung", "Xã Hoằng Phú"], "Xã Hoằng Phú"),
    ("Huyện Hoằng Hóa", ["Xã Hoằng Xuân", "Xã Hoằng Quỳ", "Xã Hoằng Hợp", "Xã Hoằng Giang"], "Xã Hoằng Giang"),

    # Huyện Quảng Xương (items 27-33)
    ("Huyện Quảng Xương", ["Thị trấn Tân Phong", "Xã Quảng Đức", "Xã Quảng Định"], "Xã Lưu Vệ"),
    ("Huyện Quảng Xương", ["Xã Quảng Trạch", "Xã Quảng Hòa", "Xã Quảng Long", "Xã Quảng Yên"], "Xã Quảng Yên"),
    ("Huyện Quảng Xương", ["Xã Quảng Hợp", "Xã Quảng Văn", "Xã Quảng Phúc", "Xã Quảng Ngọc"], "Xã Quảng Ngọc"),
    ("Huyện Quảng Xương", ["Xã Quảng Nhân", "Xã Quảng Hải", "Xã Quảng Ninh"], "Xã Quảng Ninh"),
    ("Huyện Quảng Xương", ["Xã Quảng Lưu", "Xã Quảng Lộc", "Xã Quảng Thái", "Xã Quảng Bình"], "Xã Quảng Bình"),
    ("Huyện Quảng Xương", ["Xã Quảng Thạch", "Xã Quảng Nham", "Xã Tiên Trang"], "Xã Tiên Trang"),
    ("Huyện Quảng Xương", ["Xã Quảng Trường", "Xã Quảng Khê", "Xã Quảng Trung", "Xã Quảng Chính"], "Xã Quảng Chính"),

    # Huyện Nông Cống (items 34-39)
    ("Huyện Nông Cống", ["Thị trấn Nông Cống", "Xã Vạn Thắng", "Xã Vạn Hòa", "Xã Vạn Thiện", "Xã Minh Nghĩa", "Xã Minh Khôi"], "Xã Nông Cống"),
    ("Huyện Nông Cống", ["Xã Trung Thành", "Xã Tế Nông", "Xã Tế Thắng", "Xã Tế Lợi"], "Xã Thắng Lợi"),
    ("Huyện Nông Cống", ["Xã Tân Phúc", "Xã Tân Thọ", "Xã Tân Khang", "Xã Hoàng Sơn", "Xã Hoàng Giang", "Xã Trung Chính"], "Xã Trung Chính"),
    ("Huyện Nông Cống", ["Xã Trường Minh", "Xã Trường Trung", "Xã Trường Sơn", "Xã Trường Giang"], "Xã Trường Văn"),
    ("Huyện Nông Cống", ["Xã Thăng Long", "Xã Thăng Thọ", "Xã Thăng Bình"], "Xã Thăng Bình"),
    ("Huyện Nông Cống", ["Xã Tượng Sơn", "Xã Tượng Văn", "Xã Tượng Lĩnh"], "Xã Tượng Lĩnh"),

    # Huyện Thiệu Hóa (items 40-45)
    ("Huyện Thiệu Hóa", ["Xã Công Liêm", "Xã Yên Mỹ", "Xã Công Chính", "Xã Thanh Tân"], "Xã Công Chính"),
    ("Huyện Thiệu Hóa", ["Xã Thiệu Phúc", "Xã Thiệu Công", "Xã Thiệu Nguyên", "Thị trấn Thiệu Hóa", "Xã Thiệu Long"], "Xã Thiệu Hóa"),
    ("Huyện Thiệu Hóa", ["Xã Thiệu Duy", "Xã Thiệu Hợp", "Xã Thiệu Thịnh", "Xã Thiệu Giang", "Xã Thiệu Quang", "Thị trấn Thiệu Hóa"], "Xã Thiệu Quang"),
    ("Huyện Thiệu Hóa", ["Xã Thiệu Ngọc", "Xã Thiệu Vũ", "Xã Thiệu Thành", "Xã Thiệu Tiến"], "Xã Thiệu Tiến"),
    ("Huyện Thiệu Hóa", ["Thị trấn Hậu Hiền", "Xã Thiệu Chính", "Xã Thiệu Hòa", "Xã Thiệu Toán"], "Xã Thiệu Toán"),
    ("Huyện Thiệu Hóa", ["Xã Thiệu Vận", "Xã Thiệu Lý", "Xã Thiệu Viên", "Xã Thiệu Trung", "Thị trấn Thiệu Hóa"], "Xã Thiệu Trung"),

    # Huyện Yên Định (items 46-52)
    ("Huyện Yên Định", ["Thị trấn Quán Lào", "Xã Định Liên", "Xã Định Long", "Xã Định Tăng"], "Xã Yên Định"),
    ("Huyện Yên Định", ["Xã Yên Trung", "Xã Yên Phong", "Xã Yên Thái", "Xã Yên Trường"], "Xã Yên Trường"),
    ("Huyện Yên Định", ["Thị trấn Thống Nhất", "Xã Yên Tâm", "Xã Yên Phú"], "Xã Yên Phú"),
    ("Huyện Yên Định", ["Xã Yên Thọ", "Thị trấn Yên Lâm", "Thị trấn Quý Lộc"], "Xã Quý Lộc"),
    ("Huyện Yên Định", ["Xã Yên Hùng", "Xã Yên Thịnh", "Xã Yên Ninh"], "Xã Yên Ninh"),
    ("Huyện Yên Định", ["Xã Định Hải", "Xã Định Hưng", "Xã Định Tiến", "Xã Định Tân"], "Xã Định Tân"),
    ("Huyện Yên Định", ["Xã Định Bình", "Xã Định Công", "Xã Định Thành", "Xã Định Hòa", "Xã Thiệu Long"], "Xã Định Hòa"),

    # Huyện Thọ Xuân (items 53-60)
    ("Huyện Thọ Xuân", ["Thị trấn Thọ Xuân", "Xã Xuân Hồng", "Xã Xuân Trường", "Xã Xuân Giang"], "Xã Thọ Xuân"),
    ("Huyện Thọ Xuân", ["Xã Thọ Lộc", "Xã Xuân Phong", "Xã Nam Giang", "Xã Bắc Lương", "Xã Tây Hồ"], "Xã Thọ Long"),
    ("Huyện Thọ Xuân", ["Xã Xuân Hòa", "Xã Thọ Hải", "Xã Thọ Diên", "Xã Xuân Hưng"], "Xã Xuân Hòa"),
    ("Huyện Thọ Xuân", ["Thị trấn Sao Vàng", "Xã Thọ Lâm", "Xã Xuân Phú", "Xã Xuân Sinh"], "Xã Sao Vàng"),
    ("Huyện Thọ Xuân", ["Thị trấn Lam Sơn", "Xã Xuân Bái", "Xã Thọ Xương"], "Xã Lam Sơn"),
    ("Huyện Thọ Xuân", ["Xã Xuân Thiên", "Xã Thuận Minh", "Xã Thọ Lập"], "Xã Thọ Lập"),
    ("Huyện Thọ Xuân", ["Xã Phú Xuân", "Xã Quảng Phú", "Xã Xuân Tín"], "Xã Xuân Tín"),
    ("Huyện Thọ Xuân", ["Xã Xuân Minh", "Xã Xuân Lai", "Xã Trường Xuân", "Xã Xuân Lập"], "Xã Xuân Lập"),

    # Huyện Vĩnh Lộc (items 61-63)
    ("Huyện Vĩnh Lộc", ["Thị trấn Vĩnh Lộc", "Xã Ninh Khang", "Xã Vĩnh Phúc", "Xã Vĩnh Hưng", "Xã Vĩnh Hòa"], "Xã Vĩnh Lộc"),
    ("Huyện Vĩnh Lộc", ["Xã Vĩnh Quang", "Xã Vĩnh Yên", "Xã Vĩnh Tiến", "Xã Vĩnh Long"], "Xã Tây Đô"),
    ("Huyện Vĩnh Lộc", ["Xã Vĩnh Hùng", "Xã Minh Tân", "Xã Vĩnh Thịnh", "Xã Vĩnh An"], "Xã Biện Thượng"),

    # Huyện Triệu Sơn (items 64-71)
    ("Huyện Triệu Sơn", ["Thị trấn Triệu Sơn", "Xã Minh Sơn", "Xã Dân Lực", "Xã Dân Lý", "Xã Dân Quyền"], "Xã Triệu Sơn"),
    ("Huyện Triệu Sơn", ["Xã Thọ Sơn", "Xã Bình Sơn", "Xã Thọ Bình"], "Xã Thọ Bình"),
    ("Huyện Triệu Sơn", ["Xã Thọ Tiến", "Xã Xuân Thọ", "Xã Thọ Cường", "Xã Thọ Ngọc"], "Xã Thọ Ngọc"),
    ("Huyện Triệu Sơn", ["Xã Xuân Lộc", "Xã Thọ Dân", "Xã Thọ Thế", "Xã Thọ Tân", "Xã Thọ Phú"], "Xã Thọ Phú"),
    ("Huyện Triệu Sơn", ["Xã Hợp Lý", "Xã Hợp Thắng", "Xã Hợp Thành", "Xã Triệu Thành", "Xã Hợp Tiến"], "Xã Hợp Tiến"),
    ("Huyện Triệu Sơn", ["Xã Tiến Nông", "Xã Khuyến Nông", "Xã Nông Trường", "Xã An Nông"], "Xã An Nông"),
    ("Huyện Triệu Sơn", ["Thị trấn Nưa", "Xã Thái Hòa", "Xã Vân Sơn"], "Xã Tân Ninh"),
    ("Huyện Triệu Sơn", ["Xã Đồng Lợi", "Xã Đồng Thắng", "Xã Đồng Tiến"], "Xã Đồng Tiến"),

    # Huyện Quan Hóa (items 72-77)
    ("Huyện Quan Hóa", ["Thị trấn Hồi Xuân", "Xã Phú Nghiêm"], "Xã Hồi Xuân"),
    ("Huyện Quan Hóa", ["Xã Nam Tiến", "Xã Nam Xuân"], "Xã Nam Xuân"),
    ("Huyện Quan Hóa", ["Xã Nam Động", "Xã Thiên Phủ"], "Xã Thiên Phủ"),
    ("Huyện Quan Hóa", ["Xã Hiền Chung", "Xã Hiền Kiệt"], "Xã Hiền Kiệt"),
    ("Huyện Quan Hóa", ["Xã Phú Sơn", "Xã Phú Thanh", "Xã Phú Lệ"], "Xã Phú Lệ"),
    ("Huyện Quan Hóa", ["Xã Thành Sơn", "Xã Trung Thành"], "Xã Trung Thành"),

    # Huyện Quan Sơn (items 78-80)
    ("Huyện Quan Sơn", ["Xã Sơn Hà", "Xã Tam Lư", "Thị trấn Sơn Lư"], "Xã Tam Lư"),
    ("Huyện Quan Sơn", ["Xã Trung Thượng", "Thị trấn Sơn Lư"], "Xã Quan Sơn"),
    ("Huyện Quan Sơn", ["Xã Trung Tiến", "Xã Trung Xuân", "Xã Trung Hạ"], "Xã Trung Hạ"),

    # Huyện Lang Chánh (items 81-84)
    ("Huyện Lang Chánh", ["Thị trấn Lang Chánh", "Xã Trí Nang"], "Xã Linh Sơn"),
    ("Huyện Lang Chánh", ["Xã Tân Phúc", "Xã Đồng Lương"], "Xã Đồng Lương"),
    ("Huyện Lang Chánh", ["Xã Tam Văn", "Xã Lâm Phú"], "Xã Văn Phú"),
    ("Huyện Lang Chánh", ["Xã Giao Thiện", "Xã Giao An"], "Xã Giao An"),

    # Huyện Bá Thước (items 85-92)
    ("Huyện Bá Thước", ["Thị trấn Cành Nàng", "Xã Ban Công", "Xã Hạ Trung"], "Xã Bá Thước"),
    ("Huyện Bá Thước", ["Xã Thiết Kế", "Xã Thiết Ống"], "Xã Thiết Ống"),
    ("Huyện Bá Thước", ["Xã Kỳ Tân", "Xã Văn Nho"], "Xã Văn Nho"),
    ("Huyện Bá Thước", ["Xã Điền Thượng", "Xã Điền Hạ", "Xã Điền Quang"], "Xã Điền Quang"),
    ("Huyện Bá Thước", ["Xã Ái Thượng", "Xã Điền Trung", "Xã Điền Lư"], "Xã Điền Lư"),
    ("Huyện Bá Thước", ["Xã Lương Nội", "Xã Lương Trung", "Xã Lương Ngoại"], "Xã Quý Lương"),
    ("Huyện Bá Thước", ["Xã Lũng Cao", "Xã Cổ Lũng"], "Xã Cổ Lũng"),
    ("Huyện Bá Thước", ["Xã Thành Sơn", "Xã Lũng Niêm", "Xã Thành Lâm"], "Xã Pù Luông"),

    # Huyện Ngọc Lặc (items 93-98)
    ("Huyện Ngọc Lặc", ["Thị trấn Ngọc Lặc", "Xã Mỹ Tân", "Xã Thúy Sơn"], "Xã Ngọc Lặc"),
    ("Huyện Ngọc Lặc", ["Xã Quang Trung", "Xã Đồng Thịnh", "Xã Thạch Lập"], "Xã Thạch Lập"),
    ("Huyện Ngọc Lặc", ["Xã Lộc Thịnh", "Xã Cao Thịnh", "Xã Ngọc Sơn", "Xã Ngọc Trung", "Xã Ngọc Liên"], "Xã Ngọc Liên"),
    ("Huyện Ngọc Lặc", ["Xã Minh Sơn", "Xã Lam Sơn", "Xã Cao Ngọc", "Xã Minh Tiến"], "Xã Minh Sơn"),
    ("Huyện Ngọc Lặc", ["Xã Phùng Giáo", "Xã Vân Am", "Xã Nguyệt Ấn"], "Xã Nguyệt Ấn"),
    ("Huyện Ngọc Lặc", ["Xã Phúc Thịnh", "Xã Phùng Minh", "Xã Kiên Thọ"], "Xã Kiên Thọ"),

    # Huyện Cẩm Thủy (items 99-103)
    ("Huyện Cẩm Thủy", ["Xã Cẩm Thành", "Xã Cẩm Liên", "Xã Cẩm Bình", "Xã Cẩm Thạch"], "Xã Cẩm Thạch"),
    ("Huyện Cẩm Thủy", ["Thị trấn Phong Sơn", "Xã Cẩm Ngọc"], "Xã Cẩm Thủy"),
    ("Huyện Cẩm Thủy", ["Xã Cẩm Quý", "Xã Cẩm Giang", "Xã Cẩm Lương", "Xã Cẩm Tú"], "Xã Cẩm Tú"),
    ("Huyện Cẩm Thủy", ["Xã Cẩm Tâm", "Xã Cẩm Châu", "Xã Cẩm Yên", "Xã Cẩm Vân"], "Xã Cẩm Vân"),
    ("Huyện Cẩm Thủy", ["Xã Cẩm Long", "Xã Cẩm Phú", "Xã Cẩm Tân"], "Xã Cẩm Tân"),

    # Huyện Thạch Thành (items 104-109)
    ("Huyện Thạch Thành", ["Thị trấn Kim Tân", "Xã Thành Hưng", "Xã Thành Thọ", "Xã Thạch Định", "Xã Thành Trực", "Xã Thành Tiến"], "Xã Kim Tân"),
    ("Huyện Thạch Thành", ["Thị trấn Vân Du", "Xã Thành Công", "Xã Thành Tân"], "Xã Vân Du"),
    ("Huyện Thạch Thành", ["Xã Thành An", "Xã Thành Long", "Xã Thành Tâm", "Xã Ngọc Trạo"], "Xã Ngọc Trạo"),
    ("Huyện Thạch Thành", ["Xã Thạch Sơn", "Xã Thạch Long", "Xã Thạch Cẩm", "Xã Thạch Bình"], "Xã Thạch Bình"),
    ("Huyện Thạch Thành", ["Xã Thành Minh", "Xã Thành Mỹ", "Xã Thành Yên", "Xã Thành Vinh"], "Xã Thành Vinh"),
    ("Huyện Thạch Thành", ["Xã Thạch Lâm", "Xã Thạch Tượng", "Xã Thạch Quảng"], "Xã Thạch Quảng"),

    # Huyện Như Xuân (items 110-115)
    ("Huyện Như Xuân", ["Thị trấn Yên Cát", "Xã Tân Bình"], "Xã Như Xuân"),
    ("Huyện Như Xuân", ["Xã Cát Tân", "Xã Cát Vân", "Xã Thượng Ninh"], "Xã Thượng Ninh"),
    ("Huyện Như Xuân", ["Xã Xuân Hòa", "Xã Bãi Trành", "Xã Xuân Bình"], "Xã Xuân Bình"),
    ("Huyện Như Xuân", ["Xã Bình Lương", "Xã Hóa Quỳ"], "Xã Hóa Quỳ"),
    ("Huyện Như Xuân", ["Xã Thanh Hòa", "Xã Thanh Lâm", "Xã Thanh Phong"], "Xã Thanh Phong"),
    ("Huyện Như Xuân", ["Xã Thanh Sơn", "Xã Thanh Xuân", "Xã Thanh Quân"], "Xã Thanh Quân"),

    # Huyện Như Thanh (items 116-120)
    ("Huyện Như Thanh", ["Xã Cán Khê", "Xã Phượng Nghi", "Xã Xuân Du"], "Xã Xuân Du"),
    ("Huyện Như Thanh", ["Xã Phú Nhuận", "Xã Mậu Lâm"], "Xã Mậu Lâm"),
    ("Huyện Như Thanh", ["Thị trấn Bến Sung", "Xã Xuân Khang", "Xã Hải Long", "Xã Yên Thọ"], "Xã Như Thanh"),
    ("Huyện Như Thanh", ["Xã Xuân Phúc", "Xã Yên Lạc", "Xã Yên Thọ"], "Xã Yên Thọ"),
    ("Huyện Như Thanh", ["Xã Thanh Kỳ", "Xã Thanh Tân"], "Xã Thanh Kỳ"),

    # Huyện Thường Xuân (items 121-125)
    ("Huyện Thường Xuân", ["Thị trấn Thường Xuân", "Xã Thọ Thanh", "Xã Ngọc Phụng", "Xã Xuân Dương"], "Xã Thường Xuân"),
    ("Huyện Thường Xuân", ["Xã Xuân Cao", "Xã Luận Thành", "Xã Luận Khê"], "Xã Luận Thành"),
    ("Huyện Thường Xuân", ["Xã Tân Thành", "Xã Luận Khê"], "Xã Tân Thành"),
    ("Huyện Thường Xuân", ["Xã Xuân Lộc", "Xã Xuân Thắng"], "Xã Thắng Lộc"),
    ("Huyện Thường Xuân", ["Xã Xuân Lẹ", "Xã Xuân Chinh"], "Xã Xuân Chinh"),

    # Huyện Mường Lát (item 126)
    ("Huyện Mường Lát", ["Thị trấn Mường Lát"], "Xã Mường Lát"),

    # Thành phố Thanh Hóa (items 127-133)
    ("Thành phố Thanh Hóa", ["Phường Phú Sơn", "Phường Lam Sơn", "Phường Ba Đình", "Phường Ngọc Trạo", "Phường Đông Sơn", "Phường Trường Thi", "Phường Điện Biên", "Phường Đông Hương", "Phường Đông Hải", "Phường Đông Vệ", "Phường Đông Thọ", "Phường An Hưng"], "Phường Hạc Thành"),
    ("Thành phố Thanh Hóa", ["Phường Quảng Hưng", "Phường Quảng Tâm", "Phường Quảng Thành", "Phường Quảng Đông", "Phường Quảng Thịnh", "Phường Quảng Cát", "Phường Quảng Phú"], "Phường Quảng Phú"),
    ("Thành phố Thanh Hóa", ["Phường Quảng Thắng", "Xã Đông Vinh", "Xã Đông Quang", "Xã Đông Yên", "Xã Đông Văn", "Xã Đông Phú", "Xã Đông Nam", "Phường An Hưng"], "Phường Đông Quang"),
    ("Thành phố Thanh Hóa", ["Phường Rừng Thông", "Phường Đông Thịnh", "Phường Đông Tân", "Xã Đông Hòa", "Xã Đông Minh", "Xã Đông Hoàng", "Xã Đông Khê", "Xã Đông Ninh"], "Phường Đông Sơn"),
    ("Thành phố Thanh Hóa", ["Phường Đông Lĩnh", "Phường Thiệu Khánh", "Xã Đông Thanh", "Xã Thiệu Vân", "Xã Tân Châu", "Xã Thiệu Giao", "Xã Đông Tiến"], "Phường Đông Tiến"),
    ("Thành phố Thanh Hóa", ["Phường Thiệu Dương", "Phường Đông Cương", "Phường Nam Ngạn", "Phường Hàm Rồng", "Phường Đông Thọ"], "Phường Hàm Rồng"),
    ("Thành phố Thanh Hóa", ["Phường Tào Xuyên", "Phường Long Anh", "Phường Hoằng Quang", "Phường Hoằng Đại"], "Phường Nguyệt Viên"),

    # Thành phố Sầm Sơn (items 134-135)
    ("Thành phố Sầm Sơn", ["Phường Bắc Sơn", "Phường Quảng Tiến", "Phường Quảng Cư", "Phường Trung Sơn", "Phường Trường Sơn", "Phường Quảng Châu", "Phường Quảng Thọ"], "Phường Sầm Sơn"),
    ("Thành phố Sầm Sơn", ["Phường Quảng Vinh", "Xã Quảng Minh", "Xã Đại Hùng", "Xã Quảng Giao"], "Phường Nam Sầm Sơn"),

    # Thị xã Bỉm Sơn (items 136-137)
    ("Thị xã Bỉm Sơn", ["Phường Đông Sơn", "Phường Lam Sơn", "Phường Ba Đình", "Xã Hà Vinh"], "Phường Bỉm Sơn"),
    ("Thị xã Bỉm Sơn", ["Phường Bắc Sơn", "Phường Ngọc Trạo", "Phường Phú Sơn", "Xã Quang Trung"], "Phường Quang Trung"),

    # Thị xã Nghi Sơn (items 138-145)
    ("Thị xã Nghi Sơn", ["Xã Thanh Sơn", "Xã Thanh Thủy", "Phường Hải Châu", "Phường Hải Ninh"], "Phường Ngọc Sơn"),
    ("Thị xã Nghi Sơn", ["Phường Hải An", "Phường Tân Dân", "Xã Ngọc Lĩnh"], "Phường Tân Dân"),
    ("Thị xã Nghi Sơn", ["Xã Định Hải", "Phường Ninh Hải", "Phường Hải Lĩnh"], "Phường Hải Lĩnh"),
    ("Thị xã Nghi Sơn", ["Phường Hải Hòa", "Phường Bình Minh", "Phường Hải Thanh", "Xã Hải Nhân"], "Phường Tĩnh Gia"),
    ("Thị xã Nghi Sơn", ["Phường Nguyên Bình", "Phường Xuân Lâm"], "Phường Đào Duy Từ"),
    ("Thị xã Nghi Sơn", ["Phường Mai Lâm", "Phường Tĩnh Hải", "Phường Hải Bình"], "Phường Hải Bình"),
    ("Thị xã Nghi Sơn", ["Phường Trúc Lâm", "Xã Phú Sơn", "Xã Phú Lâm", "Xã Tùng Lâm"], "Phường Trúc Lâm"),
    ("Thị xã Nghi Sơn", ["Phường Hải Thượng", "Xã Hải Hà", "Xã Nghi Sơn"], "Phường Nghi Sơn"),
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

    # Process Thanh Hóa
    tinh_name = "Tỉnh Thanh Hóa"

    print(f"Processing {tinh_name}...")

    # Generate entries
    dia_danh_entry = generate_dia_danh_entry(tinh_name, thanhhoa_restructuring_data)
    chuyen_doi_entries = generate_chuyen_doi_entries(tinh_name, thanhhoa_restructuring_data)

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

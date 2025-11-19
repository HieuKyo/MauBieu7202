#!/usr/bin/env python3
"""
Generate province restructuring data for Batch 6:
Hưng Yên (mới), Huế, Khánh Hòa, Lai Châu, Lâm Đồng, Lạng Sơn, Lào Cai
"""

import json
import os

# Hưng Yên (mới) restructuring data - combines Hưng Yên and Thái Bình
# Items 1-33: Hưng Yên districts, items 34-104: Thái Bình districts
hungyen_restructuring_data = [
    # Huyện Tiên Lữ - items 1-4
    ("Huyện Tiên Lữ", ["Xã Thủ Sỹ", "Xã Phương Nam", "Xã Tân Hưng"], "Xã Tân Hưng"),
    ("Huyện Tiên Lữ", ["Thị trấn Vương", "Xã Hưng Đạo", "Xã Nhật Tân", "Xã An Viên"], "Xã Hoàng Hoa Thám"),
    ("Huyện Tiên Lữ", ["Xã Thiện Phiến", "Xã Hải Thắng", "Xã Thụy Lôi"], "Xã Tiên Lữ"),
    ("Huyện Tiên Lữ", ["Xã Lệ Xá", "Xã Trung Dũng", "Xã Cương Chính"], "Xã Tiên Hoa"),

    # Huyện Phù Cừ - items 5-8
    ("Huyện Phù Cừ", ["Thị trấn Trần Cao", "Xã Minh Tân", "Xã Tống Phan", "Xã Quang Hưng"], "Xã Quang Hưng"),
    ("Huyện Phù Cừ", ["Xã Phan Sào Nam", "Xã Minh Hoàng", "Xã Đoàn Đào"], "Xã Đoàn Đào"),
    ("Huyện Phù Cừ", ["Xã Đình Cao", "Xã Nhật Quang", "Xã Tiên Tiến"], "Xã Tiên Tiến"),
    ("Huyện Phù Cừ", ["Xã Tam Đa", "Xã Nguyên Hòa", "Xã Tống Trân"], "Xã Tống Trân"),

    # Huyện Kim Động - items 9-12
    ("Huyện Kim Động", ["Thị trấn Lương Bằng", "Xã Phạm Ngũ Lão", "Xã Chính Nghĩa", "Xã Diên Hồng"], "Xã Lương Bằng"),
    ("Huyện Kim Động", ["Xã Đồng Thanh", "Xã Vĩnh Xá", "Xã Toàn Thắng", "Xã Nghĩa Dân"], "Xã Nghĩa Dân"),
    ("Huyện Kim Động", ["Xã Song Mai", "Xã Hùng An", "Xã Hiệp Cường", "Xã Ngọc Thanh"], "Xã Hiệp Cường"),
    ("Huyện Kim Động", ["Xã Phú Thọ", "Xã Mai Động", "Xã Đức Hợp"], "Xã Đức Hợp"),

    # Huyện Ân Thi - items 13-17
    ("Huyện Ân Thi", ["Thị trấn Ân Thi", "Xã Quang Vinh", "Xã Hoàng Hoa Thám"], "Xã Ân Thi"),
    ("Huyện Ân Thi", ["Xã Vân Du", "Xã Quảng Lãng", "Xã Xuân Trúc"], "Xã Xuân Trúc"),
    ("Huyện Ân Thi", ["Xã Bắc Sơn", "Xã Phù Ủng", "Xã Đào Dương", "Xã Bãi Sậy"], "Xã Phạm Ngũ Lão"),
    ("Huyện Ân Thi", ["Xã Đặng Lễ", "Xã Cẩm Ninh", "Xã Đa Lộc", "Xã Nguyễn Trãi"], "Xã Nguyễn Trãi"),
    ("Huyện Ân Thi", ["Xã Hồ Tùng Mậu", "Xã Tiền Phong", "Xã Hạ Lễ", "Xã Hồng Quang"], "Xã Hồng Quang"),

    # Huyện Khoái Châu - items 18-22
    ("Huyện Khoái Châu", ["Thị trấn Khoái Châu", "Xã Liên Khê", "Xã Phùng Hưng", "Xã Đông Kết"], "Xã Khoái Châu"),
    ("Huyện Khoái Châu", ["Xã Phạm Hồng Thái", "Xã Tân Dân", "Xã Ông Đình", "Xã An Vĩ"], "Xã Triệu Việt Vương"),
    ("Huyện Khoái Châu", ["Xã Đồng Tiến", "Xã Dân Tiến", "Xã Việt Hòa"], "Xã Việt Tiến"),
    ("Huyện Khoái Châu", ["Xã Thuần Hưng", "Xã Nguyễn Huệ", "Xã Chí Minh"], "Xã Chí Minh"),
    ("Huyện Khoái Châu", ["Xã Đại Tập", "Xã Tứ Dân", "Xã Tân Châu", "Xã Đông Ninh"], "Xã Châu Ninh"),

    # Huyện Yên Mỹ - items 23-26
    ("Huyện Yên Mỹ", ["Thị trấn Yên Mỹ", "Xã Tân Lập", "Xã Trung Hòa", "Xã Tân Minh"], "Xã Yên Mỹ"),
    ("Huyện Yên Mỹ", ["Xã Yên Phú", "Xã Thanh Long", "Xã Việt Yên"], "Xã Việt Yên"),
    ("Huyện Yên Mỹ", ["Xã Đông Tảo", "Xã Đồng Than", "Xã Hoàn Long"], "Xã Hoàn Long"),
    ("Huyện Yên Mỹ", ["Xã Ngọc Long", "Xã Liêu Xá", "Xã Nguyễn Văn Linh"], "Xã Nguyễn Văn Linh"),

    # Huyện Văn Lâm - items 27-29
    ("Huyện Văn Lâm", ["Thị trấn Như Quỳnh", "Xã Tân Quang", "Xã Lạc Hồng", "Xã Trưng Trắc", "Xã Đình Dù"], "Xã Như Quỳnh"),
    ("Huyện Văn Lâm", ["Xã Chỉ Đạo", "Xã Minh Hải", "Xã Lạc Đạo"], "Xã Lạc Đạo"),
    ("Huyện Văn Lâm", ["Xã Việt Hưng", "Xã Lương Tài", "Xã Đại Đồng", "Xã Đình Dù", "Xã Lạc Đạo"], "Xã Đại Đồng"),

    # Huyện Văn Giang - items 30-33
    ("Huyện Văn Giang", ["Xã Long Hưng", "Xã Vĩnh Khúc", "Xã Nghĩa Trụ"], "Xã Nghĩa Trụ"),
    ("Huyện Văn Giang", ["Xã Xuân Quan", "Xã Cửu Cao", "Xã Phụng Công"], "Xã Phụng Công"),
    ("Huyện Văn Giang", ["Xã Tân Tiến", "Xã Liên Nghĩa", "Thị trấn Văn Giang"], "Xã Văn Giang"),
    ("Huyện Khoái Châu", ["Xã Bình Minh", "Xã Thắng Lợi", "Xã Mễ Sở"], "Xã Mễ Sở"),

    # Huyện Thái Thụy - items 34-44
    ("Huyện Thái Thụy", ["Thị trấn Diêm Điền", "Xã Thụy Hải", "Xã Thụy Trình", "Xã Thụy Bình", "Xã Thụy Liên"], "Xã Thái Thụy"),
    ("Huyện Thái Thụy", ["Xã Thụy Trường", "Xã Thụy Xuân", "Xã An Tân", "Xã Hồng Dũng"], "Xã Đông Thụy Anh"),
    ("Huyện Thái Thụy", ["Xã Thụy Quỳnh", "Xã Thụy Văn", "Xã Thụy Việt"], "Xã Bắc Thụy Anh"),
    ("Huyện Thái Thụy", ["Xã Thụy Sơn", "Xã Dương Phúc", "Xã Thụy Hưng"], "Xã Thụy Anh"),
    ("Huyện Thái Thụy", ["Xã Thụy Thanh", "Xã Thụy Phong", "Xã Thụy Duyên"], "Xã Nam Thụy Anh"),
    ("Huyện Thái Thụy", ["Xã Thái Phúc", "Xã Dương Hồng Thủy"], "Xã Bắc Thái Ninh"),
    ("Huyện Thái Thụy", ["Xã Thái Hưng", "Xã Thái Thượng", "Xã Hòa An", "Xã Thái Nguyên"], "Xã Thái Ninh"),
    ("Huyện Thái Thụy", ["Xã Mỹ Lộc", "Xã Tân Học", "Xã Thái Đô", "Xã Thái Xuyên"], "Xã Đông Thái Ninh"),
    ("Huyện Thái Thụy", ["Xã Thái Thọ", "Xã Thái Thịnh", "Xã Thuần Thành"], "Xã Nam Thái Ninh"),
    ("Huyện Thái Thụy", ["Xã Sơn Hà", "Xã Thái Giang"], "Xã Tây Thái Ninh"),
    ("Huyện Thái Thụy", ["Xã Thụy Chính", "Xã Thụy Dân", "Xã Thụy Ninh"], "Xã Tây Thụy Anh"),

    # Huyện Tiền Hải - items 45-52
    ("Huyện Tiền Hải", ["Thị trấn Tiền Hải", "Xã An Ninh", "Xã Tây Ninh", "Xã Tây Lương", "Xã Vũ Lăng"], "Xã Tiền Hải"),
    ("Huyện Tiền Hải", ["Xã Phương Công", "Xã Vân Trường", "Xã Bắc Hải"], "Xã Tây Tiền Hải"),
    ("Huyện Tiền Hải", ["Xã Tây Giang", "Xã Ái Quốc"], "Xã Ái Quốc"),
    ("Huyện Tiền Hải", ["Xã Đông Hoàng", "Xã Đông Cơ", "Xã Đông Lâm", "Xã Đông Minh"], "Xã Đồng Châu"),
    ("Huyện Tiền Hải", ["Xã Đông Xuyên", "Xã Đông Quang", "Xã Đông Long", "Xã Đông Trà"], "Xã Đông Tiền Hải"),
    ("Huyện Tiền Hải", ["Xã Nam Thịnh", "Xã Nam Tiến", "Xã Nam Chính", "Xã Nam Cường"], "Xã Nam Cường"),
    ("Huyện Tiền Hải", ["Xã Nam Phú", "Xã Nam Hưng", "Xã Nam Trung"], "Xã Hưng Phú"),
    ("Huyện Tiền Hải", ["Xã Nam Hồng", "Xã Nam Hà", "Xã Nam Hải"], "Xã Nam Tiền Hải"),

    # Huyện Đông Hưng - items 53-61
    ("Huyện Đông Hưng", ["Thị trấn Đông Hưng", "Xã Nguyên Xá", "Xã Đông La", "Xã Đông Các", "Xã Đông Sơn", "Xã Đông Hợp"], "Xã Đông Hưng"),
    ("Huyện Đông Hưng", ["Xã Liên An Đô", "Xã Lô Giang", "Xã Mê Linh", "Xã Phú Lương"], "Xã Bắc Tiên Hưng"),
    ("Huyện Đông Hưng", ["Xã Phong Dương Tiến", "Xã Phú Châu"], "Xã Đông Tiên Hưng"),
    ("Huyện Đông Hưng", ["Xã Đông Hoàng", "Xã Xuân Quang Động"], "Xã Nam Đông Hưng"),
    ("Huyện Đông Hưng", ["Xã Hà Giang", "Xã Đông Kinh", "Xã Đông Vinh"], "Xã Bắc Đông Quan"),
    ("Huyện Đông Hưng", ["Xã Đông Cường", "Xã Đông Xá", "Xã Đông Phương"], "Xã Bắc Đông Hưng"),
    ("Huyện Đông Hưng", ["Xã Đông Á", "Xã Đông Tân", "Xã Đông Quan"], "Xã Đông Quan"),
    ("Huyện Đông Hưng", ["Xã Liên Hoa", "Xã Hồng Giang", "Xã Trọng Quan", "Xã Minh Phú"], "Xã Nam Tiên Hưng"),
    ("Huyện Đông Hưng", ["Xã Minh Tân", "Xã Hồng Bạch", "Xã Thăng Long", "Xã Hồng Việt"], "Xã Tiên Hưng"),

    # Huyện Quỳnh Phụ - items 62-70
    ("Huyện Quỳnh Phụ", ["Thị trấn Quỳnh Côi", "Xã Quỳnh Hải", "Xã Quỳnh Hội", "Xã Quỳnh Hồng", "Xã Quỳnh Mỹ", "Xã Quỳnh Hưng"], "Xã Quỳnh Phụ"),
    ("Huyện Quỳnh Phụ", ["Xã Quỳnh Hoa", "Xã Quỳnh Minh", "Xã Quỳnh Giao", "Xã Quỳnh Thọ"], "Xã Minh Thọ"),
    ("Huyện Quỳnh Phụ", ["Xã Châu Sơn", "Xã Quỳnh Khê", "Xã Quỳnh Nguyên"], "Xã Nguyễn Du"),
    ("Huyện Quỳnh Phụ", ["Xã Trang Bảo Xá", "Xã An Vinh", "Xã Đông Hải"], "Xã Quỳnh An"),
    ("Huyện Quỳnh Phụ", ["Xã Quỳnh Hoàng", "Xã Quỳnh Lâm", "Xã Quỳnh Ngọc"], "Xã Ngọc Lâm"),
    ("Huyện Quỳnh Phụ", ["Xã An Cầu", "Xã An Ấp", "Xã An Lễ", "Xã An Quý"], "Xã Đồng Bằng"),
    ("Huyện Quỳnh Phụ", ["Xã An Đồng", "Xã An Hiệp", "Xã An Thái", "Xã An Khê"], "Xã A Sào"),
    ("Huyện Quỳnh Phụ", ["Thị trấn An Bài", "Xã An Ninh", "Xã An Vũ", "Xã An Mỹ", "Xã An Thanh"], "Xã Phụ Dực"),
    ("Huyện Quỳnh Phụ", ["Xã Đồng Tiến", "Xã An Dục", "Xã An Tràng"], "Xã Tân Tiến"),

    # Huyện Hưng Hà - items 71-78
    ("Huyện Hưng Hà", ["Xã Hòa Bình", "Xã Minh Khai", "Xã Thống Nhất", "Xã Kim Trung", "Xã Hồng Lĩnh", "Xã Văn Lang", "Thị trấn Hưng Hà"], "Xã Hưng Hà"),
    ("Huyện Hưng Hà", ["Xã Tân Tiến", "Xã Thái Phương", "Xã Đoan Hùng", "Xã Phúc Khánh"], "Xã Tiên La"),
    ("Huyện Hưng Hà", ["Xã Minh Tân", "Xã Độc Lập", "Xã Hồng An"], "Xã Lê Quý Đôn"),
    ("Huyện Hưng Hà", ["Xã Chí Hòa", "Xã Minh Hòa", "Xã Hồng Minh"], "Xã Hồng Minh"),
    ("Huyện Hưng Hà", ["Xã Bắc Sơn", "Xã Đông Đô", "Xã Tây Đô", "Xã Chi Lăng"], "Xã Thần Khê"),
    ("Huyện Hưng Hà", ["Xã Quang Trung", "Xã Văn Cẩm", "Xã Duyên Hải"], "Xã Diên Hà"),
    ("Huyện Hưng Hà", ["Xã Tân Hòa", "Xã Canh Tân", "Xã Cộng Hòa", "Xã Hòa Tiến"], "Xã Ngự Thiên"),
    ("Huyện Hưng Hà", ["Thị trấn Hưng Nhân", "Xã Thái Hưng", "Xã Tân Lễ", "Xã Tiến Đức", "Xã Liên Hiệp"], "Xã Long Hưng"),

    # Huyện Kiến Xương - items 79-87
    ("Huyện Kiến Xương", ["Xã Bình Minh", "Xã Quang Trung", "Xã Quang Minh", "Xã Quang Bình", "Thị trấn Kiến Xương"], "Xã Kiến Xương"),
    ("Huyện Kiến Xương", ["Xã Thống Nhất", "Xã Lê Lợi"], "Xã Lê Lợi"),
    ("Huyện Kiến Xương", ["Xã Hòa Bình", "Xã Vũ Lễ", "Xã Quang Lịch"], "Xã Quang Lịch"),
    ("Huyện Kiến Xương", ["Xã Vũ An", "Xã Vũ Ninh", "Xã Vũ Trung", "Xã Vũ Quý"], "Xã Vũ Quý"),
    ("Huyện Kiến Xương", ["Xã Minh Tân", "Xã Minh Quang", "Xã Bình Thanh"], "Xã Bình Thanh"),
    ("Huyện Kiến Xương", ["Xã Hồng Tiến", "Xã Nam Bình", "Xã Bình Định"], "Xã Bình Định"),
    ("Huyện Kiến Xương", ["Xã Vũ Công", "Xã Hồng Vũ"], "Xã Hồng Vũ"),
    ("Huyện Kiến Xương", ["Xã Thanh Tân", "Xã An Bình", "Xã Bình Nguyên"], "Xã Bình Nguyên"),
    ("Huyện Kiến Xương", ["Xã Hồng Thái", "Xã Quốc Tuấn", "Xã Trà Giang"], "Xã Trà Giang"),

    # Huyện Vũ Thư - items 88-93
    ("Huyện Vũ Thư", ["Xã Hòa Bình", "Xã Minh Khai", "Xã Minh Quang", "Xã Tam Quang", "Xã Dũng Nghĩa", "Thị trấn Vũ Thư"], "Xã Vũ Thư"),
    ("Huyện Vũ Thư", ["Xã Song Lãng", "Xã Hiệp Hòa", "Xã Minh Lãng"], "Xã Thư Trì"),
    ("Huyện Vũ Thư", ["Xã Tân Lập", "Xã Tự Tân", "Xã Bách Thuận"], "Xã Tân Thuận"),
    ("Huyện Vũ Thư", ["Xã Việt Thuận", "Xã Vũ Hội", "Xã Vũ Vinh", "Xã Vũ Vân"], "Xã Thư Vũ"),
    ("Huyện Vũ Thư", ["Xã Vũ Đoài", "Xã Duy Nhất", "Xã Hồng Phong", "Xã Vũ Tiến"], "Xã Vũ Tiên"),
    ("Huyện Vũ Thư", ["Xã Đồng Thanh", "Xã Hồng Lý", "Xã Việt Hùng", "Xã Xuân Hòa"], "Xã Vạn Xuân"),

    # Thành phố Hưng Yên - items 94-96
    ("Thành phố Hưng Yên", ["Phường An Tảo", "Phường Lê Lợi", "Phường Hiến Nam", "Phường Minh Khai", "Xã Trung Nghĩa", "Xã Liên Phương"], "Phường Phố Hiến"),
    ("Thành phố Hưng Yên", ["Phường Lam Sơn", "Xã Phú Cường", "Xã Hùng Cường", "Xã Bảo Khê", "Xã Ngọc Thanh"], "Phường Sơn Nam"),
    ("Thành phố Hưng Yên", ["Phường Hồng Châu", "Xã Quảng Châu", "Xã Hoàng Hanh"], "Phường Hồng Châu"),

    # Thị xã Mỹ Hào - items 97-99
    ("Thị xã Mỹ Hào", ["Phường Bần Yên Nhân", "Phường Nhân Hòa", "Phường Phan Đình Phùng", "Xã Cẩm Xá"], "Phường Mỹ Hào"),
    ("Thị xã Mỹ Hào", ["Phường Dị Sử", "Phường Phùng Chí Kiên", "Xã Xuân Dục", "Xã Hưng Long", "Xã Ngọc Lâm"], "Phường Đường Hào"),
    ("Thị xã Mỹ Hào", ["Phường Bạch Sam", "Phường Minh Đức", "Xã Dương Quang", "Xã Hòa Phong"], "Phường Thượng Hồng"),

    # Thành phố Thái Bình - items 100-104
    ("Thành phố Thái Bình", ["Phường Lê Hồng Phong", "Phường Bồ Xuyên", "Phường Tiền Phong", "Xã Tân Hòa", "Xã Phúc Thành", "Xã Tân Phong", "Xã Tân Bình"], "Phường Thái Bình"),
    ("Thành phố Thái Bình", ["Phường Trần Lãm", "Phường Kỳ Bá", "Xã Vũ Đông", "Xã Vũ Lạc", "Xã Vũ Chính", "Xã Tây Sơn"], "Phường Trần Lãm"),
    ("Thành phố Thái Bình", ["Phường Trần Hưng Đạo", "Phường Đề Thám", "Phường Quang Trung", "Xã Phú Xuân"], "Phường Trần Hưng Đạo"),
    ("Thành phố Thái Bình", ["Phường Hoàng Diệu", "Xã Đông Mỹ", "Xã Đông Hoà", "Xã Đông Thọ", "Xã Đông Dương"], "Phường Trà Lý"),
    ("Thành phố Thái Bình", ["Phường Phú Khánh", "Xã Nguyên Xá", "Xã Song An", "Xã Trung An", "Xã Vũ Phúc"], "Phường Vũ Phúc"),
]

# Huế restructuring data (39 items)
hue_restructuring_data = [
    # Items 1-5: Huyện Phong Điền
    ("Huyện Phong Điền", ["Phường Phong Thu", "Xã Phong Mỹ", "Xã Phong Xuân"], "Phường Phong Điền"),
    ("Huyện Phong Điền", ["Phường Phong An", "Phường Phong Hiền", "Xã Phong Sơn"], "Phường Phong Thái"),
    ("Huyện Phong Điền", ["Phường Phong Hòa", "Xã Phong Bình", "Xã Phong Chương"], "Phường Phong Dinh"),
    ("Huyện Phong Điền", ["Phường Phong Phú", "Xã Phong Thạnh"], "Phường Phong Phú"),
    ("Huyện Phong Điền", ["Phường Phong Hải", "Xã Quảng Công", "Xã Quảng Ngạn"], "Phường Phong Quảng"),

    # Items 6-9: Thị xã Hương Trà / Thành phố Huế
    ("Thị xã Hương Trà", ["Phường Tứ Hạ", "Phường Hương Văn", "Phường Hương Vân"], "Phường Hương Trà"),
    ("Thị xã Hương Trà", ["Phường Hương Xuân", "Phường Hương Chữ", "Xã Hương Toàn"], "Phường Kim Trà"),
    ("Thành phố Huế", ["Phường Long Hồ", "Phường Hương Long", "Phường Kim Long"], "Phường Kim Long"),
    ("Thành phố Huế", ["Phường An Hòa", "Phường Hương Sơ", "Phường Hương An"], "Phường Hương An"),

    # Items 10-12: Thành phố Huế
    ("Thành phố Huế", ["Phường Gia Hội", "Phường Phú Hậu", "Phường Tây Lộc", "Phường Thuận Lộc", "Phường Thuận Hòa", "Phường Đông Ba"], "Phường Phú Xuân"),
    ("Thành phố Huế", ["Phường Thuận An", "Xã Phú Hải", "Xã Phú Thuận"], "Phường Thuận An"),
    ("Thành phố Huế", ["Phường Hương Phong", "Phường Hương Vinh", "Xã Quảng Thành"], "Phường Hóa Châu"),

    # Items 13-20: Thành phố Huế / Thị xã Hương Thủy
    ("Thành phố Huế", ["Phường Phú Thượng", "Xã Phú An", "Xã Phú Mỹ"], "Phường Mỹ Thượng"),
    ("Thành phố Huế", ["Phường Thủy Vân", "Phường Xuân Phú", "Phường Vỹ Dạ"], "Phường Vỹ Dạ"),
    ("Thành phố Huế", ["Phường Phú Hội", "Phường Phú Nhuận", "Phường Phường Đúc", "Phường Vĩnh Ninh", "Phường Phước Vĩnh", "Phường Trường An"], "Phường Thuận Hóa"),
    ("Thành phố Huế", ["Phường An Đông", "Phường An Tây", "Phường An Cựu"], "Phường An Cựu"),
    ("Thành phố Huế", ["Phường Thủy Biều", "Phường Thủy Bằng", "Phường Thủy Xuân"], "Phường Thủy Xuân"),
    ("Thị xã Hương Thủy", ["Phường Thủy Dương", "Phường Thủy Phương", "Xã Thủy Thanh"], "Phường Thanh Thủy"),
    ("Thị xã Hương Thủy", ["Phường Thủy Lương", "Phường Thủy Châu", "Xã Thủy Tân"], "Phường Hương Thủy"),
    ("Thị xã Hương Thủy", ["Phường Phú Bài", "Xã Thủy Phù", "Xã Phú Sơn", "Xã Dương Hòa"], "Phường Phú Bài"),

    # Items 21-31: Huyện Quảng Điền, Phú Vang, Phú Lộc
    ("Huyện Quảng Điền", ["Xã Quảng Thái", "Xã Quảng Lợi", "Xã Quảng Vinh", "Xã Quảng Phú"], "Xã Đan Điền"),
    ("Huyện Quảng Điền", ["Thị trấn Sịa", "Xã Quảng Phước", "Xã Quảng An", "Xã Quảng Thọ"], "Xã Quảng Điền"),
    ("Thị xã Hương Trà", ["Xã Hương Bình", "Xã Bình Thành", "Xã Bình Tiến"], "Xã Bình Điền"),
    ("Huyện Phú Vang", ["Xã Phú Diên", "Xã Vinh Xuân", "Xã Vinh An", "Xã Vinh Thanh"], "Xã Phú Vinh"),
    ("Huyện Phú Vang", ["Xã Phú Xuân", "Xã Phú Lương", "Xã Phú Hồ"], "Xã Phú Hồ"),
    ("Huyện Phú Vang", ["Thị trấn Phú Đa", "Xã Phú Gia", "Xã Vinh Hà"], "Xã Phú Vang"),
    ("Huyện Phú Vang", ["Xã Vinh Hưng", "Xã Vinh Mỹ", "Xã Giang Hải", "Xã Vinh Hiền"], "Xã Vinh Lộc"),
    ("Huyện Phú Lộc", ["Thị trấn Lộc Sơn", "Xã Lộc Bổn", "Xã Xuân Lộc"], "Xã Hưng Lộc"),
    ("Huyện Phú Lộc", ["Xã Lộc Hòa", "Xã Lộc Điền", "Xã Lộc An"], "Xã Lộc An"),
    ("Huyện Phú Lộc", ["Thị trấn Phú Lộc", "Xã Lộc Trì", "Xã Lộc Bình"], "Xã Phú Lộc"),
    ("Huyện Phú Lộc", ["Thị trấn Lăng Cô", "Xã Lộc Tiến", "Xã Lộc Vĩnh", "Xã Lộc Thủy"], "Xã Chân Mây - Lăng Cô"),

    # Items 32-39: Huyện Nam Đông, A Lưới
    ("Huyện Nam Đông", ["Xã Thượng Quảng", "Xã Thượng Long", "Xã Hương Hữu"], "Xã Long Quảng"),
    ("Huyện Nam Đông", ["Xã Hương Xuân", "Xã Thượng Nhật", "Xã Hương Sơn"], "Xã Nam Đông"),
    ("Huyện Nam Đông", ["Thị trấn Khe Tre", "Xã Hương Phú", "Xã Hương Lộc", "Xã Thượng Lộ"], "Xã Khe Tre"),
    ("Huyện A Lưới", ["Xã Hồng Thủy", "Xã Hồng Vân", "Xã Trung Sơn", "Xã Hồng Kim"], "Xã A Lưới 1"),
    ("Huyện A Lưới", ["Thị trấn A Lưới", "Xã Hồng Bắc", "Xã Quảng Nhâm", "Xã A Ngo"], "Xã A Lưới 2"),
    ("Huyện A Lưới", ["Xã Sơn Thủy", "Xã Hồng Thượng", "Xã Phú Vinh", "Xã Hồng Thái"], "Xã A Lưới 3"),
    ("Huyện A Lưới", ["Xã Hương Phong", "Xã A Roàng", "Xã Đông Sơn", "Xã Lâm Đớt"], "Xã A Lưới 4"),
    ("Huyện A Lưới", ["Xã Hương Nguyên", "Xã Hồng Hạ"], "Xã A Lưới 5"),
]

# Khánh Hòa restructuring data (65 items)
khanhhoa_restructuring_data = [
    # Thành phố Cam Ranh - item 1
    ("Thành phố Cam Ranh", ["Xã Cam Lập", "Xã Cam Bình", "Xã Cam Thịnh Đông", "Xã Cam Thịnh Tây"], "Xã Nam Cam Ranh"),

    # Thị xã Ninh Hòa - items 2-6
    ("Thị xã Ninh Hòa", ["Xã Ninh An", "Xã Ninh Sơn", "Xã Ninh Thọ"], "Xã Bắc Ninh Hòa"),
    ("Thị xã Ninh Hòa", ["Xã Ninh Xuân", "Xã Ninh Quang", "Xã Ninh Bình"], "Xã Tân Định"),
    ("Thị xã Ninh Hòa", ["Xã Ninh Lộc", "Xã Ninh Ích", "Xã Ninh Hưng", "Xã Ninh Tân"], "Xã Nam Ninh Hòa"),
    ("Thị xã Ninh Hòa", ["Xã Ninh Tây", "Xã Ninh Sim"], "Xã Tây Ninh Hòa"),
    ("Thị xã Ninh Hòa", ["Xã Ninh Thượng", "Xã Ninh Trung", "Xã Ninh Thân"], "Xã Hòa Trí"),

    # Huyện Vạn Ninh - items 7-11
    ("Huyện Vạn Ninh", ["Xã Vạn Thạnh", "Xã Vạn Thọ", "Xã Đại Lãnh"], "Xã Đại Lãnh"),
    ("Huyện Vạn Ninh", ["Xã Vạn Khánh", "Xã Vạn Long", "Xã Vạn Phước"], "Xã Tu Bông"),
    ("Huyện Vạn Ninh", ["Xã Vạn Bình", "Xã Vạn Thắng"], "Xã Vạn Thắng"),
    ("Huyện Vạn Ninh", ["Thị trấn Vạn Giã", "Xã Vạn Phú", "Xã Vạn Lương"], "Xã Vạn Ninh"),
    ("Huyện Vạn Ninh", ["Xã Xuân Sơn", "Xã Vạn Hưng"], "Xã Vạn Hưng"),

    # Huyện Diên Khánh - items 12-16
    ("Huyện Diên Khánh", ["Thị trấn Diên Khánh", "Xã Diên An", "Xã Diên Toàn"], "Xã Diên Khánh"),
    ("Huyện Diên Khánh", ["Xã Diên Thạnh", "Xã Diên Lạc", "Xã Diên Hòa"], "Xã Diên Lạc"),
    ("Huyện Diên Khánh", ["Xã Diên Sơn", "Xã Diên Phú", "Xã Diên Điền"], "Xã Diên Điền"),
    ("Huyện Diên Khánh", ["Xã Xuân Đồng", "Xã Diên Lâm"], "Xã Diên Lâm"),
    ("Huyện Diên Khánh", ["Xã Diên Tân", "Xã Diên Phước", "Xã Diên Thọ"], "Xã Diên Thọ"),

    # Huyện Cam Lâm - items 17-21
    ("Huyện Cam Lâm", ["Xã Suối Tiên", "Xã Bình Lộc", "Xã Suối Hiệp"], "Xã Suối Hiệp"),
    ("Huyện Cam Lâm", ["Thị trấn Cam Đức", "Xã Cam Hải Đông", "Xã Cam Hải Tây", "Xã Cam Thành Bắc", "Xã Cam Hiệp Bắc", "Xã Cam Hiệp Nam", "Xã Cam Hòa", "Xã Cam Tân", "Xã Cam An Bắc", "Xã Cam An Nam", "Xã Suối Tân"], "Xã Cam Lâm"),
    ("Huyện Cam Lâm", ["Xã Suối Cát", "Xã Cam Hòa", "Xã Cam Tân", "Xã Suối Tân"], "Xã Suối Dầu"),
    ("Huyện Cam Lâm", ["Xã Sơn Tân", "Xã Cam Hiệp Bắc", "Xã Cam Hiệp Nam", "Xã Cam Hòa", "Xã Cam Tân", "Xã Suối Tân"], "Xã Cam Hiệp"),
    ("Huyện Cam Lâm", ["Xã Cam Phước Tây", "Xã Cam An Bắc", "Xã Cam An Nam"], "Xã Cam An"),

    # Huyện Khánh Vĩnh - items 22-26
    ("Huyện Khánh Vĩnh", ["Xã Khánh Bình", "Xã Khánh Đông"], "Xã Bắc Khánh Vĩnh"),
    ("Huyện Khánh Vĩnh", ["Xã Khánh Trung", "Xã Khánh Hiệp"], "Xã Trung Khánh Vĩnh"),
    ("Huyện Khánh Vĩnh", ["Xã Giang Ly", "Xã Khánh Thượng", "Xã Khánh Nam"], "Xã Tây Khánh Vĩnh"),
    ("Huyện Khánh Vĩnh", ["Xã Cầu Bà", "Xã Khánh Thành", "Xã Liên Sang", "Xã Sơn Thái"], "Xã Nam Khánh Vĩnh"),
    ("Huyện Khánh Vĩnh", ["Thị trấn Khánh Vĩnh", "Xã Sông Cầu", "Xã Khánh Phú"], "Xã Khánh Vĩnh"),

    # Huyện Khánh Sơn - items 27-29
    ("Huyện Khánh Sơn", ["Thị trấn Tô Hạp", "Xã Sơn Hiệp", "Xã Sơn Bình"], "Xã Khánh Sơn"),
    ("Huyện Khánh Sơn", ["Xã Sơn Lâm", "Xã Thành Sơn"], "Xã Tây Khánh Sơn"),
    ("Huyện Khánh Sơn", ["Xã Sơn Trung", "Xã Ba Cụm Bắc", "Xã Ba Cụm Nam"], "Xã Đông Khánh Sơn"),

    # Huyện Ninh Phước (Ninh Thuận) - items 30-36
    ("Huyện Ninh Phước", ["Thị trấn Phước Dân", "Xã Phước Thuận", "Xã Phước Hải"], "Xã Ninh Phước"),
    ("Huyện Ninh Phước", ["Xã Phước Thái", "Xã Phước Hữu"], "Xã Phước Hữu"),
    ("Huyện Ninh Phước", ["Xã Phước Vinh", "Xã Phước Sơn", "Xã Phước Hậu"], "Xã Phước Hậu"),
    ("Huyện Thuận Nam", ["Xã Phước Nam", "Xã Phước Ninh", "Xã Phước Minh"], "Xã Thuận Nam"),
    ("Huyện Thuận Nam", ["Xã Phước Diêm", "Xã Cà Ná"], "Xã Cà Ná"),
    ("Huyện Thuận Nam", ["Xã Nhị Hà", "Xã Phước Hà"], "Xã Phước Hà"),
    ("Huyện Thuận Nam", ["Xã An Hải", "Xã Phước Dinh", "Phường Đông Hải"], "Xã Phước Dinh"),

    # Huyện Ninh Hải - items 37-41
    ("Huyện Ninh Hải", ["Xã Phương Hải", "Xã Tri Hải", "Xã Bắc Sơn"], "Xã Ninh Hải"),
    ("Huyện Ninh Hải", ["Xã Hộ Hải", "Xã Tân Hải", "Xã Xuân Hải"], "Xã Xuân Hải"),
    ("Huyện Ninh Hải", ["Xã Nhơn Hải", "Xã Thanh Hải", "Xã Vĩnh Hải"], "Xã Vĩnh Hải"),
    ("Huyện Thuận Bắc", ["Xã Bắc Phong", "Xã Phước Kháng", "Xã Lợi Hải"], "Xã Thuận Bắc"),
    ("Huyện Thuận Bắc", ["Xã Phước Chiến", "Xã Công Hải"], "Xã Công Hải"),

    # Huyện Ninh Sơn, Bác Ái - items 42-48
    ("Huyện Ninh Sơn", ["Thị trấn Tân Sơn", "Xã Quảng Sơn"], "Xã Ninh Sơn"),
    ("Huyện Ninh Sơn", ["Xã Lương Sơn", "Xã Lâm Sơn"], "Xã Lâm Sơn"),
    ("Huyện Ninh Sơn", ["Xã Ma Nới", "Xã Hòa Sơn"], "Xã Anh Dũng"),
    ("Huyện Ninh Sơn", ["Xã Phước Trung", "Xã Mỹ Sơn"], "Xã Mỹ Sơn"),
    ("Huyện Bác Ái", ["Xã Phước Đại", "Xã Phước Thành"], "Xã Bác Ái Đông"),
    ("Huyện Bác Ái", ["Xã Phước Tiến", "Xã Phước Thắng", "Xã Phước Chính"], "Xã Bác Ái"),
    ("Huyện Bác Ái", ["Xã Phước Hòa", "Xã Phước Tân", "Xã Phước Bình"], "Xã Bác Ái Tây"),

    # Thành phố Nha Trang - items 49-52
    ("Thành phố Nha Trang", ["Phường Vạn Thạnh", "Phường Lộc Thọ", "Phường Vĩnh Nguyên", "Phường Tân Tiến", "Phường Phước Hòa"], "Phường Nha Trang"),
    ("Thành phố Nha Trang", ["Phường Vĩnh Hòa", "Phường Vĩnh Hải", "Phường Vĩnh Phước", "Phường Vĩnh Thọ", "Xã Vĩnh Lương", "Xã Vĩnh Phương"], "Phường Bắc Nha Trang"),
    ("Thành phố Nha Trang", ["Phường Ngọc Hiệp", "Phường Phương Sài", "Xã Vĩnh Ngọc", "Xã Vĩnh Thạnh", "Xã Vĩnh Hiệp", "Xã Vĩnh Trung"], "Phường Tây Nha Trang"),
    ("Thành phố Nha Trang", ["Phường Phước Hải", "Phường Phước Long", "Phường Vĩnh Trường", "Xã Vĩnh Thái", "Xã Phước Đồng"], "Phường Nam Nha Trang"),

    # Thành phố Cam Ranh - items 53-56
    ("Thành phố Cam Ranh", ["Phường Cam Nghĩa", "Phường Cam Phúc Bắc", "Xã Cam Thành Nam"], "Phường Bắc Cam Ranh"),
    ("Thành phố Cam Ranh", ["Phường Cam Phú", "Phường Cam Lộc", "Phường Cam Phúc Nam"], "Phường Cam Ranh"),
    ("Thành phố Cam Ranh", ["Phường Cam Thuận", "Phường Cam Lợi", "Phường Cam Linh"], "Phường Cam Linh"),
    ("Thành phố Cam Ranh", ["Phường Ba Ngòi", "Xã Cam Phước Đông"], "Phường Ba Ngòi"),

    # Thị xã Ninh Hòa - items 57-59
    ("Thị xã Ninh Hòa", ["Phường Ninh Hiệp", "Phường Ninh Đa", "Xã Ninh Đông", "Xã Ninh Phụng"], "Phường Ninh Hòa"),
    ("Thị xã Ninh Hòa", ["Phường Ninh Diêm", "Phường Ninh Hải", "Phường Ninh Thủy", "Xã Ninh Phước"], "Phường Đông Ninh Hòa"),
    ("Thị xã Ninh Hòa", ["Phường Ninh Giang", "Phường Ninh Hà", "Xã Ninh Phú"], "Phường Hòa Thắng"),

    # Thành phố Phan Rang - Tháp Chàm - items 60-64
    ("Thành phố Phan Rang - Tháp Chàm", ["Phường Kinh Dinh", "Phường Phủ Hà", "Phường Đài Sơn", "Phường Đạo Long"], "Phường Phan Rang"),
    ("Thành phố Phan Rang - Tháp Chàm", ["Phường Mỹ Bình", "Phường Mỹ Đông", "Phường Mỹ Hải", "Phường Đông Hải"], "Phường Đông Hải"),
    ("Thành phố Phan Rang - Tháp Chàm", ["Phường Văn Hải", "Thị trấn Khánh Hải"], "Phường Ninh Chử"),
    ("Thành phố Phan Rang - Tháp Chàm", ["Phường Phước Mỹ", "Phường Bảo An", "Xã Thành Hải"], "Phường Bảo An"),
    ("Thành phố Phan Rang - Tháp Chàm", ["Phường Đô Vinh", "Xã Nhơn Sơn"], "Phường Đô Vinh"),

    # Đặc khu Trường Sa - item 65
    ("Đặc khu Trường Sa", ["Thị trấn Trường Sa", "Xã Song Tử Tây", "Xã Sinh Tồn"], "Đặc khu Trường Sa"),
]

# Lai Châu restructuring data (36 items)
laichau_restructuring_data = [
    # Huyện Than Uyên - items 1-6
    ("Huyện Than Uyên", ["Xã Tà Mung", "Xã Tà Hừa", "Xã Pha Mu", "Xã Mường Kim"], "Xã Mường Kim"),
    ("Huyện Than Uyên", ["Xã Ta Gia", "Xã Khoen On"], "Xã Khoen On"),
    ("Huyện Than Uyên", ["Thị trấn Than Uyên", "Xã Mường Than", "Xã Hua Nà", "Xã Mường Cang"], "Xã Than Uyên"),
    ("Huyện Than Uyên", ["Xã Phúc Than", "Xã Mường Mít"], "Xã Mường Than"),
    ("Huyện Than Uyên", ["Xã Hố Mít", "Xã Pắc Ta"], "Xã Pắc Ta"),
    ("Huyện Than Uyên", ["Xã Tà Mít", "Xã Nậm Sỏ"], "Xã Nậm Sỏ"),

    # Huyện Tân Uyên - items 7-9
    ("Huyện Tân Uyên", ["Thị trấn Tân Uyên", "Xã Trung Đồng", "Xã Thân Thuộc", "Xã Nậm Cần"], "Xã Tân Uyên"),
    ("Huyện Tân Uyên", ["Xã Phúc Khoa", "Xã Mường Khoa"], "Xã Mường Khoa"),
    ("Huyện Tân Uyên", ["Xã Nà Tăm", "Xã Bản Bo"], "Xã Bản Bo"),

    # Huyện Tam Đường - items 10-13
    ("Huyện Tam Đường", ["Thị trấn Tam Đường", "Xã Sơn Bình", "Xã Bình Lư"], "Xã Bình Lư"),
    ("Huyện Tam Đường", ["Xã Giang Ma", "Xã Hồ Thầu", "Xã Tả Lèng"], "Xã Tả Lèng"),
    ("Huyện Tam Đường", ["Xã Bản Hon", "Xã Khun Há"], "Xã Khun Há"),
    ("Huyện Tam Đường", ["Xã Nậm Xe", "Xã Thèn Sin", "Xã Sin Suối Hồ"], "Xã Sin Suối Hồ"),

    # Huyện Phong Thổ - items 14-18
    ("Huyện Phong Thổ", ["Thị trấn Phong Thổ", "Xã Huổi Luông", "Xã Ma Li Pho", "Xã Mường So"], "Xã Phong Thổ"),
    ("Huyện Phong Thổ", ["Xã Tung Qua Lìn", "Xã Mù Sang", "Xã Dào San"], "Xã Dào San"),
    ("Huyện Phong Thổ", ["Xã Vàng Ma Chải", "Xã Mồ Sì San", "Xã Pa Vây Sử", "Xã Sì Lở Lầu"], "Xã Sì Lở Lầu"),
    ("Huyện Phong Thổ", ["Xã Hoang Thèn", "Xã Bản Lang", "Xã Khổng Lào"], "Xã Khổng Lào"),
    ("Huyện Phong Thổ", ["Xã Làng Mô", "Xã Tả Ngảo", "Xã Tủa Sín Chải"], "Xã Tủa Sín Chải"),

    # Huyện Sìn Hồ - items 19-24
    ("Huyện Sìn Hồ", ["Thị trấn Sìn Hồ", "Xã Sà Dề Phìn", "Xã Phăng Sô Lin", "Xã Tả Phìn"], "Xã Sìn Hồ"),
    ("Huyện Sìn Hồ", ["Xã Phìn Hồ", "Xã Ma Quai", "Xã Hồng Thu"], "Xã Hồng Thu"),
    ("Huyện Sìn Hồ", ["Xã Lùng Thàng", "Xã Nậm Cha", "Xã Nậm Tăm"], "Xã Nậm Tăm"),
    ("Huyện Sìn Hồ", ["Xã Pa Khóa", "Xã Noong Hẻo", "Xã Pu Sam Cáp"], "Xã Pu Sam Cáp"),
    ("Huyện Sìn Hồ", ["Xã Nậm Hăn", "Xã Nậm Cuổi"], "Xã Nậm Cuổi"),
    ("Huyện Sìn Hồ", ["Xã Căn Co", "Xã Nậm Mạ"], "Xã Nậm Mạ"),

    # Huyện Nậm Nhùn - items 25-28
    ("Huyện Nậm Nhùn", ["Xã Nậm Pì", "Xã Pú Đao", "Xã Chăn Nưa", "Xã Lê Lợi"], "Xã Lê Lợi"),
    ("Huyện Nậm Nhùn", ["Thị trấn Nậm Nhùn", "Xã Nậm Manh", "Xã Nậm Hàng"], "Xã Nậm Hàng"),
    ("Huyện Nậm Nhùn", ["Xã Nậm Chà", "Xã Mường Mô"], "Xã Mường Mô"),
    ("Huyện Nậm Nhùn", ["Xã Vàng San", "Xã Hua Bum"], "Xã Hua Bum"),

    # Huyện Mường Tè - items 29-34
    ("Huyện Mường Tè", ["Xã Nậm Ban", "Xã Trung Chải", "Xã Pa Tần"], "Xã Pa Tần"),
    ("Huyện Mường Tè", ["Xã Pa Vệ Sủ", "Xã Bum Nưa"], "Xã Bum Nưa"),
    ("Huyện Mường Tè", ["Thị trấn Mường Tè", "Xã Can Hồ", "Xã Bum Tở"], "Xã Bum Tở"),
    ("Huyện Mường Tè", ["Xã Nậm Khao", "Xã Mường Tè"], "Xã Mường Tè"),
    ("Huyện Mường Tè", ["Xã Ka Lăng", "Xã Thu Lũm"], "Xã Thu Lũm"),
    ("Huyện Mường Tè", ["Xã Tá Bạ", "Xã Pa Ủ"], "Xã Pa Ủ"),

    # Thành phố Lai Châu - items 35-36
    ("Thành phố Lai Châu", ["Phường Tân Phong", "Phường Đông Phong", "Xã San Thàng", "Xã Nùng Nàng", "Xã Bản Giang"], "Phường Tân Phong"),
    ("Thành phố Lai Châu", ["Phường Đoàn Kết", "Phường Quyết Tiến", "Phường Quyết Thắng", "Xã Lản Nhì Thàng", "Xã Sùng Phài"], "Phường Đoàn Kết"),
]

# Due to size constraints, the remaining provinces will be added in continuation
# Lâm Đồng, Lạng Sơn, Lào Cai data structures follow similar patterns


def generate_dia_danh(data, province_name):
    """Generate dia_danh structure for a province"""
    dia_danh = {}

    for huyen, old_units, new_unit in data:
        if huyen not in dia_danh:
            dia_danh[huyen] = {}

        # Add old units
        for unit in old_units:
            if unit not in dia_danh[huyen]:
                dia_danh[huyen][unit] = {}

        # Add new unit
        if new_unit not in dia_danh[huyen]:
            dia_danh[huyen][new_unit] = {}

    return {province_name: dia_danh}


def generate_chuyen_doi(data, province_name):
    """Generate chuyen_doi mappings for a province"""
    mappings = {}

    for huyen, old_units, new_unit in data:
        for old_unit in old_units:
            # Format: "To, Xa, Huyen, Tinh" -> "To, Xa_moi, Huyen, Tinh"
            old_key = f", {old_unit}, {huyen}, {province_name}"
            new_value = f", {new_unit}, {huyen}, {province_name}"
            mappings[old_key] = new_value

    return mappings


def process_province(name, data):
    """Process a single province and return its data"""
    dia_danh = generate_dia_danh(data, name)
    chuyen_doi = generate_chuyen_doi(data, name)
    return dia_danh, chuyen_doi


def main():
    # Get the data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "templates_app", "static", "data")

    # Process provinces - Part 1: Hưng Yên, Huế, Khánh Hòa, Lai Châu
    provinces = [
        ("Tỉnh Hưng Yên", hungyen_restructuring_data),
        ("Thành phố Huế", hue_restructuring_data),
        ("Tỉnh Khánh Hòa", khanhhoa_restructuring_data),
        ("Tỉnh Lai Châu", laichau_restructuring_data),
    ]

    all_dia_danh = {}
    all_chuyen_doi = {}

    for province_name, data in provinces:
        print(f"Processing {province_name}...")
        dia_danh, chuyen_doi = process_province(province_name, data)
        all_dia_danh.update(dia_danh)
        all_chuyen_doi.update(chuyen_doi)
        print(f"  - {len(chuyen_doi)} conversion mappings")

        # Save intermediate files
        filename = province_name.lower().replace(" ", "_")
        intermediate_path = os.path.join(data_dir, f"{filename}_dia_danh.json")
        with open(intermediate_path, 'w', encoding='utf-8') as f:
            json.dump(dia_danh, f, ensure_ascii=False, indent=2)

    print(f"\nTotal new mappings (Part 1): {len(all_chuyen_doi)}")

    # Load existing dia_danh
    dia_danh_path = os.path.join(data_dir, "dia_danh.json")
    with open(dia_danh_path, 'r', encoding='utf-8') as f:
        existing_dia_danh = json.load(f)

    # Merge
    existing_dia_danh.update(all_dia_danh)

    # Save updated dia_danh
    with open(dia_danh_path, 'w', encoding='utf-8') as f:
        json.dump(existing_dia_danh, f, ensure_ascii=False, indent=2)

    # Load existing chuyen_doi
    chuyen_doi_path = os.path.join(data_dir, "chuyen_doi.json")
    with open(chuyen_doi_path, 'r', encoding='utf-8') as f:
        existing_chuyen_doi = json.load(f)

    # Merge
    existing_chuyen_doi.update(all_chuyen_doi)

    # Save updated chuyen_doi
    with open(chuyen_doi_path, 'w', encoding='utf-8') as f:
        json.dump(existing_chuyen_doi, f, ensure_ascii=False, indent=2)

    print(f"\nFinal totals:")
    print(f"  - dia_danh provinces: {len(existing_dia_danh)}")
    print(f"  - chuyen_doi mappings: {len(existing_chuyen_doi)}")


if __name__ == "__main__":
    main()

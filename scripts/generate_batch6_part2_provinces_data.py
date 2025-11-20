#!/usr/bin/env python3
"""
Generate province restructuring data for Batch 6 Part 2:
Lâm Đồng, Lạng Sơn, Lào Cai
"""

import json
import os

# Lâm Đồng restructuring data (119 items)
lamdong_restructuring_data = [
    # Huyện Lạc Dương - item 1
    ("Huyện Lạc Dương", ["Xã Đạ Sar", "Xã Đạ Nhim", "Xã Đạ Chais"], "Xã Lạc Dương"),

    # Huyện Đơn Dương - items 2-6
    ("Huyện Đơn Dương", ["Thị trấn Thạnh Mỹ", "Xã Đạ Ròn", "Xã Tu Tra"], "Xã Đơn Dương"),
    ("Huyện Đơn Dương", ["Xã Lạc Lâm", "Xã Ka Đô"], "Xã Ka Đô"),
    ("Huyện Đơn Dương", ["Xã Ka Đơn", "Xã Quảng Lập"], "Xã Quảng Lập"),
    ("Huyện Đơn Dương", ["Thị trấn D'Ran", "Xã Lạc Xuân"], "Xã D'Ran"),
    ("Huyện Đơn Dương", ["Xã Hiệp An", "Xã Liên Hiệp", "Xã Hiệp Thạnh"], "Xã Hiệp Thạnh"),

    # Huyện Đức Trọng - items 7-10
    ("Huyện Đức Trọng", ["Thị trấn Liên Nghĩa", "Xã Phú Hội"], "Xã Đức Trọng"),
    ("Huyện Đức Trọng", ["Xã Tân Thành", "Xã N' Thôn Hạ", "Xã Tân Hội"], "Xã Tân Hội"),
    ("Huyện Đức Trọng", ["Xã Ninh Loan", "Xã Đà Loan", "Xã Tà Hine"], "Xã Tà Hine"),
    ("Huyện Đức Trọng", ["Xã Đa Quyn", "Xã Tà Năng"], "Xã Tà Năng"),

    # Huyện Lâm Hà - items 11-16
    ("Huyện Lâm Hà", ["Xã Bình Thạnh", "Xã Tân Văn", "Thị trấn Đinh Văn"], "Xã Đinh Văn Lâm Hà"),
    ("Huyện Lâm Hà", ["Xã Phú Sơn", "Xã Đạ Đờn"], "Xã Phú Sơn Lâm Hà"),
    ("Huyện Lâm Hà", ["Xã Nam Hà", "Xã Phi Tô"], "Xã Nam Hà Lâm Hà"),
    ("Huyện Lâm Hà", ["Thị trấn Nam Ban", "Xã Đông Thanh", "Xã Mê Linh", "Xã Gia Lâm"], "Xã Nam Ban Lâm Hà"),
    ("Huyện Lâm Hà", ["Xã Tân Hà", "Xã Hoài Đức", "Xã Đan Phượng", "Xã Liên Hà"], "Xã Tân Hà Lâm Hà"),
    ("Huyện Lâm Hà", ["Xã Phúc Thọ", "Xã Tân Thanh"], "Xã Phúc Thọ Lâm Hà"),

    # Huyện Đam Rông - items 17-20
    ("Huyện Đam Rông", ["Xã Phi Liêng", "Xã Đạ K'Nàng"], "Xã Đam Rông 1"),
    ("Huyện Đam Rông", ["Xã Rô Men", "Xã Liêng Srônh"], "Xã Đam Rông 2"),
    ("Huyện Đam Rông", ["Xã Đạ Rsal", "Xã Đạ M'Rông"], "Xã Đam Rông 3"),
    ("Huyện Đam Rông", ["Xã Đạ Tông", "Xã Đạ Long", "Xã Đưng K'Nớ"], "Xã Đam Rông 4"),

    # Huyện Di Linh - items 21-27
    ("Huyện Di Linh", ["Thị trấn Di Linh", "Xã Liên Đầm", "Xã Tân Châu", "Xã Gung Ré"], "Xã Di Linh"),
    ("Huyện Di Linh", ["Xã Đinh Trang Hòa", "Xã Hòa Trung", "Xã Hòa Ninh"], "Xã Hòa Ninh"),
    ("Huyện Di Linh", ["Xã Hòa Nam", "Xã Hòa Bắc"], "Xã Hòa Bắc"),
    ("Huyện Di Linh", ["Xã Tân Lâm", "Xã Tân Thượng", "Xã Đinh Trang Thượng"], "Xã Đinh Trang Thượng"),
    ("Huyện Di Linh", ["Xã Đinh Lạc", "Xã Tân Nghĩa", "Xã Bảo Thuận"], "Xã Bảo Thuận"),
    ("Huyện Di Linh", ["Xã Gia Bắc", "Xã Sơn Điền"], "Xã Sơn Điền"),
    ("Huyện Di Linh", ["Xã Tam Bố", "Xã Gia Hiệp"], "Xã Gia Hiệp"),

    # Huyện Bảo Lâm - items 28-32
    ("Huyện Bảo Lâm", ["Thị trấn Lộc Thắng", "Xã Lộc Quảng", "Xã Lộc Ngãi"], "Xã Bảo Lâm 1"),
    ("Huyện Bảo Lâm", ["Xã Lộc An", "Xã Lộc Đức", "Xã Tân Lạc"], "Xã Bảo Lâm 2"),
    ("Huyện Bảo Lâm", ["Xã Lộc Thành", "Xã Lộc Nam"], "Xã Bảo Lâm 3"),
    ("Huyện Bảo Lâm", ["Xã Lộc Phú", "Xã Lộc Lâm", "Xã B'Lá"], "Xã Bảo Lâm 4"),
    ("Huyện Bảo Lâm", ["Xã Lộc Bảo", "Xã Lộc Bắc"], "Xã Bảo Lâm 5"),

    # Huyện Đạ Huoai - items 33-34
    ("Huyện Đạ Huoai", ["Thị trấn Mađaguôi", "Xã Mađaguôi", "Xã Đạ Oai"], "Xã Đạ Huoai"),
    ("Huyện Đạ Huoai", ["Thị trấn Đạ M'ri", "Xã Hà Lâm"], "Xã Đạ Huoai 2"),

    # Huyện Đạ Tẻh - items 35-37
    ("Huyện Đạ Tẻh", ["Thị trấn Đạ Tẻh", "Xã An Nhơn", "Xã Đạ Lây"], "Xã Đạ Tẻh"),
    ("Huyện Đạ Tẻh", ["Xã Quảng Trị", "Xã Đạ Pal", "Xã Đạ Kho"], "Xã Đạ Tẻh 2"),
    ("Huyện Đạ Tẻh", ["Xã Mỹ Đức", "Xã Quốc Oai"], "Xã Đạ Tẻh 3"),

    # Huyện Cát Tiên - items 38-40
    ("Huyện Cát Tiên", ["Thị trấn Cát Tiên", "Xã Nam Ninh", "Xã Quảng Ngãi"], "Xã Cát Tiên"),
    ("Huyện Cát Tiên", ["Thị trấn Phước Cát", "Xã Phước Cát 2", "Xã Đức Phổ"], "Xã Cát Tiên 2"),
    ("Huyện Cát Tiên", ["Xã Gia Viễn", "Xã Tiên Hoàng", "Xã Đồng Nai Thượng"], "Xã Cát Tiên 3"),

    # Huyện Tuy Phong - items 41-44
    ("Huyện Tuy Phong", ["Xã Vĩnh Tân", "Xã Vĩnh Hảo"], "Xã Vĩnh Hảo"),
    ("Huyện Tuy Phong", ["Thị trấn Liên Hương", "Xã Bình Thạnh", "Xã Phước Thể", "Xã Phú Lạc"], "Xã Liên Hương"),
    ("Huyện Tuy Phong", ["Xã Phan Dũng", "Xã Phong Phú"], "Xã Tuy Phong"),
    ("Huyện Tuy Phong", ["Thị trấn Phan Rí Cửa", "Xã Chí Công", "Xã Hòa Minh", "Xã Phong Phú"], "Xã Phan Rí Cửa"),

    # Huyện Bắc Bình - items 45-51
    ("Huyện Bắc Bình", ["Thị trấn Chợ Lầu", "Xã Phan Hòa", "Xã Phan Hiệp", "Xã Phan Rí Thành"], "Xã Bắc Bình"),
    ("Huyện Bắc Bình", ["Xã Phan Thanh", "Xã Hồng Thái", "Xã Hòa Thắng"], "Xã Hồng Thái"),
    ("Huyện Bắc Bình", ["Xã Bình An", "Xã Phan Điền", "Xã Hải Ninh"], "Xã Hải Ninh"),
    ("Huyện Bắc Bình", ["Xã Phan Lâm", "Xã Phan Sơn"], "Xã Phan Sơn"),
    ("Huyện Bắc Bình", ["Xã Phan Tiến", "Xã Bình Tân", "Xã Sông Lũy"], "Xã Sông Lũy"),
    ("Huyện Bắc Bình", ["Thị trấn Lương Sơn", "Xã Sông Bình"], "Xã Lương Sơn"),
    ("Huyện Bắc Bình", ["Xã Hồng Phong", "Xã Hòa Thắng"], "Xã Hòa Thắng"),

    # Huyện Hàm Thuận Bắc - items 52-58
    ("Huyện Hàm Thuận Bắc", ["Xã Đông Tiến", "Xã Đông Giang"], "Xã Đông Giang"),
    ("Huyện Hàm Thuận Bắc", ["Xã Đa Mi", "Xã La Dạ"], "Xã La Dạ"),
    ("Huyện Hàm Thuận Bắc", ["Xã Thuận Hòa", "Xã Hàm Trí", "Xã Hàm Phú"], "Xã Hàm Thuận Bắc"),
    ("Huyện Hàm Thuận Bắc", ["Thị trấn Ma Lâm", "Xã Thuận Minh", "Xã Hàm Đức"], "Xã Hàm Thuận"),
    ("Huyện Hàm Thuận Bắc", ["Xã Hồng Liêm", "Xã Hồng Sơn"], "Xã Hồng Sơn"),
    ("Huyện Hàm Thuận Bắc", ["Xã Hàm Chính", "Xã Hàm Liêm"], "Xã Hàm Liêm"),
    ("Huyện Hàm Thuận Bắc", ["Xã Tiến Lợi", "Xã Hàm Mỹ"], "Xã Tuyên Quang"),

    # Huyện Hàm Thuận Nam - items 59-63
    ("Huyện Hàm Thuận Nam", ["Xã Mỹ Thạnh", "Xã Hàm Cần", "Xã Hàm Thạnh"], "Xã Hàm Thạnh"),
    ("Huyện Hàm Thuận Nam", ["Xã Mương Mán", "Xã Hàm Cường", "Xã Hàm Kiệm"], "Xã Hàm Kiệm"),
    ("Huyện Hàm Thuận Nam", ["Xã Tân Thành", "Xã Thuận Quý", "Xã Tân Thuận"], "Xã Tân Thành"),
    ("Huyện Hàm Thuận Nam", ["Thị trấn Thuận Nam", "Xã Hàm Minh"], "Xã Hàm Thuận Nam"),
    ("Huyện Hàm Thuận Nam", ["Xã Sông Phan", "Xã Tân Lập"], "Xã Tân Lập"),

    # Huyện Hàm Tân - items 64-67
    ("Huyện Hàm Tân", ["Thị trấn Tân Minh", "Xã Tân Đức", "Xã Tân Phúc"], "Xã Tân Minh"),
    ("Huyện Hàm Tân", ["Xã Tân Hà", "Xã Tân Xuân", "Thị trấn Tân Nghĩa"], "Xã Hàm Tân"),
    ("Huyện Hàm Tân", ["Xã Tân Thắng", "Xã Thắng Hải", "Xã Sơn Mỹ"], "Xã Sơn Mỹ"),
    ("Huyện Hàm Tân", ["Xã Tân Tiến", "Xã Tân Hải"], "Xã Tân Hải"),

    # Huyện Tánh Linh - items 68-72
    ("Huyện Tánh Linh", ["Xã Đức Phú", "Xã Nghị Đức"], "Xã Nghị Đức"),
    ("Huyện Tánh Linh", ["Xã Măng Tố", "Xã Bắc Ruộng"], "Xã Bắc Ruộng"),
    ("Huyện Tánh Linh", ["Xã Huy Khiêm", "Xã La Ngâu", "Xã Đức Bình", "Xã Đồng Kho"], "Xã Đồng Kho"),
    ("Huyện Tánh Linh", ["Thị trấn Lạc Tánh", "Xã Gia An", "Xã Đức Thuận"], "Xã Tánh Linh"),
    ("Huyện Tánh Linh", ["Xã Gia Huynh", "Xã Suối Kiết"], "Xã Suối Kiết"),

    # Huyện Đức Linh - items 73-76
    ("Huyện Đức Linh", ["Xã Mê Pu", "Xã Sùng Nhơn", "Xã Đa Kai"], "Xã Nam Thành"),
    ("Huyện Đức Linh", ["Thị trấn Võ Xu", "Xã Nam Chính", "Xã Vũ Hòa"], "Xã Đức Linh"),
    ("Huyện Đức Linh", ["Thị trấn Đức Tài", "Xã Đức Tín", "Xã Đức Hạnh"], "Xã Hoài Đức"),
    ("Huyện Đức Linh", ["Xã Tân Hà", "Xã Đông Hà", "Xã Trà Tân"], "Xã Trà Tân"),

    # Huyện Cư Jút (Đắk Nông) - items 77-80
    ("Huyện Cư Jút", ["Xã Ea Pô", "Xã Đắk Wil"], "Xã Đắk Wil"),
    ("Huyện Cư Jút", ["Xã Đắk D'rông", "Xã Nam Dong"], "Xã Nam Dong"),
    ("Huyện Cư Jút", ["Thị trấn Ea T'ling", "Xã Trúc Sơn", "Xã Tâm Thắng", "Xã Cư K'nia"], "Xã Cư Jút"),
    ("Huyện Cư Jút", ["Xã Đắk Lao", "Xã Thuận An"], "Xã Thuận An"),

    # Huyện Đắk Mil - items 81-84
    ("Huyện Đắk Mil", ["Thị trấn Đắk Mil", "Xã Đức Mạnh", "Xã Đức Minh"], "Xã Đức Lập"),
    ("Huyện Đắk Mil", ["Xã Đắk Gằn", "Xã Đắk N'Drót", "Xã Đắk R'La"], "Xã Đắk Mil"),
    ("Huyện Đắk Mil", ["Xã Nam Xuân", "Xã Long Sơn", "Xã Đắk Sắk"], "Xã Đắk Sắk"),
    ("Huyện Đắk Mil", ["Xã Buôn Choáh", "Xã Đắk Sôr", "Xã Nam Đà"], "Xã Nam Đà"),

    # Huyện Krông Nô - items 85-87
    ("Huyện Krông Nô", ["Xã Tân Thành", "Xã Đắk Drô", "Thị trấn Đắk Mâm"], "Xã Krông Nô"),
    ("Huyện Krông Nô", ["Xã Nâm N'Đir", "Xã Nâm Nung"], "Xã Nâm Nung"),
    ("Huyện Krông Nô", ["Xã Đức Xuyên", "Xã Đắk Nang", "Xã Quảng Phú"], "Xã Quảng Phú"),

    # Huyện Đắk Song - items 88-91
    ("Huyện Đắk Song", ["Xã Đắk Môl", "Xã Đắk Hòa"], "Xã Đắk Song"),
    ("Huyện Đắk Song", ["Thị trấn Đức An", "Xã Đắk N'Drung", "Xã Nam Bình"], "Xã Đức An"),
    ("Huyện Đắk Song", ["Xã Thuận Hà", "Xã Thuận Hạnh"], "Xã Thuận Hạnh"),
    ("Huyện Đắk Song", ["Xã Nâm N'Jang", "Xã Trường Xuân"], "Xã Trường Xuân"),

    # Huyện Đắk Glong - items 92-94
    ("Huyện Đắk Glong", ["Xã Đắk Som", "Xã Đắk R'Măng"], "Xã Tà Đùng"),
    ("Huyện Đắk Glong", ["Xã Đắk Plao", "Xã Quảng Khê"], "Xã Quảng Khê"),
    ("Huyện Đắk Glong", ["Xã Đắk Ngo", "Xã Quảng Tân"], "Xã Quảng Tân"),

    # Huyện Tuy Đức - item 95
    ("Huyện Tuy Đức", ["Xã Quảng Tâm", "Xã Đắk R'Tíh", "Xã Đắk Búk So"], "Xã Tuy Đức"),

    # Huyện Đắk R'Lấp - items 96-98
    ("Huyện Đắk R'Lấp", ["Thị trấn Kiến Đức", "Xã Đạo Nghĩa", "Xã Nghĩa Thắng", "Xã Kiến Thành"], "Xã Kiến Đức"),
    ("Huyện Đắk R'Lấp", ["Xã Nhân Đạo", "Xã Đắk Wer", "Xã Nhân Cơ"], "Xã Nhân Cơ"),
    ("Huyện Đắk R'Lấp", ["Xã Đắk Sin", "Xã Hưng Bình", "Xã Đắk Ru", "Xã Quảng Tín"], "Xã Quảng Tín"),

    # Thành phố Đà Lạt - items 99-103
    ("Thành phố Đà Lạt", ["Phường 1", "Phường 2", "Phường 3", "Phường 4", "Phường 10"], "Phường Xuân Hương - Đà Lạt"),
    ("Thành phố Đà Lạt", ["Phường 5", "Phường 6", "Xã Tà Nung"], "Phường Cam Ly - Đà Lạt"),
    ("Thành phố Đà Lạt", ["Phường 8", "Phường 9", "Phường 12"], "Phường Lâm Viên - Đà Lạt"),
    ("Thành phố Đà Lạt", ["Phường 11", "Xã Xuân Thọ", "Xã Xuân Trường", "Xã Trạm Hành"], "Phường Xuân Trường - Đà Lạt"),
    ("Thành phố Đà Lạt", ["Phường 7", "Thị trấn Lạc Dương", "Xã Lát"], "Phường Lang Biang - Đà Lạt"),

    # Thành phố Bảo Lộc - items 104-107
    ("Thành phố Bảo Lộc", ["Phường 1", "Phường Lộc Phát", "Xã Lộc Thanh"], "Phường 1 Bảo Lộc"),
    ("Thành phố Bảo Lộc", ["Phường 2", "Xã Lộc Tân", "Xã ĐamBri"], "Phường 2 Bảo Lộc"),
    ("Thành phố Bảo Lộc", ["Phường Lộc Tiến", "Xã Lộc Châu", "Xã Đại Lào"], "Phường 3 Bảo Lộc"),
    ("Thành phố Bảo Lộc", ["Phường Lộc Sơn", "Phường B'Lao", "Xã Lộc Nga"], "Phường B'Lao"),

    # Thành phố Phan Thiết - items 108-113
    ("Thành phố Phan Thiết", ["Phường Xuân An", "Thị trấn Phú Long", "Xã Hàm Thắng"], "Phường Hàm Thắng"),
    ("Thành phố Phan Thiết", ["Phường Phú Tài", "Xã Phong Nẫm", "Xã Hàm Hiệp"], "Phường Bình Thuận"),
    ("Thành phố Phan Thiết", ["Phường Hàm Tiến", "Phường Mũi Né", "Xã Thiện Nghiệp"], "Phường Mũi Né"),
    ("Thành phố Phan Thiết", ["Phường Thanh Hải", "Phường Phú Hài", "Phường Phú Thủy"], "Phường Phú Thủy"),
    ("Thành phố Phan Thiết", ["Phường Phú Trinh", "Phường Lạc Đạo", "Phường Bình Hưng"], "Phường Phan Thiết"),
    ("Thành phố Phan Thiết", ["Phường Đức Long", "Xã Tiến Thành"], "Phường Tiến Thành"),

    # Thị xã La Gi - items 114-115
    ("Thị xã La Gi", ["Phường Tân An", "Phường Bình Tân", "Phường Tân Thiện", "Xã Tân Bình"], "Phường La Gi"),
    ("Thị xã La Gi", ["Phường Phước Lộc", "Phường Phước Hội", "Xã Tân Phước"], "Phường Phước Hội"),

    # Thành phố Gia Nghĩa - items 116-118
    ("Thành phố Gia Nghĩa", ["Phường Quảng Thành", "Phường Nghĩa Thành", "Phường Nghĩa Đức", "Xã Đắk Ha"], "Phường Bắc Gia Nghĩa"),
    ("Thành phố Gia Nghĩa", ["Phường Nghĩa Phú", "Phường Nghĩa Tân", "Xã Đắk R'Moan"], "Phường Nam Gia Nghĩa"),
    ("Thành phố Gia Nghĩa", ["Phường Nghĩa Trung", "Xã Đắk Nia"], "Phường Đông Gia Nghĩa"),

    # Đặc khu Phú Quý - item 119
    ("Đặc khu Phú Quý", ["Xã Long Hải", "Xã Ngũ Phụng", "Xã Tam Thanh"], "Đặc khu Phú Quý"),
]

# Lạng Sơn restructuring data (65 items)
langson_restructuring_data = [
    # Huyện Tràng Định - items 1-7
    ("Huyện Tràng Định", ["Xã Chi Lăng", "Xã Chí Minh", "Thị trấn Thất Khê"], "Xã Thất Khê"),
    ("Huyện Tràng Định", ["Xã Khánh Long", "Xã Cao Minh", "Xã Đoàn Kết"], "Xã Đoàn Kết"),
    ("Huyện Tràng Định", ["Xã Tân Yên", "Xã Kim Đồng", "Xã Tân Tiến"], "Xã Tân Tiến"),
    ("Huyện Tràng Định", ["Xã Đề Thám", "Xã Hùng Sơn", "Xã Hùng Việt"], "Xã Tràng Định"),
    ("Huyện Tràng Định", ["Xã Tri Phương", "Xã Đội Cấn", "Xã Quốc Khánh"], "Xã Quốc Khánh"),
    ("Huyện Tràng Định", ["Xã Trung Thành", "Xã Tân Minh", "Xã Kháng Chiến"], "Xã Kháng Chiến"),
    ("Huyện Tràng Định", ["Xã Đào Viên", "Xã Quốc Việt"], "Xã Quốc Việt"),

    # Huyện Bình Gia - items 8-15
    ("Huyện Bình Gia", ["Xã Hoàng Văn Thụ", "Xã Mông Ân", "Thị trấn Bình Gia"], "Xã Bình Gia"),
    ("Huyện Bình Gia", ["Xã Hồng Thái", "Xã Bình La", "Xã Tân Văn"], "Xã Tân Văn"),
    ("Huyện Bình Gia", ["Xã Hồng Phong", "Xã Minh Khai"], "Xã Hồng Phong"),
    ("Huyện Bình Gia", ["Xã Hưng Đạo", "Xã Hoa Thám"], "Xã Hoa Thám"),
    ("Huyện Bình Gia", ["Xã Vĩnh Yên", "Xã Quý Hòa"], "Xã Quý Hòa"),
    ("Huyện Bình Gia", ["Xã Yên Lỗ", "Xã Thiện Hòa"], "Xã Thiện Hòa"),
    ("Huyện Bình Gia", ["Xã Quang Trung", "Xã Thiện Thuật"], "Xã Thiện Thuật"),
    ("Huyện Bình Gia", ["Xã Hòa Bình", "Xã Tân Hòa", "Xã Thiện Long"], "Xã Thiện Long"),

    # Huyện Bắc Sơn - items 16-21
    ("Huyện Bắc Sơn", ["Thị trấn Bắc Sơn", "Xã Long Đống", "Xã Bắc Quỳnh"], "Xã Bắc Sơn"),
    ("Huyện Bắc Sơn", ["Xã Trấn Yên", "Xã Hưng Vũ"], "Xã Hưng Vũ"),
    ("Huyện Bắc Sơn", ["Xã Tân Lập", "Xã Tân Hương", "Xã Chiêu Vũ", "Xã Vũ Lăng"], "Xã Vũ Lăng"),
    ("Huyện Bắc Sơn", ["Xã Tân Thành", "Xã Nhất Tiến", "Xã Nhất Hòa"], "Xã Nhất Hòa"),
    ("Huyện Bắc Sơn", ["Xã Chiến Thắng", "Xã Vũ Sơn", "Xã Vũ Lễ"], "Xã Vũ Lễ"),
    ("Huyện Bắc Sơn", ["Xã Đồng Ý", "Xã Vạn Thủy", "Xã Tân Tri"], "Xã Tân Tri"),

    # Huyện Văn Quan - items 22-25
    ("Huyện Văn Quan", ["Xã Hòa Bình", "Xã Tú Xuyên", "Thị trấn Văn Quan"], "Xã Văn Quan"),
    ("Huyện Văn Quan", ["Xã Trấn Ninh", "Xã Liên Hội", "Xã Điềm He"], "Xã Điềm He"),
    ("Huyện Văn Quan", ["Xã An Sơn", "Xã Bình Phúc", "Xã Yên Phúc"], "Xã Yên Phúc"),
    ("Huyện Văn Quan", ["Xã Lương Năng", "Xã Hữu Lễ", "Xã Tri Lễ"], "Xã Tri Lễ"),

    # Huyện Cao Lộc - items 26-27
    ("Huyện Cao Lộc", ["Xã Tân Thành", "Xã Tràng Phái", "Xã Tân Đoàn"], "Xã Tân Đoàn"),
    ("Huyện Cao Lộc", ["Xã Xuân Long", "Xã Bình Trung", "Xã Khánh Khê"], "Xã Khánh Khê"),

    # Huyện Văn Lãng - items 28-32
    ("Huyện Văn Lãng", ["Thị trấn Na Sầm", "Xã Hoàng Việt", "Xã Bắc Hùng"], "Xã Na Sầm"),
    ("Huyện Văn Lãng", ["Xã Hồng Thái", "Xã Hoàng Văn Thụ", "Xã Tân Mỹ", "Xã Nhạc Kỳ", "Xã Tân Thanh"], "Xã Hoàng Văn Thụ"),
    ("Huyện Văn Lãng", ["Xã Thụy Hùng", "Xã Thanh Long", "Xã Trùng Khánh"], "Xã Thụy Hùng"),
    ("Huyện Văn Lãng", ["Xã Bắc Việt", "Xã Bắc La", "Xã Tân Tác", "Xã Thành Hòa"], "Xã Văn Lãng"),
    ("Huyện Văn Lãng", ["Xã Gia Miễn", "Xã Hội Hoan"], "Xã Hội Hoan"),

    # Huyện Lộc Bình - items 33-38
    ("Huyện Lộc Bình", ["Thị trấn Lộc Bình", "Xã Khánh Xuân", "Xã Đồng Bục", "Xã Hữu Khánh"], "Xã Lộc Bình"),
    ("Huyện Lộc Bình", ["Xã Mẫu Sơn", "Xã Yên Khoái", "Xã Tú Mịch"], "Xã Mẫu Sơn"),
    ("Huyện Lộc Bình", ["Thị trấn Na Dương", "Xã Đông Quan", "Xã Tú Đoạn"], "Xã Na Dương"),
    ("Huyện Lộc Bình", ["Xã Sàn Viên", "Xã Lợi Bác"], "Xã Lợi Bác"),
    ("Huyện Lộc Bình", ["Xã Minh Hiệp", "Xã Hữu Lân", "Xã Thống Nhất"], "Xã Thống Nhất"),
    ("Huyện Lộc Bình", ["Xã Nam Quan", "Xã Ái Quốc", "Xã Xuân Dương"], "Xã Xuân Dương"),

    # Huyện Đình Lập - items 39-43
    ("Huyện Đình Lập", ["Xã Tam Gia", "Xã Khuất Xá"], "Xã Khuất Xá"),
    ("Huyện Đình Lập", ["Thị trấn Đình Lập", "Xã Đình Lập", "Xã Bính Xá"], "Xã Đình Lập"),
    ("Huyện Đình Lập", ["Thị trấn Nông Trường Thái Bình", "Xã Lâm Ca", "Xã Thái Bình"], "Xã Thái Bình"),
    ("Huyện Đình Lập", ["Xã Bắc Lãng", "Xã Đồng Thắng", "Xã Cường Lợi", "Xã Châu Sơn", "Xã Kiên Mộc"], "Xã Châu Sơn"),
    ("Huyện Đình Lập", ["Xã Bắc Xa", "Xã Bính Xá", "Xã Kiên Mộc"], "Xã Kiên Mộc"),

    # Huyện Hữu Lũng - items 44-51
    ("Huyện Hữu Lũng", ["Thị trấn Hữu Lũng", "Xã Đồng Tân", "Xã Hồ Sơn"], "Xã Hữu Lũng"),
    ("Huyện Hữu Lũng", ["Xã Minh Sơn", "Xã Minh Hòa", "Xã Hòa Thắng"], "Xã Tuấn Sơn"),
    ("Huyện Hữu Lũng", ["Xã Tân Thành", "Xã Hòa Lạc", "Xã Hòa Sơn"], "Xã Tân Thành"),
    ("Huyện Hữu Lũng", ["Xã Minh Tiến", "Xã Nhật Tiến", "Xã Vân Nham"], "Xã Vân Nham"),
    ("Huyện Hữu Lũng", ["Xã Thanh Sơn", "Xã Đồng Tiến", "Xã Thiện Tân"], "Xã Thiện Tân"),
    ("Huyện Hữu Lũng", ["Xã Hòa Bình", "Xã Quyết Thắng", "Xã Yên Bình"], "Xã Yên Bình"),
    ("Huyện Hữu Lũng", ["Xã Yên Thịnh", "Xã Hữu Liên"], "Xã Hữu Liên"),
    ("Huyện Hữu Lũng", ["Xã Yên Vượng", "Xã Yên Sơn", "Xã Cai Kinh"], "Xã Cai Kinh"),

    # Huyện Chi Lăng - items 52-57
    ("Huyện Chi Lăng", ["Xã Chi Lăng", "Thị trấn Chi Lăng", "Thị trấn Đồng Mỏ"], "Xã Chi Lăng"),
    ("Huyện Chi Lăng", ["Xã Hữu Kiên", "Xã Quan Sơn"], "Xã Quan Sơn"),
    ("Huyện Chi Lăng", ["Xã Chiến Thắng", "Xã Vân An", "Xã Liên Sơn", "Xã Vân Thủy"], "Xã Chiến Thắng"),
    ("Huyện Chi Lăng", ["Xã Mai Sao", "Xã Bắc Thủy", "Xã Lâm Sơn", "Xã Nhân Lý"], "Xã Nhân Lý"),
    ("Huyện Chi Lăng", ["Xã Gia Lộc", "Xã Bằng Hữu", "Xã Thượng Cường", "Xã Bằng Mạc"], "Xã Bằng Mạc"),
    ("Huyện Chi Lăng", ["Xã Hòa Bình", "Xã Y Tịch", "Xã Vạn Linh"], "Xã Vạn Linh"),

    # Huyện Cao Lộc (continued) - items 58-61
    ("Huyện Cao Lộc", ["Thị trấn Đồng Đăng", "Xã Thụy Hùng", "Xã Phú Xá", "Xã Hồng Phong", "Xã Bảo Lâm"], "Xã Đồng Đăng"),
    ("Huyện Cao Lộc", ["Xã Lộc Yên", "Xã Thanh Lòa", "Xã Thạch Đạn"], "Xã Cao Lộc"),
    ("Huyện Cao Lộc", ["Xã Hòa Cư", "Xã Hải Yến", "Xã Công Sơn"], "Xã Công Sơn"),
    ("Huyện Cao Lộc", ["Xã Mẫu Sơn", "Xã Cao Lâu", "Xã Xuất Lễ"], "Xã Ba Sơn"),

    # Thành phố Lạng Sơn - items 62-65
    ("Thành phố Lạng Sơn", ["Phường Tam Thanh", "Xã Hoàng Đồng"], "Phường Tam Thanh"),
    ("Thành phố Lạng Sơn", ["Phường Chi Lăng", "Xã Quảng Lạc"], "Phường Lương Văn Tri"),
    ("Thành phố Lạng Sơn", ["Phường Hoàng Văn Thụ", "Thị trấn Cao Lộc", "Xã Hợp Thành", "Xã Tân Liên", "Xã Gia Cát"], "Phường Kỳ Lừa"),
    ("Thành phố Lạng Sơn", ["Phường Vĩnh Trại", "Phường Đông Kinh", "Xã Yên Trạch", "Xã Mai Pha"], "Phường Đông Kinh"),
]

# Lào Cai restructuring data (91 items) - combining Yên Bái and Lào Cai
laocai_restructuring_data = [
    # Huyện Mù Cang Chải - items 1-3
    ("Huyện Mù Cang Chải", ["Xã Hồ Bốn", "Xã Khao Mang"], "Xã Khao Mang"),
    ("Huyện Mù Cang Chải", ["Thị trấn Mù Cang Chải", "Xã Kim Nọi", "Xã Mồ Dề", "Xã Chế Cu Nha"], "Xã Mù Cang Chải"),
    ("Huyện Mù Cang Chải", ["Xã Nậm Khắt", "Xã La Pán Tẩn", "Xã Dế Xu Phình", "Xã Púng Luông"], "Xã Púng Luông"),

    # Huyện Văn Chấn - items 4-14
    ("Huyện Văn Chấn", ["Xã Cao Phạ", "Xã Tú Lệ"], "Xã Tú Lệ"),
    ("Huyện Trạm Tấu", ["Xã Pá Lau", "Xã Pá Hu", "Xã Túc Đán", "Xã Trạm Tấu"], "Xã Trạm Tấu"),
    ("Huyện Trạm Tấu", ["Thị trấn Trạm Tấu", "Xã Bản Công", "Xã Hát Lừu", "Xã Xà Hồ"], "Xã Hạnh Phúc"),
    ("Huyện Trạm Tấu", ["Xã Làng Nhì", "Xã Bản Mù", "Xã Phình Hồ"], "Xã Phình Hồ"),
    ("Huyện Văn Chấn", ["Thị trấn Nông trường Liên Sơn", "Xã Sơn A", "Xã Nghĩa Phúc"], "Xã Liên Sơn"),
    ("Huyện Văn Chấn", ["Xã Nậm Búng", "Xã Nậm Lành", "Xã Gia Hội"], "Xã Gia Hội"),
    ("Huyện Văn Chấn", ["Xã Nậm Mười", "Xã Sùng Đô", "Xã Suối Quyền", "Xã Sơn Lương"], "Xã Sơn Lương"),
    ("Huyện Văn Chấn", ["Thị trấn Sơn Thịnh", "Xã Đồng Khê", "Xã Suối Bu", "Xã Suối Giàng"], "Xã Văn Chấn"),
    ("Huyện Văn Chấn", ["Thị trấn Nông trường Trần Phú", "Xã Thượng Bằng La"], "Xã Thượng Bằng La"),
    ("Huyện Văn Chấn", ["Xã Tân Thịnh", "Xã Đại Lịch", "Xã Chấn Thịnh"], "Xã Chấn Thịnh"),
    ("Huyện Văn Chấn", ["Xã Bình Thuận", "Xã Minh An", "Xã Nghĩa Tâm"], "Xã Nghĩa Tâm"),

    # Huyện Văn Yên - items 15-21
    ("Huyện Văn Yên", ["Xã Xuân Tầm", "Xã Phong Dụ Hạ"], "Xã Phong Dụ Hạ"),
    ("Huyện Văn Yên", ["Xã Châu Quế Thượng", "Xã Châu Quế Hạ"], "Xã Châu Quế"),
    ("Huyện Văn Yên", ["Xã Lang Thíp", "Xã Lâm Giang"], "Xã Lâm Giang"),
    ("Huyện Văn Yên", ["Xã Quang Minh", "Xã An Bình", "Xã Đông An", "Xã Đông Cuông"], "Xã Đông Cuông"),
    ("Huyện Văn Yên", ["Xã Đại Sơn", "Xã Nà Hẩu", "Xã Tân Hợp"], "Xã Tân Hợp"),
    ("Huyện Văn Yên", ["Thị trấn Mậu A", "Xã Yên Thái", "Xã An Thịnh", "Xã Mậu Đông", "Xã Ngòi A"], "Xã Mậu A"),
    ("Huyện Văn Yên", ["Xã Đại Phác", "Xã Yên Phú", "Xã Yên Hợp", "Xã Viễn Sơn", "Xã Xuân Ái"], "Xã Xuân Ái"),

    # Huyện Lục Yên - items 22-31
    ("Huyện Lục Yên", ["Xã An Lương", "Xã Mỏ Vàng"], "Xã Mỏ Vàng"),
    ("Huyện Lục Yên", ["Xã Mai Sơn", "Xã Khánh Thiện", "Xã Tân Phượng", "Xã Lâm Thượng"], "Xã Lâm Thượng"),
    ("Huyện Lục Yên", ["Thị trấn Yên Thế", "Xã Minh Xuân", "Xã Yên Thắng", "Xã Liễu Đô"], "Xã Lục Yên"),
    ("Huyện Lục Yên", ["Xã Minh Chuẩn", "Xã Tân Lập", "Xã Phan Thanh", "Xã Khai Trung", "Xã Tân Lĩnh"], "Xã Tân Lĩnh"),
    ("Huyện Lục Yên", ["Xã Tô Mậu", "Xã An Lạc", "Xã Động Quan", "Xã Khánh Hòa"], "Xã Khánh Hòa"),
    ("Huyện Lục Yên", ["Xã Trúc Lâu", "Xã Trung Tâm", "Xã Phúc Lợi"], "Xã Phúc Lợi"),
    ("Huyện Yên Bình", ["Xã An Phú", "Xã Vĩnh Lạc", "Xã Minh Tiến", "Xã Mường Lai"], "Xã Mường Lai"),
    ("Huyện Yên Bình", ["Xã Xuân Long", "Xã Ngọc Chấn", "Xã Cảm Nhân"], "Xã Cảm Nhân"),
    ("Huyện Yên Bình", ["Xã Phúc Ninh", "Xã Mỹ Gia", "Xã Xuân Lai", "Xã Phúc An", "Xã Yên Thành"], "Xã Yên Thành"),
    ("Huyện Yên Bình", ["Thị trấn Thác Bà", "Xã Vũ Linh", "Xã Bạch Hà", "Xã Hán Đà", "Xã Vĩnh Kiên", "Xã Đại Minh"], "Xã Thác Bà"),

    # Huyện Yên Bình (continued) - items 32-33
    ("Huyện Yên Bình", ["Thị trấn Yên Bình", "Xã Tân Hương", "Xã Thịnh Hưng", "Xã Đại Đồng"], "Xã Yên Bình"),
    ("Huyện Yên Bình", ["Xã Cảm Ân", "Xã Mông Sơn", "Xã Tân Nguyên", "Xã Bảo Ái"], "Xã Bảo Ái"),

    # Huyện Trấn Yên - items 34-38
    ("Huyện Trấn Yên", ["Thị trấn Cổ Phúc", "Xã Báo Đáp", "Xã Tân Đồng", "Xã Thành Thịnh", "Xã Hòa Cuông", "Xã Minh Quán"], "Xã Trấn Yên"),
    ("Huyện Trấn Yên", ["Xã Hồng Ca", "Xã Hưng Khánh"], "Xã Hưng Khánh"),
    ("Huyện Trấn Yên", ["Xã Hưng Thịnh", "Xã Lương Thịnh"], "Xã Lương Thịnh"),
    ("Huyện Trấn Yên", ["Xã Việt Cường", "Xã Vân Hội", "Xã Việt Hồng"], "Xã Việt Hồng"),
    ("Huyện Trấn Yên", ["Xã Kiên Thành", "Xã Y Can", "Xã Quy Mông"], "Xã Quy Mông"),

    # Thành phố Lào Cai - items 39-45
    ("Thành phố Lào Cai", ["Xã Đồng Tuyển", "Xã Tòng Sành", "Xã Cốc San"], "Xã Cốc San"),
    ("Thành phố Lào Cai", ["Xã Tả Phời", "Xã Hợp Thành"], "Xã Hợp Thành"),
    ("Huyện Bảo Thắng", ["Thị trấn Nông trường Phong Hải", "Xã Bản Cầm"], "Xã Phong Hải"),
    ("Huyện Bảo Thắng", ["Xã Phong Niên", "Xã Trì Quang", "Xã Xuân Quang"], "Xã Xuân Quang"),
    ("Huyện Bảo Thắng", ["Thị trấn Phố Lu", "Xã Sơn Hà", "Xã Sơn Hải", "Xã Thái Niên"], "Xã Bảo Thắng"),
    ("Huyện Bảo Thắng", ["Thị trấn Tằng Loỏng", "Xã Phú Nhuận"], "Xã Tằng Loỏng"),
    ("Huyện Bảo Thắng", ["Xã Xuân Giao", "Xã Thống Nhất", "Xã Gia Phú"], "Xã Gia Phú"),

    # Huyện Bát Xát - items 46-52
    ("Huyện Bát Xát", ["Xã Nậm Pung", "Xã Trung Lèng Hồ", "Xã Mường Hum"], "Xã Mường Hum"),
    ("Huyện Bát Xát", ["Xã Dền Thàng", "Xã Sàng Ma Sáo", "Xã Dền Sáng"], "Xã Dền Sáng"),
    ("Huyện Bát Xát", ["Xã A Lù", "Xã Y Tý"], "Xã Y Tý"),
    ("Huyện Bát Xát", ["Xã Nậm Chạc", "Xã A Mú Sung"], "Xã A Mú Sung"),
    ("Huyện Bát Xát", ["Xã Cốc Mỳ", "Xã Trịnh Tường"], "Xã Trịnh Tường"),
    ("Huyện Bát Xát", ["Xã Pa Cheo", "Xã Mường Vi", "Xã Bản Xèo"], "Xã Bản Xèo"),
    ("Huyện Bát Xát", ["Thị trấn Bát Xát", "Xã Bản Vược", "Xã Bản Qua", "Xã Phìn Ngan", "Xã Quang Kim"], "Xã Bát Xát"),

    # Huyện Văn Bàn - items 53-59
    ("Huyện Văn Bàn", ["Xã Nậm Mả", "Xã Nậm Dạng", "Xã Võ Lao"], "Xã Võ Lao"),
    ("Huyện Văn Bàn", ["Xã Khánh Yên Trung", "Xã Liêm Phú", "Xã Khánh Yên Hạ"], "Xã Khánh Yên"),
    ("Huyện Văn Bàn", ["Thị trấn Khánh Yên", "Xã Khánh Yên Thượng", "Xã Sơn Thuỷ", "Xã Làng Giàng", "Xã Hòa Mạc"], "Xã Văn Bàn"),
    ("Huyện Văn Bàn", ["Xã Thẳm Dương", "Xã Dương Quỳ"], "Xã Dương Quỳ"),
    ("Huyện Văn Bàn", ["Xã Nậm Tha", "Xã Chiềng Ken"], "Xã Chiềng Ken"),
    ("Huyện Văn Bàn", ["Xã Nậm Xây", "Xã Minh Lương"], "Xã Minh Lương"),
    ("Huyện Văn Bàn", ["Xã Dần Thàng", "Xã Nậm Chày"], "Xã Nậm Chày"),

    # Huyện Bảo Yên - items 60-65
    ("Huyện Bảo Yên", ["Thị trấn Phố Ràng", "Xã Yên Sơn", "Xã Lương Sơn", "Xã Xuân Thượng"], "Xã Bảo Yên"),
    ("Huyện Bảo Yên", ["Xã Tân Tiến", "Xã Vĩnh Yên", "Xã Nghĩa Đô"], "Xã Nghĩa Đô"),
    ("Huyện Bảo Yên", ["Xã Điện Quan", "Xã Minh Tân", "Xã Thượng Hà"], "Xã Thượng Hà"),
    ("Huyện Bảo Yên", ["Xã Tân Dương", "Xã Xuân Hòa"], "Xã Xuân Hòa"),
    ("Huyện Bảo Yên", ["Xã Việt Tiến", "Xã Phúc Khánh"], "Xã Phúc Khánh"),
    ("Huyện Bảo Yên", ["Xã Kim Sơn", "Xã Cam Cọn", "Xã Tân An", "Xã Tân Thượng", "Xã Bảo Hà"], "Xã Bảo Hà"),

    # Thị xã Sa Pa - items 66-69
    ("Thị xã Sa Pa", ["Xã Liên Minh", "Xã Mường Bo"], "Xã Mường Bo"),
    ("Thị xã Sa Pa", ["Xã Thanh Bình", "Xã Bản Hồ"], "Xã Bản Hồ"),
    ("Thị xã Sa Pa", ["Xã Hoàng Liên", "Xã Mường Hoa", "Xã Tả Van"], "Xã Tả Van"),
    ("Thị xã Sa Pa", ["Xã Trung Chải", "Xã Tả Phìn"], "Xã Tả Phìn"),

    # Huyện Bắc Hà - items 70-75
    ("Huyện Bắc Hà", ["Xã Nậm Lúc", "Xã Bản Cái", "Xã Cốc Lầu"], "Xã Cốc Lầu"),
    ("Huyện Bắc Hà", ["Xã Nậm Đét", "Xã Cốc Ly", "Xã Bảo Nhai"], "Xã Bảo Nhai"),
    ("Huyện Bắc Hà", ["Xã Nậm Khánh", "Xã Bản Liền"], "Xã Bản Liền"),
    ("Huyện Bắc Hà", ["Thị trấn Bắc Hà", "Xã Na Hối", "Xã Thải Giàng Phố", "Xã Bản Phố", "Xã Hoàng Thu Phố", "Xã Nậm Mòn"], "Xã Bắc Hà"),
    ("Huyện Bắc Hà", ["Xã Lùng Cải", "Xã Tả Củ Tỷ"], "Xã Tả Củ Tỷ"),
    ("Huyện Bắc Hà", ["Xã Tả Van Chư", "Xã Lùng Phình", "Xã Lùng Thẩn"], "Xã Lùng Phình"),

    # Huyện Mường Khương - items 76-79
    ("Huyện Mường Khương", ["Xã Tả Ngài Chồ", "Xã Dìn Chin", "Xã Tả Gia Khâu", "Xã Pha Long"], "Xã Pha Long"),
    ("Huyện Mường Khương", ["Thị trấn Mường Khương", "Xã Thanh Bình", "Xã Nậm Chảy", "Xã Tung Chung Phố", "Xã Nấm Lư"], "Xã Mường Khương"),
    ("Huyện Mường Khương", ["Xã Bản Sen", "Xã Lùng Vai", "Xã Bản Lầu"], "Xã Bản Lầu"),
    ("Huyện Mường Khương", ["Xã Lùng Khấu Nhin", "Xã Tả Thàng", "Xã La Pan Tẩn", "Xã Cao Sơn"], "Xã Cao Sơn"),

    # Huyện Si Ma Cai - items 80-81
    ("Huyện Si Ma Cai", ["Thị trấn Si Ma Cai", "Xã Sán Chải", "Xã Nàn Sán", "Xã Cán Cấu", "Xã Quan Hồ Thẩn"], "Xã Si Ma Cai"),
    ("Huyện Si Ma Cai", ["Xã Bản Mế", "Xã Thào Chư Phìn", "Xã Nàn Sín", "Xã Sín Chéng"], "Xã Sín Chéng"),

    # Thị xã Nghĩa Lộ - items 82-84
    ("Thị xã Nghĩa Lộ", ["Phường Tân An", "Phường Pú Trạng", "Xã Nghĩa An", "Xã Nghĩa Sơn"], "Phường Nghĩa Lộ"),
    ("Thị xã Nghĩa Lộ", ["Phường Trung Tâm", "Xã Phù Nham", "Xã Nghĩa Lợi", "Xã Nghĩa Lộ"], "Phường Trung Tâm"),
    ("Thị xã Nghĩa Lộ", ["Phường Cầu Thia", "Xã Thanh Lương", "Xã Thạch Lương", "Xã Phúc Sơn", "Xã Hạnh Sơn"], "Phường Cầu Thia"),

    # Thành phố Yên Bái - items 85-88
    ("Thành phố Yên Bái", ["Phường Yên Thịnh", "Xã Tân Thịnh", "Xã Văn Phú", "Xã Phú Thịnh"], "Phường Văn Phú"),
    ("Thành phố Yên Bái", ["Phường Đồng Tâm", "Phường Yên Ninh", "Phường Minh Tân", "Phường Nguyễn Thái Học", "Phường Hồng Hà"], "Phường Yên Bái"),
    ("Thành phố Yên Bái", ["Phường Nam Cường", "Xã Minh Bảo", "Xã Tuy Lộc", "Xã Cường Thịnh"], "Phường Nam Cường"),
    ("Thành phố Yên Bái", ["Phường Hợp Minh", "Xã Giới Phiên", "Xã Minh Quân", "Xã Âu Lâu"], "Phường Âu Lâu"),

    # Thành phố Lào Cai - items 89-91
    ("Thành phố Lào Cai", ["Phường Nam Cường", "Phường Xuân Tăng", "Phường Pom Hán", "Phường Bắc Cường", "Phường Bắc Lệnh", "Phường Bình Minh", "Xã Cam Đường"], "Phường Cam Đường"),
    ("Thành phố Lào Cai", ["Phường Duyên Hải", "Phường Cốc Lếu", "Phường Kim Tân", "Phường Lào Cai", "Xã Vạn Hòa", "Xã Bản Phiệt"], "Phường Lào Cai"),
    ("Thị xã Sa Pa", ["Phường Hàm Rồng", "Phường Ô Quý Hồ", "Phường Sa Pả", "Phường Cầu Mây", "Phường Phan Si Păng", "Phường Sa Pa"], "Phường Sa Pa"),
]


def generate_dia_danh(data, province_name):
    """Generate dia_danh structure for a province"""
    dia_danh = {}

    for huyen, old_units, new_unit in data:
        if huyen not in dia_danh:
            dia_danh[huyen] = {}

        for unit in old_units:
            if unit not in dia_danh[huyen]:
                dia_danh[huyen][unit] = {}

        if new_unit not in dia_danh[huyen]:
            dia_danh[huyen][new_unit] = {}

    return {province_name: dia_danh}


def generate_chuyen_doi(data, province_name):
    """Generate chuyen_doi mappings for a province"""
    mappings = {}

    for huyen, old_units, new_unit in data:
        for old_unit in old_units:
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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "templates_app", "static", "data")

    provinces = [
        ("Tỉnh Lâm Đồng", lamdong_restructuring_data),
        ("Tỉnh Lạng Sơn", langson_restructuring_data),
        ("Tỉnh Lào Cai", laocai_restructuring_data),
    ]

    all_dia_danh = {}
    all_chuyen_doi = {}

    for province_name, data in provinces:
        print(f"Processing {province_name}...")
        dia_danh, chuyen_doi = process_province(province_name, data)
        all_dia_danh.update(dia_danh)
        all_chuyen_doi.update(chuyen_doi)
        print(f"  - {len(chuyen_doi)} conversion mappings")

        filename = province_name.lower().replace(" ", "_")
        intermediate_path = os.path.join(data_dir, f"{filename}_dia_danh.json")
        with open(intermediate_path, 'w', encoding='utf-8') as f:
            json.dump(dia_danh, f, ensure_ascii=False, indent=2)

    print(f"\nTotal new mappings (Part 2): {len(all_chuyen_doi)}")

    dia_danh_path = os.path.join(data_dir, "dia_danh.json")
    with open(dia_danh_path, 'r', encoding='utf-8') as f:
        existing_dia_danh = json.load(f)

    existing_dia_danh.update(all_dia_danh)

    with open(dia_danh_path, 'w', encoding='utf-8') as f:
        json.dump(existing_dia_danh, f, ensure_ascii=False, indent=2)

    chuyen_doi_path = os.path.join(data_dir, "chuyen_doi.json")
    with open(chuyen_doi_path, 'r', encoding='utf-8') as f:
        existing_chuyen_doi = json.load(f)

    existing_chuyen_doi.update(all_chuyen_doi)

    with open(chuyen_doi_path, 'w', encoding='utf-8') as f:
        json.dump(existing_chuyen_doi, f, ensure_ascii=False, indent=2)

    print(f"\nFinal totals:")
    print(f"  - dia_danh provinces: {len(existing_dia_danh)}")
    print(f"  - chuyen_doi mappings: {len(existing_chuyen_doi)}")


if __name__ == "__main__":
    main()

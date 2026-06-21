#!/usr/bin/env python3
"""
Generate province restructuring data for Batch 5: Hà Tĩnh, Hải Phòng (mới)
"""

import json
import os

# Hà Tĩnh restructuring data (67 items)
hatinh_restructuring_data = [
    # Huyện Thạch Hà - items 1-4
    ("Huyện Thạch Hà", ["Xã Tượng Sơn", "Xã Thạch Thắng", "Xã Thạch Lạc"], "Xã Thạch Lạc"),
    ("Huyện Thạch Hà", ["Xã Thạch Trị", "Xã Thạch Hội", "Xã Thạch Văn"], "Xã Đồng Tiến"),
    ("Huyện Thạch Hà", ["Xã Đỉnh Bàn", "Xã Thạch Hải", "Xã Thạch Khê"], "Xã Thạch Khê"),
    ("Huyện Thạch Hà", ["Xã Cẩm Vịnh", "Xã Thạch Bình", "Xã Cẩm Thành", "Xã Cẩm Bình"], "Xã Cẩm Bình"),

    # Huyện Kỳ Anh - items 5-11
    ("Huyện Kỳ Anh", ["Xã Kỳ Phong", "Xã Kỳ Bắc", "Xã Kỳ Xuân"], "Xã Kỳ Xuân"),
    ("Huyện Kỳ Anh", ["Thị trấn Kỳ Đồng", "Xã Kỳ Giang", "Xã Kỳ Tiến", "Xã Kỳ Phú"], "Xã Kỳ Anh"),
    ("Huyện Kỳ Anh", ["Xã Kỳ Tân", "Xã Kỳ Hoa"], "Xã Kỳ Hoa"),
    ("Huyện Kỳ Anh", ["Xã Kỳ Tây", "Xã Kỳ Trung", "Xã Kỳ Văn"], "Xã Kỳ Văn"),
    ("Huyện Kỳ Anh", ["Xã Kỳ Thọ", "Xã Kỳ Thư", "Xã Kỳ Khang"], "Xã Kỳ Khang"),
    ("Huyện Kỳ Anh", ["Xã Lâm Hợp", "Xã Kỳ Lạc"], "Xã Kỳ Lạc"),
    ("Huyện Kỳ Anh", ["Xã Kỳ Sơn", "Xã Kỳ Thượng"], "Xã Kỳ Thượng"),

    # Huyện Cẩm Xuyên - items 12-18
    ("Huyện Cẩm Xuyên", ["Thị trấn Cẩm Xuyên", "Xã Cẩm Quang", "Xã Cẩm Quan"], "Xã Cẩm Xuyên"),
    ("Huyện Cẩm Xuyên", ["Thị trấn Thiên Cầm", "Xã Nam Phúc Thăng", "Xã Cẩm Nhượng"], "Xã Thiên Cầm"),
    ("Huyện Cẩm Xuyên", ["Xã Cẩm Mỹ", "Xã Cẩm Thạch", "Xã Cẩm Duệ"], "Xã Cẩm Duệ"),
    ("Huyện Cẩm Xuyên", ["Xã Cẩm Thịnh", "Xã Cẩm Hà", "Xã Cẩm Hưng"], "Xã Cẩm Hưng"),
    ("Huyện Cẩm Xuyên", ["Xã Cẩm Minh", "Xã Cẩm Sơn", "Xã Cẩm Lạc"], "Xã Cẩm Lạc"),
    ("Huyện Cẩm Xuyên", ["Xã Cẩm Lĩnh", "Xã Cẩm Lộc", "Xã Cẩm Trung"], "Xã Cẩm Trung"),
    ("Huyện Cẩm Xuyên", ["Xã Cẩm Dương", "Xã Yên Hòa"], "Xã Yên Hòa"),

    # Huyện Thạch Hà (continued) - items 19-23
    ("Huyện Thạch Hà", ["Thị trấn Thạch Hà", "Xã Thạch Long", "Xã Thạch Sơn"], "Xã Thạch Hà"),
    ("Huyện Thạch Hà", ["Xã Ngọc Sơn", "Xã Lưu Vĩnh Sơn"], "Xã Toàn Lưu"),
    ("Huyện Thạch Hà", ["Xã Việt Tiến", "Xã Thạch Ngọc"], "Xã Việt Xuyên"),
    ("Huyện Thạch Hà", ["Xã Thạch Kênh", "Xã Thạch Liên", "Xã Ích Hậu"], "Xã Đông Kinh"),
    ("Huyện Thạch Hà", ["Xã Nam Điền", "Xã Thạch Xuân"], "Xã Thạch Xuân"),

    # Huyện Lộc Hà - items 24-26
    ("Huyện Lộc Hà", ["Thị trấn Lộc Hà", "Xã Bình An", "Xã Thịnh Lộc", "Xã Thạch Kim"], "Xã Lộc Hà"),
    ("Huyện Lộc Hà", ["Xã Tân Lộc", "Xã Hồng Lộc"], "Xã Hồng Lộc"),
    ("Huyện Lộc Hà", ["Xã Thạch Mỹ", "Xã Thạch Châu", "Xã Phù Lưu", "Xã Mai Phụ"], "Xã Mai Phụ"),

    # Huyện Can Lộc - items 27-32
    ("Huyện Can Lộc", ["Thị trấn Nghèn", "Xã Thiên Lộc", "Xã Vượng Lộc"], "Xã Can Lộc"),
    ("Huyện Can Lộc", ["Xã Thuần Thiện", "Xã Tùng Lộc"], "Xã Tùng Lộc"),
    ("Huyện Can Lộc", ["Xã Khánh Vĩnh Yên", "Xã Thanh Lộc", "Xã Gia Hanh"], "Xã Gia Hanh"),
    ("Huyện Can Lộc", ["Xã Kim Song Trường", "Xã Thường Nga", "Xã Phú Lộc"], "Xã Trường Lưu"),
    ("Huyện Can Lộc", ["Xã Sơn Lộc", "Xã Quang Lộc", "Xã Xuân Lộc"], "Xã Xuân Lộc"),
    ("Huyện Can Lộc", ["Thị trấn Đồng Lộc", "Xã Thượng Lộc", "Xã Mỹ Lộc"], "Xã Đồng Lộc"),

    # Huyện Nghi Xuân - items 33-36
    ("Huyện Nghi Xuân", ["Thị trấn Tiên Điền", "Xã Xuân Yên", "Xã Xuân Mỹ", "Xã Xuân Thành"], "Xã Tiên Điền"),
    ("Huyện Nghi Xuân", ["Thị trấn Xuân An", "Xã Xuân Giang", "Xã Xuân Hồng", "Xã Xuân Viên", "Xã Xuân Lĩnh"], "Xã Nghi Xuân"),
    ("Huyện Nghi Xuân", ["Xã Cương Gián", "Xã Xuân Liên", "Xã Cổ Đạm"], "Xã Cổ Đạm"),
    ("Huyện Nghi Xuân", ["Xã Đan Trường", "Xã Xuân Hải", "Xã Xuân Hội", "Xã Xuân Phổ"], "Xã Đan Hải"),

    # Huyện Đức Thọ - items 37-41
    ("Huyện Đức Thọ", ["Thị trấn Đức Thọ", "Xã Tùng Ảnh", "Xã Hòa Lạc", "Xã Tân Dân"], "Xã Đức Thọ"),
    ("Huyện Đức Thọ", ["Xã Đức Lạng", "Xã Tân Hương", "Xã Đức Đồng"], "Xã Đức Đồng"),
    ("Huyện Đức Thọ", ["Xã Quang Vĩnh", "Xã Bùi La Nhân", "Xã Yên Hồ"], "Xã Đức Quang"),
    ("Huyện Đức Thọ", ["Xã Thanh Bình Thịnh", "Xã Lâm Trung Thủy", "Xã An Dũng"], "Xã Đức Thịnh"),
    ("Huyện Đức Thọ", ["Xã Trường Sơn", "Xã Tùng Châu", "Xã Liên Minh"], "Xã Đức Minh"),

    # Huyện Hương Sơn - items 42-48
    ("Huyện Hương Sơn", ["Thị trấn Phố Châu", "Xã Sơn Phú", "Xã Sơn Bằng", "Xã Sơn Ninh", "Xã Sơn Trung"], "Xã Hương Sơn"),
    ("Huyện Hương Sơn", ["Thị trấn Tây Sơn", "Xã Sơn Tây"], "Xã Sơn Tây"),
    ("Huyện Hương Sơn", ["Xã Châu Bình", "Xã Tân Mỹ Hà", "Xã Mỹ Long"], "Xã Tứ Mỹ"),
    ("Huyện Hương Sơn", ["Xã Sơn Lâm", "Xã Quang Diệm", "Xã Sơn Giang"], "Xã Sơn Giang"),
    ("Huyện Hương Sơn", ["Xã Sơn Lễ", "Xã An Hòa Thịnh", "Xã Sơn Tiến"], "Xã Sơn Tiến"),
    ("Huyện Hương Sơn", ["Xã Sơn Lĩnh", "Xã Sơn Hồng"], "Xã Sơn Hồng"),
    ("Huyện Hương Sơn", ["Xã Hàm Trường", "Xã Kim Hoa"], "Xã Kim Hoa"),

    # Huyện Vũ Quang - items 49-51
    ("Huyện Vũ Quang", ["Thị trấn Vũ Quang", "Xã Hương Minh", "Xã Quang Thọ", "Xã Thọ Điền"], "Xã Vũ Quang"),
    ("Huyện Vũ Quang", ["Xã Ân Phú", "Xã Đức Giang", "Xã Đức Lĩnh"], "Xã Mai Hoa"),
    ("Huyện Vũ Quang", ["Xã Đức Bồng", "Xã Đức Hương", "Xã Đức Liên"], "Xã Thượng Đức"),

    # Huyện Hương Khê - items 52-58
    ("Huyện Hương Khê", ["Thị trấn Hương Khê", "Xã Hương Long", "Xã Phú Gia"], "Xã Hương Khê"),
    ("Huyện Hương Khê", ["Xã Hương Giang", "Xã Hương Thủy", "Xã Gia Phố"], "Xã Hương Phố"),
    ("Huyện Hương Khê", ["Xã Lộc Yên", "Xã Hương Trà", "Xã Hương Đô"], "Xã Hương Đô"),
    ("Huyện Hương Khê", ["Xã Điền Mỹ", "Xã Hà Linh"], "Xã Hà Linh"),
    ("Huyện Hương Khê", ["Xã Hòa Hải", "Xã Phúc Đồng", "Xã Hương Bình"], "Xã Hương Bình"),
    ("Huyện Hương Khê", ["Xã Hương Trạch", "Xã Hương Liên", "Xã Phúc Trạch"], "Xã Phúc Trạch"),
    ("Huyện Hương Khê", ["Xã Hương Lâm", "Xã Hương Vĩnh", "Xã Hương Xuân"], "Xã Hương Xuân"),

    # Thành phố Hà Tĩnh - items 59-61
    ("Thành phố Hà Tĩnh", ["Phường Bắc Hà", "Phường Thạch Quý", "Phường Tân Giang", "Phường Thạch Hưng", "Phường Nam Hà", "Phường Trần Phú", "Phường Hà Huy Tập", "Phường Văn Yên", "Phường Đại Nài"], "Phường Thành Sen"),
    ("Thành phố Hà Tĩnh", ["Phường Thạch Trung", "Phường Đồng Môn", "Phường Thạch Hạ", "Xã Hộ Độ"], "Phường Trần Phú"),
    ("Thành phố Hà Tĩnh", ["Xã Tân Lâm Hương", "Xã Thạch Đài", "Phường Đại Nài"], "Phường Hà Huy Tập"),

    # Thị xã Kỳ Anh - items 62-65
    ("Thị xã Kỳ Anh", ["Phường Kỳ Long", "Phường Kỳ Thịnh", "Xã Kỳ Lợi"], "Phường Vũng Áng"),
    ("Thị xã Kỳ Anh", ["Phường Hưng Trí", "Phường Kỳ Trinh", "Xã Kỳ Châu", "Xã Kỳ Lợi"], "Phường Sông Trí"),
    ("Thị xã Kỳ Anh", ["Phường Kỳ Nam", "Phường Kỳ Phương", "Phường Kỳ Liên", "Xã Kỳ Lợi"], "Phường Hoành Sơn"),
    ("Thị xã Kỳ Anh", ["Phường Kỳ Ninh", "Xã Kỳ Hà", "Xã Kỳ Hải"], "Phường Hải Ninh"),

    # Thị xã Hồng Lĩnh - items 66-67
    ("Thị xã Hồng Lĩnh", ["Phường Bắc Hồng", "Phường Đức Thuận", "Phường Trung Lương", "Xã Xuân Lam"], "Phường Bắc Hồng Lĩnh"),
    ("Thị xã Hồng Lĩnh", ["Phường Nam Hồng", "Phường Đậu Liêu", "Xã Thuận Lộc"], "Phường Nam Hồng Lĩnh"),
]

# Hải Phòng (mới) restructuring data (114 items)
# Note: This is a mega-province combining Hải Phòng and Hải Dương
haiphong_restructuring_data = [
    # Thành phố Thủy Nguyên - items 1-7
    ("Thành phố Thủy Nguyên", ["Phường Dương Quan", "Phường Thủy Đường", "Phường Hoa Động", "Phường An Lư", "Phường Thủy Hà"], "Phường Thủy Nguyên"),
    ("Thành phố Thủy Nguyên", ["Phường Thiên Hương", "Phường Hoàng Lâm", "Phường Lê Hồng Phong", "Phường Hoa Động"], "Phường Thiên Hương"),
    ("Thành phố Thủy Nguyên", ["Phường Hòa Bình", "Phường An Lư", "Phường Thủy Hà"], "Phường Hòa Bình"),
    ("Thành phố Thủy Nguyên", ["Phường Nam Triệu Giang", "Phường Lập Lễ", "Phường Tam Hưng"], "Phường Nam Triệu"),
    ("Thành phố Thủy Nguyên", ["Phường Minh Đức", "Xã Bạch Đằng", "Phường Phạm Ngũ Lão"], "Phường Bạch Đằng"),
    ("Thành phố Thủy Nguyên", ["Phường Trần Hưng Đạo", "Phường Lưu Kiếm", "Xã Liên Xuân", "Xã Quang Trung"], "Phường Lưu Kiếm"),
    ("Thành phố Thủy Nguyên", ["Phường Quảng Thanh", "Phường Lê Hồng Phong", "Xã Quang Trung"], "Phường Lê Ích Mộc"),

    # Quận Hồng Bàng - item 8
    ("Quận Hồng Bàng", ["Phường Hoàng Văn Thụ", "Phường Minh Khai", "Phường Phan Bội Châu", "Phường Thượng Lý", "Phường Sở Dầu", "Phường Hùng Vương", "Phường Gia Viên"], "Phường Hồng Bàng"),

    # Quận Ngô Quyền - items 9-11
    ("Quận Ngô Quyền", ["Phường Quán Toan", "Phường An Hồng", "Phường An Hưng", "Phường Đại Bản", "Phường Lê Thiện", "Phường Tân Tiến"], "Phường Hồng An"),
    ("Quận Ngô Quyền", ["Phường Máy Chai", "Phường Vạn Mỹ", "Phường Cầu Tre", "Phường Gia Viên", "Phường Đông Khê"], "Phường Ngô Quyền"),
    ("Quận Ngô Quyền", ["Phường Đằng Giang", "Phường Cầu Đất", "Phường Lạch Tray", "Phường Gia Viên", "Phường Đông Khê"], "Phường Gia Viên"),

    # Quận Lê Chân - items 12-13
    ("Quận Lê Chân", ["Phường Hàng Kênh", "Phường Dư Hàng Kênh", "Phường Kênh Dương", "Phường An Biên", "Phường Trần Nguyên Hãn", "Phường Vĩnh Niệm", "Phường Cầu Đất", "Phường Lạch Tray"], "Phường Lê Chân"),
    ("Quận Lê Chân", ["Phường An Dương", "Phường An Biên", "Phường Trần Nguyên Hãn", "Phường Vĩnh Niệm"], "Phường An Biên"),

    # Quận Hải An - items 14-15
    ("Quận Hải An", ["Phường Cát Bi", "Phường Đằng Lâm", "Phường Thành Tô", "Phường Đằng Hải", "Phường Tràng Cát", "Phường Nam Hải", "Phường Đông Hải 2"], "Phường Hải An"),
    ("Quận Hải An", ["Phường Đông Hải 1", "Phường Đông Hải 2", "Phường Nam Hải"], "Phường Đông Hải"),

    # Quận Kiến An - items 16-17
    ("Quận Kiến An", ["Phường Nam Sơn", "Phường Đồng Hòa", "Phường Bắc Sơn", "Phường Trần Thành Ngọ", "Phường Văn Đẩu"], "Phường Kiến An"),
    ("Quận Kiến An", ["Phường Bắc Hà", "Phường Ngọc Sơn", "Thị trấn Trường Sơn", "Phường Nam Sơn", "Phường Đồng Hòa", "Phường Bắc Sơn", "Phường Trần Thành Ngọ", "Phường Văn Đẩu"], "Phường Phù Liễn"),

    # Quận Đồ Sơn - items 18-19
    ("Quận Đồ Sơn", ["Phường Minh Đức", "Phường Bàng La", "Phường Hợp Đức", "Phường Vạn Hương", "Phường Ngọc Xuyên"], "Phường Nam Đồ Sơn"),
    ("Quận Đồ Sơn", ["Phường Hải Sơn", "Phường Tân Thành", "Phường Vạn Hương", "Phường Ngọc Xuyên"], "Phường Đồ Sơn"),

    # Quận Dương Kinh - items 20-21
    ("Quận Dương Kinh", ["Phường Đa Phúc", "Phường Hưng Đạo", "Phường Anh Dũng", "Phường Hải Thành"], "Phường Hưng Đạo"),
    ("Quận Dương Kinh", ["Phường Hòa Nghĩa", "Phường Tân Thành", "Phường Anh Dũng", "Phường Hải Thành"], "Phường Dương Kinh"),

    # Quận An Dương - items 22-24
    ("Quận An Dương", ["Phường Nam Sơn", "Phường An Hải", "Phường Lê Lợi", "Phường Đồng Thái", "Phường Tân Tiến", "Phường An Hưng"], "Phường An Dương"),
    ("Quận An Dương", ["Phường An Đồng", "Phường Hồng Thái", "Phường Lê Lợi", "Phường An Hải", "Phường Đồng Thái"], "Phường An Hải"),
    ("Quận An Dương", ["Phường An Hòa", "Phường Hồng Phong", "Phường Đại Bản", "Phường Lê Thiện", "Phường Tân Tiến", "Phường Lê Lợi"], "Phường An Phong"),

    # Thành phố Hải Dương - items 25-33
    ("Thành phố Hải Dương", ["Phường Trần Hưng Đạo", "Phường Nhị Châu", "Phường Ngọc Châu", "Phường Quang Trung"], "Phường Hải Dương"),
    ("Thành phố Hải Dương", ["Phường Tân Bình", "Phường Thanh Bình", "Phường Lê Thanh Nghị", "Phường Trần Phú"], "Phường Lê Thanh Nghị"),
    ("Thành phố Hải Dương", ["Phường Việt Hòa", "Xã Cao An", "Phường Tứ Minh", "Thị trấn Lai Cách"], "Phường Việt Hòa"),
    ("Thành phố Hải Dương", ["Phường Cẩm Thượng", "Phường Bình Hàn", "Phường Nguyễn Trãi", "Xã An Thượng"], "Phường Thành Đông"),
    ("Thành phố Hải Dương", ["Phường Nam Đồng", "Xã Tiền Tiến"], "Phường Nam Đồng"),
    ("Thành phố Hải Dương", ["Phường Hải Tân", "Phường Tân Hưng", "Xã Ngọc Sơn", "Phường Trần Phú"], "Phường Tân Hưng"),
    ("Thành phố Hải Dương", ["Phường Thạch Khôi", "Xã Gia Xuyên", "Xã Liên Hồng", "Xã Thống Nhất"], "Phường Thạch Khôi"),
    ("Thành phố Hải Dương", ["Xã Cẩm Đoài", "Phường Tứ Minh", "Thị trấn Lai Cách"], "Phường Tứ Minh"),
    ("Thành phố Hải Dương", ["Phường Ái Quốc", "Xã Quyết Thắng", "Xã Hồng Lạc"], "Phường Ái Quốc"),

    # Thành phố Chí Linh - items 34-39
    ("Thành phố Chí Linh", ["Phường Sao Đỏ", "Phường Văn An", "Phường Chí Minh", "Phường Thái Học", "Phường Cộng Hòa", "Phường Văn Đức"], "Phường Chu Văn An"),
    ("Thành phố Chí Linh", ["Phường Phả Lại", "Phường Cổ Thành", "Xã Nhân Huệ"], "Phường Chí Linh"),
    ("Thành phố Chí Linh", ["Xã Lê Lợi", "Xã Hưng Đạo", "Phường Cộng Hòa"], "Phường Trần Hưng Đạo"),
    ("Thành phố Chí Linh", ["Phường Bến Tắm", "Xã Bắc An", "Xã Hoàng Hoa Thám"], "Phường Nguyễn Trãi"),
    ("Thành phố Chí Linh", ["Phường Hoàng Tân", "Phường Hoàng Tiến", "Phường Văn Đức"], "Phường Trần Nhân Tông"),
    ("Thành phố Chí Linh", ["Phường Tân Dân", "Phường An Lạc", "Phường Đồng Lạc"], "Phường Lê Đại Hành"),

    # Thị xã Kinh Môn - items 40-45
    ("Thị xã Kinh Môn", ["Phường An Lưu", "Phường Hiệp An", "Phường Long Xuyên"], "Phường Kinh Môn"),
    ("Thị xã Kinh Môn", ["Phường Thái Thịnh", "Phường Hiến Thành", "Xã Minh Hòa"], "Phường Nguyễn Đại Năng"),
    ("Thị xã Kinh Môn", ["Phường An Phụ", "Xã Hiệp Hòa", "Xã Thượng Quận"], "Phường Trần Liễu"),
    ("Thị xã Kinh Môn", ["Phường Thất Hùng", "Xã Bạch Đằng", "Xã Lê Ninh", "Phường Văn Đức"], "Phường Bắc An Phụ"),
    ("Thị xã Kinh Môn", ["Phường Phạm Thái", "Phường An Sinh", "Phường Hiệp Sơn"], "Phường Phạm Sư Mạnh"),
    ("Thị xã Kinh Môn", ["Phường Tân Dân", "Phường Minh Tân", "Phường Duy Tân", "Phường Phú Thứ"], "Phường Nhị Chiểu"),

    # Huyện An Lão - items 46-50
    ("Huyện An Lão", ["Xã An Thái", "Xã An Thọ", "Xã Chiến Thắng"], "Xã An Hưng"),
    ("Huyện An Lão", ["Xã Tân Viên", "Xã Mỹ Đức", "Xã Thái Sơn"], "Xã An Khánh"),
    ("Huyện An Lão", ["Xã Quốc Tuấn", "Xã Quang Trung", "Xã Quang Hưng"], "Xã An Quang"),
    ("Huyện An Lão", ["Xã Bát Trang", "Xã Trường Thọ", "Xã Trường Thành"], "Xã An Trường"),
    ("Huyện An Lão", ["Thị trấn An Lão", "Xã An Thắng", "Xã Tân Dân", "Xã An Tiến", "Thị trấn Trường Sơn", "Xã Thái Sơn"], "Xã An Lão"),

    # Huyện Kiến Thụy - items 51-55
    ("Huyện Kiến Thụy", ["Thị trấn Núi Đối", "Xã Thanh Sơn", "Xã Thuận Thiên", "Xã Hữu Bằng", "Xã Kiến Hưng"], "Xã Kiến Thụy"),
    ("Huyện Kiến Thụy", ["Xã Minh Tân", "Xã Đại Đồng", "Xã Đông Phương"], "Xã Kiến Minh"),
    ("Huyện Kiến Thụy", ["Xã Tân Phong", "Xã Đại Hợp", "Xã Tú Sơn", "Xã Đoàn Xá"], "Xã Kiến Hải"),
    ("Huyện Kiến Thụy", ["Xã Tân Trào", "Xã Kiến Hưng", "Xã Đoàn Xá"], "Xã Kiến Hưng"),
    ("Huyện Kiến Thụy", ["Xã Ngũ Phúc", "Xã Kiến Quốc", "Xã Du Lễ"], "Xã Nghi Dương"),

    # Huyện Tiên Lãng - items 56-61
    ("Huyện Tiên Lãng", ["Xã Đại Thắng", "Xã Tiên Cường", "Xã Tự Cường"], "Xã Quyết Thắng"),
    ("Huyện Tiên Lãng", ["Thị trấn Tiên Lãng", "Xã Quyết Tiến", "Xã Tiên Thanh", "Xã Khởi Nghĩa"], "Xã Tiên Lãng"),
    ("Huyện Tiên Lãng", ["Xã Cấp Tiến", "Xã Kiến Thiết", "Xã Đoàn Lập", "Xã Tân Minh"], "Xã Tân Minh"),
    ("Huyện Tiên Lãng", ["Xã Tiên Thắng", "Xã Tiên Minh", "Xã Tân Minh"], "Xã Tiên Minh"),
    ("Huyện Tiên Lãng", ["Xã Nam Hưng", "Xã Bắc Hưng", "Xã Đông Hưng", "Xã Tây Hưng"], "Xã Chấn Hưng"),
    ("Huyện Tiên Lãng", ["Xã Hùng Thắng", "Xã Vinh Quang"], "Xã Hùng Thắng"),

    # Huyện Vĩnh Bảo - items 62-68
    ("Huyện Vĩnh Bảo", ["Thị trấn Vĩnh Bảo", "Xã Vĩnh Hưng", "Xã Tân Hưng", "Xã Tân Liên"], "Xã Vĩnh Bảo"),
    ("Huyện Vĩnh Bảo", ["Xã Trấn Dương", "Xã Hòa Bình", "Xã Lý Học"], "Xã Nguyễn Bỉnh Khiêm"),
    ("Huyện Vĩnh Bảo", ["Xã Tam Cường", "Xã Cao Minh", "Xã Liên Am"], "Xã Vĩnh Am"),
    ("Huyện Vĩnh Bảo", ["Xã Tiền Phong", "Xã Vĩnh Hải"], "Xã Vĩnh Hải"),
    ("Huyện Vĩnh Bảo", ["Xã Vĩnh Hòa", "Xã Hùng Tiến"], "Xã Vĩnh Hòa"),
    ("Huyện Vĩnh Bảo", ["Xã Thắng Thủy", "Xã Trung Lập", "Xã Việt Tiến"], "Xã Vĩnh Thịnh"),
    ("Huyện Vĩnh Bảo", ["Xã Vĩnh An", "Xã Giang Biên", "Xã Dũng Tiến"], "Xã Vĩnh Thuận"),

    # Thành phố Thủy Nguyên (continued) - item 69
    ("Thành phố Thủy Nguyên", ["Xã Ninh Sơn", "Xã Liên Xuân"], "Xã Việt Khê"),

    # Thị xã Kinh Môn / Huyện Nam Sách - items 70-75
    ("Thị xã Kinh Môn", ["Xã Quang Thành", "Xã Lạc Long", "Xã Thăng Long", "Xã Tuấn Việt", "Xã Vũ Dũng", "Xã Cộng Hòa"], "Xã Nam An Phụ"),
    ("Huyện Nam Sách", ["Thị trấn Nam Sách", "Xã Hồng Phong", "Xã Đồng Lạc"], "Xã Nam Sách"),
    ("Huyện Nam Sách", ["Xã Minh Tân", "Xã An Sơn", "Xã Thái Tân"], "Xã Thái Tân"),
    ("Huyện Nam Sách", ["Xã Quốc Tuấn", "Xã Hiệp Cát", "Xã Trần Phú"], "Xã Trần Phú"),
    ("Huyện Nam Sách", ["Xã Nam Hưng", "Xã Nam Tân", "Xã Hợp Tiến"], "Xã Hợp Tiến"),
    ("Huyện Nam Sách", ["Xã An Bình", "Xã An Phú", "Xã Cộng Hòa"], "Xã An Phú"),

    # Huyện Thanh Hà - items 76-80
    ("Huyện Thanh Hà", ["Thị trấn Thanh Hà", "Xã Thanh Sơn", "Xã Thanh Tân"], "Xã Thanh Hà"),
    ("Huyện Thanh Hà", ["Xã Tân An", "Xã An Phượng", "Xã Thanh Hải"], "Xã Hà Tây"),
    ("Huyện Thanh Hà", ["Xã Tân Việt", "Xã Cẩm Việt", "Xã Hồng Lạc"], "Xã Hà Bắc"),
    ("Huyện Thanh Hà", ["Xã Thanh Xuân", "Xã Liên Mạc", "Xã Thanh Lang", "Xã Thanh An", "Xã Hòa Bình"], "Xã Hà Nam"),
    ("Huyện Thanh Hà", ["Xã Thanh Hồng", "Xã Vĩnh Cường", "Xã Thanh Quang"], "Xã Hà Đông"),

    # Huyện Cẩm Giàng - items 81-84
    ("Huyện Cẩm Giàng", ["Xã Tân Trường", "Xã Cẩm Đông", "Xã Phúc Điền"], "Xã Mao Điền"),
    ("Huyện Cẩm Giàng", ["Xã Lương Điền", "Xã Ngọc Liên", "Xã Cẩm Hưng", "Xã Phúc Điền"], "Xã Cẩm Giàng"),
    ("Huyện Cẩm Giàng", ["Thị trấn Cẩm Giang", "Xã Định Sơn", "Xã Cẩm Hoàng"], "Xã Cẩm Giang"),
    ("Huyện Cẩm Giàng", ["Xã Đức Chính", "Xã Cẩm Vũ", "Xã Cẩm Văn"], "Xã Tuệ Tĩnh"),

    # Huyện Bình Giang - items 85-88
    ("Huyện Bình Giang", ["Xã Vĩnh Hưng", "Xã Hùng Thắng", "Thị trấn Kẻ Sặt", "Xã Vĩnh Hồng"], "Xã Kẻ Sặt"),
    ("Huyện Bình Giang", ["Xã Tân Việt", "Xã Long Xuyên", "Xã Hồng Khê", "Xã Cổ Bì", "Xã Vĩnh Hồng"], "Xã Bình Giang"),
    ("Huyện Bình Giang", ["Xã Thúc Kháng", "Xã Thái Minh", "Xã Tân Hồng", "Xã Thái Dương", "Xã Thái Hòa"], "Xã Đường An"),
    ("Huyện Bình Giang", ["Xã Bình Xuyên", "Xã Thanh Tùng", "Xã Đoàn Tùng", "Xã Thúc Kháng", "Xã Thái Minh", "Xã Tân Hồng", "Xã Thái Dương", "Xã Thái Hòa"], "Xã Thượng Hồng"),

    # Huyện Gia Lộc - items 89-92
    ("Huyện Gia Lộc", ["Xã Gia Tiến", "Thị trấn Gia Lộc", "Xã Gia Phúc", "Xã Yết Kiêu", "Xã Lê Lợi"], "Xã Gia Lộc"),
    ("Huyện Gia Lộc", ["Xã Thống Nhất", "Xã Lê Lợi", "Xã Yết Kiêu"], "Xã Yết Kiêu"),
    ("Huyện Gia Lộc", ["Xã Toàn Thắng", "Xã Hoàng Diệu", "Xã Hồng Hưng", "Xã Thống Kênh", "Xã Đoàn Thượng", "Xã Quang Đức", "Thị trấn Gia Lộc", "Xã Gia Phúc"], "Xã Gia Phúc"),
    ("Huyện Gia Lộc", ["Xã Phạm Trấn", "Xã Nhật Quang", "Xã Thống Kênh", "Xã Đoàn Thượng", "Xã Quang Đức", "Thị trấn Thanh Miện"], "Xã Trường Tân"),

    # Huyện Tứ Kỳ - items 93-98
    ("Huyện Tứ Kỳ", ["Thị trấn Tứ Kỳ", "Xã Minh Đức", "Xã Quang Khải", "Xã Quang Phục"], "Xã Tứ Kỳ"),
    ("Huyện Tứ Kỳ", ["Xã Đại Hợp", "Xã Tân Kỳ", "Xã Dân An", "Xã Kỳ Sơn", "Xã Hưng Đạo"], "Xã Tân Kỳ"),
    ("Huyện Tứ Kỳ", ["Xã Bình Lãng", "Xã Đại Sơn", "Xã Thanh Hải", "Xã Hưng Đạo"], "Xã Đại Sơn"),
    ("Huyện Tứ Kỳ", ["Xã An Thanh", "Xã Văn Tố", "Xã Chí Minh"], "Xã Chí Minh"),
    ("Huyện Tứ Kỳ", ["Xã Quang Trung", "Xã Lạc Phượng", "Xã Tiên Động"], "Xã Lạc Phượng"),
    ("Huyện Tứ Kỳ", ["Xã Hà Kỳ", "Xã Nguyên Giáp", "Xã Hà Thanh", "Xã Tiên Động"], "Xã Nguyên Giáp"),

    # Huyện Ninh Giang - items 99-103
    ("Huyện Ninh Giang", ["Thị trấn Ninh Giang", "Xã Vĩnh Hòa", "Xã Hồng Dụ", "Xã Hiệp Lực"], "Xã Ninh Giang"),
    ("Huyện Ninh Giang", ["Xã Ứng Hòe", "Xã Tân Hương", "Xã Nghĩa An"], "Xã Vĩnh Lại"),
    ("Huyện Ninh Giang", ["Xã Bình Xuyên", "Xã Hồng Phong", "Xã Kiến Phúc"], "Xã Khúc Thừa Dụ"),
    ("Huyện Ninh Giang", ["Xã Tân Phong", "Xã An Đức", "Xã Đức Phúc"], "Xã Tân An"),
    ("Huyện Ninh Giang", ["Xã Tân Quang", "Xã Văn Hội", "Xã Hưng Long"], "Xã Hồng Châu"),

    # Huyện Thanh Miện - items 104-108
    ("Huyện Thanh Miện", ["Xã Cao Thắng", "Xã Ngũ Hùng", "Xã Tứ Cường", "Thị trấn Thanh Miện"], "Xã Thanh Miện"),
    ("Huyện Thanh Miện", ["Xã Hồng Quang", "Xã Lam Sơn", "Xã Lê Hồng"], "Xã Bắc Thanh Miện"),
    ("Huyện Thanh Miện", ["Xã Tân Trào", "Xã Ngô Quyền", "Xã Đoàn Kết"], "Xã Hải Hưng"),
    ("Huyện Thanh Miện", ["Xã Phạm Kha", "Xã Nhân Quyền", "Xã Thanh Tùng", "Xã Đoàn Tùng"], "Xã Nguyễn Lương Bằng"),
    ("Huyện Thanh Miện", ["Xã Hồng Phong", "Xã Thanh Giang", "Xã Chi Lăng Bắc", "Xã Chi Lăng Nam"], "Xã Nam Thanh Miện"),

    # Huyện Kim Thành - items 109-112
    ("Huyện Kim Thành", ["Thị trấn Phú Thái", "Xã Kim Xuyên", "Xã Kim Anh", "Xã Kim Liên", "Xã Thượng Quận"], "Xã Phú Thái"),
    ("Huyện Kim Thành", ["Xã Lai Khê", "Xã Vũ Dũng", "Xã Tuấn Việt", "Xã Cộng Hòa", "Xã Thanh An", "Xã Cẩm Việt"], "Xã Lai Khê"),
    ("Huyện Kim Thành", ["Xã Ngũ Phúc", "Xã Kim Tân", "Xã Kim Đính"], "Xã An Thành"),
    ("Huyện Kim Thành", ["Xã Đồng Cẩm", "Xã Tam Kỳ", "Xã Đại Đức", "Xã Hòa Bình"], "Xã Kim Thành"),

    # Đặc khu - items 113-114
    ("Đặc khu Cát Hải", ["Thị trấn Cát Hải", "Thị trấn Cát Bà", "Xã Đồng Bài", "Xã Hoàng Châu", "Xã Nghĩa Lộ", "Xã Văn Phong", "Xã Gia Luận", "Xã Hiền Hào", "Xã Phù Long", "Xã Trân Châu", "Xã Việt Hải", "Xã Xuân Đám"], "Đặc khu Cát Hải"),
    ("Đặc khu Bạch Long Vĩ", ["Huyện Bạch Long Vĩ"], "Đặc khu Bạch Long Vĩ"),
]


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

    # Process provinces
    provinces = [
        ("Tỉnh Hà Tĩnh", hatinh_restructuring_data),
        ("Thành phố Hải Phòng", haiphong_restructuring_data),
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

    print(f"\nTotal new mappings: {len(all_chuyen_doi)}")

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

    print("\nFinal totals:")
    print(f"  - dia_danh provinces: {len(existing_dia_danh)}")
    print(f"  - chuyen_doi mappings: {len(existing_chuyen_doi)}")


if __name__ == "__main__":
    main()

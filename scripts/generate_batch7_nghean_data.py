#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch 7 Part 1: Generate Nghệ An province data
Province: Tỉnh Nghệ An (121 items)
"""

import json
import os

# Nghệ An restructuring data - 121 items organized by district
nghean_restructuring_data = [
    # Huyện Anh Sơn - items 1-6
    ("Huyện Anh Sơn", ["Thị trấn Kim Nhan", "Xã Đức Sơn", "Xã Phúc Sơn"], "Xã Anh Sơn"),
    ("Huyện Anh Sơn", ["Xã Cao Sơn", "Xã Khai Sơn", "Xã Lĩnh Sơn", "Xã Long Sơn"], "Xã Yên Xuân"),
    ("Huyện Anh Sơn", ["Xã Cẩm Sơn", "Xã Hùng Sơn", "Xã Tam Đỉnh"], "Xã Nhân Hòa"),
    ("Huyện Anh Sơn", ["Xã Lạng Sơn", "Xã Tào Sơn", "Xã Vĩnh Sơn"], "Xã Anh Sơn Đông"),
    ("Huyện Anh Sơn", ["Xã Hoa Sơn", "Xã Hội Sơn", "Xã Tường Sơn"], "Xã Vĩnh Tường"),
    ("Huyện Anh Sơn", ["Xã Bình Sơn", "Xã Thành Sơn", "Xã Thọ Sơn"], "Xã Thành Bình Thọ"),

    # Huyện Con Cuông - items 7-11
    ("Huyện Con Cuông", ["Thị trấn Trà Lân", "Xã Chi Khê", "Xã Yên Khê"], "Xã Con Cuông"),
    ("Huyện Con Cuông", ["Xã Lục Dạ", "Xã Môn Sơn"], "Xã Môn Sơn"),
    ("Huyện Con Cuông", ["Xã Mậu Đức", "Xã Thạch Ngàn"], "Xã Mậu Thạch"),
    ("Huyện Con Cuông", ["Xã Cam Lâm", "Xã Đôn Phục"], "Xã Cam Phục"),
    ("Huyện Con Cuông", ["Xã Lạng Khê", "Xã Châu Khê"], "Xã Châu Khê"),

    # Huyện Diễn Châu - items 12-19
    ("Huyện Diễn Châu", ["Thị trấn Diễn Thành", "Xã Diễn Hoa", "Xã Diễn Phúc", "Xã Ngọc Bích"], "Xã Diễn Châu"),
    ("Huyện Diễn Châu", ["Xã Diễn Hồng", "Xã Diễn Kỷ", "Xã Diễn Phong", "Xã Diễn Vạn"], "Xã Đức Châu"),
    ("Huyện Diễn Châu", ["Xã Diễn Đồng", "Xã Diễn Liên", "Xã Diễn Thái", "Xã Xuân Tháp"], "Xã Quảng Châu"),
    ("Huyện Diễn Châu", ["Xã Diễn Hoàng", "Xã Diễn Kim", "Xã Diễn Mỹ", "Xã Hùng Hải"], "Xã Hải Châu"),
    ("Huyện Diễn Châu", ["Xã Diễn Lộc", "Xã Diễn Lợi", "Xã Diễn Phú", "Xã Diễn Thọ"], "Xã Tân Châu"),
    ("Huyện Diễn Châu", ["Xã Diễn An", "Xã Diễn Tân", "Xã Diễn Thịnh", "Xã Diễn Trung"], "Xã An Châu"),
    ("Huyện Diễn Châu", ["Xã Diễn Cát", "Xã Diễn Nguyên", "Xã Hạnh Quảng", "Xã Minh Châu"], "Xã Minh Châu"),
    ("Huyện Diễn Châu", ["Xã Diễn Đoài", "Xã Diễn Lâm", "Xã Diễn Trường", "Xã Diễn Yên"], "Xã Hùng Châu"),

    # Huyện Đô Lương - items 20-25
    ("Huyện Đô Lương", ["Xã Bắc Sơn", "Xã Nam Sơn", "Xã Đà Sơn", "Xã Đặng Sơn", "Xã Lưu Sơn", "Xã Thịnh Sơn", "Xã Văn Sơn", "Xã Yên Sơn", "Thị trấn Đô Lương"], "Xã Đô Lương"),
    ("Huyện Đô Lương", ["Xã Bồi Sơn", "Xã Giang Sơn Đông", "Xã Giang Sơn Tây", "Xã Bạch Ngọc"], "Xã Bạch Ngọc"),
    ("Huyện Đô Lương", ["Xã Tân Sơn", "Xã Hòa Sơn", "Xã Quang Sơn", "Xã Thái Sơn", "Xã Thượng Sơn"], "Xã Văn Hiến"),
    ("Huyện Đô Lương", ["Xã Đại Sơn", "Xã Hiến Sơn", "Xã Mỹ Sơn", "Xã Trù Sơn"], "Xã Bạch Hà"),
    ("Huyện Đô Lương", ["Xã Minh Sơn", "Xã Lạc Sơn", "Xã Nhân Sơn", "Xã Thuận Sơn", "Xã Trung Sơn", "Xã Xuân Sơn"], "Xã Thuần Trung"),
    ("Huyện Đô Lương", ["Xã Bài Sơn", "Xã Đông Sơn", "Xã Hồng Sơn", "Xã Tràng Sơn"], "Xã Lương Sơn"),

    # Huyện Hưng Nguyên - items 26-29
    ("Huyện Hưng Nguyên", ["Thị trấn Hưng Nguyên", "Xã Hưng Đạo", "Xã Hưng Tây", "Xã Thịnh Mỹ"], "Xã Hưng Nguyên"),
    ("Huyện Hưng Nguyên", ["Xã Hưng Yên Bắc", "Xã Hưng Yên Nam", "Xã Hưng Trung"], "Xã Yên Trung"),
    ("Huyện Hưng Nguyên", ["Xã Hưng Lĩnh", "Xã Long Xá", "Xã Thông Tân", "Xã Xuân Lam"], "Xã Hưng Nguyên Nam"),
    ("Huyện Hưng Nguyên", ["Xã Châu Nhân", "Xã Hưng Nghĩa", "Xã Hưng Thành", "Xã Phúc Lợi"], "Xã Lam Thành"),

    # Huyện Kỳ Sơn - items 30-36
    ("Huyện Kỳ Sơn", ["Xã Bảo Thắng", "Xã Chiêu Lưu"], "Xã Chiêu Lưu"),
    ("Huyện Kỳ Sơn", ["Xã Bảo Nam", "Xã Hữu Lập", "Xã Hữu Kiệm"], "Xã Hữu Kiệm"),
    ("Huyện Kỳ Sơn", ["Xã Mường Ải", "Xã Mường Típ"], "Xã Mường Típ"),
    ("Huyện Kỳ Sơn", ["Thị trấn Mường Xén", "Xã Tà Cạ", "Xã Tây Sơn"], "Xã Mường Xén"),
    ("Huyện Kỳ Sơn", ["Xã Đoọc Mạy", "Xã Na Loi"], "Xã Na Loi"),
    ("Huyện Kỳ Sơn", ["Xã Nậm Càn", "Xã Na Ngoi"], "Xã Na Ngoi"),
    ("Huyện Kỳ Sơn", ["Xã Phà Đánh", "Xã Nậm Cắn"], "Xã Nậm Cắn"),

    # Huyện Nam Đàn - items 37-41
    ("Huyện Nam Đàn", ["Xã Hùng Tiến", "Xã Nam Cát", "Xã Nam Giang", "Xã Xuân Hồng", "Xã Kim Liên"], "Xã Kim Liên"),
    ("Huyện Nam Đàn", ["Thị trấn Nam Đàn", "Xã Thượng Tân Lộc", "Xã Xuân Hòa"], "Xã Vạn An"),
    ("Huyện Nam Đàn", ["Xã Nghĩa Thái", "Xã Nam Hưng", "Xã Nam Thanh"], "Xã Nam Đàn"),
    ("Huyện Nam Đàn", ["Xã Nam Anh", "Xã Nam Lĩnh", "Xã Nam Xuân"], "Xã Đại Huệ"),
    ("Huyện Nam Đàn", ["Xã Khánh Sơn", "Xã Nam Kim", "Xã Trung Phúc Cường"], "Xã Thiên Nhẫn"),

    # Huyện Nghĩa Đàn - items 42-48
    ("Huyện Nghĩa Đàn", ["Thị trấn Nghĩa Đàn", "Xã Nghĩa Bình", "Xã Nghĩa Trung"], "Xã Nghĩa Đàn"),
    ("Huyện Nghĩa Đàn", ["Xã Nghĩa Hội", "Xã Nghĩa Lợi", "Xã Nghĩa Thọ"], "Xã Nghĩa Thọ"),
    ("Huyện Nghĩa Đàn", ["Xã Nghĩa Lạc", "Xã Nghĩa Sơn", "Xã Nghĩa Yên", "Xã Nghĩa Lâm"], "Xã Nghĩa Lâm"),
    ("Huyện Nghĩa Đàn", ["Xã Nghĩa Hồng", "Xã Nghĩa Minh", "Xã Nghĩa Mai"], "Xã Nghĩa Mai"),
    ("Huyện Nghĩa Đàn", ["Xã Nghĩa Thành", "Xã Nghĩa Hưng"], "Xã Nghĩa Hưng"),
    ("Huyện Nghĩa Đàn", ["Xã Nghĩa An", "Xã Nghĩa Đức", "Xã Nghĩa Khánh"], "Xã Nghĩa Khánh"),
    ("Huyện Nghĩa Đàn", ["Xã Nghĩa Long", "Xã Nghĩa Lộc"], "Xã Nghĩa Lộc"),

    # Huyện Nghi Lộc - items 49-55
    ("Huyện Nghi Lộc", ["Thị trấn Quán Hành", "Xã Diên Hoa", "Xã Nghi Trung", "Xã Nghi Vạn"], "Xã Nghi Lộc"),
    ("Huyện Nghi Lộc", ["Xã Nghi Công Bắc", "Xã Nghi Công Nam", "Xã Nghi Lâm", "Xã Nghi Mỹ"], "Xã Phúc Lộc"),
    ("Huyện Nghi Lộc", ["Xã Khánh Hợp", "Xã Nghi Thạch", "Xã Thịnh Trường"], "Xã Đông Lộc"),
    ("Huyện Nghi Lộc", ["Xã Nghi Long", "Xã Nghi Quang", "Xã Nghi Thuận", "Xã Nghi Xá"], "Xã Trung Lộc"),
    ("Huyện Nghi Lộc", ["Xã Nghi Đồng", "Xã Nghi Hưng", "Xã Nghi Phương"], "Xã Thần Lĩnh"),
    ("Huyện Nghi Lộc", ["Xã Nghi Thiết", "Xã Nghi Tiến", "Xã Nghi Yên"], "Xã Hải Lộc"),
    ("Huyện Nghi Lộc", ["Xã Nghi Kiều", "Xã Nghi Văn"], "Xã Văn Kiều"),

    # Huyện Quế Phong - items 56-60
    ("Huyện Quế Phong", ["Xã Cắm Muộn", "Xã Châu Thôn", "Xã Quang Phong"], "Xã Mường Quàng"),
    ("Huyện Quế Phong", ["Thị trấn Kim Sơn", "Xã Châu Kim", "Xã Mường Nọc", "Xã Nậm Giải"], "Xã Quế Phong"),
    ("Huyện Quế Phong", ["Xã Đồng Văn", "Xã Thông Thụ"], "Xã Thông Thụ"),
    ("Huyện Quế Phong", ["Xã Hạnh Dịch", "Xã Tiền Phong"], "Xã Tiền Phong"),
    ("Huyện Quế Phong", ["Xã Nậm Nhoóng", "Xã Tri Lễ"], "Xã Tri Lễ"),

    # Huyện Quỳ Châu - items 61-63
    ("Huyện Quỳ Châu", ["Thị trấn Tân Lạc", "Xã Châu Hạnh", "Xã Châu Hội", "Xã Châu Nga"], "Xã Quỳ Châu"),
    ("Huyện Quỳ Châu", ["Xã Châu Tiến", "Xã Châu Bính", "Xã Châu Thắng", "Xã Châu Thuận"], "Xã Châu Tiến"),
    ("Huyện Quỳ Châu", ["Xã Châu Hoàn", "Xã Châu Phong", "Xã Diên Lãm"], "Xã Hùng Chân"),

    # Huyện Quỳ Hợp - items 64-70
    ("Huyện Quỳ Hợp", ["Thị trấn Quỳ Hợp", "Xã Châu Đình", "Xã Châu Quang", "Xã Thọ Hợp"], "Xã Quỳ Hợp"),
    ("Huyện Quỳ Hợp", ["Xã Tam Hợp", "Xã Đồng Hợp", "Xã Nghĩa Xuân", "Xã Yên Hợp"], "Xã Tam Hợp"),
    ("Huyện Quỳ Hợp", ["Xã Liên Hợp", "Xã Châu Lộc"], "Xã Châu Lộc"),
    ("Huyện Quỳ Hợp", ["Xã Châu Tiến", "Xã Châu Thành", "Xã Châu Hồng"], "Xã Châu Hồng"),
    ("Huyện Quỳ Hợp", ["Xã Châu Cường", "Xã Châu Thái"], "Xã Mường Ham"),
    ("Huyện Quỳ Hợp", ["Xã Bắc Sơn", "Xã Nam Sơn", "Xã Châu Lý"], "Xã Mường Chọng"),
    ("Huyện Quỳ Hợp", ["Xã Hạ Sơn", "Xã Văn Lợi", "Xã Minh Hợp"], "Xã Minh Hợp"),

    # Huyện Quỳnh Lưu - items 71-77
    ("Huyện Quỳnh Lưu", ["Thị trấn Cầu Giát", "Xã Bình Sơn", "Xã Quỳnh Diễn", "Xã Quỳnh Giang", "Xã Quỳnh Hậu"], "Xã Quỳnh Lưu"),
    ("Huyện Quỳnh Lưu", ["Xã Quỳnh Tân", "Xã Quỳnh Thạch", "Xã Quỳnh Văn"], "Xã Quỳnh Văn"),
    ("Huyện Quỳnh Lưu", ["Xã Minh Lương", "Xã Quỳnh Bảng", "Xã Quỳnh Đôi", "Xã Quỳnh Thanh", "Xã Quỳnh Yên"], "Xã Quỳnh Anh"),
    ("Huyện Quỳnh Lưu", ["Xã Tân Sơn", "Xã Quỳnh Châu", "Xã Quỳnh Tam"], "Xã Quỳnh Tam"),
    ("Huyện Quỳnh Lưu", ["Xã An Hòa", "Xã Phú Nghĩa", "Xã Thuận Long", "Xã Văn Hải"], "Xã Quỳnh Phú"),
    ("Huyện Quỳnh Lưu", ["Xã Ngọc Sơn", "Xã Quỳnh Lâm", "Xã Quỳnh Sơn"], "Xã Quỳnh Sơn"),
    ("Huyện Quỳnh Lưu", ["Xã Tân Thắng", "Xã Quỳnh Thắng"], "Xã Quỳnh Thắng"),

    # Huyện Tân Kỳ - items 78-84
    ("Huyện Tân Kỳ", ["Thị trấn Tân Kỳ", "Xã Nghĩa Dũng", "Xã Kỳ Tân", "Xã Kỳ Sơn"], "Xã Tân Kỳ"),
    ("Huyện Tân Kỳ", ["Xã Nghĩa Thái", "Xã Hoàn Long", "Xã Tân Xuân", "Xã Tân Phú"], "Xã Tân Phú"),
    ("Huyện Tân Kỳ", ["Xã Hương Sơn", "Xã Nghĩa Phúc", "Xã Tân An"], "Xã Tân An"),
    ("Huyện Tân Kỳ", ["Xã Bình Hợp", "Xã Nghĩa Đồng"], "Xã Nghĩa Đồng"),
    ("Huyện Tân Kỳ", ["Xã Tân Hợp", "Xã Giai Xuân"], "Xã Giai Xuân"),
    ("Huyện Tân Kỳ", ["Xã Phú Sơn", "Xã Tân Hương", "Xã Nghĩa Hành"], "Xã Nghĩa Hành"),
    ("Huyện Tân Kỳ", ["Xã Đồng Văn", "Xã Tiên Kỳ"], "Xã Tiên Đồng"),

    # Thị xã Thái Hòa - items 85-86 (xã)
    ("Thị xã Thái Hòa", ["Xã Nghĩa Mỹ", "Xã Nghĩa Thuận", "Xã Đông Hiếu"], "Xã Đông Hiếu"),
    ("Thị xã Thái Hòa", ["Xã Mai Giang", "Xã Thanh Lâm", "Xã Thanh Tùng", "Xã Thanh Xuân"], "Xã Bích Hào"),

    # Huyện Thanh Chương - items 87-95
    ("Huyện Thanh Chương", ["Xã Minh Sơn", "Xã Cát Văn", "Xã Phong Thịnh"], "Xã Cát Ngạn"),
    ("Huyện Thanh Chương", ["Thị trấn Dùng", "Xã Đồng Văn", "Xã Thanh Ngọc", "Xã Thanh Phong", "Xã Đại Đồng"], "Xã Đại Đồng"),
    ("Huyện Thanh Chương", ["Xã Thanh Đức", "Xã Hạnh Lâm"], "Xã Hạnh Lâm"),
    ("Huyện Thanh Chương", ["Xã Thanh An", "Xã Thanh Hương", "Xã Thanh Quả", "Xã Thanh Thịnh"], "Xã Hoa Quân"),
    ("Huyện Thanh Chương", ["Xã Thanh Hà", "Xã Thanh Thủy", "Xã Kim Bảng"], "Xã Kim Bảng"),
    ("Huyện Thanh Chương", ["Xã Ngọc Lâm", "Xã Thanh Sơn"], "Xã Sơn Lâm"),
    ("Huyện Thanh Chương", ["Xã Thanh Liên", "Xã Thanh Mỹ", "Xã Thanh Tiên"], "Xã Tam Đồng"),
    ("Huyện Thanh Chương", ["Xã Ngọc Sơn", "Xã Minh Tiến", "Xã Xuân Dương"], "Xã Xuân Lâm"),
    ("Huyện Thanh Chương", ["Xã Xiêng My", "Xã Nga My"], "Xã Nga My"),

    # Huyện Tương Dương - items 96-101
    ("Huyện Tương Dương", ["Xã Mai Sơn", "Xã Nhôn Mai"], "Xã Nhôn Mai"),
    ("Huyện Tương Dương", ["Xã Tam Đình", "Xã Tam Quang"], "Xã Tam Quang"),
    ("Huyện Tương Dương", ["Xã Tam Hợp", "Xã Tam Thái"], "Xã Tam Thái"),
    ("Huyện Tương Dương", ["Thị trấn Thạch Giám", "Xã Lưu Kiền", "Xã Xá Lượng"], "Xã Tương Dương"),
    ("Huyện Tương Dương", ["Xã Yên Thắng", "Xã Yên Hòa"], "Xã Yên Hòa"),
    ("Huyện Tương Dương", ["Xã Yên Tĩnh", "Xã Yên Na"], "Xã Yên Na"),

    # Huyện Yên Thành - items 102-110
    ("Huyện Yên Thành", ["Thị trấn Hoa Thành", "Xã Đông Thành", "Xã Tăng Thành", "Xã Văn Thành"], "Xã Yên Thành"),
    ("Huyện Yên Thành", ["Xã Bắc Thành", "Xã Nam Thành", "Xã Trung Thành", "Xã Xuân Thành"], "Xã Quan Thành"),
    ("Huyện Yên Thành", ["Xã Bảo Thành", "Xã Long Thành", "Xã Sơn Thành", "Xã Viên Thành", "Xã Vĩnh Thành"], "Xã Hợp Minh"),
    ("Huyện Yên Thành", ["Xã Liên Thành", "Xã Mỹ Thành", "Xã Vân Tụ"], "Xã Vân Tụ"),
    ("Huyện Yên Thành", ["Xã Minh Thành", "Xã Tây Thành", "Xã Thịnh Thành"], "Xã Vân Du"),
    ("Huyện Yên Thành", ["Xã Đồng Thành", "Xã Kim Thành", "Xã Quang Thành"], "Xã Quang Đồng"),
    ("Huyện Yên Thành", ["Xã Hậu Thành", "Xã Lăng Thành", "Xã Phúc Thành"], "Xã Giai Lạc"),
    ("Huyện Yên Thành", ["Xã Đức Thành", "Xã Mã Thành", "Xã Tân Thành", "Xã Tiến Thành"], "Xã Bình Minh"),
    ("Huyện Yên Thành", ["Xã Đô Thành", "Xã Phú Thành", "Xã Thọ Thành"], "Xã Đông Thành"),

    # Thị xã Hoàng Mai - items 111-113
    ("Thị xã Hoàng Mai", ["Phường Quỳnh Thiện", "Xã Quỳnh Trang", "Xã Quỳnh Vinh"], "Phường Hoàng Mai"),
    ("Thị xã Hoàng Mai", ["Phường Mai Hùng", "Phường Quỳnh Phương", "Phường Quỳnh Xuân", "Xã Quỳnh Liên"], "Phường Quỳnh Mai"),
    ("Thị xã Hoàng Mai", ["Phường Quỳnh Dị", "Xã Quỳnh Lập", "Xã Quỳnh Lộc"], "Phường Tân Mai"),

    # Thị xã Thái Hòa - items 114-115 (phường)
    ("Thị xã Thái Hòa", ["Phường Hòa Hiếu", "Phường Long Sơn", "Phường Quang Phong"], "Phường Thái Hòa"),
    ("Thị xã Thái Hòa", ["Phường Quang Tiến", "Xã Nghĩa Tiến", "Xã Tây Hiếu"], "Phường Tây Hiếu"),

    # Thành phố Vinh - items 116-120
    ("Thành phố Vinh", ["Phường Bến Thủy", "Phường Hưng Dũng", "Phường Hưng Phúc", "Phường Trung Đô", "Phường Trường Thi", "Phường Vinh Tân", "Xã Hưng Hòa"], "Phường Trường Vinh"),
    ("Thành phố Vinh", ["Phường Cửa Nam", "Phường Đông Vĩnh", "Phường Hưng Bình", "Phường Lê Lợi", "Phường Quang Trung", "Xã Hưng Chính"], "Phường Thành Vinh"),
    ("Thành phố Vinh", ["Phường Hưng Đông", "Phường Quán Bàu", "Xã Nghi Kim", "Xã Nghi Liên"], "Phường Vinh Hưng"),
    ("Thành phố Vinh", ["Phường Hà Huy Tập", "Phường Nghi Đức", "Phường Nghi Phú", "Xã Nghi Ân"], "Phường Vinh Phú"),
    ("Thành phố Vinh", ["Phường Hưng Lộc", "Xã Nghi Phong", "Xã Nghi Thái", "Xã Nghi Xuân", "Xã Phúc Thọ"], "Phường Vinh Lộc"),

    # Thị xã Cửa Lò - item 121
    ("Thị xã Cửa Lò", ["Phường Nghi Hải", "Phường Nghi Hòa", "Phường Nghi Hương", "Phường Nghi Tân", "Phường Nghi Thu", "Phường Nghi Thủy", "Phường Thu Thủy"], "Phường Cửa Lò"),
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

    # Process Nghệ An
    province_name = "Tỉnh Nghệ An"
    province_dia_danh, province_chuyen_doi = generate_province_data(
        province_name, nghean_restructuring_data
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

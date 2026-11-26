#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to generate restructuring data for Gia Lai (mới) and Hà Nội provinces.
Gia Lai (mới) combines Gia Lai + Bình Định provinces.
"""

import json
import os

# Gia Lai (mới) restructuring data - combines Gia Lai + Bình Định
# Items 1-40: Bình Định districts
# Items 41-101: Gia Lai districts
# Items 102-126: Urban areas

gialai_restructuring_data = [
    # Thị xã An Nhơn (Bình Định) - item 1
    ("Thị xã An Nhơn", ["Xã Nhơn Lộc", "Xã Nhơn Tân"], "Xã An Nhơn Tây"),

    # Huyện Phù Cát (Bình Định) - items 2-8
    ("Huyện Phù Cát", ["Thị trấn Ngô Mây", "Xã Cát Trinh", "Xã Cát Tân"], "Xã Phù Cát"),
    ("Huyện Phù Cát", ["Xã Cát Nhơn", "Xã Cát Tường"], "Xã Xuân An"),
    ("Huyện Phù Cát", ["Xã Cát Hưng", "Xã Cát Thắng", "Xã Cát Chánh"], "Xã Ngô Mây"),
    ("Huyện Phù Cát", ["Thị trấn Cát Tiến", "Xã Cát Thành", "Xã Cát Hải"], "Xã Cát Tiến"),
    ("Huyện Phù Cát", ["Thị trấn Cát Khánh", "Xã Cát Minh", "Xã Cát Tài"], "Xã Đề Gi"),
    ("Huyện Phù Cát", ["Xã Cát Hanh", "Xã Cát Hiệp"], "Xã Hòa Hội"),
    ("Huyện Phù Cát", ["Xã Cát Lâm", "Xã Cát Sơn"], "Xã Hội Sơn"),

    # Huyện Phù Mỹ (Bình Định) - items 9-15
    ("Huyện Phù Mỹ", ["Thị trấn Phù Mỹ", "Xã Mỹ Quang", "Xã Mỹ Chánh Tây"], "Xã Phù Mỹ"),
    ("Huyện Phù Mỹ", ["Xã Mỹ Chánh", "Xã Mỹ Thành", "Xã Mỹ Cát"], "Xã An Lương"),
    ("Huyện Phù Mỹ", ["Thị trấn Bình Dương", "Xã Mỹ Lợi", "Xã Mỹ Phong"], "Xã Bình Dương"),
    ("Huyện Phù Mỹ", ["Xã Mỹ An", "Xã Mỹ Thọ", "Xã Mỹ Thắng"], "Xã Phù Mỹ Đông"),
    ("Huyện Phù Mỹ", ["Xã Mỹ Trinh", "Xã Mỹ Hòa"], "Xã Phù Mỹ Tây"),
    ("Huyện Phù Mỹ", ["Xã Mỹ Tài", "Xã Mỹ Hiệp"], "Xã Phù Mỹ Nam"),
    ("Huyện Phù Mỹ", ["Xã Mỹ Đức", "Xã Mỹ Châu", "Xã Mỹ Lộc"], "Xã Phù Mỹ Bắc"),

    # Huyện Tuy Phước (Bình Định) - items 16-19
    ("Huyện Tuy Phước", ["Thị trấn Tuy Phước", "Thị trấn Diêu Trì", "Xã Phước Thuận", "Xã Phước Nghĩa", "Xã Phước Lộc"], "Xã Tuy Phước"),
    ("Huyện Tuy Phước", ["Xã Phước Sơn", "Xã Phước Hòa", "Xã Phước Thắng"], "Xã Tuy Phước Đông"),
    ("Huyện Tuy Phước", ["Xã Phước An", "Xã Phước Thành"], "Xã Tuy Phước Tây"),
    ("Huyện Tuy Phước", ["Xã Phước Hiệp", "Xã Phước Hưng", "Xã Phước Quang"], "Xã Tuy Phước Bắc"),

    # Huyện Tây Sơn (Bình Định) - items 20-24
    ("Huyện Tây Sơn", ["Thị trấn Phú Phong", "Xã Tây Xuân", "Xã Bình Nghi"], "Xã Tây Sơn"),
    ("Huyện Tây Sơn", ["Xã Tây Giang", "Xã Tây Thuận"], "Xã Bình Khê"),
    ("Huyện Tây Sơn", ["Xã Vĩnh An", "Xã Bình Tường", "Xã Tây Phú"], "Xã Bình Phú"),
    ("Huyện Tây Sơn", ["Xã Bình Thuận", "Xã Bình Tân", "Xã Tây An"], "Xã Bình Hiệp"),
    ("Huyện Tây Sơn", ["Xã Tây Vinh", "Xã Tây Bình", "Xã Bình Hòa", "Xã Bình Thành"], "Xã Bình An"),

    # Huyện Hoài Ân (Bình Định) - items 25-29
    ("Huyện Hoài Ân", ["Thị trấn Tăng Bạt Hổ", "Xã Ân Phong", "Xã Ân Đức", "Xã Ân Tường Đông"], "Xã Hoài Ân"),
    ("Huyện Hoài Ân", ["Xã Ân Tường Tây", "Xã Ân Hữu", "Xã Đak Mang"], "Xã Ân Tường"),
    ("Huyện Hoài Ân", ["Xã Ân Nghĩa", "Xã Bok Tới"], "Xã Kim Sơn"),
    ("Huyện Hoài Ân", ["Xã Ân Sơn", "Xã Ân Tín", "Xã Ân Thạnh"], "Xã Vạn Đức"),
    ("Huyện Hoài Ân", ["Xã Ân Hảo Tây", "Xã Ân Hảo Đông", "Xã Ân Mỹ"], "Xã Ân Hảo"),

    # Huyện Vân Canh (Bình Định) - items 30-32
    ("Huyện Vân Canh", ["Thị trấn Vân Canh", "Xã Canh Thuận", "Xã Canh Hòa", "Xã Canh Hiệp"], "Xã Vân Canh"),
    ("Huyện Vân Canh", ["Xã Canh Vinh", "Xã Canh Hiển", "Xã Canh Liên", "Xã Canh Hiệp"], "Xã Canh Vinh"),
    ("Huyện Vân Canh", ["Xã Canh Liên"], "Xã Canh Liên"),

    # Huyện Vĩnh Thạnh (Bình Định) - items 33-36
    ("Huyện Vĩnh Thạnh", ["Thị trấn Vĩnh Thạnh", "Xã Vĩnh Hảo"], "Xã Vĩnh Thạnh"),
    ("Huyện Vĩnh Thạnh", ["Xã Vĩnh Hiệp", "Xã Vĩnh Thịnh"], "Xã Vĩnh Thịnh"),
    ("Huyện Vĩnh Thạnh", ["Xã Vĩnh Thuận", "Xã Vĩnh Hòa", "Xã Vĩnh Quang"], "Xã Vĩnh Quang"),
    ("Huyện Vĩnh Thạnh", ["Xã Vĩnh Kim", "Xã Vĩnh Sơn"], "Xã Vĩnh Sơn"),

    # Huyện An Lão (Bình Định) - items 37-40
    ("Huyện An Lão", ["Xã An Hòa", "Xã An Quang", "Xã An Nghĩa"], "Xã An Hòa"),
    ("Huyện An Lão", ["Thị trấn An Lão", "Xã An Tân", "Xã An Hưng"], "Xã An Lão"),
    ("Huyện An Lão", ["Xã An Trung", "Xã An Dũng", "Xã An Vinh"], "Xã An Vinh"),
    ("Huyện An Lão", ["Xã An Toàn", "Xã An Nghĩa"], "Xã An Toàn"),

    # Thành phố Pleiku (Gia Lai) - items 41-42
    ("Thành phố Pleiku", ["Xã Nghĩa Hưng", "Xã Chư Đang Ya", "Xã Hà Bầu", "Xã Biển Hồ"], "Xã Biển Hồ"),
    ("Thành phố Pleiku", ["Xã Ia Kênh", "Xã Ia Pếch", "Xã Gào"], "Xã Gào"),

    # Huyện Chư Păh (Gia Lai) - items 43-46
    ("Huyện Chư Păh", ["Thị trấn Ia Ly", "Xã Ia Mơ Nông", "Xã Ia Kreng"], "Xã Ia Ly"),
    ("Huyện Chư Păh", ["Thị trấn Phú Hòa", "Xã Nghĩa Hòa", "Xã Hòa Phú"], "Xã Chư Păh"),
    ("Huyện Chư Păh", ["Xã Đăk Tơ Ver", "Xã Hà Tây", "Xã Ia Khươl"], "Xã Ia Khươl"),
    ("Huyện Chư Păh", ["Xã Ia Ka", "Xã Ia Nhin", "Xã Ia Phí"], "Xã Ia Phí"),

    # Huyện Chư Prông (Gia Lai) - items 47-52
    ("Huyện Chư Prông", ["Thị trấn Chư Prông", "Xã Ia Phìn", "Xã Ia Kly", "Xã Ia Drang"], "Xã Chư Prông"),
    ("Huyện Chư Prông", ["Xã Thăng Hưng", "Xã Bình Giáo", "Xã Bàu Cạn"], "Xã Bàu Cạn"),
    ("Huyện Chư Prông", ["Xã Ia O", "Xã Ia Me", "Xã Ia Boòng"], "Xã Ia Boòng"),
    ("Huyện Chư Prông", ["Xã Ia Piơr", "Xã Ia Lâu"], "Xã Ia Lâu"),
    ("Huyện Chư Prông", ["Xã Ia Ga", "Xã Ia Vê", "Xã Ia Pia"], "Xã Ia Pia"),
    ("Huyện Chư Prông", ["Xã Ia Băng", "Xã Ia Bang", "Xã Ia Tôr"], "Xã Ia Tôr"),

    # Huyện Chư Sê (Gia Lai) - items 53-56
    ("Huyện Chư Sê", ["Thị trấn Chư Sê", "Xã Dun", "Xã Ia Blang", "Xã Ia Pal", "Xã Ia Glai"], "Xã Chư Sê"),
    ("Huyện Chư Sê", ["Xã Bar Măih", "Xã Ia Tiêm", "Xã Chư Pơng", "Xã Bờ Ngoong"], "Xã Bờ Ngoong"),
    ("Huyện Chư Sê", ["Xã Ia Hlốp", "Xã Ia Hla", "Xã Ia Ko"], "Xã Ia Ko"),
    ("Huyện Chư Sê", ["Xã Ayun", "Xã Kông Htok", "Xã Al Bá"], "Xã Al Bá"),

    # Huyện Chư Pưh (Gia Lai) - items 57-59
    ("Huyện Chư Pưh", ["Thị trấn Nhơn Hòa", "Xã Chư Don", "Xã Ia Phang"], "Xã Chư Pưh"),
    ("Huyện Chư Pưh", ["Xã Ia Blứ", "Xã Ia Le"], "Xã Ia Le"),
    ("Huyện Chư Pưh", ["Xã Ia Dreng", "Xã Ia Rong", "Xã HBông", "Xã Ia Hrú"], "Xã Ia Hrú"),

    # Thị xã An Khê (Gia Lai) - item 60
    ("Thị xã An Khê", ["Xã Tú An", "Xã Xuân An", "Xã Song An", "Xã Cửu An"], "Xã Cửu An"),

    # Huyện Đak Pơ (Gia Lai) - items 61-62
    ("Huyện Đak Pơ", ["Thị trấn Đak Pơ", "Xã Hà Tam", "Xã An Thành", "Xã Yang Bắc"], "Xã Đak Pơ"),
    ("Huyện Đak Pơ", ["Xã Phú An", "Xã Ya Hội"], "Xã Ya Hội"),

    # Huyện Kbang (Gia Lai) - items 63-67
    ("Huyện Kbang", ["Thị trấn Kbang", "Xã Lơ Ku", "Xã Đak Smar"], "Xã Kbang"),
    ("Huyện Kbang", ["Xã Đông", "Xã Nghĩa An", "Xã Kông Bơ La"], "Xã Kông Bơ La"),
    ("Huyện Kbang", ["Xã Kông Lơng Khơng", "Xã Tơ Tung"], "Xã Tơ Tung"),
    ("Huyện Kbang", ["Xã Sơ Pai", "Xã Sơn Lang"], "Xã Sơn Lang"),
    ("Huyện Kbang", ["Xã Kon Pne", "Xã Đak Rong"], "Xã Đak Rong"),

    # Huyện Kông Chro (Gia Lai) - items 68-73
    ("Huyện Kông Chro", ["Thị trấn Kông Chro", "Xã Yang Trung", "Xã Yang Nam"], "Xã Kông Chro"),
    ("Huyện Kông Chro", ["Xã Đăk Tơ Pang", "Xã Kông Yang", "Xã Ya Ma"], "Xã Ya Ma"),
    ("Huyện Kông Chro", ["Xã An Trung", "Xã Chư Krey"], "Xã Chư Krey"),
    ("Huyện Kông Chro", ["Xã Đăk Kơ Ning", "Xã SRó"], "Xã SRó"),
    ("Huyện Kông Chro", ["Xã Đăk Pling", "Xã Đăk Song"], "Xã Đăk Song"),
    ("Huyện Kông Chro", ["Xã Đăk Pơ Pho", "Xã Chơ GLong"], "Xã Chơ Long"),

    # Thị xã Ayun Pa (Gia Lai) - items 74-75
    ("Thị xã Ayun Pa", ["Xã Chư Băh", "Xã Ia Rbol"], "Xã Ia Rbol"),
    ("Thị xã Ayun Pa", ["Xã Ia Sao", "Xã Ia Rtô"], "Xã Ia Sao"),

    # Huyện Phú Thiện (Gia Lai) - items 76-78
    ("Huyện Phú Thiện", ["Thị trấn Phú Thiện", "Xã Ia Sol", "Xã Ia Piar", "Xã Ia Yeng"], "Xã Phú Thiện"),
    ("Huyện Phú Thiện", ["Xã Ayun Hạ", "Xã Ia Ake", "Xã Chư A Thai"], "Xã Chư A Thai"),
    ("Huyện Phú Thiện", ["Xã Chrôh Pơnan", "Xã Ia Peng", "Xã Ia Hiao"], "Xã Ia Hiao"),

    # Huyện Ia Pa (Gia Lai) - items 79-81
    ("Huyện Ia Pa", ["Xã Chư Răng", "Xã Pờ Tó"], "Xã Pờ Tó"),
    ("Huyện Ia Pa", ["Xã Ia Mrơn", "Xã Kim Tân", "Xã Ia Trôk"], "Xã Ia Pa"),
    ("Huyện Ia Pa", ["Xã Chư Mố", "Xã Ia Broăi", "Xã Ia Kdăm", "Xã Ia Tul"], "Xã Ia Tul"),

    # Huyện Krông Pa (Gia Lai) - items 82-85
    ("Huyện Krông Pa", ["Thị trấn Phú Túc", "Xã Phú Cần", "Xã Chư Ngọc", "Xã Ia Mlah", "Xã Đất Bằng"], "Xã Phú Túc"),
    ("Huyện Krông Pa", ["Xã Ia Rmok", "Xã Krông Năng", "Xã Ia Dreh"], "Xã Ia Dreh"),
    ("Huyện Krông Pa", ["Xã Chư RCăm", "Xã Chư Gu", "Xã Ia Rsai"], "Xã Ia Rsai"),
    ("Huyện Krông Pa", ["Xã Ia Rsươm", "Xã Chư Drăng", "Xã Uar"], "Xã Uar"),

    # Huyện Đak Đoa (Gia Lai) - items 86-90
    ("Huyện Đak Đoa", ["Thị trấn Đak Đoa", "Xã Tân Bình", "Xã Glar"], "Xã Đak Đoa"),
    ("Huyện Đak Đoa", ["Xã Đak Krong", "Xã Hneng", "Xã Nam Yang", "Xã Kon Gang"], "Xã Kon Gang"),
    ("Huyện Đak Đoa", ["Xã Ia Băng", "Xã Adơk", "Xã Ia Pết"], "Xã Ia Băng"),
    ("Huyện Đak Đoa", ["Xã Hnol", "Xã Trang", "Xã KDang"], "Xã KDang"),
    ("Huyện Đak Đoa", ["Xã Hà Đông", "Xã Đak Sơmei"], "Xã Đak Sơmei"),

    # Huyện Mang Yang (Gia Lai) - items 91-95
    ("Huyện Mang Yang", ["Thị trấn Kon Dơng", "Xã Đăk Yă", "Xã Đak Djrăng", "Xã Hải Yang"], "Xã Mang Yang"),
    ("Huyện Mang Yang", ["Xã Đê Ar", "Xã Kon Thụp", "Xã Lơ Pang"], "Xã Lơ Pang"),
    ("Huyện Mang Yang", ["Xã Đak Trôi", "Xã Kon Chiêng"], "Xã Kon Chiêng"),
    ("Huyện Mang Yang", ["Xã Đak Ta Ley", "Xã Hra"], "Xã Hra"),
    ("Huyện Mang Yang", ["Xã Đak Jơ Ta", "Xã Ayun"], "Xã Ayun"),

    # Huyện Ia Grai (Gia Lai) - items 96-98
    ("Huyện Ia Grai", ["Thị trấn Ia Kha", "Xã Ia Bă", "Xã Ia Grăng"], "Xã Ia Grai"),
    ("Huyện Ia Grai", ["Xã Ia Tô", "Xã Ia Khai", "Xã Ia Krái"], "Xã Ia Krái"),
    ("Huyện Ia Grai", ["Xã Ia Sao", "Xã Ia Yok", "Xã Ia Dêr", "Xã Ia Hrung"], "Xã Ia Hrung"),

    # Huyện Đức Cơ (Gia Lai) - items 99-101
    ("Huyện Đức Cơ", ["Thị trấn Chư Ty", "Xã Ia Kriêng"], "Xã Đức Cơ"),
    ("Huyện Đức Cơ", ["Xã Ia Kla", "Xã Ia Dơk"], "Xã Ia Dơk"),
    ("Huyện Đức Cơ", ["Xã Ia Lang", "Xã Ia Din", "Xã Ia Krêl"], "Xã Ia Krêl"),

    # Thành phố Quy Nhơn (Bình Định) - items 102-106
    ("Thành phố Quy Nhơn", ["Phường Đống Đa", "Phường Hải Cảng", "Phường Thị Nại", "Phường Trần Phú"], "Phường Quy Nhơn"),
    ("Thành phố Quy Nhơn", ["Phường Nhơn Bình", "Xã Nhơn Hội", "Xã Nhơn Lý", "Xã Nhơn Hải"], "Phường Quy Nhơn Đông"),
    ("Thành phố Quy Nhơn", ["Phường Bùi Thị Xuân", "Xã Phước Mỹ"], "Phường Quy Nhơn Tây"),
    ("Thành phố Quy Nhơn", ["Phường Ngô Mây", "Phường Nguyễn Văn Cừ", "Phường Quang Trung", "Phường Ghềnh Ráng"], "Phường Quy Nhơn Nam"),
    ("Thành phố Quy Nhơn", ["Phường Trần Quang Diệu", "Phường Nhơn Phú"], "Phường Quy Nhơn Bắc"),

    # Thị xã An Nhơn (Bình Định) - items 107-111
    ("Thị xã An Nhơn", ["Phường Bình Định", "Xã Nhơn Khánh", "Xã Nhơn Phúc"], "Phường Bình Định"),
    ("Thị xã An Nhơn", ["Phường Đập Đá", "Xã Nhơn Mỹ", "Xã Nhơn Hậu"], "Phường An Nhơn"),
    ("Thị xã An Nhơn", ["Phường Nhơn Hưng", "Xã Nhơn An"], "Phường An Nhơn Đông"),
    ("Thị xã An Nhơn", ["Phường Nhơn Hòa", "Xã Nhơn Thọ"], "Phường An Nhơn Nam"),
    ("Thị xã An Nhơn", ["Phường Nhơn Thành", "Xã Nhơn Phong", "Xã Nhơn Hạnh"], "Phường An Nhơn Bắc"),

    # Thị xã Hoài Nhơn (Bình Định) - items 112-118
    ("Thị xã Hoài Nhơn", ["Phường Hoài Đức", "Phường Bồng Sơn"], "Phường Bồng Sơn"),
    ("Thị xã Hoài Nhơn", ["Phường Hoài Thanh", "Phường Tam Quan Nam", "Phường Hoài Thanh Tây"], "Phường Hoài Nhơn"),
    ("Thị xã Hoài Nhơn", ["Phường Tam Quan", "Xã Hoài Châu"], "Phường Tam Quan"),
    ("Thị xã Hoài Nhơn", ["Phường Hoài Hương", "Xã Hoài Hải", "Xã Hoài Mỹ"], "Phường Hoài Nhơn Đông"),
    ("Thị xã Hoài Nhơn", ["Phường Hoài Hảo", "Xã Hoài Phú"], "Phường Hoài Nhơn Tây"),
    ("Thị xã Hoài Nhơn", ["Phường Hoài Tân", "Phường Hoài Xuân"], "Phường Hoài Nhơn Nam"),
    ("Thị xã Hoài Nhơn", ["Phường Tam Quan Bắc", "Xã Hoài Sơn", "Xã Hoài Châu Bắc"], "Phường Hoài Nhơn Bắc"),

    # Thành phố Pleiku (Gia Lai) - items 119-123
    ("Thành phố Pleiku", ["Phường Tây Sơn", "Phường Hội Thương", "Phường Hoa Lư", "Phường Phù Đổng", "Xã Trà Đa"], "Phường Pleiku"),
    ("Thành phố Pleiku", ["Phường Trà Bá", "Phường Chi Lăng", "Phường Hội Phú"], "Phường Hội Phú"),
    ("Thành phố Pleiku", ["Phường Đống Đa", "Phường Yên Thế", "Phường Thống Nhất"], "Phường Thống Nhất"),
    ("Thành phố Pleiku", ["Phường Yên Đỗ", "Phường Ia Kring", "Phường Diên Hồng", "Xã Diên Phú"], "Phường Diên Hồng"),
    ("Thành phố Pleiku", ["Phường Thắng Lợi", "Xã Chư Á", "Xã An Phú"], "Phường An Phú"),

    # Thị xã An Khê (Gia Lai) - items 124-125
    ("Thị xã An Khê", ["Phường Ngô Mây", "Phường Tây Sơn", "Phường An Phú", "Phường An Phước", "Phường An Tân", "Xã Thành An"], "Phường An Khê"),
    ("Thị xã An Khê", ["Phường An Bình", "Xã Tân An", "Xã Cư An"], "Phường An Bình"),

    # Thị xã Ayun Pa (Gia Lai) - item 126
    ("Thị xã Ayun Pa", ["Phường Đoàn Kết", "Phường Sông Bờ", "Phường Cheo Reo", "Phường Hòa Bình"], "Phường Ayun Pa"),
]

# Hà Nội restructuring data - simplified version focusing on main mergers
hanoi_restructuring_data = [
    # Quận Hoàn Kiếm - items 1-2
    ("Quận Hoàn Kiếm", ["Phường Hàng Bạc", "Phường Hàng Bồ", "Phường Hàng Buồm", "Phường Hàng Đào", "Phường Hàng Gai", "Phường Hàng Mã", "Phường Lý Thái Tổ", "Phường Cửa Đông", "Phường Cửa Nam", "Phường Điện Biên", "Phường Đồng Xuân", "Phường Hàng Bông", "Phường Hàng Trống", "Phường Tràng Tiền"], "Phường Hoàn Kiếm"),
    ("Quận Hoàn Kiếm", ["Phường Hàng Bài", "Phường Phan Chu Trinh", "Phường Trần Hưng Đạo", "Phường Cửa Nam", "Phường Nguyễn Du", "Phường Phạm Đình Hổ", "Phường Hàng Bông", "Phường Hàng Trống", "Phường Tràng Tiền"], "Phường Cửa Nam"),

    # Quận Ba Đình - items 3-5
    ("Quận Ba Đình", ["Phường Quán Thánh", "Phường Trúc Bạch", "Phường Cửa Nam", "Phường Điện Biên", "Phường Đội Cấn", "Phường Kim Mã", "Phường Ngọc Hà", "Phường Thụy Khuê", "Phường Cửa Đông", "Phường Đồng Xuân"], "Phường Ba Đình"),
    ("Quận Ba Đình", ["Phường Vĩnh Phúc", "Phường Liễu Giai", "Phường Cống Vị", "Phường Kim Mã", "Phường Ngọc Khánh", "Phường Nghĩa Đô", "Phường Đội Cấn", "Phường Ngọc Hà"], "Phường Ngọc Hà"),
    ("Quận Ba Đình", ["Phường Giảng Võ", "Phường Cát Linh", "Phường Láng Hạ", "Phường Ngọc Khánh", "Phường Thành Công", "Phường Cống Vị", "Phường Kim Mã"], "Phường Giảng Võ"),

    # Quận Hai Bà Trưng - items 6-8
    ("Quận Hai Bà Trưng", ["Phường Đồng Nhân", "Phường Phố Huế", "Phường Bạch Đằng", "Phường Lê Đại Hành", "Phường Nguyễn Du", "Phường Thanh Nhàn", "Phường Phạm Đình Hổ"], "Phường Hai Bà Trưng"),
    ("Quận Hai Bà Trưng", ["Phường Mai Động", "Phường Thanh Lương", "Phường Vĩnh Hưng", "Phường Vĩnh Tuy"], "Phường Vĩnh Tuy"),
    ("Quận Hai Bà Trưng", ["Phường Bạch Mai", "Phường Bách Khoa", "Phường Quỳnh Mai", "Phường Minh Khai", "Phường Đồng Tâm", "Phường Lê Đại Hành", "Phường Phương Mai", "Phường Trương Định", "Phường Thanh Nhàn"], "Phường Bạch Mai"),

    # Quận Đống Đa - items 9-13
    ("Quận Đống Đa", ["Phường Thịnh Quang", "Phường Quang Trung", "Phường Láng Hạ", "Phường Nam Đồng", "Phường Ô Chợ Dừa", "Phường Trung Liệt"], "Phường Đống Đa"),
    ("Quận Đống Đa", ["Phường Kim Liên", "Phường Khương Thượng", "Phường Nam Đồng", "Phường Phương Liên - Trung Tự", "Phường Trung Liệt", "Phường Phương Mai", "Phường Quang Trung"], "Phường Kim Liên"),
    ("Quận Đống Đa", ["Phường Khâm Thiên", "Phường Thổ Quan", "Phường Văn Chương", "Phường Điện Biên", "Phường Hàng Bột", "Phường Văn Miếu - Quốc Tử Giám", "Phường Cửa Nam", "Phường Lê Đại Hành", "Phường Nam Đồng", "Phường Nguyễn Du", "Phường Phương Liên - Trung Tự"], "Phường Văn Miếu - Quốc Tử Giám"),
    ("Quận Đống Đa", ["Phường Láng Thượng", "Phường Láng Hạ", "Phường Ngọc Khánh"], "Phường Láng"),
    ("Quận Đống Đa", ["Phường Cát Linh", "Phường Điện Biên", "Phường Thành Công", "Phường Ô Chợ Dừa", "Phường Trung Liệt", "Phường Hàng Bột", "Phường Văn Miếu - Quốc Tử Giám"], "Phường Ô Chợ Dừa"),

    # Quận Hoàng Mai - items 14-21
    ("Quận Hoàng Mai", ["Phường Chương Dương", "Phường Phúc Tân", "Phường Phúc Xá", "Phường Nhật Tân", "Phường Phú Thượng", "Phường Quảng An", "Phường Thanh Lương", "Phường Tứ Liên", "Phường Yên Phụ", "Phường Bồ Đề", "Phường Ngọc Thụy", "Phường Bạch Đằng"], "Phường Hồng Hà"),
    ("Quận Hoàng Mai", ["Phường Lĩnh Nam", "Phường Thanh Trì", "Phường Trần Phú", "Phường Yên Sở", "Phường Thanh Lương"], "Phường Lĩnh Nam"),
    ("Quận Hoàng Mai", ["Phường Giáp Bát", "Phường Hoàng Liệt", "Phường Hoàng Văn Thụ", "Phường Lĩnh Nam", "Phường Tân Mai", "Phường Thịnh Liệt", "Phường Tương Mai", "Phường Trần Phú", "Phường Vĩnh Hưng", "Phường Yên Sở"], "Phường Hoàng Mai"),
    ("Quận Hoàng Mai", ["Phường Vĩnh Hưng", "Phường Lĩnh Nam", "Phường Thanh Trì", "Phường Vĩnh Tuy"], "Phường Vĩnh Hưng"),
    ("Quận Hoàng Mai", ["Phường Giáp Bát", "Phường Phương Liệt", "Phường Mai Động", "Phường Minh Khai", "Phường Đồng Tâm", "Phường Trương Định", "Phường Hoàng Văn Thụ", "Phường Tân Mai", "Phường Tương Mai", "Phường Vĩnh Hưng"], "Phường Tương Mai"),
    ("Quận Hoàng Mai", ["Phường Định Công", "Phường Hoàng Liệt", "Phường Thịnh Liệt", "Xã Tân Triều", "Xã Thanh Liệt", "Phường Đại Kim", "Phường Giáp Bát"], "Phường Định Công"),
    ("Quận Hoàng Mai", ["Phường Hoàng Liệt", "Thị trấn Văn Điển", "Xã Tam Hiệp", "Xã Thanh Liệt", "Phường Đại Kim"], "Phường Hoàng Liệt"),
    ("Quận Hoàng Mai", ["Phường Thịnh Liệt", "Phường Yên Sở", "Xã Tứ Hiệp", "Phường Hoàng Liệt", "Phường Trần Phú"], "Phường Yên Sở"),

    # Quận Thanh Xuân - items 22-24
    ("Quận Thanh Xuân", ["Phường Nhân Chính", "Phường Thanh Xuân Bắc", "Phường Thanh Xuân Trung", "Phường Thượng Đình", "Phường Trung Hoà", "Phường Trung Văn"], "Phường Thanh Xuân"),
    ("Quận Thanh Xuân", ["Phường Hạ Đình", "Phường Khương Đình", "Phường Khương Trung", "Phường Đại Kim", "Xã Tân Triều", "Phường Thanh Xuân Trung", "Phường Thượng Đình"], "Phường Khương Đình"),
    ("Quận Thanh Xuân", ["Phường Khương Mai", "Phường Thịnh Liệt", "Phường Phương Liệt", "Phường Định Công", "Phường Khương Đình", "Phường Khương Trung"], "Phường Phương Liệt"),

    # Quận Cầu Giấy - items 25-27
    ("Quận Cầu Giấy", ["Phường Dịch Vọng", "Phường Dịch Vọng Hậu", "Phường Quan Hoa", "Phường Mỹ Đình 1", "Phường Mỹ Đình 2", "Phường Yên Hòa"], "Phường Cầu Giấy"),
    ("Quận Cầu Giấy", ["Phường Nghĩa Tân", "Phường Cổ Nhuế 1", "Phường Mai Dịch", "Phường Nghĩa Đô", "Phường Xuân La", "Phường Xuân Tảo", "Phường Dịch Vọng", "Phường Dịch Vọng Hậu", "Phường Quan Hoa"], "Phường Nghĩa Đô"),
    ("Quận Cầu Giấy", ["Phường Mễ Trì", "Phường Nhân Chính", "Phường Trung Hòa", "Phường Yên Hòa"], "Phường Yên Hòa"),

    # Quận Tây Hồ - items 28-29
    ("Quận Tây Hồ", ["Phường Bưởi", "Phường Phú Thượng", "Phường Xuân La", "Phường Nhật Tân", "Phường Quảng An", "Phường Tứ Liên", "Phường Yên Phụ", "Phường Nghĩa Đô", "Phường Thụy Khuê"], "Phường Tây Hồ"),
    ("Quận Tây Hồ", ["Phường Đông Ngạc", "Phường Xuân La", "Phường Xuân Đỉnh", "Phường Xuân Tảo", "Phường Phú Thượng"], "Phường Phú Thượng"),

    # Quận Bắc Từ Liêm - items 30-36
    ("Quận Bắc Từ Liêm", ["Phường Minh Khai", "Phường Tây Tựu", "Xã Kim Chung"], "Phường Tây Tựu"),
    ("Quận Bắc Từ Liêm", ["Phường Phú Diễn", "Phường Cổ Nhuế 1", "Phường Mai Dịch", "Phường Phúc Diễn"], "Phường Phú Diễn"),
    ("Quận Bắc Từ Liêm", ["Phường Xuân Đỉnh", "Phường Cổ Nhuế 1", "Phường Xuân La", "Phường Xuân Tảo"], "Phường Xuân Đỉnh"),
    ("Quận Bắc Từ Liêm", ["Phường Đức Thắng", "Phường Cổ Nhuế 2", "Phường Thụy Phương", "Phường Minh Khai", "Phường Đông Ngạc", "Phường Xuân Đỉnh"], "Phường Đông Ngạc"),
    ("Quận Bắc Từ Liêm", ["Phường Liên Mạc", "Phường Thượng Cát", "Phường Minh Khai", "Phường Tây Tựu", "Phường Cổ Nhuế 2", "Phường Thụy Phương"], "Phường Thượng Cát"),
    ("Quận Bắc Từ Liêm", ["Phường Cầu Diễn", "Phường Mễ Trì", "Phường Phú Đô", "Phường Mai Dịch", "Phường Mỹ Đình 1", "Phường Mỹ Đình 2"], "Phường Từ Liêm"),
    ("Quận Bắc Từ Liêm", ["Phường Phương Canh", "Phường Xuân Phương", "Phường Đại Mỗ", "Phường Tây Mỗ", "Xã Vân Canh", "Phường Minh Khai", "Phường Phúc Diễn"], "Phường Xuân Phương"),

    # Quận Nam Từ Liêm - items 37-38
    ("Quận Nam Từ Liêm", ["Phường Đại Mỗ", "Phường Dương Nội", "Xã An Khánh", "Phường Tây Mỗ"], "Phường Tây Mỗ"),
    ("Quận Nam Từ Liêm", ["Phường Dương Nội", "Phường Đại Mỗ", "Phường Mộ Lao", "Phường Mễ Trì", "Phường Nhân Chính", "Phường Trung Hòa", "Phường Phú Đô", "Phường Trung Văn"], "Phường Đại Mỗ"),

    # Quận Long Biên - items 39-42
    ("Quận Long Biên", ["Phường Cự Khối", "Phường Phúc Đồng", "Phường Thạch Bàn", "Xã Bát Tràng", "Phường Long Biên", "Phường Bồ Đề", "Phường Gia Thụy"], "Phường Long Biên"),
    ("Quận Long Biên", ["Phường Ngọc Lâm", "Phường Đức Giang", "Phường Gia Thụy", "Phường Thượng Thanh", "Phường Phúc Đồng", "Phường Ngọc Thụy", "Phường Bồ Đề", "Phường Long Biên"], "Phường Bồ Đề"),
    ("Quận Long Biên", ["Phường Giang Biên", "Phường Phúc Đồng", "Phường Việt Hưng", "Phường Phúc Lợi", "Phường Gia Thụy", "Phường Đức Giang", "Phường Thượng Thanh"], "Phường Việt Hưng"),
    ("Quận Long Biên", ["Phường Thạch Bàn", "Xã Cổ Bi", "Phường Giang Biên", "Phường Việt Hưng", "Phường Phúc Lợi", "Phường Phúc Đồng"], "Phường Phúc Lợi"),

    # Quận Hà Đông - items 43-49
    ("Quận Hà Đông", ["Phường Phúc La", "Phường Vạn Phúc", "Phường Quang Trung", "Phường Đại Mỗ", "Phường Hà Cầu", "Phường La Khê", "Phường Văn Quán", "Xã Tân Triều", "Phường Mộ Lao"], "Phường Hà Đông"),
    ("Quận Hà Đông", ["Phường Dương Nội", "Phường Phú La", "Phường Yên Nghĩa", "Xã La Phù", "Phường Đại Mỗ", "Phường La Khê"], "Phường Dương Nội"),
    ("Quận Hà Đông", ["Phường Đồng Mai", "Phường Yên Nghĩa"], "Phường Yên Nghĩa"),
    ("Quận Hà Đông", ["Phường Phú Lãm", "Phường Kiến Hưng", "Phường Phú Lương", "Xã Cự Khê", "Xã Hữu Hòa"], "Phường Phú Lương"),
    ("Quận Hà Đông", ["Phường Kiến Hưng", "Phường Phú Lương", "Phường Quang Trung", "Phường Hà Cầu", "Phường Phú La"], "Phường Kiến Hưng"),
    ("Quận Hà Đông", ["Xã Tả Thanh Oai", "Phường Đại Kim", "Phường Thanh Xuân Bắc", "Phường Hạ Đình", "Phường Văn Quán", "Xã Thanh Liệt", "Xã Tân Triều"], "Phường Thanh Liệt"),
    ("Quận Hà Đông", ["Phường Biên Giang", "Thị trấn Chúc Sơn", "Xã Đại Yên", "Xã Ngọc Hòa", "Xã Phụng Châu", "Xã Tiên Phương", "Xã Thuỵ Hương", "Phường Đồng Mai"], "Phường Chương Mỹ"),

    # Thị xã Sơn Tây - items 50-51
    ("Thị xã Sơn Tây", ["Phường Ngô Quyền", "Phường Phú Thịnh", "Phường Viên Sơn", "Xã Đường Lâm", "Phường Trung Hưng", "Phường Sơn Lộc", "Xã Thanh Mỹ"], "Phường Sơn Tây"),
    ("Thị xã Sơn Tây", ["Phường Xuân Khanh", "Phường Trung Sơn Trầm", "Xã Xuân Sơn", "Phường Trung Hưng", "Phường Sơn Lộc", "Xã Thanh Mỹ"], "Phường Tùng Thiện"),

    # Huyện Thanh Trì - items 52-55
    ("Huyện Thanh Trì", ["Thị trấn Văn Điển", "Xã Ngũ Hiệp", "Xã Vĩnh Quỳnh", "Xã Yên Mỹ", "Xã Duyên Hà", "Xã Tứ Hiệp", "Phường Yên Sở"], "Xã Thanh Trì"),
    ("Huyện Thanh Trì", ["Xã Tam Hiệp", "Xã Hữu Hòa", "Phường Kiến Hưng", "Thị trấn Văn Điển", "Xã Tả Thanh Oai", "Xã Vĩnh Quỳnh"], "Xã Đại Thanh"),
    ("Huyện Thanh Trì", ["Xã Vạn Phúc", "Xã Liên Ninh", "Xã Ninh Sở", "Xã Đông Mỹ", "Xã Duyên Thái", "Xã Ngũ Hiệp", "Xã Yên Mỹ", "Xã Duyên Hà"], "Xã Nam Phù"),
    ("Huyện Thanh Trì", ["Xã Ngọc Hồi", "Xã Duyên Thái", "Xã Đại Áng", "Xã Khánh Hà", "Xã Liên Ninh"], "Xã Ngọc Hồi"),

    # Huyện Thường Tín - items 56-59
    ("Huyện Thường Tín", ["Xã Tân Minh", "Xã Dũng Tiến", "Xã Quất Động", "Xã Nghiêm Xuyên", "Xã Nguyễn Trãi"], "Xã Thượng Phúc"),
    ("Huyện Thường Tín", ["Thị trấn Thường Tín", "Xã Tiền Phong", "Xã Hiền Giang", "Xã Hòa Bình", "Xã Nhị Khê", "Xã Văn Bình", "Xã Văn Phú", "Xã Đại Áng", "Xã Khánh Hà"], "Xã Thường Tín"),
    ("Huyện Thường Tín", ["Xã Chương Dương", "Xã Lê Lợi", "Xã Thắng Lợi", "Xã Tự Nhiên", "Xã Tô Hiệu", "Xã Vạn Nhất"], "Xã Chương Dương"),
    ("Huyện Thường Tín", ["Xã Hà Hồi", "Xã Hồng Vân", "Xã Liên Phương", "Xã Vân Tảo", "Xã Duyên Thái", "Xã Ninh Sở", "Xã Đông Mỹ"], "Xã Hồng Vân"),

    # Huyện Phú Xuyên - items 60-63
    ("Huyện Phú Xuyên", ["Thị trấn Phú Minh", "Thị trấn Phú Xuyên", "Xã Hồng Thái", "Xã Minh Cường", "Xã Nam Phong", "Xã Nam Tiến", "Xã Quang Hà", "Xã Văn Tự", "Xã Tô Hiệu", "Xã Vạn Nhất"], "Xã Phú Xuyên"),
    ("Huyện Phú Xuyên", ["Xã Hoàng Long", "Xã Hồng Minh", "Xã Phú Túc", "Xã Văn Hoàng", "Xã Phượng Dực"], "Xã Phượng Dực"),
    ("Huyện Phú Xuyên", ["Xã Tân Dân", "Xã Châu Can", "Xã Phú Yên", "Xã Vân Từ", "Xã Chuyên Mỹ"], "Xã Chuyên Mỹ"),
    ("Huyện Phú Xuyên", ["Xã Bạch Hạ", "Xã Khai Thái", "Xã Minh Tân", "Xã Phúc Tiến", "Xã Quang Lãng", "Xã Tri Thủy", "Xã Đại Xuyên"], "Xã Đại Xuyên"),

    # Huyện Thanh Oai - items 64-67
    ("Huyện Thanh Oai", ["Thị trấn Kim Bài", "Xã Đỗ Động", "Xã Kim An", "Xã Phương Trung", "Xã Thanh Mai", "Xã Kim Thư"], "Xã Thanh Oai"),
    ("Huyện Thanh Oai", ["Xã Bích Hòa", "Xã Bình Minh", "Xã Cao Viên", "Xã Thanh Cao", "Xã Lam Điền", "Xã Cự Khê", "Phường Phú Lương"], "Xã Bình Minh"),
    ("Huyện Thanh Oai", ["Xã Mỹ Hưng", "Xã Thanh Thùy", "Xã Thanh Văn", "Xã Tam Hưng"], "Xã Tam Hưng"),
    ("Huyện Thanh Oai", ["Xã Cao Xuân Dương", "Xã Hồng Dương", "Xã Liên Châu", "Xã Tân Ước", "Xã Dân Hòa"], "Xã Dân Hòa"),

    # Huyện Ứng Hòa - items 68-71
    ("Huyện Ứng Hòa", ["Thị trấn Vân Đình", "Xã Cao Sơn Tiến", "Xã Phương Tú", "Xã Tảo Dương Văn"], "Xã Vân Đình"),
    ("Huyện Ứng Hòa", ["Xã Hoa Viên", "Xã Liên Bạt", "Xã Quảng Phú Cầu", "Xã Trường Thịnh"], "Xã Ứng Thiên"),
    ("Huyện Ứng Hòa", ["Xã Hòa Phú", "Xã Thái Hòa", "Xã Bình Lưu Quang", "Xã Phù Lưu"], "Xã Hòa Xá"),
    ("Huyện Ứng Hòa", ["Xã Đại Cường", "Xã Đại Hùng", "Xã Đông Lỗ", "Xã Đồng Tân", "Xã Kim Đường", "Xã Minh Đức", "Xã Trầm Lộng", "Xã Trung Tú"], "Xã Ứng Hòa"),

    # Huyện Mỹ Đức - items 72-75
    ("Huyện Mỹ Đức", ["Thị trấn Đại Nghĩa", "Xã An Phú", "Xã Đại Hưng", "Xã Hợp Thanh", "Xã Phù Lưu Tế"], "Xã Mỹ Đức"),
    ("Huyện Mỹ Đức", ["Xã Phùng Xá", "Xã An Mỹ", "Xã Hợp Tiến", "Xã Lê Thanh", "Xã Xuy Xá", "Xã Hồng Sơn"], "Xã Hồng Sơn"),
    ("Huyện Mỹ Đức", ["Xã Mỹ Xuyên", "Xã Phúc Lâm", "Xã Thượng Lâm", "Xã Tuy Lai", "Xã Đồng Tâm"], "Xã Phúc Sơn"),
    ("Huyện Mỹ Đức", ["Xã An Tiến", "Xã Hùng Tiến", "Xã Vạn Tín", "Xã Hương Sơn"], "Xã Hương Sơn"),

    # Huyện Chương Mỹ - items 76-80
    ("Huyện Chương Mỹ", ["Xã Đông Phương Yên", "Xã Đông Sơn", "Xã Thanh Bình", "Xã Trung Hòa", "Xã Trường Yên", "Xã Phú Nghĩa"], "Xã Phú Nghĩa"),
    ("Huyện Chương Mỹ", ["Thị trấn Xuân Mai", "Xã Nam Phương Tiến", "Xã Thủy Xuân Tiên", "Xã Tân Tiến"], "Xã Xuân Mai"),
    ("Huyện Chương Mỹ", ["Xã Hoàng Văn Thụ", "Xã Hữu Văn", "Xã Mỹ Lương", "Xã Trần Phú", "Xã Đồng Tâm", "Xã Tân Tiến"], "Xã Trần Phú"),
    ("Huyện Chương Mỹ", ["Xã Hòa Phú", "Xã Đồng Lạc", "Xã Hồng Phú", "Xã Thượng Vực", "Xã Văn Võ", "Xã Kim Thư"], "Xã Hòa Phú"),
    ("Huyện Chương Mỹ", ["Xã Hoàng Diệu", "Xã Hợp Đồng", "Xã Quảng Bị", "Xã Tốt Động", "Xã Lam Điền"], "Xã Quảng Bị"),

    # Huyện Ba Vì - items 81-87
    ("Huyện Ba Vì", ["Xã Minh Châu", "Thị trấn Tây Đằng", "Xã Chu Minh"], "Xã Minh Châu"),
    ("Huyện Ba Vì", ["Xã Cam Thượng", "Xã Đông Quang", "Xã Tiên Phong", "Xã Thụy An", "Thị trấn Tây Đằng", "Xã Chu Minh"], "Xã Quảng Oai"),
    ("Huyện Ba Vì", ["Xã Thái Hòa", "Xã Phú Sơn", "Xã Đồng Thái", "Xã Phú Châu", "Xã Vật Lại"], "Xã Vật Lại"),
    ("Huyện Ba Vì", ["Xã Phú Cường", "Xã Cổ Đô", "Xã Phong Vân", "Xã Phú Hồng", "Xã Phú Đông", "Xã Vạn Thắng"], "Xã Cổ Đô"),
    ("Huyện Ba Vì", ["Xã Thuần Mỹ", "Xã Tòng Bạt", "Xã Sơn Đà", "Xã Cẩm Lĩnh", "Xã Minh Quang"], "Xã Bất Bạt"),
    ("Huyện Ba Vì", ["Xã Ba Trại", "Xã Tản Lĩnh", "Xã Thụy An", "Xã Cẩm Lĩnh"], "Xã Suối Hai"),
    ("Huyện Ba Vì", ["Xã Ba Vì", "Xã Khánh Thượng", "Xã Minh Quang"], "Xã Ba Vì"),

    # Thị xã Sơn Tây/Huyện Thạch Thất - items 88-89
    ("Huyện Thạch Thất", ["Xã Vân Hòa", "Xã Yên Bài", "Xã Thạch Hòa"], "Xã Yên Bài"),
    ("Huyện Thạch Thất", ["Xã Kim Sơn", "Xã Sơn Đông", "Xã Cổ Đông"], "Xã Đoài Phương"),

    # Huyện Phúc Thọ - items 90-92
    ("Huyện Phúc Thọ", ["Thị trấn Phúc Thọ", "Xã Long Thượng", "Xã Phúc Hòa", "Xã Phụng Thượng", "Xã Tích Lộc", "Xã Trạch Mỹ Lộc"], "Xã Phúc Thọ"),
    ("Huyện Phúc Thọ", ["Xã Nam Hà", "Xã Sen Phương", "Xã Vân Phúc", "Xã Võng Xuyên", "Xã Xuân Đình"], "Xã Phúc Lộc"),
    ("Huyện Phúc Thọ", ["Xã Tam Hiệp", "Xã Hiệp Thuận", "Xã Liên Hiệp", "Xã Ngọc Tảo", "Xã Tam Thuấn", "Xã Thanh Đa", "Xã Hát Môn"], "Xã Hát Môn"),

    # Huyện Thạch Thất - items 93-101
    ("Huyện Thạch Thất", ["Thị trấn Liên Quan", "Xã Cẩm Yên", "Xã Đại Đồng", "Xã Kim Quan", "Xã Lại Thượng", "Xã Phú Kim"], "Xã Thạch Thất"),
    ("Huyện Thạch Thất", ["Xã Cần Kiệm", "Xã Đồng Trúc", "Xã Bình Yên", "Xã Hạ Bằng", "Xã Tân Xã", "Xã Phú Cát"], "Xã Hạ Bằng"),
    ("Huyện Thạch Thất", ["Xã Phùng Xá", "Xã Hương Ngải", "Xã Lam Sơn", "Xã Thạch Xá", "Xã Quang Trung", "Thị trấn Quốc Oai", "Xã Ngọc Liệp", "Xã Phượng Sơn"], "Xã Tây Phương"),
    ("Huyện Thạch Thất", ["Xã Tiến Xuân", "Xã Thạch Hòa", "Xã Cổ Đông", "Xã Bình Yên", "Xã Hạ Bằng", "Xã Tân Xã"], "Xã Hòa Lạc"),
    ("Huyện Thạch Thất", ["Xã Đông Xuân", "Xã Yên Bình", "Xã Yên Trung", "Xã Tiến Xuân", "Xã Thạch Hòa"], "Xã Yên Xuân"),
    ("Huyện Quốc Oai", ["Xã Thạch Thán", "Xã Sài Sơn", "Xã Ngọc Mỹ", "Thị trấn Quốc Oai", "Xã Phượng Sơn"], "Xã Quốc Oai"),
    ("Huyện Quốc Oai", ["Xã Cộng Hoà", "Xã Đồng Quang", "Xã Hưng Đạo"], "Xã Hưng Đạo"),
    ("Huyện Quốc Oai", ["Xã Cấn Hữu", "Xã Liệp Nghĩa", "Xã Tuyết Nghĩa", "Xã Ngọc Liệp", "Xã Quang Trung", "Xã Ngọc Mỹ"], "Xã Kiều Phú"),
    ("Huyện Quốc Oai", ["Xã Đông Yên", "Xã Hoà Thạch", "Xã Phú Mãn", "Xã Phú Cát"], "Xã Phú Cát"),

    # Huyện Hoài Đức - items 102-105
    ("Huyện Hoài Đức", ["Thị trấn Trạm Trôi", "Xã Di Trạch", "Xã Đức Giang", "Xã Đức Thượng", "Phường Tây Tựu", "Xã Tân Lập", "Xã Kim Chung"], "Xã Hoài Đức"),
    ("Huyện Hoài Đức", ["Xã Cát Quế", "Xã Dương Liễu", "Xã Đắc Sở", "Xã Minh Khai", "Xã Yên Sở"], "Xã Dương Hòa"),
    ("Huyện Hoài Đức", ["Xã Lại Yên", "Xã Sơn Đồng", "Xã Tiền Yên", "Xã An Khánh", "Xã Song Phương", "Xã Vân Côn", "Xã An Thượng", "Xã Vân Canh"], "Xã Sơn Đồng"),
    ("Huyện Hoài Đức", ["Xã Đông La", "Phường Dương Nội", "Xã An Khánh", "Xã La Phù", "Xã Song Phương", "Xã Vân Côn", "Xã An Thượng"], "Xã An Khánh"),

    # Huyện Đan Phượng - items 106-108
    ("Huyện Đan Phượng", ["Thị trấn Phùng", "Xã Đồng Tháp", "Xã Song Phượng", "Xã Thượng Mỗ", "Xã Đan Phượng"], "Xã Đan Phượng"),
    ("Huyện Đan Phượng", ["Xã Hạ Mỗ", "Xã Tân Hội", "Xã Liên Hà", "Xã Hồng Hà", "Xã Liên Hồng", "Xã Liên Trung", "Xã Văn Khê", "Phường Tây Tựu", "Xã Tân Lập"], "Xã Ô Diên"),
    ("Huyện Đan Phượng", ["Xã Phương Đình", "Xã Trung Châu", "Xã Thọ Xuân", "Xã Thọ An", "Xã Hồng Hà", "Xã Tiến Thịnh"], "Xã Liên Minh"),

    # Huyện Gia Lâm - items 109-112
    ("Huyện Gia Lâm", ["Xã Dương Xá", "Xã Kiêu Kỵ", "Thị trấn Trâu Quỳ", "Phường Thạch Bàn", "Xã Phú Sơn", "Xã Cổ Bi", "Xã Đa Tốn", "Xã Bát Tràng"], "Xã Gia Lâm"),
    ("Huyện Gia Lâm", ["Xã Dương Quang", "Xã Lệ Chi", "Xã Đặng Xá", "Xã Phú Sơn"], "Xã Thuận An"),
    ("Huyện Gia Lâm", ["Xã Kim Đức", "Phường Cự Khối", "Phường Thạch Bàn", "Thị trấn Trâu Quỳ", "Xã Đa Tốn", "Xã Bát Tràng"], "Xã Bát Tràng"),
    ("Huyện Gia Lâm", ["Thị trấn Yên Viên", "Xã Ninh Hiệp", "Xã Phù Đổng", "Xã Thiên Đức", "Xã Yên Thường", "Xã Yên Viên", "Xã Cổ Bi", "Xã Đặng Xá"], "Xã Phù Đổng"),

    # Huyện Đông Anh - items 113-117
    ("Huyện Đông Anh", ["Xã Thụy Lâm", "Xã Vân Hà", "Xã Xuân Nộn", "Thị trấn Đông Anh", "Xã Liên Hà", "Xã Dục Tú", "Xã Nguyên Khê", "Xã Uy Nỗ", "Xã Việt Hùng"], "Xã Thư Lâm"),
    ("Huyện Đông Anh", ["Xã Cổ Loa", "Xã Đông Hội", "Xã Mai Lâm", "Thị trấn Đông Anh", "Xã Tàm Xá", "Xã Tiên Dương", "Xã Vĩnh Ngọc", "Xã Xuân Canh", "Xã Liên Hà", "Xã Dục Tú", "Xã Uy Nỗ", "Xã Việt Hùng"], "Xã Đông Anh"),
    ("Huyện Đông Anh", ["Xã Bắc Hồng", "Xã Nam Hồng", "Xã Vân Nội", "Xã Vĩnh Ngọc", "Xã Nguyên Khê", "Xã Xuân Nộn", "Xã Tiên Dương", "Thị trấn Đông Anh"], "Xã Phúc Thịnh"),
    ("Huyện Đông Anh", ["Xã Võng La", "Xã Kim Chung", "Xã Đại Mạch", "Xã Kim Nỗ", "Xã Tiền Phong", "Xã Hải Bối"], "Xã Thiên Lộc"),
    ("Huyện Đông Anh", ["Xã Tàm Xá", "Xã Xuân Canh", "Xã Vĩnh Ngọc", "Xã Kim Chung", "Xã Hải Bối", "Xã Kim Nỗ"], "Xã Vĩnh Thanh"),

    # Huyện Mê Linh - items 118-121
    ("Huyện Mê Linh", ["Xã Tráng Việt", "Xã Tiền Phong", "Xã Văn Khê", "Xã Mê Linh", "Xã Đại Thịnh", "Xã Hồng Hà", "Xã Liên Hà", "Xã Liên Hồng", "Xã Liên Trung", "Xã Đại Mạch"], "Xã Mê Linh"),
    ("Huyện Mê Linh", ["Xã Chu Phan", "Xã Hoàng Kim", "Xã Liên Mạc", "Xã Thạch Đà", "Xã Văn Khê", "Xã Tiến Thịnh", "Xã Trung Châu", "Xã Thọ Xuân", "Xã Thọ An", "Xã Hồng Hà"], "Xã Yên Lãng"),
    ("Huyện Mê Linh", ["Xã Tam Đồng", "Xã Tiến Thắng", "Xã Tự Lập", "Xã Đại Thịnh", "Xã Kim Hoa", "Xã Thanh Lâm", "Xã Văn Khê", "Xã Thạch Đà"], "Xã Tiến Thắng"),
    ("Huyện Mê Linh", ["Thị trấn Chi Đông", "Thị trấn Quang Minh", "Xã Mê Linh", "Xã Tiền Phong", "Xã Đại Thịnh", "Xã Kim Hoa", "Xã Thanh Lâm"], "Xã Quang Minh"),

    # Huyện Sóc Sơn - items 122-126
    ("Huyện Sóc Sơn", ["Thị trấn Sóc Sơn", "Xã Tân Minh", "Xã Đông Xuân", "Xã Phù Lỗ", "Xã Phù Linh", "Xã Tiên Dược", "Xã Mai Đình", "Xã Phú Minh", "Xã Quang Tiến"], "Xã Sóc Sơn"),
    ("Huyện Sóc Sơn", ["Xã Bắc Phú", "Xã Đức Hoà", "Xã Kim Lũ", "Xã Tân Hưng", "Xã Việt Long", "Xã Xuân Giang", "Xã Xuân Thu"], "Xã Đa Phúc"),
    ("Huyện Sóc Sơn", ["Xã Phú Cường", "Xã Hiền Ninh", "Xã Thanh Xuân", "Xã Mai Đình", "Xã Phú Minh", "Xã Quang Tiến"], "Xã Nội Bài"),
    ("Huyện Sóc Sơn", ["Xã Bắc Sơn", "Xã Hồng Kỳ", "Xã Nam Sơn", "Xã Trung Giã"], "Xã Trung Giã"),
    ("Huyện Sóc Sơn", ["Xã Tân Dân", "Xã Minh Phú", "Xã Minh Trí"], "Xã Kim Anh"),
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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, "templates_app", "static", "data")

    # Process provinces
    provinces = [
        ("Tỉnh Gia Lai", gialai_restructuring_data),
        ("Thành phố Hà Nội", hanoi_restructuring_data),
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

    print(f"\nTotal: {len(all_chuyen_doi)} conversion mappings")
    print(f"Provinces: {len(provinces)}")

    # Save batch file
    batch_chuyen_doi_path = os.path.join(data_dir, "batch4_chuyen_doi.json")
    with open(batch_chuyen_doi_path, 'w', encoding='utf-8') as f:
        json.dump(all_chuyen_doi, f, ensure_ascii=False, indent=2)

    # Merge with main files
    print("\nMerging with main files...")

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

"""
Mẫu lọc nhanh mặc định của các tab Thống kê. Chỉ dùng để tạo dữ liệu ban đầu (migration 0005)
và nút "Khôi phục mẫu mặc định"; sau đó mẫu được thêm / sửa / xoá trên giao diện (model MauThongKe).
"""

MAU_MAC_DINH = {
    'kh': [
        ('Tiền gửi ≥ 1 tỷ, chưa có Agribank Plus', 'so_du_tu=1000000000&loai=ca_nhan&dv_agribank_plus=chua'),
        ('Vừa đăng ký OTT vừa có SMS Banking', 'dv_agribank_plus_ott=co&dv_sms_banking=co'),
        ('Có SMS Banking nhưng chưa dùng OTT', 'dv_sms_banking=co&dv_agribank_plus_ott=chua'),
        ('Đang vay nhưng chưa có Agribank Plus', 'du_no=co&loai=ca_nhan&dv_agribank_plus=chua'),
        ('VIP chưa có thẻ ghi nợ nội địa', 'hang=vip&loai=ca_nhan&dv_the_gn_noi_dia=chua'),
        ('Có TK thanh toán nhưng chưa có thẻ', 'dv_tktt=co&dv_the_gn_noi_dia=chua&dv_the_gn_quoc_te=chua'),
        ('Từ 60 tuổi, tiền gửi ≥ 500 triệu', 'tuoi_tu=60&so_du_tu=500000000'),
        ('Có Loa Thần tài nhưng chưa có QR', 'loa=co&qr=khong'),
        ('TK thanh toán ≥ 50 triệu, chưa có sổ tiết kiệm', 'kkh_tu=50000000&ckh_den=0'),
    ],
    'so': [
        ('Đến hạn trong 7 ngày tới', 'den_han=7'),
        ('Đến hạn trong tháng này', 'den_han=thang_nay'),
        ('Đến hạn tháng sau', 'den_han=thang_sau'),
        ('Sổ ≥ 500 triệu đến hạn trong 30 ngày', 'den_han=30&so_du_tu=500000000'),
        ('Đến hạn tháng này, KH chưa có Agribank Plus', 'den_han=thang_nay&dv=agribank_plus&dv_tt=chua'),
        ('Kỳ hạn ngắn (1–3 tháng)', 'ky_han=1&ky_han=2&ky_han=3'),
        ('Kỳ hạn từ 12 tháng, sổ ≥ 1 tỷ', 'ky_han_tu=12&so_du_tu=1000000000'),
        ('Gửi lâu năm (đã gửi từ 36 tháng)', 'gui_tu=36'),
        ('Tiết kiệm gửi góp', 'hinh_thuc=gui_gop'),
    ],
    'vay': [
        ('Giải ngân 30 ngày qua, KH chưa có Agribank Plus', 'giai_ngan=qua_30&dv=agribank_plus&dv_tt=chua'),
        ('Giải ngân trong tháng này', 'giai_ngan=thang_nay'),
        ('Kỳ trả nợ trong 7 ngày tới', 'tra_tiep=7'),
        ('Đáo hạn trong 30 ngày tới', 'dao_han=30'),
        ('Đã quá ngày đáo hạn (còn dư nợ)', 'dao_han=qua_han'),
        ('Nợ nhóm 2 trở lên', 'nhom_no=02&nhom_no=03&nhom_no=04&nhom_no=05'),
        ('Nợ xấu (nhóm 3–5)', 'nhom_no=03&nhom_no=04&nhom_no=05'),
        ('Dư nợ ≥ 1 tỷ', 'du_no_tu=1000000000'),
        ('Vay ngắn hạn (≤ 12 tháng)', 'thoi_han_loai=ngan'),
        ('Vay trung, dài hạn (> 12 tháng)', 'thoi_han_tu=13'),
        ('Thấu chi', 'san_pham=thau_chi'),
    ],
}


def tao_mau_mac_dinh(model, tab=None):
    """Thêm các mẫu mặc định còn thiếu (so theo tên) cho một tab hoặc tất cả tab. Trả số mẫu đã thêm."""
    them = 0
    for t, ds in MAU_MAC_DINH.items():
        if tab and t != tab:
            continue
        co_san = set(model.objects.filter(tab=t).values_list('ten', flat=True))
        thu_tu = (model.objects.filter(tab=t).order_by('-thu_tu').values_list('thu_tu', flat=True).first() or 0)
        for ten, tham_so in ds:
            if ten not in co_san:
                thu_tu += 10
                model.objects.create(tab=t, ten=ten, tham_so=tham_so, thu_tu=thu_tu)
                them += 1
    return them

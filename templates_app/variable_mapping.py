"""
Ánh xạ biến từ hệ thống mẫu biểu cũ sang hệ thống mới
File này giúp chuyển đổi các template Word cũ sang định dạng mới

Cách sử dụng:
    from templates_app.variable_mapping import OLD_TO_NEW_MAPPING, convert_old_variable

    new_var = convert_old_variable('[ChiNhanh]')  # Returns 'ten_chi_nhanh'
"""

from datetime import date
from django.utils import timezone


# ============================================
# MAPPING: Biến cũ → Biến mới
# ============================================

OLD_TO_NEW_MAPPING = {
    # ===== BIẾN CHI NHÁNH / TOÀN CỤC (GlobalConfig) =====
    '[ChiNhanh]': 'ten_chi_nhanh',
    '[ChiNhanhHOA]': 'ten_chi_nhanh_hoa',
    '[DiaChi]': 'dia_chi_chi_nhanh',
    '[DienThoai]': 'dien_thoai_chi_nhanh',
    '[SoFax]': 'so_fax',
    '[DiaDanh]': 'dia_danh',
    '[MaSoThue]': 'mst',
    '[MaCN]': 'ma_chi_nhanh',
    '[USER]': 'user_name',  # Username của giao dịch viên

    # Cán bộ
    '[GiaoDichVien]': 'giao_dich_vien',
    '[KiemSoatVien]': 'kiem_soat_vien',
    '[GiamDoc]': 'giam_doc',

    # ===== BIẾN TỰ ĐỘNG (Auto-generated) =====
    '[Ngay//]': 'ngay_hien_tai',  # Format: DD/MM/YYYY
    '[NgayThangNam]': 'ngay_thang_nam_text',  # Format: ngày DD tháng MM năm YYYY
    '[DateMonthYear]': 'date_month_year',  # Format: Date DD Month MM Year YYYY
    '[So_HopDong]': 'so_hop_dong',  # Auto-increment

    # ===== BIẾN KHÁCH HÀNG CƠ BẢN (Customer) =====
    '[HotenKhachhangVN]': 'ho_ten',
    '[HotenKhachhangE]': 'ho_ten_tieng_anh',
    '[NamSinh]': 'ngay_sinh',
    '[GioiTinh]': 'gioi_tinh',
    '[DanToc]': 'dan_toc',

    # Liên hệ
    '[SoDienThoai]': 'so_dien_thoai',
    '[Email]': 'email',
    '[DiaChiKhachHang]': 'dia_chi',
    '[HoKhau]': 'ho_khau',  # Hộ khẩu thường trú (khác với địa chỉ hiện tại)

    # CMND/CCCD/Hộ chiếu
    '[SoCMT]': 'so_cmnd',
    '[NgayCMT]': 'ngay_cap_cmnd',
    '[NoiCapCMT]': 'noi_cap_cmnd',
    '[NgayHetHan]': 'ngay_het_han_cmnd',

    # Mã khách hàng
    '[MaSoKhachHang]': 'ma_khach_hang',  # CIF
    '[MaSoThueCN]': 'ma_so_thue',

    # ===== BIẾN TÀI KHOẢN & THẺ (Customer) =====
    '[SoTaiKhoan]': 'so_tai_khoan',
    '[SoTheATM]': 'so_the_atm',
    '[ThoiHanThe]': 'thoi_han_the',
    '[LoaiThe]': 'loai_the',
    '[LoaiPhi]': 'loai_phi',
    '[NgayTraThe]': 'ngay_tra_the',
    '[TienTe]': 'loai_tien_te',

    # ===== BIẾN VAY VỐN (LoanApplication - Tính năng tương lai) =====
    # Thông tin vay
    '[DoiTuongVay]': 'doi_tuong_vay',
    '[DuAnDauTu]': 'du_an_dau_tu',
    '[ThanhToan]': 'phuong_thuc_thanh_toan',
    '[PhuongThucVay]': 'phuong_thuc_vay',

    # Hạn mức & nhu cầu vốn
    '[HanMucTD_So]': 'han_muc_tin_dung',
    '[HanMucTD_Chu]': 'han_muc_tin_dung_chu',  # Auto-convert từ số
    '[NhuCauVon]': 'nhu_cau_von',
    '[NhuCauVon_Chu]': 'nhu_cau_von_chu',

    # Vốn đối ứng
    '[VonTienMat]': 'von_tien_mat',
    '[VonTaiSan_So]': 'von_tai_san',
    '[VonTaiSan_Chu]': 'von_tai_san_chu',
    '[VonSucLD_So]': 'von_suc_lao_dong',
    '[VonSucLD_Chu]': 'von_suc_lao_dong_chu',
    '[VonDoiUng]': 'von_doi_ung',
    '[TyLe]': 'ty_le_von_doi_ung',

    # Thu nhập
    '[ThuNhapKhac]': 'thu_nhap_khac',
    '[ThuNhapSXKD]': 'thu_nhap_san_xuat_kinh_doanh',
    '[ThuNhapPhu]': 'thu_nhap_phu',
    '[TongThuNhap_So]': 'tong_thu_nhap',
    '[TongThuNhap_Chu]': 'tong_thu_nhap_chu',

    # Lãi suất & thời gian
    '[ThoiGianVay]': 'thoi_gian_vay',
    '[LaiSuat]': 'lai_suat',
    '[LSQH]': 'lai_suat_qua_han',  # = lai_suat * 1.5
    '[SoKy]': 'so_ky_tra_no',
    '[HanTraGoc]': 'han_tra_goc',
    '[HanTraLai]': 'han_tra_lai',
    '[QSDD]': 'quyen_su_dung_dat',

    # ===== BIẾN DOANH NGHIỆP (Business - Tính năng tương lai) =====
    '[TenDoanhNghiep]': 'ten_doanh_nghiep',
    '[GiayDKKD]': 'giay_dang_ky_kinh_doanh',
    '[NgDKKD]': 'ngay_cap_giay_dkkd',
    '[NoiCapDKKD]': 'noi_cap_giay_dkkd',
    '[MaSoThueDN]': 'ma_so_thue_doanh_nghiep',
    '[NgayThue]': 'ngay_cap_ma_so_thue',
    '[NoiCapThue]': 'noi_cap_ma_so_thue',
    '[NganhNgheKD]': 'nganh_nghe_kinh_doanh',
    '[DiaChiDoanhNghiep]': 'dia_chi_doanh_nghiep',

    # Ủy quyền
    '[UQGiaoDich]': 'giay_uy_quyen_giao_dich',
    '[NguoiUQ]': 'nguoi_uy_quyen',
    '[NgayUQ]': 'ngay_uy_quyen',
    '[ChucVu]': 'chuc_vu',
    '[ThoiHanHDLD]': 'thoi_han_hop_dong_lao_dong',

    # ===== BIẾN GIAO DỊCH (Transaction - Tính năng tương lai) =====
    '[SoTien]': 'so_tien',
    '[SoTien_Chu]': 'so_tien_chu',
    '[SoTienPhi]': 'so_tien_phi',
    '[SoTienPhi_Chu]': 'so_tien_phi_chu',
    '[NgayGiaoDich]': 'ngay_giao_dich',
    '[TKChuyenSai]': 'tai_khoan_chuyen_sai',
    '[MaGiaoDich]': 'ma_giao_dich',
    '[NoiDung]': 'noi_dung_giao_dich',

    # ===== BIẾN NGƯỜI NHẬN (Beneficiary) =====
    '[NguoiNhan]': 'nguoi_nhan',
    '[NguoiThuHuong1]': 'nguoi_thu_huong',
    '[DTNgNhan]': 'dien_thoai_nguoi_nhan',
    '[CMTNgNhan]': 'cmnd_nguoi_nhan',
    '[NgCMTNgN]': 'ngay_cap_cmnd_nguoi_nhan',
    '[NoiCMTNgN]': 'noi_cap_cmnd_nguoi_nhan',
    '[DiaChiKHNhan]': 'dia_chi_nguoi_nhan',
    '[TKNHNhan]': 'tai_khoan_nguoi_nhan',
    '[NganHangNhan]': 'ngan_hang_nguoi_nhan',

    # ===== BIẾN DỊCH VỤ (Service) =====
    '[ViDienTu]': 'loai_vi_dien_tu',
    '[ThuHo]': 'loai_thu_ho',
    '[NhaCungCap]': 'nha_cung_cap_dich_vu',

    # ===== BIẾN POS/QR CODE (POSDevice - Tính năng tương lai) =====
    # Cán bộ quản lý
    '[CanBoQL]': 'can_bo_quan_ly_thiet_bi',
    '[DTCanBo]': 'dien_thoai_can_bo',
    '[UserCBQL]': 'user_can_bo_quan_ly',
    '[EmailCBQL]': 'email_can_bo_quan_ly',

    # Thông tin thiết bị
    '[ModelPOS]': 'model_pos',
    '[MerchantID]': 'merchant_id',
    '[TerminalID]': 'terminal_id',
    '[SerialPOS]': 'serial_pos',

    # Phí chiết khấu POS
    '[APos]': 'phi_ck_pos_agribank',
    '[NPos]': 'phi_ck_pos_napas',
    '[VPos]': 'phi_ck_pos_visa',
    '[MPos]': 'phi_ck_pos_mastercard',
    '[JPos]': 'phi_ck_pos_jcb',
    '[CPos]': 'phi_ck_pos_cup',

    # Phí chiết khấu QR Code
    '[AQr]': 'phi_ck_qr_agribank',
    '[NQr]': 'phi_ck_qr_napas',
    '[VQr]': 'phi_ck_qr_visa',
    '[MQr]': 'phi_ck_qr_mastercard',
    '[JQr]': 'phi_ck_qr_jcb',
    '[CQr]': 'phi_ck_qr_cup',

    # Cửa hàng
    '[TenCuaHang]': 'ten_cua_hang',
    '[DiaChiCuaHang]': 'dia_chi_cua_hang',
}


# ============================================
# REVERSE MAPPING: Biến mới → Biến cũ
# ============================================

NEW_TO_OLD_MAPPING = {v: k for k, v in OLD_TO_NEW_MAPPING.items()}


# ============================================
# PHÂN LOẠI BIẾN THEO MODEL
# ============================================

GLOBAL_CONFIG_VARIABLES = [
    'ten_chi_nhanh', 'ten_chi_nhanh_hoa', 'dia_chi_chi_nhanh',
    'dien_thoai_chi_nhanh', 'so_fax', 'dia_danh', 'mst', 'ma_chi_nhanh',
    'giao_dich_vien', 'kiem_soat_vien', 'giam_doc', 'user_name'
]

CUSTOMER_VARIABLES = [
    'ho_ten', 'ho_ten_tieng_anh', 'ngay_sinh', 'gioi_tinh', 'dan_toc',
    'so_dien_thoai', 'email', 'dia_chi', 'ho_khau',
    'so_cmnd', 'ngay_cap_cmnd', 'noi_cap_cmnd', 'ngay_het_han_cmnd',
    'ma_khach_hang', 'ma_so_thue',
    'so_tai_khoan', 'so_the_atm', 'thoi_han_the', 'loai_the',
    'loai_phi', 'ngay_tra_the', 'loai_tien_te'
]

# Biến tiền gửi tiết kiệm chung (Joint Savings)
JOINT_SAVINGS_VARIABLES = [
    # Thông tin người gửi tiền thứ hai
    'ho_ten_nguoi_gui_2', 'so_cmnd_nguoi_gui_2', 'ngay_cap_cmnd_nguoi_gui_2',
    'noi_cap_cmnd_nguoi_gui_2', 'dia_chi_nguoi_gui_2', 'sdt_nguoi_gui_2',
    # Giao dịch thẻ tiết kiệm - Tất cả người gửi tiền
    'gd_rut_lai_tat_ca', 'gd_tat_toan_tat_ca', 'gd_bao_mat_tat_ca',
    'gd_bao_hong_tat_ca', 'gd_phong_toa_tat_ca', 'gd_xac_nhan_so_du_tat_ca',
    # Giao dịch thẻ tiết kiệm - Một/một số người gửi tiền
    'gd_rut_lai_mot_so', 'gd_tat_toan_mot_so', 'gd_bao_mat_mot_so',
    'gd_bao_hong_mot_so', 'gd_phong_toa_mot_so', 'gd_xac_nhan_so_du_mot_so',
]

AUTO_GENERATED_VARIABLES = [
    'ngay_hien_tai', 'ngay_thang_nam_text', 'date_month_year', 'so_hop_dong'
]

LOAN_VARIABLES = [
    'doi_tuong_vay', 'du_an_dau_tu', 'phuong_thuc_thanh_toan', 'phuong_thuc_vay',
    'han_muc_tin_dung', 'han_muc_tin_dung_chu', 'nhu_cau_von', 'nhu_cau_von_chu',
    'von_tien_mat', 'von_tai_san', 'von_tai_san_chu',
    'von_suc_lao_dong', 'von_suc_lao_dong_chu', 'von_doi_ung', 'ty_le_von_doi_ung',
    'thu_nhap_khac', 'thu_nhap_san_xuat_kinh_doanh', 'thu_nhap_phu',
    'tong_thu_nhap', 'tong_thu_nhap_chu',
    'thoi_gian_vay', 'lai_suat', 'lai_suat_qua_han', 'so_ky_tra_no',
    'han_tra_goc', 'han_tra_lai', 'quyen_su_dung_dat'
]

BUSINESS_VARIABLES = [
    'ten_doanh_nghiep', 'giay_dang_ky_kinh_doanh', 'ngay_cap_giay_dkkd',
    'noi_cap_giay_dkkd', 'ma_so_thue_doanh_nghiep', 'ngay_cap_ma_so_thue',
    'noi_cap_ma_so_thue', 'nganh_nghe_kinh_doanh', 'dia_chi_doanh_nghiep',
    'giay_uy_quyen_giao_dich', 'nguoi_uy_quyen', 'ngay_uy_quyen',
    'chuc_vu', 'thoi_han_hop_dong_lao_dong'
]

TRANSACTION_VARIABLES = [
    'so_tien', 'so_tien_chu', 'so_tien_phi', 'so_tien_phi_chu',
    'ngay_giao_dich', 'tai_khoan_chuyen_sai', 'ma_giao_dich',
    'noi_dung_giao_dich'
]

BENEFICIARY_VARIABLES = [
    'nguoi_nhan', 'nguoi_thu_huong', 'dien_thoai_nguoi_nhan',
    'cmnd_nguoi_nhan', 'ngay_cap_cmnd_nguoi_nhan', 'noi_cap_cmnd_nguoi_nhan',
    'dia_chi_nguoi_nhan', 'tai_khoan_nguoi_nhan', 'ngan_hang_nguoi_nhan'
]

SERVICE_VARIABLES = [
    'loai_vi_dien_tu', 'loai_thu_ho', 'nha_cung_cap_dich_vu'
]

POS_DEVICE_VARIABLES = [
    'can_bo_quan_ly_thiet_bi', 'dien_thoai_can_bo', 'user_can_bo_quan_ly',
    'email_can_bo_quan_ly', 'model_pos', 'merchant_id', 'terminal_id', 'serial_pos',
    'phi_ck_pos_agribank', 'phi_ck_pos_napas', 'phi_ck_pos_visa',
    'phi_ck_pos_mastercard', 'phi_ck_pos_jcb', 'phi_ck_pos_cup',
    'phi_ck_qr_agribank', 'phi_ck_qr_napas', 'phi_ck_qr_visa',
    'phi_ck_qr_mastercard', 'phi_ck_qr_jcb', 'phi_ck_qr_cup',
    'ten_cua_hang', 'dia_chi_cua_hang'
]


# ============================================
# HELPER FUNCTIONS
# ============================================

def convert_old_variable(old_var):
    """
    Chuyển đổi tên biến cũ sang biến mới

    Args:
        old_var (str): Tên biến cũ, ví dụ: '[ChiNhanh]'

    Returns:
        str: Tên biến mới, ví dụ: 'ten_chi_nhanh'
        None nếu không tìm thấy
    """
    return OLD_TO_NEW_MAPPING.get(old_var)


def convert_new_variable(new_var):
    """
    Chuyển đổi tên biến mới sang biến cũ

    Args:
        new_var (str): Tên biến mới, ví dụ: 'ten_chi_nhanh'

    Returns:
        str: Tên biến cũ, ví dụ: '[ChiNhanh]'
        None nếu không tìm thấy
    """
    return NEW_TO_OLD_MAPPING.get(new_var)


def get_variable_category(var_name):
    """
    Xác định biến thuộc nhóm nào

    Args:
        var_name (str): Tên biến (có thể là cũ hoặc mới)

    Returns:
        str: Tên category (global_config, customer, auto, loan, business, etc.)
        None nếu không xác định được
    """
    # Convert về biến mới nếu là biến cũ
    if var_name.startswith('[') and var_name.endswith(']'):
        var_name = convert_old_variable(var_name)
        if not var_name:
            return None

    if var_name in GLOBAL_CONFIG_VARIABLES:
        return 'global_config'
    elif var_name in CUSTOMER_VARIABLES:
        return 'customer'
    elif var_name in JOINT_SAVINGS_VARIABLES:
        return 'joint_savings'
    elif var_name in AUTO_GENERATED_VARIABLES:
        return 'auto_generated'
    elif var_name in LOAN_VARIABLES:
        return 'loan'
    elif var_name in BUSINESS_VARIABLES:
        return 'business'
    elif var_name in TRANSACTION_VARIABLES:
        return 'transaction'
    elif var_name in BENEFICIARY_VARIABLES:
        return 'beneficiary'
    elif var_name in SERVICE_VARIABLES:
        return 'service'
    elif var_name in POS_DEVICE_VARIABLES:
        return 'pos_device'
    else:
        return 'unknown'


def convert_template_content(content):
    """
    Chuyển đổi nội dung template từ format cũ sang mới

    Args:
        content (str): Nội dung template với biến cũ

    Returns:
        str: Nội dung template với biến mới (Jinja2 format)

    Example:
        Input: "Khách hàng: [HotenKhachhangVN]"
        Output: "Khách hàng: {{ ho_ten }}"
    """
    import re

    def replace_variable(match):
        old_var = match.group(0)
        new_var = convert_old_variable(old_var)
        if new_var:
            return f"{{{{ {new_var} }}}}"
        else:
            # Giữ nguyên nếu không tìm thấy mapping
            return old_var

    # Replace tất cả biến [TenBien] → {{ ten_bien }}
    pattern = r'\[[\w/]+\]'
    converted = re.sub(pattern, replace_variable, content)

    return converted


def generate_auto_variables():
    """
    Tạo dictionary các biến tự động

    Returns:
        dict: Dictionary chứa các biến tự động với giá trị hiện tại
    """
    from datetime import date
    import locale

    today = date.today()

    # Format ngày tháng năm
    day = today.day
    month = today.month
    year = today.year

    # Tiếng Việt
    ngay_thang_nam_text = f"ngày {day:02d} tháng {month:02d} năm {year}"

    # Tiếng Anh
    month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    date_month_year = f"Date {day:02d} Month {month:02d} Year {year}"

    return {
        'ngay_hien_tai': today.strftime('%d/%m/%Y'),
        'ngay_thang_nam_text': ngay_thang_nam_text,
        'date_month_year': date_month_year,
        'nam_hien_tai': year,
        'thang_hien_tai': month,
        'ngay_hien_tai_day': day,
    }


# ============================================
# EXPORT
# ============================================

__all__ = [
    'OLD_TO_NEW_MAPPING',
    'NEW_TO_OLD_MAPPING',
    'GLOBAL_CONFIG_VARIABLES',
    'CUSTOMER_VARIABLES',
    'JOINT_SAVINGS_VARIABLES',
    'AUTO_GENERATED_VARIABLES',
    'convert_old_variable',
    'convert_new_variable',
    'get_variable_category',
    'convert_template_content',
    'generate_auto_variables',
]

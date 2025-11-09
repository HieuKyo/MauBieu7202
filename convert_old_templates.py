#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT CHUYỂN ĐỔI MẪU BIỂU TỰ ĐỘNG
Chuyển đổi các placeholder cũ [TenBien] sang biến mới {{ ten_bien }}

Sử dụng:
    python convert_old_templates.py <thu_muc_mau_bieu>

Ví dụ:
    python convert_old_templates.py ./mau_bieu_cu
"""

import os
import sys
import shutil
from docx import Document
from datetime import datetime


# =====================================================
# BẢNG MAPPING: Biến cũ → Biến mới
# Sync từ templates_app/variable_mapping.py
# =====================================================
VARIABLE_MAPPING = {
    # ===== BIẾN CHI NHÁNH / TOÀN CỤC (GlobalConfig) =====
    '[ChiNhanh]': '{{ ten_chi_nhanh }}',
    '[ChiNhanhHOA]': '{{ ten_chi_nhanh_hoa }}',
    '[DiaChi]': '{{ dia_chi_chi_nhanh }}',
    '[DienThoai]': '{{ dien_thoai_chi_nhanh }}',
    '[SoFax]': '{{ so_fax }}',
    '[DiaDanh]': '{{ dia_danh }}',
    '[MaSoThue]': '{{ mst }}',
    '[MaCN]': '{{ ma_chi_nhanh }}',
    '[USER]': '{{ user_name }}',

    # Cán bộ
    '[GiaoDichVien]': '{{ giao_dich_vien }}',
    '[GDichVien]': '{{ giao_dich_vien }}',  # Alias
    '[KiemSoatVien]': '{{ kiem_soat_vien }}',
    '[KiemSoat]': '{{ kiem_soat_vien }}',  # Alias
    '[GiamDoc]': '{{ giam_doc }}',
    '[LanhDao]': '{{ giam_doc }}',  # Alias

    # ===== BIẾN TỰ ĐỘNG (Auto-generated) =====
    '[Ngay//]': '{{ ngay_hien_tai }}',
    '[NgayThangNam]': '{{ ngay_thang_nam_text }}',
    '[DateMonthYear]': '{{ date_month_year }}',
    '[So_HopDong]': '{{ so_hop_dong }}',

    # ===== BIẾN KHÁCH HÀNG CƠ BẢN (Customer) =====
    '[HotenKhachhangVN]': '{{ ho_ten }}',
    '[HotenKhachhangE]': '{{ ho_ten_tieng_anh }}',
    '[NamSinh]': '{{ ngay_sinh }}',
    '[GioiTinh]': '{{ gioi_tinh }}',
    '[DanToc]': '{{ dan_toc }}',

    # Liên hệ
    '[SoDienThoai]': '{{ so_dien_thoai }}',
    '[Email]': '{{ email }}',
    '[DiaChiKhachHang]': '{{ dia_chi }}',
    '[HoKhau]': '{{ ho_khau }}',

    # CMND/CCCD/Hộ chiếu
    '[SoCMT]': '{{ so_cmnd }}',
    '[NgayCMT]': '{{ ngay_cap_cmnd }}',
    '[NoiCapCMT]': '{{ noi_cap_cmnd }}',
    '[NgayHetHan]': '{{ ngay_het_han_cmnd }}',

    # Mã khách hàng
    '[MaSoKhachHang]': '{{ ma_khach_hang }}',
    '[MaSoThueCN]': '{{ ma_so_thue }}',

    # ===== BIẾN TÀI KHOẢN & THẺ (Customer) =====
    '[SoTaiKhoan]': '{{ so_tai_khoan }}',
    '[SoTheATM]': '{{ so_the_atm }}',
    '[ThoiHanThe]': '{{ thoi_han_the }}',
    '[LoaiThe]': '{{ loai_the }}',
    '[LoaiPhi]': '{{ loai_phi }}',
    '[NgayTraThe]': '{{ ngay_tra_the }}',
    '[TienTe]': '{{ loai_tien_te }}',

    # ===== BIẾN VAY VỐN (LoanApplication) =====
    # Thông tin vay
    '[DoiTuongVay]': '{{ doi_tuong_vay }}',
    '[DuAnDauTu]': '{{ du_an_dau_tu }}',
    '[ThanhToan]': '{{ phuong_thuc_thanh_toan }}',
    '[PhuongThucVay]': '{{ phuong_thuc_vay }}',

    # Hạn mức & nhu cầu vốn
    '[HanMucTD_So]': '{{ han_muc_tin_dung }}',
    '[HanMucTD_Chu]': '{{ han_muc_tin_dung_chu }}',
    '[NhuCauVon]': '{{ nhu_cau_von }}',
    '[NhuCauVon_Chu]': '{{ nhu_cau_von_chu }}',

    # Vốn đối ứng
    '[VonTienMat]': '{{ von_tien_mat }}',
    '[VonTaiSan_So]': '{{ von_tai_san }}',
    '[VonTaiSan_Chu]': '{{ von_tai_san_chu }}',
    '[VonSucLD_So]': '{{ von_suc_lao_dong }}',
    '[VonSucLD_Chu]': '{{ von_suc_lao_dong_chu }}',
    '[VonDoiUng]': '{{ von_doi_ung }}',
    '[TyLe]': '{{ ty_le_von_doi_ung }}',

    # Thu nhập
    '[ThuNhapKhac]': '{{ thu_nhap_khac }}',
    '[ThuNhapSXKD]': '{{ thu_nhap_san_xuat_kinh_doanh }}',
    '[ThuNhapPhu]': '{{ thu_nhap_phu }}',
    '[TongThuNhap_So]': '{{ tong_thu_nhap }}',
    '[TongThuNhap_Chu]': '{{ tong_thu_nhap_chu }}',

    # Lãi suất & thời gian
    '[ThoiGianVay]': '{{ thoi_gian_vay }}',
    '[LaiSuat]': '{{ lai_suat }}',
    '[LSQH]': '{{ lai_suat_qua_han }}',
    '[SoKy]': '{{ so_ky_tra_no }}',
    '[HanTraGoc]': '{{ han_tra_goc }}',
    '[HanTraLai]': '{{ han_tra_lai }}',
    '[QSDD]': '{{ quyen_su_dung_dat }}',

    # ===== BIẾN DOANH NGHIỆP (Business) =====
    '[TenDoanhNghiep]': '{{ ten_doanh_nghiep }}',
    '[GiayDKKD]': '{{ giay_dang_ky_kinh_doanh }}',
    '[NgDKKD]': '{{ ngay_cap_giay_dkkd }}',
    '[NoiCapDKKD]': '{{ noi_cap_giay_dkkd }}',
    '[MaSoThueDN]': '{{ ma_so_thue_doanh_nghiep }}',
    '[NgayThue]': '{{ ngay_cap_ma_so_thue }}',
    '[NoiCapThue]': '{{ noi_cap_ma_so_thue }}',
    '[NganhNgheKD]': '{{ nganh_nghe_kinh_doanh }}',
    '[DiaChiDoanhNghiep]': '{{ dia_chi_doanh_nghiep }}',

    # Ủy quyền
    '[UQGiaoDich]': '{{ giay_uy_quyen_giao_dich }}',
    '[NguoiUQ]': '{{ nguoi_uy_quyen }}',
    '[NgayUQ]': '{{ ngay_uy_quyen }}',
    '[ChucVu]': '{{ chuc_vu }}',
    '[ThoiHanHDLD]': '{{ thoi_han_hop_dong_lao_dong }}',

    # ===== BIẾN GIAO DỊCH (Transaction) =====
    '[SoTien]': '{{ so_tien }}',
    '[SoTien_Chu]': '{{ so_tien_chu }}',
    '[SoTienPhi]': '{{ so_tien_phi }}',
    '[SoTienPhi_Chu]': '{{ so_tien_phi_chu }}',
    '[NgayGiaoDich]': '{{ ngay_giao_dich }}',
    '[TKChuyenSai]': '{{ tai_khoan_chuyen_sai }}',
    '[MaGiaoDich]': '{{ ma_giao_dich }}',
    '[NoiDung]': '{{ noi_dung_giao_dich }}',

    # ===== BIẾN NGƯỜI NHẬN (Beneficiary) =====
    '[NguoiNhan]': '{{ nguoi_nhan }}',
    '[NguoiThuHuong1]': '{{ nguoi_thu_huong }}',
    '[DTNgNhan]': '{{ dien_thoai_nguoi_nhan }}',
    '[CMTNgNhan]': '{{ cmnd_nguoi_nhan }}',
    '[NgCMTNgN]': '{{ ngay_cap_cmnd_nguoi_nhan }}',
    '[NoiCMTNgN]': '{{ noi_cap_cmnd_nguoi_nhan }}',
    '[DiaChiKHNhan]': '{{ dia_chi_nguoi_nhan }}',
    '[TKNHNhan]': '{{ tai_khoan_nguoi_nhan }}',
    '[NganHangNhan]': '{{ ngan_hang_nguoi_nhan }}',

    # ===== BIẾN DỊCH VỤ (Service) =====
    '[ViDienTu]': '{{ loai_vi_dien_tu }}',
    '[ThuHo]': '{{ loai_thu_ho }}',
    '[NhaCungCap]': '{{ nha_cung_cap_dich_vu }}',

    # ===== BIẾN POS/QR CODE (POSDevice) =====
    # Cán bộ quản lý
    '[CanBoQL]': '{{ can_bo_quan_ly_thiet_bi }}',
    '[DTCanBo]': '{{ dien_thoai_can_bo }}',
    '[UserCBQL]': '{{ user_can_bo_quan_ly }}',
    '[EmailCBQL]': '{{ email_can_bo_quan_ly }}',

    # Thông tin thiết bị
    '[ModelPOS]': '{{ model_pos }}',
    '[MerchantID]': '{{ merchant_id }}',
    '[TerminalID]': '{{ terminal_id }}',
    '[SerialPOS]': '{{ serial_pos }}',

    # Phí chiết khấu POS
    '[APos]': '{{ phi_ck_pos_agribank }}',
    '[NPos]': '{{ phi_ck_pos_napas }}',
    '[VPos]': '{{ phi_ck_pos_visa }}',
    '[MPos]': '{{ phi_ck_pos_mastercard }}',
    '[JPos]': '{{ phi_ck_pos_jcb }}',
    '[CPos]': '{{ phi_ck_pos_cup }}',

    # Phí chiết khấu QR Code
    '[AQr]': '{{ phi_ck_qr_agribank }}',
    '[NQr]': '{{ phi_ck_qr_napas }}',
    '[VQr]': '{{ phi_ck_qr_visa }}',
    '[MQr]': '{{ phi_ck_qr_mastercard }}',
    '[JQr]': '{{ phi_ck_qr_jcb }}',
    '[CQr]': '{{ phi_ck_qr_cup }}',

    # Cửa hàng
    '[TenCuaHang]': '{{ ten_cua_hang }}',
    '[DiaChiCuaHang]': '{{ dia_chi_cua_hang }}',
}

# Các biến ngày tháng (từng chữ số)
DATE_DIGIT_MAPPING = {
    # Ngày sinh
    '[d1]': '{{ d1 }}',
    '[d2]': '{{ d2 }}',
    '[m1]': '{{ m1 }}',
    '[m2]': '{{ m2 }}',
    '[y1]': '{{ y1 }}',
    '[y2]': '{{ y2 }}',
    '[y3]': '{{ y3 }}',
    '[y4]': '{{ y4 }}',

    # Ngày cấp CCCD
    '[dcc1]': '{{ dcc1 }}',
    '[dcc2]': '{{ dcc2 }}',
    '[mcc1]': '{{ mcc1 }}',
    '[mcc2]': '{{ mcc2 }}',
    '[ycc1]': '{{ ycc1 }}',
    '[ycc2]': '{{ ycc2 }}',
    '[ycc3]': '{{ ycc3 }}',
    '[ycc4]': '{{ ycc4 }}',

    # Ngày hết hạn CCCD
    '[dhh1]': '{{ dhh1 }}',
    '[dhh2]': '{{ dhh2 }}',
    '[mhh1]': '{{ mhh1 }}',
    '[mhh2]': '{{ mhh2 }}',
    '[yhh1]': '{{ yhh1 }}',
    '[yhh2]': '{{ yhh2 }}',
    '[yhh3]': '{{ yhh3 }}',
    '[yhh4]': '{{ yhh4 }}',
}

# Merge tất cả mappings
ALL_MAPPINGS = {**VARIABLE_MAPPING, **DATE_DIGIT_MAPPING}


# =====================================================
# BẢNG MAPPING: Checkbox Tag Cũ → Checkbox Tag Mới
# Ánh xạ các Tag names từ template cũ sang biến mới
# =====================================================
CHECKBOX_TAG_MAPPING = {
    # ===== GIỚI TÍNH =====
    'Check_NAM': 'gioi_tinh_nam',
    'Check_NU': 'gioi_tinh_nu',
    'Check_Nam': 'gioi_tinh_nam',
    'Check_Nu': 'gioi_tinh_nu',

    # ===== LOẠI TÀI KHOẢN =====
    'LoaiTK_Auto': 'tk_ngau_nhien',
    'LoaiTK_Chon': 'tk_theo_yeu_cau',
    'LoaiTK_ChDung': 'tk_theo_yeu_cau',  # Alias
    'Check_TK_Auto': 'tk_ngau_nhien',
    'Check_TK_Chon': 'tk_theo_yeu_cau',

    # ===== LOẠI TIỀN TỆ =====
    'Check_VND': 'loai_tien_vnd',
    'Check_USD': 'loai_tien_usd',
    'Check_EUR': 'loai_tien_eur',

    # ===== HẠNG THẺ =====
    'Check_C': 'the_hang_chuan',
    'Check_Chuan': 'the_hang_chuan',
    'Check_V': 'the_hang_vang',
    'Check_Vang': 'the_hang_vang',
    'Check_P': 'the_hang_bach_kim',
    'Check_BachKim': 'the_hang_bach_kim',

    # ===== LOẠI THẺ =====
    'Check_ND': 'the_ghi_no_noi_dia',
    'Check_GN_ND': 'the_ghi_no_noi_dia',
    'Check_LN': 'the_ghi_no_quoc_te',
    'Check_GN_QT': 'the_ghi_no_quoc_te',
    'Check_TH': 'the_tin_dung',
    'Check_TD': 'the_tin_dung',
    'Check_JCB': 'loai_the_jcb',
    'Check_VS': 'loai_the_visa',
    'Check_Visa': 'loai_the_visa',
    'Check_MT': 'loai_the_mastercard',
    'Check_Mastercard': 'loai_the_mastercard',
    'Check_KHAC': 'loai_the_khac',

    # ===== PHÁT HÀNH THẺ =====
    'Check_LD': 'phat_hanh_lan_dau',
    'Check_LanDau': 'phat_hanh_lan_dau',
    'Check_PHL': 'phat_hanh_lai',
    'Check_PhatHanhLai': 'phat_hanh_lai',

    # ===== NGHỀ NGHIỆP =====
    'Check_CongChuc': 'nghe_nghiep_cong_chuc',
    'Check_CC': 'nghe_nghiep_cong_chuc',
    'Check_NongDan': 'nghe_nghiep_nong_dan',
    'Check_ND': 'nghe_nghiep_nong_dan',
    'Check_GiaoVien': 'nghe_nghiep_giao_vien_bac_si',
    'Check_BacSi': 'nghe_nghiep_giao_vien_bac_si',
    'Check_GV': 'nghe_nghiep_giao_vien_bac_si',
    'Check_CongNhan': 'nghe_nghiep_cong_nhan',
    'Check_CN': 'nghe_nghiep_cong_nhan',
    'Check_KinhDoanh': 'nghe_nghiep_kinh_doanh',
    'Check_KD': 'nghe_nghiep_kinh_doanh',
    'Check_HocSinh': 'nghe_nghiep_hoc_sinh_sinh_vien',
    'Check_SinhVien': 'nghe_nghiep_hoc_sinh_sinh_vien',
    'Check_HS': 'nghe_nghiep_hoc_sinh_sinh_vien',
    'Check_NoiTro': 'nghe_nghiep_noi_tro',
    'Check_NT': 'nghe_nghiep_noi_tro',
    'Check_NgheNghiepKhac': 'nghe_nghiep_khac',

    # ===== DỊCH VỤ NGÂN HÀNG ĐIỆN TỬ =====
    'Check_S': 'dv_sms_banking',
    'Check_SMS': 'dv_sms_banking',
    'Check_E': 'dv_e_mobile',
    'Check_EMobile': 'dv_e_mobile',
    'Check_AP': 'dv_e_mobile',  # Agribank Plus → E-Mobile (dịch vụ chính)
    'Check_B': 'dv_bankplus',
    'Check_BankPlus': 'dv_bankplus',
    'Check_EC': 'dv_e_commerce',
    'Check_ECommerce': 'dv_e_commerce',
    'Check_IB': 'dv_retail_ebanking',
    'Check_Retail': 'dv_retail_ebanking',
    'Check_RetailEB': 'dv_retail_ebanking',
    'Check_OTPI': 'dv_soft_otp',
    'Check_OTP_SI': 'dv_soft_otp',
    'Check_SoftOTP': 'dv_soft_otp',
    'Check_OTP_TI': 'dv_smart_otp',
    'Check_SmartOTP': 'dv_smart_otp',

    # ===== DỊCH VỤ THU HỘ =====
    'Check_Nuoc': 'dv_thu_ho_tien_nuoc',
    'Check_TienNuoc': 'dv_thu_ho_tien_nuoc',
    'Check_Dien': 'dv_thu_ho_tien_dien',
    'Check_TienDien': 'dv_thu_ho_tien_dien',
    'Check_VT': 'dv_thu_ho_vien_thong',
    'Check_VienT': 'dv_thu_ho_vien_thong',
    'Check_VienThong': 'dv_thu_ho_vien_thong',
    'Check_HP': 'dv_thu_ho_hoc_phi',
    'Check_HocP': 'dv_thu_ho_hoc_phi',
    'Check_HocPhi': 'dv_thu_ho_hoc_phi',
    'Check_BH': 'dv_thu_ho_bao_hiem',
    'Check_BaoHiem': 'dv_thu_ho_bao_hiem',

    # ===== KÊNH GIAO DỊCH =====
    'Check_Mobile': 'kenh_mobile',
    'Check_Internet': 'kenh_internet',
    'Check_IB_Kenh': 'kenh_internet',
}


def convert_checkbox_tags(doc):
    """
    Chuyển đổi Tag names của Content Control checkboxes

    Args:
        doc: Document object

    Returns:
        dict: Thống kê số lượng checkbox tags đã thay thế
    """
    # Namespace cho Word XML
    NSMAP = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'w14': 'http://schemas.microsoft.com/office/word/2010/wordml'
    }

    tag_replacements = {}

    # Tìm tất cả Content Controls
    for sdt in doc.element.findall('.//w:sdt', namespaces=NSMAP):
        # Lấy tag element
        tag_element = sdt.find('.//w:tag', namespaces=NSMAP)
        if tag_element is None:
            continue

        old_tag = tag_element.get(f'{{{NSMAP["w"]}}}val')
        if not old_tag:
            continue

        # Kiểm tra xem có trong mapping không
        if old_tag in CHECKBOX_TAG_MAPPING:
            new_tag = CHECKBOX_TAG_MAPPING[old_tag]

            # Set tag mới
            tag_element.set(f'{{{NSMAP["w"]}}}val', new_tag)

            # Update alias/title (optional)
            alias_element = sdt.find('.//w:alias', namespaces=NSMAP)
            if alias_element is not None:
                alias_element.set(f'{{{NSMAP["w"]}}}val', new_tag)

            # Thống kê
            tag_replacements[old_tag] = tag_replacements.get(old_tag, 0) + 1

    return tag_replacements


def convert_document(input_path, output_path, backup=True):
    """
    Chuyển đổi một file Word từ placeholder cũ sang biến mới

    Args:
        input_path: Đường dẫn file input
        output_path: Đường dẫn file output
        backup: Có tạo backup không

    Returns:
        dict: Thống kê số lượng biến đã thay thế
    """
    # Backup file gốc nếu cần
    if backup and input_path == output_path:
        backup_path = input_path.replace('.docx', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx')
        shutil.copy2(input_path, backup_path)
        print(f"  ✓ Đã backup: {os.path.basename(backup_path)}")

    # Load document
    doc = Document(input_path)

    replacements = {}

    def replace_text_in_paragraph(paragraph):
        """Thay thế text trong paragraph"""
        if not paragraph.text:
            return

        original_text = paragraph.text
        new_text = original_text

        # Thay thế từng mapping
        for old_var, new_var in ALL_MAPPINGS.items():
            if old_var in new_text:
                count = new_text.count(old_var)
                new_text = new_text.replace(old_var, new_var)
                replacements[old_var] = replacements.get(old_var, 0) + count

        # Nếu có thay đổi, update paragraph
        if new_text != original_text:
            # Clear existing runs
            for run in paragraph.runs:
                run.text = ''

            # Add new text to first run
            if paragraph.runs:
                paragraph.runs[0].text = new_text
            else:
                paragraph.add_run(new_text)

    # Process paragraphs
    for paragraph in doc.paragraphs:
        replace_text_in_paragraph(paragraph)

    # Process tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    replace_text_in_paragraph(paragraph)

    # Process headers
    for section in doc.sections:
        for paragraph in section.header.paragraphs:
            replace_text_in_paragraph(paragraph)

        # Process footers
        for paragraph in section.footer.paragraphs:
            replace_text_in_paragraph(paragraph)

    # Convert checkbox tags
    checkbox_replacements = convert_checkbox_tags(doc)

    # Save document
    doc.save(output_path)

    # Combine statistics
    combined_stats = {
        'text_variables': replacements,
        'checkbox_tags': checkbox_replacements
    }

    return combined_stats


def process_folder(folder_path, output_folder=None, backup=True):
    """
    Xử lý tất cả file .docx trong folder

    Args:
        folder_path: Đường dẫn folder chứa file cần convert
        output_folder: Folder output (None = ghi đè file gốc)
        backup: Có tạo backup không
    """
    if not os.path.exists(folder_path):
        print(f"❌ Không tìm thấy folder: {folder_path}")
        return

    # Tìm tất cả file .docx
    docx_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.docx') and not file.startswith('~$'):
                docx_files.append(os.path.join(root, file))

    if not docx_files:
        print(f"❌ Không tìm thấy file .docx nào trong folder: {folder_path}")
        return

    print(f"\n{'='*60}")
    print(f"Tìm thấy {len(docx_files)} file .docx")
    print(f"{'='*60}\n")

    # Process từng file
    total_text_replacements = {}
    total_checkbox_replacements = {}
    successful = 0
    failed = 0

    for i, input_path in enumerate(docx_files, 1):
        filename = os.path.basename(input_path)
        print(f"[{i}/{len(docx_files)}] Đang xử lý: {filename}")

        try:
            # Determine output path
            if output_folder:
                os.makedirs(output_folder, exist_ok=True)
                output_path = os.path.join(output_folder, filename)
            else:
                output_path = input_path

            # Convert
            stats = convert_document(input_path, output_path, backup)

            # Update statistics
            text_vars = stats.get('text_variables', {})
            checkbox_tags = stats.get('checkbox_tags', {})

            for var, count in text_vars.items():
                total_text_replacements[var] = total_text_replacements.get(var, 0) + count

            for tag, count in checkbox_tags.items():
                total_checkbox_replacements[tag] = total_checkbox_replacements.get(tag, 0) + count

            # Print summary for this file
            text_count = sum(text_vars.values())
            checkbox_count = sum(checkbox_tags.values())

            if text_count > 0:
                print(f"  ✓ Đã thay thế {text_count} biến text")
            if checkbox_count > 0:
                print(f"  ✓ Đã thay thế {checkbox_count} checkbox tags")
            if text_count == 0 and checkbox_count == 0:
                print(f"  ℹ Không tìm thấy biến cũ nào")

            successful += 1

        except Exception as e:
            print(f"  ❌ Lỗi: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1

        print()

    # Print summary
    print(f"\n{'='*80}")
    print(f"KẾT QUẢ CHUYỂN ĐỔI")
    print(f"{'='*80}")
    print(f"✓ Thành công: {successful} file")
    if failed > 0:
        print(f"❌ Thất bại: {failed} file")

    # Print text variables
    if total_text_replacements:
        print(f"\nCHI TIẾT BIẾN TEXT ĐÃ THAY THẾ:")
        print(f"{'-'*80}")
        for old_var, count in sorted(total_text_replacements.items(), key=lambda x: x[1], reverse=True):
            new_var = ALL_MAPPINGS.get(old_var, '???')
            print(f"  {old_var:30s} → {new_var:35s} ({count} lần)")

    # Print checkbox tags
    if total_checkbox_replacements:
        print(f"\nCHI TIẾT CHECKBOX TAGS ĐÃ THAY THẾ:")
        print(f"{'-'*80}")
        for old_tag, count in sorted(total_checkbox_replacements.items(), key=lambda x: x[1], reverse=True):
            new_tag = CHECKBOX_TAG_MAPPING.get(old_tag, '???')
            print(f"  {old_tag:30s} → {new_tag:35s} ({count} lần)")

    if not total_text_replacements and not total_checkbox_replacements:
        print(f"\nℹ Không tìm thấy biến cũ hoặc checkbox tags nào cần thay thế")

    print(f"{'='*80}\n")


def print_mapping_table():
    """In bảng mapping để tham khảo"""
    print(f"\n{'='*100}")
    print(f"BẢNG MAPPING BIẾN CŨ → BIẾN MỚI (Tổng: {len(ALL_MAPPINGS)} biến)")
    print(f"{'='*100}")
    print(f"{'Biến cũ':<30} {'Biến mới':<40} {'Nhóm':<20}")
    print(f"{'-'*100}")

    # Phân loại biến
    categories = {
        'CHI NHÁNH': ['[ChiNhanh]', '[ChiNhanhHOA]', '[DiaChi]', '[DienThoai]', '[SoFax]',
                      '[DiaDanh]', '[MaSoThue]', '[MaCN]', '[USER]',
                      '[GiaoDichVien]', '[GDichVien]', '[KiemSoatVien]', '[KiemSoat]',
                      '[GiamDoc]', '[LanhDao]'],
        'TỰ ĐỘNG': ['[Ngay//]', '[NgayThangNam]', '[DateMonthYear]', '[So_HopDong]'],
        'KHÁCH HÀNG': ['[HotenKhachhangVN]', '[HotenKhachhangE]', '[NamSinh]', '[GioiTinh]',
                       '[DanToc]', '[SoDienThoai]', '[Email]', '[DiaChiKhachHang]', '[HoKhau]',
                       '[SoCMT]', '[NgayCMT]', '[NoiCapCMT]', '[NgayHetHan]',
                       '[MaSoKhachHang]', '[MaSoThueCN]'],
        'TÀI KHOẢN & THẺ': ['[SoTaiKhoan]', '[SoTheATM]', '[ThoiHanThe]', '[LoaiThe]',
                            '[LoaiPhi]', '[NgayTraThe]', '[TienTe]'],
        'VAY VỐN': ['[DoiTuongVay]', '[DuAnDauTu]', '[ThanhToan]', '[PhuongThucVay]',
                    '[HanMucTD_So]', '[HanMucTD_Chu]', '[NhuCauVon]', '[NhuCauVon_Chu]',
                    '[VonTienMat]', '[VonTaiSan_So]', '[VonTaiSan_Chu]',
                    '[VonSucLD_So]', '[VonSucLD_Chu]', '[VonDoiUng]', '[TyLe]',
                    '[ThuNhapKhac]', '[ThuNhapSXKD]', '[ThuNhapPhu]',
                    '[TongThuNhap_So]', '[TongThuNhap_Chu]',
                    '[ThoiGianVay]', '[LaiSuat]', '[LSQH]', '[SoKy]',
                    '[HanTraGoc]', '[HanTraLai]', '[QSDD]'],
        'DOANH NGHIỆP': ['[TenDoanhNghiep]', '[GiayDKKD]', '[NgDKKD]', '[NoiCapDKKD]',
                         '[MaSoThueDN]', '[NgayThue]', '[NoiCapThue]', '[NganhNgheKD]',
                         '[DiaChiDoanhNghiep]', '[UQGiaoDich]', '[NguoiUQ]', '[NgayUQ]',
                         '[ChucVu]', '[ThoiHanHDLD]'],
        'GIAO DỊCH': ['[SoTien]', '[SoTien_Chu]', '[SoTienPhi]', '[SoTienPhi_Chu]',
                      '[NgayGiaoDich]', '[TKChuyenSai]', '[MaGiaoDich]', '[NoiDung]'],
        'NGƯỜI NHẬN': ['[NguoiNhan]', '[NguoiThuHuong1]', '[DTNgNhan]', '[CMTNgNhan]',
                       '[NgCMTNgN]', '[NoiCMTNgN]', '[DiaChiKHNhan]', '[TKNHNhan]', '[NganHangNhan]'],
        'DỊCH VỤ': ['[ViDienTu]', '[ThuHo]', '[NhaCungCap]'],
        'POS/QR CODE': ['[CanBoQL]', '[DTCanBo]', '[UserCBQL]', '[EmailCBQL]',
                        '[ModelPOS]', '[MerchantID]', '[TerminalID]', '[SerialPOS]',
                        '[APos]', '[NPos]', '[VPos]', '[MPos]', '[JPos]', '[CPos]',
                        '[AQr]', '[NQr]', '[VQr]', '[MQr]', '[JQr]', '[CQr]',
                        '[TenCuaHang]', '[DiaChiCuaHang]'],
    }

    # In theo từng nhóm
    for category_name, var_list in categories.items():
        print(f"\n--- {category_name} ({len(var_list)} biến) ---")
        for old_var in var_list:
            if old_var in ALL_MAPPINGS:
                new_var = ALL_MAPPINGS[old_var]
                print(f"{old_var:<30} {new_var:<40} {category_name:<20}")

    # In các biến ngày tháng riêng
    print(f"\n--- NGÀY THÁNG (CHỮ SỐ) ({len(DATE_DIGIT_MAPPING)} biến) ---")
    for old_var in sorted(DATE_DIGIT_MAPPING.keys()):
        new_var = DATE_DIGIT_MAPPING[old_var]
        print(f"{old_var:<30} {new_var:<40} {'Ngày tháng':<20}")

    print(f"\n{'='*100}\n")
    print(f"TỔNG SỐ: {len(ALL_MAPPINGS)} biến đã được mapping")
    print(f"{'='*100}\n")


def main():
    """Main function"""
    print(f"\n{'*'*60}")
    print(f"  CÔNG CỤ CHUYỂN ĐỔI MẪU BIỂU TỰ ĐỘNG")
    print(f"  Agribank - Chi nhánh Giá Rai Bạc Liêu")
    print(f"{'*'*60}\n")

    # Check arguments
    if len(sys.argv) < 2:
        print("Cách sử dụng:")
        print(f"  python {sys.argv[0]} <thu_muc_mau_bieu> [thu_muc_output]")
        print(f"\nVí dụ:")
        print(f"  python {sys.argv[0]} ./mau_bieu_cu")
        print(f"  python {sys.argv[0]} ./mau_bieu_cu ./mau_bieu_moi")
        print(f"\nTùy chọn:")
        print(f"  --mapping : Hiển thị bảng mapping biến")

        if '--mapping' in sys.argv:
            print_mapping_table()

        return

    # Get paths
    input_folder = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else None

    # Confirm
    print(f"Folder input:  {os.path.abspath(input_folder)}")
    if output_folder:
        print(f"Folder output: {os.path.abspath(output_folder)}")
    else:
        print(f"Folder output: GHI ĐÈ FILE GỐC (có backup)")

    print(f"\nNhấn Enter để bắt đầu, hoặc Ctrl+C để hủy...")
    try:
        input()
    except KeyboardInterrupt:
        print(f"\n\n❌ Đã hủy bởi người dùng\n")
        return

    # Process
    process_folder(input_folder, output_folder, backup=True)

    print(f"\n✅ HOÀN THÀNH!\n")


if __name__ == '__main__':
    main()

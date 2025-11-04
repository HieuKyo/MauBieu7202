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

    # Save document
    doc.save(output_path)

    return replacements


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
    total_replacements = {}
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
            replacements = convert_document(input_path, output_path, backup)

            # Update statistics
            for var, count in replacements.items():
                total_replacements[var] = total_replacements.get(var, 0) + count

            if replacements:
                print(f"  ✓ Đã thay thế {sum(replacements.values())} biến")
            else:
                print(f"  ℹ Không tìm thấy biến cũ nào")

            successful += 1

        except Exception as e:
            print(f"  ❌ Lỗi: {str(e)}")
            failed += 1

        print()

    # Print summary
    print(f"\n{'='*60}")
    print(f"KẾT QUẢ CHUYỂN ĐỔI")
    print(f"{'='*60}")
    print(f"✓ Thành công: {successful} file")
    if failed > 0:
        print(f"❌ Thất bại: {failed} file")

    if total_replacements:
        print(f"\nCHI TIẾT CÁC BIẾN ĐÃ THAY THẾ:")
        print(f"{'-'*60}")
        for old_var, count in sorted(total_replacements.items(), key=lambda x: x[1], reverse=True):
            new_var = ALL_MAPPINGS[old_var]
            print(f"  {old_var:30s} → {new_var:25s} ({count} lần)")
    else:
        print(f"\nℹ Không tìm thấy biến cũ nào cần thay thế")

    print(f"{'='*60}\n")


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

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
# =====================================================
VARIABLE_MAPPING = {
    # Thông tin cá nhân
    '[HotenKhachhangVN]': '{{ ho_ten }}',
    '[HoTenKhachHang]': '{{ ho_ten }}',
    '[TenKhachHang]': '{{ ho_ten }}',
    '[NgaySinh]': '{{ ngay_sinh }}',
    '[GioiTinh]': '{{ gioi_tinh }}',

    # Giấy tờ tùy thân
    '[SoCMT]': '{{ so_cmnd }}',
    '[SoCMND]': '{{ so_cmnd }}',
    '[SoCCCD]': '{{ so_cmnd }}',
    '[NgayCMT]': '{{ ngay_cap_cmnd }}',
    '[NgayCapCMT]': '{{ ngay_cap_cmnd }}',
    '[NgayCapCMND]': '{{ ngay_cap_cmnd }}',
    '[NoiCapCMT]': '{{ noi_cap_cmnd }}',
    '[NoiCapCMND]': '{{ noi_cap_cmnd }}',
    '[NgayHetHanCMT]': '{{ ngay_het_han_cmnd }}',
    '[NgayHetHanCMND]': '{{ ngay_het_han_cmnd }}',

    # Thông tin liên hệ
    '[DiaChiKhachHang]': '{{ dia_chi }}',
    '[DiaChi]': '{{ dia_chi }}',
    '[SoDienThoai]': '{{ so_dien_thoai }}',
    '[DienThoai]': '{{ so_dien_thoai }}',
    '[Email]': '{{ email }}',

    # Thông tin nghề nghiệp
    '[NgheNghiep]': '{{ nghe_nghiep }}',
    '[NoiLamViec]': '{{ noi_lam_viec }}',

    # Thông tin tài khoản
    '[SoTaiKhoan]': '{{ so_tai_khoan }}',
    '[STK]': '{{ so_tai_khoan }}',
    '[LoaiTaiKhoan]': '{{ loai_tai_khoan }}',
    '[LoaiTienTe]': '{{ loai_tien_te }}',

    # Thông tin thẻ
    '[LoaiThe]': '{{ loai_the }}',
    '[HangThe]': '{{ hang_the }}',

    # Thông tin chi nhánh
    '[TenChiNhanh]': '{{ ten_chi_nhanh }}',
    '[TenChiNhanhHoa]': '{{ ten_chi_nhanh_hoa }}',
    '[MaSoThue]': '{{ mst }}',
    '[GiaoDichVien]': '{{ giao_dich_vien }}',
    '[KiemSoatVien]': '{{ kiem_soat_vien }}',
    '[GiamDoc]': '{{ giam_doc }}',
    '[DiaChiChiNhanh]': '{{ dia_chi_chi_nhanh }}',

    # Ngày in/lập
    '[NgayIn]': '{{ ngay_in }}',
    '[NgayLap]': '{{ ngay_lap }}',

    # Mã khách hàng
    '[MaKhachHang]': '{{ ma_khach_hang }}',
    '[CIF]': '{{ cif }}',
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
    print(f"\n{'='*80}")
    print(f"BẢNG MAPPING BIẾN CŨ → BIẾN MỚI")
    print(f"{'='*80}")
    print(f"{'Biến cũ':<35} {'Biến mới':<35} {'Mô tả':<20}")
    print(f"{'-'*80}")

    descriptions = {
        '[HotenKhachhangVN]': 'Họ tên',
        '[SoCMT]': 'Số CMND/CCCD',
        '[NgayCMT]': 'Ngày cấp',
        '[NoiCapCMT]': 'Nơi cấp',
        '[DiaChiKhachHang]': 'Địa chỉ',
        '[SoDienThoai]': 'Số điện thoại',
        '[SoTaiKhoan]': 'Số tài khoản',
        '[TenChiNhanh]': 'Tên chi nhánh',
        '[GiaoDichVien]': 'Giao dịch viên',
    }

    for old_var in sorted(VARIABLE_MAPPING.keys()):
        new_var = VARIABLE_MAPPING[old_var]
        desc = descriptions.get(old_var, '')
        print(f"{old_var:<35} {new_var:<35} {desc:<20}")

    print(f"{'='*80}\n")


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

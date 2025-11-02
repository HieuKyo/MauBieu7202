"""
Script import khách hàng từ file TSV (clipboard AGRIBANK)
"""
import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.insert(0, '/home/user/MauBieu7202')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wordgen.settings')
django.setup()

from templates_app.models import Customer
from templates_app.issueby_mapping import get_issueby_name
from django.contrib.auth.models import User


def parse_date(date_str):
    """
    Convert date from YYYYMMDD to YYYY-MM-DD
    Args:
        date_str: Date string in YYYYMMDD format
    Returns:
        Date string in YYYY-MM-DD format or None
    """
    if not date_str or date_str.strip() == '' or len(date_str) < 8:
        return None

    try:
        # Remove spaces
        date_str = date_str.strip()
        if len(date_str) == 8:
            year = date_str[:4]
            month = date_str[4:6]
            day = date_str[6:8]
            # Validate date
            datetime.strptime(f"{year}-{month}-{day}", '%Y-%m-%d')
            return f"{year}-{month}-{day}"
    except (ValueError, IndexError):
        pass

    return None


def clean_value(value):
    """Clean whitespace from value"""
    if value is None:
        return ''
    return str(value).strip()


def import_from_tsv(tsv_file_path, created_by_username='admin'):
    """
    Import customers from TSV file

    Args:
        tsv_file_path: Path to TSV file
        created_by_username: Username of user who imports data

    Returns:
        Tuple of (success_count, error_count, errors_list)
    """
    try:
        # Get or create user
        try:
            created_by = User.objects.get(username=created_by_username)
        except User.DoesNotExist:
            created_by = User.objects.filter(is_superuser=True).first()
            if not created_by:
                return 0, 0, ['Không tìm thấy user để gán created_by']

        with open(tsv_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if len(lines) < 2:
            return 0, 0, ['File không có dữ liệu']

        # Parse header
        header = lines[0].strip().split('\t')

        success_count = 0
        error_count = 0
        errors = []

        # Process each data line
        for line_num, line in enumerate(lines[1:], start=2):
            try:
                values = line.strip().split('\t')

                # Create dict from header and values
                data = {}
                for i, field in enumerate(header):
                    data[field] = values[i] if i < len(values) else ''

                # Extract and map fields
                custno = clean_value(data.get('custno', ''))
                nmloc = clean_value(data.get('nmloc', ''))
                regno = clean_value(data.get('regno', ''))

                # Validate required fields
                if not nmloc:
                    errors.append(f'Dòng {line_num}: Thiếu họ tên')
                    error_count += 1
                    continue

                if not regno:
                    errors.append(f'Dòng {line_num}: Thiếu số CMND/CCCD')
                    error_count += 1
                    continue

                # Check if customer already exists
                if Customer.objects.filter(so_cmnd=regno).exists():
                    # Update existing customer
                    customer = Customer.objects.get(so_cmnd=regno)
                    update_mode = True
                else:
                    # Create new customer
                    customer = Customer(created_by=created_by)
                    update_mode = False

                # Map fields
                customer.ma_khach_hang = custno
                customer.cif = custno if custno else None
                customer.ho_ten = nmloc
                customer.so_cmnd = regno

                # Parse dates
                ngay_sinh = parse_date(data.get('name_1', ''))
                if ngay_sinh:
                    customer.ngay_sinh = ngay_sinh

                ngay_cap = parse_date(data.get('issuedt1', ''))
                if ngay_cap:
                    customer.ngay_cap_cmnd = ngay_cap

                # Gender
                gioi_tinh = clean_value(data.get('name_3', ''))
                if gioi_tinh:
                    customer.gioi_tinh = gioi_tinh

                # Phone
                so_dien_thoai = clean_value(data.get('name_4', ''))
                if so_dien_thoai:
                    customer.so_dien_thoai = so_dien_thoai

                # Address
                dia_chi = clean_value(data.get('addr1loc', ''))
                if dia_chi:
                    customer.dia_chi = dia_chi

                # Issueby
                issueby_code = clean_value(data.get('issueby1', ''))
                if issueby_code:
                    customer.ma_noi_cap_cmnd = issueby_code
                    issueby_name = get_issueby_name(issueby_code)
                    # Try to match with existing choices
                    if 'Cục' in issueby_name or 'CSQLHC' in issueby_name:
                        customer.noi_cap_cmnd = 'Cục CSQLHC về TTXH'
                    elif 'Bộ Công An' in issueby_name:
                        customer.noi_cap_cmnd = 'Bộ Công An'
                    else:
                        customer.noi_cap_cmnd = 'Khác'
                    customer.noi_cap_cmnd_custom = issueby_name

                # Profession
                profnm = clean_value(data.get('profnm', ''))
                if profnm:
                    customer.nghe_nghiep = profnm

                # Email
                email = clean_value(data.get('emailaddr', ''))
                if email:
                    customer.email = email

                # Administrative codes
                ma_tinh = clean_value(data.get('province', ''))
                if ma_tinh:
                    customer.ma_tinh = ma_tinh

                ma_quan_huyen = clean_value(data.get('district', ''))
                if ma_quan_huyen:
                    customer.ma_quan_huyen = ma_quan_huyen

                ma_phuong_xa = clean_value(data.get('commune_ward', ''))
                if ma_phuong_xa:
                    customer.ma_phuong_xa = ma_phuong_xa

                # Nationality
                quoc_tich = clean_value(data.get('ctrycdnatl', ''))
                if quoc_tich:
                    customer.quoc_tich = quoc_tich

                # Tax code
                ma_so_thue = clean_value(data.get('taxno', ''))
                if ma_so_thue:
                    customer.ma_so_thue = ma_so_thue

                # Passport
                so_ho_chieu = clean_value(data.get('passno', ''))
                if so_ho_chieu:
                    customer.so_ho_chieu = so_ho_chieu

                # Save customer
                customer.save()

                success_count += 1
                if update_mode:
                    print(f"✓ Đã cập nhật: {customer.ho_ten} ({regno})")
                else:
                    print(f"✓ Đã thêm: {customer.ho_ten} ({regno})")

            except Exception as e:
                error_count += 1
                error_msg = f'Dòng {line_num}: Lỗi - {str(e)}'
                errors.append(error_msg)
                print(f"✗ {error_msg}")
                continue

        return success_count, error_count, errors

    except Exception as e:
        return 0, 0, [f'Lỗi đọc file: {str(e)}']


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Import khách hàng từ file TSV')
    parser.add_argument('file', help='Đường dẫn đến file TSV')
    parser.add_argument('--user', default='admin', help='Username của người import (default: admin)')

    args = parser.parse_args()

    print("=" * 80)
    print("IMPORT KHÁCH HÀNG TỪ FILE TSV")
    print("=" * 80)
    print(f"File: {args.file}")
    print(f"User: {args.user}")
    print("=" * 80)

    success, errors_count, errors = import_from_tsv(args.file, args.user)

    print("\n" + "=" * 80)
    print("KẾT QUẢ IMPORT")
    print("=" * 80)
    print(f"✓ Thành công: {success} khách hàng")
    print(f"✗ Lỗi: {errors_count} dòng")

    if errors:
        print("\nChi tiết lỗi:")
        for error in errors:
            print(f"  - {error}")

    print("=" * 80)

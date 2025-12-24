"""
Management command để import dữ liệu từ file Excel/CSV vào database
Sử dụng: python manage.py import_tax_data --locations <path> --subentries <path>
"""
import os
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from tax_payment.models import TaxLocation, TaxSubEntry


class Command(BaseCommand):
    help = 'Import dữ liệu Cơ quan thu và Tiểu mục từ file Excel/CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--locations',
            type=str,
            help='Đường dẫn đến file CO QUAN THU.xlsx hoặc .csv'
        )
        parser.add_argument(
            '--subentries',
            type=str,
            help='Đường dẫn đến file MA TIEU MUC.xlsx hoặc .csv'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Xóa toàn bộ dữ liệu cũ trước khi import'
        )

    def handle(self, *args, **options):
        locations_file = options.get('locations')
        subentries_file = options.get('subentries')
        clear_data = options.get('clear', False)

        if not locations_file and not subentries_file:
            raise CommandError('Vui lòng cung cấp ít nhất một file để import (--locations hoặc --subentries)')

        # Import Cơ quan thu
        if locations_file:
            self.import_tax_locations(locations_file, clear_data)

        # Import Tiểu mục
        if subentries_file:
            self.import_tax_subentries(subentries_file, clear_data)

        self.stdout.write(self.style.SUCCESS('Import dữ liệu thành công!'))

    def import_tax_locations(self, file_path, clear_data=False):
        """Import dữ liệu Cơ quan thu từ file Excel/CSV"""
        if not os.path.exists(file_path):
            raise CommandError(f'File không tồn tại: {file_path}')

        self.stdout.write(f'Đang import Cơ quan thu từ: {file_path}')

        # Đọc file Excel hoặc CSV
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        else:
            df = pd.read_excel(file_path)

        # Chuẩn hóa tên cột (loại bỏ khoảng trắng thừa)
        df.columns = df.columns.str.strip()

        # Mapping các tên cột có thể có
        column_mapping = {
            'Tỉnh': 'tinh',
            'Cơ quan thuế': 'co_quan_thue',
            'Xã': 'xa',
            'Mã cơ quan thu': 'ma_co_quan_thu',
            'Tên cơ quan thu': 'ten_co_quan_thu',
            'KBNN': 'kbnn',
            'Mã DB': 'ma_db'
        }

        # Kiểm tra các cột cần thiết
        required_columns = set(column_mapping.keys())
        actual_columns = set(df.columns)
        missing_columns = required_columns - actual_columns

        if missing_columns:
            self.stdout.write(self.style.WARNING(f'Các cột trong file: {list(df.columns)}'))
            self.stdout.write(self.style.WARNING(f'Thiếu các cột: {missing_columns}'))
            self.stdout.write(self.style.WARNING('Đang thử tự động mapping...'))

        # Xóa dữ liệu cũ nếu cần
        if clear_data:
            deleted_count = TaxLocation.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f'Đã xóa {deleted_count} bản ghi cũ'))

        # Import dữ liệu
        created_count = 0
        updated_count = 0
        error_count = 0

        for index, row in df.iterrows():
            try:
                # Lấy dữ liệu từng cột (xử lý NaN)
                tinh = str(row.get('Tỉnh', '')).strip() if pd.notna(row.get('Tỉnh')) else ''
                co_quan_thue = str(row.get('Cơ quan thuế', '')).strip() if pd.notna(row.get('Cơ quan thuế')) else ''
                xa = str(row.get('Xã', '')).strip() if pd.notna(row.get('Xã')) else ''
                ma_co_quan_thu = str(row.get('Mã cơ quan thu', '')).strip() if pd.notna(row.get('Mã cơ quan thu')) else ''
                ten_co_quan_thu = str(row.get('Tên cơ quan thu', '')).strip() if pd.notna(row.get('Tên cơ quan thu')) else ''
                kbnn = str(row.get('KBNN', '')).strip() if pd.notna(row.get('KBNN')) else ''
                ma_db = str(row.get('Mã DB', '')).strip() if pd.notna(row.get('Mã DB')) else ''

                # Bỏ qua dòng trống
                if not ma_co_quan_thu:
                    continue

                # Update hoặc Create
                obj, created = TaxLocation.objects.update_or_create(
                    ma_co_quan_thu=ma_co_quan_thu,
                    defaults={
                        'tinh': tinh,
                        'co_quan_thue_group': co_quan_thue,
                        'xa_phuong': xa,
                        'ten_co_quan_thu': ten_co_quan_thu,
                        'kho_bac': kbnn,
                        'ma_dia_ban': ma_db
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'Lỗi dòng {index + 2}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(
            f'Cơ quan thu - Tạo mới: {created_count}, Cập nhật: {updated_count}, Lỗi: {error_count}'
        ))

    def import_tax_subentries(self, file_path, clear_data=False):
        """Import dữ liệu Tiểu mục từ file Excel/CSV"""
        if not os.path.exists(file_path):
            raise CommandError(f'File không tồn tại: {file_path}')

        self.stdout.write(f'Đang import Tiểu mục từ: {file_path}')

        # Đọc file Excel hoặc CSV
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        else:
            df = pd.read_excel(file_path)

        # Chuẩn hóa tên cột
        df.columns = df.columns.str.strip()

        # Xóa dữ liệu cũ nếu cần
        if clear_data:
            deleted_count = TaxSubEntry.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f'Đã xóa {deleted_count} bản ghi cũ'))

        # Import dữ liệu
        created_count = 0
        updated_count = 0
        error_count = 0

        for index, row in df.iterrows():
            try:
                # Lấy dữ liệu (các tên cột có thể khác nhau)
                ma_tieu_muc = None
                ten_tieu_muc = None

                # Thử các tên cột có thể có
                for col in df.columns:
                    if 'mã' in col.lower() and 'tiểu mục' in col.lower():
                        ma_tieu_muc = str(row[col]).strip() if pd.notna(row[col]) else ''
                    elif 'tên' in col.lower() or 'gọi' in col.lower():
                        ten_tieu_muc = str(row[col]).strip() if pd.notna(row[col]) else ''

                # Fallback nếu không tìm thấy cột
                if not ma_tieu_muc and 'Mã số Tiểu mục' in df.columns:
                    ma_tieu_muc = str(row['Mã số Tiểu mục']).strip() if pd.notna(row['Mã số Tiểu mục']) else ''
                if not ten_tieu_muc and 'TÊN GỌI' in df.columns:
                    ten_tieu_muc = str(row['TÊN GỌI']).strip() if pd.notna(row['TÊN GỌI']) else ''

                # Bỏ qua dòng trống
                if not ma_tieu_muc or not ten_tieu_muc:
                    continue

                # Update hoặc Create
                obj, created = TaxSubEntry.objects.update_or_create(
                    ma_tieu_muc=ma_tieu_muc,
                    defaults={
                        'ten_tieu_muc': ten_tieu_muc
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'Lỗi dòng {index + 2}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(
            f'Tiểu mục - Tạo mới: {created_count}, Cập nhật: {updated_count}, Lỗi: {error_count}'
        ))

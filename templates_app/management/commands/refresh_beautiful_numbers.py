"""
Tính lại category/price_tier/fee cho toàn bộ BeautifulNumber theo engine tính phí mới
(beautiful_number_services V3.0), sau khi engine được cập nhật đầy đủ mẫu số đẹp hơn
theo Phụ lục 02 QĐ 479. Không xóa/thêm bản ghi nào, chỉ cập nhật 3 field trên.
"""
from django.core.management.base import BaseCommand

from templates_app.beautiful_number_generator import refresh_all_beautiful_numbers


class Command(BaseCommand):
    help = 'Cập nhật lại category/price_tier/fee cho toàn bộ số đẹp trong kho theo engine tính phí mới'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Chỉ in ra thay đổi, không lưu vào DB',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        self.stdout.write(f'Đang xử lý...')

        stats = refresh_all_beautiful_numbers(dry_run=dry_run)

        self.stdout.write(
            f'Tổng {stats["total"]} số. Thay đổi: {stats["changed_fee"]} số đổi fee, '
            f'{stats["changed_tier"]} số đổi price_tier, {stats["changed_category"]} số nâng lên Đặc biệt. '
            f'Bỏ qua (lỗi): {stats["errors"]}.'
        )

        if dry_run:
            self.stdout.write(self.style.WARNING('Dry-run: chưa lưu vào DB.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Đã cập nhật {stats["updated"]} số đẹp.'))

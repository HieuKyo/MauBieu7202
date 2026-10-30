from django.core.management.base import BaseCommand
from django.db import transaction
from payroll_statistics.models import PayingUnit, BeneficiaryAccount, Transaction


class Command(BaseCommand):
    help = 'Xóa các PayingUnit không hợp lệ (không match pattern 7202201xxx hoặc 7202000xxx)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Chỉ hiển thị những gì sẽ bị xóa, không thực sự xóa',
        )
        parser.add_argument(
            '--exclude',
            type=str,
            help='Danh sách STK cần loại trừ (ngăn cách bởi dấu phẩy)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        exclude_list = []
        if options['exclude']:
            exclude_list = [acc.strip() for acc in options['exclude'].split(',')]

        self.stdout.write('=' * 80)
        self.stdout.write('Kiểm tra PayingUnit không hợp lệ...')
        self.stdout.write('=' * 80)

        # Tìm tất cả PayingUnit không match pattern
        all_units = PayingUnit.objects.all()
        invalid_units = []

        for unit in all_units:
            acc = unit.account_number.strip()
            # Kiểm tra pattern hợp lệ
            if not (acc.startswith('7202201') or acc.startswith('7202000')):
                # Kiểm tra exclude list
                if acc not in exclude_list:
                    invalid_units.append(unit)

        if not invalid_units:
            self.stdout.write(self.style.SUCCESS('\n✓ Không tìm thấy PayingUnit không hợp lệ!'))
            return

        self.stdout.write(f'\nTìm thấy {len(invalid_units)} PayingUnit không hợp lệ:\n')

        # Thống kê chi tiết
        stats = []
        for unit in invalid_units:
            beneficiary_count = BeneficiaryAccount.objects.filter(unit=unit).count()
            transaction_count = Transaction.objects.filter(unit=unit).count()
            stats.append({
                'account': unit.account_number,
                'name': unit.name or '(Chưa có tên)',
                'beneficiaries': beneficiary_count,
                'transactions': transaction_count,
            })

        # Hiển thị danh sách
        for s in stats:
            self.stdout.write(
                f"  • {s['account']:<20} | {s['name']:<30} | "
                f"NV: {s['beneficiaries']:<5} | GD: {s['transactions']}"
            )

        total_beneficiaries = sum(s['beneficiaries'] for s in stats)
        total_transactions = sum(s['transactions'] for s in stats)

        self.stdout.write('\n' + '-' * 80)
        self.stdout.write('Tổng cộng:')
        self.stdout.write(f'  - PayingUnit sẽ xóa: {len(invalid_units)}')
        self.stdout.write(f'  - BeneficiaryAccount sẽ xóa: {total_beneficiaries}')
        self.stdout.write(f'  - Transaction sẽ xóa: {total_transactions}')
        self.stdout.write('-' * 80)

        if dry_run:
            self.stdout.write(self.style.WARNING('\n[DRY RUN] Không thực hiện xóa.'))
            self.stdout.write('Chạy lại không có --dry-run để thực sự xóa.\n')
        else:
            # Xác nhận
            confirm = input('\nBạn có chắc chắn muốn XÓA các PayingUnit này? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Đã hủy.'))
                return

            # Xóa trong transaction
            with transaction.atomic():
                deleted_count = 0
                for unit in invalid_units:
                    unit.delete()  # Cascade sẽ tự động xóa BeneficiaryAccount và Transaction
                    deleted_count += 1

            self.stdout.write(self.style.SUCCESS(f'\n✓ Đã xóa {deleted_count} PayingUnit không hợp lệ!'))

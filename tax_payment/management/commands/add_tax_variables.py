"""
Management command để thêm các biến mới của Tax Payment vào Thư viện biến
"""
from django.core.management.base import BaseCommand
from templates_app.models import Variable


class Command(BaseCommand):
    help = 'Thêm các biến Tax Payment vào Thư viện biến'

    def handle(self, *args, **options):
        # Danh sách các biến mới cho Tax Payment
        tax_variables = [
            # Thông tin người nộp thuế
            {
                'name': 'ten_nguoi_nop_thue',
                'label': 'Tên người nộp thuế',
                'field_type': 'text',
                'help_text': 'Tên đầy đủ của người nộp thuế',
                'required': True,
                'default_value': ''
            },
            {
                'name': 'ma_so_thue',
                'label': 'Mã số thuế',
                'field_type': 'text',
                'help_text': 'Mã số thuế của người nộp',
                'required': False,
                'default_value': ''
            },
            {
                'name': 'dia_chi_nguoi_nop_thue',
                'label': 'Địa chỉ người nộp thuế',
                'field_type': 'textarea',
                'help_text': 'Địa chỉ liên hệ của người nộp thuế',
                'required': False,
                'default_value': ''
            },
            {
                'name': 'ngay_lap_bang_ke',
                'label': 'Ngày lập bảng kê thuế',
                'field_type': 'date',
                'help_text': 'Ngày lập bảng kê nộp thuế',
                'required': True,
                'default_value': ''
            },
            {
                'name': 'ngay_thang_nam_text',
                'label': 'Ngày tháng năm (dạng chữ)',
                'field_type': 'text',
                'help_text': 'Ngày lập bảng kê dạng chữ (VD: Ngày 24 tháng 12 năm 2025)',
                'required': False,
                'default_value': ''
            },
            {
                'name': 'nguoi_nop_thay',
                'label': 'Người nộp thay',
                'field_type': 'text',
                'help_text': 'Tên người đại diện nộp thuế thay',
                'required': False,
                'default_value': ''
            },

            # Thông tin cơ quan thu
            {
                'name': 'tinh_thanh_pho',
                'label': 'Tỉnh/Thành phố (Cơ quan thu)',
                'field_type': 'text',
                'help_text': 'Tên tỉnh/thành phố nơi nộp thuế',
                'required': False,
                'default_value': ''
            },
            {
                'name': 'co_quan_thue',
                'label': 'Cơ quan thuế',
                'field_type': 'text',
                'help_text': 'Tên cơ quan thuế quản lý',
                'required': False,
                'default_value': ''
            },
            {
                'name': 'xa_phuong_nop_thue',
                'label': 'Xã/Phường (Cơ quan thu)',
                'field_type': 'text',
                'help_text': 'Xã/Phường nơi cơ quan thu đặt trụ sở',
                'required': False,
                'default_value': ''
            },
            {
                'name': 'ma_co_quan_thu',
                'label': 'Mã cơ quan thu',
                'field_type': 'text',
                'help_text': 'Mã định danh của cơ quan thu thuế',
                'required': False,
                'default_value': ''
            },
            {
                'name': 'ten_co_quan_thu',
                'label': 'Tên cơ quan thu (đầy đủ)',
                'field_type': 'textarea',
                'help_text': 'Tên đầy đủ của cơ quan thu thuế',
                'required': False,
                'default_value': ''
            },
            {
                'name': 'ma_dia_ban',
                'label': 'Mã địa bàn hành chính',
                'field_type': 'text',
                'help_text': 'Mã địa bàn hành chính nơi nộp thuế',
                'required': False,
                'default_value': ''
            },
            {
                'name': 'kho_bac_nha_nuoc',
                'label': 'Kho bạc nhà nước (KBNN)',
                'field_type': 'text',
                'help_text': 'Tên Kho bạc nhà nước nơi nộp thuế',
                'required': False,
                'default_value': ''
            },

            # Thông tin tổng hợp
            {
                'name': 'tong_so_tien_nop_thue',
                'label': 'Tổng số tiền nộp thuế',
                'field_type': 'number',
                'help_text': 'Tổng số tiền nộp thuế (VNĐ)',
                'required': False,
                'default_value': '0'
            },
            {
                'name': 'so_tien_bang_chu',
                'label': 'Số tiền bằng chữ',
                'field_type': 'text',
                'help_text': 'Tổng số tiền viết bằng chữ (tiếng Việt)',
                'required': False,
                'default_value': ''
            },

            # Thông tin tiểu mục (có thể dùng cho loop)
            {
                'name': 'ma_tieu_muc_thue',
                'label': 'Mã tiểu mục thuế',
                'field_type': 'text',
                'help_text': 'Mã tiểu mục khoản nộp thuế',
                'required': False,
                'default_value': ''
            },
            {
                'name': 'noi_dung_tieu_muc',
                'label': 'Nội dung tiểu mục thuế',
                'field_type': 'textarea',
                'help_text': 'Nội dung/diễn giải khoản nộp thuế',
                'required': False,
                'default_value': ''
            },
            {
                'name': 'so_tien_tieu_muc',
                'label': 'Số tiền tiểu mục',
                'field_type': 'number',
                'help_text': 'Số tiền của từng khoản nộp (VNĐ)',
                'required': False,
                'default_value': '0'
            },
        ]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for var_data in tax_variables:
            try:
                obj, created = Variable.objects.update_or_create(
                    name=var_data['name'],
                    defaults={
                        'label': var_data['label'],
                        'field_type': var_data['field_type'],
                        'help_text': var_data['help_text'],
                        'required': var_data['required'],
                        'default_value': var_data['default_value']
                    }
                )

                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'✓ Đã tạo biến mới: {var_data["name"]}'))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f'↻ Đã cập nhật biến: {var_data["name"]}'))

            except Exception as e:
                skipped_count += 1
                self.stdout.write(self.style.ERROR(f'✗ Lỗi với biến {var_data["name"]}: {str(e)}'))

        # Tổng kết
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'Đã tạo mới: {created_count} biến'))
        self.stdout.write(self.style.WARNING(f'Đã cập nhật: {updated_count} biến'))
        if skipped_count > 0:
            self.stdout.write(self.style.ERROR(f'Bỏ qua (lỗi): {skipped_count} biến'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Hoàn tất cập nhật Thư viện biến!'))

from django.core.management.base import BaseCommand
from templates_app.models import Variable

class Command(BaseCommand):
    help = 'Thêm các biến module Thuế vào thư viện'

    def handle(self, *args, **options):
        # Danh sách biến cần thêm
        vars_to_add = [
            # Thông tin người nộp
            {'name': 'ten_nguoi_nop', 'desc': 'Tên người nộp thuế'},
            {'name': 'ma_so_thue', 'desc': 'Mã số thuế người nộp'},
            {'name': 'dia_chi', 'desc': 'Địa chỉ người nộp'},
            {'name': 'ngay_lap', 'desc': 'Ngày lập bảng kê (dd/mm/yyyy)'},
            
            # Thông tin Cơ quan thu
            {'name': 'tinh', 'desc': 'Tên Tỉnh/Thành phố nộp thuế'},
            {'name': 'co_quan_thue', 'desc': 'Tên nhóm Cơ quan thuế'},
            {'name': 'xa_phuong', 'desc': 'Tên Xã/Phường'},
            {'name': 'ma_co_quan_thu', 'desc': 'Mã số định danh cơ quan thu'},
            {'name': 'ten_co_quan_thu', 'desc': 'Tên đầy đủ cơ quan thu'},
            {'name': 'ma_dia_ban', 'desc': 'Mã địa bàn hành chính'},
            {'name': 'kho_bac', 'desc': 'Tên Kho bạc nhà nước (KBNN)'},
            
            # Tài chính & Bảng
            {'name': 'tong_so_tien', 'desc': 'Tổng số tiền nộp (đã format)'},
            {'name': 'so_tien_bang_chu', 'desc': 'Số tiền bằng chữ'},
            
            # Các biến trong vòng lặp (Chỉ mang tính chất tham khảo cho thư viện)
            {'name': 'items', 'desc': 'Danh sách các khoản nộp (Vòng lặp)'},
            {'name': 'item.stt', 'desc': 'Số thứ tự dòng (trong lặp items)'},
            {'name': 'item.ma_tieu_muc', 'desc': 'Mã tiểu mục (trong lặp items)'},
            {'name': 'item.noi_dung', 'desc': 'Nội dung khoản nộp (trong lặp items)'},
            {'name': 'item.so_tien', 'desc': 'Số tiền từng khoản (trong lặp items)'},
        ]

        count = 0
        for var in vars_to_add:
            # Map dữ liệu vào đúng trường của Model Variable
            # name -> name
            # desc -> label (nhãn hiển thị)
            # desc -> help_text (gợi ý/mô tả chi tiết)
            
            obj, created = Variable.objects.get_or_create(
                name=var['name'],
                defaults={
                    'label': var['desc'],      # Sửa ở đây
                    'help_text': var['desc'],  # Sửa ở đây
                    'field_type': 'text',      # Mặc định là text
                    'required': False          # Không bắt buộc
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'+ Đã thêm: {var["name"]}'))
                count += 1
            else:
                # Nếu đã tồn tại, cập nhật lại mô tả
                obj.label = var['desc']
                obj.help_text = var['desc']
                obj.save()
                self.stdout.write(f'* Đã cập nhật: {var["name"]}')

        self.stdout.write(self.style.SUCCESS(f'Hoàn tất! Đã xử lý {count} biến mới.'))
"""
Tạo mẫu "Phát hành thẻ Học sinh": dùng chung file Word của Mẫu 1A, chọn sẵn thông tin thẻ học sinh
(không có trường bắt buộc thêm). Chỉnh lại được trong Admin → Mẫu biểu → "Nhập nhanh".
"""
from django.db import migrations

NAME = 'Phát hành thẻ Học sinh (Mẫu 1A)'
MAU_1A_FILE = 'templates/docx/NHOM_MO_TAI_KHOAN_-_1032_TK_LAN_DAU_-_PHT_R.docx'
PRESET = {
    'nghe_nghiep': 'Học sinh/Sinh viên',
    'loai_tai_khoan': 'Tài khoản ngẫu nhiên',
    'loai_tien_te': 'VND',
    'loai_the': 'Thẻ Ghi nợ nội địa',
    'hang_the': 'Hạng chuẩn',
    'phat_hanh_lan_dau': True,
    'ket_qua_phan_loai_kh': 'Trung bình',
}
REQUIRED = []


def create_student_card_template(apps, schema_editor):
    Template = apps.get_model('templates_app', 'Template')
    if Template.objects.filter(name=NAME).exists():
        return
    base = (Template.objects.filter(name__startswith='Mẫu 1A').order_by('id').first()
            or Template.objects.filter(file=MAU_1A_FILE).order_by('id').first())
    if base is None:
        return   # máy chưa có Mẫu 1A → tạo tay trong Admin nếu cần
    t = Template.objects.create(
        category=base.category,
        name=NAME,
        description='Mẫu 1A chọn sẵn thông tin thẻ cho học sinh.',
        file=base.file.name,
        order=base.order,
        is_active=True,
        preset_values=PRESET,
        required_fields=REQUIRED,
    )
    t.allowed_groups.set(base.allowed_groups.all())


def remove_student_card_template(apps, schema_editor):
    apps.get_model('templates_app', 'Template').objects.filter(name=NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('templates_app', '0085_template_preset_required'),
    ]

    operations = [
        migrations.RunPython(create_student_card_template, remove_student_card_template),
    ]

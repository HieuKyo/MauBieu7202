from django.db import migrations


def tao_bang_neu_thieu(apps, schema_editor):
    """Một số DB đã đánh dấu chạy 0033 nhưng không có 2 bảng này → trang Bì thư lỗi 500. Tạo lại nếu thiếu."""
    tables = schema_editor.connection.introspection.table_names()
    for name in ('MailEnvelopeTracking', 'ReportConfiguration'):
        model = apps.get_model('templates_app', name)
        if model._meta.db_table not in tables:
            schema_editor.create_model(model)


class Migration(migrations.Migration):

    dependencies = [
        ('templates_app', '0093_qr_da_in'),
    ]

    operations = [
        migrations.RunPython(tao_bang_neu_thieu, migrations.RunPython.noop),
    ]

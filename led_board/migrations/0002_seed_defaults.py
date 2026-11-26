from django.db import migrations


def seed(apps, schema_editor):
    ExchangeRate = apps.get_model('led_board', 'ExchangeRate')
    BoardSetting = apps.get_model('led_board', 'BoardSetting')
    ExchangeRate.objects.get_or_create(code='USD', defaults={'order': 1})
    ExchangeRate.objects.get_or_create(code='EUR', defaults={'order': 2})
    BoardSetting.objects.get_or_create(pk=1)


class Migration(migrations.Migration):

    dependencies = [
        ('led_board', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]

# Generated migration to add ten_the_2 field to Customer model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('templates_app', '0015_add_new_variables_to_library'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='ten_the_2',
            field=models.CharField(blank=True, max_length=200, verbose_name='Tên thẻ 2'),
        ),
    ]

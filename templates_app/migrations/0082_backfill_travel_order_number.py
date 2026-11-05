from django.db import migrations
from collections import defaultdict


def backfill_travel_order_number(apps, schema_editor):
    """
    Đánh số lại các phiếu tiếp quỹ ATM đã có sẵn, theo thứ tự thời gian, đánh riêng cho
    từng năm (năm nào đánh số từ 1 của năm đó) — dựa hoàn toàn trên dữ liệu thực tế đang có
    trong database tại thời điểm chạy migration, không hard-code số lượng cụ thể. Khi chạy
    trên bất kỳ database nào (máy dev hay hệ thống thật), số lượng bản ghi và do đó số cuối
    cùng sẽ tự động khớp đúng với dữ liệu thực tế của database đó.
    """
    ATMReplenishment = apps.get_model('templates_app', 'ATMReplenishment')
    qs = ATMReplenishment.objects.filter(
        travel_order_number__isnull=True
    ).order_by('replenishment_date', 'created_at', 'pk')

    counters = defaultdict(int)
    for obj in qs:
        year = obj.replenishment_date.year
        counters[year] += 1
        obj.travel_order_number = counters[year]
        obj.travel_order_year = year
        obj.save(update_fields=['travel_order_number', 'travel_order_year'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('templates_app', '0081_atmreplenishment_travel_order_year_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_travel_order_number, noop_reverse),
    ]

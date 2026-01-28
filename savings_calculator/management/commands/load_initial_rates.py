"""
Management command: Nạp dữ liệu lãi suất Agribank ban đầu.
Chạy: python manage.py load_initial_rates
"""

from datetime import date
from django.core.management.base import BaseCommand
from savings_calculator.models import SavingsProduct, InterestRate


PRODUCTS = [
    {
        "code": "TK_TRA_LAI_SAU",
        "name": "Tiết kiệm có kỳ hạn - Trả lãi sau",
        "description": "Sản phẩm tiết kiệm có kỳ hạn trả lãi cuối kỳ.",
        "order": 1,
        "rates": [
            (1, 2, 2.6, "1 đến 2 tháng"),
            (3, 5, 2.9, "3 đến 5 tháng"),
            (6, 11, 4.0, "6 đến 11 tháng"),
            (12, 17, 5.2, "12 đến 17 tháng"),
            (18, 23, 5.2, "18 đến 23 tháng"),
            (24, 24, 5.3, "24 tháng"),
        ],
    },
    {
        "code": "TK_RUT_GOC_LINH_HOAT",
        "name": "Tiết kiệm rút gốc linh hoạt",
        "description": "Tiết kiệm cho phép rút gốc linh hoạt, lãi suất thấp hơn ~0.1%.",
        "order": 2,
        "rates": [
            (1, 2, 2.5, "1 đến 2 tháng"),
            (3, 5, 2.8, "3 đến 5 tháng"),
            (6, 11, 3.9, "6 đến 11 tháng"),
            (12, 17, 5.1, "12 đến 17 tháng"),
            (18, 23, 5.1, "18 đến 23 tháng"),
            (24, 24, 5.2, "24 tháng"),
        ],
    },
    {
        "code": "TK_TRA_LAI_DINH_KY",
        "name": "Tiết kiệm trả lãi định kỳ hàng tháng",
        "description": "Trả lãi định kỳ hàng tháng, lãi suất lẻ.",
        "order": 3,
        "rates": [
            (3, 5, 2.892, "3 đến 5 tháng"),
            (6, 11, 3.957, "6 đến 11 tháng"),
            (12, 17, 5.089, "12 đến 17 tháng"),
            (18, 23, 5.089, "18 đến 23 tháng"),
            (24, 24, 5.184, "24 tháng"),
        ],
    },
    {
        "code": "TK_ONLINE",
        "name": "Tiết kiệm trực tuyến (E-Mobile)",
        "description": "Tiết kiệm online qua ứng dụng E-Mobile Banking, lãi suất ưu đãi.",
        "order": 4,
        "rates": [
            (1, 2, 3.0, "1 đến 2 tháng"),
            (3, 5, 3.5, "3 đến 5 tháng"),
            (6, 11, 5.0, "6 đến 11 tháng"),
            (12, 23, 5.3, "12 đến 23 tháng"),
        ],
    },
    {
        "code": "TK_AN_SINH",
        "name": "Tiết kiệm An Sinh",
        "description": "Sản phẩm tiết kiệm An Sinh xã hội.",
        "order": 5,
        "rates": [
            (1, 11, 3.8, "Dưới 12 tháng"),
            (12, 24, 5.0, "12 đến 24 tháng"),
        ],
    },
]


class Command(BaseCommand):
    help = "Nạp dữ liệu lãi suất Agribank ban đầu (áp dụng từ 15/01/2026)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Xóa toàn bộ dữ liệu cũ trước khi nạp",
        )

    def handle(self, *args, **options):
        effective = date(2026, 1, 15)

        if options["clear"]:
            InterestRate.objects.all().delete()
            SavingsProduct.objects.all().delete()
            self.stdout.write(self.style.WARNING("Đã xóa dữ liệu cũ."))

        created_products = 0
        created_rates = 0

        for item in PRODUCTS:
            product, p_created = SavingsProduct.objects.update_or_create(
                code=item["code"],
                defaults={
                    "name": item["name"],
                    "description": item["description"],
                    "order": item["order"],
                    "is_active": True,
                },
            )
            if p_created:
                created_products += 1

            for term_min, term_max, rate, desc in item["rates"]:
                _, r_created = InterestRate.objects.update_or_create(
                    product=product,
                    term_month_min=term_min,
                    term_month_max=term_max,
                    defaults={
                        "interest_rate_yearly": rate,
                        "description": desc,
                        "effective_date": effective,
                        "is_active": True,
                    },
                )
                if r_created:
                    created_rates += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Hoàn tất! Tạo mới {created_products} sản phẩm, {created_rates} mức lãi suất."
            )
        )

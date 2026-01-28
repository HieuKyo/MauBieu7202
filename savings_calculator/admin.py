from django.contrib import admin
from .models import SavingsProduct, InterestRate


class InterestRateInline(admin.TabularInline):
    model = InterestRate
    extra = 1
    fields = [
        "term_month_min",
        "term_month_max",
        "interest_rate_yearly",
        "description",
        "effective_date",
        "is_active",
    ]


@admin.register(SavingsProduct)
class SavingsProductAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "is_active", "order", "updated_at"]
    list_editable = ["is_active", "order"]
    search_fields = ["name", "code"]
    list_filter = ["is_active"]
    inlines = [InterestRateInline]


@admin.register(InterestRate)
class InterestRateAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "description",
        "term_month_min",
        "term_month_max",
        "interest_rate_yearly",
        "effective_date",
        "is_active",
    ]
    list_filter = ["product", "is_active"]
    list_editable = ["interest_rate_yearly", "is_active"]
    search_fields = ["product__name", "description"]

from django.contrib import admin
from .models import TaxLocation, TaxSubEntry, TaxPaymentStatement, TaxPaymentItem


@admin.register(TaxLocation)
class TaxLocationAdmin(admin.ModelAdmin):
    list_display = ['tinh', 'co_quan_thue_group', 'xa_phuong', 'ma_co_quan_thu', 'ma_dia_ban']
    list_filter = ['tinh', 'co_quan_thue_group']
    search_fields = ['tinh', 'xa_phuong', 'ma_co_quan_thu', 'ten_co_quan_thu']
    ordering = ['tinh', 'co_quan_thue_group', 'xa_phuong']


@admin.register(TaxSubEntry)
class TaxSubEntryAdmin(admin.ModelAdmin):
    list_display = ['ma_tieu_muc', 'ten_tieu_muc']
    search_fields = ['ma_tieu_muc', 'ten_tieu_muc']
    ordering = ['ma_tieu_muc']


class TaxPaymentItemInline(admin.TabularInline):
    model = TaxPaymentItem
    extra = 1
    fields = ['stt', 'ma_tieu_muc', 'noi_dung', 'so_tien']


@admin.register(TaxPaymentStatement)
class TaxPaymentStatementAdmin(admin.ModelAdmin):
    list_display = ['ten_nguoi_nop', 'ma_so_thue', 'ngay_lap', 'tong_so_tien', 'created_at']
    list_filter = ['ngay_lap', 'created_at']
    search_fields = ['ten_nguoi_nop', 'ma_so_thue']
    ordering = ['-created_at']
    inlines = [TaxPaymentItemInline]
    readonly_fields = ['created_at', 'updated_at']

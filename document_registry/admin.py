from django.contrib import admin
from .models import OutgoingDocument, IncomingDocument


@admin.register(OutgoingDocument)
class OutgoingDocumentAdmin(admin.ModelAdmin):
    list_display = ['so_ky_hieu', 'ngay_van_ban', 'get_nguoi_ky_display_name', 'get_noi_nhan_display', 'loai_chuyen_phat', 'created_by']
    list_filter = ['nguoi_ky', 'loai_chuyen_phat', 'ngay_van_ban']
    search_fields = ['so_ky_hieu', 'ten_loai_trich_yeu', 'nguoi_ky_khac']
    date_hierarchy = 'ngay_van_ban'
    readonly_fields = ['created_at', 'created_by']


@admin.register(IncomingDocument)
class IncomingDocumentAdmin(admin.ModelAdmin):
    list_display = ['so_den', 'ngay_den', 'tac_gia', 'so_ky_hieu', 'don_vi_nguoi_nhan', 'created_by']
    list_filter = ['ngay_den']
    search_fields = ['so_den', 'so_ky_hieu', 'tac_gia', 'ten_loai_trich_yeu']
    date_hierarchy = 'ngay_den'
    readonly_fields = ['created_at', 'created_by']

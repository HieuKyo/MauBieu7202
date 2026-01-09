"""
Django Admin configuration cho module KPI Tool
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import ConversionRule, TellerTransactionBatch, TellerTransactionDetail


@admin.register(ConversionRule)
class ConversionRuleAdmin(admin.ModelAdmin):
    list_display = ['code', 'debit_account_pattern', 'credit_account_pattern',
                    'score_1', 'score_2', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'debit_account_pattern', 'credit_account_pattern', 'description']
    list_editable = ['is_active']
    ordering = ['code']

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('code', 'description', 'is_active')
        }),
        ('Quy tắc so khớp', {
            'fields': ('debit_account_pattern', 'credit_account_pattern', 'formula')
        }),
        ('Điểm quy đổi', {
            'fields': ('score_1', 'score_2')
        }),
    )

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Kích hoạt</span>')
        return format_html('<span style="color: red;">✗ Không kích hoạt</span>')
    is_active_badge.short_description = 'Trạng thái'


@admin.register(TellerTransactionBatch)
class TellerTransactionBatchAdmin(admin.ModelAdmin):
    list_display = ['teller_id', 'teller_name', 'month', 'year', 'file_date',
                    'total_transactions', 'matched_transactions', 'total_score',
                    'processing_status_badge', 'created_at']
    list_filter = ['processing_status', 'year', 'month', 'created_at']
    search_fields = ['teller_id', 'teller_name']
    readonly_fields = ['total_transactions', 'total_score', 'matched_transactions',
                      'unmatched_transactions', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Thông tin giao dịch viên', {
            'fields': ('teller_id', 'teller_name', 'month', 'year', 'file_date')
        }),
        ('Thống kê', {
            'fields': ('total_transactions', 'matched_transactions',
                      'unmatched_transactions', 'total_score')
        }),
        ('Trạng thái xử lý', {
            'fields': ('processing_status', 'error_message')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def processing_status_badge(self, obj):
        colors = {
            'completed': 'green',
            'processing': 'orange',
            'error': 'red',
        }
        labels = {
            'completed': 'Hoàn thành',
            'processing': 'Đang xử lý',
            'error': 'Có lỗi',
        }
        color = colors.get(obj.processing_status, 'gray')
        label = labels.get(obj.processing_status, obj.processing_status)
        return format_html(f'<span style="color: {color}; font-weight: bold;">● {label}</span>')
    processing_status_badge.short_description = 'Trạng thái'


@admin.register(TellerTransactionDetail)
class TellerTransactionDetailAdmin(admin.ModelAdmin):
    list_display = ['reference_no', 'batch_info', 'transaction_date',
                    'debit_account', 'credit_account', 'amount',
                    'score', 'is_matched_badge']
    list_filter = ['is_matched', 'transaction_date', 'batch__teller_id']
    search_fields = ['reference_no', 'debit_account', 'credit_account']
    readonly_fields = ['created_at']
    ordering = ['-transaction_date', '-transaction_time']

    fieldsets = (
        ('Thông tin lô', {
            'fields': ('batch',)
        }),
        ('Thông tin giao dịch', {
            'fields': ('reference_no', 'transaction_date', 'transaction_time',
                      'debit_account', 'credit_account', 'amount')
        }),
        ('Kết quả so khớp', {
            'fields': ('matched_rule', 'score', 'is_matched', 'notes')
        }),
        ('Thời gian', {
            'fields': ('created_at',)
        }),
    )

    def batch_info(self, obj):
        return f"{obj.batch.teller_id} - {obj.batch.month}/{obj.batch.year}"
    batch_info.short_description = 'Lô'

    def is_matched_badge(self, obj):
        if obj.is_matched:
            return format_html('<span style="color: green;">✓ Khớp</span>')
        return format_html('<span style="color: orange;">✗ Không khớp</span>')
    is_matched_badge.short_description = 'Trạng thái'

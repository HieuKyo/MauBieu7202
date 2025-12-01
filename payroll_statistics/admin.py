"""
Admin configuration cho app Payroll Statistics
"""
from django.contrib import admin
from django.http import HttpResponse
from django.db.models import Count, Sum, Q
from datetime import datetime
import csv
from .models import PayingUnit, BeneficiaryAccount, Transaction


def export_units_to_excel(modeladmin, request, queryset):
    """Export danh sách đơn vị ra Excel (CSV format) với thống kê"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="danh_sach_don_vi_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

    # Add BOM for Excel UTF-8 support
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow([
        'STK Đơn vị',
        'Tên Đơn vị',
        'Số Nhân viên',
        'Tổng GD Chi lương',
        'Tổng tiền Chi lương',
        'Tổng GD Thu hộ',
        'Tổng tiền Thu hộ',
        'Ngày tạo'
    ])

    # Annotate với thống kê chi tiết
    units = queryset.annotate(
        beneficiary_count=Count('beneficiaries', distinct=True),
        payroll_count=Count('transactions', filter=Q(transactions__transaction_type='payroll')),
        payroll_amount=Sum('transactions__amount', filter=Q(transactions__transaction_type='payroll')),
        collection_count=Count('transactions', filter=Q(transactions__transaction_type='collection')),
        collection_amount=Sum('transactions__amount', filter=Q(transactions__transaction_type='collection'))
    )

    for unit in units:
        writer.writerow([
            unit.account_number,
            unit.name or '',
            unit.beneficiary_count,
            unit.payroll_count,
            f"{unit.payroll_amount or 0:,.0f}",
            unit.collection_count,
            f"{unit.collection_amount or 0:,.0f}",
            unit.created_at.strftime('%d/%m/%Y %H:%M') if unit.created_at else ''
        ])

    return response

export_units_to_excel.short_description = "Xuất Excel - Thống kê đơn vị"


@admin.register(PayingUnit)
class PayingUnitAdmin(admin.ModelAdmin):
    list_display = ['account_number', 'name', 'get_beneficiary_count', 'created_at']
    search_fields = ['account_number', 'name']
    list_filter = ['created_at']
    ordering = ['account_number']
    actions = [export_units_to_excel]

    def get_beneficiary_count(self, obj):
        return obj.beneficiaries.count()
    get_beneficiary_count.short_description = 'Số Nhân viên'


def export_beneficiaries_to_excel(modeladmin, request, queryset):
    """Export danh sách nhân viên ra Excel (CSV format)"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="danh_sach_nhan_vien_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

    # Add BOM for Excel UTF-8 support
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow([
        'STK Nhân viên',
        'STK Đơn vị',
        'Tên Đơn vị',
        'Nội dung tham chiếu',
        'Số GD',
        'Tổng tiền GD',
        'Ngày tạo'
    ])

    # Annotate với thống kê
    beneficiaries = queryset.select_related('unit').annotate(
        transaction_count=Count('transactions'),
        total_amount=Sum('transactions__amount')
    )

    for ben in beneficiaries:
        writer.writerow([
            ben.account_number,
            ben.unit.account_number,
            ben.unit.name or '',
            ben.remark_ref or '',
            ben.transaction_count,
            f"{ben.total_amount or 0:,.0f}",
            ben.created_at.strftime('%d/%m/%Y %H:%M') if ben.created_at else ''
        ])

    return response

export_beneficiaries_to_excel.short_description = "Xuất Excel - Danh sách nhân viên"


@admin.register(BeneficiaryAccount)
class BeneficiaryAccountAdmin(admin.ModelAdmin):
    list_display = ['account_number', 'unit', 'remark_ref', 'get_transaction_count', 'created_at']
    search_fields = ['account_number', 'unit__account_number', 'remark_ref']
    list_filter = ['created_at', 'unit']
    ordering = ['unit', 'account_number']
    autocomplete_fields = ['unit']
    actions = [export_beneficiaries_to_excel]

    def get_transaction_count(self, obj):
        return obj.transactions.count()
    get_transaction_count.short_description = 'Số GD'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_date', 'transaction_type', 'unit', 'beneficiary', 'amount', 'remark']
    search_fields = ['unit__account_number', 'beneficiary__account_number', 'remark', 'facno', 'tacno']
    list_filter = ['transaction_type', 'transaction_date', 'created_at']
    ordering = ['-transaction_date', '-created_at']
    autocomplete_fields = ['unit', 'beneficiary']
    date_hierarchy = 'transaction_date'

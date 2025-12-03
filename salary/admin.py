"""
Admin configuration cho app Salary
"""
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Bank, CompanyAccount, Beneficiary, ProcessingHistory
from .resources import (
    BankResource,
    CompanyAccountResource,
    BeneficiaryResource,
    ProcessingHistoryResource
)


@admin.register(Bank)
class BankAdmin(ImportExportModelAdmin):
    """Admin cho Bank với import/export"""
    resource_class = BankResource
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    ordering = ('code',)


@admin.register(CompanyAccount)
class CompanyAccountAdmin(ImportExportModelAdmin):
    """Admin cho CompanyAccount với import/export"""
    resource_class = CompanyAccountResource
    list_display = ('account_number', 'account_name', 'bank', 'is_active', 'created_at')
    list_filter = ('is_active', 'bank', 'created_at')
    search_fields = ('account_number', 'account_name')
    ordering = ('account_number',)
    date_hierarchy = 'created_at'


@admin.register(Beneficiary)
class BeneficiaryAdmin(ImportExportModelAdmin):
    """Admin cho Beneficiary với import/export"""
    resource_class = BeneficiaryResource
    list_display = ('full_name', 'account_number', 'bank', 'bank_code', 'company', 'created_at')
    list_filter = ('bank', 'company', 'created_at')
    search_fields = ('full_name', 'account_number', 'bank_code')
    ordering = ('full_name',)
    date_hierarchy = 'created_at'
    autocomplete_fields = ['company']


@admin.register(ProcessingHistory)
class ProcessingHistoryAdmin(ImportExportModelAdmin):
    """Admin cho ProcessingHistory với import/export"""
    resource_class = ProcessingHistoryResource
    list_display = (
        'filename',
        'transaction_type',
        'company_account',
        'total_records',
        'total_amount',
        'status',
        'processed_by',
        'processed_at'
    )
    list_filter = ('transaction_type', 'status', 'processed_at')
    search_fields = ('filename', 'company_account__account_name', 'processed_by__username')
    ordering = ('-processed_at',)
    date_hierarchy = 'processed_at'
    readonly_fields = (
        'filename',
        'transaction_type',
        'total_records',
        'successful_records',
        'failed_records',
        'total_amount',
        'duplicate_accounts',
        'status',
        'error_message',
        'output_file',
        'processed_by',
        'processed_at'
    )

    def has_add_permission(self, request):
        """Không cho phép thêm mới trực tiếp"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Chỉ superuser mới được xóa"""
        return request.user.is_superuser

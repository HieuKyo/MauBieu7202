"""
Admin configuration cho app Payroll Statistics
"""
from django.contrib import admin
from .models import PayingUnit, BeneficiaryAccount, Transaction


@admin.register(PayingUnit)
class PayingUnitAdmin(admin.ModelAdmin):
    list_display = ['account_number', 'name', 'created_at']
    search_fields = ['account_number', 'name']
    list_filter = ['created_at']
    ordering = ['account_number']


@admin.register(BeneficiaryAccount)
class BeneficiaryAccountAdmin(admin.ModelAdmin):
    list_display = ['account_number', 'unit', 'remark_ref', 'created_at']
    search_fields = ['account_number', 'unit__account_number', 'remark_ref']
    list_filter = ['created_at', 'unit']
    ordering = ['unit', 'account_number']
    autocomplete_fields = ['unit']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_date', 'transaction_type', 'unit', 'beneficiary', 'amount', 'remark']
    search_fields = ['unit__account_number', 'beneficiary__account_number', 'remark', 'facno', 'tacno']
    list_filter = ['transaction_type', 'transaction_date', 'created_at']
    ordering = ['-transaction_date', '-created_at']
    autocomplete_fields = ['unit', 'beneficiary']
    date_hierarchy = 'transaction_date'

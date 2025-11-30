"""
Admin configuration cho app Payroll Statistics
"""
from django.contrib import admin
from .models import PayingUnit, BeneficiaryAccount


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

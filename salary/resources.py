"""
Resources cho import/export trong Django Admin
"""
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Bank, CompanyAccount, Beneficiary, ProcessingHistory


class BankResource(resources.ModelResource):
    """Resource cho import/export Bank"""
    class Meta:
        model = Bank
        fields = ('code', 'name')
        export_order = ('code', 'name')
        import_id_fields = ('code',)


class CompanyAccountResource(resources.ModelResource):
    """Resource cho import/export CompanyAccount"""
    bank = fields.Field(
        column_name='bank',
        attribute='bank',
        widget=ForeignKeyWidget(Bank, 'code')
    )
    class Meta:
        model = CompanyAccount
        fields = ('account_number', 'account_name', 'bank', 'is_active')
        export_order = ('account_number', 'account_name', 'bank', 'is_active')
        import_id_fields = ('account_number',)


class BeneficiaryResource(resources.ModelResource):
    """Resource cho import/export Beneficiary"""
    bank = fields.Field(
        column_name='bank',
        attribute='bank',
        widget=ForeignKeyWidget(Bank, 'code')
    )
    company = fields.Field(
        column_name='company',
        attribute='company',
        widget=ForeignKeyWidget(CompanyAccount, 'account_number')
    )
    class Meta:
        model = Beneficiary
        fields = ('full_name', 'account_number', 'bank', 'bank_code', 'company', 'note')
        export_order = ('full_name', 'account_number', 'bank', 'bank_code', 'company', 'note')
        import_id_fields = ('account_number', 'bank_code')


class ProcessingHistoryResource(resources.ModelResource):
    """Resource cho export ProcessingHistory"""
    company_account = fields.Field(
        column_name='company_account',
        attribute='company_account',
        widget=ForeignKeyWidget(CompanyAccount, 'account_number')
    )
    class Meta:
        model = ProcessingHistory
        fields = (
            'id', 'filename', 'transaction_type', 'company_account',
            'total_records', 'successful_records', 'failed_records',
            'total_amount', 'status', 'processed_by', 'processed_at'
        )
        export_order = (
            'id', 'filename', 'transaction_type', 'company_account',
            'total_records', 'successful_records', 'failed_records',
            'total_amount', 'status', 'processed_by', 'processed_at'
        )

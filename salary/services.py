"""
Services cho app Salary - Logic xu ly file Excel/CSV
"""
import pandas as pd
import os
from decimal import Decimal
from unidecode import unidecode
from .models import Bank, Beneficiary, ProcessingHistory


class SalaryFileProcessor:
    """Xu ly file Excel/CSV chi luong va thu ho"""

    # Mapping ma ngan hang
    BANK_CODES = {
        'AGRIBANK': 'AGR',
        'VIETINBANK': 'CTG',
        'BIDV': 'BIDV',
        'VIETCOMBANK': 'VCB',
        'TECHCOMBANK': 'TCB',
        'MB': 'MB',
    }

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.duplicate_accounts = []

    def detect_bank_code(self, bank_name):
        """Phat hien ma ngan hang tu ten"""
        if not bank_name or pd.isna(bank_name):
            return 'KHAC', None

        bank_name_upper = str(bank_name).upper().strip()

        for name, code in self.BANK_CODES.items():
            if name.upper() in bank_name_upper:
                try:
                    bank = Bank.objects.get(code=code)
                    return code, bank
                except Bank.DoesNotExist:
                    return code, None

        try:
            bank = Bank.objects.get(code=bank_name_upper)
            return bank_name_upper, bank
        except Bank.DoesNotExist:
            pass

        return 'KHAC', None

    def normalize_text(self, text):
        """Chuan hoa text"""
        if not text or pd.isna(text):
            return ''
        text = str(text).strip()
        text = unidecode(text)
        text = text.upper()
        text = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in text)
        text = ' '.join(text.split())
        return text

    def check_duplicates(self, df, account_column='account_number'):
        """Kiem tra STK trung lap"""
        duplicates = df[df.duplicated(subset=[account_column], keep=False)]
        if not duplicates.empty:
            dup_accounts = duplicates[account_column].unique().tolist()
            self.duplicate_accounts = dup_accounts
            self.warnings.append(f"Phat hien {len(dup_accounts)} tai khoan trung lap")
            return dup_accounts
        return []

    def process_excel_file(self, file_path, transaction_type, company_account=None):
        """Xu ly file Excel/CSV"""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8-sig')
            else:
                df = pd.read_excel(file_path)

            required_columns = ['full_name', 'account_number', 'amount', 'description']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                self.errors.append(f"Thieu cac cot: {', '.join(missing_columns)}")
                return {'success': False, 'errors': self.errors, 'warnings': self.warnings}

            if 'bank_name' in df.columns and 'bank_code' not in df.columns:
                df['bank_code'] = df['bank_name'].apply(lambda x: self.detect_bank_code(x)[0])

            self.check_duplicates(df, 'account_number')

            df['full_name_normalized'] = df['full_name'].apply(self.normalize_text)
            df['description_normalized'] = df['description'].apply(self.normalize_text)

            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
            total_amount = Decimal(str(df['amount'].sum()))

            output_filename = self._generate_output_filename(file_path, transaction_type)
            output_path = os.path.join(os.path.dirname(file_path), output_filename)

            # Get bank names if available
            bank_names = []
            if 'bank_name' in df.columns:
                bank_names = df['bank_name'].fillna('Agribank')
            else:
                # Map bank codes to names
                bank_code_to_name = {
                    'AGR': 'Agribank',
                    'CTG': 'Vietinbank',
                    'BIDV': 'BIDV',
                    'VCB': 'Vietcombank',
                    'TCB': 'Techcombank',
                    'MB': 'MB Bank',
                }
                bank_names = df.get('bank_code', 'AGR').apply(lambda x: bank_code_to_name.get(x, 'Agribank'))

            output_df = pd.DataFrame({
                'STT': range(1, len(df) + 1),
                'HO_TEN': df['full_name_normalized'],
                'SO_TAI_KHOAN': df['account_number'],
                'NGAN_HANG': bank_names,
                'SO_TIEN': df['amount'].astype(int),
                'NOI_DUNG': df['description_normalized'],
            })

            output_df.to_csv(output_path, index=False, encoding='utf-8-sig')

            if company_account:
                self._save_beneficiaries(df, company_account)

            return {
                'success': True,
                'output_file': output_filename,
                'total_records': len(df),
                'total_amount': total_amount,
                'errors': self.errors,
                'warnings': self.warnings,
                'duplicate_accounts': self.duplicate_accounts
            }

        except Exception as e:
            self.errors.append(f"Loi xu ly file: {str(e)}")
            return {'success': False, 'errors': self.errors, 'warnings': self.warnings}

    def _generate_output_filename(self, input_path, transaction_type):
        """Tao ten file output"""
        basename = os.path.basename(input_path)
        name_without_ext = os.path.splitext(basename)[0]
        prefix = 'CHI_LUONG' if transaction_type == 'PAYROLL' else 'THU_HO'
        return f"{prefix}_{name_without_ext}_AGR.csv"

    def _save_beneficiaries(self, df, company_account):
        """Luu thong tin beneficiary"""
        for _, row in df.iterrows():
            try:
                bank_code = row.get('bank_code', 'AGR')
                bank_obj = None
                if bank_code and bank_code != 'KHAC':
                    try:
                        bank_obj = Bank.objects.get(code=bank_code)
                    except Bank.DoesNotExist:
                        pass
                Beneficiary.objects.get_or_create(
                    account_number=row['account_number'],
                    bank_code=bank_code,
                    defaults={
                        'full_name': row['full_name'],
                        'bank': bank_obj,
                        'company': company_account,
                    }
                )
            except Exception as e:
                self.warnings.append(f"Khong the luu beneficiary {row['account_number']}: {str(e)}")


class SalaryStatisticsService:
    """Service tinh toan thong ke dashboard"""

    @staticmethod
    def get_statistics(period='month', start_date=None, end_date=None):
        """Lay thong ke theo khoang thoi gian"""
        from django.db.models import Sum, Count
        from datetime import datetime, timedelta

        if not start_date:
            today = datetime.now()
            if period == 'week':
                start_date = today - timedelta(days=7)
            elif period == 'month':
                start_date = today.replace(day=1)
            elif period == 'quarter':
                quarter_month = ((today.month - 1) // 3) * 3 + 1
                start_date = today.replace(month=quarter_month, day=1)
            elif period == 'year':
                start_date = today.replace(month=1, day=1)

        queryset = ProcessingHistory.objects.filter(status='SUCCESS')
        if start_date:
            queryset = queryset.filter(processed_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(processed_at__lte=end_date)

        stats = queryset.aggregate(
            total_amount=Sum('total_amount'),
            total_files=Count('id')
        )

        payroll_stats = queryset.filter(transaction_type='PAYROLL').aggregate(
            payroll_amount=Sum('total_amount'),
            payroll_count=Count('id')
        )

        collection_stats = queryset.filter(transaction_type='COLLECTION').aggregate(
            collection_amount=Sum('total_amount'),
            collection_count=Count('id')
        )

        return {
            'total_amount': stats['total_amount'] or Decimal('0.00'),
            'total_files': stats['total_files'] or 0,
            'payroll_amount': payroll_stats['payroll_amount'] or Decimal('0.00'),
            'payroll_count': payroll_stats['payroll_count'] or 0,
            'collection_amount': collection_stats['collection_amount'] or Decimal('0.00'),
            'collection_count': collection_stats['collection_count'] or 0,
        }

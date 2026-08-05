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
        """Xu ly file Excel/CSV - Su dung logic code cu"""
        try:
            from datetime import datetime

            # Doc file KHONG CO header (nhu code cu)
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, dtype=str, header=None, sep=',', encoding='utf-8-sig')
            else:
                df = pd.read_excel(file_path, dtype=str, header=None)

            # Kiem tra so cot (phai co it nhat 5 cot)
            if len(df.columns) < 5:
                self.errors.append('File phai co it nhat 5 cot: Ho ten, STK, Ten NH, So tien, Noi dung.')
                return {'success': False, 'errors': self.errors, 'warnings': self.warnings}

            # Tao mapping bank codes
            bank_codes_signed = {b.name.strip().lower(): b.code for b in Bank.objects.all()}
            bank_codes_unsigned = {self.normalize_text(b.name).lower(): b.code for b in Bank.objects.all()}

            # Kiem tra phai co company_account
            if not company_account:
                self.errors.append('Phai chon tai khoan cong ty de xu ly file')
                return {'success': False, 'errors': self.errors, 'warnings': self.warnings}

            current_date = datetime.now().strftime('%Y%m%d')

            successful_rows = []
            error_rows = []
            seen_accounts = set()

            total_amount = Decimal('0')

            # Xu ly tung dong
            for index, row in df.iterrows():
                line_number = index + 1
                try:
                    # Lay du lieu tu 5 cot
                    ho_ten_raw = row[0]
                    stk_raw = row[1]
                    ten_ngan_hang_raw = row[2]
                    so_tien_raw = row[3]
                    noi_dung_raw = row[4]

                    # Validate du lieu
                    if pd.isna(ho_ten_raw) or str(ho_ten_raw).strip() == '':
                        raise ValueError("Ho ten khong duoc de trong")
                    if pd.isna(stk_raw) or str(stk_raw).strip() == '':
                        raise ValueError("So tai khoan khong duoc de trong")
                    if pd.isna(so_tien_raw):
                        raise ValueError("So tien khong duoc de trong")

                    ho_ten = str(ho_ten_raw).strip()
                    stk = str(stk_raw).strip()
                    ten_ngan_hang = str(ten_ngan_hang_raw).strip() if not pd.isna(ten_ngan_hang_raw) else 'Agribank'

                    # Xac dinh ngan hang
                    ten_ngan_hang_unsigned = self.normalize_text(ten_ngan_hang).lower()
                    is_agribank = 'agribank' in ten_ngan_hang_unsigned or 'nong nghiep' in ten_ngan_hang_unsigned

                    # VALIDATE: STK Agribank phai co dung 13 ky tu
                    if is_agribank and len(stk) != 13:
                        raise ValueError(f"STK Agribank phai co dung 13 ky tu (hien tai: {len(stk)})")

                    # Kiem tra trung lap
                    if stk in seen_accounts:
                        if stk not in self.duplicate_accounts:
                            self.duplicate_accounts.append(stk)
                            self.warnings.append(f"STK trung lap: {stk}")
                    else:
                        seen_accounts.add(stk)

                    # Xu ly so tien
                    so_tien = Decimal(str(so_tien_raw).replace(',', ''))
                    total_amount += so_tien

                    noi_dung = str(noi_dung_raw).strip()

                    # Xac dinh ma_cot_1
                    ma_cot_1 = 'HQIL'
                    if is_agribank:
                        ma_cot_1 = 'KO'
                    elif 'vietinbank' in ten_ngan_hang_unsigned or 'cong thuong' in ten_ngan_hang_unsigned or \
                         'bidv' in ten_ngan_hang_unsigned or 'dau tu va phat trien' in ten_ngan_hang_unsigned:
                        ma_cot_1 = 'BP'

                    # Xac dinh ma lien ngan hang
                    if is_agribank:
                        agribank_branch_name = "Agribank Gia Rai Bac Lieu"
                        ma_lien_ngan_hang9 = agribank_branch_name
                        ma_lien_ngan_hang10 = agribank_branch_name
                    else:
                        lookup_code = bank_codes_signed.get(ten_ngan_hang.lower()) or \
                                    bank_codes_unsigned.get(ten_ngan_hang_unsigned, '')
                        ma_lien_ngan_hang9 = lookup_code
                        ma_lien_ngan_hang10 = '95204006'

                    # Luu beneficiary
                    try:
                        beneficiary, created = Beneficiary.objects.get_or_create(
                            full_name=ho_ten,
                            account_number=stk,
                            company=company_account
                        )
                    except Exception as e:
                        self.warnings.append(f"Khong the luu beneficiary {stk}: {str(e)}")

                    # Tao dong CSV theo transaction_type
                    csv_row_raw = []
                    if transaction_type == 'PAYROLL':
                        csv_row_raw = [
                            ma_cot_1,
                            company_account.account_number,
                            company_account.account_name,
                            stk,
                            ho_ten,
                            'VND',
                            str(int(so_tien)),
                            current_date,
                            ma_lien_ngan_hang9,
                            ma_lien_ngan_hang10,
                            noi_dung
                        ]
                    elif transaction_type == 'COLLECTION':
                        csv_row_raw = [
                            ma_cot_1,
                            stk,
                            ho_ten,
                            company_account.account_number,  # Cot D: STK cong ty
                            company_account.account_name,    # Cot E: Ten cong ty
                            'VND',
                            str(int(so_tien)),
                            current_date,
                            ma_lien_ngan_hang9,
                            ma_lien_ngan_hang10,
                            noi_dung
                        ]

                    # Chuan hoa text (bo dau)
                    final_csv_row = [self.normalize_text(str(item)) for item in csv_row_raw]
                    successful_rows.append(final_csv_row)

                except (ValueError, Exception) as e:
                    error_message = str(e)
                    error_rows.append({
                        'Dong': line_number,
                        'Ho ten': row[0] if len(row) > 0 else '',
                        'STK': row[1] if len(row) > 1 else '',
                        'So tien': row[3] if len(row) > 3 else '',
                        'Loi': error_message
                    })

            # Neu co loi, return errors
            if error_rows:
                error_msg = f"Co {len(error_rows)} dong loi:\n"
                for err in error_rows[:5]:  # Chi hien thi 5 loi dau
                    error_msg += f"- Dong {err['Dong']}: {err['Loi']}\n"
                if len(error_rows) > 5:
                    error_msg += f"... va {len(error_rows) - 5} loi khac"
                self.errors.append(error_msg)

            # Luu file output
            output_filename = self._generate_output_filename(file_path, transaction_type)
            output_path = os.path.join(os.path.dirname(file_path), output_filename)

            # Ghi file CSV khong co header
            with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
                import csv
                writer = csv.writer(f)
                writer.writerows(successful_rows)

            return {
                'success': True if not error_rows else False,
                'output_file': output_filename,
                'total_records': len(successful_rows),
                'total_amount': total_amount,
                'errors': self.errors,
                'warnings': self.warnings,
                'duplicate_accounts': self.duplicate_accounts,
                'error_rows': error_rows
            }

        except Exception as e:
            self.errors.append(f"Loi xu ly file: {str(e)}")
            import traceback
            self.errors.append(traceback.format_exc())
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
        from django.db.models.functions import Coalesce
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

        # Use Coalesce to handle NULL values and ensure Decimal type
        try:
            stats = queryset.aggregate(
                total_amount=Coalesce(Sum('total_amount'), Decimal('0.00')),
                total_files=Count('id')
            )

            payroll_stats = queryset.filter(transaction_type='PAYROLL').aggregate(
                payroll_amount=Coalesce(Sum('total_amount'), Decimal('0.00')),
                payroll_count=Count('id')
            )

            collection_stats = queryset.filter(transaction_type='COLLECTION').aggregate(
                collection_amount=Coalesce(Sum('total_amount'), Decimal('0.00')),
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
        except Exception as e:
            # If aggregation fails, return zero values
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error calculating statistics: {e}")

            return {
                'total_amount': Decimal('0.00'),
                'total_files': 0,
                'payroll_amount': Decimal('0.00'),
                'payroll_count': 0,
                'collection_amount': Decimal('0.00'),
                'collection_count': 0,
            }

"""
Core logic xử lý file DBF và tính điểm quy đổi
"""
import os
import re
from datetime import datetime, date, time
from decimal import Decimal
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

from dbfread import DBF
from django.db import transaction

from .models import ConversionRule, TellerTransactionBatch, TellerTransactionDetail


class DBFProcessor:
    """
    Xử lý file DBF và tính điểm quy đổi
    """

    def __init__(self):
        self.conversion_rules = list(ConversionRule.objects.filter(is_active=True))

    def parse_filename(self, filename: str) -> Optional[Tuple[str, date]]:
        """
        Parse tên file để lấy thông tin teller_id và file_date
        Format: [USER_ID][DDMMYYYY].DBF
        Ví dụ: GRATHIEU26092025.DBF

        Returns: (teller_id, file_date) hoặc None nếu không parse được
        """
        # Loại bỏ extension .DBF
        basename = os.path.splitext(filename)[0].upper()

        # Tìm 8 ký tự số cuối cùng (DDMMYYYY)
        match = re.search(r'(\d{8})$', basename)
        if not match:
            return None

        date_str = match.group(1)
        teller_id = basename[:-8]  # Lấy phần trước ngày

        if not teller_id:
            return None

        # Parse ngày tháng (DDMMYYYY)
        try:
            day = int(date_str[0:2])
            month = int(date_str[2:4])
            year = int(date_str[4:8])
            file_date = date(year, month, day)
        except (ValueError, IndexError):
            return None

        return teller_id, file_date

    def read_dbf_file(self, file_path: str) -> List[Dict]:
        """
        Đọc file DBF và trả về danh sách records
        """
        records = []
        try:
            dbf = DBF(file_path, encoding='cp1252')  # Hoặc encoding khác tùy file
            for record in dbf:
                records.append(dict(record))
        except Exception as e:
            raise ValueError(f"Không thể đọc file DBF: {str(e)}")

        return records

    def group_transactions_by_refno(self, records: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Gom nhóm các dòng theo REFNO (Số tham chiếu)
        """
        grouped = defaultdict(list)
        for record in records:
            refno = str(record.get('REFNO', '')).strip()
            if refno:
                grouped[refno].append(record)

        return grouped

    def reconstruct_journal_entry(self, refno_records: List[Dict]) -> Optional[Dict]:
        """
        Tái tạo bút toán từ các dòng có cùng REFNO
        Tìm cặp Nợ/Có từ các dòng

        Returns: {
            'refno': str,
            'debit_account': str,
            'credit_account': str,
            'amount': Decimal,
            'transaction_date': date,
            'transaction_time': time,
        }
        """
        debit_entries = []
        credit_entries = []

        for record in refno_records:
            trdrcr = str(record.get('TRDRCR', '')).strip().upper()
            acctcd = str(record.get('ACCTCD', '')).strip()
            tramt = record.get('TRAMT', 0)

            # Parse amount an toàn
            try:
                if tramt is None or tramt == '':
                    amount = Decimal('0')
                else:
                    # Chuyển sang string và loại bỏ khoảng trắng
                    amount_str = str(tramt).strip()
                    amount = Decimal(amount_str) if amount_str else Decimal('0')
            except (ValueError, TypeError, Exception):
                amount = Decimal('0')

            if trdrcr == 'D':  # Debit/Nợ
                debit_entries.append({
                    'account': acctcd,
                    'amount': amount,
                    'record': record
                })
            elif trdrcr == 'C':  # Credit/Có
                credit_entries.append({
                    'account': acctcd,
                    'amount': amount,
                    'record': record
                })

        # Cần ít nhất 1 Nợ và 1 Có để tạo thành bút toán
        if not debit_entries or not credit_entries:
            return None

        # Lấy entry đầu tiên của mỗi loại (có thể có nhiều dòng)
        debit_entry = debit_entries[0]
        credit_entry = credit_entries[0]

        # Parse ngày giờ giao dịch
        first_record = refno_records[0]
        trans_date = self._parse_date(first_record.get('TRDATE'))
        trans_time = self._parse_time(first_record.get('TRTIME'))

        return {
            'refno': str(first_record.get('REFNO', '')).strip(),
            'debit_account': debit_entry['account'],
            'credit_account': credit_entry['account'],
            'amount': debit_entry['amount'],
            'transaction_date': trans_date,
            'transaction_time': trans_time,
        }

    def _parse_date(self, date_value) -> Optional[date]:
        """Parse date từ nhiều format khác nhau"""
        if isinstance(date_value, date):
            return date_value
        if isinstance(date_value, datetime):
            return date_value.date()
        if isinstance(date_value, str):
            # Thử parse từ string (YYYYMMDD, YYYY-MM-DD, etc.)
            for fmt in ['%Y%m%d', '%Y-%m-%d', '%d/%m/%Y']:
                try:
                    return datetime.strptime(date_value, fmt).date()
                except ValueError:
                    continue
        return date.today()

    def _parse_time(self, time_value) -> Optional[time]:
        """Parse time từ nhiều format khác nhau"""
        if isinstance(time_value, time):
            return time_value
        if isinstance(time_value, datetime):
            return time_value.time()
        if isinstance(time_value, str):
            # Thử parse từ string (HHMMSS, HH:MM:SS, etc.)
            for fmt in ['%H%M%S', '%H:%M:%S', '%H%M']:
                try:
                    return datetime.strptime(time_value, fmt).time()
                except ValueError:
                    continue
        return None

    def match_rule(self, debit_account: str, credit_account: str) -> Optional[ConversionRule]:
        """
        Tìm quy tắc khớp với cặp tài khoản Nợ/Có
        """
        for rule in self.conversion_rules:
            if rule.matches_transaction(debit_account, credit_account):
                return rule
        return None

    def calculate_score(self, transaction: Dict) -> Tuple[Decimal, Optional[ConversionRule], bool]:
        """
        Tính điểm cho một giao dịch

        Returns: (score, matched_rule, is_matched)
        """
        debit_account = transaction['debit_account']
        credit_account = transaction['credit_account']

        matched_rule = self.match_rule(debit_account, credit_account)

        if matched_rule:
            # Mặc định lấy score_1, có thể mở rộng logic chọn score_2
            score = matched_rule.score_1
            return score, matched_rule, True

        return Decimal('0'), None, False

    @transaction.atomic
    def process_dbf_file(self, file_path: str, teller_name: str = None, original_filename: str = None) -> TellerTransactionBatch:
        """
        Xử lý file DBF và lưu vào database

        Args:
            file_path: Đường dẫn đến file DBF
            teller_name: Tên giao dịch viên (optional, nếu không có sẽ dùng teller_id)
            original_filename: Tên file gốc (optional, dùng khi file_path là file tạm)

        Returns: TellerTransactionBatch object
        """
        # Sử dụng original_filename nếu có, nếu không dùng basename của file_path
        filename = original_filename if original_filename else os.path.basename(file_path)

        # Parse tên file
        parse_result = self.parse_filename(filename)
        if not parse_result:
            raise ValueError(f"Không thể parse tên file: {filename}")

        teller_id, file_date = parse_result

        if not teller_name:
            teller_name = teller_id

        # Tạo batch record
        batch = TellerTransactionBatch.objects.create(
            teller_id=teller_id,
            teller_name=teller_name,
            month=file_date.month,
            year=file_date.year,
            file_date=file_date,
            processing_status='processing'
        )

        try:
            # Đọc file DBF
            records = self.read_dbf_file(file_path)

            # Gom nhóm theo REFNO
            grouped_records = self.group_transactions_by_refno(records)

            total_score = Decimal('0')
            matched_count = 0
            unmatched_count = 0
            transaction_count = 0

            # Xử lý từng nhóm REFNO
            for refno, refno_records in grouped_records.items():
                # Tái tạo bút toán
                journal_entry = self.reconstruct_journal_entry(refno_records)

                if not journal_entry:
                    continue

                # Tính điểm
                score, matched_rule, is_matched = self.calculate_score(journal_entry)

                # Lưu chi tiết giao dịch
                TellerTransactionDetail.objects.create(
                    batch=batch,
                    reference_no=journal_entry['refno'],
                    transaction_date=journal_entry['transaction_date'],
                    transaction_time=journal_entry['transaction_time'],
                    debit_account=journal_entry['debit_account'],
                    credit_account=journal_entry['credit_account'],
                    amount=journal_entry['amount'],
                    matched_rule=matched_rule,
                    score=score,
                    is_matched=is_matched
                )

                # Cập nhật tổng
                total_score += score
                transaction_count += 1

                if is_matched:
                    matched_count += 1
                else:
                    unmatched_count += 1

            # Cập nhật batch
            batch.total_transactions = transaction_count
            batch.total_score = total_score
            batch.matched_transactions = matched_count
            batch.unmatched_transactions = unmatched_count
            batch.processing_status = 'completed'
            batch.save()

        except Exception as e:
            batch.processing_status = 'error'
            batch.error_message = str(e)
            batch.save()
            raise

        return batch

    def process_multiple_files(self, file_paths: List[str], teller_name: str = None) -> List[TellerTransactionBatch]:
        """
        Xử lý nhiều file DBF cùng lúc

        Args:
            file_paths: Danh sách đường dẫn file DBF
            teller_name: Tên giao dịch viên (optional)

        Returns: List of TellerTransactionBatch objects
        """
        batches = []
        for file_path in file_paths:
            try:
                batch = self.process_dbf_file(file_path, teller_name)
                batches.append(batch)
            except Exception as e:
                # Log lỗi nhưng tiếp tục xử lý file khác
                print(f"Error processing {file_path}: {str(e)}")
                continue

        return batches


class RuleImporter:
    """
    Import quy tắc từ file hesoquydoi.BAK (DBF format)
    """

    @transaction.atomic
    def import_from_dbf(self, file_path: str) -> int:
        """
        Import quy tắc từ file DBF

        Returns: Số lượng quy tắc được import
        """
        count = 0
        try:
            dbf = DBF(file_path, encoding='cp1252')

            for record in dbf:
                # Parse các trường từ file
                code = str(record.get('CODE', '')).strip() or str(record.get('MALOAI', '')).strip()
                tkno = str(record.get('TKNO', '')).strip()
                tkco = str(record.get('TKCO', '')).strip()

                # Parse hệ số quy đổi an toàn
                try:
                    hq1_value = record.get('HESOQUAY1', 0)
                    hesoquay1 = Decimal(str(hq1_value).strip()) if hq1_value else Decimal('0')
                except (ValueError, TypeError, Exception):
                    hesoquay1 = Decimal('0')

                try:
                    hq2_value = record.get('HESOQUAY2', 0)
                    hesoquay2 = Decimal(str(hq2_value).strip()) if hq2_value else Decimal('0')
                except (ValueError, TypeError, Exception):
                    hesoquay2 = Decimal('0')

                congthuc = str(record.get('CONGTHUC', '')).strip()
                description = str(record.get('GHICHU', '')).strip() or str(record.get('MOTA', '')).strip()

                if not tkno or not tkco:
                    continue

                # Tạo hoặc cập nhật quy tắc
                ConversionRule.objects.update_or_create(
                    code=code,
                    debit_account_pattern=tkno,
                    credit_account_pattern=tkco,
                    defaults={
                        'score_1': hesoquay1,
                        'score_2': hesoquay2,
                        'formula': congthuc if congthuc else None,
                        'description': description,
                        'is_active': True
                    }
                )
                count += 1

        except Exception as e:
            raise ValueError(f"Không thể import quy tắc từ file: {str(e)}")

        return count

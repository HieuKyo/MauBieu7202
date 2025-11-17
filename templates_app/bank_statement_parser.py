"""
Module xử lý và phân tích file sao kê ngân hàng Agribank
"""
import re
import pandas as pd
from datetime import datetime
from decimal import Decimal


class BankStatementParser:
    """Class xử lý file sao kê ngân hàng Agribank"""

    # Các cột bắt buộc trong file sao kê Agribank
    REQUIRED_COLUMNS = ['trdt', 'acctccyamt', 'aftrbal', 'rem', 'trcdnm']

    def __init__(self, file_path):
        """
        Khởi tạo parser với đường dẫn file

        Args:
            file_path: Đường dẫn đến file Excel (.xls hoặc .xlsx)
        """
        self.file_path = file_path
        self.df = None
        self.processed_data = []

    def validate_file(self):
        """
        Kiểm tra file có đúng định dạng sao kê Agribank không

        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Đọc file Excel
            if self.file_path.endswith('.xls'):
                self.df = pd.read_excel(self.file_path, engine='xlrd')
            elif self.file_path.endswith('.xlsx'):
                self.df = pd.read_excel(self.file_path, engine='openpyxl')
            else:
                return False, "File phải có định dạng .xls hoặc .xlsx"

            # Kiểm tra các cột bắt buộc
            missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in self.df.columns]
            if missing_cols:
                return False, f"File thiếu các cột bắt buộc: {', '.join(missing_cols)}"

            # Kiểm tra có dữ liệu không
            if len(self.df) == 0:
                return False, "File không có dữ liệu"

            return True, ""

        except Exception as e:
            return False, f"Lỗi khi đọc file: {str(e)}"

    def parse_beneficiary_info(self, rem, tomgntno, acctccyamt):
        """
        Parse thông tin người thụ hưởng từ nội dung giao dịch

        Args:
            rem: Nội dung giao dịch
            tomgntno: Tài khoản đối ứng
            acctccyamt: Số tiền (âm/dương)

        Returns:
            dict: {'bank_name': str, 'account_number': str, 'beneficiary_name': str}
        """
        rem = str(rem)
        bank_name = ""
        account_number = ""
        beneficiary_name = ""

        # Pattern 1: Chuyển khoản nội bộ Agribank
        # Format: MB(mã_giao_dịch)(nội dung)
        pattern1 = re.search(r'MB\((\d+)\)\((.*?)\)', rem)
        if pattern1:
            bank_name = "Agribank"
            content = pattern1.group(2)
            # Nếu tiền vào (acctccyamt > 0), lấy số TK từ tomgntno
            if acctccyamt > 0 and tomgntno:
                account_number = str(tomgntno)
            # Parse tên người từ nội dung
            # Thường là các từ in hoa ở đầu
            words = content.split()
            name_parts = []
            for word in words:
                # Nếu là từ in hoa hoặc chữ cái đầu viết hoa
                if word and (word.isupper() or word[0].isupper()):
                    # Kiểm tra không phải là từ khóa
                    if word.lower() not in ['chuyen', 'khoan', 'chuyển', 'khoản', 'mb', 'fcc', 'ct']:
                        name_parts.append(word)
                    else:
                        break
            if name_parts:
                beneficiary_name = ' '.join(name_parts[:4])  # Lấy tối đa 4 từ
            return {'bank_name': bank_name, 'account_number': account_number, 'beneficiary_name': beneficiary_name}

        # Pattern 2: Vietcombank
        # Format 1: mã-VCB;số_tài_khoản;nội_dung
        pattern2_1 = re.search(r'\d+-VCB;(\d{10,20});(.*)', rem)
        if pattern2_1:
            bank_name = "Vietcombank"
            account_number = pattern2_1.group(1)
            content = pattern2_1.group(2)
            # Parse tên từ content
            words = content.split()
            name_parts = []
            for word in words:
                if word and (word.isupper() or word[0].isupper()):
                    if word.lower() not in ['chuyen', 'khoan', 'chuyển', 'khoản', 'vcb', 'ct']:
                        name_parts.append(word)
                    else:
                        break
            if name_parts:
                beneficiary_name = ' '.join(name_parts[:4])
            return {'bank_name': bank_name, 'account_number': account_number, 'beneficiary_name': beneficiary_name}

        # Format 2: Vietcombank:số_tài_khoản:nội_dung
        pattern2_2 = re.search(r'Vietcombank:(\d{10,20}):(.*)', rem)
        if pattern2_2:
            bank_name = "Vietcombank"
            account_number = pattern2_2.group(1)
            content = pattern2_2.group(2)
            words = content.split()
            name_parts = []
            for word in words:
                if word and (word.isupper() or word[0].isupper()):
                    if word.lower() not in ['chuyen', 'khoan', 'chuyển', 'khoản', 'vcb', 'ct']:
                        name_parts.append(word)
                    else:
                        break
            if name_parts:
                beneficiary_name = ' '.join(name_parts[:4])
            return {'bank_name': bank_name, 'account_number': account_number, 'beneficiary_name': beneficiary_name}

        # Format 3: mã-Vietcombanksố_tài_khoảnnội_dung (viết liền)
        pattern2_3 = re.search(r'\d+-Vietcombank(\d{10,20})(.*)', rem)
        if pattern2_3:
            bank_name = "Vietcombank"
            account_number = pattern2_3.group(1)
            content = pattern2_3.group(2)
            words = content.split()
            name_parts = []
            for word in words:
                if word and (word.isupper() or word[0].isupper()):
                    if word.lower() not in ['chuyen', 'khoan', 'chuyển', 'khoản', 'vcb', 'ct']:
                        name_parts.append(word)
                    else:
                        break
            if name_parts:
                beneficiary_name = ' '.join(name_parts[:4])
            return {'bank_name': bank_name, 'account_number': account_number, 'beneficiary_name': beneficiary_name}

        # Pattern 3: IBFT (liên ngân hàng)
        # Format: xxx-IBFT nội_dung
        pattern3 = re.search(r'\d+-IBFT\s+(.*)', rem)
        if pattern3:
            content = pattern3.group(1)
            # Parse tên ngân hàng từ nội dung
            if 'VCB' in content.upper() or 'VIETCOMBANK' in content.upper():
                bank_name = "Vietcombank"
            elif 'VIETINBANK' in content.upper() or 'CTG' in content.upper():
                bank_name = "Vietinbank"
            elif 'TECHCOMBANK' in content.upper() or 'TCB' in content.upper():
                bank_name = "Techcombank"
            elif 'BIDV' in content.upper():
                bank_name = "BIDV"
            elif 'MB' in content.upper() and 'MBBANK' in content.upper():
                bank_name = "MB Bank"
            elif 'ACB' in content.upper():
                bank_name = "ACB"
            elif 'SACOMBANK' in content.upper() or 'STB' in content.upper():
                bank_name = "Sacombank"
            else:
                bank_name = "Liên ngân hàng"

            # Parse tên người và số TK
            words = content.split()
            name_parts = []
            for word in words:
                if word and (word.isupper() or word[0].isupper()):
                    # Kiểm tra có phải số TK không
                    if re.match(r'^\d{10,20}$', word):
                        account_number = word
                    elif word.lower() not in ['chuyen', 'khoan', 'chuyển', 'khoản', 'ibft', 'ct', 'fcc']:
                        name_parts.append(word)
                    else:
                        if name_parts:  # Đã có tên rồi thì dừng
                            break
            if name_parts:
                beneficiary_name = ' '.join(name_parts[:4])

            return {'bank_name': bank_name, 'account_number': account_number, 'beneficiary_name': beneficiary_name}

        # Không parse được
        return {'bank_name': '', 'account_number': '', 'beneficiary_name': ''}

    def classify_transaction(self, row):
        """
        Phân loại giao dịch

        Args:
            row: DataFrame row chứa thông tin giao dịch

        Returns:
            str: Loại giao dịch
        """
        rem = str(row.get('rem', ''))
        trcdnm = str(row.get('trcdnm', ''))
        amount = row.get('acctccyamt', 0)

        # Chuyển khoản nội bộ Agribank
        if 'MB(' in rem:
            if amount > 0:
                return "Nhận chuyển khoản nội bộ Agribank"
            else:
                return "Chuyển khoản nội bộ Agribank"

        # IBFT
        if 'IBFT' in rem:
            if amount > 0:
                return "Nhận chuyển khoản liên ngân hàng"
            else:
                return "Chuyển khoản liên ngân hàng"

        # Rút tiền
        if 'Withdrawal BankNet ATM' in trcdnm:
            return "Rút tiền ATM"
        if 'RUT TM' in rem.upper() or 'RUT TIEN' in rem.upper():
            return "Rút tiền mặt"

        # Nộp tiền
        if 'Deposit' in trcdnm:
            return "Nộp tiền ATM"
        if 'NOP TIEN' in rem.upper() or 'NOP TM' in rem.upper():
            return "Nộp tiền mặt"

        # Thanh toán
        if 'Debit Purchase' in trcdnm:
            if 'POS' in rem:
                return "Thanh toán POS"
            return "Thanh toán thẻ"

        # Dịch vụ
        if re.search(r'\d{9,11}@\d{9,11}', rem):
            return "Nạp tiền điện thoại"
        if 'MA_GD' in rem and 'PB' in rem:
            return "Thanh toán tiền điện"
        if 'VNPT' in rem.upper():
            return "Thanh toán dịch vụ (VNPT)"

        # Phí và lãi
        if 'PHI THU THEO LO' in trcdnm.upper() or 'PHI' in rem.upper():
            return "Phí dịch vụ"
        if 'LAI TIEN GUI' in trcdnm.upper() or 'LAI' in rem.upper():
            return "Trả lãi tiền gửi"

        # Không xác định được
        return ""

    def parse_date(self, date_value):
        """
        Parse ngày từ nhiều định dạng khác nhau

        Args:
            date_value: Giá trị ngày (có thể là string, datetime, etc.)

        Returns:
            datetime.date hoặc None
        """
        if pd.isna(date_value):
            return None

        # Nếu đã là datetime
        if isinstance(date_value, datetime):
            return date_value.date()

        # Nếu là string, thử parse
        if isinstance(date_value, str):
            # Thử các format phổ biến
            formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt).date()
                except:
                    continue

        return None

    def process(self):
        """
        Xử lý toàn bộ file và trả về dữ liệu đã parse

        Returns:
            list: Danh sách dict chứa thông tin các giao dịch đã parse
        """
        if self.df is None:
            raise ValueError("File chưa được validate. Gọi validate_file() trước.")

        self.processed_data = []

        for idx, row in self.df.iterrows():
            # Bỏ qua các dòng không có dữ liệu quan trọng
            if pd.isna(row.get('trdt')) or pd.isna(row.get('acctccyamt')):
                continue

            stt = idx + 1

            # Parse ngày giao dịch
            transaction_date = self.parse_date(row.get('trdt'))
            if not transaction_date:
                continue

            # Số tiền
            acctccyamt = float(row.get('acctccyamt', 0))
            debit_amount = abs(acctccyamt) if acctccyamt < 0 else 0
            credit_amount = acctccyamt if acctccyamt > 0 else 0

            # Số dư sau giao dịch
            balance = float(row.get('aftrbal', 0))

            # Nội dung gốc
            description = str(row.get('rem', ''))

            # Parse thông tin người thụ hưởng
            tomgntno = row.get('tomgntno', '')
            beneficiary_info = self.parse_beneficiary_info(
                description,
                tomgntno,
                acctccyamt
            )

            # Phân loại giao dịch
            transaction_type = self.classify_transaction(row)

            # Tạo dict cho giao dịch
            transaction = {
                'stt': stt,
                'ngay_giao_dich': transaction_date,
                'so_tien_ghi_no': Decimal(str(debit_amount)),
                'so_tien_ghi_co': Decimal(str(credit_amount)),
                'so_du_sau_gd': Decimal(str(balance)),
                'ngan_hang': beneficiary_info['bank_name'],
                'so_tai_khoan': beneficiary_info['account_number'],
                'ten_nguoi': beneficiary_info['beneficiary_name'],
                'noi_dung': description,
                'ghi_chu': transaction_type,
                # Raw data
                'raw_trcdnm': str(row.get('trcdnm', '')),
                'raw_tomgntno': str(tomgntno),
            }

            self.processed_data.append(transaction)

        return self.processed_data

    def get_summary(self):
        """
        Tính toán thống kê tổng quan

        Returns:
            dict: Thống kê tổng quan
        """
        if not self.processed_data:
            return {
                'total_transactions': 0,
                'total_debit': 0,
                'total_credit': 0,
                'final_balance': 0,
                'by_type': {}
            }

        total_debit = sum(t['so_tien_ghi_no'] for t in self.processed_data)
        total_credit = sum(t['so_tien_ghi_co'] for t in self.processed_data)
        final_balance = self.processed_data[-1]['so_du_sau_gd'] if self.processed_data else 0

        # Thống kê theo loại giao dịch
        by_type = {}
        for t in self.processed_data:
            trans_type = t['ghi_chu']
            if trans_type:
                if trans_type not in by_type:
                    by_type[trans_type] = {
                        'count': 0,
                        'total_debit': Decimal('0'),
                        'total_credit': Decimal('0')
                    }
                by_type[trans_type]['count'] += 1
                by_type[trans_type]['total_debit'] += t['so_tien_ghi_no']
                by_type[trans_type]['total_credit'] += t['so_tien_ghi_co']

        return {
            'total_transactions': len(self.processed_data),
            'total_debit': total_debit,
            'total_credit': total_credit,
            'final_balance': final_balance,
            'by_type': by_type
        }

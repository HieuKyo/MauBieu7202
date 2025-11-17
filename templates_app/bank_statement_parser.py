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

    # Mapping tên viết tắt ngân hàng
    BANK_CODE_MAPPING = {
        'VCB': 'Vietcombank',
        'VIETCOMBANK': 'Vietcombank',
        'TCB': 'Techcombank',
        'TECHCOMBANK': 'Techcombank',
        'BIDV': 'BIDV',
        'CTG': 'Vietinbank',
        'VIETINBANK': 'Vietinbank',
        'MB': 'MB Bank',
        'MBBANK': 'MB Bank',
        'ACB': 'ACB',
        'VPB': 'VPBank',
        'VPBANK': 'VPBank',
        'STB': 'Sacombank',
        'SACOMBANK': 'Sacombank',
        'SCB': 'SCB',
        'VIB': 'VIB',
        'SHB': 'SHB',
        'EXIMBANK': 'Eximbank',
        'EIB': 'Eximbank',
        'MSB': 'MSB',
        'OCB': 'OCB',
        'TPB': 'TPBank',
        'TPBANK': 'TPBank',
        'SEABANK': 'SeABank',
        'HDBank': 'HDBank',
        'LPB': 'LienVietPostBank',
        'LIENVIETPOSTBANK': 'LienVietPostBank',
        'PVCOMBANK': 'PVcomBank',
        'BAB': 'BacABank',
        'BACABANK': 'BacABank',
        'NAB': 'NamABank',
        'NAMABANK': 'NamABank',
        'VAB': 'VietABank',
        'VIETABANK': 'VietABank',
        'PGBANK': 'PGBank',
        'ABB': 'ABBank',
        'ABBANK': 'ABBank',
        'VIETBANK': 'VietBank',
        'NCB': 'NCB',
        'OCEANBANK': 'OceanBank',
        'GPB': 'GPBank',
        'GPBANK': 'GPBank',
        'CIMB': 'CIMB',
        'WOORI': 'Woori Bank',
        'SHINHAN': 'Shinhan Bank',
        'PUBLICBANK': 'Public Bank',
        'NONGHYUP': 'Nonghyup Bank',
        'INDOVINA': 'Indovina Bank',
        'CAKE': 'Cake by VPBank',
        'TIMO': 'Timo by VPBank',
        'UBANK': 'UBank by VPBank',
        'KLB': 'Kiên Long Bank',
        'KIENLONGBANK': 'Kiên Long Bank',
    }

    # Mapping BIN code (Bank Identification Number) từ hệ thống NAPAS
    # BIN code gồm 6 số dùng để định danh ngân hàng trong giao dịch thẻ
    BIN_CODE_MAPPING = {
        '970405': 'Agribank',
        '970422': 'Vietinbank',  # CTG
        '970436': 'Vietcombank',  # VCB
        '970418': 'BIDV',
        '970407': 'Techcombank',  # TCB
        '970432': 'VPBank',
        '970403': 'Sacombank',  # STB
        '970416': 'ACB',
        '970423': 'TPBank',
        '970441': 'VIB',
        '970443': 'SHB',
        '970431': 'Eximbank',
        '970426': 'MB Bank',
        '970448': 'OCB',
        '970414': 'PVcomBank',
        '970433': 'VietABank',
        '970427': 'VietCapital Bank',
        '970438': 'BaoViet Bank',
        '970457': 'Woori Bank',
        '970410': 'Standard Chartered',
        '970424': 'Shinhan Bank',
        '970412': 'HSBC',
        '970419': 'NCB',
        '970406': 'DongA Bank',
        '970437': 'HDBank',
        '970429': 'SCB',
        '970454': 'VietBank',
        '970430': 'PGBank',
        '970425': 'ABBank',
        '970409': 'BacABank',
        '970428': 'NamABank',
        '970458': 'UOB',
        '970434': 'Indovina Bank',
        '970439': 'Public Bank',
        '970415': 'Vietinbank',  # Duplicate entry for legacy
        '970400': 'SaigonBank',
        '970449': 'LienVietPostBank',
        '970452': 'Kiên Long Bank',  # KLB
        '970446': 'Cooperative Bank',
        '970421': 'VRB',
        '970456': 'IBK',
        '970440': 'SeABank',
        '970460': 'CAKE by VPBank',
        '970463': 'Timo by VPBank',
    }

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
            # Đọc file Excel (case-insensitive)
            file_lower = self.file_path.lower()
            if file_lower.endswith('.xls') and not file_lower.endswith('.xlsx'):
                self.df = pd.read_excel(self.file_path, engine='xlrd')
            elif file_lower.endswith('.xlsx'):
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

    def get_bank_name_from_code(self, bank_code):
        """
        Lấy tên đầy đủ ngân hàng từ mã viết tắt

        Args:
            bank_code: Mã viết tắt ngân hàng (VD: VCB, TCB, BIDV, STB)

        Returns:
            str: Tên đầy đủ ngân hàng hoặc mã gốc nếu không tìm thấy
        """
        bank_code_upper = bank_code.upper().strip()
        return self.BANK_CODE_MAPPING.get(bank_code_upper, bank_code)

    def get_bank_name_from_bin(self, bin_code):
        """
        Lấy tên đầy đủ ngân hàng từ BIN code (Bank Identification Number)

        Args:
            bin_code: Mã BIN 6 số của ngân hàng (VD: 970422, 970436)

        Returns:
            str: Tên đầy đủ ngân hàng hoặc 'MCC' nếu không tìm thấy
        """
        bin_code_str = str(bin_code).strip()
        return self.BIN_CODE_MAPPING.get(bin_code_str, 'MCC')

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

        # Pattern 0: Nộp tiền tại Agribank
        # Format: "TÊN NGƯỜI NỘP nộp tiền :" hoặc "TÊN nộp tiền", "NOP TIEN"
        rem_lower = rem.lower()
        if 'nop tien' in rem_lower or 'nộp tiền' in rem_lower:
            bank_name = "Agribank"
            # Parse tên người nộp tiền (ở trước cụm "nộp tiền")
            # Tìm vị trí của "nộp tiền" hoặc "nop tien"
            nop_tien_patterns = [
                (r'([A-Z\s]+)\s*nộp tiền\s*:?', 'nộp tiền'),
                (r'([A-Z\s]+)\s*Nộp tiền\s*:?', 'Nộp tiền'),
                (r'([A-Z\s]+)\s*nop tien\s*:?', 'nop tien'),
                (r'([A-Z\s]+)\s*NOP TIEN\s*:?', 'NOP TIEN'),
            ]
            for pattern, keyword in nop_tien_patterns:
                match = re.search(pattern, rem, re.IGNORECASE)
                if match:
                    name_part = match.group(1).strip()
                    # Làm sạch tên (bỏ các ký tự đặc biệt)
                    name_words = name_part.split()
                    clean_words = [w for w in name_words if w and len(w) > 1]
                    if clean_words:
                        beneficiary_name = ' '.join(clean_words[:5])
                    break
            return {'bank_name': bank_name, 'account_number': account_number, 'beneficiary_name': beneficiary_name}

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

        # Pattern 2: MCC transactions with BIN code (PHẢI CHECK TRƯỚC Pattern 2 general!)
        # Format 1: 1000A17202 - 337221-NGUYEN THI KIM THOA chuyen khoan;MCC;20231220224051;0976831420123;970422
        # Format 2: 679450-7202205158872;MCC;20231226044837;0702281569;970422
        # Pattern: [optional_prefix] [trace]-[content];MCC;[datetime];[account];[BIN]
        if ';MCC;' in rem:  # Quick check trước khi chạy regex phức tạp
            pattern_mcc = re.search(r'(?:1000A\d+ - )?(?:(\d+)-)?([^;]+);MCC;(\d{14});(\d+);(\d{6})', rem)
            if pattern_mcc:
                trace_or_account = pattern_mcc.group(1)  # Could be trace number or account
                content_before_mcc = pattern_mcc.group(2)  # Content before MCC
                datetime_str = pattern_mcc.group(3)  # Transaction datetime
                account_from_pattern = pattern_mcc.group(4)  # Account number
                bin_code = pattern_mcc.group(5)  # BIN code (6 digits)

                # Get bank name from BIN code
                bank_name = self.get_bank_name_from_bin(bin_code)

                # Account number is from the pattern
                account_number = account_from_pattern

                # Parse beneficiary name from content before MCC
                # Content could be: "NGUYEN THI KIM THOA chuyen khoan" or "7202205158872"
                # (số trace đã bị tách ra group 1 rồi)
                if content_before_mcc:
                    # Kiểm tra xem content có phải là tên người không (có chữ cái in hoa)
                    if re.search(r'[A-Z]', content_before_mcc):
                        # Parse tên người, bỏ các từ khóa
                        name_words = content_before_mcc.split()
                        clean_name_parts = []
                        for word in name_words:
                            # Bỏ qua số và các từ khóa
                            if word.isdigit():
                                continue
                            if word.lower() not in ['chuyen', 'khoan', 'chuyển', 'khoản', 'ck', 'ct', 'fcc']:
                                clean_name_parts.append(word)
                            else:
                                break
                        if clean_name_parts:
                            beneficiary_name = ' '.join(clean_name_parts[:4])

                return {'bank_name': bank_name, 'account_number': account_number, 'beneficiary_name': beneficiary_name}

        # Pattern 2.5: MBVCB/IBVCB - Chuyển khoản Vietcombank format đặc biệt
        # Format: MBVCB.5667288555.032551.931922.CT tu 1988944725 NGUYEN DINH TRUONG toi 7202205158872 Phan Giang Nam tai AGRIBANK
        # MBVCB = Mobile Banking VCB, IBVCB = Internet Banking VCB
        if 'VCB.' in rem and ('CT tu' in rem or 'CT TU' in rem.upper()):
            pattern_vcb = re.search(
                r'(?:MB|IB)VCB\.[^.]+\.[^.]+\.[^.]+\.CT tu\s+(\d+)\s+([A-Z\s]+?)\s+toi\s+(\d+)\s+([A-Z\s]+?)\s+tai\s+([A-Z\s]+)',
                rem,
                re.IGNORECASE
            )
            if pattern_vcb:
                bank_name = "Vietcombank"
                account_number = pattern_vcb.group(1)  # Số TK người chuyển
                sender_name = pattern_vcb.group(2).strip()  # Tên người chuyển
                receiver_account = pattern_vcb.group(3)  # Số TK người nhận (TK của user)
                receiver_name = pattern_vcb.group(4).strip()  # Tên người nhận
                receiver_bank = pattern_vcb.group(5).strip()  # Ngân hàng đích

                # Beneficiary là người chuyển tiền
                beneficiary_name = sender_name

                return {'bank_name': bank_name, 'account_number': account_number, 'beneficiary_name': beneficiary_name}

        # Pattern 3: Ngân hàng khác với format chuẩn
        # Format 1: BANK_CODE;số_tài_khoản;nội_dung (VD: STB;070055505932;ck, Vietinbank;102006240267;...)
        # Format 2: mã-BANK_CODE;số_tài_khoản;nội_dung (VD: 337133-BIDV;78810000156950;nam)
        # LƯU Ý: Pattern này có thể nhầm MCC là bank code, nên MCC pattern phải check trước!
        # Cho phép cả chữ hoa và thường: [A-Za-z]
        pattern2_general = re.search(r'(?:(\d+)-)?([A-Za-z]{2,15});(\d{10,20});(.*)', rem, re.IGNORECASE)
        if pattern2_general:
            transaction_code = pattern2_general.group(1)  # Có thể None
            bank_code = pattern2_general.group(2)
            account_number = pattern2_general.group(3)
            content = pattern2_general.group(4)

            # Tra cứu tên ngân hàng
            bank_name = self.get_bank_name_from_code(bank_code)

            # Parse tên người từ content
            words = content.split()
            name_parts = []
            for word in words:
                if word and (word.isupper() or word[0].isupper()):
                    # Bỏ qua các từ khóa
                    if word.lower() not in ['chuyen', 'khoan', 'chuyển', 'khoản', 'ck', 'ct', 'fcc']:
                        name_parts.append(word)
                    else:
                        break
            if name_parts:
                beneficiary_name = ' '.join(name_parts[:4])

            return {'bank_name': bank_name, 'account_number': account_number, 'beneficiary_name': beneficiary_name}

        # Pattern 3: Vietcombank (legacy patterns - giữ lại để backward compatible)
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

        # Pattern 4: IBFT (liên ngân hàng)
        # Format: xxx-IBFT nội_dung
        pattern4 = re.search(r'\d+-IBFT\s+(.*)', rem)
        if pattern4:
            content = pattern4.group(1)
            content_upper = content.upper()

            # Parse tên ngân hàng từ nội dung bằng cách duyệt mapping
            bank_name = "Liên ngân hàng"  # Default
            for code, name in self.BANK_CODE_MAPPING.items():
                if code in content_upper:
                    bank_name = name
                    break

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

        # Lấy số tiền tuyệt đối để check phí rút tiền
        abs_amount = abs(amount)

        rem_lower = rem.lower()
        trcdnm_lower = trcdnm.lower()

        # Chuyển khoản nội bộ Agribank
        if 'MB(' in rem:
            if amount > 0:
                return "Nhận chuyển khoản nội bộ Agribank"
            else:
                return "Chuyển khoản nội bộ Agribank"

        # MCC transactions (merchant/payment)
        if ';MCC;' in rem and re.search(r'\d{6}$', rem):  # Check for BIN code at end
            if amount > 0:
                return "Nhận thanh toán MCC"
            else:
                return "Thanh toán qua MCC"

        # MBVCB/IBVCB - Chuyển khoản Vietcombank format đặc biệt
        if 'VCB.' in rem and ('CT tu' in rem or 'CT TU' in rem.upper()):
            if amount > 0:
                return "Nhận chuyển khoản liên ngân hàng"
            else:
                return "Chuyển khoản liên ngân hàng"

        # Vietcombank legacy format với dấu hai chấm (Vietcombank:số_tk:nội_dung)
        if 'Vietcombank:' in rem or 'vietcombank:' in rem_lower:
            if amount > 0:
                return "Nhận chuyển khoản liên ngân hàng"
            else:
                return "Chuyển khoản liên ngân hàng"

        # Chuyển khoản ngân hàng khác (STB, BIDV, TCB, VCB, Vietinbank, etc.)
        # Pattern: [mã]-[BANK_CODE];số_tk;nội_dung hoặc [BANK_CODE];số_tk;nội_dung
        # Cho phép cả chữ hoa và thường
        if re.search(r'(?:\d+-)?[A-Za-z]{2,15};\d{10,20};', rem, re.IGNORECASE):
            if amount > 0:
                return "Nhận chuyển khoản liên ngân hàng"
            else:
                return "Chuyển khoản liên ngân hàng"

        # IBFT - Kiểm tra cả trong rem và trcdnm
        if 'IBFT' in rem or 'IBFT' in trcdnm or 'ibft' in trcdnm_lower:
            if amount > 0:
                return "Nhận chuyển khoản liên ngân hàng"
            else:
                return "Chuyển khoản liên ngân hàng"

        # Rút tiền với phí cụ thể
        # 1,100 đồng: Rút tiền mặt cùng hệ thống (từ thẻ rút tiền mặt)
        if abs_amount == 1100 and 'rút tiền' in trcdnm_lower and 'từ thẻ rút tiền mặt' in trcdnm_lower:
            return "Phí rút tiền mặt cùng hệ thống"

        # 3,300 đồng: Rút tiền ATM khác hệ thống (Withdrawal BankNet ATM)
        if abs_amount == 3300 and 'withdrawal banknet atm' in trcdnm_lower:
            return "Phí rút tiền ATM khác hệ thống"

        # 1,650 đồng: Rút tiền mặt cùng hệ thống + in sao kê (550 đồng)
        if abs_amount == 1650 and 'rút tiền' in trcdnm_lower and 'từ thẻ rút tiền mặt' in trcdnm_lower:
            return "Phí rút tiền mặt cùng hệ thống (kèm in sao kê)"

        # Rút tiền tổng quát
        if 'Withdrawal BankNet ATM' in trcdnm or 'withdrawal banknet atm' in trcdnm_lower:
            return "Rút tiền ATM khác hệ thống"
        if 'rút tiền' in trcdnm_lower and ('từ thẻ rút tiền mặt' in trcdnm_lower or 'rut tien mat' in trcdnm_lower):
            return "Rút tiền mặt cùng hệ thống"
        if 'RUT TM' in rem.upper() or 'RUT TIEN' in rem.upper():
            return "Rút tiền mặt"

        # Nộp tiền
        if 'Deposit' in trcdnm:
            return "Nộp tiền qua ATM"
        # Nộp tiền tại Agribank (có tên người nộp trong nội dung)
        if 'nop tien' in rem_lower or 'nộp tiền' in rem_lower:
            return "Nộp tiền tại Agribank"
        if 'NOP TM' in rem.upper():
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

        # Lãi tiền gửi - Kiểm tra không có nội dung và trcdnm là "Lãi tiền gửi"
        if (not rem or rem.strip() == '' or rem == 'nan') and 'lãi tiền gửi' in trcdnm_lower.strip():
            return "Trả lãi tiền gửi hằng tháng"

        # Phí và lãi (tổng quát)
        if 'PHI THU THEO LO' in trcdnm.upper() or 'PHI' in rem.upper():
            return "Phí dịch vụ"
        if 'LAI TIEN GUI' in trcdnm.upper() or ('LAI' in rem.upper() and 'GUI' in rem.upper()):
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

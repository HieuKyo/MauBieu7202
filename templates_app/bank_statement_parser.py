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
        'VBA': 'Agribank',  # Vietnam Bank for Agriculture (Agribank)
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

            # Chuẩn hoá tên cột (strip whitespace, lowercase để so sánh)
            self.df.columns = self.df.columns.str.strip()
            col_lower_map = {c.lower(): c for c in self.df.columns}
            # Rename về lowercase nếu cần
            rename_map = {}
            missing_cols = []
            for req in self.REQUIRED_COLUMNS:
                if req in self.df.columns:
                    pass  # Đã đúng
                elif req.lower() in col_lower_map:
                    rename_map[col_lower_map[req.lower()]] = req
                else:
                    missing_cols.append(req)
            if rename_map:
                self.df.rename(columns=rename_map, inplace=True)
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

    def parse_beneficiary_info(self, rem, tomgntno, acctccyamt, toacctno='', lclbrnm='', thrref=''):
        """
        Parse thông tin người thụ hưởng từ nội dung giao dịch

        Args:
            rem: Nội dung giao dịch
            tomgntno: Tài khoản đối ứng
            acctccyamt: Số tiền (âm/dương)
            toacctno: Tài khoản người nhận (cho giao dịch nội bộ Agribank)
            lclbrnm: Tên chi nhánh địa phương (Local Branch Name)
            thrref: Mã ngân hàng đối ứng (VBA = Agribank, VCB = Vietcombank, ...)

        Returns:
            dict: {'bank_name': str, 'account_number': str, 'beneficiary_name': str}
        """
        rem = str(rem)
        bank_name = ""
        account_number = ""
        beneficiary_name = ""

        tomgntno_str = str(tomgntno).strip()
        toacctno_str = str(toacctno).strip()

        # Priority -1: thrref xác định ngân hàng đối ứng trực tiếp
        # VBA = Agribank nội bộ; các mã khác tra BANK_CODE_MAPPING
        if thrref and thrref not in ('', 'nan'):
            thrref_upper = thrref.upper()
            if thrref_upper == 'VBA':
                bank_name = 'Agribank'
                # Số TK đối ứng: nhận tiền lấy từ tomgntno, gửi tiền lấy từ toacctno
                if acctccyamt > 0 and tomgntno_str and tomgntno_str.isdigit():
                    account_number = tomgntno_str
                elif acctccyamt < 0 and toacctno_str and toacctno_str.isdigit():
                    account_number = toacctno_str
                return {'bank_name': bank_name, 'account_number': account_number, 'beneficiary_name': beneficiary_name}
            else:
                mapped = self.BANK_CODE_MAPPING.get(thrref_upper)
                if mapped:
                    bank_name = mapped
                    if acctccyamt > 0 and tomgntno_str and tomgntno_str.isdigit():
                        account_number = tomgntno_str
                    elif acctccyamt < 0 and toacctno_str and toacctno_str.isdigit():
                        account_number = toacctno_str
                    return {'bank_name': bank_name, 'account_number': account_number, 'beneficiary_name': beneficiary_name}

        # Priority 0: Check lclbrnm để xác định bank_name
        # Nếu lclbrnm có "Agribank" → bank_name = "Agribank" + chi tiết chi nhánh
        if lclbrnm and ('agribank' in lclbrnm.lower() or 'agri' in lclbrnm.lower()):
            # Parse tên chi nhánh từ lclbrnm
            # Format: "Agribank CN Vĩnh Châu Sóc Trăng" hoặc "Agribank CN Giá Rai Bạc Liêu"
            if 'CN ' in lclbrnm or 'cn ' in lclbrnm.lower():
                # Lấy phần sau "CN" làm tên chi nhánh
                parts = lclbrnm.split('CN', 1)
                if len(parts) > 1:
                    branch_name = parts[1].strip()
                    bank_name = f"Agribank CN {branch_name}"
                else:
                    bank_name = "Agribank"
            else:
                bank_name = lclbrnm.strip() if lclbrnm else "Agribank"

        # Pattern 0: Nộp tiền tại Agribank
        # Format: "Phạm Ngọc Đặng nộp tiền :", "TRUONG HONG DIEM  nộp tiền :", "nguyễn thị cẩm hường nộp tiền :"
        rem_lower = rem.lower()
        if 'nop tien' in rem_lower or 'nộp tiền' in rem_lower:
            bank_name = "Agribank"
            # Lấy phần text trước "nộp tiền" / "nop tien"
            match = re.search(r'^(.+?)\s*(?:nộp tiền|nop tien)\s*:?', rem, re.IGNORECASE)
            if match:
                name_part = match.group(1).strip()
                name_words = name_part.split()
                clean_words = [w for w in name_words if w and len(w) > 1]
                if clean_words:
                    beneficiary_name = ' '.join(clean_words[:5])
            return {'bank_name': bank_name, 'account_number': account_number, 'beneficiary_name': beneficiary_name}

        # Pattern 1: Chuyển khoản nội bộ Agribank
        # Format MB(mã_giao_dịch)(nội dung) hoặc SMS(mã_giao_dịch)(nội dung)
        pattern1 = re.search(r'(?:MB|SMS)\((\d+)\)\(([^)]*)\)?', rem)
        if pattern1:
            bank_name = "Agribank"
            if acctccyamt > 0 and tomgntno:
                account_number = str(tomgntno)
            elif acctccyamt < 0 and toacctno:
                account_number = str(toacctno)
            # Parse tên từ nội dung trong ngoặc thứ hai
            content = pattern1.group(2).strip()
            _stop = {'chuyen', 'khoan', 'ck', 'ct', 'gui', 'tien', 'nhan', 'thanh', 'toan'}
            name_parts = []
            for word in content.split():
                if word.lower() in _stop:
                    break
                name_parts.append(word)
            beneficiary_name = ' '.join(name_parts[:5]) if name_parts else ''
            return {'bank_name': bank_name, 'account_number': account_number, 'beneficiary_name': beneficiary_name}

        # Pattern 1.5: Chuyển khoản nội bộ/liên ngân hàng (không có MB pattern)
        # Ưu tiên check rem có mã ngân hàng không

        # Kiểm tra rem có phải mã ngân hàng không
        is_bank_code_in_rem = False
        bank_from_rem = ""
        if rem and len(rem.strip()) <= 10:  # rem ngắn có thể là mã ngân hàng
            rem_upper = rem.strip().upper()
            bank_from_rem = self.get_bank_name_from_code(rem_upper)
            # Nếu tìm thấy trong mapping (không phải giữ nguyên rem_upper)
            if bank_from_rem != rem_upper:
                is_bank_code_in_rem = True
                bank_name = bank_from_rem

        # Nếu có tomgntno/toacctno và rem chứa mã ngân hàng
        if (tomgntno_str and len(tomgntno_str) >= 10 and tomgntno_str.isdigit()) or \
           (toacctno_str and len(toacctno_str) >= 10 and toacctno_str.isdigit()):

            if is_bank_code_in_rem:
                # Đã xác định được bank_name từ rem
                if acctccyamt > 0 and tomgntno_str:
                    account_number = tomgntno_str
                elif acctccyamt < 0 and toacctno_str:
                    account_number = toacctno_str

                # Parse tên từ rem nếu có (trừ khi rem chỉ là mã NH)
                if rem and rem.strip() and rem.strip().upper() not in self.BANK_CODE_MAPPING:
                    rem_words = rem.split()
                    name_parts = []
                    for word in rem_words:
                        word_clean = word.strip()
                        if word_clean.lower() not in ['ck', 'ct', 'chuyen', 'khoan', 'tien']:
                            name_parts.append(word_clean)
                    if name_parts:
                        beneficiary_name = ' '.join(name_parts[:5])

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

        # Pattern 2.3: IBFT + tên người trong rem (nhận tiền qua BankNet/NAPAS)
        # VD: "902724-IBFT Son chuyen tien", "003976-IBFT TO KIM THOA chuyen tien"
        # VD: "IBFT NGUYEN HOANG NAM chuyen tien"
        if 'IBFT' in rem.upper():
            pattern_ibft_name = re.search(
                r'IBFT\s+([A-Za-z][A-Za-z\s]+?)(?:\s+(?:chuyen|ck|ct|gui|tra|nop|thanh|toan)|$)',
                rem,
                re.IGNORECASE
            )
            if pattern_ibft_name:
                raw_name = pattern_ibft_name.group(1).strip()
                # Khi nhận tiền (amount > 0): tên sau IBFT là người gửi → hiển thị làm beneficiary
                bname = raw_name if acctccyamt > 0 else ''
                return {'bank_name': '', 'account_number': '', 'beneficiary_name': bname}

        # Pattern 2.4: BankNet IBFT format - [trace]-[BankName][account][name] [desc]
        # VD: 897749-Vietcombank1037050854NGUYEN CONG DANH chuyen khoan s dat chuyen
        pattern_banknet = re.search(
            r'(?:\d+-)?([A-Za-z]+)(\d{8,20})([A-Z][A-Z\s]+?)(?:\s+(?:chuyen|ck|ct|gui|tra|nop|thanh|toan|s\s|so\s)|$)',
            rem,
            re.IGNORECASE
        )
        if pattern_banknet:
            raw_bank = pattern_banknet.group(1).strip()
            acct = pattern_banknet.group(2).strip()
            raw_name = pattern_banknet.group(3).strip()
            bank = self.get_bank_name_from_code(raw_bank)
            if not bank:
                bank = raw_bank.capitalize()
            # Tên trong rem là chủ TK (người gửi) → chỉ hiển thị khi nhận tiền vào
            bname = raw_name if acctccyamt > 0 else ''
            return {'bank_name': bank, 'account_number': acct, 'beneficiary_name': bname}

        # Pattern 2.5: MBVCB/IBVCB - Chuyển khoản Vietcombank format đặc biệt
        # Format mới: MBVCB.5667288555.032551.931922.CT tu 1988944725 NGUYEN DINH TRUONG toi 7202205158872 Phan Giang Nam tai AGRIBANK
        # Format mới: 969816-MBVCB.3250279254.057991.PHAM LE NGOC TRAN chuyen tien.CT tu 0891000651394 PHAM LE NGOC TRAN toi 7202205158872 PHAN GIANG NAM Ngan hang...
        # Format cũ: 971906-MBVCB191049425.Chi Thu gui.CT tu 0511000450997 LAM HAI VI toi 7202205112842 NGUYEN CONG DANH NNO PT
        # MBVCB = Mobile Banking VCB, IBVCB = Internet Banking VCB
        if 'VCB' in rem.upper() and ('CT tu' in rem or 'CT TU' in rem.upper()):
            # Try Pattern 1 (with "tai" keyword)
            pattern_vcb_v1 = re.search(
                r'(?:\d+-)?(?:MB|IB)VCB\.[^.]+\.[^.]+\.[^.]+\.CT tu\s+(\d+)\s+([A-Z\s]+?)\s+toi\s+(\d+)\s+([A-Z\s]+?)\s+tai\s+([A-Z\s]+)',
                rem,
                re.IGNORECASE
            )
            if pattern_vcb_v1:
                bank_name = "Vietcombank"
                account_number = pattern_vcb_v1.group(1)  # Số TK người chuyển
                sender_name = pattern_vcb_v1.group(2).strip()  # Tên người chuyển
                receiver_account = pattern_vcb_v1.group(3)  # Số TK người nhận (TK của user)
                receiver_name = pattern_vcb_v1.group(4).strip()  # Tên người nhận
                receiver_bank = pattern_vcb_v1.group(5).strip()  # Ngân hàng đích

                # Beneficiary là người chuyển tiền
                beneficiary_name = sender_name

                return {'bank_name': bank_name, 'account_number': account_number, 'beneficiary_name': beneficiary_name}

            # Try Pattern 2 (without "tai", ending with "Ngan hang" or similar)
            pattern_vcb_v2 = re.search(
                r'(?:\d+-)?(?:MB|IB)VCB\.[^.]+\.[^.]+\.[^.]+\.CT tu\s+(\d+)\s+([A-Z\s]+?)\s+toi\s+(\d+)\s+([A-Z\s]+?)(?:\s+Ngan\s+hang|\s+NH|\s*$)',
                rem,
                re.IGNORECASE
            )
            if pattern_vcb_v2:
                bank_name = "Vietcombank"
                account_number = pattern_vcb_v2.group(1)  # Số TK người chuyển
                sender_name = pattern_vcb_v2.group(2).strip()  # Tên người chuyển
                receiver_account = pattern_vcb_v2.group(3)  # Số TK người nhận (TK của user)
                receiver_name = pattern_vcb_v2.group(4).strip()  # Tên người nhận

                # Beneficiary là người chuyển tiền
                beneficiary_name = sender_name

                return {'bank_name': bank_name, 'account_number': account_number, 'beneficiary_name': beneficiary_name}

            # Format cũ: 971906-MBVCB191049425.Chi Thu gui.CT tu 0511000450997 LAM HAI VI toi 7202205112842 ...
            # MBVCB tiếp liền với số tham chiếu (không có dấu chấm giữa VCB và số)
            pattern_vcb_old = re.search(
                r'(?:\d+-)?(?:MB|IB)VCB\d+\..*?\.+CT\s+tu\s+(\d+)\s+([A-Z][A-Z\s]+?)\s+toi\s+(\d+)\s+([A-Z][A-Z\s]+?)(?:\s+NNO|\s+AGRIBANK|\s+Nong|$)',
                rem,
                re.IGNORECASE
            )
            if pattern_vcb_old:
                bank_name = "Vietcombank"
                account_number = pattern_vcb_old.group(1)   # Số TK người chuyển
                sender_name = pattern_vcb_old.group(2).strip()
                beneficiary_name = sender_name
                return {'bank_name': bank_name, 'account_number': account_number, 'beneficiary_name': beneficiary_name}

        # Pattern 2.6: BankName:account:content (dấu hai chấm, VD: Vietcombank:1028442818:NGUYEN TRIET DAM chuyen khoan)
        pattern_colon = re.search(r'([A-Za-z]{3,20}):([A-Za-z0-9]{4,25}):(.*)', rem, re.IGNORECASE)
        if pattern_colon:
            raw_bank = pattern_colon.group(1).strip()
            acct = pattern_colon.group(2).strip()
            bank = self.get_bank_name_from_code(raw_bank)
            if not bank or bank == raw_bank:
                bank = raw_bank.capitalize()
            return {'bank_name': bank, 'account_number': acct, 'beneficiary_name': ''}

        # Pattern 3: Ngân hàng khác với format chuẩn
        # Format 1: BANK_CODE;số_tài_khoản;nội_dung (VD: STB;070055505932;ck, Vietinbank;102006240267;...)
        # Format 2: mã-BANK_CODE;số_tài_khoản;nội_dung (VD: 337133-BIDV;78810000156950;nam, 907666-MB;871888999;...)
        # LƯU Ý: Pattern này có thể nhầm MCC là bank code, nên MCC pattern phải check trước!
        # Cho phép cả chữ hoa và thường: [A-Za-z]
        # Số/mã TK từ 4-25 ký tự (chữ+số) để bắt được TK ngắn (OCB 5 số) và TK alphanumeric (VPB ZLP...)
        pattern2_general = re.search(r'(?:(\d+)-)?([A-Za-z]{2,15});([A-Za-z0-9]{4,25});(.*)', rem, re.IGNORECASE)
        if pattern2_general:
            transaction_code = pattern2_general.group(1)  # Có thể None
            bank_code = pattern2_general.group(2)
            account_number = pattern2_general.group(3)
            content = pattern2_general.group(4)

            # Tra cứu tên ngân hàng
            bank_name = self.get_bank_name_from_code(bank_code)

            # Chỉ parse tên người khi là giao dịch nhận tiền (acctccyamt > 0)
            # Khi chuyển tiền đi (acctccyamt < 0), tên trong rem là tên người gửi (chủ TK), không phải người thụ hưởng
            if acctccyamt > 0:
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

        # Fallback: rem là văn bản tự do, parse tên từ các từ VIẾT HOA liên tiếp đầu chuỗi
        # VD: "HUYNH THI THU MAI TRA TIEN CUA SAN BAY." → "HUYNH THI THU MAI"
        if rem and rem.strip():
            words = rem.strip().split()
            name_parts = []
            _stop = {'CHUYEN', 'TIEN', 'CT', 'CK', 'GD', 'TRA', 'GUI', 'MUA', 'BAN', 'THANH', 'TOAN', 'NHAN', 'NAP', 'RUT', 'PHI', 'LAI', 'TOPUP'}
            for word in words:
                clean_word = word.rstrip('.,;:')
                if clean_word and clean_word.isupper() and len(clean_word) >= 2 and clean_word.isalpha() and clean_word not in _stop:
                    name_parts.append(clean_word)
                else:
                    break
            if len(name_parts) >= 2:  # Ít nhất 2 từ mới coi là tên người
                beneficiary_name = ' '.join(name_parts[:5])
                return {'bank_name': 'Agribank', 'account_number': '', 'beneficiary_name': beneficiary_name}

        return {'bank_name': '', 'account_number': '', 'beneficiary_name': ''}

    def classify_transaction(self, row):
        """
        Phân loại giao dịch

        Args:
            row: DataFrame row chứa thông tin giao dịch

        Returns:
            str: Loại giao dịch
        """
        rem     = str(row.get('rem', ''))
        trcdnm  = str(row.get('trcdnm', ''))
        trcd    = str(row.get('trcd', '')).strip()
        amount  = row.get('acctccyamt', 0)
        thrref  = str(row.get('thrref', '')).strip()

        abs_amount   = abs(amount)
        rem_lower    = rem.lower()
        trcdnm_lower = trcdnm.lower()

        husrid  = str(row.get('husrid', '')).strip()
        lclbrnm = str(row.get('lclbrnm', '')).strip()
        ourref  = str(row.get('ourref', '')).strip()

        # ── Ưu tiên cao nhất: dựa vào trcd (mã loại giao dịch) ───────────
        # W000: Mở tài khoản
        if trcd == 'W000':
            return "Mở tài khoản"

        # Giải ngân
        if '7202LDS' in rem:
            return "Giải ngân"

        # Nạp tiền điện thoại / mua thẻ - rem chứa "Topup"
        if 'topup' in rem_lower and amount < 0:
            return "Nạp tiền điện thoại"

        # Chuyển khoản nội bộ Agribank - Pattern MB(xxx)(yyy) hoặc SMS(xxx)(yyy)
        if 'MB(' in rem or 'SMS(' in rem:
            return "Nhận chuyển khoản nội bộ Agribank" if amount > 0 else "Chuyển khoản nội bộ Agribank"

        # Lãi tiền gửi: trcdnm chứa "lãi tiền gửi" và rem trống
        if ('lãi tiền gửi' in trcdnm_lower or 'lai tien gui' in trcdnm_lower) and (not rem or rem.strip() in ('', 'nan')):
            return "Trả lãi tiền gửi hàng tháng"

        # ── Phí dịch vụ — kiểm tra rem sớm, trước các check trcdnm ─────────
        # Ưu tiên cao để tránh bị nhầm thành "Rút tiền mặt" do trcdnm
        if rem and amount < 0:
            rem_upper = rem.upper()
            _FEE_KEYWORDS = [
                'PHI SMS', 'PHISMS',
                'THU PHI QUAN LY TAI KHOAN', 'PHI QUAN LY TAI KHOAN',
                'THU PHI THUONG NIEN', 'PHI THUONG NIEN',
                'PHI DICH VU E-MOBILE BANKING', 'E-MOBILE BANKING', 'EMOBILE BANKING',
                'ANNUAL FEE',
                'PHI DICH VU', 'PHI QUAN LY',
                'PHI THU THEO LO',
            ]
            if any(k in rem_upper for k in _FEE_KEYWORDS) or 'ABIC' in rem_upper:
                return "Phí dịch vụ"

        # ── Thanh toán hóa đơn — ưu tiên trước tất cả check trcd ──────────────
        # MA_GD: là mã thanh toán hóa đơn hệ thống Agribank (điện, nước, viễn thông...)
        if 'MA_GD:' in rem.upper():
            return "Thanh toán hóa đơn"
        # MAP(số)(nội dung) — hệ thống thanh toán hóa đơn qua SMS/Mobile Banking
        if re.search(r'MAP\(\d+\)', rem, re.IGNORECASE):
            return "Thanh toán hóa đơn"

        # trcd C204: Rút tiền bằng thẻ 24/24 (ATM)
        # fndtpcd=101 → tiền mặt thực rút; fndtpcd=198 → phí dịch vụ kèm theo
        if trcd == 'C204' and amount < 0:
            fndtpcd = str(row.get('fndtpcd', '')).strip()
            if fndtpcd == '198':
                return "Phí rút tiền ATM"
            return "Rút tiền ATM"

        # trcd W100: Nộp tiền mặt tại quầy ngân hàng
        if trcd == 'W100' and amount > 0:
            return "Nộp tiền tại quầy"

        # trcd W200: Rút tiền TG KKH tại quầy
        if trcd == 'W200' and amount < 0:
            return "Rút tiền mặt"

        # trcd X204: Withdrawal BankNet ATM (rút tiền tại ATM ngân hàng khác qua BankNet/NAPAS)
        # fndtpcd=101 → tiền thực rút; fndtpcd=198 → phí dịch vụ
        if trcd == 'X204' and amount < 0:
            fndtpcd = str(row.get('fndtpcd', '')).strip()
            if fndtpcd == '198':
                return "Phí rút tiền ATM khác hệ thống"
            return "Rút tiền ATM khác hệ thống"

        # trcd X202: Giao dịch qua thẻ tại ATM Agribank (Rút tiền ATM cùng hệ thống)
        # fndtpcd=101 → tiền thực rút/chuyển; fndtpcd=198 → phí dịch vụ kèm theo
        if trcd == 'X202' and amount < 0:
            fndtpcd = str(row.get('fndtpcd', '')).strip()
            if fndtpcd == '198':
                if 'rút tiền' in trcdnm_lower or 'rut tien' in trcdnm_lower:
                    return "Phí rút tiền ATM cùng hệ thống"
                return "Phí chuyển khoản ATM"
            if 'rút tiền' in trcdnm_lower or 'rut tien' in trcdnm_lower:
                return "Rút tiền ATM cùng hệ thống"
            return "Chuyển khoản nội bộ Agribank"

        # trcd X207: Hủy rút tiền ATM cùng hệ thống (đảo bút toán X202)
        if trcd == 'X207':
            fndtpcd = str(row.get('fndtpcd', '')).strip()
            if fndtpcd == '198':
                return "Hoàn phí rút tiền ATM cùng hệ thống"
            return "Hủy rút tiền ATM cùng hệ thống"

        # tomgntno hoặc ourref dạng [số]ITL[số] → nội bộ Agribank khác chi nhánh
        _itl_field = str(row.get('tomgntno', '')).strip() or str(row.get('ourref', '')).strip()
        if re.search(r'\d+ITL\d+', _itl_field, re.IGNORECASE):
            if amount > 0:
                return "Nhận chuyển khoản nội bộ Agribank"
            else:
                return "Chuyển khoản nội bộ Agribank"

        # trcdnm chứa "Rút tiền" → ưu tiên phân loại trước khi vào logic nội bộ/liên NH
        # Tránh trường hợp bị nhầm thành chuyển khoản do husrid/lclbrnm Agribank
        # NGOẠI LỆ: rem chứa pattern liên ngân hàng rõ ràng → không dùng trcdnm
        _rem_is_interbank = bool(
            re.search(r'[A-Za-z]{2,15};[A-Za-z0-9]{4,25};', rem) or
            re.search(r'[A-Za-z]+:[A-Za-z0-9]{4,25}:', rem) or
            'VCB.' in rem or 'MBVCB' in rem or 'IBVCB' in rem
        )
        if amount < 0 and ('rút tiền' in trcdnm_lower or 'rut tien' in trcdnm_lower) and not _rem_is_interbank:
            if 'từ thẻ rút tiền mặt' in trcdnm_lower or 'thẻ 24/24' in trcdnm_lower or 'bằng thẻ' in trcdnm_lower:
                # Phân biệt phí và tiền thực rút
                if abs_amount in (1100, 1650):
                    return "Phí rút tiền mặt cùng hệ thống"
                if abs_amount == 3300:
                    return "Phí rút tiền ATM"
                return "Rút tiền ATM"
            return "Rút tiền mặt"

        # trcd X101 + rem ATM Fund Transfer = nhận chuyển khoản từ ATM Agribank nội bộ
        if trcd == 'X101' and amount > 0 and 'atm fund transfer' in rem_lower:
            return "Nhận chuyển khoản từ ATM"

        # trcd X101 + thrref=VBA = nhận chuyển khoản nội bộ qua ATM
        if trcd == 'X101' and amount > 0 and thrref.upper() == 'VBA':
            return "Nhận chuyển khoản từ ATM"

        # ── Xác định nguồn gốc giao dịch ─────────────────────────────────
        is_internal_agribank = False
        is_interbank = False

        # Priority 0a: thrref = VBA → Agribank nội bộ
        if thrref.upper() == 'VBA':
            is_internal_agribank = True

        # Priority 0b: lclbrnm chứa "Agribank"
        elif lclbrnm and ('agribank' in lclbrnm.lower() or 'agri' in lclbrnm.lower()):
            is_internal_agribank = True

        # Priority 0c: thrref là mã ngân hàng khác (không phải VBA)
        elif thrref and thrref.upper() in self.BANK_CODE_MAPPING and thrref.upper() != 'VBA':
            is_interbank = True

        # Priority 0d: thrref chứa BANKNET hoặc IBFT → giao dịch liên ngân hàng qua BankNet/NAPAS
        elif thrref and ('BANKNET' in thrref.upper() or 'IBFT' in thrref.upper()):
            is_interbank = True

        # Priority 1: rem ngắn chứa mã ngân hàng
        if not is_internal_agribank and not is_interbank:
            if rem and len(rem.strip()) <= 10:
                rem_upper = rem.strip().upper()
                if rem_upper in self.BANK_CODE_MAPPING or rem_upper in ['AGRIBANK', 'AGRI']:
                    bank_from_rem = self.BANK_CODE_MAPPING.get(rem_upper, rem_upper)
                    if bank_from_rem == 'Agribank' or rem_upper in ['AGRIBANK', 'AGRI']:
                        is_internal_agribank = True
                    else:
                        is_interbank = True

        # Priority 2: husrid format Agribank
        if not is_internal_agribank and not is_interbank:
            # Format GDV: 8 ký tự toàn chữ cái (GRATNNHI, GRATKIEN...)
            branch_codes = ['GRA', 'HOB', 'HAN', 'SGN', 'DNA', 'CTO', 'BTR', 'BDG', 'HUE',
                            'VTU', 'QNI', 'KHA', 'DLK', 'BIN', 'PTH', 'GLA', 'NTR', 'BTE',
                            'KGI', 'BLU', 'CMU', 'VLO', 'LAI', 'YEN']
            if husrid and len(husrid) == 8 and husrid.isalpha() and husrid[:3].upper() in branch_codes:
                is_internal_agribank = True
            # Format ATM: 4 chữ số mã CN + "ATM" + số hiệu (VD: 6480ATM02, 6460ATM01)
            elif husrid and re.match(r'^\d{4}ATM\d+$', husrid, re.IGNORECASE):
                is_internal_agribank = True

        # Nếu là giao dịch nội bộ Agribank — chỉ phân loại chuyển khoản ở đây;
        # rút tiền/nộp tiền để các check phía dưới xử lý chính xác hơn
        if is_internal_agribank:
            _is_withdrawal = amount < 0 and (
                'rut' in rem_lower or 'rút' in rem_lower or
                'rut tien' in trcdnm_lower or 'rút tiền' in trcdnm_lower or
                '7202atm' in rem_lower or 'rut tm' in rem.upper() or
                'withdrawal' in trcdnm_lower
            )
            _is_deposit = amount > 0 and (
                'nop tien' in rem_lower or 'nộp tiền' in rem_lower or
                'nop tm' in rem.upper() or 'deposit' in trcdnm_lower
            )
            _is_fee_or_service = any(k in rem_lower for k in ['atm', 'pos', 'mcc', 'phi', 'lai', 'vnpt', 'ma_gd'])

            if not _is_withdrawal and not _is_deposit and not _is_fee_or_service:
                # Không phải rút/nộp/phí → chuyển khoản nội bộ
                if amount > 0:
                    return "Nhận chuyển khoản nội bộ Agribank"
                else:
                    return "Chuyển khoản nội bộ Agribank"
            # Nếu là rút/nộp/phí → tiếp tục xuống để xử lý đúng loại

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
                return "Chuyển khoản đi khác ngân hàng"

        # Vietcombank legacy format với dấu hai chấm (Vietcombank:số_tk:nội_dung)
        if 'Vietcombank:' in rem or 'vietcombank:' in rem_lower:
            if amount > 0:
                return "Nhận chuyển khoản liên ngân hàng"
            else:
                return "Chuyển khoản đi khác ngân hàng"

        # Chuyển khoản ngân hàng khác (STB, BIDV, TCB, VCB, Vietinbank, MB, KLB, etc.)
        # Pattern: [mã]-[BANK_CODE];số_tk;nội_dung hoặc [BANK_CODE];số_tk;nội_dung
        # TK từ 4-25 ký tự (chữ+số): bắt TK ngắn (OCB 5 số) và TK alphanumeric (VPB ZLP...)
        if re.search(r'(?:\d+-)?[A-Za-z]{2,15};[A-Za-z0-9]{4,25};', rem, re.IGNORECASE):
            if amount > 0:
                return "Nhận chuyển khoản liên ngân hàng"
            else:
                return "Chuyển khoản đi khác ngân hàng"

        # IBFT - Kiểm tra cả trong rem và trcdnm
        if 'IBFT' in rem or 'IBFT' in trcdnm or 'ibft' in trcdnm_lower:
            if amount > 0:
                return "Nhận chuyển khoản liên ngân hàng"
            else:
                return "Chuyển khoản đi khác ngân hàng"

        # Interbank transfers (đã xác định từ rem ở trên)
        if is_interbank:
            if amount > 0:
                return "Nhận chuyển khoản liên ngân hàng"
            else:
                return "Chuyển khoản đi khác ngân hàng"

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
        # Rút tiền ATM với mã 7202ATM trong nội dung
        if '7202ATM' in rem:
            return "Rút tiền ATM"
        # Rút tiền mặt (bao gồm RUT TM, RUT TIEN, RUT TK)
        if 'RUT TM' in rem.upper() or 'RUT TIEN' in rem.upper() or 'RUT TK' in rem.upper() or 'rut tk' in rem_lower:
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
        # Pattern 1: Debit Purchase (thẻ ghi nợ)
        if 'Debit Purchase' in trcdnm:
            if 'POS' in rem:
                return "Thanh toán POS"
            return "Thanh toán thẻ"

        # Pattern 2: Purchase BankNet POS (thanh toán POS qua BankNet)
        # Check: trcdnm có "Purchase" và "POS", hoặc husrid có pattern "1000PO"
        if ('Purchase' in trcdnm and 'POS' in trcdnm) or (husrid and husrid.startswith('1000PO')):
            return "Thanh toán POS"

        # Pattern 3: Purchase tổng quát (không phải POS)
        if 'Purchase' in trcdnm and amount < 0:
            return "Thanh toán thẻ"

        # Dịch vụ
        # Nạp tiền điện thoại - đổi thành Thanh toán dịch vụ
        if re.search(r'\d{9,11}@\d{9,11}', rem):
            return "Thanh toán dịch vụ"
        # C/C Transfer TO - Thanh toán dịch vụ
        if 'C/C Transfer TO' in rem or 'c/c transfer to' in rem_lower:
            return "Thanh toán dịch vụ"
        if 'VNPT' in rem.upper():
            return "Thanh toán dịch vụ (VNPT)"

        # Phí và lãi (tổng quát)
        if 'PHI THU THEO LO' in trcdnm.upper():
            return "Phí dịch vụ"
        if 'LAI TIEN GUI' in trcdnm.upper() or ('LAI' in rem.upper() and 'GUI' in rem.upper()):
            return "Trả lãi tiền gửi"

        # Giao dịch đặc biệt dựa vào husrid
        husrid = str(row.get('husrid', ''))
        if husrid and len(husrid) >= 7:
            # PaymentHub: husrid starts with '7202API'
            if husrid[:7] == '7202API':
                if amount > 0:
                    return "Nhận tiền qua PaymentHub"
                else:
                    return "Thanh toán qua PaymentHub"
            # OSB: husrid starts with '7202OSB'
            elif husrid[:7] == '7202OSB':
                if amount > 0:
                    return "Nhận tiền qua OSB"
                else:
                    return "Chuyển tiền qua OSB"

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

    @staticmethod
    def parse_itl_file(file_path):
        """
        Parse file FXIR64 (Lấy số liệu ITL - Search Customer Number).
        Trả về dict {trref: ordcust} để tra cứu tên người chuyển cho giao dịch ITL.

        Args:
            file_path: Đường dẫn đến file FXIR64 (.xlsx / .xls / .txt tab-separated)

        Returns:
            dict: {mã_ITL: tên_người_chuyển}  VD: {'7202ITL161013516': 'Lê Thị Hơn'}
        """
        try:
            ext = str(file_path).lower()
            if ext.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path, dtype=str)
            else:
                # Tab-separated text export từ hệ thống Agribank
                df = pd.read_csv(file_path, sep='\t', dtype=str, encoding='utf-8-sig')

            df.columns = [str(c).strip().lower() for c in df.columns]

            mapping = {}
            for _, row in df.iterrows():
                trref = str(row.get('trref', '')).strip()
                ordcust = str(row.get('ordcust', '')).strip()
                if trref and ordcust and ordcust.lower() != 'nan':
                    mapping[trref] = ordcust
            return mapping
        except Exception:
            return {}

    def process(self, itl_mapping=None):
        """
        Xử lý toàn bộ file và trả về dữ liệu đã parse

        Args:
            itl_mapping: dict {trref: ordcust} từ file FXIR64 (tùy chọn).
                         Nếu cung cấp, tên người chuyển của giao dịch ITL sẽ được
                         lấy từ cột ordcust thay vì parse từ rem.

        Returns:
            list: Danh sách dict chứa thông tin các giao dịch đã parse
        """
        if self.df is None:
            raise ValueError("File chưa được validate. Gọi validate_file() trước.")

        self.processed_data = []
        stt_counter = 0

        for idx, row in self.df.iterrows():
            # Bỏ qua dòng header lặp lại giữa file (trdt = 'trdt')
            trdt_val = row.get('trdt')
            if str(trdt_val).strip().lower() == 'trdt':
                continue

            # Bỏ qua các dòng không có dữ liệu quan trọng
            if pd.isna(trdt_val) or pd.isna(row.get('acctccyamt')):
                continue

            stt_counter += 1
            stt = stt_counter

            # Parse ngày giao dịch
            transaction_date = self.parse_date(trdt_val)
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

            # Các trường bổ sung
            tomgntno = row.get('tomgntno', '')
            toacctno = row.get('toacctno', '')
            lclbrnm  = str(row.get('lclbrnm', ''))
            thrref   = str(row.get('thrref', '')).strip()
            husrid   = str(row.get('husrid', '')).strip()
            ourref   = str(row.get('ourref', '')).strip()

            # Parse thông tin người thụ hưởng
            beneficiary_info = self.parse_beneficiary_info(
                description,
                tomgntno,
                acctccyamt,
                toacctno,
                lclbrnm,
                thrref,
            )

            # Fallback: xác định ngân hàng từ husrid đặc biệt
            if not beneficiary_info['bank_name']:
                if husrid.startswith('7202API'):
                    beneficiary_info['bank_name'] = 'PaymentHub'
                elif husrid.startswith('7202OSB'):
                    beneficiary_info['bank_name'] = 'OSB'
                # ATM nội bộ Agribank: husrid = 4chữsố + ATM + số (VD: 6360ATM05)
                elif re.match(r'^\d{4}ATM\d+$', husrid, re.IGNORECASE):
                    beneficiary_info['bank_name'] = 'Agribank'
                    tomgntno_str = str(tomgntno).strip()
                    if not beneficiary_info['account_number'] and tomgntno_str and tomgntno_str.isdigit():
                        beneficiary_info['account_number'] = tomgntno_str

            # Phân loại giao dịch
            transaction_type = self.classify_transaction(row)

            # Các loại phí nội bộ Agribank → bank_name = Agribank
            _FEE_TYPES = {
                'Phí dịch vụ',
                'Phí rút tiền ATM', 'Phí rút tiền ATM cùng hệ thống',
                'Phí rút tiền ATM khác hệ thống', 'Phí chuyển khoản ATM',
                'Phí rút tiền mặt cùng hệ thống',
                'Hoàn phí rút tiền ATM cùng hệ thống',
                'Trả lãi tiền gửi hàng tháng', 'Trả lãi tiền gửi hằng tháng', 'Trả lãi tiền gửi',
                'Mở tài khoản', 'Nạp tiền điện thoại',
                'Rút tiền mặt', 'Nộp tiền tại quầy',
                'Thanh toán tiền điện', 'Thanh toán hóa đơn',
            }
            if transaction_type in _FEE_TYPES and not beneficiary_info['bank_name']:
                beneficiary_info['bank_name'] = 'Agribank'

            # Giao dịch ITL (nội bộ Agribank khác chi nhánh) → bank=Agribank, account=mã ITL
            # Kiểm tra tomgntno trước, fallback sang ourref
            _itl_val = str(row.get('tomgntno', '')).strip()
            if not re.search(r'\d+ITL\d+', _itl_val, re.IGNORECASE):
                _itl_val = str(row.get('ourref', '')).strip()
            if re.search(r'\d+ITL\d+', _itl_val, re.IGNORECASE):
                beneficiary_info['bank_name'] = 'Agribank'
                beneficiary_info['account_number'] = _itl_val
                # Lấy tên người chuyển từ file FXIR64 nếu có (chỉ cho GD nhận tiền)
                if itl_mapping and acctccyamt > 0:
                    sender_name = itl_mapping.get(_itl_val, '')
                    if sender_name:
                        beneficiary_info['beneficiary_name'] = sender_name

            # Giao dịch tiền ra (< 0): tên trong rem là chủ TK người gửi, không phải người thụ hưởng
            if acctccyamt < 0:
                beneficiary_info['beneficiary_name'] = ''

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

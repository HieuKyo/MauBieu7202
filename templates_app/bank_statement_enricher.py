"""
Bổ sung thông tin đối tác (tên, số TK, ngân hàng) cho sao kê DPTB18
từ các file đối soát CSP / MSPH02 chiều đi và chiều đến.

Quy tắc khớp với DPTB18 (đã kiểm chứng trên dữ liệu thật):
- MSPH02 (đi/đến):  cột trace       = cột thrref của DPTB18
- CSP chiều đến:    cột TRACE IPCAS = mã 6 số đầu rem ("678144-..." hoặc "1000A87202 - 678144-...")
- CSP chiều đi:     dòng 369-Transfer Debit, cột TRACE = mã 6 số đầu rem;
                    số TK / ngân hàng nhận lấy từ dòng 91-Transfer Credit cùng REMARK + số tiền
                    tên người nhận lấy từ cột TO_ACCOUNT_REMARK (nếu có), không có thì đối chiếu chéo
Mọi phép khớp đều kiểm tra thêm chiều tiền (vào/ra) và số tiền bằng nhau.
"""
import re
import pandas as pd

from .bank_statement_parser import BankStatementParser


AUX_FILES = {
    'msph02_den': 'MSPH02 chiều đến',
    'msph02_di': 'MSPH02 chiều đi',
    'csp_den': 'CSP chiều đến',
    'csp_di': 'CSP chiều đi',
}

_MSPH02_COLS = ['trace', 'sttlamt', 'rspcd', 'nh_nhan_gui_nhan', 'noi_dung',
                'ten_nguoi_chuyen', 'ten_nguoi_nhan', 'ngay_giao_dich', 'tk_chuyen', 'tk_nhan']
REQUIRED_COLUMNS = {
    'msph02_den': _MSPH02_COLS,
    'msph02_di': _MSPH02_COLS,
    'csp_den': ['TRANSACTION TIME', 'FROM ACCOUNT', 'SENDER NAME', 'AMOUNT', 'STATUS',
                'CONTENT', 'TRACE IPCAS', 'FROM BANK CODE'],
    'csp_di': ['TRANSACTION TIME', 'TO_ACCOUNT', 'TRANCODE', 'AMOUNT', 'TRACE',
               'RESPONSE', 'REMARK', 'TO_BANK_CODE'],
}

# Trạng thái MSPH02 được coi là giao dịch thành công (có hạch toán vào DPTB18)
_MSPH02_SUCCESS = {'Đã trả KH', 'Hoàn thành'}

# Tên ngân hàng đầy đủ trong cột nh_nhan_gui_nhan (MSPH02) → tên ngắn.
# So khớp theo cụm từ (không phân biệt hoa thường); không có trong bảng thì giữ nguyên.
_MSPH02_BANK_NAMES = [
    ('NH NT Viet Nam', 'Vietcombank'),
    ('Quân đội', 'MB Bank'),
    ('Công thương', 'Vietinbank'),
    ('Đầu tư và Phát triển', 'BIDV'),
    ('Phương Đông', 'OCB'),
    ('Sài gòn thương tín', 'Sacombank'),
    ('Phát triển TP Ho chi Minh', 'HDBank'),
    ('Xuất Nhập Khẩu', 'Eximbank'),
    ('Sài gòn-Hà nội', 'SHB'),
    ('Số Vikki', 'Vikki Bank'),
    ('Thịnh Vượng và Phát triển', 'PGBank'),
    ('Việt Nam Thịnh Vượng', 'VPBank'),
    ('Lộc Phát', 'LPBank'),
    ('Kỹ thương', 'Techcombank'),
    ('Đông Nam á', 'SeABank'),
    ('á Châu', 'ACB'),
    ('Hàng Hải', 'MSB'),
    ('Bản Việt', 'BVBank'),
    ('SHINHAN', 'Shinhan Bank'),
    ('INDOVINA', 'Indovina Bank'),
]

_REM_TRACE_RE = re.compile(r'(?:^|- )(\d{6})-')


def _s(value):
    """Giá trị ô Excel → chuỗi sạch ('' nếu trống, 123.0 → '123')."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    text = str(value).strip()
    return '' if text.lower() == 'nan' else text


def _norm_acct(value):
    """Chuẩn hoá số TK / mã tham chiếu để so sánh (file CSP làm mất số 0 đầu)."""
    return _s(value).lstrip('0').upper()


def _amount(value):
    text = _s(value).replace(',', '')
    try:
        return abs(float(text))
    except ValueError:
        return 0.0


def _bin_bank(code):
    """'970448-OCB' → 'OCB' (tra BIN), '971025-' → ''."""
    code = _s(code)
    if not code:
        return '', ''
    bin_code, _, short = code.partition('-')
    bin_code = bin_code.strip()
    name = BankStatementParser.BIN_CODE_MAPPING.get(bin_code) or short.strip()
    return bin_code, name


def _msph02_bank(text):
    text = _s(text)
    lower = text.lower()
    for phrase, short in _MSPH02_BANK_NAMES:
        if phrase.lower() in lower:
            return short
    return text


def _valid_name(name):
    """Tên đối tác hợp lệ: không rỗng và không phải tên/mã ngân hàng (VD 'SACOMBANK')."""
    name = _s(name)
    if not name:
        return False
    upper = name.upper().replace(' ', '')
    bank_names = {k.upper() for k in BankStatementParser.BANK_CODE_MAPPING}
    bank_names |= {v.upper().replace(' ', '') for v in BankStatementParser.BANK_CODE_MAPPING.values()}
    return upper not in bank_names


def read_aux_file(path, kind):
    """Đọc file phụ, kiểm tra đủ cột. Raise ValueError nếu sai định dạng."""
    df = pd.read_excel(path, dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    missing = [c for c in REQUIRED_COLUMNS[kind] if c not in df.columns]
    if missing:
        raise ValueError(f"File {AUX_FILES[kind]} thiếu cột: {', '.join(missing)}")
    return df


class _DptbIndex:
    """Chỉ mục các dòng DPTB18 theo thrref và theo mã trace đầu rem."""

    def __init__(self, df):
        self.by_thrref = {}
        self.by_trace = {}
        self.amounts = {}
        self.used = set()
        for idx, row in df.iterrows():
            try:
                amt = float(row.get('acctccyamt'))
            except (TypeError, ValueError):
                continue
            if pd.isna(amt) or amt == 0:
                continue
            sign = 1 if amt > 0 else -1
            self.amounts[idx] = abs(amt)
            thrref = _norm_acct(row.get('thrref'))
            if thrref:
                self.by_thrref.setdefault((thrref, sign), []).append(idx)
            m = _REM_TRACE_RE.search(_s(row.get('rem')))
            if m:
                self.by_trace.setdefault((m.group(1), sign), []).append(idx)

    def take(self, table, key, amount):
        """Lấy dòng DPTB18 chưa dùng có cùng khoá và số tiền."""
        for idx in table.get(key, []):
            if idx not in self.used and self.amounts[idx] == amount:
                self.used.add(idx)
                return idx
        return None


def _unmatched(kind, time, amount, account, name, content, trace):
    return {
        'file': AUX_FILES[kind], 'time': _s(time), 'amount': amount,
        'account': _s(account), 'name': _s(name), 'content': _s(content), 'trace': _s(trace),
    }


def enrich(dptb_df, aux_paths):
    """
    Args:
        dptb_df: DataFrame DPTB18 (parser.df sau validate_file)
        aux_paths: dict {kind: đường dẫn file}, kind thuộc AUX_FILES (file nào thiếu thì bỏ qua)

    Returns:
        (enrichment, unmatched)
        enrichment: {index dòng DPTB18: {'beneficiary_name', 'account_number', 'bank_name', 'source'}}
        unmatched: list dict các dòng thành công trong file phụ không tìm thấy trong DPTB18
    """
    frames = {kind: read_aux_file(path, kind) for kind, path in aux_paths.items() if path}
    index = _DptbIndex(dptb_df)
    enrichment = {}
    unmatched = []

    # ── MSPH02: trace = thrref ──────────────────────────────────────────
    for kind, sign, name_col, acct_col in [
        ('msph02_den', 1, 'ten_nguoi_chuyen', 'tk_chuyen'),
        ('msph02_di', -1, 'ten_nguoi_nhan', 'tk_nhan'),
    ]:
        if kind not in frames:
            continue
        for _, r in frames[kind].iterrows():
            if _s(r['rspcd']) not in _MSPH02_SUCCESS:
                continue
            amount = _amount(r['sttlamt'])
            idx = index.take(index.by_thrref, (_norm_acct(r['trace']), sign), amount)
            if idx is None:
                unmatched.append(_unmatched(kind, r['ngay_giao_dich'], amount, r[acct_col],
                                            r[name_col], r['noi_dung'], r['trace']))
                continue
            enrichment[idx] = {
                'beneficiary_name': _s(r[name_col]) if _valid_name(r[name_col]) else '',
                'account_number': _s(r[acct_col]),
                'bank_name': _msph02_bank(r['nh_nhan_gui_nhan']),
                'source': AUX_FILES[kind],
            }

    # ── CSP chiều đến: TRACE IPCAS = mã 6 số đầu rem ─────────────────────
    if 'csp_den' in frames:
        for _, r in frames['csp_den'].iterrows():
            if not _s(r['STATUS']).startswith('00'):
                continue
            amount = _amount(r['AMOUNT'])
            idx = index.take(index.by_trace, (_s(r['TRACE IPCAS']).zfill(6), 1), amount)
            if idx is None:
                unmatched.append(_unmatched('csp_den', r['TRANSACTION TIME'], amount, r['FROM ACCOUNT'],
                                            r['SENDER NAME'], r['CONTENT'], r['TRACE IPCAS']))
                continue
            enrichment[idx] = {
                'beneficiary_name': _s(r['SENDER NAME']) if _valid_name(r['SENDER NAME']) else '',
                'account_number': _s(r['FROM ACCOUNT']),
                'bank_name': _bin_bank(r['FROM BANK CODE'])[1],
                'source': AUX_FILES['csp_den'],
            }

    # ── CSP chiều đi: dòng Debit khớp DPTB18, dòng Credit cho TK/NH nhận ─
    if 'csp_di' in frames:
        df = frames['csp_di'].copy()
        df['_ts'] = pd.to_datetime(df['TRANSACTION TIME'], errors='coerce')
        approved = df['RESPONSE'].fillna('').str.startswith('1-')
        debits = df[approved & df['TRANCODE'].fillna('').str.startswith('369')]
        credits = df[approved & df['TRANCODE'].fillna('').str.startswith('91')]
        used_credits = set()
        names = _cross_check_names(frames)

        for _, r in debits.iterrows():
            amount = _amount(r['AMOUNT'])
            idx = index.take(index.by_trace, (_s(r['TRACE']).zfill(6), -1), amount)
            credit = _pair_credit(r, credits, used_credits)
            account = _s(credit['TO_ACCOUNT']) if credit is not None else ''
            # Tên người nhận ghi trực tiếp trong file (cột TO_ACCOUNT_REMARK, không bắt buộc)
            to_name = _to_account_remark(r) or (_to_account_remark(credit) if credit is not None else '')
            if idx is None:
                unmatched.append(_unmatched('csp_di', r['TRANSACTION TIME'], amount, account,
                                            to_name, r['REMARK'], r['TRACE']))
                continue
            bin_code, bank = _bin_bank(credit['TO_BANK_CODE']) if credit is not None else ('', '')
            source = AUX_FILES['csp_di']
            name = to_name
            if not name:
                # Không có tên trong file → đối chiếu chéo số TK với các file khác
                name, name_src = names.lookup(account, bin_code)
                if name:
                    source += f' (tên từ {name_src})'
            enrichment[idx] = {
                'beneficiary_name': name,
                'account_number': account,
                'bank_name': bank,
                'source': source,
            }

    return enrichment, unmatched


def _to_account_remark(row):
    """
    Tên người nhận từ cột TO_ACCOUNT_REMARK (CSP chiều đi). Nếu giá trị dạng
    'NGÂN HÀNG;SỐ TK;TÊN' thì lấy phần cuối. Trả '' nếu không có cột / không phải tên người.
    """
    name = _s(row.get('TO_ACCOUNT_REMARK')).split(';')[-1].strip()
    return name if _valid_name(name) else ''


def _norm_remark(text):
    return ' '.join(_s(text).replace(';', ' ').split())


def _pair_credit(debit, credits, used, max_seconds=300):
    """Tìm dòng 91-Transfer Credit cùng REMARK + số tiền, gần thời điểm nhất."""
    # REMARK dòng Credit có thể ngăn cách bằng dấu cách thay vì ';' (VD VPB, NCB) → so sau khi chuẩn hoá
    cand = credits[(credits['AMOUNT'] == debit['AMOUNT'])
                   & (credits['REMARK'].map(_norm_remark) == _norm_remark(debit['REMARK']))
                   & ~credits.index.isin(used)]
    if cand.empty or pd.isna(debit['_ts']):
        return None
    gap = (cand['_ts'] - debit['_ts']).abs().dt.total_seconds()
    best = gap.idxmin()
    if gap[best] > max_seconds:
        return None
    used.add(best)
    return cand.loc[best]


class _NameBook:
    """Tra tên chủ TK theo số TK, gom từ các file có ghi tên."""

    def __init__(self):
        self.csp = {}      # norm acct → (name, bin)
        self.msph02 = {}   # norm acct → (name, label)

    def lookup(self, account, bin_code):
        acct = _norm_acct(account)
        if not acct:
            return '', ''
        # CSP chiều đến có mã BIN → bắt buộc cùng ngân hàng
        if acct in self.csp and self.csp[acct][1] == bin_code:
            return self.csp[acct][0], AUX_FILES['csp_den']
        # MSPH02 không có mã BIN → chỉ nhận số TK đủ dài để tránh trùng giữa các ngân hàng
        if acct in self.msph02 and len(acct) >= 8:
            return self.msph02[acct]
        return '', ''


def _cross_check_names(frames):
    book = _NameBook()
    if 'csp_den' in frames:
        for _, r in frames['csp_den'].iterrows():
            if _valid_name(r['SENDER NAME']):
                book.csp.setdefault(_norm_acct(r['FROM ACCOUNT']),
                                    (_s(r['SENDER NAME']), _bin_bank(r['FROM BANK CODE'])[0]))
    for kind, name_col, acct_col in [('msph02_den', 'ten_nguoi_chuyen', 'tk_chuyen'),
                                     ('msph02_di', 'ten_nguoi_nhan', 'tk_nhan')]:
        if kind not in frames:
            continue
        for _, r in frames[kind].iterrows():
            if _s(r['rspcd']) in _MSPH02_SUCCESS and _valid_name(r[name_col]):
                book.msph02.setdefault(_norm_acct(r[acct_col]), (_s(r[name_col]), AUX_FILES[kind]))
    return book

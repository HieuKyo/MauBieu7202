"""
Xử lý file CSP/Visa/E-Mobile/SMS Banking cho báo cáo Thống kê chỉ tiêu Sản phẩm dịch vụ (SPDV).
Khác với templates_app/kpi_utils/kpi_data_processor.py (xử lý từng GDV một),
các hàm ở đây gom kết quả cho TOÀN BỘ GDV xuất hiện trong file cùng lúc, trong 1
khoảng ngày bất kỳ (1 tháng hoặc cả quý) — kết quả được gán về đúng tháng của từng
giao dịch để vẫn lưu theo SPDVKpiRecord (theo tháng).

Mỗi hàm parse_* trả về 1 DataFrame đã chuẩn hóa 3 cột: `user` (tài khoản GDV, đã
lowercase/strip), `date` (ngày giao dịch, datetime), `customer_code` (mã khách hàng
nếu file có, dùng để hiển thị chi tiết — không phải để khớp GDV). Dùng `counts_from_df()`
để gom thành dict {(user, year, month): số_lượng}, hoặc `rows_for_user_period()` để lấy
danh sách dòng chi tiết của 1 GDV trong 1 kỳ (phục vụ màn hình xem chi tiết chỉ tiêu).

Khách hàng đang vay (theo file MSIT80) được loại trừ khỏi mọi chỉ tiêu: đối chiếu
mã khách hàng PCODE (file CSP) / custseq (file Agribank Plus, SMS Banking) với cột
`brcd` của MSIT80 sau khi cắt bỏ 4 ký tự đầu (mã chi nhánh).
"""

import io
import warnings

import pandas as pd


def _read_csv_robust(file_obj, header):
    """
    Đọc file .csv thử qua nhiều encoding (một số file xuất từ IPCAS/công cụ truy vấn
    không phải UTF-8 mà là Windows-1258/ANSI tiếng Việt) kết hợp dấu phẩy/tab làm
    dấu phân cách — một số file .csv thực chất phân cách bằng tab, hoặc có nội dung
    chứa dấu phẩy (vd: TEN_KH) khiến đọc theo phẩy bị lệch cột.

    Tự giải mã bytes → text trước (thay vì để pandas tự mở file + tự dò encoding),
    vì pandas dùng `sep=None` (tự dò dấu phân cách) kết hợp đọc trực tiếp từ file
    object nhị phân dễ lỗi nội bộ khi gặp encoding không phải UTF-8.
    """
    file_obj.seek(0)
    raw = file_obj.read()
    if isinstance(raw, str):
        raw = raw.encode('utf-8')

    best = None
    last_err = None
    for encoding in ('utf-8', 'utf-8-sig', 'cp1258', 'latin1'):
        try:
            text = raw.decode(encoding)
        except UnicodeDecodeError as e:
            last_err = e
            continue
        for sep in (',', '\t'):
            try:
                df = pd.read_csv(io.StringIO(text), header=header, sep=sep)
            except pd.errors.ParserError as e:
                last_err = e
                continue
            if df.shape[1] > 1:
                return df
            if best is None:
                best = df
    if best is not None:
        return best
    raise last_err


def _read_file(file_obj, header=0):
    """
    Đọc CSV/Excel. Với .xls, thử engine xlrd trước rồi mới fallback sang openpyxl —
    một số file .xls xuất từ IPCAS có cấu trúc OLE2 không chuẩn khiến xlrd cảnh báo
    (không phải lỗi), nhưng đôi khi engine kia đọc được đúng hơn.
    """
    file_obj.seek(0)
    filename = file_obj.name.lower()
    if filename.endswith('.csv'):
        return _read_csv_robust(file_obj, header)

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        if filename.endswith('.xls'):
            file_obj.seek(0)
            try:
                return pd.read_excel(file_obj, header=header, engine='xlrd')
            except Exception:
                file_obj.seek(0)
                return pd.read_excel(file_obj, header=header, engine='openpyxl')
        file_obj.seek(0)
        return pd.read_excel(file_obj, header=header)


def _filter_by_date_range(df, date_column, start_date, end_date):
    """Lọc df theo khoảng [start_date, end_date] (cả 2 đầu), trả về df còn cột ngày dạng datetime."""
    df[date_column] = pd.to_datetime(df[date_column], dayfirst=True, errors='coerce')
    mask = (df[date_column].dt.date >= start_date) & (df[date_column].dt.date <= end_date)
    return df[mask].copy()


def _normalize_customer_code(val):
    """Chuẩn hóa mã khách hàng về string thuần (bỏ '.0' do Excel đọc thành số, bỏ số 0 thừa phía trước)."""
    s = str(val).strip()
    if s.endswith('.0'):
        s = s[:-2]
    s = s.lstrip('0')
    return s or '0'


def _format_display_code(val):
    """Chuẩn hóa 1 giá trị để HIỂN THỊ (vd: số tài khoản) — chỉ bỏ '.0' do Excel đọc thành số,
    KHÔNG bỏ số 0 ở đầu (khác với _normalize_customer_code, vốn dùng để SO KHỚP mã khách hàng)."""
    s = str(val).strip()
    if s.endswith('.0'):
        s = s[:-2]
    return s


def _exclude_loan_customers(df, customer_column, excluded_customers):
    """Loại bỏ các dòng có mã khách hàng (customer_column) nằm trong tập `excluded_customers`."""
    if not excluded_customers or customer_column not in df.columns:
        return df
    codes = df[customer_column].apply(_normalize_customer_code)
    return df[~codes.isin(excluded_customers)].copy()


EMPTY_DETAIL_DF = pd.DataFrame(columns=['user', 'date', 'customer_code', 'customer_name', 'account_number'])


def _find_col(columns, candidates):
    """Tìm cột đầu tiên trong `candidates` có mặt trong `columns` (không phân biệt hoa/thường)."""
    lower_map = {str(c).strip().lower(): c for c in columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None


NAME_COL_CANDIDATES = ['CUSTVIENAME', 'custnm', 'custname', 'nmloc', 'ten_kh', 'ho_ten']
ACCOUNT_COL_CANDIDATES = ['ACCOUNT', 'acctseq', 'idxacno', 'acctno', 'acctcd', 'mblno1', 'so_tai_khoan', 'account_no']


def _to_normalized(df, user_column, date_column, customer_column=None, name_column=None, account_column=None):
    """Chuẩn hóa df đã lọc về các cột chung: user, date, customer_code, customer_name, account_number."""
    if df.empty:
        return EMPTY_DETAIL_DF.copy()

    name_column = name_column or _find_col(df.columns, NAME_COL_CANDIDATES)
    account_column = account_column or _find_col(df.columns, ACCOUNT_COL_CANDIDATES)

    return pd.DataFrame({
        'user': df[user_column].astype(str).str.strip().str.lower(),
        'date': df[date_column],
        'customer_code': df[customer_column].apply(_normalize_customer_code) if customer_column and customer_column in df.columns else '',
        'customer_name': df[name_column].astype(str).str.strip() if name_column and name_column in df.columns else '',
        'account_number': df[account_column].apply(_format_display_code) if account_column and account_column in df.columns else '',
    })


def counts_from_df(df):
    """Gom DataFrame đã chuẩn hóa thành dict {(user, year, month): số_lượng}."""
    if df.empty:
        return {}
    d = df.copy()
    d['_year'] = d['date'].dt.year
    d['_month'] = d['date'].dt.month
    counts = d.groupby(['user', '_year', '_month']).size()
    return {(user, int(y), int(m)): int(cnt) for (user, y, m), cnt in counts.items()}


def rows_for_user_period(df, user_value, year, month):
    """Trả về list dict (date, customer_code, customer_name, account_number) các dòng của `user_value` trong đúng (year, month)."""
    if df.empty or not user_value:
        return []
    mask = (df['user'] == user_value) & (df['date'].dt.year == year) & (df['date'].dt.month == month)
    sub = df[mask]
    return [
        {
            'date': row.date.date(),
            'customer_code': row.customer_code,
            'customer_name': getattr(row, 'customer_name', ''),
            'account_number': getattr(row, 'account_number', ''),
        }
        for row in sub.itertuples(index=False)
    ]


def filter_by_customer_codes(df, customer_codes):
    """Lọc df đã chuẩn hóa, chỉ giữ các dòng có customer_code nằm trong tập `customer_codes`."""
    if df is None or df.empty or not customer_codes:
        return EMPTY_DETAIL_DF.copy()
    return df[df['customer_code'].isin(customer_codes)].copy()


def parse_spdv_quarter_file(file_obj):
    """
    File 'SPDV quý' — đối chiếu khách hàng đã đăng ký Tài khoản Plus (cột TK_OSB) và
    OTT (cột DK_AGRIBANK_PLUS_OTT), mỗi dòng 1 khách hàng, giá trị '1' nghĩa là đã đăng ký.
    Mã khách hàng ở cột MA_KH có dấu ' ở đầu (Excel giữ số 0 đầu) — phải bỏ đi rồi mới so khớp
    với custseq của file E-Mobile Banking (cùng quy tắc chuẩn hóa _normalize_customer_code).
    Tên cột trong file gốc có thể dư khoảng trắng ở đầu (" MA_KH", " TK_OSB", ...) — tự strip.

    Returns: (tk_plus_customers, ott_customers) — 2 set mã khách hàng đã chuẩn hóa
    """
    df = _read_file(file_obj)
    df.columns = [str(c).strip() for c in df.columns]

    required_cols = ['MA_KH', 'TK_OSB', 'DK_AGRIBANK_PLUS_OTT']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"File SPDV quý thiếu các cột: {', '.join(missing)}")

    def _clean_ma_kh(val):
        s = str(val).strip()
        if s.startswith("'"):
            s = s[1:]
        return _normalize_customer_code(s)

    def _is_registered(val):
        return str(val).strip() == '1'

    ma_kh = df['MA_KH'].apply(_clean_ma_kh)
    tk_plus_customers = set(ma_kh[df['TK_OSB'].apply(_is_registered)])
    ott_customers = set(ma_kh[df['DK_AGRIBANK_PLUS_OTT'].apply(_is_registered)])
    return tk_plus_customers, ott_customers


def parse_loan_customers(file_obj):
    """
    File MSIT80 — danh sách khách hàng đang vay, dùng để loại trừ khỏi mọi chỉ tiêu SPDV.
    Mã khách hàng nằm ở cột `brcd` (13 ký tự: 4 ký tự đầu là mã chi nhánh + 9 ký tự mã khách hàng),
    phải cắt bỏ 4 ký tự đầu mới so sánh được với PCODE (file CSP) / custseq (Agribank Plus, SMS Banking).

    Returns: set mã khách hàng đã chuẩn hóa (9 ký tự, không mã chi nhánh)
    """
    df = _read_file(file_obj)
    df.columns = [str(c).strip().lower() for c in df.columns]

    if 'brcd' not in df.columns:
        raise ValueError("File danh sách khách hàng vay (MSIT80) thiếu cột 'brcd'")

    codes = set()
    for val in df['brcd'].dropna():
        s = str(val).strip()
        if s.endswith('.0'):
            s = s[:-2]
        if len(s) <= 4:
            continue
        codes.add(_normalize_customer_code(s[4:]))
    return codes


def parse_csp_file(file_obj, start_date, end_date, excluded_customers=None):
    """
    File phát hành thẻ CSP.
    Cột: CUSER (tài khoản phát hành), CDATE (ngày phát hành),
         PCODE (mã khách hàng, tùy chọn — dùng để loại trừ khách hàng đang vay + hiển thị chi tiết).
    Tính toàn bộ các dòng (không phân biệt phát hành mới hay phát hành lại).

    Returns: DataFrame chuẩn hóa (user, date, customer_code) — user khớp UserProfile.csp_cuser
    """
    df = _read_file(file_obj)

    required_cols = ['CUSER', 'CDATE']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"File Thẻ CSP thiếu các cột: {', '.join(missing)}")

    df = _exclude_loan_customers(df, 'PCODE', excluded_customers)
    df['CDATE'] = pd.to_datetime(df['CDATE'], dayfirst=True, errors='coerce')
    df = _filter_by_date_range(df, 'CDATE', start_date, end_date)

    return _to_normalized(df, 'CUSER', 'CDATE', 'PCODE')


def parse_visa_file(file_obj, start_date, end_date):
    """
    File phát hành thẻ Visa.
    Cột: dlvrydt (ngày phát hành), dlvryusrid (user phát hành, dạng GRATHIEU),
         isutycd (loại phát hành). Chỉ tính isutycd == 'New Issue'.

    Returns: DataFrame chuẩn hóa (user, date, customer_code) — user khớp UserProfile.ipcas_user
    """
    df = _read_file(file_obj)

    required_cols = ['dlvrydt', 'dlvryusrid', 'isutycd']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"File Thẻ Visa thiếu các cột: {', '.join(missing)}")

    df = df[df['isutycd'].astype(str).str.strip() == 'New Issue'].copy()
    df['dlvrydt'] = pd.to_datetime(df['dlvrydt'], dayfirst=True, errors='coerce')
    df = _filter_by_date_range(df, 'dlvrydt', start_date, end_date)

    return _to_normalized(df, 'dlvryusrid', 'dlvrydt')


def _parse_sms_emobile_file(file_obj, start_date, end_date, excluded_customers, file_label):
    """
    Dùng chung cho file E-Mobile Banking và SMS Banking (cùng cấu trúc).
    Cột: entydt (ngày đăng ký), crtusr (user đăng ký), uptdtm (ngày cập nhật —
    có giá trị nghĩa là bản cập nhật, không tính), custseq (mã khách hàng, tùy chọn —
    dùng để loại trừ khách hàng đang vay + hiển thị chi tiết).

    Returns: DataFrame chuẩn hóa (user, date, customer_code) — user khớp UserProfile.ipcas_user
    """
    df = _read_file(file_obj)

    required_cols = ['entydt', 'crtusr']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"File {file_label} thiếu các cột: {', '.join(missing)}")

    if 'uptdtm' in df.columns:
        df = df[df['uptdtm'].isna() | (df['uptdtm'].astype(str).str.strip() == '')].copy()

    df = _exclude_loan_customers(df, 'custseq', excluded_customers)
    df['entydt'] = pd.to_datetime(df['entydt'], dayfirst=True, errors='coerce')
    df = _filter_by_date_range(df, 'entydt', start_date, end_date)

    return _to_normalized(df, 'crtusr', 'entydt', 'custseq')


def parse_emobile_file(file_obj, start_date, end_date, excluded_customers=None):
    """File E-Mobile Banking, dùng để tính chỉ tiêu Agribank Plus (và góp phần vào Mobile Banking)."""
    return _parse_sms_emobile_file(file_obj, start_date, end_date, excluded_customers, "E-Mobile Banking")


def parse_sms_file(file_obj, start_date, end_date, excluded_customers=None):
    """File SMS Banking, góp phần vào chỉ tiêu Mobile Banking (cùng với E-Mobile Banking)."""
    return _parse_sms_emobile_file(file_obj, start_date, end_date, excluded_customers, "SMS Banking")


def the_count_for(csp_counts, visa_counts, profile, year, month):
    """Tổng số thẻ (CSP + Visa) của 1 GDV trong đúng (year, month), không phân biệt hoa/thường."""
    total = 0
    if profile.csp_cuser:
        total += csp_counts.get((profile.csp_cuser.strip().lower(), year, month), 0)
    if profile.ipcas_user:
        total += visa_counts.get((profile.ipcas_user.strip().lower(), year, month), 0)
    return total


def emobile_count_for(emobile_counts, profile, year, month):
    """Số lượng Agribank Plus của 1 GDV trong đúng (year, month)."""
    if not profile.ipcas_user:
        return 0
    return emobile_counts.get((profile.ipcas_user.strip().lower(), year, month), 0)


def mobile_banking_count_for(emobile_counts, sms_counts, profile, year, month):
    """Số lượng Mobile Banking (E-Mobile + SMS Banking) của 1 GDV trong đúng (year, month)."""
    if not profile.ipcas_user:
        return 0
    key = (profile.ipcas_user.strip().lower(), year, month)
    return emobile_counts.get(key, 0) + sms_counts.get(key, 0)

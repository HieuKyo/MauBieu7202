"""
Đọc file nguồn Khách hàng 360. Không ghi DB — chỉ trả về dữ liệu đã chuẩn hoá.

- CN05 / DP01 / LN01: CSV (hoặc ZIP chứa CSV) xuất từ IPCAS, UTF-8, mã có dấu ' đứng đầu,
  ngày dạng YYYYMMDD; ngày dữ liệu lấy từ tên file (vd 7202_dp01_20261031.csv).
- Loa Thần tài: XLSX "BẢNG THỐNG KÊ DOANH SỐ LOA" (kỳ lấy từ ô Từ ngày / Đến ngày).
- QR: XLSX sổ theo dõi nhập tay (sheet có cột Họ Tên + STK).
- KHTC: XLSX "Quản trị khách hàng tổ chức" (ngày lấy từ tên file).
"""
import csv
import io
import re
import unicodedata
import zipfile
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import openpyxl

csv.field_size_limit(2**31 - 1)


class FileLoi(Exception):
    """Lỗi file không đúng định dạng — thông báo hiển thị thẳng cho người dùng."""


# ── Chuẩn hoá giá trị ──────────────────────────────────────────────────────────

def s(v):
    """Chuỗi đã bỏ khoảng trắng và dấu ' đầu (IPCAS thêm để giữ số 0)."""
    if v is None:
        return ''
    return str(v).strip().lstrip("'").strip()


def so(v):
    try:
        return Decimal(s(v).replace(',', '') or 0)
    except InvalidOperation:
        return Decimal(0)


def so_nguyen(v):
    try:
        return int(so(v))
    except (ValueError, ArithmeticError):
        return 0


def ngay(v):
    """YYYYMMDD → date; '00000000' hoặc rỗng → None."""
    v = s(v)
    if len(v) == 8 and v.isdigit() and v != '00000000':
        try:
            return date(int(v[:4]), int(v[4:6]), int(v[6:]))
        except ValueError:
            return None
    return None


def ngay_linh_hoat(v):
    """Ngày từ ô Excel nhập tay: datetime, 'dd/mm/yyyy[ hh:mm:ss]', 'yyyy-mm-dd...', 'ddmmyyyy'."""
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    t = s(v)
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', t)
    if m:
        d, mo, y = map(int, m.groups())
    else:
        m = re.match(r'(\d{4})-(\d{2})-(\d{2})', t)
        if m:
            y, mo, d = map(int, m.groups())
        elif re.fullmatch(r'\d{8}', t):
            d, mo, y = int(t[:2]), int(t[2:4]), int(t[4:])
        else:
            return None
    try:
        return date(y, mo, d)
    except ValueError:
        return None


def khong_dau(text):
    """Chữ thường, bỏ dấu tiếng Việt (đ → d) — dùng cho tìm kiếm."""
    text = (text or '').lower().replace('đ', 'd')
    text = unicodedata.normalize('NFD', text)
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn')


def chuan_ten(text):
    """Khoá so khớp tên tổ chức: không dấu, chỉ chữ + số."""
    return re.sub(r'[^a-z0-9]', '', khong_dau(text))


def ngay_tu_ten_file(ten):
    m = re.search(r'(20\d{2})(\d{2})(\d{2})', ten)
    if m:
        try:
            return date(*map(int, m.groups()))
        except ValueError:
            pass
    return None


# ── CSV / ZIP ─────────────────────────────────────────────────────────────────

def _mo_csv(uploaded):
    """Trả về file text của CSV (tự giải nén nếu là ZIP) và tên file CSV thật."""
    ten = uploaded.name
    if ten.lower().endswith('.zip'):
        try:
            zf = zipfile.ZipFile(uploaded)
        except zipfile.BadZipFile:
            raise FileLoi(f'File {ten} không phải file ZIP hợp lệ.')
        csvs = [n for n in zf.namelist() if n.lower().endswith('.csv')]
        if not csvs:
            raise FileLoi(f'File ZIP {ten} không chứa file CSV.')
        try:
            member = zf.open(csvs[0])
        except RuntimeError:  # ZIP có mật khẩu
            raise FileLoi(f'File {ten} có mật khẩu — hãy giải nén và chọn file .csv bên trong.')
        return io.TextIOWrapper(member, encoding='utf-8-sig', errors='replace', newline=''), csvs[0]
    if not ten.lower().endswith('.csv'):
        raise FileLoi(f'File {ten}: chỉ nhận file .csv hoặc .zip.')
    uploaded.seek(0)
    return io.TextIOWrapper(uploaded, encoding='utf-8-sig', errors='replace', newline=''), ten


def _doc_csv(uploaded, nguon, cot_bat_buoc):
    f, ten_csv = _mo_csv(uploaded)
    reader = csv.reader(f)
    header = [c.strip() for c in next(reader, [])]
    thieu = [c for c in cot_bat_buoc if c not in header]
    if thieu:
        raise FileLoi(f'File {uploaded.name} không đúng cấu trúc {nguon} (thiếu cột: {", ".join(thieu[:5])}).')
    idx = {c: i for i, c in enumerate(header)}
    ngay_file = ngay_tu_ten_file(ten_csv) or ngay_tu_ten_file(uploaded.name)
    if not ngay_file:
        raise FileLoi(f'Không đọc được ngày dữ liệu từ tên file {uploaded.name} (cần dạng ..._YYYYMMDD).')

    def rows():
        for row in reader:
            if row:
                yield lambda c: row[idx[c]] if idx[c] < len(row) else ''
    return ngay_file, rows()


# Cột dịch vụ CN05: (cột file, khoá lưu, nhãn hiển thị)
CN05_DICH_VU = [
    ('TKTT_SO_TK', 'tktt', 'TK thanh toán'),
    ('TKTT_TK_SODEP', 'tk_so_dep', 'TK số đẹp'),
    ('TK_OSB', 'tk_osb', 'TK OSB'),
    ('TG_TIEN_GUI_TAI_QUAY', 'tg_tai_quay', 'Tiền gửi tại quầy'),
    ('TG_TIEN_GUI_TRUC_TUYEN', 'tg_truc_tuyen', 'Tiền gửi trực tuyến'),
    ('TG_TIEN_GUI_LOI_THONG_MINH', 'tg_loi_thong_minh', 'Tiền gửi lời thông minh'),
    ('TG_SMS_TIEN_GUI', 'tg_sms', 'SMS tiền gửi'),
    ('VV_TONG_SO_LDS', 'vay_so_lds', 'Khoản vay'),
    ('VV_SMS_TIEN_VAY', 'vay_sms', 'SMS tiền vay'),
    ('THE_GHI_NO_NOI_DIA', 'the_gn_noi_dia', 'Thẻ ghi nợ nội địa'),
    ('THE_GHI_NO_QUOC_TE', 'the_gn_quoc_te', 'Thẻ ghi nợ quốc tế'),
    ('THE_TIN_DUNG_NOI_DIA', 'the_td_noi_dia', 'Thẻ tín dụng nội địa'),
    ('THE_TIN_DUNG_QUOC_TE', 'the_td_quoc_te', 'Thẻ tín dụng quốc tế'),
    ('VISA', 'the_visa', 'Thẻ Visa'),
    ('MASTER', 'the_master', 'Thẻ Master'),
    ('JCB', 'the_jcb', 'Thẻ JCB'),
    ('DK_AGRIBANK_PLUS', 'agribank_plus', 'Agribank Plus'),
    ('DK_AGRIBANK_PLUS_OTT', 'agribank_plus_ott', 'Agribank Plus OTT'),
    ('SMS_BANKING', 'sms_banking', 'SMS Banking'),
]
NHAN_DICH_VU = {k: nhan for _, k, nhan in CN05_DICH_VU}


def doc_cn05(uploaded):
    """→ (ngày, {ma_kh: {'ten', 'dich_vu': {khoá: số}}})"""
    cot = ['MA_KH', 'TEN_KH'] + [c for c, _, _ in CN05_DICH_VU]
    ngay_file, rows = _doc_csv(uploaded, 'CN05', cot)
    kq = {}
    for g in rows:
        ma = s(g('MA_KH'))
        if not ma:
            continue
        dv = {k: so_nguyen(g(c)) for c, k, _ in CN05_DICH_VU}
        kq[ma] = {'ten': s(g('TEN_KH')), 'dich_vu': {k: v for k, v in dv.items() if v}}
    return ngay_file, kq


GIOI_TINH = {'Male': 'Nam', 'Female': 'Nữ'}


def doc_dp01(uploaded):
    """→ (ngày, {so_tk: dict TK}, {ma_kh: dict thông tin KH})"""
    cot = ['MA_KH', 'TEN_KH', 'SO_TAI_KHOAN', 'TAI_KHOAN_HACH_TOAN', 'DP_TYPE_NAME', 'CCY',
           'CURRENT_BALANCE', 'RATE', 'MONTH_TERM', 'OPENING_DATE', 'MATURITY_DATE',
           'ACCOUNT_STATUS', 'TEN_PGD', 'NOTENO', 'EMPLOYEE_NAME', 'TERM_DP_NAME', 'CUST_TYPE', 'CUST_TYPE_NAME',
           'ID_NUMBER', 'ISSUE_DATE', 'SEX_TYPE', 'BIRTH_DATE', 'TELEPHONE', 'ADDRESS']
    ngay_file, rows = _doc_csv(uploaded, 'DP01', cot)
    tk, kh = {}, {}
    for g in rows:
        so_tk, ma = s(g('SO_TAI_KHOAN')), s(g('MA_KH'))
        if not so_tk or not ma:
            continue
        trang_thai = s(g('ACCOUNT_STATUS'))
        tk[so_tk] = {
            'ma_kh': ma, 'ten_kh': s(g('TEN_KH')), 'tk_hach_toan': s(g('TAI_KHOAN_HACH_TOAN')),
            'loai_tg': s(g('DP_TYPE_NAME')), 'ccy': s(g('CCY')), 'so_du': so(g('CURRENT_BALANCE')),
            'lai_suat': so(g('RATE')), 'ky_han': so_nguyen(g('MONTH_TERM')),
            'ngay_mo': ngay(g('OPENING_DATE')), 'ngay_den_han': ngay(g('MATURITY_DATE')),
            'trang_thai': trang_thai, 'pgd': s(g('TEN_PGD')), 'so_so': s(g('NOTENO')),
            'can_bo': s(g('EMPLOYEE_NAME')), 'hinh_thuc': s(g('TERM_DP_NAME'))[:60],
            'con_hoat_dong': trang_thai != 'Close',
        }
        if ma not in kh or (not kh[ma]['cccd'] and s(g('ID_NUMBER'))):
            kh[ma] = {
                'ten': s(g('TEN_KH')), 'loai_kh': s(g('CUST_TYPE')), 'ten_loai_kh': s(g('CUST_TYPE_NAME')),
                'cccd': s(g('ID_NUMBER')), 'ngay_cap': ngay(g('ISSUE_DATE')),
                'gioi_tinh': GIOI_TINH.get(s(g('SEX_TYPE')), ''), 'ngay_sinh': ngay(g('BIRTH_DATE')),
                'sdt': s(g('TELEPHONE')), 'dia_chi': s(g('ADDRESS')), 'pgd': s(g('TEN_PGD')),
            }
    return ngay_file, tk, kh


def doc_ln01(uploaded):
    """→ (ngày, {so_giai_ngan: dict khoản vay})"""
    cot = ['CUSTSEQ', 'CUSTNM', 'TAI_KHOAN', 'DU_NO', 'DSBSSEQ', 'DSBSDT', 'DISBURSEMENT_AMOUNT',
           'DSBSMATDT', 'INTEREST_RATE', 'LOAN_TYPE', 'FUND_PURPOSE_CODE', 'NEXT_REPAY_DATE',
           'NEXT_REPAY_AMOUNT', 'OFFICER_NAME', 'NHOM_NO', 'TAI_KHOAN_GIAI_NGAN_1', 'CMT_HC',
           'NGAY_SINH', 'ADDR1', 'CUSTOMER_TYPE_CODE', 'TRCTNM']
    ngay_file, rows = _doc_csv(uploaded, 'LN01', cot)
    kq = {}
    for g in rows:
        so_gn, ma = s(g('DSBSSEQ')), s(g('CUSTSEQ'))
        if not so_gn or not ma:
            continue
        du_no = so(g('DU_NO'))
        kq[so_gn] = {
            'ma_kh': ma, 'ten_kh': s(g('CUSTNM')), 'loai_kh': s(g('CUSTOMER_TYPE_CODE')),
            'tk_hach_toan': s(g('TAI_KHOAN')), 'loai_vay': s(g('LOAN_TYPE'))[:100],
            'muc_dich': s(g('FUND_PURPOSE_CODE'))[:150], 'du_no': du_no,
            'so_tien_giai_ngan': so(g('DISBURSEMENT_AMOUNT')), 'ngay_giai_ngan': ngay(g('DSBSDT')),
            'ngay_dao_han': ngay(g('DSBSMATDT')), 'lai_suat': so(g('INTEREST_RATE')),
            'nhom_no': s(g('NHOM_NO')), 'can_bo': s(g('OFFICER_NAME')),
            'tk_nhan_giai_ngan': s(g('TAI_KHOAN_GIAI_NGAN_1')), 'ngay_tra_tiep': ngay(g('NEXT_REPAY_DATE')),
            'so_tien_tra_tiep': so(g('NEXT_REPAY_AMOUNT')), 'pgd': s(g('TRCTNM')),
            'cccd': s(g('CMT_HC')), 'ngay_sinh': ngay(g('NGAY_SINH')), 'dia_chi': s(g('ADDR1'))[:300],
            'con_du_no': du_no > 0,
        }
    return ngay_file, kq


def doc_bc06(uploaded):
    """BC06 (MSPL09) phân hạng KH → (ngày, {ma_kh: dict})"""
    cot = ['MA_KHACH_HANG', 'THANG_PHAN_LOAI', 'NHOM_TAI_CN', 'HANG_TAI_CN', 'NHOM_TT_CN', 'HANG_TT_CN',
           'NHOM_AGR', 'HANG_AGR', 'NHOM_TT_AGR', 'HANG_TT_AGR', 'DIEM_KH_CN', 'DIEM_LOI_ICH_CN',
           'DIEM_SDBQ_CN', 'DIEM_DINH_TINH_CN', 'LOI_ICH_TG_TAI_CN', 'LOI_ICH_TV_TAI_CN',
           'LOI_ICH_DV_TAI_CN', 'SDBQ_TGCKH_CN', 'SDBQ_TGKKH_CN', 'SDBQ_TV', 'DON_VI_DAU_MOI']
    ngay_file, rows = _doc_csv(uploaded, 'BC06', cot)
    kq = {}
    for g in rows:
        ma = s(g('MA_KHACH_HANG'))
        if not ma:
            continue
        kq[ma] = {
            'thang': s(g('THANG_PHAN_LOAI'))[:6],
            'nhom_cn': s(g('NHOM_TAI_CN')), 'hang_cn': s(g('HANG_TAI_CN')),
            'nhom_tt_cn': s(g('NHOM_TT_CN')), 'hang_tt_cn': s(g('HANG_TT_CN')),
            'nhom_agr': s(g('NHOM_AGR')), 'hang_agr': s(g('HANG_AGR')),
            'nhom_tt_agr': s(g('NHOM_TT_AGR')), 'hang_tt_agr': s(g('HANG_TT_AGR')),
            'diem_kh': so_nguyen(g('DIEM_KH_CN')), 'diem_loi_ich': so_nguyen(g('DIEM_LOI_ICH_CN')),
            'diem_sdbq': so_nguyen(g('DIEM_SDBQ_CN')), 'diem_dinh_tinh': so_nguyen(g('DIEM_DINH_TINH_CN')),
            'loi_ich_tg': round(so(g('LOI_ICH_TG_TAI_CN')), 2), 'loi_ich_tv': round(so(g('LOI_ICH_TV_TAI_CN')), 2),
            'loi_ich_dv': round(so(g('LOI_ICH_DV_TAI_CN')), 2),
            'sdbq_tg_co_ky_han': round(so(g('SDBQ_TGCKH_CN')), 2),
            'sdbq_tg_khong_ky_han': round(so(g('SDBQ_TGKKH_CN')), 2),
            'sdbq_tien_vay': round(so(g('SDBQ_TV')), 2), 'don_vi_dau_moi': s(g('DON_VI_DAU_MOI'))[:100],
        }
    return ngay_file, kq


# ── XLSX ──────────────────────────────────────────────────────────────────────

def _mo_xlsx(uploaded):
    if not uploaded.name.lower().endswith('.xlsx'):
        raise FileLoi(f'File {uploaded.name}: chỉ nhận file .xlsx.')
    try:
        return openpyxl.load_workbook(uploaded, read_only=True, data_only=True)
    except Exception:
        raise FileLoi(f'Không mở được file Excel {uploaded.name}.')


def _tim_header(rows, cot_bat_buoc, gioi_han=40):
    """Vị trí dòng tiêu đề và {tên cột: chỉ số}; None nếu không thấy."""
    for i, r in enumerate(rows[:gioi_han]):
        ten = {s(v): j for j, v in enumerate(r) if s(v)}
        if all(c in ten for c in cot_bat_buoc):
            return i, ten
    return None, None


def doc_loa(uploaded):
    """→ (tu_ngay, den_ngay, [dict loa])"""
    wb = _mo_xlsx(uploaded)
    rows = list(wb.worksheets[0].iter_rows(values_only=True))
    hi, cot = _tim_header(rows, ['TK ảo', 'TK Agribank', 'Số lượng giao dịch', 'Doanh số'])
    if hi is None:
        raise FileLoi(f'File {uploaded.name} không đúng cấu trúc Thống kê doanh số Loa '
                      '(thiếu cột TK ảo / TK Agribank / Số lượng giao dịch / Doanh số).')
    moc = {}
    for r in rows[:hi]:
        for j, v in enumerate(r):
            if s(v) in ('Từ ngày', 'Đến ngày'):
                moc[s(v)] = next((ngay_linh_hoat(x) for x in r[j + 1:] if ngay_linh_hoat(x)), None)
    tu_ngay, den_ngay = moc.get('Từ ngày'), moc.get('Đến ngày')
    if not tu_ngay or not den_ngay:
        raise FileLoi(f'File {uploaded.name}: không đọc được Từ ngày / Đến ngày.')

    def g(r, c):
        j = cot.get(c)
        return r[j] if j is not None and j < len(r) else None
    kq = []
    for r in rows[hi + 1:]:
        so_tk = s(g(r, 'TK Agribank'))
        if not so_tk:
            continue
        kq.append({
            'tk_ao': s(g(r, 'TK ảo')), 'so_tk': so_tk, 'ten_kh': s(g(r, 'Tên KH')),
            'nha_cung_cap': s(g(r, 'Nhà cung cấp Loa')), 'so_giao_dich': so_nguyen(g(r, 'Số lượng giao dịch')),
            'doanh_so': so(g(r, 'Doanh số')),
        })
    return tu_ngay, den_ngay, kq


def doc_qr(uploaded):
    """→ [dict QR]. Đọc sheet đầu tiên có cột Họ Tên + STK (sheet tổng hợp)."""
    wb = _mo_xlsx(uploaded)
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        hi, cot = _tim_header(rows, ['Họ Tên', 'STK'], gioi_han=5)
        if hi is not None:
            break
    else:
        raise FileLoi(f'File {uploaded.name} không đúng cấu trúc tổng hợp QR (cần cột Họ Tên, STK).')

    def g(r, c):
        j = cot.get(c)
        return r[j] if j is not None and j < len(r) else None
    # Cột ghi chú không có tiêu đề nằm ngay sau NGAY LAM
    j_ghi_chu = cot['NGAY LAM'] + 1 if 'NGAY LAM' in cot else None
    kq = []
    for r in rows[hi + 1:]:
        so_tk = re.sub(r'\D', '', s(g(r, 'STK')))
        if not so_tk:
            continue
        ngay_goc = g(r, 'NGAY LAM')
        kq.append({
            'so_tk': so_tk, 'ho_ten': s(g(r, 'Họ Tên'))[:255], 'ten_cua_hang': s(g(r, 'TEN CUA HANG'))[:255],
            'phong': s(g(r, 'PHONG PHAT SINH'))[:100], 'ngay_lam': ngay_linh_hoat(ngay_goc),
            'ngay_lam_goc': s(ngay_goc)[:50],
            'ghi_chu': s(r[j_ghi_chu])[:255] if j_ghi_chu is not None and j_ghi_chu < len(r) else '',
        })
    return kq


def doc_khtc(uploaded):
    """→ (ngày, [dict tổ chức])"""
    wb = _mo_xlsx(uploaded)
    rows = list(wb.worksheets[0].iter_rows(values_only=True))
    hi, cot = _tim_header(rows, ['Mã Tổ chức', 'Tên khách hàng'], gioi_han=10)
    if hi is None:
        raise FileLoi(f'File {uploaded.name} không đúng cấu trúc Quản trị khách hàng tổ chức '
                      '(cần cột Mã Tổ chức, Tên khách hàng).')
    m = re.search(r'(20\d{2})-(\d{2})-(\d{2})', uploaded.name)
    ngay_file = date(*map(int, m.groups())) if m else (ngay_tu_ten_file(uploaded.name) or date.today())

    def g(r, c):
        j = cot.get(c)
        return r[j] if j is not None and j < len(r) else None
    kq = []
    for r in rows[hi + 1:]:
        ma = s(g(r, 'Mã Tổ chức'))
        if not ma:
            continue
        kq.append({
            'ma_to_chuc': ma, 'ten': s(g(r, 'Tên khách hàng'))[:255],
            'trang_thai': s(g(r, 'Trạng thái hoạt động')), 'ngay_dang_ky': ngay_linh_hoat(g(r, 'Thời gian đăng ký')),
            'nguoi_tao': s(g(r, 'Người tạo')), 'ngay_dong_bo': ngay_linh_hoat(g(r, 'Thời gian đồng bộ cuối')),
        })
    return ngay_file, kq

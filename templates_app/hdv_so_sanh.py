"""
Xử lý dữ liệu So sánh Huy động vốn theo file (DP01 / MSIT81 / RT13) — không phụ thuộc request.

- Mỗi file → bảng tài khoản chuẩn hoá (ma_kh, ccy, so_du, nhom KKH/CKH, cán bộ, PGD, ...).
- So sánh kỳ đầu vs kỳ cuối theo Mã KH + Loại tiền (cộng mọi TK của KH — tất toán rồi mở lại
  sổ sinh số TK mới vẫn đúng KH). Ngoại tệ tách riêng, không quy đổi.
- Từ 3 kỳ trở lên có thêm xu hướng theo kỳ.
"""
import io
import re
import unicodedata
import zipfile
from datetime import date

import pandas as pd

from .report_views import _find_col, _read_csv_robust, _read_excel_safe

# Trường có '*' là bắt buộc; còn lại không có thì bỏ qua phần phân tích tương ứng.
LOAI_FILE = {
    'dp01': {
        'nhan': 'DP01',
        'mo_ta': 'File DP01 – Tài khoản tiền gửi (CSV/ZIP/Excel)',
        'cot': {
            'ma_kh*': ['MA_KH'],
            'so_du*': ['CURRENT_BALANCE'],
            'ccy*': ['CCY'],
            'ten_kh': ['TEN_KH'],
            'so_tk': ['SO_TAI_KHOAN'],
            'pgd': ['TEN_PGD'],
            'can_bo': ['EMPLOYEE_NAME'],
            'ky_han': ['MONTH_TERM'],
            'loai_kh': ['CUST_TYPE_NAME'],
            'sdt': ['TELEPHONE'],
            'cccd': ['ID_NUMBER'],
        },
    },
    'msit81': {
        'nhan': 'MSIT81',
        'mo_ta': 'File MSIT81 – File TG, vd tg31032026_... (Excel/CSV)',
        'cot': {
            'ma_kh*': ['Customer_No'],
            'so_du*': ['Curent_Balance', 'Current_Balance'],  # file TG ghi sai chính tả 'Curent'
            'ccy*': ['Ccy'],
            'ten_kh': ['Customer_Name'],
            'so_tk': ['Account_Number'],
            'pgd': ['Tr_Office_Name'],
            'can_bo': ['empnm'],
            'ky_han': ['Month_Term'],
            'loai_kh': ['Cust_Name'],  # file TG: Cust_Name là tên loại KH (Cá nhân, Hộ gia đình...)
            'sdt': ['Tel'],
            'cccd': ['ID_Number'],
        },
    },
    'rt13': {
        'nhan': 'RT13',
        'mo_ta': 'File RT13 – Tiền gửi (CSV/ZIP/Excel)',
        'cot': {
            'ma_kh*': ['MA_KH'],
            'so_du*': ['SO_DU', 'SO_DU_HIEN_TAI', 'SO_DU_CUOI_KY', 'CURRENT_BALANCE', 'SO_DU_TK'],
            'ccy*': ['LOAI_TIEN', 'MA_LOAI_TIEN', 'CCY', 'MA_TIEN_TE'],
            'ten_kh': ['TEN_KH'],
            'so_tk': ['SO_TK_TIEN_GUI', 'SO_TAI_KHOAN'],
            'pgd': ['TEN_PGD', 'MA_CN'],
            'can_bo': ['TEN_CAN_BO', 'TEN_CB', 'EMPLOYEE_NAME'],
            'ky_han': ['LOAI_KY_HAN', 'KY_HAN', 'MONTH_TERM'],
            'loai_kh': ['TEN_LOAI_KH'],
            'sdt': [],   # RT13 không có SĐT / CCCD
            'cccd': [],
        },
    },
}

TRANG_THAI = ['Mới', 'Tăng', 'Giảm', 'Tất toán', 'Không đổi']
TRUONG_TUY_CHON = ['ten_kh', 'so_tk', 'pgd', 'can_bo', 'ky_han', 'loai_kh', 'sdt', 'cccd']


class FileLoi(Exception):
    """Lỗi file — thông báo hiển thị thẳng cho người dùng."""


# ── Đọc file ──────────────────────────────────────────────────────────────────

def ngay_tu_ten_file(ten):
    """Ngày trong tên file: YYYYMMDD (7202_dp01_20261031) hoặc DDMMYYYY (tg31032026_...)."""
    for so in re.findall(r'(?<!\d)\d{8}(?!\d)', ten or ''):
        for y, mo, d in ((so[:4], so[4:6], so[6:]), (so[4:], so[2:4], so[:2])):
            if y.startswith('20'):
                try:
                    return date(int(y), int(mo), int(d))
                except ValueError:
                    pass
    return None


def _doc_file(uploaded):
    """→ (DataFrame, tên file thật). Nhận .csv, .zip (chứa csv/xlsx), .xlsx, .xls."""
    ten = uploaded.name
    lower = ten.lower()
    if lower.endswith('.zip'):
        try:
            zf = zipfile.ZipFile(uploaded)
        except zipfile.BadZipFile:
            raise FileLoi(f'File {ten} không phải file ZIP hợp lệ.')
        members = [n for n in zf.namelist() if n.lower().endswith(('.csv', '.xlsx', '.xls'))]
        if not members:
            raise FileLoi(f'File ZIP {ten} không chứa file CSV/Excel.')
        try:
            data = zf.read(members[0])
        except RuntimeError:
            raise FileLoi(f'File {ten} có mật khẩu — hãy giải nén và chọn file bên trong.')
        ten, lower = members[0], members[0].lower()
        uploaded = io.BytesIO(data)
    if lower.endswith('.csv'):
        df = _read_csv_robust(uploaded, dtype=str)
    elif lower.endswith(('.xlsx', '.xls')):
        df = _read_excel_safe(uploaded, dtype=str)
    else:
        raise FileLoi(f'File {ten}: chỉ nhận .csv, .zip, .xlsx, .xls.')
    df.columns = [str(c).strip() for c in df.columns]
    return df, ten


def _chuan(series):
    """Bỏ dấu ' đầu (IPCAS), khoảng trắng, đuôi '.0'; NaN → ''."""
    s = series.fillna('').astype(str).str.strip().str.lstrip("'").str.strip()
    return s.str.replace(r'\.0$', '', regex=True)


def _so(series):
    return pd.to_numeric(_chuan(series).str.replace(',', '', regex=False), errors='coerce').fillna(0)


def _khong_dau(text):
    text = (text or '').upper().replace('Đ', 'D')
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')


def _nhom_ky_han(v):
    """Kỳ hạn (số tháng hoặc chữ) → 'KKH' / 'CKH' / '' (không rõ)."""
    if not v:
        return ''
    m = re.search(r'\d+(?:[.,]\d+)?', v)
    if m:
        return 'CKH' if float(m.group(0).replace(',', '.')) > 0 else 'KKH'
    t = _khong_dau(v)
    if 'KHONG KY HAN' in t or 'KKH' in t:
        return 'KKH'
    if 'KY HAN' in t or 'CKH' in t:
        return 'CKH'
    return ''


def doc_tai_khoan(uploaded, loai):
    """→ (ngày | None, DataFrame tài khoản chuẩn hoá, set trường tuỳ chọn có trong file)."""
    cfg = LOAI_FILE[loai]
    df, ten_that = _doc_file(uploaded)

    cot, thieu = {}, []
    for truong, ung_vien in cfg['cot'].items():
        ten = truong.rstrip('*')
        col = _find_col(df.columns, ung_vien)
        if col is None and truong.endswith('*'):
            thieu.append(f"{ten} ({'/'.join(ung_vien)})")
        cot[ten] = col
    if thieu:
        raise FileLoi(
            f"File {uploaded.name} không đúng cấu trúc {cfg['nhan']} — không tìm thấy cột: {'; '.join(thieu)}. "
            f"Các cột có trong file: {', '.join(map(str, df.columns[:60]))}"
        )

    data = pd.DataFrame({
        'ma_kh': _chuan(df[cot['ma_kh']]),
        'ccy': _chuan(df[cot['ccy']]).str.upper().replace('', 'VND'),
        'so_du': _so(df[cot['so_du']]),
    })
    for k in TRUONG_TUY_CHON:
        data[k] = _chuan(df[cot[k]]) if cot[k] else ''
    data['nhom'] = data['ky_han'].map(_nhom_ky_han) if cot['ky_han'] else ''
    data = data[data['ma_kh'] != ''].drop(columns='ky_han')
    co = {k for k in TRUONG_TUY_CHON if cot[k]}
    return ngay_tu_ten_file(ten_that) or ngay_tu_ten_file(uploaded.name), data, co


# ── Tổng hợp ─────────────────────────────────────────────────────────────────

def _noi(values):
    return '; '.join(dict.fromkeys(v for v in values if v))


def _theo_kh(tk):
    """Tài khoản → 1 dòng / (ma_kh, ccy). Cán bộ/PGD chính = của TK có số dư lớn nhất."""
    tk = tk.assign(kkh=tk['so_du'].where(tk['nhom'] == 'KKH', 0),
                   ckh=tk['so_du'].where(tk['nhom'] == 'CKH', 0))
    tk = tk.sort_values('so_du', ascending=False, kind='stable')
    g = tk.groupby(['ma_kh', 'ccy'], sort=False)
    kh = g.agg(so_du=('so_du', 'sum'), kkh=('kkh', 'sum'), ckh=('ckh', 'sum'),
               so_luong_tk=('so_du', 'size'), ten_kh=('ten_kh', 'first'),
               can_bo=('can_bo', 'first'), pgd=('pgd', 'first'), loai_kh=('loai_kh', 'first'))
    # sdt / cccd: giá trị khác rỗng đầu tiên; số TK: nối các TK còn số dư
    kh['sdt'] = g['sdt'].agg(lambda x: next((v for v in x if v), ''))
    kh['cccd'] = g['cccd'].agg(lambda x: next((v for v in x if v), ''))
    kh['so_tk'] = tk[tk['so_du'] != 0].groupby(['ma_kh', 'ccy'], sort=False)['so_tk'].agg(_noi)
    kh['so_tk'] = kh['so_tk'].fillna('')
    return kh.reset_index()


def _trang_thai(truoc, sau, co_truoc):
    if not co_truoc or truoc == 0:
        return 'Mới' if sau != 0 else 'Không đổi'
    if sau == 0:
        return 'Tất toán'
    if sau > truoc:
        return 'Tăng'
    if sau < truoc:
        return 'Giảm'
    return 'Không đổi'


def so_sanh_kh(kh_a, kh_b):
    m = kh_a.merge(kh_b, on=['ma_kh', 'ccy'], how='outer', suffixes=('_truoc', '_sau'), indicator=True)
    co_truoc = m['_merge'] != 'right_only'
    for c in ('so_du', 'kkh', 'ckh', 'so_luong_tk'):
        m[f'{c}_truoc'] = m[f'{c}_truoc'].fillna(0)
        m[f'{c}_sau'] = m[f'{c}_sau'].fillna(0)
    for c in ('ten_kh', 'loai_kh', 'sdt', 'cccd'):
        sau = m[f'{c}_sau'].fillna('')
        m[c] = sau.where(sau != '', m[f'{c}_truoc'].fillna(''))
    for c in ('can_bo', 'pgd', 'so_tk'):
        m[f'{c}_truoc'] = m[f'{c}_truoc'].fillna('')
        m[f'{c}_sau'] = m[f'{c}_sau'].fillna('')
    # Cán bộ/PGD "hiện tại": kỳ sau, KH đã tất toán thì lấy kỳ trước
    m['can_bo'] = m['can_bo_sau'].where(m['so_du_sau'] != 0, m['can_bo_truoc'])
    m['pgd'] = m['pgd_sau'].where(m['so_du_sau'] != 0, m['pgd_truoc'])

    m['chenh_lech'] = m['so_du_sau'] - m['so_du_truoc']
    m['cl_kkh'] = m['kkh_sau'] - m['kkh_truoc']
    m['cl_ckh'] = m['ckh_sau'] - m['ckh_truoc']
    m['ty_le'] = (m['chenh_lech'] / m['so_du_truoc'].where(m['so_du_truoc'] != 0)).astype(float)
    m['trang_thai'] = [_trang_thai(a, b, c) for a, b, c in zip(m['so_du_truoc'], m['so_du_sau'], co_truoc)]
    # Đổi cán bộ / PGD: KH có số dư ở cả 2 kỳ mà cán bộ (PGD) chính khác nhau
    ca_hai = (m['so_du_truoc'] != 0) & (m['so_du_sau'] != 0)
    m['doi_can_bo'] = ca_hai & (m['can_bo_truoc'] != m['can_bo_sau']) & (m['can_bo_truoc'] != '') & (m['can_bo_sau'] != '')
    m['doi_pgd'] = ca_hai & (m['pgd_truoc'] != m['pgd_sau']) & (m['pgd_truoc'] != '') & (m['pgd_sau'] != '')
    m = m[(m['so_du_truoc'] != 0) | (m['so_du_sau'] != 0)].drop(columns=[
        '_merge', 'ten_kh_truoc', 'ten_kh_sau', 'loai_kh_truoc', 'loai_kh_sau',
        'sdt_truoc', 'sdt_sau', 'cccd_truoc', 'cccd_sau'])
    m = m.assign(_abs=m['chenh_lech'].abs()).sort_values(['ccy', '_abs'], ascending=[True, False])
    return m.drop(columns='_abs').reset_index(drop=True)


def so_sanh_nhom(tk_a, tk_b, kh, cot):
    """Tổng hợp theo cán bộ / PGD (cot) + loại tiền, tính từ số dư từng TK của mỗi kỳ."""
    def tong(tk):
        tk = tk.assign(kkh=tk['so_du'].where(tk['nhom'] == 'KKH', 0),
                       ckh=tk['so_du'].where(tk['nhom'] == 'CKH', 0))
        co_du = tk[tk['so_du'] != 0]
        g = tk.groupby([cot, 'ccy'])[['so_du', 'kkh', 'ckh']].sum()
        g['so_kh'] = co_du.groupby([cot, 'ccy'])['ma_kh'].nunique()
        return g
    a, b = tong(tk_a), tong(tk_b)
    m = a.join(b, how='outer', lsuffix='_truoc', rsuffix='_sau').fillna(0).reset_index()
    m['chenh_lech'] = m['so_du_sau'] - m['so_du_truoc']
    m['cl_kkh'] = m['kkh_sau'] - m['kkh_truoc']
    m['cl_ckh'] = m['ckh_sau'] - m['ckh_truoc']
    m['ty_le'] = (m['chenh_lech'] / m['so_du_truoc'].where(m['so_du_truoc'] != 0)).astype(float)
    # Số KH theo trạng thái — KH tính cho cán bộ/PGD "hiện tại" của KH
    dem = kh.groupby([cot, 'ccy', 'trang_thai']).size().unstack(fill_value=0)
    for t in TRANG_THAI:
        m[f'kh_{t}'] = [int(dem.at[(x, c), t]) if (x, c) in dem.index and t in dem.columns else 0
                        for x, c in zip(m[cot], m['ccy'])]
    m = m[(m['so_du_truoc'] != 0) | (m['so_du_sau'] != 0)]
    m[cot] = m[cot].replace('', '(Không có)')
    return m.rename(columns={cot: 'ten'}).sort_values(['ccy', 'chenh_lech'], ascending=[True, False]).reset_index(drop=True)


def tong_hop(kh):
    """1 dòng / loại tiền: tổng 2 kỳ, KKH/CKH, số KH, số KH + chênh lệch theo trạng thái."""
    rows = []
    for ccy, g in kh.groupby('ccy', sort=True):
        r = {'ccy': ccy}
        for c in ('so_du', 'kkh', 'ckh'):
            r[f'{c}_truoc'] = g[f'{c}_truoc'].sum()
            r[f'{c}_sau'] = g[f'{c}_sau'].sum()
        r['chenh_lech'] = r['so_du_sau'] - r['so_du_truoc']
        r['cl_kkh'] = r['kkh_sau'] - r['kkh_truoc']
        r['cl_ckh'] = r['ckh_sau'] - r['ckh_truoc']
        r['ty_le'] = r['chenh_lech'] / r['so_du_truoc'] if r['so_du_truoc'] else None
        r['so_kh_truoc'] = int((g['so_du_truoc'] != 0).sum())
        r['so_kh_sau'] = int((g['so_du_sau'] != 0).sum())
        for t in TRANG_THAI:
            gt = g[g['trang_thai'] == t]
            r[f'kh_{t}'] = len(gt)
            r[f'cl_{t}'] = gt['chenh_lech'].sum()
        rows.append(r)
    return pd.DataFrame(rows)


def theo_loai_kh(kh):
    g = kh.assign(loai_kh=kh['loai_kh'].replace('', '(Không rõ)')).groupby(['ccy', 'loai_kh'])
    m = g[['so_du_truoc', 'so_du_sau', 'chenh_lech', 'cl_kkh', 'cl_ckh']].sum()
    m['so_kh_truoc'] = g['so_du_truoc'].agg(lambda x: int((x != 0).sum()))
    m['so_kh_sau'] = g['so_du_sau'].agg(lambda x: int((x != 0).sum()))
    m['kh_Mới'] = g['trang_thai'].agg(lambda x: int((x == 'Mới').sum()))
    m['kh_Tất toán'] = g['trang_thai'].agg(lambda x: int((x == 'Tất toán').sum()))
    m = m.reset_index()
    m['ty_le'] = (m['chenh_lech'] / m['so_du_truoc'].where(m['so_du_truoc'] != 0)).astype(float)
    return m.sort_values(['ccy', 'so_du_sau'], ascending=[True, False]).reset_index(drop=True)


def gan_dang_ky_hdv(kh, tu_ngay, den_ngay):
    """Gắn đăng ký chỉ tiêu HĐV (CCCD khớp, ngày dự kiến gửi trong (tu_ngay, den_ngay])."""
    from .models import HDVRegistration
    kh['dk_so_tien'] = 0
    kh['dk_can_bo'] = ''
    if not (tu_ngay and den_ngay) or not (kh['cccd'] != '').any():
        return kh, False
    regs = HDVRegistration.objects.filter(
        ngay_dk_huy_dong__gt=tu_ngay, ngay_dk_huy_dong__lte=den_ngay,
    ).values('cccd', 'loai_tien', 'so_tien', 'ten_can_bo', 'ma_can_bo')
    tong, can_bo = {}, {}
    for r in regs:
        key = ((r['cccd'] or '').strip().lstrip('0'), (r['loai_tien'] or 'VND').upper())
        tong[key] = tong.get(key, 0) + (r['so_tien'] or 0)
        can_bo.setdefault(key, []).append(r['ten_can_bo'] or r['ma_can_bo'])
    keys = list(zip(kh['cccd'].str.lstrip('0'), kh['ccy']))
    kh['dk_so_tien'] = [tong.get(k, 0) for k in keys]
    kh['dk_can_bo'] = [_noi(can_bo.get(k, [])) for k in keys]
    return kh, True


def xu_huong(ky_list):
    """ky_list: [(nhãn kỳ, DataFrame TK)] ≥ 3 kỳ → (tổng theo kỳ, cán bộ × kỳ, KH × kỳ)."""
    tong_rows, cb, kh = [], [], []
    for nhan, tk in ky_list:
        for ccy, g in tk.groupby('ccy'):
            tong_rows.append({
                'ky': nhan, 'ccy': ccy, 'so_du': g['so_du'].sum(),
                'kkh': g.loc[g['nhom'] == 'KKH', 'so_du'].sum(),
                'ckh': g.loc[g['nhom'] == 'CKH', 'so_du'].sum(),
                'so_kh': g.loc[g['so_du'] != 0, 'ma_kh'].nunique(),
            })
        cb.append(tk.groupby(['can_bo', 'ccy'])['so_du'].sum().rename(nhan))
        kh.append(tk.groupby(['ma_kh', 'ccy'])['so_du'].sum().rename(nhan))
    nhan_ky = [n for n, _ in ky_list]
    cb_df = pd.concat(cb, axis=1).fillna(0).reset_index()
    cb_df['can_bo'] = cb_df['can_bo'].replace('', '(Không có)')
    cb_df['chenh_lech'] = cb_df[nhan_ky[-1]] - cb_df[nhan_ky[0]]
    kh_df = pd.concat(kh, axis=1).fillna(0).reset_index()
    ten = pd.concat([tk[['ma_kh', 'ten_kh']] for _, tk in ky_list]).drop_duplicates('ma_kh', keep='last')
    kh_df = kh_df.merge(ten, on='ma_kh', how='left')
    kh_df['chenh_lech'] = kh_df[nhan_ky[-1]] - kh_df[nhan_ky[0]]
    kh_df = kh_df[(kh_df[nhan_ky] != 0).any(axis=1)]
    return (pd.DataFrame(tong_rows),
            cb_df.sort_values(['ccy', 'chenh_lech'], ascending=[True, False]).reset_index(drop=True),
            kh_df.sort_values(['ccy', 'chenh_lech'], ascending=[True, False]).reset_index(drop=True))


def phan_tich(files, loai):
    """files: list UploadedFile (≥ 2). → dict kết quả (lưu tạm, dùng cho trang xem + Excel)."""
    ky = []
    co_chung = set(TRUONG_TUY_CHON)
    for i, f in enumerate(files):
        ngay, tk, co = doc_tai_khoan(f, loai)
        ky.append((ngay, i, f.name, tk))
        co_chung &= co
    # Sắp theo ngày trong tên file; file không có ngày giữ thứ tự chọn
    if all(k[0] for k in ky):
        ky.sort(key=lambda k: k[0])
        ngays = [k[0] for k in ky]
        if len(set(ngays)) != len(ngays):
            raise FileLoi('Có 2 file trùng ngày dữ liệu — hãy kiểm tra lại các file đã chọn.')
    nhan = [k[0].strftime('%d/%m/%Y') if k[0] else f'Kỳ {j}' for j, k in enumerate(ky, 1)]

    tk_a, tk_b = ky[0][3], ky[-1][3]
    kh = so_sanh_kh(_theo_kh(tk_a), _theo_kh(tk_b))
    kh, co_dk = gan_dang_ky_hdv(kh, ky[0][0], ky[-1][0])
    kq = {
        'loai': loai,
        'nhan_file': LOAI_FILE[loai]['nhan'],
        'ky': [{'nhan': n, 'file': k[2]} for n, k in zip(nhan, ky)],
        'nhan_truoc': nhan[0],
        'nhan_sau': nhan[-1],
        'co': sorted(co_chung | ({'nhom'} if (tk_a['nhom'] != '').any() else set())),
        'co_dk': co_dk,
        'kh': kh,
        'tong': tong_hop(kh),
        'can_bo': so_sanh_nhom(tk_a, tk_b, kh, 'can_bo') if 'can_bo' in co_chung else None,
        'pgd': so_sanh_nhom(tk_a, tk_b, kh, 'pgd') if 'pgd' in co_chung else None,
        'loai_kh': theo_loai_kh(kh) if 'loai_kh' in co_chung else None,
        'xu_huong': xu_huong([(n, k[3]) for n, k in zip(nhan, ky)]) if len(ky) >= 3 else None,
    }
    return kq

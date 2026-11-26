"""
Đối chiếu Hóa đơn điện tử (Einvoice) với IPCAS (GLST30 – Day, SOLD) và lập file import HĐĐT.

Viết lại theo macro "DOI CHIEU HDDT.xlsm" (Module1: rundoichieu / runlaphd):

1. Einvoice (xuất từ website/BKCT, tiêu đề dòng 6): khoá = TTV & SEQ; tiền thuế VND = Tiền thuế × Tỉ giá.
   Kiểm tra lỗi: chưa ký (Goc + ChoKy), đảo doanh thu thành tổng thanh toán (Tổng TT − Thuế − DS < 0),
   sai tỷ giá (VND ≠ 1, USD/GBP = 1), HĐ doanh nghiệp chưa có MST (KH loại C, Goc).
2. IPCAS (tiêu đề dòng 1): khoá = user & trseq, dò thuế bên Einvoice.
   P = 2 nếu không có HĐ hoặc (thuế HĐ + amt) < 10; Q (cho dòng P=2): 1 = có HĐ, 2 = thiếu HĐ cần lập,
   0 = bỏ qua (7202CD sau 21/07/2022, ATM/POS không có remark dài).
3. Tổng hợp theo user: Einvoice (thuế HĐ Goc theo TTV), Ipcas (tổng amt), Chênh lệch = Ipcas − Einvoice,
   Số món lệch = số dòng Q=2 của user (khi có chênh lệch).
4. File import: gom chênh lệch — 7202CD → Phí thường niên; 7202EI → Phí dịch vụ kiều hối (USD, cần tỷ giá);
   còn lại → Phí dịch vụ chuyển tiền. Thêm được hoá đơn riêng (vd Thu lãi tiền vay cho DN yêu cầu xuất riêng).
"""
import io
import re
from datetime import date, datetime

import pandas as pd

from .report_views import _read_excel_safe

MOC_CD = date(2022, 7, 21)

# Thông tin dòng gom "bán lẻ" (theo các file import đã lập)
MAC_DINH = {
    'ten_kh': 'Bán cho người tiêu dùng',
    'dia_chi': 'Giá Rai',
    'tai_ngan_hang': 'AgriBank chi nhánh Giá Rai Bạc Liêu',
    'ma_ttv': '0002',
    'ht_thanh_toan': 'TM/CK',
    'cif': '000000000',
}

# (Tên hàng, Nội dung hoá đơn, Thuế suất)
NHOM_IMPORT = {
    'chuyen_tien': ('Phí dịch vụ chuyển tiền', 'Thu phí chuyển tiền', 10),
    'thuong_nien': ('Phí thường niên', 'Thu phí thường niên', 10),
    'kieu_hoi': ('Phí dịch vụ kiều hối', 'Thu phí DV kiều hối', 10),
}
# Hoá đơn riêng (khách hàng yêu cầu xuất riêng)
HANG_RIENG = {
    'lai_vay': ('Thu lãi tiền vay', 'Thu lãi tiền vay', -1),
    'quan_ly_tk': ('Thu phí quản lý tài khoản', 'Thu phí quản lý tài khoản', 10),
    'chuyen_tien': ('Phí dịch vụ chuyển tiền', 'Thu phí chuyển tiền', 10),
    'thuong_nien': ('Phí thường niên', 'Thu phí thường niên', 10),
}

IMPORT_HEADERS = [
    'GroupId *', 'Giờ giao dịch* ', 'Ngày HĐ*', 'HT thanh toán*', 'Tiền tệ*', 'Tỷ giá*', 'Số CIF*', 'Tên khách hàng*',
    'Mã số thuế ', 'Địa chỉ', 'Mã số đơn vị có quan hệ với ngân sách', 'Số CC/CCCD/Định danh',
    'Số hộ chiếu/giấy tờ xuất/nhập cảnh', 'Số tài khoản ', 'Tại ngân hàng', 'Email người mua', 'Loại khách hàng *',
    'Mã TTV*', 'MerNo', 'BidNo', 'Tổng tiền chưa có thuế GTGT *', 'Tổng cộng tiền thuế GTGT*',
    'Tổng tiền thanh toán đã có thuế GTGT*', 'Nội dung hóa đơn', 'Tên hàng*', 'Nội dung hàng hóa', 'ĐVT', 'Số lượng',
    'Đơn giá', 'Thành tiền chưa có thuế GTGT*', 'Thuế suất GTGT*', 'Tiền thuế GTGT*', 'Thành tiền có thuế GTGT*',
    'RefNo ', 'Màu xanh: Header',
]


class FileLoi(Exception):
    """Lỗi file — thông báo hiển thị thẳng cho người dùng."""


# ── Đọc file ──────────────────────────────────────────────────────────────────

def _s(series):
    return series.fillna('').astype(str).str.strip()


def _trim(series):
    """TRIM của Excel: bỏ khoảng trắng đầu/cuối và gộp khoảng trắng giữa."""
    return series.fillna('').astype(str).str.split().str.join(' ')


def _so(series):
    return pd.to_numeric(_s(series).str.replace(',', '', regex=False), errors='coerce').fillna(0)


def _ngay(v):
    v = str(v or '').strip()
    for fmt in ('%d/%m/%Y', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            return datetime.strptime(v, fmt).date()
        except ValueError:
            pass
    return None


def ma_ngay(ten_file):
    """'0511.xlsx' → '0511' (tên file đặt theo ngày tháng DDMM như macro cũ)."""
    m = re.match(r'\s*(\d{4})', ten_file.rsplit('/', 1)[-1].rsplit('\\', 1)[-1])
    return m.group(1) if m else None


def _cat_den_dong_trong(df, cot):
    """Macro dừng ở dòng đầu tiên có cột A trống."""
    trong = _s(df[cot]) == ''
    return df[:trong.idxmax()] if trong.any() else df


def doc_einvoice(f):
    try:
        df = _read_excel_safe(f, header=5, dtype=str)
    except Exception as e:
        raise FileLoi(f'Không đọc được file Einvoice {f.name}: {e}')
    return chuan_einvoice(df, f.name)


def chuan_einvoice(df, ten='Einvoice'):
    """DataFrame Einvoice thô (tiêu đề dòng 6) → bảng chuẩn hoá + cờ lỗi."""
    df.columns = [str(c).replace('﻿', '').strip() for c in df.columns]
    can = ['STT', 'TTV', 'SEQ', 'Tiền thuế GTGT', 'Tỉ giá', 'Tình trạng hóa đơn']
    thieu = [c for c in can if c not in df.columns]
    if thieu:
        raise FileLoi(f'File {ten} không phải file Einvoice (tiêu đề dòng 6) — thiếu cột: {", ".join(thieu)}.')
    df = _cat_den_dong_trong(df.reset_index(drop=True), 'STT')
    out = pd.DataFrame({
        'stt': _s(df['STT']),
        'so_hd': _s(df.get('Số hóa đơn', pd.Series(dtype=str))),
        'ttv': _s(df['TTV']),
        'seq': _s(df['SEQ']),
        'ten_nguoi_mua': _s(df.get('Tên người mua', pd.Series(dtype=str))),
        'mst': _s(df.get('Mã số thuế người mua', pd.Series(dtype=str))),
        'ten_hang': _s(df.get('Tên hàng hóa', pd.Series(dtype=str))),
        'tien_thue': _so(df['Tiền thuế GTGT']),
        'ty_gia': _so(df['Tỉ giá']),
        'tien_te': _s(df.get('Tiền tệ', pd.Series(dtype=str))),
        'tinh_trang': _s(df['Tình trạng hóa đơn']),
        'tinh_trang_ky': _s(df.get('Tình trạng ký', pd.Series(dtype=str))),
        'loai_nv': _s(df.get('Loại nghiệp vụ', pd.Series(dtype=str))),
        'loai_kh': _s(df.get('Loại khách hàng', pd.Series(dtype=str))),
        'tong_ds': _so(df.get('Tổng doanh số bán chưa có thuế', pd.Series(dtype=str))),
        'tong_thue': _so(df.get('Tổng tiền thuế GTGT', pd.Series(dtype=str))),
        'tong_tt': _so(df.get('Tổng tiền thanh toán', pd.Series(dtype=str))),
        'don_gia': _so(df.get('Đơn giá', pd.Series(dtype=str))),
        'doanh_so': _so(df.get('Doanh số bán chưa có thuế', pd.Series(dtype=str))),
        'thue_suat': _so(df.get('Thuế suất GTGT', pd.Series(dtype=str))),
        'cong_tien_hang': _so(df.get('Cộng tiền hàng', pd.Series(dtype=str))),
        'so_cif': _s(df.get('Số cif', pd.Series(dtype=str))),
        'ngay_hd': _s(df.get('Ngày hóa đơn', pd.Series(dtype=str))),
    })
    out['khoa'] = _trim(out['ttv'] + out['seq'])
    out['thue_vnd'] = out['tien_thue'] * out['ty_gia']
    goc = out['tinh_trang'] == 'Goc'
    out['loi_chua_ky'] = goc & (out['tinh_trang_ky'] == 'ChoKy')
    out['loi_dao_dt'] = goc & ((out['tong_tt'] - out['tong_thue'] - out['tong_ds']) < 0)
    out['loi_ty_gia'] = (((out['tien_te'] == 'VND') & (out['ty_gia'] != 1))
                         | (out['tien_te'].isin(['USD', 'GBP']) & (out['ty_gia'] == 1)))
    out['loi_mst'] = goc & (out['loai_kh'] == 'C') & (out['mst'] == '')
    # Kiểm tra thêm (theo file "DCHD" của chi nhánh bạn)
    khong_chiu_thue = (out['thue_suat'] == -1) & ((out['loai_nv'].str.upper() == 'LN')
                                                 | out['ten_hang'].str.startswith(HANG_KHONG_CHIU_THUE))
    out['loi_don_gia'] = goc & ((out['don_gia'] - out['doanh_so']).abs() > 0.5)
    out['loi_thue_suat'] = goc & (out['thue_suat'] != 10) & ~khong_chiu_thue
    ty_le = (out['tien_thue'] / out['doanh_so'].where(out['doanh_so'] != 0)).round(2)
    out['loi_tien_thue'] = goc & (out['thue_suat'] == 10) & ((out['tien_thue'] == 0) | (ty_le != 0.1))
    out['loi_tong'] = goc & ((out['cong_tien_hang'] - out['doanh_so'] - out['tien_thue']).abs() > 0.5) \
        & ((out['tong_tt'] - out['tong_ds'] - out['tong_thue']).abs() > 0.5)
    # HĐ lãi (LN, lãi thấu chi…) do hệ thống tự phát hành, không có user → không bắt lỗi
    out['loi_khong_user'] = goc & ~khong_chiu_thue & (out['loai_nv'].str.upper() != 'LN') & out['ttv'].isin(['', '0'])
    return out


# Hàng hoá được phép thuế suất -1 (không chịu thuế) ngoài nghiệp vụ LN
HANG_KHONG_CHIU_THUE = ('Thu lãi', 'Lãi ', 'Thu phí chậm trả', 'Phí trả nợ trước hạn',
                        'Thu khác - dịch vụ không chịu thuế', 'Thu từ nghiệp vụ bảo lãnh')
# (cột cờ lỗi, nhãn hiển thị, màu badge)
LOI_HD = [
    ('loi_chua_ky', 'Chưa ký', 'danger'),
    ('loi_dao_dt', 'Đảo doanh thu thành tổng thanh toán', 'success'),
    ('loi_ty_gia', 'Sai tỷ giá', 'primary'),
    ('loi_mst', 'DN chưa có MST', 'warning'),
    ('loi_don_gia', 'Đơn giá ≠ doanh số chưa thuế', 'secondary'),
    ('loi_thue_suat', 'Kiểm tra lại thuế suất', 'secondary'),
    ('loi_tien_thue', 'Kiểm tra lại tiền GTGT (≠ 10%)', 'secondary'),
    ('loi_tong', 'Tổng thanh toán ≠ đơn giá + VAT', 'secondary'),
    ('loi_khong_user', 'Không có user (TTV)', 'secondary'),
]


def doc_ipcas(f):
    try:
        df = _read_excel_safe(f, dtype=str)
    except Exception as e:
        raise FileLoi(f'Không đọc được file IPCAS {f.name}: {e}')
    df.columns = [str(c).strip() for c in df.columns]
    can = ['user', 'trseq', 'trdate', 'tramt', 'amt']
    thieu = [c for c in can if c not in df.columns]
    if thieu:
        raise FileLoi(f'File {f.name} không phải file IPCAS GLST30 — thiếu cột: {", ".join(thieu)}.')
    df = _cat_den_dong_trong(df.reset_index(drop=True), 'user')
    out = pd.DataFrame({c: _s(df[c]) if c in df.columns else '' for c in
                        ('user', 'trseq', 'trdate', 'cust', 'taxcode', 'slip1', 'item', 'rate', 'remark', 'serino', 'frmid')})
    out['tramt'] = _so(df['tramt'])
    out['amt'] = _so(df['amt'])
    out['khoa'] = _trim(out['user'] + out['trseq'])
    return out


# ── Đối chiếu ────────────────────────────────────────────────────────────────

def _q(row):
    if not pd.isna(row['thue_hd']):
        return 1
    u, d = row['user'], _ngay(row['trdate'])
    if u[4:6] == 'CD' and u[:1] == '7' and d and d > MOC_CD:
        return 0
    loai = u[4:7]
    if (loai not in ('ATM', 'POS')) or (loai == 'ATM' and len(row['remark'].strip()) > 10):
        return 2
    return 0


def doi_chieu(ei, ip):
    """→ dict: tong_hop (DataFrame theo user), ipcas (DataFrame có thue_hd/p/q), loi_hd (DataFrame)."""
    thue_theo_khoa = ei.drop_duplicates('khoa').set_index('khoa')['thue_vnd']  # VLOOKUP: lấy dòng đầu
    ip = ip.copy()
    ip['thue_hd'] = ip['khoa'].map(thue_theo_khoa)
    ip['p'] = [2 if pd.isna(o) or (o + a) < 10 else 0 for o, a in zip(ip['thue_hd'], ip['amt'])]
    ip['q'] = [(_q(r) if r['p'] == 2 else None) for _, r in ip.iterrows()]
    ip = ip.assign(_q=ip['q'].fillna(-1)).sort_values(['p', '_q'], kind='stable').drop(columns='_q')

    users = sorted((set(ip['user']) | set(ei['ttv'])) - {''})
    ei_goc = ei[ei['tinh_trang'] == 'Goc']
    b = ei_goc.groupby('ttv')['thue_vnd'].sum()
    c = ip.groupby('user')['amt'].sum()
    mon = ip[ip['q'] == 2].groupby('user').size()
    rows = []
    for u in users:
        bb, cc = float(b.get(u, 0)), float(c.get(u, 0))
        d = round(cc - bb, 2)
        rows.append({'user': u, 'einvoice': bb, 'ipcas': cc, 'chenh_lech': d,
                     'so_mon_lech': 0 if d == 0 else int(mon.get(u, 0)), 'nhom': nhom_cua_user(u)})
    tong_hop = pd.DataFrame(rows, columns=['user', 'einvoice', 'ipcas', 'chenh_lech', 'so_mon_lech', 'nhom'])

    loi = ei[ei[[c for c, _, _ in LOI_HD]].any(axis=1)].copy()
    ngays = {d for d in ip['trdate'] if d}
    return {'tong_hop': tong_hop, 'ipcas': ip.reset_index(drop=True), 'loi_hd': loi,
            'ngay': _ngay(sorted(ngays)[0]) if ngays else None,
            'so_dong_ei': len(ei), 'so_dong_ip': len(ip)}


def nhom_cua_user(u):
    if u[4:6] == 'CD':
        return 'thuong_nien'
    if u[4:6] == 'EI':
        return 'kieu_hoi'
    return 'chuyen_tien'


# Chênh lệch âm lớn của 1 user thường là HĐ lập riêng (vd thuế GTGT bán đấu giá tài sản) → mặc định không gom
NGUONG_AM_LON = -1_000_000


def user_bo_mac_dinh(kq):
    th = kq['tong_hop']
    return set(th.loc[th['chenh_lech'] <= NGUONG_AM_LON, 'user'])


def gom_import(kq, bo_user=None):
    """Số tiền thuế VND cần lập HĐ theo nhóm (= tổng chênh lệch các user trong nhóm, trừ user bị bỏ) + kiều hối."""
    if bo_user is None:
        bo_user = user_bo_mac_dinh(kq)
    th = kq['tong_hop'][~kq['tong_hop']['user'].isin(bo_user)]
    tong = th.groupby('nhom')['chenh_lech'].sum().to_dict()
    ip = kq['ipcas']
    ei_rows = ip[(ip['user'].str[4:6] == 'EI') & (ip['q'] == 2) & ~ip['user'].isin(bo_user)]
    return {
        'chuyen_tien': round(tong.get('chuyen_tien', 0)),
        'thuong_nien': round(tong.get('thuong_nien', 0)),
        'kieu_hoi': round(tong.get('kieu_hoi', 0)),
        'kieu_hoi_tramt': float(ei_rows['tramt'].sum()),
        'kieu_hoi_amt': float(ei_rows['amt'].sum()),
    }


# ── Xuất Excel ───────────────────────────────────────────────────────────────

def _style():
    from openpyxl.styles import Border, Font, PatternFill, Side
    thin = Side(style='thin', color='BBBBBB')
    return {
        'head': Font(bold=True, color='FFFFFF'), 'head_fill': PatternFill('solid', fgColor='9C1C2B'),
        'border': Border(left=thin, right=thin, top=thin, bottom=thin), 'bold': Font(bold=True),
        'vang': PatternFill('solid', fgColor='FFFF00'), 'xanh': PatternFill('solid', fgColor='00B0F0'),
        'do': PatternFill('solid', fgColor='FF0000'), 'xanh_la': PatternFill('solid', fgColor='92D050'),
    }


def xuat_ket_qua(kq, ma):
    """File kết quả như ketquaDDMMYYYY.xlsx của macro: sheet Ipcas (thêm cột khoá / thuế HĐ / P / Q,
    tô vàng dòng thiếu HĐ, xanh dòng lệch có HĐ) + bảng tổng hợp theo user bên dưới; thêm sheet lỗi Einvoice."""
    from openpyxl import Workbook
    st = _style()
    wb = Workbook()
    ws = wb.active
    ws.title = 'Ipcas'
    cols = ['user', 'trseq', 'trdate', 'cust', 'taxcode', 'tramt', 'amt', 'slip1', 'item', 'rate', 'remark', 'serino', 'frmid']
    ws.append(cols + ['khoa', 'thue_hd', 'P', 'Q'])
    ip = kq['ipcas']
    for r in ip.itertuples(index=False):
        ws.append([r.user, r.trseq, r.trdate, r.cust, r.taxcode, r.tramt, r.amt, r.slip1, r.item, r.rate, r.remark,
                   r.serino, r.frmid, r.khoa, None if pd.isna(r.thue_hd) else r.thue_hd, r.p,
                   None if pd.isna(r.q) else int(r.q)])
        fill = st['vang'] if r.q == 2 else (st['xanh'] if r.q == 1 else None)
        if fill:
            for c in ws[ws.max_row]:
                c.fill = fill
    n = ws.max_row
    ws.append([None] * 6 + [f'=SUM(G2:G{n})', None, None, None, None, None, None, None, None,
                            int((ip['p'] == 2).sum()), int((ip['q'] == 2).sum())])
    ws.append([ma, None, None, None, None, None, f'=SUMIF(Q2:Q{n},2,G2:G{n})'])
    for c in ws[n + 1] + ws[n + 2]:
        c.font = st['bold']
    ws.append([])
    ws.append([])
    r0 = ws.max_row + 1
    ws.append(['User', 'Einvoice', 'Ipcas', 'Chênh Lệch', 'Số Món Lệch'])
    for c in ws[r0]:
        c.font, c.fill, c.border = st['head'], st['head_fill'], st['border']
    th = kq['tong_hop']
    for r in th.itertuples(index=False):
        ws.append([r.user, r.einvoice, r.ipcas, r.chenh_lech, r.so_mon_lech])
        if r.chenh_lech:
            ws.cell(row=ws.max_row, column=4).fill = st['vang']
    ws.append(['Tổng', f'=SUM(B{r0 + 1}:B{ws.max_row})', f'=SUM(C{r0 + 1}:C{ws.max_row})',
               f'=SUM(D{r0 + 1}:D{ws.max_row})', f'=SUM(E{r0 + 1}:E{ws.max_row})'])
    for c in ws[ws.max_row]:
        c.font = st['bold']
    for row in ws.iter_rows(min_row=2):
        for c in row:
            if c.column in (6, 7, 15) or (c.row > r0 and c.column in (2, 3, 4)):
                c.number_format = '#,##0'
    for col, w in zip('ABCDEFGHIJKLMNOPQ', (12, 8, 11, 30, 12, 12, 10, 16, 6, 5, 28, 8, 10, 16, 10, 4, 4)):
        ws.column_dimensions[col].width = w

    # Lỗi hoá đơn Einvoice
    ws2 = wb.create_sheet('Loi Einvoice')
    ws2.append(['STT', 'Số hóa đơn', 'TTV', 'SEQ', 'Tên người mua', 'MST', 'Loại KH', 'Tiền tệ', 'Tỉ giá',
                'Tiền thuế', 'Tình trạng', 'Tình trạng ký', 'Lỗi'])
    for c in ws2[1]:
        c.font, c.fill = st['head'], st['head_fill']
    for r in kq['loi_hd'].itertuples(index=False):
        loi = [nhan for c, nhan, _ in LOI_HD if getattr(r, c)]
        ws2.append([r.stt, r.so_hd, r.ttv, r.seq, r.ten_nguoi_mua, r.mst, r.loai_kh, r.tien_te, r.ty_gia,
                    r.tien_thue, r.tinh_trang, r.tinh_trang_ky, '; '.join(loi)])
        fill = st['do'] if r.loi_chua_ky else st['xanh_la'] if r.loi_dao_dt else st['xanh'] if r.loi_ty_gia else st['vang']
        for c in ws2[ws2.max_row]:
            c.fill = fill
    ws2.column_dimensions['E'].width = 35
    ws2.column_dimensions['M'].width = 40
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


def dong_import(group_id, gio, ngay, ten_hang, noi_dung, thue_suat, u, v, kh=None, tien_te='VND', ty_gia=1):
    """1 dòng file import (35 cột). u = tiền chưa thuế, v = tiền thuế (theo tiền tệ của dòng)."""
    kh = {**MAC_DINH, **(kh or {})}
    w = round(u + v, 2)
    return [group_id, gio, ngay.strftime('%d/%m/%Y'), kh['ht_thanh_toan'], tien_te, ty_gia, kh['cif'], kh['ten_kh'],
            kh.get('mst') or None, kh.get('dia_chi') or None, None, None, None, kh.get('so_tk') or None,
            kh.get('tai_ngan_hang') or None, None, kh.get('loai_kh') or 'I', kh['ma_ttv'], None, None,
            u, v, w, noi_dung, ten_hang, None, 'Lần', 1, u, u, thue_suat, v, w, None, None]


def lap_dong_import(kq, gio, ty_gia_kh=None, rieng=(), cau_hinh=None, bo_user=None):
    """→ (dòng file chính, [(tên, dòng file riêng)], cảnh báo). rieng: các hoá đơn riêng người dùng nhập."""
    ngay = kq['ngay']
    gom = gom_import(kq, bo_user)
    kh_chung = {**MAC_DINH, **(cau_hinh or {})}
    chinh, canh_bao = [], []
    for nhom in ('chuyen_tien', 'thuong_nien'):
        v = gom[nhom]
        if v < 0:
            canh_bao.append(f'{NHOM_IMPORT[nhom][0]}: tổng chênh lệch âm ({v:,}) — không đưa vào file import, kiểm tra lại.')
        elif v:
            ten_hang, nd, ts = NHOM_IMPORT[nhom]
            chinh.append(dong_import(len(chinh) + 1, gio, ngay, ten_hang, nd, ts, v * 10, v, kh_chung))
    if gom['kieu_hoi'] or gom['kieu_hoi_amt']:
        if not ty_gia_kh:
            canh_bao.append('Có phí kiều hối (7202EI) — nhập tỷ giá quy đổi USD để đưa vào file import.')
        else:
            ten_hang, nd, ts = NHOM_IMPORT['kieu_hoi']
            # Số tiền ghi theo giá trị đã quy đổi VND (IPCAS đã là VND), cột Tiền tệ/Tỷ giá giữ USD + tỷ giá nhập
            u = round(gom['kieu_hoi_tramt'])
            v = round(gom['kieu_hoi_amt'] or gom['kieu_hoi'])
            if v < 0 or u < 0:
                canh_bao.append(f'{ten_hang}: tổng âm ({v:,}) — không đưa vào file import, kiểm tra lại.')
            else:
                chinh.append(dong_import(len(chinh) + 1, gio, ngay, ten_hang, nd, ts, u, v, kh_chung, 'USD', ty_gia_kh))
    rieng_files = {}
    for hd in rieng:
        ten_hang, nd, ts = HANG_RIENG[hd['loai']]
        u = round(hd['so_tien'])
        if u <= 0:
            canh_bao.append(f'HĐ riêng {hd["ten_kh"] or ""}: số tiền ≤ 0 — không đưa vào file import.')
            continue
        v = round(u * ts / 100) if ts > 0 else 0
        kh = {**kh_chung, 'cif': hd['cif'] or kh_chung['cif'], 'ten_kh': hd['ten_kh'], 'mst': hd['mst'],
              'dia_chi': hd['dia_chi'], 'so_tk': hd['so_tk'], 'loai_kh': hd['loai_kh'] or 'C'}
        if hd.get('file_rieng'):
            dsach = rieng_files.setdefault(hd['ten_kh'] or 'KH', [])
            dsach.append(dong_import(len(dsach) + 1, gio, ngay, ten_hang, hd['noi_dung'] or nd, ts, u, v, kh))
        else:
            chinh.append(dong_import(len(chinh) + 1, gio, ngay, ten_hang, hd['noi_dung'] or nd, ts, u, v, kh))
    return chinh, list(rieng_files.items()), canh_bao


def xuat_import(dong):
    """File import HĐĐT (sheet Invoice): dòng 1 tiêu đề, dòng 2 ghi chú loại KH, dòng 3 số thứ tự cột, từ dòng 4 dữ liệu."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, PatternFill
    wb = Workbook()
    ws = wb.active
    ws.title = 'Invoice'
    ws.append(IMPORT_HEADERS)
    ws.append([None] * 16 + ['I - Cá nhân\nC - Doanh nghiệp'])
    ws.append(list(range(1, 35)) + ['Detail'])
    xanh = PatternFill('solid', fgColor='BDD7EE')
    for c in ws[1]:
        c.fill = xanh
        c.alignment = Alignment(wrap_text=True, vertical='center')
    ws.cell(row=2, column=17).alignment = Alignment(wrap_text=True)
    for d in dong:
        ws.append(d)
    for row in ws.iter_rows(min_row=4):
        for c in row:
            if c.column in (21, 22, 23, 29, 30, 32, 33):
                c.number_format = '#,##0.##'
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()

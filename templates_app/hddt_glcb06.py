"""
Đối chiếu HĐĐT nguồn GLCB06 (sao kê theo bút toán) — cách làm của file "DCHD" (macro lay_user):

- GLCB06 (24 cột A–X xuất từ IPCAS, sao kê TK 453101 VAT đầu ra và các TK thu không chịu thuế 702…):
  TK = 6 số đầu acctnm; VAT = có − nợ (dòng 453101); dòng khác: số tiền = có − nợ (vd thu lãi 702…).
  Khoá bút toán: dòng 453101 → user-journal-VAT-loại tiền-453101; dòng khác → user-journal-số tiền-loại tiền-bucd.
- Einvoice: khoá TTV-SEQ-(thuế suất > 0 ? tiền thuế : doanh số)-tiền tệ-(thuế suất > 0 ? 453101 : loại nghiệp vụ).
- Bút toán không khớp hoá đơn → "Không có HĐ / gom user"; TK 702… → "Tiền vay" (cần lập HĐ lãi).
  Nếu tổng VAT của user (VND) bằng tổng thuế HĐ của user thì coi như khớp cả user (không xét từng món).
- Tổng hợp theo user + loại tiền: Ein (nguyên tệ / VND), IPCAS (nguyên tệ / VND), chênh lệch.
- GLCB41 (tuỳ chọn): cân đối — phát sinh có − nợ của 453101 / 702 / 711 so với tổng thuế / tổng HĐ không chịu thuế.
"""
import re

import pandas as pd

from .hddt_doi_chieu import FileLoi, _cat_den_dong_trong, _s, _so
from .report_views import _read_excel_safe

TK_VAT = '453101'
COT_GLCB06 = ['tran_time', 'dyhbr', 'user', 'journal', 'bucd', 'unit', 'trcd', 'cust', 'ccy', 'trtp', 'dramt', 'cramt',
              'bal', 'acbldrcr', 'beforebal', 'pre_bal', 'nd_hoa_don', 'nd_hang_hoa', 'brcdnm', 'inqdate', 'acctnm',
              'custnm', 'currency', 'dien_giai']


def _txt(x):
    """Số → chuỗi như Excel nối chuỗi (2000 → '2000', 0.36 → '0.36')."""
    if isinstance(x, str):
        return x
    if pd.isna(x):
        return ''
    if float(x) == int(x):
        return str(int(x))
    return ('%.10f' % x).rstrip('0').rstrip('.')


def _khoa(*phan):
    return re.sub(r'\s', '', '-'.join(_txt(p) for p in phan))


def doc_glcb06(f):
    try:
        df = _read_excel_safe(f, dtype=str)
    except Exception as e:
        raise FileLoi(f'Không đọc được file GLCB06 {f.name}: {e}')
    return chuan_glcb06(df, f.name)


def chuan_glcb06(df, ten='GLCB06'):
    df = df.iloc[:, :24].copy()
    if df.shape[1] < 24 or str(df.columns[2]).strip().lower() != 'user' or str(df.columns[3]).strip().lower() != 'journal':
        raise FileLoi(f'File {ten} không phải file GLCB06 (cần 24 cột A–X: tran_time, dyhbr, user, journal, …).')
    df.columns = COT_GLCB06
    df = _cat_den_dong_trong(df.reset_index(drop=True), 'tran_time')
    out = pd.DataFrame({c: _s(df[c]) for c in COT_GLCB06 if c not in ('dramt', 'cramt')})
    out['dramt'] = _so(df['dramt'])
    out['cramt'] = _so(df['cramt'])
    out['tk'] = out['acctnm'].str[:6]
    out['ccy'] = out['ccy'].str.upper()
    return out


def doc_glcb41(f):
    try:
        df = _read_excel_safe(f, dtype=str)
    except Exception as e:
        raise FileLoi(f'Không đọc được file GLCB41 {f.name}: {e}')
    df.columns = [str(c).strip().lower() for c in df.columns]
    if not {'ccy', 'acctcd', 'dramt', 'cramt'} <= set(df.columns):
        raise FileLoi(f'File {f.name} không phải file GLCB41 (cần cột ccy, Acctcd, dramt, cramt).')
    out = pd.DataFrame({'ccy': _s(df['ccy']).str.upper(),
                        'tk': _s(df['acctcd']).str.replace(r'\.0$', '', regex=True),
                        'ten_tk': _s(df['acctnm']) if 'acctnm' in df.columns else '',
                        'dramt': _so(df['dramt']), 'cramt': _so(df['cramt'])})
    return out[out['tk'] != '']


def _don_gia_glst30(glst30):
    """GLST30 (tuỳ chọn) → {user-trseq: tramt} để lấy đơn giá thật thay vì VAT × 10."""
    if glst30 is None:
        return {}
    return {_khoa(u, s): t for u, s, t in zip(glst30['user'], glst30['trseq'], glst30['tramt'])}


def doi_chieu_glcb06(ei, cb, glst30=None, cb41=None):
    """ei: Einvoice chuẩn hoá (hddt_doi_chieu.chuan_einvoice); cb: GLCB06 chuẩn hoá."""
    ei = ei.copy()
    cb = cb.copy()
    goc = ei['tinh_trang'].str.upper() == 'GOC'
    co_thue = ei['thue_suat'] > 0
    ei['khoa_cb'] = [_khoa(u, s, (v if t > 0 else d), tt, (TK_VAT if t > 0 else nv))
                     for u, s, v, d, tt, t, nv in zip(ei['ttv'], ei['seq'], ei['tien_thue'], ei['doanh_so'],
                                                      ei['tien_te'], ei['thue_suat'], ei['loai_nv'])]
    ei['user_tt'] = ['' if not u.strip() else _khoa(u, tt) for u, tt in zip(ei['ttv'], ei['tien_te'])]
    vnd = ei['tien_te'].str.upper() == 'VND'
    ttv_trong = ei['ttv'].str.strip() == ''
    # Ein nguyên tệ (không tính lãi vay): HĐ gốc ngoại tệ — thuế (TS > 0) hoặc doanh số (TS = -1)
    ei['ein_nt'] = 0.0
    ei.loc[goc & ~vnd & co_thue & ~ttv_trong, 'ein_nt'] = ei['tien_thue']
    ei.loc[goc & ~vnd & (ei['thue_suat'] == -1), 'ein_nt'] = ei['doanh_so']
    ei['ein_vnd'] = ei['ty_gia'] * ei['tien_thue']

    unit_cb = cb['unit'].str.lower() == 'cb'
    transfer = cb['dien_giai'].str.lower().str.startswith('transfer')
    la_vat = cb['tk'] == TK_VAT
    cb_vnd = cb['ccy'] == 'VND'
    so_tien = cb['cramt'] - cb['dramt']
    cb['user_tt'] = [_khoa(u, c) for u, c in zip(cb['user'], cb['ccy'])]
    cb['vat_nt'] = so_tien.where(~cb_vnd & ~unit_cb, 0)
    # VAT VND: dòng ngoại tệ lấy dòng VND cùng bút toán (user-journal-VND-TK)
    vnd_theo_bt = {(u, j, t): v for u, j, c, t, v in zip(cb['user'], cb['journal'], cb['ccy'], cb['tk'], so_tien) if c == 'VND'}
    cb['vat_vnd'] = [0.0 if (not vat or ucb or tr) else (st if c == 'VND' else vnd_theo_bt.get((u, j, t), st))
                     for vat, ucb, tr, c, u, j, t, st in zip(la_vat, unit_cb, transfer, cb['ccy'], cb['user'], cb['journal'],
                                                             cb['tk'], so_tien)]
    dg = _don_gia_glst30(glst30)
    don_gia, can_nhap = [], []
    for vat, ucb, u, j, vv, st in zip(la_vat, unit_cb, cb['user'], cb['journal'], cb['vat_vnd'], so_tien):
        if not vat:
            don_gia.append(st); can_nhap.append(False)
        elif ucb:
            don_gia.append(0.0); can_nhap.append(False)
        elif _khoa(u, j) in dg:
            don_gia.append(dg[_khoa(u, j)]); can_nhap.append(False)
        elif round(vv) % 10:          # VAT lẻ đơn vị đồng → đơn giá không phải VAT × 10, phải nhập
            don_gia.append(None); can_nhap.append(True)
        else:
            don_gia.append(vv * 10); can_nhap.append(False)
    cb['don_gia_vnd'] = don_gia
    cb['can_nhap_don_gia'] = can_nhap
    cb['thue_suat'] = [10 if v else -1 for v in la_vat]
    cb['khoa_ei'] = [_khoa(u, j, (vn if c != 'VND' else vv) if vat else ('' if c != 'VND' else (dgv if dgv is not None else '')),
                           c, TK_VAT if vat else bu)
                     for u, j, c, vat, vn, vv, dgv, bu in zip(cb['user'], cb['journal'], cb['ccy'], la_vat, cb['vat_nt'],
                                                              cb['vat_vnd'], cb['don_gia_vnd'], cb['bucd'])]
    # Khớp cả user: tổng VAT VND của user = tổng thuế HĐ của user
    vat_user = cb[la_vat].groupby('user_tt')['vat_vnd'].sum()
    thue_ein_user = ei.groupby('user_tt')['tien_thue'].sum()
    khop_user = {u for u, v in vat_user.items() if u.endswith('-VND') and v > 0 and abs(v - thue_ein_user.get(u, 0)) < 0.5}
    khoa_ei = set(ei['khoa_cb'])
    trang_thai = []
    for vat, ucb, tr, ut, k, tk in zip(la_vat, unit_cb, transfer, cb['user_tt'], cb['khoa_ei'], cb['tk']):
        if ucb or (vat and ut in khop_user) or (ucb and tr) or k in khoa_ei:
            trang_thai.append('khop')
        elif tk.startswith('702'):
            trang_thai.append('tien_vay')
        else:
            trang_thai.append('thieu_hd')
    cb['trang_thai'] = trang_thai

    khoa_cb = set(cb['khoa_ei'])
    la_lai = (ei['loai_nv'].str.lower() == 'ln') | ei['ten_hang'].str.startswith('Thu lãi')
    ei['khong_co_ipcas'] = ~la_lai & ~ei['khoa_cb'].isin(khoa_cb)

    users = sorted((set(cb['user_tt']) | set(ei['user_tt'])) - {''})
    so = lambda s: float(pd.to_numeric(s, errors='coerce').fillna(0).sum())  # noqa: E731
    rows = []
    for u in users:
        e_u, c_u = ei[ei['user_tt'] == u], cb[cb['user_tt'] == u]
        ein_nt, ein_vnd = float(e_u['ein_nt'].sum()), round(float(e_u['ein_vnd'].sum()))
        ip_nt = 0.0 if u.endswith('VND') else float(c_u.loc[c_u['tk'] == TK_VAT, 'vat_nt'].sum())
        ip_vnd = float(c_u.loc[c_u['tk'] == TK_VAT, 'vat_vnd'].sum()) + so(c_u.loc[c_u['tk'] != TK_VAT, 'don_gia_vnd'])
        rows.append({'user': u, 'ein_nt': ein_nt, 'ein_vnd': ein_vnd, 'ipcas_nt': ip_nt, 'ipcas_vnd': ip_vnd,
                     'cl_nt': round(ip_nt - ein_nt, 2), 'cl_vnd': round(ip_vnd - ein_vnd, 2),
                     'so_mon': int((c_u['trang_thai'] != 'khop').sum())})
    tong_hop = pd.DataFrame(rows, columns=['user', 'ein_nt', 'ein_vnd', 'ipcas_nt', 'ipcas_vnd', 'cl_nt', 'cl_vnd', 'so_mon'])
    return {'tong_hop': tong_hop, 'glcb06': cb, 'einvoice': ei, 'can_doi': can_doi(ei, cb41) if cb41 is not None else None,
            'so_can_nhap_don_gia': int((cb['can_nhap_don_gia'] & (cb['trang_thai'] != 'khop')).sum())}


CHE_DO_IMPORT = [
    ('ket_hop', 'Kết hợp: tổ chức & lãi vay lập HĐ từng bút toán, cá nhân gom theo nhóm phí'),
    ('chi_tiet', 'Lập HĐ từng bút toán (tất cả)'),
    ('gom', 'Gom theo nhóm phí (như cách cũ), lãi vay vẫn từng bút toán'),
]


def lap_dong_import_glcb06(kq, ngay, gio, ty_gia=None, che_do='ket_hop', tra_kh=None, cau_hinh=None):
    """Bút toán chưa có HĐ → dòng file import. tra_kh(cif) → dict KH (Khách hàng 360) hoặc None.
    → (dòng, cảnh báo)."""
    from . import hddt_doi_chieu as hd
    ty_gia = ty_gia or {}
    kh_chung = {**hd.MAC_DINH, **(cau_hinh or {})}
    cb = kq['glcb06']
    can = cb[cb['trang_thai'] != 'khop']
    dong, canh_bao, gom = [], [], {}
    thieu_ty_gia, nhap_dg = set(), 0
    cache = {}

    def kh_cua(cif):
        if cif not in cache:
            cache[cif] = tra_kh(cif) if (tra_kh and cif) else None
        return cache[cif]

    for r in can.itertuples(index=False):
        lai_vay = r.tk != TK_VAT             # thu không chịu thuế (702… lãi vay, thu khác)
        nhom = hd.nhom_cua_user(r.user)
        if not lai_vay:
            ten_hang, nd, ts = hd.NHOM_IMPORT[nhom]
        elif r.tk.startswith('702'):
            ten_hang, nd, ts = hd.HANG_RIENG['lai_vay']
        else:
            ten_hang, nd, ts = 'Thu khác - dịch vụ không chịu thuế', r.nd_hoa_don or 'Thu khác', -1
        ngoai_te = r.ccy != 'VND'
        tg = 1
        if ngoai_te:
            tg = ty_gia.get(r.ccy)
            if not tg:
                thieu_ty_gia.add(r.ccy)
                continue
        if lai_vay:
            u, v = (r.don_gia_vnd if not ngoai_te else r.cramt - r.dramt) or 0, 0
        else:
            v = r.vat_nt if ngoai_te else r.vat_vnd
            if r.don_gia_vnd is None or ngoai_te:
                u = round(v * 10, 2)
                nhap_dg += 1 if not ngoai_te else 0
            else:
                u = r.don_gia_vnd
        kh = kh_cua(r.cust)
        chi_tiet = che_do == 'chi_tiet' or lai_vay or (che_do == 'ket_hop' and kh and kh['loai_kh'] == 'C')
        if chi_tiet:
            thong_tin = {**kh_chung, **({k: kh[k] for k in ('cif', 'ten_kh', 'mst', 'dia_chi', 'so_tk', 'loai_kh')} if kh else {})}
            d = hd.dong_import(len(dong) + 1, gio, ngay, ten_hang, nd, ts, u, v, thong_tin, r.ccy, tg)
            d[33] = f'{r.user}-{r.journal}'          # RefNo: user-số bút toán để tra lại
            if r.nd_hang_hoa:
                d[25] = r.nd_hang_hoa                 # Nội dung hàng hoá (TK chuyển đổi)
            dong.append(d)
        else:
            g = gom.setdefault((nhom, r.ccy), {'u': 0, 'v': 0, 'tg': tg})
            g['u'] += u
            g['v'] += v
    for (nhom, ccy), g in sorted(gom.items()):
        ten_hang, nd, ts = hd.NHOM_IMPORT[nhom]
        if round(g['v'], 2) <= 0:
            canh_bao.append(f'{ten_hang} ({ccy}): tổng thuế ≤ 0 — không đưa vào file import, kiểm tra lại.')
            continue
        dong.append(hd.dong_import(len(dong) + 1, gio, ngay, ten_hang, nd, ts, round(g['u'], 2), round(g['v'], 2),
                                   kh_chung, ccy, g['tg']))
    if thieu_ty_gia:
        canh_bao.append(f'Có bút toán ngoại tệ ({", ".join(sorted(thieu_ty_gia))}) — nhập tỷ giá quy đổi để đưa vào file import.')
    if nhap_dg:
        canh_bao.append(f'{nhap_dg} bút toán có VAT lẻ đơn vị đồng: đơn giá đang tạm tính = VAT × 10 — kiểm tra lại '
                        '(hoặc tải kèm file GLST30 để lấy đơn giá thật).')
    if any(can['ccy'] != 'VND'):
        canh_bao.append('Bút toán ngoại tệ: đơn giá nguyên tệ đang tạm tính = VAT × 10 — kiểm tra lại trước khi import.')
    return dong, canh_bao


TRANG_THAI_BT = {'khop': 'Đã có HĐ', 'thieu_hd': 'Không có HĐ / gom user', 'tien_vay': 'Tiền vay (chưa có HĐ)'}


def xuat_ket_qua_glcb06(kq):
    import io

    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill

    from . import hddt_doi_chieu as hd
    wb = Workbook()
    head, fill = Font(bold=True, color='FFFFFF'), PatternFill('solid', fgColor='9C1C2B')
    vang = PatternFill('solid', fgColor='FFFF00')

    def sheet(ten, cols, rows, so=()):
        ws = wb.create_sheet(ten)
        ws.append([c for c, _ in cols])
        for c in ws[1]:
            c.font, c.fill = head, fill
        for r in rows:
            ws.append([r.get(k) for _, k in cols])
        for row in ws.iter_rows(min_row=2):
            for c in row:
                if c.column in so:
                    c.number_format = '#,##0.##'
        for i in range(1, len(cols) + 1):
            ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = 16
        return ws

    wb.remove(wb.active)
    th = kq['tong_hop'].to_dict('records')
    ws = sheet('Tong hop user', [('User - loại tiền', 'user'), ('Ein (nguyên tệ)', 'ein_nt'), ('Ein (VND)', 'ein_vnd'),
                                 ('IPCAS (nguyên tệ)', 'ipcas_nt'), ('IPCAS (VND)', 'ipcas_vnd'),
                                 ('Chênh lệch (nguyên tệ)', 'cl_nt'), ('Chênh lệch (VND)', 'cl_vnd'), ('Số món lệch', 'so_mon')],
               th, so=(2, 3, 4, 5, 6, 7))
    for i, r in enumerate(th, 2):
        if r['cl_nt'] or r['cl_vnd']:
            for c in ws[i]:
                c.fill = vang
    cb = kq['glcb06']
    can = cb[cb['trang_thai'] != 'khop'].assign(tt=lambda d: d['trang_thai'].map(TRANG_THAI_BT),
                                                 dg=lambda d: d['don_gia_vnd'].map(lambda x: 'Nhập đơn giá' if x is None else x))
    sheet('But toan chua co HD', [('User', 'user'), ('Bút toán', 'journal'), ('bucd', 'bucd'), ('unit', 'unit'), ('CIF', 'cust'),
                                  ('Khách hàng', 'custnm'), ('Loại tiền', 'ccy'), ('TK', 'tk'), ('Nợ', 'dramt'), ('Có', 'cramt'),
                                  ('VAT nguyên tệ', 'vat_nt'), ('VAT VND', 'vat_vnd'), ('Đơn giá VND', 'dg'),
                                  ('Nội dung hàng hoá', 'nd_hang_hoa'), ('Diễn giải', 'dien_giai'), ('Trạng thái', 'tt')],
          can.to_dict('records'), so=(9, 10, 11, 12, 13))
    ei = kq['einvoice']
    sheet('HD khong co IPCAS', [('Số HĐ', 'so_hd'), ('TTV', 'ttv'), ('SEQ', 'seq'), ('Người mua', 'ten_nguoi_mua'),
                                ('Tên hàng', 'ten_hang'), ('Tiền tệ', 'tien_te'), ('Thuế suất', 'thue_suat'),
                                ('Doanh số', 'doanh_so'), ('Tiền thuế', 'tien_thue')],
          ei[ei['khong_co_ipcas'] & (ei['tinh_trang'].str.upper() == 'GOC')].to_dict('records'), so=(8, 9))
    loi = kq['loi_hd'].assign(loi=lambda d: d.apply(lambda r: '; '.join(n for c, n, _ in hd.LOI_HD if r[c]), axis=1)) \
        if len(kq['loi_hd']) else kq['loi_hd'].assign(loi='')
    sheet('Loi Einvoice', [('Số HĐ', 'so_hd'), ('TTV', 'ttv'), ('SEQ', 'seq'), ('Người mua', 'ten_nguoi_mua'), ('MST', 'mst'),
                           ('Loại KH', 'loai_kh'), ('Tiền tệ', 'tien_te'), ('Tiền thuế', 'tien_thue'), ('Lỗi', 'loi')],
          loi.to_dict('records'), so=(8,))
    if kq.get('can_doi') is not None:
        sheet('Can doi GLCB41', [('TK', 'tk'), ('Nội dung', 'ten'), ('Phát sinh (có − nợ)', 'phat_sinh'), ('Trên hoá đơn', 'hoa_don'),
                                 ('Chênh lệch', 'chenh_lech'), ('Ghi chú', 'ghi_chu')],
              kq['can_doi'].to_dict('records'), so=(3, 4, 5))
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


def can_doi(ei, cb41):
    """Cân đối GLCB41: phát sinh có − nợ của 453101 / 702 / 711 so với tổng trên hoá đơn gốc (VND)."""
    goc = ei['tinh_trang'].str.upper() == 'GOC'
    thue_hd = float((ei.loc[goc & (ei['thue_suat'] > 0), 'tien_thue'] * ei.loc[goc & (ei['thue_suat'] > 0), 'ty_gia']).round().sum())
    kct = goc & (ei['thue_suat'] == -1)
    khong_thue_hd = float((ei.loc[kct, 'doanh_so'] * ei.loc[kct, 'ty_gia']).sum())
    co_thue = goc & (ei['thue_suat'] > 0)
    ds_co_thue = float((ei.loc[co_thue, 'doanh_so'] * ei.loc[co_thue, 'ty_gia']).sum())
    vnd = cb41[cb41['ccy'] == 'VND'].set_index('tk')
    rows = []
    for tk, ten, so_hd, ghi_chu in ((TK_VAT, 'Thuế GTGT đầu ra (453101)', thue_hd, 'so với tổng tiền thuế HĐ gốc'),
                                    ('702', 'Thu lãi (702)', khong_thue_hd, 'so với tổng HĐ không chịu thuế'),
                                    ('711', 'Thu phí dịch vụ (711)', ds_co_thue, 'so với tổng doanh số HĐ có thuế')):
        if tk not in vnd.index:
            continue
        r = vnd.loc[tk]
        r = r.iloc[0] if isinstance(r, pd.DataFrame) else r
        ps = float(r['cramt'] - r['dramt'])
        rows.append({'tk': tk, 'ten': ten, 'phat_sinh': ps, 'hoa_don': so_hd, 'chenh_lech': round(ps - so_hd, 2),
                     'ghi_chu': ghi_chu})
    return pd.DataFrame(rows, columns=['tk', 'ten', 'phat_sinh', 'hoa_don', 'chenh_lech', 'ghi_chu'])

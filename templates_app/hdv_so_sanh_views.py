"""
So sánh Huy động vốn theo file (theo kỳ): DP01 / MSIT81 (file TG) / RT13.

Kết quả phân tích lưu tạm (pickle nén) trong tmp/hdv_so_sanh, mỗi người dùng chỉ giữ bản mới
nhất và tự xoá sau 24 giờ — để xem trước / lọc / xuất Excel mà không phải tải lại file.
Không lưu dữ liệu khách hàng vào DB.
"""
import gzip
import io
import json
import pickle
import time
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .hdv_so_sanh import LOAI_FILE, TRANG_THAI, FileLoi, phan_tich

TMP_DIR = settings.BASE_DIR / 'tmp' / 'hdv_so_sanh'
TMP_TTL = 24 * 3600
SESSION_KEY = 'hdv_so_sanh_file'


# ── Lưu tạm kết quả ──────────────────────────────────────────────────────────

def _don_file_cu(user_id):
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    now = time.time()
    for p in TMP_DIR.glob('*.pkl.gz'):
        if now - p.stat().st_mtime > TMP_TTL or p.name.startswith(f'{user_id}_'):
            p.unlink(missing_ok=True)


def _luu(request, kq):
    _don_file_cu(request.user.pk)
    ten = f'{request.user.pk}_{uuid.uuid4().hex}.pkl.gz'
    with gzip.open(TMP_DIR / ten, 'wb') as f:
        pickle.dump(kq, f, protocol=pickle.HIGHEST_PROTOCOL)
    request.session[SESSION_KEY] = ten


def _doc(request):
    ten = request.session.get(SESSION_KEY, '')
    # Chỉ đọc file do chính hệ thống ghi cho đúng người dùng này
    if not ten.startswith(f'{request.user.pk}_') or '/' in ten or '\\' in ten:
        return None
    p = TMP_DIR / ten
    if not p.exists() or time.time() - p.stat().st_mtime > TMP_TTL:
        return None
    with gzip.open(p, 'rb') as f:
        return pickle.load(f)


# ── Bộ lọc ───────────────────────────────────────────────────────────────────

def _so_nhap(v):
    try:
        return float(str(v).replace('.', '').replace(',', '').strip() or 0)
    except ValueError:
        return 0.0


def _bo_loc(request, kq):
    g = request.GET
    ccys = list(kq['tong']['ccy'])
    ccy = g.get('ccy', 'VND' if 'VND' in ccys else (ccys[0] if ccys else ''))
    if ccy not in ccys:
        ccy = ''
    return {
        'ccy': ccy,
        'theo': g.get('theo', 'tong') if g.get('theo') in ('tong', 'kkh', 'ckh') else 'tong',
        'trang_thai': [t for t in g.getlist('trang_thai') if t in TRANG_THAI],
        'nguong_tien': _so_nhap(g.get('nguong_tien', '')),
        'nguong_pct': _so_nhap(g.get('nguong_pct', '')),
        'can_bo': g.get('can_bo', ''),
        'pgd': g.get('pgd', ''),
        'loai_kh': g.get('loai_kh', ''),
        'q': g.get('q', '').strip(),
        'chi_dk': g.get('chi_dk') == '1',
    }


COT_CL = {'tong': 'chenh_lech', 'kkh': 'cl_kkh', 'ckh': 'cl_ckh'}


def _loc_kh(kh, bl):
    if bl['ccy']:
        kh = kh[kh['ccy'] == bl['ccy']]
    if bl['trang_thai']:
        kh = kh[kh['trang_thai'].isin(bl['trang_thai'])]
    cl = kh[COT_CL[bl['theo']]]
    if bl['nguong_tien']:
        kh = kh[cl.abs() >= bl['nguong_tien']]
    if bl['nguong_pct']:
        # Tỷ lệ theo tổng số dư; KH mới (không có số dư kỳ trước) luôn đạt ngưỡng %
        kh = kh[kh['ty_le'].isna() | (kh['ty_le'].abs() * 100 >= bl['nguong_pct'])]
    if bl['can_bo']:
        kh = kh[(kh['can_bo_truoc'] == bl['can_bo']) | (kh['can_bo_sau'] == bl['can_bo'])]
    if bl['pgd']:
        kh = kh[(kh['pgd_truoc'] == bl['pgd']) | (kh['pgd_sau'] == bl['pgd'])]
    if bl['loai_kh']:
        kh = kh[kh['loai_kh'] == bl['loai_kh']]
    if bl['chi_dk']:
        kh = kh[kh['dk_so_tien'] > 0]
    if bl['q']:
        q = bl['q'].lower()
        kh = kh[kh['ma_kh'].str.contains(q, regex=False) | kh['ten_kh'].str.lower().str.contains(q, regex=False)]
    if bl['theo'] != 'tong':
        kh = kh[cl.reindex(kh.index) != 0]
        kh = kh.assign(_a=kh[COT_CL[bl['theo']]].abs()).sort_values('_a', ascending=False).drop(columns='_a')
    return kh


def _cham_soc(kh, bl):
    """KH tất toán / giảm số dư (theo bộ lọc, mặc định giảm mạnh nhất trước)."""
    d = _loc_kh(kh, {**bl, 'trang_thai': ['Tất toán', 'Giảm']})
    return d.sort_values(COT_CL[bl['theo']])


def _chuyen(kh, bl):
    d = _loc_kh(kh, {**bl, 'trang_thai': []})
    return d[d['doi_can_bo'] | d['doi_pgd']]


def _ban_ghi(df):
    """DataFrame → list dict (NaN → None) cho template; 'tt' = [(trạng thái, số KH, chênh lệch)]."""
    rows = json.loads(df.to_json(orient='records', force_ascii=False))
    for r in rows:
        if r.get('ty_le') is not None:
            r['ty_le_pct'] = round(r['ty_le'] * 100, 1)
        if f'kh_{TRANG_THAI[0]}' in r:
            r['tt'] = [(t, r.get(f'kh_{t}'), r.get(f'cl_{t}')) for t in TRANG_THAI]
    return rows


# ── Views ────────────────────────────────────────────────────────────────────

@login_required
def hdv_so_sanh_file_view(request):
    """GET: chọn kiểu so sánh / form tải file. POST: phân tích, lưu tạm, chuyển sang trang kết quả."""
    loai = request.POST.get('loai') or request.GET.get('loai')
    if loai not in LOAI_FILE:
        loai = None

    if request.method == 'POST' and loai:
        files = request.FILES.getlist('files')
        if len(files) < 2:
            messages.error(request, 'Vui lòng chọn từ 2 file trở lên (2 kỳ cần so sánh).')
            return redirect(f'{request.path}?loai={loai}')
        try:
            kq = phan_tich(files, loai)
        except FileLoi as e:
            messages.error(request, str(e))
            return redirect(f'{request.path}?loai={loai}')
        except Exception as e:
            messages.error(request, f'Không đọc được file: {e}')
            return redirect(f'{request.path}?loai={loai}')
        _luu(request, kq)
        return redirect('hdv_so_sanh_ket_qua')

    return render(request, 'templates_app/hdv/so_sanh_file.html', {
        'loai': loai,
        'cfg': LOAI_FILE.get(loai),
        'loai_file': LOAI_FILE,
        'co_ket_qua': _doc(request) is not None,
    })


TABS = [
    ('tong', 'Tổng hợp'), ('can_bo', 'Cán bộ huy động'), ('pgd', 'PGD'), ('loai_kh', 'Loại KH'),
    ('chi_tiet', 'Chi tiết KH'), ('cham_soc', 'Cần chăm sóc'), ('chuyen', 'Chuyển CB/PGD'), ('xu_huong', 'Xu hướng'),
]


@login_required
def hdv_so_sanh_ket_qua_view(request):
    kq = _doc(request)
    if kq is None:
        messages.warning(request, 'Kết quả so sánh đã hết hạn (lưu tạm 24 giờ) — vui lòng tải file lại.')
        return redirect('hdv_so_sanh_file')

    bl = _bo_loc(request, kq)
    kh = kq['kh']
    tabs = [(k, n) for k, n in TABS
            if not (k in ('can_bo', 'pgd', 'loai_kh') and kq[k] is None)
            and not (k == 'xu_huong' and kq['xu_huong'] is None)]
    tab = request.GET.get('tab', 'tong')
    if tab not in dict(tabs):
        tab = 'tong'

    def theo_ccy(df):
        return df[df['ccy'] == bl['ccy']] if bl['ccy'] else df

    ctx = {
        'kq': kq, 'bl': bl, 'tab': tab, 'tabs': tabs,
        'trang_thai_list': TRANG_THAI,
        'ccys': list(kq['tong']['ccy']),
        'co_nhom': 'nhom' in kq['co'],
        'co_sdt': 'sdt' in kq['co'],
        'ds_can_bo': sorted(set(kh['can_bo_truoc']) | set(kh['can_bo_sau']) - {''}),
        'ds_pgd': sorted(set(kh['pgd_truoc']) | set(kh['pgd_sau']) - {''}),
        'ds_loai_kh': sorted(set(kh['loai_kh']) - {''}),
        'tong': _ban_ghi(kq['tong']),
    }
    query = request.GET.copy()
    query.pop('tab', None)
    query.pop('page', None)
    ctx['query'] = query.urlencode()

    if tab == 'tong':
        if kq['can_bo'] is not None:
            cb = theo_ccy(kq['can_bo'])
            ctx['top_tang'] = _ban_ghi(cb[cb['chenh_lech'] > 0].nlargest(5, 'chenh_lech'))
            ctx['top_giam'] = _ban_ghi(cb[cb['chenh_lech'] < 0].nsmallest(5, 'chenh_lech'))
        if kq['co_dk']:
            tang = theo_ccy(kh)[lambda d: d['trang_thai'].isin(['Mới', 'Tăng'])]
            co = tang[tang['dk_so_tien'] > 0]
            ctx['dk'] = {
                'kh_co': len(co), 'cl_co': co['chenh_lech'].sum(),
                'kh_khong': len(tang) - len(co), 'cl_khong': tang['chenh_lech'].sum() - co['chenh_lech'].sum(),
            }
    elif tab in ('can_bo', 'pgd'):
        df = theo_ccy(kq[tab])
        rows = _ban_ghi(df)
        max_abs = max((abs(r['chenh_lech']) for r in rows), default=0) or 1
        for r in rows:
            r['bar'] = round(abs(r['chenh_lech']) / max_abs * 100)
        ctx['nhom_rows'] = rows
        ctx['nhom_tong'] = df[['so_du_truoc', 'so_du_sau', 'chenh_lech', 'cl_kkh', 'cl_ckh']].sum().to_dict()
    elif tab == 'loai_kh':
        ctx['loai_rows'] = _ban_ghi(theo_ccy(kq['loai_kh']))
    elif tab in ('chi_tiet', 'cham_soc', 'chuyen'):
        df = {'chi_tiet': _loc_kh, 'cham_soc': _cham_soc, 'chuyen': _chuyen}[tab](kh, bl)
        ctx['so_dong'] = len(df)
        ctx['tong_cl'] = df[COT_CL[bl['theo']]].sum()
        page = Paginator(range(len(df)), 100).get_page(request.GET.get('page'))
        ctx['page'] = page
        ctx['rows'] = _ban_ghi(df.iloc[page.start_index() - 1:page.end_index()]) if len(df) else []
    elif tab == 'xu_huong':
        tong_ky, cb_ky, _ = kq['xu_huong']
        nhan = [k['nhan'] for k in kq['ky']]
        t = theo_ccy(tong_ky)
        ctx['xh_tong'] = _ban_ghi(t)
        ctx['xh_chart'] = json.dumps({
            'labels': nhan,
            'tong': [float(t.loc[t['ky'] == n, 'so_du'].sum()) for n in nhan],
            'kkh': [float(t.loc[t['ky'] == n, 'kkh'].sum()) for n in nhan],
            'ckh': [float(t.loc[t['ky'] == n, 'ckh'].sum()) for n in nhan],
        })
        cb = theo_ccy(cb_ky)
        ctx['xh_nhan'] = nhan
        ctx['xh_cb'] = [{'ten': r['can_bo'], 'ccy': r['ccy'], 'gia_tri': [r[n] for n in nhan],
                         'chenh_lech': r['chenh_lech']} for r in cb.to_dict('records')]
    return render(request, 'templates_app/hdv/so_sanh_ket_qua.html', ctx)


# ── Xuất Excel ───────────────────────────────────────────────────────────────

@login_required
def hdv_so_sanh_excel_view(request):
    kq = _doc(request)
    if kq is None:
        messages.warning(request, 'Kết quả so sánh đã hết hạn — vui lòng tải file lại.')
        return redirect('hdv_so_sanh_file')
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    bl = _bo_loc(request, kq)
    a, b = kq['nhan_truoc'], kq['nhan_sau']
    co_nhom = 'nhom' in kq['co']
    wb = Workbook()
    wb.remove(wb.active)
    head_font = Font(bold=True, color='FFFFFF')
    head_fill = PatternFill('solid', fgColor='9C1C2B')
    thin = Side(style='thin', color='BBBBBB')
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    def sheet(title, cols, rows, note=None):
        """cols: [(tiêu đề, khoá, kiểu 'so'|'pct'|'' , độ rộng)]"""
        ws = wb.create_sheet(title=title[:31])
        r0 = 1
        if note:
            ws.cell(row=1, column=1, value=note).font = Font(italic=True)
            r0 = 3
        for i, (h, _, _, w) in enumerate(cols, 1):
            c = ws.cell(row=r0, column=i, value=h)
            c.font, c.fill, c.border = head_font, head_fill, border
            c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.row_dimensions[r0].height = 32
        for r_idx, row in enumerate(rows, r0 + 1):
            for c_idx, (_, key, kieu, _) in enumerate(cols, 1):
                v = row.get(key)
                if isinstance(v, float) and v != v:  # NaN
                    v = None
                c = ws.cell(row=r_idx, column=c_idx, value=v)
                c.border = border
                if kieu == 'so':
                    c.number_format = '#,##0.##'
                elif kieu == 'pct':
                    c.number_format = '0.00%'
        ws.freeze_panes = ws.cell(row=r0 + 1, column=3)
        ws.auto_filter.ref = f'A{r0}:{get_column_letter(len(cols))}{r0 + len(rows)}'
        return ws

    def cot_kkh_ckh():
        return [('Chênh lệch KKH', 'cl_kkh', 'so', 16), ('Chênh lệch CKH', 'cl_ckh', 'so', 16)] if co_nhom else []

    # Tổng hợp
    cols = [('Loại tiền', 'ccy', '', 10), (f'Số dư {a}', 'so_du_truoc', 'so', 18), (f'Số dư {b}', 'so_du_sau', 'so', 18),
            ('Chênh lệch', 'chenh_lech', 'so', 18), ('Tỷ lệ', 'ty_le', 'pct', 9)]
    if co_nhom:
        cols += [(f'KKH {a}', 'kkh_truoc', 'so', 17), (f'KKH {b}', 'kkh_sau', 'so', 17), ('Chênh lệch KKH', 'cl_kkh', 'so', 17),
                 (f'CKH {a}', 'ckh_truoc', 'so', 17), (f'CKH {b}', 'ckh_sau', 'so', 17), ('Chênh lệch CKH', 'cl_ckh', 'so', 17)]
    cols += [('Số KH kỳ trước', 'so_kh_truoc', '', 10), ('Số KH kỳ sau', 'so_kh_sau', '', 10)]
    cols += [(f'KH {t}', f'kh_{t}', '', 9) for t in TRANG_THAI] + [(f'Chênh lệch KH {t}', f'cl_{t}', 'so', 16) for t in TRANG_THAI]
    sheet('Tong hop', cols, kq['tong'].to_dict('records'),
          note=f"So sánh HĐV theo file {kq['nhan_file']}: {a} → {b} (các kỳ: {', '.join(k['nhan'] for k in kq['ky'])}). "
               "Ghép theo Mã KH + Loại tiền; ngoại tệ tách riêng, không quy đổi.")

    nhom_cols = lambda ten: [  # noqa: E731
        (ten, 'ten', '', 30), ('Loại tiền', 'ccy', '', 9), (f'Số dư {a}', 'so_du_truoc', 'so', 18),
        (f'Số dư {b}', 'so_du_sau', 'so', 18), ('Chênh lệch', 'chenh_lech', 'so', 18), ('Tỷ lệ', 'ty_le', 'pct', 9),
    ] + cot_kkh_ckh() + [('Số KH kỳ trước', 'so_kh_truoc', '', 10), ('Số KH kỳ sau', 'so_kh_sau', '', 10)] + \
        [(f'KH {t}', f'kh_{t}', '', 9) for t in TRANG_THAI]
    if kq['can_bo'] is not None:
        sheet('Can bo huy dong', nhom_cols('Cán bộ huy động'), kq['can_bo'].to_dict('records'))
    if kq['pgd'] is not None:
        sheet('PGD', nhom_cols('PGD'), kq['pgd'].to_dict('records'))
    if kq['loai_kh'] is not None:
        sheet('Loai KH', [('Loại tiền', 'ccy', '', 9), ('Loại KH', 'loai_kh', '', 25), (f'Số dư {a}', 'so_du_truoc', 'so', 18),
                          (f'Số dư {b}', 'so_du_sau', 'so', 18), ('Chênh lệch', 'chenh_lech', 'so', 18), ('Tỷ lệ', 'ty_le', 'pct', 9)]
              + cot_kkh_ckh() + [('Số KH kỳ trước', 'so_kh_truoc', '', 10), ('Số KH kỳ sau', 'so_kh_sau', '', 10),
                                 ('KH Mới', 'kh_Mới', '', 9), ('KH Tất toán', 'kh_Tất toán', '', 9)],
              kq['loai_kh'].to_dict('records'))

    kh_cols = [('Mã KH', 'ma_kh', '', 14), ('Tên KH', 'ten_kh', '', 30), ('Loại tiền', 'ccy', '', 8),
               (f'Số dư {a}', 'so_du_truoc', 'so', 17), (f'Số dư {b}', 'so_du_sau', 'so', 17),
               ('Chênh lệch', 'chenh_lech', 'so', 17), ('Tỷ lệ', 'ty_le', 'pct', 9)] + cot_kkh_ckh() + \
              [('Trạng thái', 'trang_thai', '', 10), ('Loại KH', 'loai_kh', '', 14),
               ('Cán bộ kỳ trước', 'can_bo_truoc', '', 22), ('Cán bộ kỳ sau', 'can_bo_sau', '', 22),
               ('PGD kỳ trước', 'pgd_truoc', '', 18), ('PGD kỳ sau', 'pgd_sau', '', 18),
               ('Số TK kỳ trước', 'so_tk_truoc', '', 28), ('Số TK kỳ sau', 'so_tk_sau', '', 28)]
    if kq['co_dk']:
        kh_cols += [('Số tiền ĐK HĐV', 'dk_so_tien', 'so', 16), ('Cán bộ ĐK HĐV', 'dk_can_bo', '', 22)]
    loc_note = _mo_ta_loc(bl)
    sheet('Chi tiet KH', kh_cols, _loc_kh(kq['kh'], bl).to_dict('records'), note=loc_note)
    cs_cols = kh_cols[:7] + cot_kkh_ckh() + [('Trạng thái', 'trang_thai', '', 10),
                                              ('Cán bộ', 'can_bo', '', 22), ('PGD', 'pgd', '', 18)]
    if 'sdt' in kq['co']:
        cs_cols.append(('Số điện thoại', 'sdt', '', 14))
    sheet('Can cham soc', cs_cols, _cham_soc(kq['kh'], bl).to_dict('records'), note=loc_note)
    sheet('Chuyen CB-PGD', kh_cols[:7] + [('Cán bộ kỳ trước', 'can_bo_truoc', '', 22), ('Cán bộ kỳ sau', 'can_bo_sau', '', 22),
                                           ('PGD kỳ trước', 'pgd_truoc', '', 18), ('PGD kỳ sau', 'pgd_sau', '', 18)],
          _chuyen(kq['kh'], bl).to_dict('records'), note=loc_note)

    if kq['xu_huong'] is not None:
        tong_ky, cb_ky, kh_ky = kq['xu_huong']
        nhan = [k['nhan'] for k in kq['ky']]
        sheet('Xu huong tong', [('Kỳ', 'ky', '', 12), ('Loại tiền', 'ccy', '', 9), ('Tổng số dư', 'so_du', 'so', 18)]
              + ([('KKH', 'kkh', 'so', 18), ('CKH', 'ckh', 'so', 18)] if co_nhom else []) + [('Số KH', 'so_kh', '', 10)],
              tong_ky.to_dict('records'))
        ky_cols = [(n, n, 'so', 16) for n in nhan] + [(f'Chênh lệch {nhan[0]} → {nhan[-1]}', 'chenh_lech', 'so', 18)]
        sheet('Xu huong can bo', [('Cán bộ huy động', 'can_bo', '', 28), ('Loại tiền', 'ccy', '', 9)] + ky_cols,
              cb_ky.to_dict('records'))
        sheet('Xu huong KH', [('Mã KH', 'ma_kh', '', 14), ('Tên KH', 'ten_kh', '', 30), ('Loại tiền', 'ccy', '', 9)] + ky_cols,
              kh_ky.to_dict('records'))

    out = io.BytesIO()
    wb.save(out)
    ten = f"SoSanh_HDV_{kq['nhan_file']}_{a.replace('/', '')}_{b.replace('/', '')}.xlsx"
    response = HttpResponse(out.getvalue(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{ten}"'
    return response


def _mo_ta_loc(bl):
    p = [f"Loại tiền: {bl['ccy'] or 'tất cả'}",
         f"Tính theo: {dict(tong='tổng số dư', kkh='không kỳ hạn', ckh='có kỳ hạn')[bl['theo']]}"]
    if bl['trang_thai']:
        p.append('Trạng thái: ' + ', '.join(bl['trang_thai']))
    if bl['nguong_tien']:
        p.append(f"Chênh lệch ≥ {bl['nguong_tien']:,.0f}")
    if bl['nguong_pct']:
        p.append(f"Tỷ lệ ≥ {bl['nguong_pct']:g}%")
    for k, n in (('can_bo', 'Cán bộ'), ('pgd', 'PGD'), ('loai_kh', 'Loại KH'), ('q', 'Tìm')):
        if bl[k]:
            p.append(f'{n}: {bl[k]}')
    if bl['chi_dk']:
        p.append('Chỉ KH có đăng ký HĐV')
    return 'Bộ lọc — ' + '; '.join(p)

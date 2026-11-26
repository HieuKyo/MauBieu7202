"""
Kế toán Ngân quỹ → Đối chiếu Hóa đơn điện tử: tải file Einvoice + IPCAS (đặt tên theo ngày DDMM),
xem kết quả đối chiếu theo user, giao dịch chưa có hoá đơn, lỗi hoá đơn; tải file kết quả và file import HĐĐT.

Kết quả lưu tạm (pickle nén) trong tmp/hddt — mỗi người dùng chỉ giữ bản mới nhất, tự xoá sau 24 giờ.
Không lưu dữ liệu khách hàng vào DB.
"""
import gzip
import io
import json
import pickle
import time
import uuid
import zipfile
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from . import hddt_doi_chieu as hd
from . import hddt_glcb06 as g
from .models import remove_vietnamese_diacritics

TMP_DIR = settings.BASE_DIR / 'tmp' / 'hddt'
TMP_TTL = 24 * 3600
SESSION_KEY = 'hddt_ket_qua'


def _duoc_dung(user):
    """Phòng Kế toán & Ngân quỹ, Hậu kiểm và Superuser (file có tên khách hàng)."""
    p = getattr(user, 'profile', None)
    return user.is_superuser or getattr(p, 'department', '') == 'KE_TOAN' or getattr(p, 'job_function', '') == 'HAU_KIEM_VIEN'


def _chan(request):
    messages.error(request, 'Chức năng Đối chiếu HĐĐT dành cho phòng Kế toán & Ngân quỹ / Hậu kiểm.')
    return redirect('dashboard')


def _luu(request, data):
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    now = time.time()
    for p in TMP_DIR.glob('*.pkl.gz'):
        if now - p.stat().st_mtime > TMP_TTL or p.name.startswith(f'{request.user.pk}_'):
            p.unlink(missing_ok=True)
    ten = f'{request.user.pk}_{uuid.uuid4().hex}.pkl.gz'
    with gzip.open(TMP_DIR / ten, 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    request.session[SESSION_KEY] = ten


def _doc(request):
    ten = request.session.get(SESSION_KEY, '')
    if not ten.startswith(f'{request.user.pk}_') or '/' in ten or '\\' in ten:
        return None
    p = TMP_DIR / ten
    if not p.exists() or time.time() - p.stat().st_mtime > TMP_TTL:
        return None
    with gzip.open(p, 'rb') as f:
        return pickle.load(f)


@login_required
def hddt_upload(request):
    if not _duoc_dung(request.user):
        return _chan(request)
    if request.method == 'POST' and request.POST.get('nguon') == 'glcb06':
        return _upload_glcb06(request)
    if request.method == 'POST':
        ei_files = {hd.ma_ngay(f.name): f for f in request.FILES.getlist('einvoice')}
        ip_files = {hd.ma_ngay(f.name): f for f in request.FILES.getlist('ipcas')}
        ei_files.pop(None, None)
        ip_files.pop(None, None)
        cap = sorted(set(ei_files) & set(ip_files), key=lambda m: (m[2:], m[:2]))
        if not cap:
            messages.error(request, 'Không ghép được cặp file nào. Tên file Einvoice và IPCAS phải bắt đầu bằng ngày tháng DDMM '
                                    '(vd 0511.xlsx và 0511.XLS).')
            return redirect('hddt_upload')
        thieu = sorted(set(ei_files) ^ set(ip_files))
        ket_qua = {}
        try:
            for ma in cap:
                kq = hd.doi_chieu(hd.doc_einvoice(ei_files[ma]), hd.doc_ipcas(ip_files[ma]))
                kq['bo_user'] = sorted(hd.user_bo_mac_dinh(kq))
                ket_qua[ma] = kq
        except hd.FileLoi as e:
            messages.error(request, str(e))
            return redirect('hddt_upload')
        if thieu:
            messages.warning(request, f'Bỏ qua các ngày thiếu 1 trong 2 file: {", ".join(thieu)}.')
        _luu(request, {'ngay': cap, 'ket_qua': ket_qua})
        return redirect('hddt_ket_qua')
    return render(request, 'templates_app/hddt/upload.html', {'co_ket_qua': _doc(request) is not None})


def _upload_glcb06(request):
    """Cách 2: 1 ngày — 1 file Einvoice + GLCB41 (cân đối, bắt buộc) + 1..n file GLCB06 (Transaction List in Account,
    mỗi lần search 1 tài khoản / loại tiền ra 1 file) + GLST30 tuỳ chọn (đơn giá)."""
    import pandas as pd
    ei_f, cb_fs = request.FILES.get('einvoice_cb'), request.FILES.getlist('glcb06')
    if not ei_f or not cb_fs or not request.FILES.get('glcb41'):
        messages.error(request, 'Cách 2 cần đủ: file Einvoice, file GLCB41 (bảng cân đối) và ít nhất 1 file GLCB06.')
        return redirect('hddt_upload')
    try:
        ei = hd.doc_einvoice(ei_f)
        cb = pd.concat([g.doc_glcb06(f) for f in cb_fs], ignore_index=True)
        st = request.FILES.get('glst30_dg')
        st = hd.doc_ipcas(st) if st else None
        c41 = g.doc_glcb41(request.FILES['glcb41'])
    except hd.FileLoi as e:
        messages.error(request, str(e))
        return redirect('hddt_upload')
    kq = g.doi_chieu_glcb06(ei, cb, st, c41)
    kq['loi_hd'] = ei[ei[[c for c, _, _ in hd.LOI_HD]].any(axis=1)].copy()
    kq['ngay'] = next((d for d in map(hd._ngay, ei['ngay_hd']) if d), None)
    kq['co_glst30'], kq['co_glcb41'] = st is not None, c41 is not None
    ma = f"{kq['ngay']:%d%m}" if kq['ngay'] else (hd.ma_ngay(ei_f.name) or 'ngay')
    _luu(request, {'nguon': 'glcb06', 'ngay': [ma], 'ket_qua': {ma: kq}})
    return redirect('hddt_ket_qua')


def _ket_qua_glcb06(request, data):
    ma = data['ngay'][0]
    kq = data['ket_qua'][ma]
    tab = request.GET.get('tab', 'tong_hop')
    cb, ei, th = kq['glcb06'], kq['einvoice'], kq['tong_hop']
    can = cb[cb['trang_thai'] != 'khop']
    khong_ipcas = ei[ei['khong_co_ipcas'] & (ei['tinh_trang'].str.upper() == 'GOC')]
    ctx = {'ma': ma, 'kq': kq, 'tab': tab, 'tong': _ban_ghi(th),
           'co_nt': bool((th['ein_nt'] != 0).any() or (th['ipcas_nt'] != 0).any()),
           'tong_cong': th[['ein_vnd', 'ipcas_vnd', 'cl_vnd', 'so_mon']].sum().to_dict(),
           'so_but_toan': len(can), 'so_tien_vay': int((can['trang_thai'] == 'tien_vay').sum()),
           'so_khong_ipcas': len(khong_ipcas), 'so_loi': len(kq['loi_hd']), 'trang_thai_bt': g.TRANG_THAI_BT}
    if tab == 'but_toan':
        rows = _ban_ghi(can.drop(columns=['don_gia_vnd']).assign(don_gia=can['don_gia_vnd'].astype(object)))
        ctx['rows'] = rows
    elif tab == 'khong_ipcas':
        ctx['rows'] = _ban_ghi(khong_ipcas)
    elif tab == 'loi_hd':
        rows = _ban_ghi(kq['loi_hd'])
        goi_y = _goi_y_kh360(kq['loi_hd'])
        for r in rows:
            r['loi_list'] = [(nhan, mau) for c, nhan, mau in hd.LOI_HD if r.get(c)]
            r['goi_y'] = goi_y.get(r['stt'])
        ctx['rows'] = rows
    elif tab == 'can_doi' and kq.get('can_doi') is not None:
        ctx['rows'] = _ban_ghi(kq['can_doi'])
    elif tab == 'import':
        ctx.update(_ctx_import_glcb06(request.GET, kq))
    return render(request, 'templates_app/hddt/ket_qua_glcb06.html', ctx)


def _form_glcb06(post, kq):
    gio = ''.join(ch for ch in post.get('gio', '') if ch.isdigit())[:6] or datetime.now().strftime('%H%M%S')
    che_do = post.get('che_do') if post.get('che_do') in dict(g.CHE_DO_IMPORT) else 'gom'
    cb = kq['glcb06']
    ngoai_te = sorted(set(cb.loc[(cb['trang_thai'] != 'khop') & (cb['ccy'] != 'VND'), 'ccy']))
    ty_gia = {}
    for c in ngoai_te:
        try:
            v = float(post.get(f'ty_gia_{c}', '').replace('.', '').replace(',', '.') or 0)
        except ValueError:
            v = 0
        if v:
            ty_gia[c] = v
    return gio, che_do, ngoai_te, ty_gia


def _ctx_import_glcb06(post, kq):
    gio, che_do, ngoai_te, ty_gia = _form_glcb06(post, kq)
    dong, canh_bao = g.lap_dong_import_glcb06(kq, kq['ngay'] or datetime.now().date(), int(gio), ty_gia, che_do, tra_kh360)
    return {'gio': gio, 'che_do': che_do, 'che_do_list': g.CHE_DO_IMPORT, 'canh_bao': canh_bao,
            'ngoai_te': [(c, ty_gia.get(c, '')) for c in ngoai_te], 'xem_chinh': [_xem(d) for d in dong]}


def tra_kh360(cif):
    """Thông tin lập hoá đơn từ Khách hàng 360 theo CIF (mã KH) → dict hoặc None."""
    from kh360.models import KhachHang, TaiKhoanTG
    cif = ''.join(ch for ch in str(cif) if ch.isdigit())
    if not cif:
        return None
    kh = KhachHang.objects.filter(ma_kh=cif).first() or KhachHang.objects.filter(ma_kh=cif.zfill(9)).first()
    if not kh:
        return None
    tk = (TaiKhoanTG.objects.filter(ma_kh=kh.ma_kh, ky_han=0, con_hoat_dong=True).order_by('-so_du')
          .values_list('so_tk', flat=True).first())
    return {'cif': kh.ma_kh, 'ten_kh': kh.ten, 'dia_chi': kh.dia_chi, 'loai_kh': 'C' if kh.la_to_chuc else 'I',
            'mst': kh.cccd if kh.la_to_chuc else '', 'giay_to': kh.cccd, 'so_tk': tk or ''}


def _goi_y_kh360(loi):
    """Gợi ý cho HĐ 'DN chưa có MST': khớp KH 360 theo Số cif (nếu file có) hoặc tên tổ chức."""
    from kh360.models import KhachHang
    from kh360.parsers import chuan_ten
    can = loi[loi['loi_mst']]
    if can.empty:
        return {}
    theo_ten = {chuan_ten(t): m for m, t in KhachHang.objects.filter(la_to_chuc=True).values_list('ma_kh', 'ten')}
    goi_y = {}
    for r in can.itertuples():
        cif = r.so_cif or theo_ten.get(chuan_ten(r.ten_nguoi_mua))
        kh = tra_kh360(cif) if cif else None
        if kh:
            goi_y[r.stt] = kh
    return goi_y


@login_required
def hddt_tra_kh(request):
    """JSON thông tin khách hàng (Khách hàng 360) cho ô Hoá đơn riêng."""
    if not _duoc_dung(request.user):
        return JsonResponse({'ok': False, 'loi': 'Không có quyền'}, status=403)
    kh = tra_kh360(request.GET.get('cif', ''))
    if not kh:
        return JsonResponse({'ok': False, 'loi': 'Không tìm thấy CIF trong Khách hàng 360'})
    return JsonResponse({'ok': True, **kh})


def _ban_ghi(df):
    return json.loads(df.to_json(orient='records', force_ascii=False))


@login_required
def hddt_ket_qua(request):
    if not _duoc_dung(request.user):
        return _chan(request)
    data = _doc(request)
    if data is None:
        messages.warning(request, 'Kết quả đối chiếu đã hết hạn (lưu tạm 24 giờ) — vui lòng tải file lại.')
        return redirect('hddt_upload')
    if data.get('nguon') == 'glcb06':
        return _ket_qua_glcb06(request, data)
    ma = request.GET.get('ngay') or data['ngay'][0]
    if ma not in data['ket_qua']:
        ma = data['ngay'][0]
    kq = data['ket_qua'][ma]
    tab = request.GET.get('tab', 'tong_hop')
    th = kq['tong_hop']
    ip = kq['ipcas']

    ngay_list = []
    for m in data['ngay']:
        k = data['ket_qua'][m]
        ngay_list.append({'ma': m, 'ngay': k['ngay'], 'lech': int((k['tong_hop']['chenh_lech'] != 0).sum()),
                          'loi': len(k['loi_hd'])})

    ctx = {'ma': ma, 'kq': kq, 'tab': tab, 'ngay_list': ngay_list,
           'tong': _ban_ghi(th),
           'tong_cong': th[['einvoice', 'ipcas', 'chenh_lech', 'so_mon_lech']].sum().to_dict(),
           'so_thieu_hd': int((ip['q'] == 2).sum()), 'so_loi': len(kq['loi_hd']),
           'nhom_ten': {k: v[0] for k, v in hd.NHOM_IMPORT.items()}}
    if tab == 'thieu_hd':
        ctx['rows'] = _ban_ghi(ip[ip['q'] == 2])
    elif tab == 'loi_hd':
        rows = _ban_ghi(kq['loi_hd'])
        goi_y = _goi_y_kh360(kq['loi_hd'])
        for r in rows:
            r['loi_list'] = [(nhan, mau) for c, nhan, mau in hd.LOI_HD if r.get(c)]
            r['goi_y'] = goi_y.get(r['stt'])
        ctx['rows'] = rows
        ctx['dem_loi'] = [(nhan, mau, int(kq['loi_hd'][c].sum())) for c, nhan, mau in hd.LOI_HD
                          if c in kq['loi_hd'] and kq['loi_hd'][c].any()]
    elif tab == 'import':
        ctx.update(_ctx_import(request, kq))
    return render(request, 'templates_app/hddt/ket_qua.html', ctx)


def _doc_form_import(post, kq):
    try:
        ty_gia = float(post.get('ty_gia', '').replace('.', '').replace(',', '.') or 0) or None
    except ValueError:
        ty_gia = None
    gio = ''.join(ch for ch in post.get('gio', '') if ch.isdigit())[:6] or datetime.now().strftime('%H%M%S')
    users = set(kq['tong_hop']['user'])
    bo_user = set(kq['bo_user']) if 'da_chon_user' not in post else (users - set(post.getlist('gom_user')))
    rieng = []
    for i, loai in enumerate(post.getlist('r_loai')):
        def g(k):
            vals = post.getlist(k)
            return vals[i].strip() if i < len(vals) else ''
        try:
            so_tien = float(g('r_so_tien').replace('.', '').replace(',', '.') or 0)
        except ValueError:
            so_tien = 0
        if loai not in hd.HANG_RIENG or not so_tien:
            continue
        rieng.append({'loai': loai, 'so_tien': so_tien, 'noi_dung': g('r_noi_dung'), 'cif': g('r_cif'),
                      'ten_kh': g('r_ten_kh'), 'mst': g('r_mst'), 'dia_chi': g('r_dia_chi'), 'so_tk': g('r_so_tk'),
                      'loai_kh': g('r_loai_kh') or 'C', 'file_rieng': g('r_file_rieng') == '1'})
    return gio, ty_gia, bo_user, rieng


def _xem(d):
    """1 dòng import (list 35 cột) → dict khoá ngắn cho trang xem trước."""
    return {'group': d[0], 'tien_te': d[4], 'ty_gia': d[5], 'cif': d[6], 'ten_kh': d[7], 'mst': d[8], 'loai_kh': d[16],
            'ma_ttv': d[17], 'u': d[20], 'v': d[21], 'w': d[22], 'noi_dung': d[23], 'ten_hang': d[24], 'thue_suat': d[30]}


def _ctx_import(request, kq, post=None):
    post = post if post is not None else request.GET
    gio, ty_gia, bo_user, rieng = _doc_form_import(post, kq)
    chinh, files_rieng, canh_bao = hd.lap_dong_import(kq, int(gio), ty_gia, rieng, bo_user=bo_user)
    gom = hd.gom_import(kq, bo_user)
    th = kq['tong_hop']
    return {
        'gio': gio, 'ty_gia': ty_gia or '', 'canh_bao': canh_bao, 'gom': gom,
        'co_kieu_hoi': bool(gom['kieu_hoi'] or gom['kieu_hoi_amt']),
        'user_rows': [{**r, 'gom': r['user'] not in bo_user, 'am_lon': r['chenh_lech'] <= hd.NGUONG_AM_LON}
                      for r in _ban_ghi(th[th['chenh_lech'] != 0])],
        'xem_chinh': [_xem(d) for d in chinh],
        'xem_rieng': [(ten, [_xem(d) for d in ds]) for ten, ds in files_rieng],
        'rieng': rieng, 'hang_rieng': [(k, v[0], v[2]) for k, v in hd.HANG_RIENG.items()],
    }


@login_required
def hddt_tai_import(request):
    """POST form tạo import → file LOAD DDMM.xlsx (hoặc .zip nếu có hoá đơn xuất file riêng)."""
    if not _duoc_dung(request.user):
        return _chan(request)
    data = _doc(request)
    if data is None or request.method != 'POST':
        return redirect('hddt_upload')
    ma = request.POST.get('ngay')
    kq = data['ket_qua'].get(ma)
    if kq is None:
        return redirect('hddt_ket_qua')
    if data.get('nguon') == 'glcb06':
        gio, che_do, _, ty_gia_nt = _form_glcb06(request.POST, kq)
        dong, canh_bao = g.lap_dong_import_glcb06(kq, kq['ngay'] or datetime.now().date(), int(gio), ty_gia_nt, che_do,
                                                  tra_kh360)
        if not dong:
            messages.warning(request, 'Không có dòng nào để lập file import. ' + ' '.join(canh_bao))
            return redirect(f"{reverse('hddt_ket_qua')}?tab=import")
        resp = HttpResponse(hd.xuat_import(dong),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = f'attachment; filename="LOAD {ma}.xlsx"'
        return resp
    gio, ty_gia, bo_user, rieng = _doc_form_import(request.POST, kq)
    chinh, files_rieng, canh_bao = hd.lap_dong_import(kq, int(gio), ty_gia, rieng, bo_user=bo_user)
    if not chinh and not files_rieng:
        messages.warning(request, 'Không có dòng nào để lập file import. ' + ' '.join(canh_bao))
        return redirect(f"{reverse('hddt_ket_qua')}?ngay={ma}&tab=import")
    ten_chinh = f'LOAD {ma}.xlsx'
    if not files_rieng:
        resp = HttpResponse(hd.xuat_import(chinh),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = f'attachment; filename="{ten_chinh}"'
        return resp
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        if chinh:
            zf.writestr(ten_chinh, hd.xuat_import(chinh))
        for ten, dong in files_rieng:
            ten_file = remove_vietnamese_diacritics(ten).upper().replace('/', ' ')[:40].strip()
            zf.writestr(f'LOAD {ma} {ten_file}.xlsx', hd.xuat_import(dong))
    resp = HttpResponse(buf.getvalue(), content_type='application/zip')
    resp['Content-Disposition'] = f'attachment; filename="LOAD {ma}.zip"'
    return resp


@login_required
def hddt_tai_ket_qua(request):
    """File kết quả đối chiếu (ketquaDDMMYYYY.xlsx) của 1 ngày, hoặc zip tất cả các ngày."""
    if not _duoc_dung(request.user):
        return _chan(request)
    data = _doc(request)
    if data is None:
        return redirect('hddt_upload')

    def ten(m):
        k = data['ket_qua'][m]
        return f"ketqua{k['ngay']:%d%m%Y}.xlsx" if k['ngay'] else f'ketqua{m}.xlsx'

    if data.get('nguon') == 'glcb06':
        ma = data['ngay'][0]
        resp = HttpResponse(g.xuat_ket_qua_glcb06(data['ket_qua'][ma]),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = f'attachment; filename="{ten(ma).replace("ketqua", "ketqua_glcb06_")}"'
        return resp

    ma = request.GET.get('ngay')
    if ma in data['ket_qua']:
        k = data['ket_qua'][ma]
        resp = HttpResponse(hd.xuat_ket_qua(k, f"{k['ngay']:%d%m%Y}" if k['ngay'] else ma),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = f'attachment; filename="{ten(ma)}"'
        return resp
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for m in data['ngay']:
            k = data['ket_qua'][m]
            zf.writestr(ten(m), hd.xuat_ket_qua(k, f"{k['ngay']:%d%m%Y}" if k['ngay'] else m))
    resp = HttpResponse(buf.getvalue(), content_type='application/zip')
    resp['Content-Disposition'] = 'attachment; filename="ketqua_doi_chieu_hddt.zip"'
    return resp

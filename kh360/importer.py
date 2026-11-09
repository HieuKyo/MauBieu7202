"""
Nạp một kỳ cập nhật Khách hàng 360: đọc toàn bộ file trước (lỗi → không ghi gì),
rồi ghi trong một transaction, so với trạng thái hiện tại để sinh BienDong.
"""
from collections import defaultdict
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Max, Sum

from . import parsers
from .models import (
    BienDong, EbankingToChuc, GanMaToChuc, KhachHang, KhoanVay, Ky, LoaThanTai, MaQR,
    NguonFile, TaiKhoanTG, XepHangKH,
)

BATCH = 2000


def _xoa_theo_khoa(model, khoa):
    khoa = list(khoa)
    for i in range(0, len(khoa), 900):
        model.objects.filter(pk__in=khoa[i:i + 900]).delete()


def _tien(v):
    return f'{v:,.0f}'.replace(',', '.')


class NhapKy:
    def __init__(self, files, user):
        """files: {'CN05': UploadedFile, 'DP01': ..., 'LN01'|'LOA'|'QR'|'KHTC': ... (tuỳ chọn)}"""
        self.files = {k: v for k, v in files.items() if v}
        self.user = user
        self.bien_dong = []

    # ── Đọc ──────────────────────────────────────────────────────────────────
    def doc(self):
        if 'CN05' not in self.files or 'DP01' not in self.files:
            raise parsers.FileLoi('Bắt buộc phải có file CN05 và DP01.')
        f = self.files
        self.ngay = {}
        self.ngay['CN05'], self.cn05 = parsers.doc_cn05(f['CN05'])
        self.ngay['DP01'], self.dp_tk, self.dp_kh = parsers.doc_dp01(f['DP01'])
        self.so_dong = {'CN05': len(self.cn05), 'DP01': len(self.dp_tk)}
        if 'LN01' in f:
            self.ngay['LN01'], self.ln01 = parsers.doc_ln01(f['LN01'])
            self.so_dong['LN01'] = len(self.ln01)
        if 'LOA' in f:
            self.loa_tu, self.ngay['LOA'], self.loa = parsers.doc_loa(f['LOA'])
            self.so_dong['LOA'] = len(self.loa)
        if 'QR' in f:
            self.qr = parsers.doc_qr(f['QR'])
            self.ngay['QR'] = date.today()
            self.so_dong['QR'] = len(self.qr)
        if 'KHTC' in f:
            self.ngay['KHTC'], self.khtc = parsers.doc_khtc(f['KHTC'])
            self.so_dong['KHTC'] = len(self.khtc)
        if 'BC06' in f:
            self.ngay['BC06'], self.bc06 = parsers.doc_bc06(f['BC06'])
            self.so_dong['BC06'] = len(self.bc06)
        # Không cho nạp dữ liệu cũ hơn lần trước (tránh sinh biến động ngược)
        for nguon, ngay in self.ngay.items():
            cu = NguonFile.objects.filter(nguon=nguon).aggregate(m=Max('ngay_du_lieu'))['m']
            if cu and ngay < cu:
                raise parsers.FileLoi(
                    f'File {nguon} có ngày dữ liệu {ngay:%d/%m/%Y} cũ hơn lần cập nhật trước ({cu:%d/%m/%Y}).')

    # ── Ghi ──────────────────────────────────────────────────────────────────
    def chay(self):
        self.doc()
        with transaction.atomic():
            self.ky = Ky.objects.create(ngay_du_lieu=self.ngay['CN05'], nguoi_cap_nhat=self.user)
            self.moc = {n: not NguonFile.objects.filter(nguon=n).exists() for n in self.ngay}
            self.khong_khop = defaultdict(list)
            if 'LN01' in self.files:
                self._nhap_ln01()
            self._nhap_dp01()
            self._nhap_khach_hang()
            if 'LOA' in self.files:
                self._nhap_loa()
            if 'QR' in self.files:
                self._nhap_qr()
            if 'KHTC' in self.files:
                self._nhap_khtc()
            if 'BC06' in self.files:
                XepHangKH.objects.all().delete()
                XepHangKH.objects.bulk_create([XepHangKH(ma_kh=k, **v) for k, v in self.bc06.items()],
                                              batch_size=BATCH)
            NguonFile.objects.bulk_create([
                NguonFile(ky=self.ky, nguon=n, ten_file=self.files[n].name, ngay_du_lieu=self.ngay[n],
                          so_dong=self.so_dong[n], la_moc=self.moc[n], khong_khop=self.khong_khop.get(n, []))
                for n in self.ngay
            ])
            BienDong.objects.bulk_create(self.bien_dong, batch_size=BATCH)
            self.ky.tong_hop = tong_hop()
            self.ky.save(update_fields=['tong_hop'])
        return self.ky

    def _bd(self, nguon, loai, ma_kh, ten_kh='', doi_tuong='', chi_tiet=''):
        if not self.moc[nguon]:
            self.bien_dong.append(BienDong(ky=self.ky, loai=loai, ma_kh=ma_kh, ten_kh=ten_kh[:255],
                                           doi_tuong=doi_tuong[:100], chi_tiet=chi_tiet[:255]))

    def _thay_the(self, model, moi, cot_active):
        """Ghi đè các dòng có trong file; dòng cũ không còn trong file giữ lại nhưng tắt cờ active."""
        _xoa_theo_khoa(model, moi.keys())
        model.objects.update(**{cot_active: False})
        model.objects.bulk_create([model(pk=k, **v) for k, v in moi.items()], batch_size=BATCH)

    def _nhap_dp01(self):
        cu = {k: (ma, ten, act, loai) for k, ma, ten, act, loai in
              TaiKhoanTG.objects.values_list('so_tk', 'ma_kh', 'ten_kh', 'con_hoat_dong', 'loai_tg')}
        for so_tk, tk in self.dp_tk.items():
            if so_tk not in cu and tk['con_hoat_dong']:
                self._bd('DP01', 'TK_MOI', tk['ma_kh'], tk['ten_kh'], so_tk,
                         f"{tk['loai_tg']} – số dư {_tien(tk['so_du'])} {tk['ccy']}")
        for so_tk, (ma, ten, act, loai) in cu.items():
            moi = self.dp_tk.get(so_tk)
            if act and (moi is None or not moi['con_hoat_dong']):
                self._bd('DP01', 'TK_DONG', ma, ten, so_tk,
                         loai + (' – trạng thái Close' if moi else ' – không còn trong DP01'))
        self._thay_the(TaiKhoanTG, self.dp_tk, 'con_hoat_dong')

    def _nhap_ln01(self):
        cu = {k: (ma, ten, act) for k, ma, ten, act in
              KhoanVay.objects.values_list('so_giai_ngan', 'ma_kh', 'ten_kh', 'con_du_no')}
        for so_gn, v in self.ln01.items():
            if so_gn not in cu and v['con_du_no']:
                ngay_gn = f"{v['ngay_giai_ngan']:%d/%m/%Y}" if v['ngay_giai_ngan'] else ''
                self._bd('LN01', 'VAY_MOI', v['ma_kh'], v['ten_kh'], so_gn,
                         f"Giải ngân {_tien(v['so_tien_giai_ngan'])} ngày {ngay_gn} – TK nhận {v['tk_nhan_giai_ngan']}"
                         f" – CBTD {v['can_bo']}")
        for so_gn, (ma, ten, act) in cu.items():
            moi = self.ln01.get(so_gn)
            if act and (moi is None or not moi['con_du_no']):
                self._bd('LN01', 'VAY_TAT_TOAN', ma, ten, so_gn,
                         'Dư nợ về 0' if moi else 'Không còn trong LN01')
        self._thay_the(KhoanVay, self.ln01, 'con_du_no')

    def _nhap_khach_hang(self):
        # Thông tin cá nhân: ưu tiên DP01, KH chỉ có khoản vay thì lấy từ LN01 (bảng hiện tại)
        vay, du_no = {}, defaultdict(Decimal)
        for v in KhoanVay.objects.values('ma_kh', 'ten_kh', 'loai_kh', 'cccd', 'ngay_sinh', 'dia_chi',
                                         'pgd', 'con_du_no', 'du_no'):
            if v['ma_kh'] not in vay or v['con_du_no']:
                vay[v['ma_kh']] = v
            if v['con_du_no']:
                du_no[v['ma_kh']] += v['du_no']
        so_du = defaultdict(Decimal)
        for t in self.dp_tk.values():
            if t['con_hoat_dong'] and t['ccy'] == 'VND' and t['so_du'] > 0:   # bỏ TK thấu chi (số dư âm)
                so_du[t['ma_kh']] += t['so_du']
        dang_vay = {v['ma_kh'] for v in vay.values() if v['con_du_no']}
        hoat_dong = set(self.cn05) | {tk['ma_kh'] for tk in self.dp_tk.values()} | dang_vay

        cu = {ma: (act, co_cn05, dv, ten) for ma, act, co_cn05, dv, ten in
              KhachHang.objects.values_list('ma_kh', 'con_hoat_dong', 'co_cn05', 'dich_vu', 'ten')}
        moi = {}
        for ma in hoat_dong:
            cn, dp, ln = self.cn05.get(ma), self.dp_kh.get(ma), vay.get(ma)
            info = dp or {}
            loai = info.get('loai_kh') or (ln['loai_kh'] if ln else '') or ('100' if cn else '')
            row = {
                'ten': (cn and cn['ten']) or info.get('ten') or (ln and ln['ten_kh']) or '',
                'loai_kh': loai, 'ten_loai_kh': info.get('ten_loai_kh', ''),
                'la_to_chuc': bool(loai) and loai != '100',
                'cccd': info.get('cccd') or (ln and ln['cccd']) or '',
                'ngay_cap': info.get('ngay_cap'),
                'ngay_sinh': info.get('ngay_sinh') or (ln and ln['ngay_sinh']) or None,
                'gioi_tinh': info.get('gioi_tinh', ''), 'sdt': info.get('sdt', ''),
                'dia_chi': (info.get('dia_chi') or (ln and ln['dia_chi']) or '')[:300],
                'pgd': info.get('pgd') or (ln and ln['pgd']) or '',
                'co_cn05': cn is not None, 'dich_vu': cn['dich_vu'] if cn else {},
                'tong_so_du': so_du.get(ma, 0), 'tong_du_no': du_no.get(ma, 0),
                'con_hoat_dong': True,
            }
            row['tim_kiem'] = ' '.join([ma, parsers.khong_dau(row['ten']), row['cccd'], row['sdt']])
            moi[ma] = row

            old = cu.get(ma)
            if not old or not old[0]:
                self._bd('CN05', 'KH_MOI', ma, row['ten'], ma,
                         'Tổ chức' if row['la_to_chuc'] else 'Cá nhân')
            elif cn and old[1]:
                dv_cu, dv_moi = old[2], cn['dich_vu']
                for k, nhan in parsers.NHAN_DICH_VU.items():
                    if dv_moi.get(k) and not dv_cu.get(k):
                        self._bd('CN05', 'DV_DANG_KY', ma, row['ten'], nhan)
                    elif dv_cu.get(k) and not dv_moi.get(k):
                        self._bd('CN05', 'DV_HUY', ma, row['ten'], nhan)
        for ma, (act, _, _, ten) in cu.items():
            if act and ma not in moi:
                self._bd('CN05', 'KH_MAT', ma, ten, ma, 'Không còn trong CN05, DP01 và không còn dư nợ')
        self._thay_the(KhachHang, moi, 'con_hoat_dong')

    def _ma_kh_theo_stk(self):
        return dict(TaiKhoanTG.objects.values_list('so_tk', 'ma_kh'))

    def _nhap_loa(self):
        stk_kh = self._ma_kh_theo_stk()
        ky_cu = LoaThanTai.objects.aggregate(m=Max('tu_ngay'))['m']
        cu = {t: (ma, ten, stk) for t, ma, ten, stk in
              LoaThanTai.objects.filter(tu_ngay=ky_cu).values_list('tk_ao', 'ma_kh', 'ten_kh', 'so_tk')}
        rows, thay = [], set()
        for r in self.loa:
            ma = stk_kh.get(r['so_tk'], '')
            if not ma:
                self.khong_khop['LOA'].append(f"STK {r['so_tk']} – {r['ten_kh']}")
            rows.append(LoaThanTai(ma_kh=ma, tu_ngay=self.loa_tu, den_ngay=self.ngay['LOA'], **r))
            if r['tk_ao'] not in cu and r['tk_ao'] not in thay:
                self._bd('LOA', 'LOA_MOI', ma, r['ten_kh'], r['tk_ao'], f"STK {r['so_tk']}")
            thay.add(r['tk_ao'])
        for t, (ma, ten, stk) in cu.items():
            if t not in thay:
                self._bd('LOA', 'LOA_MAT', ma, ten, t, f'STK {stk}')
        LoaThanTai.objects.filter(tu_ngay=self.loa_tu).delete()
        LoaThanTai.objects.bulk_create(rows, batch_size=BATCH)

    def _nhap_qr(self):
        stk_kh = self._ma_kh_theo_stk()
        cu = {stk: (ma, ten) for stk, ma, ten in MaQR.objects.values_list('so_tk', 'ma_kh', 'ho_ten')}
        rows, thay = [], set()
        for r in self.qr:
            ma = stk_kh.get(r['so_tk'], '')
            if not ma:
                self.khong_khop['QR'].append(f"STK {r['so_tk']} – {r['ho_ten']}")
            rows.append(MaQR(ma_kh=ma, **r))
            if r['so_tk'] not in cu and r['so_tk'] not in thay:
                self._bd('QR', 'QR_MOI', ma, r['ho_ten'], r['so_tk'], r['ten_cua_hang'])
            thay.add(r['so_tk'])
        for stk, (ma, ten) in cu.items():
            if stk not in thay:
                self._bd('QR', 'QR_MAT', ma, ten, stk)
        MaQR.objects.all().delete()
        MaQR.objects.bulk_create(rows, batch_size=BATCH)

    def _nhap_khtc(self):
        gan = dict(GanMaToChuc.objects.values_list('ma_to_chuc', 'ma_kh'))
        theo_ten = defaultdict(set)
        for ma, ten in KhachHang.objects.filter(la_to_chuc=True).values_list('ma_kh', 'ten'):
            theo_ten[parsers.chuan_ten(ten)].add(ma)
        cu = {m: (ma, ten) for m, ma, ten in EbankingToChuc.objects.values_list('ma_to_chuc', 'ma_kh', 'ten')}
        rows = []
        for r in self.khtc:
            ma = gan.get(r['ma_to_chuc'])
            if not ma:
                khop = theo_ten.get(parsers.chuan_ten(r['ten']), set())
                ma = next(iter(khop)) if len(khop) == 1 else ''
            if not ma:
                self.khong_khop['KHTC'].append(r['ma_to_chuc'])
            rows.append(EbankingToChuc(ma_kh=ma, **r))
            if r['ma_to_chuc'] not in cu:
                self._bd('KHTC', 'EB_MOI', ma, r['ten'], r['ma_to_chuc'])
        moi = {r['ma_to_chuc'] for r in self.khtc}
        for m, (ma, ten) in cu.items():
            if m not in moi:
                self._bd('KHTC', 'EB_MAT', ma, ten, m)
        EbankingToChuc.objects.all().delete()
        EbankingToChuc.objects.bulk_create(rows, batch_size=BATCH)


def tong_hop():
    kh = KhachHang.objects.filter(con_hoat_dong=True)
    tk = TaiKhoanTG.objects.filter(con_hoat_dong=True)
    vay = KhoanVay.objects.filter(con_du_no=True)
    ky_loa = LoaThanTai.objects.aggregate(m=Max('tu_ngay'))['m']
    loa = LoaThanTai.objects.filter(tu_ngay=ky_loa)
    return {
        'so_kh': kh.count(),
        'so_kh_to_chuc': kh.filter(la_to_chuc=True).count(),
        'so_tk': tk.count(),
        'tong_so_du_vnd': float(tk.filter(ccy='VND', so_du__gt=0).aggregate(t=Sum('so_du'))['t'] or 0),
        'so_so_tiet_kiem': tk.filter(ky_han__gt=0).count(),
        'so_vay': vay.count(),
        'tong_du_no': float(vay.aggregate(t=Sum('du_no'))['t'] or 0),
        'so_loa': loa.count(),
        'doanh_so_loa': float(loa.aggregate(t=Sum('doanh_so'))['t'] or 0),
        'so_qr': MaQR.objects.values('so_tk').distinct().count(),
        'so_ebanking_tc': EbankingToChuc.objects.count(),
    }

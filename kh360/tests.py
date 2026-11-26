"""Test Khách hàng 360 — toàn bộ dữ liệu là dữ liệu GIẢ tự tạo."""
import io
import zipfile
from datetime import date
from decimal import Decimal

import openpyxl
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .mau_mac_dinh import MAU_MAC_DINH, tao_mau_mac_dinh
from .importer import NhapKy
from .models import (
    BienDong, EbankingToChuc, KhachHang, KhoanVay, LoaThanTai, MaQR, MauThongKe, NguonFile, TaiKhoanTG,
    XepHangKH,
)
from .parsers import CN05_DICH_VU, FileLoi

CN05_COT = ['MA_CN', 'MA_KH', 'TEN_KH'] + [c for c, _, _ in CN05_DICH_VU]
DP01_COT = ['MA_CN', 'TAI_KHOAN_HACH_TOAN', 'MA_KH', 'TEN_KH', 'DP_TYPE_NAME', 'CCY', 'CURRENT_BALANCE',
            'RATE', 'SO_TAI_KHOAN', 'OPENING_DATE', 'MATURITY_DATE', 'ADDRESS', 'NOTENO', 'MONTH_TERM',
            'TEN_PGD', 'CUST_TYPE', 'CUST_TYPE_NAME', 'ID_NUMBER', 'ISSUE_DATE', 'SEX_TYPE', 'BIRTH_DATE',
            'TELEPHONE', 'ACCOUNT_STATUS', 'EMPLOYEE_NAME', 'TERM_DP_NAME']
LN01_COT = ['BRCD', 'CUSTSEQ', 'CUSTNM', 'TAI_KHOAN', 'DU_NO', 'DSBSSEQ', 'DSBSDT', 'DISBURSEMENT_AMOUNT',
            'DSBSMATDT', 'INTEREST_RATE', 'LOAN_TYPE', 'FUND_PURPOSE_CODE', 'NEXT_REPAY_DATE',
            'NEXT_REPAY_AMOUNT', 'OFFICER_NAME', 'NHOM_NO', 'TAI_KHOAN_GIAI_NGAN_1', 'CMT_HC', 'NGAY_SINH',
            'ADDR1', 'CUSTOMER_TYPE_CODE', 'TRCTNM']


def _csv(cot, rows):
    def q(v):
        v = str(v)
        return f'"{v}"' if ',' in v else v
    lines = [','.join(cot)] + [','.join(q(r.get(c, '')) for c in cot) for r in rows]
    return ('﻿' + '\n'.join(lines) + '\n').encode('utf-8')


def cn05(rows, ngay='20261031', zip_=False):
    data = _csv(CN05_COT, [{'MA_CN': '7202', **r} for r in rows])
    if zip_:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as z:
            z.writestr(f'7202_CN05_{ngay}.csv', data)
        return SimpleUploadedFile(f'CN05_{ngay}_7202.zip', buf.getvalue())
    return SimpleUploadedFile(f'7202_CN05_{ngay}.csv', data)


def kh_cn(ma, ten, **dv):
    return {'MA_KH': f"'{ma}", 'TEN_KH': ten, **dv}


def tk(so_tk, ma, ten, so_du=1000000, status='Normal', cust_type='100', **kw):
    return {'MA_KH': f"'{ma}", 'TEN_KH': ten, 'SO_TAI_KHOAN': f"'{so_tk}", 'TAI_KHOAN_HACH_TOAN': '421101',
            'DP_TYPE_NAME': 'Tiền gửi thanh toán', 'CCY': 'VND', 'CURRENT_BALANCE': so_du, 'RATE': '.2',
            'MONTH_TERM': "'000", 'OPENING_DATE': "'20240101", 'MATURITY_DATE': "'00000000",
            'ACCOUNT_STATUS': status, 'TEN_PGD': 'Hội sở', 'CUST_TYPE': cust_type,
            'CUST_TYPE_NAME': 'Cá nhân' if cust_type == '100' else 'Công ty TNHH',
            'ID_NUMBER': "'012345678901", 'BIRTH_DATE': "'19900115", 'TELEPHONE': "'0912345678",
            'SEX_TYPE': 'Female', 'ADDRESS': 'Ấp 1, xã A', **kw}


def dp01(rows, ngay='20261031'):
    return SimpleUploadedFile(f'7202_dp01_{ngay}.csv', _csv(DP01_COT, rows))


def vay(so_gn, ma, ten, du_no=50000000, loai='100', **kw):
    return {'BRCD': '7202', 'CUSTSEQ': f"'{ma}", 'CUSTNM': ten, 'TAI_KHOAN': '212101', 'DU_NO': du_no,
            'DSBSSEQ': so_gn, 'DSBSDT': '20261020', 'DISBURSEMENT_AMOUNT': 50000000, 'DSBSMATDT': '20271020',
            'INTEREST_RATE': '7.5', 'LOAN_TYPE': 'Cho vay ngắn hạn', 'NHOM_NO': "'01",
            'OFFICER_NAME': 'Cán bộ A', 'TAI_KHOAN_GIAI_NGAN_1': "'7202000000001", 'CMT_HC': "'098765432109",
            'NGAY_SINH': "'19800101", 'ADDR1': 'Ấp 2', 'CUSTOMER_TYPE_CODE': loai, 'TRCTNM': 'Hội sở', **kw}


def ln01(rows, ngay='20261031'):
    return SimpleUploadedFile(f'7202_ln01_{ngay}.csv', _csv(LN01_COT, rows))


BC06_COT = ['MA_CHI_NHANH', 'TEN_CHI_NHANH', 'MA_KHACH_HANG', 'TEN_KHACH_HANG', 'LOAI_KHACH_HANG', 'THANG_PHAN_LOAI',
            'LOI_ICH_TG_TAI_CN', 'LOI_ICH_TV_TAI_CN', 'LOI_ICH_DV_TAI_CN', 'SDBQ_TGCKH_CN', 'SDBQ_TGKKH_CN', 'SDBQ_TV',
            'DIEM_LOI_ICH_CN', 'DIEM_SDBQ_CN', 'DIEM_DINH_TINH_CN', 'DIEM_KH_CN', 'TIEU_CHI_BS_CN', 'NHOM_TAI_CN',
            'HANG_TAI_CN', 'NHOM_TT_CN', 'HANG_TT_CN', 'TIEU_CHI_BS_AGR', 'NHOM_AGR', 'HANG_AGR', 'NHOM_TT_AGR',
            'HANG_TT_AGR', 'DON_VI_DIEU_CHINH', 'DON_VI_DAU_MOI']


def bc(ma, nhom, hang, diem):
    return {'MA_CHI_NHANH': '7202', 'MA_KHACH_HANG': f"'{ma}", 'THANG_PHAN_LOAI': '202610',
            'LOI_ICH_TG_TAI_CN': '74000.123456', 'LOI_ICH_TV_TAI_CN': '0', 'LOI_ICH_DV_TAI_CN': '0',
            'SDBQ_TGCKH_CN': '1000000000.5', 'SDBQ_TGKKH_CN': '54000000.123456', 'SDBQ_TV': '0',
            'DIEM_KH_CN': diem, 'NHOM_TAI_CN': nhom, 'HANG_TAI_CN': hang, 'NHOM_AGR': nhom, 'HANG_AGR': hang,
            'DON_VI_DAU_MOI': 'Chi nhánh X'}


def bc06(rows):
    return SimpleUploadedFile('7202_BC06_20261031_7202_7202_0_001__.csv', _csv(BC06_COT, rows))


def _xlsx(ten, sheets):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for title, rows in sheets:
        ws = wb.create_sheet(title)
        for r in rows:
            ws.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    return SimpleUploadedFile(ten, buf.getvalue())


def loa(rows, tu='01/11/2026 00:00:00', den='08/11/2026 23:59:59'):
    head = [[None] * 12 for _ in range(16)]
    head[1][1] = 'BẢNG THỐNG KÊ DOANH SỐ LOA'
    head[4][3], head[4][6] = 'Từ ngày', tu
    head[5][3], head[5][6] = 'Đến ngày', den
    head.append([None, None, 'Mã', None, 'Chi nhánh', 'Nhà cung cấp Loa', None, 'Tên KH', 'TK ảo\t',
                 'TK Agribank', 'Số lượng giao dịch', 'Doanh số'])
    data = [[None, None, i, None, '7202', 'Loa Thần Tài MobiFone', None, ten, tk_ao, stk, n, ds]
            for i, (ten, tk_ao, stk, n, ds) in enumerate(rows, 1)]
    return _xlsx('OAB-ThongKeDoanhSoLoa08112026.xlsx', [('Sheet 1', head + data)])


def qr(rows):
    head = ['STT', 'Họ Tên', 'STK', 'TEN CUA HANG', 'PHONG PHAT SINH', 'NGAY LAM', None]
    data = [[i, *r] for i, r in enumerate(rows, 1)]
    return _xlsx('TONG HOP QR 7202.xlsx', [('Sheet1', [head] + data), ('Sheet2', [[1, 'X', '1']])])


def khtc(rows, ten='Quản trị khách hàng tổ chức (KHTC) - 03156_2026-11-08 18_52_19.xlsx'):
    head = ['No.', 'Mã Tổ chức', 'Tên khách hàng', 'Trạng thái hoạt động', 'Vùng hệ thống chính', 'Chi nhánh',
            'Thời gian đăng ký', 'Người tạo', 'Ngày cập nhật', 'Người cập nhật', 'Thời gian đồng bộ cuối']
    data = [[f'{i}.0', ma, t, 'Hoạt động', 'X', '7202', '2026-01-02 10:00:00.0', 'nv', '', '', '2026-11-08 10:00:00.0']
            for i, (ma, t) in enumerate(rows, 1)]
    return _xlsx(ten, [('Sheet 1', [head] + data)])


class Co_so(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('u', password='p')

    def nhap(self, **files):
        return NhapKy(files, self.user).chay()

    def moc(self):
        """Lần 1: 3 KH cá nhân + 1 tổ chức (chỉ DP01) + 1 KH chỉ có khoản vay."""
        return self.nhap(
            CN05=cn05([kh_cn('000000001', 'Nguyễn Văn An', DK_AGRIBANK_PLUS=1, TKTT_SO_TK=1),
                       kh_cn('000000002', 'Trần Thị Bình', SMS_BANKING=1),
                       kh_cn('000000003', 'Lê Văn Cường')]),
            DP01=dp01([tk('7202000000001', '000000001', 'Nguyễn Văn An'),
                       tk('7202000000002', '000000002', 'Trần Thị Bình', 5000000),
                       tk('7202000000003', '000000003', 'Lê Văn Cường'),
                       tk('7202000000009', '000000009', 'Công ty TNHH Hoa Mai', 9000000, cust_type='530')]),
            LN01=ln01([vay('7202LDS000000001', '000000001', 'Nguyễn Văn An'),
                       vay('7202LDS000000005', '000000005', 'Phạm Văn Năm')]),
        )


class NhapDuLieuTest(Co_so):
    def test_bat_buoc_cn05_dp01(self):
        with self.assertRaises(FileLoi):
            self.nhap(CN05=cn05([kh_cn('000000001', 'A')]))

    def test_sai_file_bao_loi_cau_truc(self):
        with self.assertRaisesRegex(FileLoi, 'CN05'):
            self.nhap(CN05=dp01([tk('1', '1', 'A')]), DP01=dp01([tk('1', '1', 'A')]))

    def test_lan_dau_la_moc_khong_ghi_bien_dong(self):
        ky = self.moc()
        self.assertEqual(BienDong.objects.count(), 0)
        self.assertTrue(all(nf.la_moc for nf in ky.files.all()))
        self.assertEqual(KhachHang.objects.filter(con_hoat_dong=True).count(), 5)
        an = KhachHang.objects.get(ma_kh='000000001')
        self.assertEqual(an.cccd, '012345678901')
        self.assertEqual(an.ngay_sinh, date(1990, 1, 15))
        self.assertEqual(an.gioi_tinh, 'Nữ')
        self.assertEqual(an.dich_vu, {'agribank_plus': 1, 'tktt': 1})
        to_chuc = KhachHang.objects.get(ma_kh='000000009')
        self.assertTrue(to_chuc.la_to_chuc)
        self.assertFalse(to_chuc.co_cn05)
        chi_vay = KhachHang.objects.get(ma_kh='000000005')   # không có trong CN05/DP01
        self.assertEqual(chi_vay.cccd, '098765432109')
        self.assertEqual(ky.tong_hop['so_kh'], 5)
        self.assertEqual(ky.tong_hop['tong_so_du_vnd'], 1000000 * 2 + 5000000 + 9000000)

    def test_zip(self):
        self.nhap(CN05=cn05([kh_cn('000000001', 'A')], zip_=True), DP01=dp01([tk('7202000000001', '000000001', 'A')]))
        self.assertTrue(KhachHang.objects.filter(ma_kh='000000001', co_cn05=True).exists())

    def test_tu_choi_du_lieu_cu_hon(self):
        self.moc()
        with self.assertRaisesRegex(FileLoi, 'cũ hơn'):
            self.nhap(CN05=cn05([kh_cn('000000001', 'A')], ngay='20261001'),
                      DP01=dp01([tk('7202000000001', '000000001', 'A')], ngay='20261001'))

    def test_bien_dong_lan_hai(self):
        self.moc()
        ky = self.nhap(
            CN05=cn05([kh_cn('000000001', 'Nguyễn Văn An', TKTT_SO_TK=1, VISA=1),      # bỏ AP, thêm Visa
                       kh_cn('000000002', 'Trần Thị Bình', SMS_BANKING=1),
                       kh_cn('000000004', 'Võ Thị Dung')], ngay='20261108'),             # KH mới; 003 mất
            DP01=dp01([tk('7202000000001', '000000001', 'Nguyễn Văn An'),
                       tk('7202000000002', '000000002', 'Trần Thị Bình', status='Close'),  # đóng
                       tk('7202000000004', '000000004', 'Võ Thị Dung'),                   # TK mới
                       tk('7202000000009', '000000009', 'Công ty TNHH Hoa Mai', cust_type='530')],
                      ngay='20261108'),                                                  # 003 biến mất
            LN01=ln01([vay('7202LDS000000001', '000000001', 'Nguyễn Văn An', du_no=0),     # tất toán
                       vay('7202LDS000000005', '000000005', 'Phạm Văn Năm'),
                       vay('7202LDS000000006', '000000004', 'Võ Thị Dung')], ngay='20261108'),
        )
        bd = {(b.loai, b.doi_tuong or b.ma_kh) for b in ky.bien_dong.all()}
        self.assertEqual(bd, {
            ('KH_MOI', '000000004'), ('KH_MAT', '000000003'),
            ('TK_MOI', '7202000000004'), ('TK_DONG', '7202000000002'), ('TK_DONG', '7202000000003'),
            ('DV_HUY', 'Agribank Plus'), ('DV_DANG_KY', 'Thẻ Visa'),
            ('VAY_TAT_TOAN', '7202LDS000000001'), ('VAY_MOI', '7202LDS000000006'),
        })
        self.assertFalse(KhachHang.objects.get(ma_kh='000000003').con_hoat_dong)
        self.assertFalse(TaiKhoanTG.objects.get(so_tk='7202000000003').con_hoat_dong)
        self.assertFalse(KhoanVay.objects.get(so_giai_ngan='7202LDS000000001').con_du_no)

    def test_khong_nap_ln01_thi_giu_nguyen_khoan_vay(self):
        self.moc()
        ky = self.nhap(CN05=cn05([kh_cn('000000001', 'Nguyễn Văn An', DK_AGRIBANK_PLUS=1, TKTT_SO_TK=1)], ngay='20261108'),
                       DP01=dp01([tk('7202000000001', '000000001', 'Nguyễn Văn An')], ngay='20261108'))
        self.assertEqual(KhoanVay.objects.filter(con_du_no=True).count(), 2)
        self.assertFalse(ky.bien_dong.filter(loai__startswith='VAY').exists())
        # KH chỉ có khoản vay vẫn còn hoạt động
        self.assertTrue(KhachHang.objects.get(ma_kh='000000005').con_hoat_dong)

    def test_loa(self):
        self.moc()
        self.nhap(CN05=cn05([kh_cn('000000001', 'A')], ngay='20261108'),
                  DP01=dp01([tk('7202000000001', '000000001', 'A'), tk('7202000000002', '000000002', 'B')], ngay='20261108'),
                  LOA=loa([('A', 'V001', '7202000000001', 5, 1500000), ('A', 'V002', '7202000000001', 0, 0),
                           ('Lạ', 'V003', '7202999999999', 1, 10)]))
        l1 = LoaThanTai.objects.get(tk_ao='V001')
        self.assertEqual((l1.ma_kh, l1.tu_ngay, l1.den_ngay, l1.doanh_so), ('000000001', date(2026, 11, 1),
                                                                            date(2026, 11, 8), Decimal(1500000)))
        nf = NguonFile.objects.get(nguon='LOA')
        self.assertTrue(nf.la_moc)
        self.assertEqual(len(nf.khong_khop), 1)
        # Kỳ sau: V002 mất, V004 mới; kỳ trước vẫn giữ
        ky = self.nhap(CN05=cn05([kh_cn('000000001', 'A')], ngay='20261108'),
                       DP01=dp01([tk('7202000000001', '000000001', 'A'), tk('7202000000002', '000000002', 'B')], ngay='20261108'),
                       LOA=loa([('A', 'V001', '7202000000001', 7, 2000000), ('B', 'V004', '7202000000002', 1, 5),
                                ('Lạ', 'V003', '7202999999999', 1, 10)],
                               tu='01/12/2026 00:00:00', den='05/12/2026 23:59:59'))
        self.assertEqual({(b.loai, b.doi_tuong) for b in ky.bien_dong.filter(loai__startswith='LOA')},
                         {('LOA_MAT', 'V002'), ('LOA_MOI', 'V004')})
        self.assertEqual(LoaThanTai.objects.filter(tk_ao='V001').count(), 2)

    def test_qr(self):
        self.moc()
        self.nhap(CN05=cn05([kh_cn('000000001', 'A')], ngay='20261108'),
                  DP01=dp01([tk('7202000000001', '000000001', 'A')], ngay='20261108'),
                  QR=qr([['A', '7202000000001', 'Tiệm X', 'HS', '12/03/2026', 'Học Sinh'],
                         ['A', '7202000000001', '', 'P1', 'Trinh', ''],
                         ['Z', '7202888888888', '', '', None, '']]))
        rows = list(MaQR.objects.filter(so_tk='7202000000001').order_by('id'))
        self.assertEqual(len(rows), 2)
        self.assertEqual((rows[0].ma_kh, rows[0].ngay_lam, rows[0].ghi_chu), ('000000001', date(2026, 3, 12), 'Học Sinh'))
        self.assertEqual((rows[1].ngay_lam, rows[1].ngay_lam_goc), (None, 'Trinh'))
        self.assertEqual(len(NguonFile.objects.get(nguon='QR').khong_khop), 1)

    def test_khtc_khop_ten_va_gan_tay(self):
        self.moc()
        files = dict(CN05=cn05([kh_cn('000000001', 'A')], ngay='20261108'),
                     DP01=dp01([tk('7202000000009', '000000009', 'Công ty TNHH Hoa Mai', cust_type='530'),
                                tk('7202000000008', '000000008', 'HTX Bình Minh', cust_type='570')], ngay='20261108'))
        self.nhap(**files, KHTC=khtc([('7202HOAMAI', 'CÔNG TY TNHH HOA MAI'), ('7202BM', 'Hợp tác xã Bình Minh')]))
        self.assertEqual(EbankingToChuc.objects.get(ma_to_chuc='7202HOAMAI').ma_kh, '000000009')
        self.assertEqual(EbankingToChuc.objects.get(ma_to_chuc='7202BM').ma_kh, '')
        c = self.client
        c.force_login(self.user)
        c.post(reverse('kh360:gan_to_chuc'), {'ma_to_chuc': '7202BM', 'ma_kh': '000000008'})
        self.assertEqual(EbankingToChuc.objects.get(ma_to_chuc='7202BM').ma_kh, '000000008')
        # Lần sau vẫn nhớ
        files = dict(CN05=cn05([kh_cn('000000001', 'A')], ngay='20261109'),
                     DP01=dp01([tk('7202000000008', '000000008', 'HTX Bình Minh', cust_type='570')], ngay='20261109'))
        self.nhap(**files, KHTC=khtc([('7202BM', 'Hợp tác xã Bình Minh')],
                                     ten='Quản trị khách hàng tổ chức (KHTC) - 03156_2026-11-09 08_00_00.xlsx'))
        self.assertEqual(EbankingToChuc.objects.get(ma_to_chuc='7202BM').ma_kh, '000000008')


class GiaoDienTest(Co_so):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_phan_quyen(self):
        from templates_app.models import UserProfile

        def user(ten, ho_so):
            u = User.objects.create_user(ten, password='p')
            if ho_so:
                UserProfile.objects.create(user=u, employee_code=ten, full_name=ten, **ho_so)
            return u
        self.moc()
        trang = {'tra_cuu': reverse('kh360:tra_cuu'), 'ho_so': reverse('kh360:ho_so', args=['000000001']),
                 'thong_ke': reverse('kh360:thong_ke'), 'thong_ke_so': reverse('kh360:thong_ke_so'),
                 'thong_ke_vay': reverse('kh360:thong_ke_vay'),
                 'bien_dong': reverse('kh360:bien_dong'),
                 'cap_nhat': reverse('kh360:cap_nhat')}
        quan_ly = {'tra_cuu', 'ho_so', 'thong_ke', 'thong_ke_so', 'thong_ke_vay', 'bien_dong'}
        chi_tra_cuu = {'tra_cuu', 'ho_so'}
        mong_doi = [   # (hồ sơ nhân viên, các trang được vào)
            ({'position': 'TRUONG_PHONG'}, quan_ly),
            ({'position': 'PHO_PHONG'}, quan_ly),
            ({'position': 'GIAM_DOC'}, quan_ly),
            ({'position': 'PHO_GIAM_DOC'}, quan_ly),
            ({'position': 'GD_PGD'}, quan_ly),
            ({'position': 'PGD_PGD'}, quan_ly),
            ({'position': 'NHAN_VIEN', 'department': 'BAN_GIAM_DOC'}, quan_ly),
            ({'position': 'NHAN_VIEN', 'job_function': 'HAU_KIEM_VIEN'}, quan_ly),
            ({'position': 'NHAN_VIEN', 'job_function': 'GIAO_DICH_VIEN'}, chi_tra_cuu),
            ({'position': 'NHAN_VIEN', 'department': 'KHACH_HANG'}, chi_tra_cuu),   # cán bộ tín dụng
            (None, chi_tra_cuu),                                                   # chưa khai báo hồ sơ
        ]
        for i, (ho_so, duoc) in enumerate(mong_doi):
            chuc_vu = ho_so
            self.client.force_login(user(f'nv{i}', ho_so))
            for ten, url in trang.items():
                r = self.client.get(url)
                self.assertEqual(r.status_code, 200 if ten in duoc else 302, f'{chuc_vu} → {ten}')
            r = self.client.get(trang['tra_cuu'])
            self.assertEqual(trang['thong_ke'] in r.content.decode(), 'thong_ke' in duoc, chuc_vu)
            self.assertNotIn(trang['cap_nhat'], r.content.decode())
            # Không cập nhật được dữ liệu bằng POST
            self.client.post(trang['cap_nhat'], {'CN05': cn05([kh_cn('1', 'A')], ngay='20261201'),
                                                 'DP01': dp01([tk('1', '1', 'A')], ngay='20261201')})
            self.assertFalse(NguonFile.objects.filter(ngay_du_lieu=date(2026, 12, 1)).exists())

    def test_chua_dang_nhap(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse('kh360:tra_cuu')).status_code, 302)

    def test_upload_va_tra_cuu(self):
        r = self.client.post(reverse('kh360:cap_nhat'), {
            'CN05': cn05([kh_cn('000000001', 'Nguyễn Văn An'), kh_cn('000000002', 'Nguyễn Thị Bé')]),
            'DP01': dp01([tk('7202000000001', '000000001', 'Nguyễn Văn An'),
                          tk('7202000000002', '000000002', 'Nguyễn Thị Bé')]),
        }, follow=True)
        self.assertContains(r, 'Đã cập nhật dữ liệu ngày 31/10/2026')
        self.assertContains(r, 'Đã cập nhật vào ngày')
        r = self.client.get(reverse('kh360:tra_cuu'), {'q': 'nguyen'})
        self.assertContains(r, 'Nguyễn Thị Bé')
        r = self.client.get(reverse('kh360:tra_cuu'), {'q': '7202000000002'})   # STK → 1 KH, tự mở bảng nổi
        self.assertEqual(r.context['page'].paginator.count, 1)
        self.assertContains(r, 'kh360Mo("/kh360/kh/000000002/")')
        r = self.client.get(reverse('kh360:ho_so', args=['000000002']), {'modal': 1})
        self.assertContains(r, '7202000000002')
        self.assertNotContains(r, '<html')                  # chỉ là nội dung bảng nổi
        self.assertContains(r, 'Bà</span>Nguyễn Thị Bé')     # danh xưng theo giới tính

    def test_sap_xep_va_phan_trang_10_dong(self):
        self.nhap(CN05=cn05([kh_cn(f'0000000{i:02d}', f'Nguyễn Khách {i:02d}') for i in range(1, 13)]),
                  DP01=dp01([tk(f'72020000000{i:02d}', f'0000000{i:02d}', f'Nguyễn Khách {i:02d}', so_du=i * 1000000)
                             for i in range(1, 13)]))
        r = self.client.get(reverse('kh360:tra_cuu'), {'q': 'nguyen'})   # mặc định: số dư giảm dần
        self.assertEqual(len(r.context['page'].object_list), 10)
        self.assertEqual(r.context['page'].object_list[0].ma_kh, '000000012')
        r = self.client.get(reverse('kh360:tra_cuu'), {'q': 'nguyen', 'sort': 'ten', 'page': 2})
        self.assertEqual([k.ma_kh for k in r.context['page'].object_list], ['000000011', '000000012'])
        r = self.client.get(reverse('kh360:tra_cuu'), {'q': 'nguyen', 'sort': 'xoa_db'})   # tham số lạ → mặc định
        self.assertEqual(r.context['sort'], '-so_du')

    def test_ghi_chu_khong_mat_khi_cap_nhat_lai(self):
        self.moc()
        r = self.client.post(reverse('kh360:luu_ghi_chu', args=['000000001']), {'noi_dung': 'Hẹn tư vấn số đẹp'})
        self.assertTrue(r.json()['ok'])
        self.nhap(CN05=cn05([kh_cn('000000001', 'Nguyễn Văn An')], ngay='20261108'),
                  DP01=dp01([tk('7202000000001', '000000001', 'Nguyễn Văn An')], ngay='20261108'))
        r = self.client.get(reverse('kh360:ho_so', args=['000000001']), {'modal': 1})
        self.assertContains(r, 'Hẹn tư vấn số đẹp')

    def test_thong_ke(self):
        self.nhap(
            CN05=cn05([kh_cn('000000001', 'Giàu Có OTT', DK_AGRIBANK_PLUS=1, DK_AGRIBANK_PLUS_OTT=1, TG_SMS_TIEN_GUI=1),
                       kh_cn('000000002', 'Giàu Chưa AP', SMS_BANKING=1),
                       kh_cn('000000003', 'Ít Tiền', DK_AGRIBANK_PLUS_OTT=1, TG_SMS_TIEN_GUI=1)]),
            DP01=dp01([tk('7202000000001', '000000001', 'Giàu Có OTT', 2000000000),
                       tk('7202000000002', '000000002', 'Giàu Chưa AP', 1500000000, BIRTH_DATE="'19500101"),
                       tk('7202000000003', '000000003', 'Ít Tiền', 1000000),
                       tk('7202000000009', '000000009', 'Công ty Lớn', 9000000000, cust_type='530')]),
            BC06=bc06([bc('000000001', 'Vip', 'Platinum', 3000), bc('000000002', 'Thân thiết', '', 250)]),
            LOA=loa([('Ít Tiền', 'V1', '7202000000003', 1, 10)]),
        )
        url = reverse('kh360:thong_ke')

        def ma(**p):
            r = self.client.get(url, p)
            return sorted(k.ma_kh for k in r.context['page'].paginator.object_list)

        self.assertEqual(ma(so_du_tu='1.000.000.000'), ['000000001', '000000002', '000000009'])
        self.assertEqual(ma(so_du_tu='1.000.000.000', so_du_den='5.000.000.000'), ['000000001', '000000002'])
        self.assertEqual(ma(so_du_tu='1000000000', dv_agribank_plus='chua'), ['000000002'])    # tổ chức bị loại
        self.assertEqual(ma(dv_agribank_plus_ott='co', dv_tg_sms='co'), ['000000001', '000000003'])
        self.assertEqual(ma(dv_sms_banking='co', dv_agribank_plus_ott='chua'), ['000000002'])
        self.assertEqual(ma(hang='vip'), ['000000001'])
        self.assertEqual(ma(hang='chua_xep', loai='ca_nhan'), ['000000003'])
        self.assertEqual(ma(tuoi_tu='60'), ['000000002'])
        self.assertEqual(ma(loa='co'), ['000000003'])
        self.assertEqual(ma(loai='to_chuc'), ['000000009'])
        r = self.client.get(url, {'so_du_tu': '1000000000'})
        self.assertEqual(r.context['tong']['so_kh'], 3)
        self.assertEqual(r.context['tong']['so_du'], Decimal('12500000000'))
        self.assertIn('sort=', r.content.decode())          # giữ điều kiện khi sắp xếp
        self.assertIn('so_du_tu=1000000000', r.content.decode())
        r = self.client.get(url, {'so_du_tu': '1000000000', 'xuat': 'excel'})
        wb = openpyxl.load_workbook(io.BytesIO(r.content))
        self.assertEqual(wb.active.max_row, 4)                # tiêu đề + 3 KH
        for _, tham_so in MAU_MAC_DINH['kh']:                 # mẫu mặc định đều chạy được
            self.assertEqual(self.client.get(f'{url}?{tham_so}').status_code, 200)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_thong_ke_so_tiet_kiem(self):
        from dateutil.relativedelta import relativedelta
        hom_nay = date.today()
        d = lambda x: "'" + x.strftime('%Y%m%d')

        def so(so_tk, ma, ten, so_du, ky_han, mo, den_han, ls, hinh_thuc='Trả lãi khi đến hạn'):
            return tk(so_tk, ma, ten, so_du, TAI_KHOAN_HACH_TOAN='423202', DP_TYPE_NAME='Tiết kiệm có kỳ hạn',
                      MONTH_TERM=f"'{ky_han}", OPENING_DATE=d(mo), MATURITY_DATE=d(den_han), RATE=ls,
                      TERM_DP_NAME=hinh_thuc)
        self.nhap(
            CN05=cn05([kh_cn('000000001', 'Chủ Sổ Một', DK_AGRIBANK_PLUS=1), kh_cn('000000002', 'Chủ Sổ Hai')]),
            DP01=dp01([
                tk('7202000000001', '000000001', 'Chủ Sổ Một', 5000000),                    # TKTT, không phải sổ
                so('S1', '000000001', 'Chủ Sổ Một', 600000000, 12, hom_nay - relativedelta(months=13),
                   hom_nay + relativedelta(days=5), '5.2'),
                so('S3', '000000001', 'Chủ Sổ Một', 50000000, 1, hom_nay - relativedelta(months=40),
                   hom_nay - relativedelta(days=3), '1.6'),
                so('S2', '000000002', 'Chủ Sổ Hai', 100000000, 6, hom_nay - relativedelta(months=2),
                   hom_nay + relativedelta(days=60), '4', 'Gửi góp không theo định kỳ hàn'),
                tk('7202000000002', '000000002', 'Chủ Sổ Hai', -20000000, TAI_KHOAN_HACH_TOAN='211108'),  # thấu chi
            ]),
        )
        # Số dư âm của TK thấu chi không bị trừ vào tổng số dư tiền gửi
        self.assertEqual(KhachHang.objects.get(ma_kh='000000002').tong_so_du, Decimal(100000000))
        url = reverse('kh360:thong_ke_so')

        def so_tk(q):
            r = self.client.get(f'{url}?{q}')
            return sorted(x.so_tk for x in r.context['page'].paginator.object_list)
        self.assertEqual(so_tk('den_han=7'), ['S1'])
        self.assertEqual(so_tk('den_han=30'), ['S1'])
        self.assertEqual(so_tk('den_han=qua_han'), ['S3'])
        self.assertEqual(so_tk(f'den_han=khoang&dh_tu={hom_nay:%Y-%m-%d}'), ['S1', 'S2'])
        self.assertEqual(so_tk('ky_han=12&ky_han=1'), ['S1', 'S3'])
        self.assertEqual(so_tk('ky_han_tu=6'), ['S1', 'S2'])
        self.assertEqual(so_tk('gui_tu=36'), ['S3'])
        self.assertEqual(so_tk('gui_den=3'), ['S2'])
        self.assertEqual(so_tk('so_du_tu=500.000.000'), ['S1'])
        self.assertEqual(so_tk('ls_tu=4&ls_den=5,5'), ['S1', 'S2'])
        self.assertEqual(so_tk('hinh_thuc=gui_gop'), ['S2'])
        self.assertEqual(so_tk('dv=agribank_plus&dv_tt=chua'), ['S2'])
        self.assertEqual(so_tk('loai=ca_nhan'), ['S1', 'S2', 'S3'])
        r = self.client.get(url, {'ky_han_tu': '1'})
        tong = r.context['tong']
        self.assertEqual((tong['so_so'], tong['so_kh'], tong['tong_du']), (3, 2, Decimal(750000000)))
        self.assertAlmostEqual(float(tong['ls_bq']), (600 * 5.2 + 50 * 1.6 + 100 * 4) / 750, places=4)
        self.assertContains(r, 'còn 5 ngày')
        self.assertContains(r, 'quá 3 ngày')
        r = self.client.get(url, {'ky_han_tu': '1', 'xuat': 'excel'})
        self.assertEqual(openpyxl.load_workbook(io.BytesIO(r.content)).active.max_row, 4)
        for _, tham_so in MAU_MAC_DINH['so']:                 # mẫu mặc định đều chạy được
            self.assertEqual(self.client.get(f'{url}?{tham_so}').status_code, 200)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_tach_so_du_khong_ky_han_va_tiet_kiem(self):
        so = lambda so_tk, ma, ten, so_du: tk(so_tk, ma, ten, so_du, TAI_KHOAN_HACH_TOAN='423202', MONTH_TERM="'6")
        self.nhap(
            CN05=cn05([kh_cn('000000001', 'TT Và Sổ'), kh_cn('000000002', 'Chỉ TT'), kh_cn('000000003', 'Hai Sổ')]),
            DP01=dp01([tk('T1', '000000001', 'TT Và Sổ', 80000000), so('S1', '000000001', 'TT Và Sổ', 150000000),
                       tk('T2', '000000002', 'Chỉ TT', 120000000),
                       so('S3', '000000003', 'Hai Sổ', 150000000), so('S4', '000000003', 'Hai Sổ', 150000000)]),
        )
        kh1 = KhachHang.objects.get(ma_kh='000000001')
        self.assertEqual((kh1.tong_so_du, kh1.so_du_kkh, kh1.so_du_ckh),
                         (Decimal(230000000), Decimal(80000000), Decimal(150000000)))
        url = reverse('kh360:thong_ke')

        def ma(**p):
            r = self.client.get(url, p)
            return sorted(k.ma_kh for k in r.context['page'].paginator.object_list)
        self.assertEqual(ma(so_du_tu='100000000', so_du_den='200000000'), ['000000002'])   # tổng theo KH
        self.assertEqual(ma(ckh_tu='100000000'), ['000000001', '000000003'])
        self.assertEqual(ma(kkh_tu='50000000', ckh_den='0'), ['000000002'])                # chưa có sổ
        r = self.client.get(url, {'so_du_tu': '1'})
        self.assertEqual((r.context['tong']['kkh'], r.context['tong']['ckh']), (Decimal(200000000), Decimal(450000000)))
        self.assertContains(r, 'Tiết kiệm')
        # Migration 0004 tính lại được từ dữ liệu cũ
        import importlib
        from django.apps import apps
        KhachHang.objects.update(so_du_kkh=0, so_du_ckh=0)
        importlib.import_module('kh360.migrations.0004_so_du_tach_thoi_han_vay').tinh_lai(apps, None)
        kh1.refresh_from_db()
        self.assertEqual((kh1.so_du_kkh, kh1.so_du_ckh), (Decimal(80000000), Decimal(150000000)))

    def test_thong_ke_tien_vay(self):
        from dateutil.relativedelta import relativedelta
        hn = date.today()
        d = lambda x: x.strftime('%Y%m%d')
        self.nhap(
            CN05=cn05([kh_cn('000000001', 'Vay Một', DK_AGRIBANK_PLUS=1), kh_cn('000000002', 'Vay Hai')]),
            DP01=dp01([tk('T1', '000000001', 'Vay Một'), tk('T2', '000000002', 'Vay Hai')]),
            LN01=ln01([
                vay('V1', '000000001', 'Vay Một', 1200000000, DSBSDT=d(hn - relativedelta(days=10)),
                    DSBSMATDT=d(hn - relativedelta(days=10) + relativedelta(months=12)),
                    NEXT_REPAY_DATE=d(hn + relativedelta(days=3))),
                vay('V2', '000000002', 'Vay Hai', 300000000, DSBSDT=d(hn - relativedelta(months=26)),
                    DSBSMATDT=d(hn - relativedelta(days=5)), NHOM_NO="'03", OFFICER_NAME='Cán bộ B',
                    LOAN_TYPE='Cho vay trung hạn', INTEREST_RATE='9'),
                vay('V3', '000000002', 'Vay Hai', 20000000, TAI_KHOAN='211108', NHOM_NO="'02",
                    DSBSDT=d(hn - relativedelta(days=60)), DSBSMATDT=d(hn + relativedelta(days=300))),
                vay('V4', '000000001', 'Vay Một', 0),
            ]),
        )
        self.assertEqual(KhoanVay.objects.get(so_giai_ngan='V1').thoi_han_thang, 12)
        url = reverse('kh360:thong_ke_vay')

        def gn(q):
            r = self.client.get(f'{url}?{q}')
            return sorted(v.so_giai_ngan for v in r.context['page'].paginator.object_list)
        self.assertEqual(gn('du_no_tu=1.000.000.000'), ['V1'])
        self.assertEqual(gn('thoi_han_tu=13'), ['V2'])
        self.assertEqual(gn('thoi_han_loai=ngan'), ['V1', 'V3'])
        self.assertEqual(gn('da_vay_tu=24'), ['V2'])
        self.assertEqual(gn('giai_ngan=qua_30'), ['V1'])
        self.assertEqual(gn('tra_tiep=7'), ['V1'])
        self.assertEqual(gn('dao_han=qua_han'), ['V2'])
        self.assertEqual(gn(f'dao_han=khoang&dh_tu={hn:%Y-%m-%d}'), ['V1', 'V3'])
        self.assertEqual(gn('nhom_no=02&nhom_no=03'), ['V2', 'V3'])
        self.assertEqual(gn('san_pham=thau_chi'), ['V3'])
        self.assertEqual(gn('san_pham=vay'), ['V1', 'V2'])
        self.assertEqual(gn('can_bo=Cán bộ B'), ['V2'])
        self.assertEqual(gn('ls_tu=8'), ['V2'])
        self.assertEqual(gn('dv=agribank_plus&dv_tt=chua'), ['V2', 'V3'])
        self.assertEqual(gn('tinh_trang=tat_toan'), ['V4'])
        r = self.client.get(url, {'du_no_tu': '1'})
        tong = r.context['tong']
        self.assertEqual((tong['so_mon'], tong['so_kh'], tong['tong_no'], tong['no_xau'], tong['mon_nhom2']),
                         (3, 2, Decimal(1520000000), Decimal(300000000), 2))
        self.assertContains(r, 'quá 5 ngày')
        self.assertContains(r, 'Thấu chi')
        r = self.client.get(url, {'du_no_tu': '1', 'xuat': 'excel'})
        self.assertEqual(openpyxl.load_workbook(io.BytesIO(r.content)).active.max_row, 4)
        for _, tham_so in MAU_MAC_DINH['vay']:                # mẫu mặc định đều chạy được
            self.assertEqual(self.client.get(f'{url}?{tham_so}').status_code, 200)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_quan_ly_mau_nhanh(self):
        self.assertEqual(tao_mau_mac_dinh(MauThongKe), sum(len(v) for v in MAU_MAC_DINH.values()))
        self.assertEqual(tao_mau_mac_dinh(MauThongKe), 0)                 # chạy lại không nhân đôi
        url = reverse('kh360:thong_ke_so')
        r = self.client.get(url)
        self.assertContains(r, 'Đến hạn trong 7 ngày tới')
        self.assertNotContains(r, 'Vay trung, dài hạn')                    # mẫu của tab khác
        # Thêm: bỏ trang / sắp xếp / ô trống khỏi điều kiện
        r = self.client.post(reverse('kh360:mau_luu'), {
            'tab': 'so', 'ten': 'Sổ lớn sắp đến hạn',
            'tham_so': 'den_han=30&so_du_tu=2000000000&so_du_den=&sort=-so_du&page=3&ky_han=6&ky_han=12'})
        mau = MauThongKe.objects.get(ten='Sổ lớn sắp đến hạn')
        self.assertEqual(mau.tham_so, 'den_han=30&so_du_tu=2000000000&ky_han=6&ky_han=12')
        self.assertEqual(mau.nguoi_sua, self.user)
        self.assertRedirects(r, f'{url}?{mau.tham_so}&mau={mau.pk}', fetch_redirect_response=False)
        r = self.client.get(f'{url}?{mau.tham_so}&mau={mau.pk}')
        self.assertEqual(r.context['mau_chon'], mau)
        self.assertContains(r, 'Lưu đè mẫu')
        # Sửa tên + thứ tự (không đụng điều kiện), rồi lưu đè điều kiện
        self.client.post(reverse('kh360:mau_luu'), {'tab': 'so', 'id': mau.pk, 'ten': 'Sổ ≥ 2 tỷ', 'thu_tu': '-5',
                                                     'quay_lai': 'quan_ly'})
        mau.refresh_from_db()
        self.assertEqual((mau.ten, mau.thu_tu, mau.tham_so[:10]), ('Sổ ≥ 2 tỷ', -5, 'den_han=30'))
        self.assertEqual(MauThongKe.objects.filter(tab='so').first(), mau)  # thứ tự nhỏ lên đầu
        self.client.post(reverse('kh360:mau_luu'), {'tab': 'so', 'id': mau.pk, 'tham_so': 'den_han=7'})
        mau.refresh_from_db()
        self.assertEqual(mau.tham_so, 'den_han=7')
        # Không cho lưu mẫu rỗng
        n = MauThongKe.objects.count()
        self.client.post(reverse('kh360:mau_luu'), {'tab': 'so', 'ten': 'Rỗng', 'tham_so': 'page=2&sort=ten'})
        self.assertEqual(MauThongKe.objects.count(), n)
        # Xoá, rồi khôi phục mẫu mặc định chỉ thêm lại mẫu mặc định đã xoá
        mac_dinh = MauThongKe.objects.get(tab='so', ten='Đến hạn trong 7 ngày tới')
        self.client.post(reverse('kh360:mau_xoa', args=[mac_dinh.pk]))
        self.client.post(reverse('kh360:mau_xoa', args=[mau.pk]))
        self.assertFalse(MauThongKe.objects.filter(pk__in=[mac_dinh.pk, mau.pk]).exists())
        self.client.post(reverse('kh360:mau_khoi_phuc'), {'tab': 'so'})
        self.assertTrue(MauThongKe.objects.filter(tab='so', ten='Đến hạn trong 7 ngày tới').exists())
        self.assertFalse(MauThongKe.objects.filter(ten='Sổ ≥ 2 tỷ').exists())
        # Nhân viên (chỉ tra cứu) không thêm / xoá được
        from templates_app.models import UserProfile
        nv = User.objects.create_user('nv_mau', password='p')
        UserProfile.objects.create(user=nv, employee_code='nv_mau', full_name='NV', position='NHAN_VIEN')
        self.client.force_login(nv)
        self.client.post(reverse('kh360:mau_luu'), {'tab': 'kh', 'ten': 'Lén', 'tham_so': 'loai=ca_nhan'})
        self.client.post(reverse('kh360:mau_xoa', args=[MauThongKe.objects.first().pk]))
        self.assertFalse(MauThongKe.objects.filter(ten='Lén').exists())
        self.assertEqual(MauThongKe.objects.count(), sum(len(v) for v in MAU_MAC_DINH.values()))

    def test_bc06_hang_vip(self):
        self.moc()
        self.nhap(CN05=cn05([kh_cn('000000001', 'Nguyễn Văn An'), kh_cn('000000002', 'Trần Thị Bình')], ngay='20261108'),
                  DP01=dp01([tk('7202000000001', '000000001', 'Nguyễn Văn An'),
                             tk('7202000000002', '000000002', 'Trần Thị Bình')], ngay='20261108'),
                  BC06=bc06([bc('000000001', 'Vip', 'Platinum', 6122), bc('000000002', 'Thân thiết', '', 40)]))
        xh = XepHangKH.objects.get(ma_kh='000000001')
        self.assertEqual((xh.nhan_cn, xh.diem_kh, xh.thang), ('Platinum VIP', 6122, '202610'))
        self.assertEqual(xh.sdbq_tg_khong_ky_han, Decimal('54000000.12'))
        r = self.client.get(reverse('kh360:ho_so', args=['000000001']), {'modal': 1})
        self.assertContains(r, 'Platinum VIP')
        self.assertContains(r, '54 tr đ')
        r = self.client.get(reverse('kh360:tra_cuu'), {'q': 'n', 'sort': '-hang'})
        self.assertEqual(r.context['page'].object_list[0].nhan_hang, 'Platinum VIP')

    def test_upload_thieu_file(self):
        r = self.client.post(reverse('kh360:cap_nhat'), {'CN05': cn05([kh_cn('1', 'A')])}, follow=True)
        self.assertContains(r, 'Bắt buộc phải có file CN05 và DP01')

    def test_ho_so_va_bien_dong(self):
        self.moc()
        self.nhap(CN05=cn05([kh_cn('000000001', 'Nguyễn Văn An', VISA=1)], ngay='20261108'),
                  DP01=dp01([tk('7202000000001', '000000001', 'Nguyễn Văn An')], ngay='20261108'),
                  LOA=loa([('A', 'V001', '7202000000001', 5, 1500000)]),
                  QR=qr([['A', '7202000000001', 'Tiệm X', 'HS', '12/03/2026', '']]))
        r = self.client.get(reverse('kh360:ho_so', args=['000000001']))
        self.assertContains(r, 'Thẻ Visa')
        self.assertContains(r, 'V001')
        self.assertContains(r, 'Tiệm X')
        self.assertContains(r, 'Hủy dịch vụ')
        r = self.client.get(reverse('kh360:bien_dong'))
        self.assertContains(r, 'KH mất')
        r = self.client.get(reverse('kh360:bien_dong'), {'xuat': 'excel'})
        self.assertEqual(r['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        r = self.client.get(reverse('kh360:cap_nhat'))
        self.assertEqual(r.status_code, 200)

"""Test Đối chiếu HĐĐT bằng dữ liệu giả (cấu trúc giống file Einvoice / IPCAS GLST30)."""
import io

import openpyxl
from django.test import SimpleTestCase

from . import hddt_doi_chieu as hd
from . import hddt_glcb06 as g

EI_COLS = ['STT', 'Ngày hóa đơn', 'Mẫu số hoá đơn', 'Ký hiệu hoá đơn', 'Số hóa đơn', 'TTV', 'SEQ', 'Mã số thuế người mua',
           'Tên người mua', 'Địa chỉ người mua', 'Mã hàng hóa', 'Tên hàng hóa', 'Đơn vị tính', 'Số lượng', 'Đơn giá',
           'Doanh số bán chưa có thuế', 'Thuế suất GTGT', 'Tiền thuế GTGT', 'Cộng tiền hàng',
           'Tổng doanh số bán chưa có thuế', 'Tổng tiền thuế GTGT', 'Tổng tiền thanh toán', 'Tiền tệ', 'Tỉ giá',
           'Tình trạng hóa đơn', 'User', 'Tình trạng ký', 'Loại nghiệp vụ', 'Loại khách hàng']
IP_COLS = ['user', 'trseq', 'trdate', 'cust', 'taxcode', 'tramt', 'amt', 'slip1', 'item', 'rate', 'remark', 'serino', 'frmid']


class _F(io.BytesIO):
    def __init__(self, data, name):
        super().__init__(data)
        self.name = name


def _einvoice(rows):
    """rows: (TTV, SEQ, thuế, tiền tệ, tỷ giá, tình trạng, ký, loại KH, MST)"""
    wb = openpyxl.Workbook()
    ws = wb.active
    for _ in range(5):
        ws.append(['BẢNG KÊ'])
    ws.append(['﻿' + EI_COLS[0]] + EI_COLS[1:])
    for i, (ttv, seq, thue, tt, tg, ttr, ky, lkh, mst) in enumerate(rows, 1):
        d = dict.fromkeys(EI_COLS, '')
        d.update({'STT': i, 'Số hóa đơn': 100 + i, 'TTV': ttv, 'SEQ': seq, 'Tiền thuế GTGT': thue, 'Tiền tệ': tt,
                  'Tỉ giá': tg, 'Tình trạng hóa đơn': ttr, 'Tình trạng ký': ky, 'Loại khách hàng': lkh,
                  'Mã số thuế người mua': mst, 'Tổng doanh số bán chưa có thuế': thue * 10,
                  'Tổng tiền thuế GTGT': thue, 'Tổng tiền thanh toán': thue * 11, 'Thuế suất GTGT': 10,
                  'Đơn giá': thue * 10, 'Doanh số bán chưa có thuế': thue * 10, 'Cộng tiền hàng': thue * 11,
                  'Loại nghiệp vụ': 'DP', 'Ngày hóa đơn': '05/11/2026'})
        ws.append([d[c] for c in EI_COLS])
    out = io.BytesIO()
    wb.save(out)
    return _F(out.getvalue(), '0511.xlsx')


def _ipcas(rows):
    """rows: (user, trseq, tramt, amt, remark)"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(IP_COLS)
    for u, seq, tramt, amt, remark in rows:
        ws.append([u, seq, '05/11/2026', 'Agribank', '', tramt, amt, '', '', 0, remark, '', ''])
    out = io.BytesIO()
    wb.save(out)
    return _F(out.getvalue(), '0511.xlsx')


class DoiChieuHDDTTests(SimpleTestCase):
    def setUp(self):
        self.ei = hd.doc_einvoice(_einvoice([
            ('GRAA', '1', 100, 'VND', 1, 'Goc', 'DaKy', 'I', ''),       # khớp IPCAS GRAA-1
            ('GRAA', '9', 50, 'VND', 1, 'Goc', 'ChoKy', 'C', ''),       # chưa ký + DN chưa MST
            ('7202CD', '1', 0, 'USD', 1, 'Goc', 'DaKy', 'I', ''),       # sai tỷ giá
        ]))
        self.ip = hd.doc_ipcas(_ipcas([
            ('GRAA', '1', 1000, 100, ''),
            ('GRAA', '2', 3000, 300, ''),          # thiếu HĐ
            ('7202CD', '5', 2000, 200, ''),        # thường niên: không đánh dấu thiếu HĐ (sau 21/07/2022)
            ('7202EI', '7', 93730, 9270, ''),      # kiều hối
            ('7202ATM05', '3', 200, 20, ''),       # ATM không remark → bỏ qua
            ('GRAB', '4', 0, -2_000_000, 'thue dau gia tai san ......'),  # âm lớn → mặc định không gom
        ]))
        self.kq = hd.doi_chieu(self.ei, self.ip)

    def test_tong_hop_theo_user(self):
        th = self.kq['tong_hop'].set_index('user')
        self.assertEqual(th.loc['GRAA', 'einvoice'], 150)
        self.assertEqual(th.loc['GRAA', 'ipcas'], 400)
        self.assertEqual(th.loc['GRAA', 'chenh_lech'], 250)
        self.assertEqual(th.loc['GRAA', 'so_mon_lech'], 1)
        self.assertEqual(th.loc['7202CD', 'so_mon_lech'], 0)
        self.assertEqual(th.loc['7202CD', 'nhom'], 'thuong_nien')
        self.assertEqual(th.loc['7202EI', 'nhom'], 'kieu_hoi')
        q = dict(zip(self.kq['ipcas']['khoa'], self.kq['ipcas']['q']))
        self.assertEqual((q['GRAA2'], q['7202ATM053'], q['7202CD5']), (2, 0, 0))

    def test_loi_hoa_don(self):
        loi = self.kq['loi_hd'].set_index('seq')
        self.assertTrue(loi.loc['9', 'loi_chua_ky'] and loi.loc['9', 'loi_mst'])
        self.assertTrue(loi.loc['1', 'loi_ty_gia'])

    def test_file_import(self):
        self.assertEqual(hd.user_bo_mac_dinh(self.kq), {'GRAB'})
        chinh, rieng, canh_bao = hd.lap_dong_import(self.kq, 134000)
        self.assertEqual([(d[24], d[21]) for d in chinh], [('Phí dịch vụ chuyển tiền', 270), ('Phí thường niên', 200)])
        self.assertTrue(any('tỷ giá' in c for c in canh_bao))      # có kiều hối mà chưa nhập tỷ giá
        chinh, _, canh_bao = hd.lap_dong_import(self.kq, 134000, 25750, rieng=[{
            'loai': 'lai_vay', 'so_tien': 1583562, 'noi_dung': '', 'cif': '123', 'ten_kh': 'DNTN A', 'mst': '01',
            'dia_chi': '', 'so_tk': '', 'loai_kh': 'C', 'file_rieng': True}])
        kh = chinh[-1]
        # Kiều hối: giữ USD + tỷ giá, số tiền ghi giá trị đã quy đổi VND
        self.assertEqual((kh[4], kh[5], kh[20], kh[21]), ('USD', 25750, 93730, 9270))
        self.assertFalse(canh_bao)
        _, rieng, _ = hd.lap_dong_import(self.kq, 134000, 25750, rieng=[{
            'loai': 'lai_vay', 'so_tien': 1583562, 'noi_dung': '', 'cif': '123', 'ten_kh': 'DNTN A', 'mst': '01',
            'dia_chi': '', 'so_tk': '', 'loai_kh': 'C', 'file_rieng': True}])
        ten, dong = rieng[0]
        self.assertEqual((ten, dong[0][24], dong[0][20], dong[0][21], dong[0][30]), ('DNTN A', 'Thu lãi tiền vay', 1583562, 0, -1))
        wb = openpyxl.load_workbook(io.BytesIO(hd.xuat_import(dong)))
        ws = wb['Invoice']
        self.assertEqual(ws['A1'].value, 'GroupId *')
        self.assertEqual(ws['Y4'].value, 'Thu lãi tiền vay')

    def test_xuat_ket_qua(self):
        wb = openpyxl.load_workbook(io.BytesIO(hd.xuat_ket_qua(self.kq, '05112026')))
        self.assertEqual(wb.sheetnames, ['Ipcas', 'Loi Einvoice'])


class DoiChieuGLCB06Tests(SimpleTestCase):
    """Nguồn GLCB06: khớp từng bút toán (user-journal-số tiền-loại tiền-TK), tiền vay, cân đối, import kết hợp."""

    def _glcb06(self, rows):
        import pandas as pd
        cols = list(range(24))
        data = []
        for user, journal, ccy, dr, cr, tk, cust, bucd in rows:
            r = [''] * 24
            r[0], r[2], r[3], r[4], r[5], r[7], r[8], r[10], r[11] = '0900', user, journal, bucd, 'DA', cust, ccy, dr, cr
            r[20] = f'{tk} Ten tai khoan'
            r[23] = 'Phi dich vu'
            data.append(r)
        df = pd.DataFrame(data, columns=cols)
        df.columns = g.COT_GLCB06[:2] + ['user', 'journal'] + g.COT_GLCB06[4:]
        return g.chuan_glcb06(df)

    def setUp(self):
        self.ei = hd.doc_einvoice(_einvoice([
            ('GRAA', '1', 100, 'VND', 1, 'Goc', 'DaKy', 'I', ''),
            ('GRAA', '9', 50, 'VND', 1, 'Goc', 'DaKy', 'I', ''),
        ]))
        self.cb = self._glcb06([
            ('GRAA', '1', 'VND', 0, 100, '453101', '000000001', 'DP'),    # khớp HĐ GRAA-1
            ('GRAA', '2', 'VND', 0, 300, '453101', '000000002', 'DP'),    # thiếu HĐ — KH tổ chức
            ('GRAB', '3', 'VND', 0, 5000, '702001', '000000003', 'LN'),   # thu lãi chưa có HĐ
        ])
        self.kq = g.doi_chieu_glcb06(self.ei, self.cb)

    def test_trang_thai_va_tong_hop(self):
        self.assertEqual(list(self.kq['glcb06']['trang_thai']), ['khop', 'thieu_hd', 'tien_vay'])
        th = self.kq['tong_hop'].set_index('user')
        self.assertEqual((th.loc['GRAA-VND', 'ein_vnd'], th.loc['GRAA-VND', 'ipcas_vnd'], th.loc['GRAA-VND', 'cl_vnd']),
                         (150, 400, 250))
        self.assertEqual(th.loc['GRAB-VND', 'ipcas_vnd'], 5000)
        # HĐ GRAA-9 không có bút toán bên IPCAS
        self.assertEqual(list(self.kq['einvoice'].loc[self.kq['einvoice']['khong_co_ipcas'], 'seq']), ['9'])

    def test_import_ket_hop(self):
        def tra_kh(cif):
            return {'cif': cif, 'ten_kh': 'CTY A', 'mst': '0101', 'dia_chi': 'X', 'so_tk': '', 'loai_kh': 'C'} \
                if cif == '000000002' else None
        dong, _ = g.lap_dong_import_glcb06(self.kq, hd._ngay('05/11/2026'), 150000, che_do='ket_hop', tra_kh=tra_kh)
        tom = sorted((d[24], d[7], d[20], d[21], d[30]) for d in dong)
        self.assertEqual(tom, [('Phí dịch vụ chuyển tiền', 'CTY A', 3000, 300, 10),
                               ('Thu lãi tiền vay', 'Bán cho người tiêu dùng', 5000, 0, -1)])
        dong, _ = g.lap_dong_import_glcb06(self.kq, hd._ngay('05/11/2026'), 150000, che_do='gom', tra_kh=tra_kh)
        self.assertEqual(sorted(d[24] for d in dong), ['Phí dịch vụ chuyển tiền', 'Thu lãi tiền vay'])
        self.assertEqual(next(d for d in dong if d[24] == 'Phí dịch vụ chuyển tiền')[7], 'Bán cho người tiêu dùng')

    def test_import_bo_mon_am_va_quy_doi_ngoai_te(self):
        cb = self._glcb06([
            ('GRAC', '4', 'VND', 0, 200, '453101', '000000004', 'DP'),    # bị đảo bởi bút toán 5
            ('GRAC', '5', 'VND', 200, 0, '453101', '000000004', 'DP'),    # món âm
            ('GRAC', '6', 'VND', 0, 70, '453101', '000000005', 'DP'),
            ('GRAC', '7', 'USD', 0, 1.5, '453101', '000000006', 'DP'),    # ngoại tệ
        ])
        kq = g.doi_chieu_glcb06(self.ei, cb)
        dong, canh_bao = g.lap_dong_import_glcb06(kq, hd._ngay('05/11/2026'), 150000, ty_gia={'USD': 25000})
        tom = sorted((d[4], d[5], d[20], d[21]) for d in dong)
        self.assertEqual(tom, [('USD', 25000, 375000, 37500), ('VND', 1, 700, 70)])
        self.assertTrue(any('1 món âm' in c and '1 món dương' in c for c in canh_bao))

    def test_can_doi(self):
        import pandas as pd
        cb41 = pd.DataFrame({'ccy': ['VND', 'VND'], 'tk': ['453101', '702'], 'ten_tk': ['', ''],
                             'dramt': [0, 0], 'cramt': [400, 5000]})
        cd = g.can_doi(self.kq['einvoice'], cb41).set_index('tk')
        self.assertEqual(cd.loc['453101', 'chenh_lech'], 250)   # 400 trên cân đối − 150 trên HĐ
        self.assertEqual(cd.loc['702', 'chenh_lech'], 5000)

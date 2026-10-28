"""Test Tạo bìa chứng từ: cấp số theo ngày, phân quyền, unique số hồ sơ, import, in PDF."""
import io
import os
import unittest
from datetime import date

import openpyxl
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .bia_chung_tu_views import _format_so, _next_so, _qr_text
from .models import BiaChungTu, BranchConfig, UserProfile

SAMPLE_FILE = os.path.join(settings.BASE_DIR, 'samples', 'FILE THANG 01 DEN THANG 7.2026.xlsx')


def _user(username, branch='HOI_SO', department='KE_TOAN', job='GIAO_DICH_VIEN', position='NHAN_VIEN', ipcas=''):
    u = User.objects.create_user(username, password='x')
    UserProfile.objects.create(user=u, employee_code=username, full_name=username.upper(), branch=branch,
                               department=department, job_function=job, position=position, ipcas_user=ipcas)
    return u


class BiaChungTuTests(TestCase):
    def setUp(self):
        for code in ('HOI_SO', 'PGD_P1'):
            BranchConfig.objects.create(branch_code=code, ten_chi_nhanh='Giá Rai Bạc Liêu',
                                        ten_chi_nhanh_hoa='GIÁ RAI BẠC LIÊU', ma_chi_nhanh='7202')
        self.pp = _user('kien', job='KIEM_SOAT_VIEN', position='PHO_PHONG', ipcas='GRATKIEN')
        self.gdvs = [_user(n, ipcas=f'GRA{n.upper()}') for n in ('a', 'b', 'c', 'd')]
        _user('tindung', department='KHACH_HANG')  # GDV phòng Khách hàng — không được liệt kê
        self.client.force_login(self.pp)

    def _cap_so(self, ngay, so_bat_dau, so_tap):
        data = {'ngay': ngay.isoformat(), 'so_bat_dau': so_bat_dau}
        for u, n in so_tap.items():
            data[f'chk_{u.pk}'] = '1'
            data[f'so_tap_{u.pk}'] = str(n)
        return self.client.post(reverse('bia_chung_tu_cap_so'), data)

    def test_cap_so_vi_du_4_gdv(self):
        a, b, c, d = self.gdvs
        self._cap_so(date(2026, 10, 26), 30, {a: 1, b: 2, c: 1, d: 1})
        rows = list(BiaChungTu.objects.order_by('so_ho_so').values_list('so_ho_so', 'tap_so', 'tong_tap', 'gdv_id', 'user_ipcas'))
        self.assertEqual(rows, [
            ('7202-2026.0030', 1, 5, a.pk, 'GRAA'),
            ('7202-2026.0031', 2, 5, b.pk, 'GRAB'),
            ('7202-2026.0032', 3, 5, b.pk, 'GRAB'),
            ('7202-2026.0033', 4, 5, c.pk, 'GRAC'),
            ('7202-2026.0034', 5, 5, d.pk, 'GRAD'),
        ])
        # Cấp thêm trong cùng ngày: tập đánh tiếp, N cả ngày cập nhật lại
        self._cap_so(date(2026, 10, 26), _next_so('HOI_SO', '7202', 2026), {a: 1})
        self.assertEqual(set(BiaChungTu.objects.values_list('tong_tap', flat=True)), {6})
        self.assertEqual(BiaChungTu.objects.get(so_ho_so='7202-2026.0035').tap_so, 6)

    def test_cap_so_theo_thu_tu_in(self):
        a, b, c, d = self.gdvs
        data = {'ngay': '2026-10-26', 'so_bat_dau': 1}
        for u in (a, b, c, d):
            data[f'chk_{u.pk}'] = '1'
            data[f'so_tap_{u.pk}'] = '1'
        data[f'thu_tu_{c.pk}'] = '1'
        data[f'thu_tu_{a.pk}'] = '2'
        self.client.post(reverse('bia_chung_tu_cap_so'), data)
        # C, A theo thứ tự đã chọn; B, D để trống → mặc định theo họ tên
        self.assertEqual(list(BiaChungTu.objects.order_by('tap_so').values_list('gdv_id', flat=True)),
                         [c.pk, a.pk, b.pk, d.pk])

    def test_thu_tu_in_duoc_nho(self):
        a, b, c, d = self.gdvs
        self.client.post(reverse('bia_chung_tu_cap_so'), {
            'ngay': '2026-10-26', 'so_bat_dau': 1, f'chk_{a.pk}': '1',
            f'thu_tu_{c.pk}': '1', f'thu_tu_{a.pk}': '2'})
        resp = self.client.get(reverse('bia_chung_tu_cap_so'))
        self.assertEqual([(r[0], r[3]) for r in resp.context['gdv_rows']],
                         [(c.pk, 1), (a.pk, 2), (b.pk, None), (d.pk, None)])
        # Xoá trống ô của C → C về mặc định
        self.client.post(reverse('bia_chung_tu_cap_so'), {'ngay': '2026-10-26', f'thu_tu_{a.pk}': '2'})
        resp = self.client.get(reverse('bia_chung_tu_cap_so'))
        self.assertEqual([r[0] for r in resp.context['gdv_rows']], [a.pk, b.pk, c.pk, d.pk])

    def test_cap_so_trung_so_bi_chan(self):
        self._cap_so(date(2026, 10, 26), 30, {self.gdvs[0]: 2})
        self._cap_so(date(2026, 10, 27), 31, {self.gdvs[1]: 1})
        self.assertEqual(BiaChungTu.objects.count(), 2)

    def test_gdv_chua_co_ipcas_bi_chan(self):
        e = _user('e')
        self._cap_so(date(2026, 10, 26), 30, {self.gdvs[0]: 1, e: 1})
        self.assertEqual(BiaChungTu.objects.count(), 0)

    def test_danh_sach_gdv_chi_phong_ke_toan(self):
        resp = self.client.get(reverse('bia_chung_tu_cap_so'))
        self.assertNotContains(resp, 'TINDUNG')
        self.assertEqual([r[1] for r in resp.context['gdv_rows']], ['A', 'B', 'C', 'D'])
        self.assertEqual(resp.context['so_bat_dau'], '')  # không điền sẵn, chỉ gợi ý
        self.assertEqual(resp.context['so_goi_y'], 1)

    def test_gdv_khong_duoc_vao(self):
        self.client.force_login(self.gdvs[0])
        self.assertRedirects(self.client.get(reverse('bia_chung_tu_list')), reverse('dashboard'), fetch_redirect_response=False)

    def test_sua_trung_so_ho_so_bi_chan(self):
        self._cap_so(date(2026, 10, 26), 30, {self.gdvs[0]: 2})
        bia = BiaChungTu.objects.get(so_ho_so='7202-2026.0031')
        self.client.post(reverse('bia_chung_tu_edit', args=[bia.pk]), {
            'so_ho_so': '7202-2026.0030', 'ngay_chung_tu': '2026-10-26', 'tap_so': 2, 'tong_tap': 2,
            'so_to': 3, 'user_ipcas': 'GRATKIEN'})
        bia.refresh_from_db()
        self.assertEqual(bia.so_ho_so, '7202-2026.0031')

    def test_pgd_danh_so_rieng(self):
        BiaChungTu.objects.create(branch='HOI_SO', so_ho_so='7202-2026.0100', ngay_chung_tu=date(2026, 1, 2), user_ipcas='X')
        self.assertEqual(_next_so('HOI_SO', '7202', 2026), 101)
        self.assertEqual(_next_so('PGD_P1', '7202', 2026), 1)
        self.assertEqual(_next_so('HOI_SO', '7202', 2027), 1)
        # PGD có hậu tố riêng: 7202LT-2026.NNNN / 7202P1-2026.NNNN
        self.assertEqual(_format_so('PGD_LANG_TRON', '7202', 2026, 5), '7202LT-2026.0005')
        self.assertEqual(_format_so('PGD_P1', '7202', 2026, 12), '7202P1-2026.0012')
        self.assertEqual(_format_so('HOI_SO', '7202', 2026, 30), '7202-2026.0030')
        BiaChungTu.objects.create(branch='PGD_P1', so_ho_so='7202P1-2026.0007', ngay_chung_tu=date(2026, 1, 2), user_ipcas='X')
        self.assertEqual(_next_so('PGD_P1', '7202', 2026), 8)

    def test_in_pdf_va_qr(self):
        self._cap_so(date(2026, 9, 14), 8, {self.gdvs[0]: 1})
        bia = BiaChungTu.objects.get()
        self.assertEqual(_qr_text(bia, '7202'), '7202-GRAA-14/09/2026-1/1-7202-2026.0008')
        resp = self.client.post(reverse('bia_chung_tu_print'), {'ids': [bia.pk], f'so_to_{bia.pk}': '7'})
        self.assertEqual(resp['Content-Type'], 'application/pdf')
        self.assertTrue(resp.content.startswith(b'%PDF'))
        self.assertIn(b'/Count 2', resp.content)  # 1 bìa = trang bìa + trang nhãn QR
        bia.refresh_from_db()
        self.assertIsNotNone(bia.ngay_in)
        self.assertEqual(bia.so_to, 7)

    def test_nhan_qr_hau_kiem_va_nguoi_dong(self):
        import fitz
        hkv = _user('hkv', branch='PGD_P1', job='HAU_KIEM_VIEN')  # role chung, khác đơn vị vẫn in
        self._cap_so(date(2026, 9, 14), 8, {self.gdvs[0]: 1})
        bia = BiaChungTu.objects.get()

        def text_trang_2():
            pdf = self.client.get(reverse('bia_chung_tu_print') + f'?id={bia.pk}').content
            return fitz.open(stream=pdf, filetype='pdf')[1].get_text()

        t = text_trang_2()
        self.assertIn('Người hậu kiểm chứng từ: HKV', t)
        self.assertIn('Người đóng chứng từ: A', t)  # GDV của tập
        # Đổi Hậu kiểm viên → bìa in sau mang tên người mới
        hkv.profile.job_function = 'GIAO_DICH_VIEN'
        hkv.profile.save()
        UserProfile.objects.filter(user=self.gdvs[1]).update(job_function='HAU_KIEM_VIEN')
        self.assertIn('Người hậu kiểm chứng từ: B', text_trang_2())

    def test_tai_huong_dan(self):
        resp = self.client.get(reverse('bia_chung_tu_huong_dan'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('attachment', resp['Content-Disposition'])
        self.assertTrue(b''.join(resp.streaming_content).startswith(b'PK'))  # .docx = zip

    def _import_sample(self):
        with open(SAMPLE_FILE, 'rb') as f:
            resp = self.client.post(reverse('bia_chung_tu_import'), {'file': SimpleUploadedFile('x.xlsx', f.read())})
        self.client.post(reverse('bia_chung_tu_import_confirm'))
        return resp.context['rows']

    @unittest.skipUnless(os.path.exists(SAMPLE_FILE), 'Thiếu file mẫu')
    def test_import_file_thang_01_07(self):
        for n in ('GRACACHI', 'GRANSINH', 'GRATHIEU', 'GRATNNHI'):
            _user(n.lower(), ipcas=n)
        rows = self._import_sample()
        self.assertEqual(len(rows), 668)  # bỏ 8 dòng cuối không có tiêu đề
        loi = [r['so_ho_so'] for r in rows if r['loi']]
        self.assertEqual(loi, ['7202-2026.0229', '7202-2026.0229'])
        self.assertEqual(BiaChungTu.objects.count(), 666)
        b = BiaChungTu.objects.get(so_ho_so='7202-2026.0001')
        self.assertEqual((b.ngay_chung_tu, b.tap_so, b.tong_tap, b.so_to, b.don_vi),
                         (date(2026, 1, 5), 1, 5, 1, 'Quyển'))
        # Cột User → QR + GDV; Số tờ của tập "…." → trống; 2 tập của GRANSINH = 2 dòng
        self.assertEqual((b.user_ipcas, b.gdv.username, b.so_to_tap), ('GRACACHI', 'gracachi', None))
        self.assertEqual(list(BiaChungTu.objects.filter(user_ipcas='GRANSINH').order_by('so_ho_so')
                              .values_list('so_ho_so', 'so_to_tap')),
                         [('7202-2026.0002', 250), ('7202-2026.0003', 277)])
        # Dòng không có User → UserIPCAS của người import
        self.assertEqual(BiaChungTu.objects.get(so_ho_so='7202-2026.0010').user_ipcas, 'GRATKIEN')
        resp = self.client.get(reverse('bia_chung_tu_list') + '?tu_ngay=02/04/2026&den_ngay=02/04/2026')
        self.assertIn(date(2026, 4, 2), resp.context['lech'])

    @unittest.skipUnless(os.path.exists(SAMPLE_FILE), 'Thiếu file mẫu')
    def test_import_lai_cap_nhat_bia_da_co(self):
        for n in ('GRACACHI', 'GRANSINH', 'GRATHIEU', 'GRATNNHI'):
            _user(n.lower(), ipcas=n)
        BiaChungTu.objects.create(branch='HOI_SO', so_ho_so='7202-2026.0005', ngay_chung_tu=date(2026, 1, 5),
                                  tap_so=5, tong_tap=5, so_to=3, user_ipcas='GRATKIEN')
        rows = self._import_sample()
        self.assertEqual(next(r for r in rows if r['so_ho_so'] == '7202-2026.0005')['hanh_dong'], 'Cập nhật')
        b = BiaChungTu.objects.get(so_ho_so='7202-2026.0005')
        self.assertEqual((b.user_ipcas, b.gdv.username, b.so_to_tap, b.so_to), ('GRATNNHI', 'gratnnhi', 300, 3))

    def test_import_user_khong_ton_tai_bao_loi(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['Số hồ sơ', 'Tiêu đề hồ sơ', 'User', 'Số tờ của tập chứng từ'])
        ws.append(['7202-2026.0001', 'Nhật ký chứng từ ngày 05/01/2026 - Tập 1/1', 'GRAXXX', 10])
        buf = io.BytesIO()
        wb.save(buf)
        resp = self.client.post(reverse('bia_chung_tu_import'), {'file': SimpleUploadedFile('x.xlsx', buf.getvalue())})
        self.assertIn('GRAXXX', resp.context['rows'][0]['loi'])

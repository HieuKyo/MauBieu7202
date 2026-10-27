"""Test Tạo bìa chứng từ: cấp số theo ngày, phân quyền, unique số hồ sơ, import, in PDF."""
import os
import unittest
from datetime import date

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .bia_chung_tu_views import _next_so, _qr_text
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
        self.assertEqual([n for _, n, _ in resp.context['gdv_rows']], ['A', 'B', 'C', 'D'])

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

    def test_in_pdf_va_qr(self):
        self._cap_so(date(2026, 9, 14), 8, {self.gdvs[0]: 1})
        bia = BiaChungTu.objects.get()
        self.assertEqual(_qr_text(bia, '7202'), '7202-GRAA-14/09/2026-1/1-7202-2026.0008')
        resp = self.client.post(reverse('bia_chung_tu_print'), {'ids': [bia.pk], f'so_to_{bia.pk}': '7'})
        self.assertEqual(resp['Content-Type'], 'application/pdf')
        self.assertTrue(resp.content.startswith(b'%PDF'))
        bia.refresh_from_db()
        self.assertIsNotNone(bia.ngay_in)
        self.assertEqual(bia.so_to, 7)

    @unittest.skipUnless(os.path.exists(SAMPLE_FILE), 'Thiếu file mẫu')
    def test_import_file_thang_01_07(self):
        with open(SAMPLE_FILE, 'rb') as f:
            resp = self.client.post(reverse('bia_chung_tu_import'), {'file': SimpleUploadedFile('x.xlsx', f.read())})
        rows = resp.context['rows']
        self.assertEqual(len(rows), 668)  # bỏ 8 dòng cuối không có tiêu đề
        loi = [r['so_ho_so'] for r in rows if r['loi']]
        self.assertEqual(loi, ['7202-2026.0229', '7202-2026.0229'])
        self.client.post(reverse('bia_chung_tu_import_confirm'))
        self.assertEqual(BiaChungTu.objects.count(), 666)
        b = BiaChungTu.objects.get(so_ho_so='7202-2026.0001')
        self.assertEqual((b.ngay_chung_tu, b.tap_so, b.tong_tap, b.so_to, b.don_vi, b.user_ipcas),
                         (date(2026, 1, 5), 1, 5, 1, 'Quyển', 'GRATKIEN'))
        resp = self.client.get(reverse('bia_chung_tu_list') + '?tu_ngay=02/04/2026&den_ngay=02/04/2026')
        self.assertIn(date(2026, 4, 2), resp.context['lech'])

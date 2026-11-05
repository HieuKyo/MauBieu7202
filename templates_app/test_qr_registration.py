"""Test Đăng ký bảng QR / Loa Thần tài: admin xem toàn bộ, đánh dấu đã in, bộ đếm."""
import io
import json
from datetime import datetime, timedelta

import openpyxl
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import QRRegistration


class QRDaInTests(TestCase):
    def setUp(self):
        self.nv1 = User.objects.create_user('nv1', password='x')
        self.nv2 = User.objects.create_user('nv2', password='x')
        self.admin = User.objects.create_superuser('ad', password='x')
        self.reg = QRRegistration.objects.create(
            user_dk=self.nv1, ten_kh='Khach Mot', so_tai_khoan='0012', phong_giao_dich='PGD A')
        self.reg2 = QRRegistration.objects.create(
            user_dk=self.nv2, ten_kh='Khach Hai', so_tai_khoan='0034', phong_giao_dich='PGD B')

    def _da_in(self, reg, value='1'):
        return self.client.post(reverse('qr_registration_mark_printed', args=[reg.pk]), {'da_in': value})

    def test_ban_ghi_moi_chua_in(self):
        self.client.force_login(self.nv1)
        self.client.post(reverse('qr_registration_create'), {'ten_kh': 'B', 'so_tai_khoan': '9'})
        self.assertFalse(QRRegistration.objects.get(ten_kh='B').da_in)

    def test_admin_thay_tat_ca_cac_phong_nhan_vien_chi_thay_cua_minh(self):
        self.client.force_login(self.admin)
        r = self.client.get(reverse('qr_registration_list'))
        self.assertContains(r, 'Khach Mot')
        self.assertContains(r, 'Khach Hai')
        self.client.force_login(self.nv1)
        r = self.client.get(reverse('qr_registration_list'))
        self.assertContains(r, 'Khach Mot')
        self.assertNotContains(r, 'Khach Hai')

    def test_nhan_vien_khong_danh_dau_duoc(self):
        self.client.force_login(self.nv1)
        self.assertEqual(self._da_in(self.reg).status_code, 403)
        self.reg.refresh_from_db()
        self.assertFalse(self.reg.da_in)
        r = self.client.get(reverse('qr_registration_list'))
        self.assertContains(r, 'disabled>')
        self.assertNotContains(r, f'onchange="toggleDaIn({self.reg.pk}')

    def test_admin_tich_ngay_khong_can_gui_duyet_va_bo_tich(self):
        self.client.force_login(self.admin)
        r = self._da_in(self.reg)
        self.assertIn('ad — ', r.json()['thong_tin_in'])
        self.reg.refresh_from_db()
        self.assertTrue(self.reg.da_in)
        self.assertEqual(self.reg.nguoi_in, 'ad')
        self.assertIsNotNone(self.reg.ngay_in)

        # Người đăng ký thấy ô đã tích và người đánh dấu
        self.client.force_login(self.nv1)
        r = self.client.get(reverse('qr_registration_list'))
        self.assertContains(r, 'checked')
        self.assertContains(r, 'ad — ')

        self.client.force_login(self.admin)
        self._da_in(self.reg, '0')
        self.reg.refresh_from_db()
        self.assertFalse(self.reg.da_in)
        self.assertEqual(self.reg.nguoi_in, '')
        self.assertIsNone(self.reg.ngay_in)

    def test_da_in_thi_nhan_vien_khong_sua_xoa_duoc(self):
        self.reg.da_in = True
        self.reg.save()
        self.client.force_login(self.nv1)
        data = {'ten_kh': 'Doi', 'so_tai_khoan': '1'}
        self.assertEqual(self.client.post(reverse('qr_registration_update', args=[self.reg.pk]), data).status_code, 403)
        self.assertEqual(self.client.post(reverse('qr_registration_delete', args=[self.reg.pk])).status_code, 403)
        self.assertNotContains(self.client.get(reverse('qr_registration_list')), f'openDeleteModal({self.reg.pk},')

        self.client.force_login(self.admin)
        self.assertEqual(self.client.post(reverse('qr_registration_update', args=[self.reg.pk]), data).status_code, 200)

    def test_loc_da_in_va_xuat_file(self):
        self.client.force_login(self.admin)
        self._da_in(self.reg)
        r = self.client.get(reverse('qr_registration_list'), {'da_in': '1'})
        self.assertContains(r, 'Khach Mot')
        self.assertNotContains(r, 'Khach Hai')
        r = self.client.get(reverse('qr_registration_list'), {'da_in': '0'})
        self.assertNotContains(r, 'Khach Mot')
        self.assertContains(r, 'Khach Hai')

        r = self.client.get(reverse('qr_registration_export'), {'da_in': '1'})
        ws = openpyxl.load_workbook(io.BytesIO(r.content)).active
        self.assertEqual(ws.max_row, 2)
        self.assertEqual(ws.cell(row=1, column=8).value, 'Trạng thái')
        self.assertEqual(ws.cell(row=2, column=8).value, 'Đã in')


class QRBoDemTests(TestCase):
    def setUp(self):
        self.nv = User.objects.create_user('nv', password='x')
        self.client.force_login(self.nv)

    def _tao(self, ngay, loai=QRRegistration.LOAI_QR, **them):
        reg = QRRegistration.objects.create(user_dk=self.nv, ten_kh='K', so_tai_khoan='1', loai=loai, **them)
        QRRegistration.objects.filter(pk=reg.pk).update(ngay_dang_ky=ngay)

    def test_dashboard_dem_thang_nam_va_bieu_do_12_thang(self):
        tz = timezone.get_current_timezone()
        self._tao(datetime(2026, 3, 10, 9, 0, tzinfo=tz))
        self._tao(datetime(2026, 3, 11, 9, 0, tzinfo=tz), da_in=True)
        self._tao(datetime(2026, 7, 2, 9, 0, tzinfo=tz))
        self._tao(datetime(2026, 7, 3, 9, 0, tzinfo=tz), loai=QRRegistration.LOAI_LOA)
        self._tao(datetime(2025, 12, 31, 9, 0, tzinfo=tz))

        r = self.client.get(reverse('qr_dashboard'), {'thang': '2026-03'})
        # Đếm số đã đăng ký: bản ghi chưa in cũng được tính
        self.assertEqual((r.context['tong_qr'], r.context['tong_loa']), (2, 0))
        self.assertEqual((r.context['tong_qr_nam'], r.context['tong_loa_nam']), (3, 1))
        self.assertEqual(json.loads(r.context['chart_thang_qr_json']), [0, 0, 2, 0, 0, 0, 1, 0, 0, 0, 0, 0])
        self.assertEqual(json.loads(r.context['chart_thang_loa_json']), [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0])
        self.assertContains(r, 'chartByMonth')

    def test_dau_thang_tinh_theo_gio_viet_nam(self):
        # 00:30 ngày 01/07 giờ VN vẫn là 30/06 theo giờ UTC
        self._tao(datetime(2026, 7, 1, 0, 30, tzinfo=timezone.get_current_timezone()))
        r = self.client.get(reverse('qr_dashboard'), {'thang': '2026-07'})
        self.assertEqual(json.loads(r.context['chart_labels_json']), ['01/07'])
        self.assertEqual(json.loads(r.context['chart_thang_qr_json'])[6], 1)

    def test_trang_dang_ky_dem_thang_va_nam_hien_tai(self):
        now = timezone.now()
        self._tao(now)
        self._tao(now - timedelta(days=366))
        r = self.client.get(reverse('qr_registration_list'))
        self.assertEqual((r.context['tong_qr_thang'], r.context['tong_qr_nam']), (1, 1))


class LoaThanTaiTests(TestCase):
    LOA = {'loai': 'loa', 'so_tai_khoan': '0056', 'ten_kh': 'Khach Loa', 'dia_chi': 'Khom 1', 'so_dien_thoai': '0912345678'}

    def setUp(self):
        self.nv = User.objects.create_user('nv', password='x')
        self.admin = User.objects.create_superuser('ad', password='x')
        self.client.force_login(self.nv)

    def _tao_loa(self, **them):
        return self.client.post(reverse('qr_registration_create'), {**self.LOA, **them})

    def test_tao_loa_luu_dia_chi_sdt_khong_dien_ten_cua_hang(self):
        self.assertTrue(self._tao_loa().json()['success'])
        reg = QRRegistration.objects.get()
        self.assertEqual(reg.loai, QRRegistration.LOAI_LOA)
        self.assertEqual((reg.dia_chi, reg.so_dien_thoai, reg.ten_cua_hang), ('Khom 1', '0912345678', ''))
        self.assertFalse(reg.da_in)

    def test_loa_bat_buoc_dia_chi_va_sdt(self):
        self.assertEqual(self._tao_loa(dia_chi='').status_code, 400)
        self.assertEqual(self._tao_loa(so_dien_thoai=' ').status_code, 400)
        self.assertFalse(QRRegistration.objects.exists())

    def test_qr_khong_can_dia_chi_va_mac_dinh_la_qr(self):
        self.client.post(reverse('qr_registration_create'), {'ten_kh': 'Q', 'so_tai_khoan': '1'})
        self.assertEqual(QRRegistration.objects.get().loai, QRRegistration.LOAI_QR)

    def test_sua_loa_giu_nguyen_loai_va_doi_dia_chi(self):
        self._tao_loa()
        reg = QRRegistration.objects.get()
        data = {'ten_kh': 'Moi', 'so_tai_khoan': '2', 'dia_chi': 'Khom 2', 'so_dien_thoai': '0900000000', 'loai': 'qr'}
        self.assertEqual(self.client.post(reverse('qr_registration_update', args=[reg.pk]), data).status_code, 200)
        reg.refresh_from_db()
        self.assertEqual((reg.loai, reg.dia_chi, reg.ten_cua_hang), (QRRegistration.LOAI_LOA, 'Khom 2', ''))
        data['dia_chi'] = ''
        self.assertEqual(self.client.post(reverse('qr_registration_update', args=[reg.pk]), data).status_code, 400)

    def test_danh_dau_da_in_nhu_qr(self):
        self._tao_loa()
        reg = QRRegistration.objects.get()
        self.client.force_login(self.admin)
        self.client.post(reverse('qr_registration_mark_printed', args=[reg.pk]), {'da_in': '1'})
        reg.refresh_from_db()
        self.assertTrue(reg.da_in)

    def test_loc_loai_dem_rieng_va_xuat_file(self):
        self._tao_loa()
        self.client.post(reverse('qr_registration_create'), {'ten_kh': 'Khach QR', 'so_tai_khoan': '1'})
        self.client.force_login(self.admin)
        r = self.client.get(reverse('qr_registration_list'), {'loai': 'loa'})
        self.assertContains(r, 'Khach Loa')
        self.assertNotContains(r, 'Khach QR')
        self.assertEqual((r.context['tong_qr_nam'], r.context['tong_loa_nam']), (1, 1))

        r = self.client.get(reverse('qr_registration_export'), {'loai': 'loa'})
        ws = openpyxl.load_workbook(io.BytesIO(r.content)).active
        self.assertEqual(ws.max_row, 2)
        self.assertEqual([ws.cell(row=2, column=c).value for c in (9, 10, 11)], ['Loa Thần tài', 'Khom 1', '0912345678'])

    def test_dashboard_thong_ke_rieng_tung_loai(self):
        self._tao_loa()
        self._tao_loa()
        self.client.post(reverse('qr_registration_create'), {'ten_kh': 'Q', 'so_tai_khoan': '1', 'ten_can_bo': 'CB'})
        r = self.client.get(reverse('qr_dashboard'))
        self.assertContains(r, 'DASHBOARD QR / LOA THẦN TÀI')
        self.assertEqual((r.context['tong_qr'], r.context['tong_loa']), (1, 2))
        self.assertEqual(sum(x['so_luong'] for x in r.context['by_can_bo']), 3)
        self.assertEqual(sum(x['loa'] for x in r.context['by_can_bo']), 2)

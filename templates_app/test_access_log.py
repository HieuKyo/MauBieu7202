from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from .models import MenuAccessLog

HTML = {'HTTP_ACCEPT': 'text/html,application/xhtml+xml'}


class MenuAccessLogTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', password='x')
        self.nv = User.objects.create_user('nv', password='x')

    def test_ghi_luot_mo_trang(self):
        self.client.force_login(self.nv)
        self.client.get('/ghi-chu-cap-nhat/', **HTML)
        log = MenuAccessLog.objects.get()
        self.assertEqual((log.user, log.view_name, log.path), (self.nv, 'ghi_chu_cap_nhat', '/ghi-chu-cap-nhat/'))

    def test_khong_ghi_fetch_nen_va_chua_dang_nhap(self):
        self.client.get('/ghi-chu-cap-nhat/', **HTML)                 # chưa đăng nhập → chuyển trang login
        self.client.force_login(self.nv)
        self.client.get('/ghi-chu-cap-nhat/', HTTP_ACCEPT='*/*')     # fetch() nền
        self.client.post('/ghi-chu-cap-nhat/', **HTML)
        self.assertEqual(MenuAccessLog.objects.count(), 0)

    def test_chi_superuser_xem_thong_ke(self):
        self.client.force_login(self.nv)
        self.assertEqual(self.client.get('/thong-ke-truy-cap/').status_code, 302)

    def test_thong_ke_theo_ngay_tuan_thang(self):
        now = timezone.now()
        for days_ago in (0, 0, 1, 40):
            log = MenuAccessLog.objects.create(user=self.nv, view_name='ghi_chu_cap_nhat', path='/ghi-chu-cap-nhat/')
            MenuAccessLog.objects.filter(pk=log.pk).update(accessed_at=now - timedelta(days=days_ago))
        old = MenuAccessLog.objects.create(user=self.nv, view_name='x', path='/x/')
        MenuAccessLog.objects.filter(pk=old.pk).update(accessed_at=now - timedelta(days=500))

        self.client.force_login(self.admin)
        r = self.client.get('/thong-ke-truy-cap/?ky=ngay&so_ky=7')
        row = next(t for t in r.context['trang'] if t['view_name'] == 'ghi_chu_cap_nhat')
        self.assertEqual(row['luot'][-1], 2)          # hôm nay
        self.assertEqual(row['luot'][-2], 1)          # hôm qua
        self.assertEqual(row['url'], '/ghi-chu-cap-nhat/')
        self.assertFalse(MenuAccessLog.objects.filter(view_name='x').exists())   # quá hạn lưu → đã xóa

        r = self.client.get('/thong-ke-truy-cap/?ky=thang&so_ky=3')
        row = next(t for t in r.context['trang'] if t['view_name'] == 'ghi_chu_cap_nhat')
        self.assertEqual(row['tong'], 4)
        self.assertEqual(sum(row['luot']), 4)

        r = self.client.get(f'/thong-ke-truy-cap/?ky=tuan&so_ky=12&user={self.admin.id}')
        self.assertEqual(r.context['trang'], [])

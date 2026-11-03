"""Test Ghi chú cập nhật: đọc docs/GHI_CHU_CAP_NHAT.md, mọi người dùng xem được."""
import importlib.util
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .changelog_views import _parse

MD = """# Ghi chú cập nhật

Giới thiệu.

## Bản tiếp theo

### Chức năng mới
- **Mới** <script>

## 2026.11.03 — 03/11/2026

### Chỉnh sửa
- **Bìa:**
  - dòng con `x.py`
"""


class GhiChuCapNhatTests(TestCase):
    def test_parse(self):
        ban = _parse(MD)
        self.assertEqual([b['phien_ban'] for b in ban], ['Bản', '2026.11.03'])
        self.assertEqual(ban[0]['muc'][0]['dong'], [(0, '<strong>Mới</strong> &lt;script&gt;')])
        self.assertEqual(ban[1]['muc'][0]['dong'][1], (1, 'dòng con <code>x.py</code>'))

    def test_nguoi_dung_thuong_xem_duoc(self):
        self.client.force_login(User.objects.create_user('nv', password='x'))
        with mock.patch('templates_app.changelog_views.APP_VERSION', '2026.10.30'):
            resp = self.client.get(reverse('ghi_chu_cap_nhat'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Phiên bản 2026.10.30')
        self.assertContains(resp, 'Máy đang chạy bản này', count=1)

    def test_dong_goi_ghi_phien_ban(self):
        path = settings.BASE_DIR / 'scripts' / 'release' / 'build_update.py'
        spec = importlib.util.spec_from_file_location('build_update', path)
        build = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build)
        out = build.dat_phien_ban_ghi_chu(MD, '2026.11.04')
        self.assertIn('## 2026.11.04 — ', out)
        self.assertNotIn('Bản tiếp theo', out)

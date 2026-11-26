"""Test Chứng từ → Giao/Nhận chứng từ: luồng GDV → KSV → GDV (GĐ ký) → Hậu kiểm, quyền, lịch sử."""
from datetime import date

from django.test import TestCase
from django.urls import reverse

from .models import BiaChungTu, BiaGiaoNhanLog, BranchConfig
from .test_bia_chung_tu import _user


class BiaGiaoNhanTests(TestCase):
    def setUp(self):
        BranchConfig.objects.create(branch_code='HOI_SO', ten_chi_nhanh='Giá Rai Bạc Liêu',
                                    ten_chi_nhanh_hoa='GIÁ RAI BẠC LIÊU', ma_chi_nhanh='7202')
        self.ksv = _user('ksv', job='KIEM_SOAT_VIEN', position='PHO_PHONG', ipcas='GRAKSV')
        self.gdv = _user('gdv', ipcas='GRAGDV')
        self.gdv2 = _user('gdv2', ipcas='GRAGDV2')
        self.hk = _user('hk', job='HAU_KIEM_VIEN')
        self.client.force_login(self.ksv)
        self.client.post(reverse('bia_chung_tu_cap_so'), {
            'ngay': date(2026, 11, 26).isoformat(), 'so_bat_dau': 1,
            f'chk_{self.gdv.pk}': '1', f'so_tap_{self.gdv.pk}': '2',
            f'chk_{self.gdv2.pk}': '1', f'so_tap_{self.gdv2.pk}': '1',
        })
        self.bias = list(BiaChungTu.objects.filter(gdv=self.gdv).order_by('so_ho_so'))
        self.bia2 = BiaChungTu.objects.get(gdv=self.gdv2)

    def _xu_ly(self, user, hanh_dong, bias, **extra):
        self.client.force_login(user)
        return self.client.post(reverse('bia_chung_tu_giao_nhan_xu_ly'),
                                {'hanh_dong': hanh_dong, 'ids': [b.pk for b in bias], **extra})

    def _tt(self, bia):
        bia.refresh_from_db()
        return bia.trang_thai_gn

    def test_bia_moi_vao_luong_bia_import_khong(self):
        self.assertEqual({self._tt(b) for b in self.bias}, {'gdv_giu'})

    def test_luong_day_du(self):
        b1, b2 = self.bias
        self._xu_ly(self.gdv, 'giao_ksv', [b1, b2], nguoi_nhan_ksv=self.ksv.pk)
        self.assertEqual(self._tt(b1), 'cho_ksv_nhan')
        self.assertEqual(b1.nguoi_xu_ly, self.ksv)
        self._xu_ly(self.ksv, 'ksv_nhan', [b1, b2])
        self.assertEqual(self._tt(b1), 'ksv_dang_ky')
        self._xu_ly(self.ksv, 'ksv_ky', [b1, b2])
        self.assertEqual(self._tt(b1), 'cho_gd_ky')
        self.assertIsNone(b1.nguoi_xu_ly)
        # Trang GDV hiện trạng thái "KSV trả chứng từ chờ GĐ ký"
        self.client.force_login(self.gdv)
        self.assertContains(self.client.get(reverse('bia_chung_tu_giao_nhan') + '?tab=cua_toi'), 'KSV trả chứng từ chờ GĐ ký')
        self._xu_ly(self.gdv, 'giao_hk', [b1, b2], nguoi_nhan_hk=self.hk.pk)
        self.assertEqual(self._tt(b1), 'cho_hk_nhan')
        self._xu_ly(self.hk, 'hk_nhan', [b1, b2])
        self.assertEqual(self._tt(b1), 'hk_da_nhan')
        self.assertEqual(b1.nguoi_xu_ly, self.hk)
        ls = list(BiaGiaoNhanLog.objects.filter(bia=b1).values_list('den_trang_thai', 'nguoi_thuc_hien__username'))
        self.assertEqual(ls, [('cho_ksv_nhan', 'gdv'), ('ksv_dang_ky', 'ksv'), ('cho_gd_ky', 'ksv'),
                              ('cho_hk_nhan', 'gdv'), ('hk_da_nhan', 'hk')])
        # Tra cứu hiện lịch sử
        self.client.force_login(self.ksv)
        self.assertContains(self.client.get(reverse('bia_chung_tu_giao_nhan') + '?tab=tra_cuu'), 'Hậu kiểm xác nhận đã nhận')

    def test_khong_dung_nguoi_hoac_trang_thai_bi_bo_qua(self):
        b1 = self.bias[0]
        # GDV khác không giao được tập của người khác
        self._xu_ly(self.gdv2, 'giao_ksv', [b1], nguoi_nhan_ksv=self.ksv.pk)
        self.assertEqual(self._tt(b1), 'gdv_giu')
        # Chọn người nhận không phải KSV → từ chối
        self._xu_ly(self.gdv, 'giao_ksv', [b1], nguoi_nhan_ksv=self.gdv2.pk)
        self.assertEqual(self._tt(b1), 'gdv_giu')
        # KSV chưa được giao thì không ký được
        self._xu_ly(self.ksv, 'ksv_ky', [b1])
        self.assertEqual(self._tt(b1), 'gdv_giu')
        # Hậu kiểm không nhận được tập đang ở KSV
        self._xu_ly(self.gdv, 'giao_ksv', [b1], nguoi_nhan_ksv=self.ksv.pk)
        self._xu_ly(self.hk, 'hk_nhan', [b1])
        self.assertEqual(self._tt(b1), 'cho_ksv_nhan')

    def test_tra_lai_can_ly_do_va_thu_hoi(self):
        b1 = self.bias[0]
        self._xu_ly(self.gdv, 'giao_ksv', [b1], nguoi_nhan_ksv=self.ksv.pk)
        self._xu_ly(self.ksv, 'ksv_tra', [b1])
        self.assertEqual(self._tt(b1), 'cho_ksv_nhan')  # thiếu lý do
        self._xu_ly(self.ksv, 'ksv_tra', [b1], ly_do='Thiếu chứng từ')
        self.assertEqual(self._tt(b1), 'gdv_giu')
        self.assertEqual(BiaGiaoNhanLog.objects.filter(bia=b1).last().ghi_chu, 'Thiếu chứng từ')
        self._xu_ly(self.gdv, 'giao_ksv', [b1], nguoi_nhan_ksv=self.ksv.pk)
        self._xu_ly(self.gdv, 'thu_hoi', [b1])
        self.assertEqual(self._tt(b1), 'gdv_giu')

    def test_quyen_xem_tra_cuu(self):
        self.client.force_login(self.gdv2)
        resp = self.client.get(reverse('bia_chung_tu_giao_nhan') + '?tab=tra_cuu')
        self.assertEqual([b.pk for b in resp.context['bias']], [self.bia2.pk])  # GDV chỉ thấy tập của mình
        self.client.force_login(self.hk)
        resp = self.client.get(reverse('bia_chung_tu_giao_nhan') + '?tab=tra_cuu')
        self.assertEqual(len(resp.context['bias']), 3)
        # GDV không có tab Tạo bìa
        self.client.force_login(self.gdv)
        self.assertNotContains(self.client.get(reverse('bia_chung_tu_giao_nhan')), 'Tạo bìa chứng từ')

    def test_pho_phong_kiem_hau_kiem_cap_so_gdv_thay_tap(self):
        # Phó phòng KT&NQ đồng thời là Hậu kiểm viên (như PGD Phường 1) cấp số → GDV thấy tập để giao KSV
        pp_hk = _user('pphk', job='HAU_KIEM_VIEN', position='PHO_PHONG', ipcas='GRAPPHK')
        self.client.force_login(pp_hk)
        self.client.post(reverse('bia_chung_tu_cap_so'), {
            'ngay': date(2026, 11, 27).isoformat(), 'so_bat_dau': 50,
            f'chk_{self.gdv2.pk}': '1', f'so_tap_{self.gdv2.pk}': '1',
        })
        moi = BiaChungTu.objects.get(so_ho_so='7202-2026.0050')
        self.assertEqual((moi.gdv, moi.trang_thai_gn), (self.gdv2, 'gdv_giu'))
        self.client.force_login(self.gdv2)
        resp = self.client.get(reverse('bia_chung_tu_giao_nhan') + '?tab=cua_toi')
        self.assertIn(moi.pk, [b.pk for b in resp.context['bias']])

    def test_dua_bia_cu_vao_giao_nhan(self):
        BiaChungTu.objects.filter(pk=self.bia2.pk).update(trang_thai_gn='')  # bìa cũ: không theo dõi
        self.client.force_login(self.gdv2)
        self.assertEqual(list(self.client.get(reverse('bia_chung_tu_giao_nhan') + '?tab=cua_toi').context['bias']), [])
        self.client.force_login(self.gdv2)  # GDV không tự đưa vào được
        self.client.post(reverse('bia_chung_tu_dua_vao_gn'), {'ids': [self.bia2.pk]})
        self.assertEqual(self._tt(self.bia2), '')
        self.client.force_login(self.ksv)
        self.client.post(reverse('bia_chung_tu_dua_vao_gn'), {'ids': [self.bia2.pk]})
        self.assertEqual(self._tt(self.bia2), 'gdv_giu')
        self.client.force_login(self.gdv2)
        resp = self.client.get(reverse('bia_chung_tu_giao_nhan') + '?tab=cua_toi')
        self.assertEqual([b.pk for b in resp.context['bias']], [self.bia2.pk])

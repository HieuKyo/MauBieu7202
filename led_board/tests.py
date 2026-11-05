import io
import shutil
import tempfile
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser, Permission, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from savings_calculator.models import InterestRate, SavingsProduct

from .context_processors import rate_reminder
from .models import BoardSetting, ExchangeRate, LedSlide, RateHistory
from .views import _format_rate

MEDIA = tempfile.mkdtemp()


def png(name='a.png'):
    buffer = io.BytesIO()
    Image.new('RGB', (4, 4), 'red').save(buffer, 'PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


def rate_post(rows):
    """rows: danh sách dict của từng dòng formset."""
    data = {
        'form-TOTAL_FORMS': len(rows),
        'form-INITIAL_FORMS': sum(1 for r in rows if r.get('id')),
        'form-MIN_NUM_FORMS': 0,
        'form-MAX_NUM_FORMS': 1000,
    }
    for i, row in enumerate(rows):
        for key, value in row.items():
            data[f'form-{i}-{key}'] = value
    return data


def usd_row(**overrides):
    row = {
        'id': ExchangeRate.objects.get(code='USD').pk, 'code': 'USD', 'order': 1,
        'buy_cash': '25900', 'sell_cash': '26200',
        'buy_transfer': '25950', 'sell_transfer': '26200',
    }
    row.update(overrides)
    return row


def eur_row():
    return {
        'id': ExchangeRate.objects.get(code='EUR').pk, 'code': 'EUR', 'order': 2,
        'buy_cash': '30100.50', 'sell_cash': '31000',
        'buy_transfer': '30200', 'sell_transfer': '31000',
    }


class FormatRateTests(TestCase):
    def test_format(self):
        self.assertEqual(_format_rate(Decimal('25950.00')), '25.950')
        self.assertEqual(_format_rate(Decimal('30100.50')), '30.100,50')
        self.assertEqual(_format_rate(Decimal('170.25')), '170,25')
        self.assertEqual(_format_rate(None), '—')


class PublicBoardTests(TestCase):
    def test_seed_has_usd_eur_without_fake_numbers(self):
        self.assertEqual(list(ExchangeRate.objects.values_list('code', flat=True)), ['USD', 'EUR'])
        payload = self.client.get(reverse('led_board:data')).json()
        self.assertEqual(payload['rates'][0]['buy_cash'], '—')
        self.assertEqual(payload['updated'], '')

    def test_board_needs_no_login(self):
        self.assertEqual(self.client.get(reverse('led_board:board')).status_code, 200)
        self.assertEqual(self.client.get(reverse('led_board:data')).status_code, 200)

    def test_board_shows_branch_and_logo(self):
        response = self.client.get(reverse('led_board:board'))
        self.assertContains(response, 'Agribank Chi nhánh Giá Rai Bạc Liêu')
        self.assertContains(response, 'images/agribank_logo.png')

    def test_board_is_not_cached(self):
        response = self.client.get(reverse('led_board:data'))
        self.assertIn('no-store', response['Cache-Control'])

    def test_board_does_not_write_or_create_session(self):
        response = self.client.get(reverse('led_board:data'))
        self.assertNotIn('sessionid', response.cookies)

    def test_loop_seconds_and_ticker_in_payload(self):
        BoardSetting.objects.filter(pk=1).update(
            rate_seconds=30, savings_seconds=12, ticker_text='  Nghỉ lễ 2/9  ',
        )
        payload = self.client.get(reverse('led_board:data')).json()
        self.assertEqual((payload['rate_seconds'], payload['savings_seconds']), (30, 12))
        self.assertEqual(payload['ticker'], 'Nghỉ lễ 2/9')


class SavingsBoardTests(TestCase):
    def setUp(self):
        self.product = SavingsProduct.objects.create(name='Tiết kiệm', code='TK')
        BoardSetting.objects.filter(pk=1).update(savings_product=self.product)

    def rate(self, low, high, value, **extra):
        return InterestRate.objects.create(
            product=self.product, term_month_min=low, term_month_max=high,
            interest_rate_yearly=value, **extra,
        )

    def savings(self):
        return self.client.get(reverse('led_board:data')).json()['savings']

    def test_no_product_selected(self):
        BoardSetting.objects.filter(pk=1).update(savings_product=None)
        self.assertEqual(self.savings()['rows'], [])

    def test_rows_and_labels(self):
        self.rate(12, 12, 5.2)
        self.rate(1, 2, 2.6)
        self.rate(6, 11, 4, description='6 đến 11 tháng')
        rows = self.savings()['rows']
        self.assertEqual(rows, [
            {'term': '1-2 tháng', 'rate': '2,60'},
            {'term': '6 đến 11 tháng', 'rate': '4,00'},
            {'term': '12 tháng', 'rate': '5,20'},
        ])

    def test_inactive_and_future_rates_hidden(self):
        self.rate(1, 1, 2, is_active=False)
        self.rate(2, 2, 3, effective_date=date.today() + timedelta(days=5))
        self.assertEqual(self.savings()['rows'], [])

    def test_other_product_hidden(self):
        other = SavingsProduct.objects.create(name='Khác', code='K')
        InterestRate.objects.create(
            product=other, term_month_min=1, term_month_max=1, interest_rate_yearly=9,
        )
        self.assertEqual(self.savings()['rows'], [])

    def test_deleting_product_keeps_board_working(self):
        self.product.delete()
        self.assertEqual(self.savings()['rows'], [])


class SavingsEditTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('nv', password='x')
        self.user.user_permissions.add(Permission.objects.get(codename='change_exchangerate'))
        self.client.force_login(self.user)
        self.url = reverse('led_board:rate_edit')
        self.product = SavingsProduct.objects.create(name='Tiết kiệm', code='TK')
        BoardSetting.objects.filter(pk=1).update(savings_product=self.product)

    def post(self, rows, initial=0):
        data = {
            'save_savings': '1', 'savings-TOTAL_FORMS': len(rows), 'savings-INITIAL_FORMS': initial,
            'savings-MIN_NUM_FORMS': 0, 'savings-MAX_NUM_FORMS': 1000,
        }
        for i, row in enumerate(rows):
            for key, value in row.items():
                data[f'savings-{i}-{key}'] = value
        return self.client.post(self.url, data)

    @staticmethod
    def row(**overrides):
        return {
            'term_month_min': '12', 'term_month_max': '12', 'description': '',
            'interest_rate_yearly': '5.2', 'effective_date': '', 'is_active': 'on', **overrides,
        }

    def test_page_shows_product_rates(self):
        InterestRate.objects.create(
            product=self.product, term_month_min=6, term_month_max=8, interest_rate_yearly=3.9,
        )
        self.assertContains(self.client.get(self.url), 'Lưu lãi suất')

    def test_unselected_still_shows_table_and_warns(self):
        BoardSetting.objects.filter(pk=1).update(savings_product=None)
        response = self.client.get(self.url)
        self.assertContains(response, 'Lưu lãi suất')
        self.assertContains(response, 'Bảng LED chưa hiện lãi suất')
        self.assertContains(response, f'<option value="{self.product.pk}" selected>')

    def test_unselected_stays_off_board_until_saved(self):
        BoardSetting.objects.filter(pk=1).update(savings_product=None)
        self.client.get(self.url)
        self.assertIsNone(BoardSetting.load().savings_product)
        self.post([self.row()])
        self.assertEqual(BoardSetting.load().savings_product, self.product)
        rows = self.client.get(reverse('led_board:data')).json()['savings']['rows']
        self.assertEqual(len(rows), 1)

    def test_selected_shows_no_warning(self):
        self.assertNotContains(self.client.get(self.url), 'Bảng LED chưa hiện lãi suất')

    def test_no_active_product_shows_prompt(self):
        BoardSetting.objects.filter(pk=1).update(savings_product=None)
        SavingsProduct.objects.update(is_active=False)
        response = self.client.get(self.url)
        self.assertContains(response, 'Chưa có sản phẩm tiết kiệm nào đang áp dụng')
        self.assertNotContains(response, 'Lưu lãi suất')

    def test_pick_product(self):
        other = SavingsProduct.objects.create(name='Khác', code='K')
        response = self.client.post(self.url, {'pick_product': '1', 'savings_product': other.pk})
        self.assertRedirects(response, self.url)
        self.assertEqual(BoardSetting.load().savings_product, other)

    def test_add_rate_reaches_board_and_calculator_table(self):
        self.assertRedirects(self.post([self.row()]), self.url)
        rate = InterestRate.objects.get()
        self.assertEqual((rate.product, rate.interest_rate_yearly), (self.product, 5.2))
        rows = self.client.get(reverse('led_board:data')).json()['savings']['rows']
        self.assertEqual(rows, [{'term': '12 tháng', 'rate': '5,20'}])

    def test_edit_and_delete_rate(self):
        keep = InterestRate.objects.create(
            product=self.product, term_month_min=1, term_month_max=1, interest_rate_yearly=2,
        )
        drop = InterestRate.objects.create(
            product=self.product, term_month_min=3, term_month_max=3, interest_rate_yearly=3,
        )
        self.post([
            self.row(id=keep.pk, term_month_min='1', term_month_max='1', interest_rate_yearly='2.5'),
            self.row(id=drop.pk, term_month_min='3', term_month_max='3', DELETE='on'),
        ], initial=2)
        keep.refresh_from_db()
        self.assertEqual(keep.interest_rate_yearly, 2.5)
        self.assertFalse(InterestRate.objects.filter(pk=drop.pk).exists())

    def test_blank_extra_row_ignored(self):
        blank = self.row(term_month_min='', term_month_max='', interest_rate_yearly='')
        self.assertRedirects(self.post([blank]), self.url)
        self.assertEqual(InterestRate.objects.count(), 0)

    def test_invalid_values_rejected(self):
        for bad in ({'interest_rate_yearly': '0'}, {'interest_rate_yearly': '101'},
                    {'term_month_min': '12', 'term_month_max': '6'}):
            response = self.post([self.row(**bad)])
            self.assertEqual(response.status_code, 200, bad)
            self.assertEqual(InterestRate.objects.count(), 0, bad)

    def test_cannot_edit_other_product_rate(self):
        other = SavingsProduct.objects.create(name='Khác', code='K')
        rate = InterestRate.objects.create(
            product=other, term_month_min=1, term_month_max=1, interest_rate_yearly=2,
        )
        self.post([self.row(id=rate.pk, interest_rate_yearly='9')], initial=1)
        rate.refresh_from_db()
        self.assertEqual((rate.product, rate.interest_rate_yearly), (other, 2))

    def test_saving_savings_does_not_stamp_exchange_rates(self):
        self.post([self.row()])
        self.assertFalse(ExchangeRate.objects.exclude(updated_at=None).exists())

    def test_requires_permission(self):
        self.client.force_login(User.objects.create_user('khac'))
        self.assertEqual(self.post([self.row()]).status_code, 403)
        self.assertEqual(InterestRate.objects.count(), 0)


class ShutdownSignalTests(TestCase):
    def signal(self, hour, minute):
        now = timezone.make_aware(datetime(2026, 11, 4, hour, minute))
        with patch('led_board.views.timezone.localtime', return_value=now):
            return self.client.get(reverse('led_board:shutdown_signal')).content

    def test_off_when_not_set(self):
        self.assertEqual(self.signal(18, 0), b'')

    def test_window(self):
        BoardSetting.objects.filter(pk=1).update(shutdown_time=time(18, 0))
        self.assertEqual(self.signal(17, 59), b'')
        self.assertEqual(self.signal(18, 0), b'TAT')
        self.assertEqual(self.signal(18, 9), b'TAT')
        self.assertEqual(self.signal(18, 10), b'')

    def test_public_without_login(self):
        self.assertEqual(self.client.get(reverse('led_board:shutdown_signal')).status_code, 200)


class ReminderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('nv', password='x')
        self.user.user_permissions.add(Permission.objects.get(codename='change_exchangerate'))

    def remind(self, user, hour=9):
        request = RequestFactory().get('/')
        request.user = user
        now = timezone.make_aware(datetime(2026, 11, 4, hour, 0))
        real_localtime = timezone.localtime
        with patch('led_board.context_processors.timezone.localtime',
                   side_effect=lambda value=None: now if value is None else real_localtime(value)):
            return rate_reminder(request)

    def test_reminds_after_time(self):
        self.assertEqual(self.remind(self.user), {'led_rate_reminder': True})

    def test_banner_shown_in_page(self):
        BoardSetting.objects.filter(pk=1).update(remind_time=time(0, 0))
        self.client.force_login(self.user)
        response = self.client.get(reverse('led_board:rate_history'))
        self.assertContains(response, 'Hôm nay chưa lưu tỷ giá')

    def test_silent_before_time(self):
        self.assertEqual(self.remind(self.user, hour=8), {})

    def test_silent_when_saved_today(self):
        saved = timezone.make_aware(datetime(2026, 11, 4, 8, 0))
        ExchangeRate.objects.update(updated_at=saved)
        self.assertEqual(self.remind(self.user), {})

    def test_reminds_when_saved_yesterday(self):
        saved = timezone.make_aware(datetime(2026, 11, 3, 8, 0))
        ExchangeRate.objects.update(updated_at=saved)
        self.assertEqual(self.remind(self.user), {'led_rate_reminder': True})

    def test_user_without_permission_not_reminded(self):
        self.assertEqual(self.remind(User.objects.create_user('khac')), {})

    def test_anonymous_not_reminded(self):
        self.assertEqual(self.remind(AnonymousUser()), {})


class PermissionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('nv', password='x')

    def test_anonymous_redirected_to_login(self):
        for name in ('rate_edit', 'slide_settings'):
            response = self.client.get(reverse(f'led_board:{name}'))
            self.assertEqual(response.status_code, 302)
            self.assertIn('login', response['Location'])

    def test_user_without_permission_forbidden(self):
        self.client.force_login(self.user)
        for name in ('rate_edit', 'slide_settings'):
            self.assertEqual(self.client.get(reverse(f'led_board:{name}')).status_code, 403)

    def test_post_without_permission_changes_nothing(self):
        self.client.force_login(self.user)
        self.client.post(reverse('led_board:rate_edit'), rate_post([usd_row(), eur_row()]))
        self.assertIsNone(ExchangeRate.objects.get(code='USD').buy_cash)


class RateEditTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('nv', password='x')
        self.user.user_permissions.add(Permission.objects.get(codename='change_exchangerate'))
        self.client.force_login(self.user)
        self.url = reverse('led_board:rate_edit')

    def test_page_renders(self):
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_save_updates_board(self):
        response = self.client.post(self.url, rate_post([usd_row(), eur_row()]))
        self.assertRedirects(response, self.url)
        payload = self.client.get(reverse('led_board:data')).json()
        self.assertEqual(payload['rates'][0]['buy_cash'], '25.900')
        self.assertEqual(payload['rates'][1]['buy_cash'], '30.100,50')
        self.assertTrue(payload['updated'])

    def test_resave_unchanged_refreshes_stamp(self):
        self.client.post(self.url, rate_post([usd_row(), eur_row()]))
        old = ExchangeRate.objects.get(code='USD').updated_at
        self.client.post(self.url, rate_post([usd_row(), eur_row()]))
        self.assertGreater(ExchangeRate.objects.get(code='USD').updated_at, old)

    def test_buy_above_sell_rejected(self):
        response = self.client.post(self.url, rate_post([usd_row(buy_cash='27000'), eur_row()]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Giá bán phải lớn hơn')
        self.assertIsNone(ExchangeRate.objects.get(code='USD').buy_cash)

    def test_missing_rate_rejected(self):
        response = self.client.post(self.url, rate_post([usd_row(sell_cash=''), eur_row()]))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(ExchangeRate.objects.get(code='USD').buy_cash)

    def test_add_currency_uppercased(self):
        new = {'code': 'jpy', 'order': 3, 'buy_cash': '165', 'sell_cash': '175',
               'buy_transfer': '166', 'sell_transfer': '175'}
        self.client.post(self.url, rate_post([usd_row(), eur_row(), new]))
        self.assertTrue(ExchangeRate.objects.filter(code='JPY').exists())

    def test_blank_extra_row_ignored(self):
        blank = {'code': '', 'order': 0, 'buy_cash': '', 'sell_cash': '',
                 'buy_transfer': '', 'sell_transfer': ''}
        response = self.client.post(self.url, rate_post([usd_row(), eur_row(), blank]))
        self.assertRedirects(response, self.url)
        self.assertEqual(ExchangeRate.objects.count(), 2)

    def test_delete_currency(self):
        self.client.post(self.url, rate_post([usd_row(), {**eur_row(), 'DELETE': 'on'}]))
        self.assertFalse(ExchangeRate.objects.filter(code='EUR').exists())

    def test_history_records_change_with_old_and_new(self):
        self.client.post(self.url, rate_post([usd_row(), eur_row()]))
        self.client.post(self.url, rate_post([usd_row(buy_cash='26000'), eur_row()]))
        entry = RateHistory.objects.first()
        self.assertEqual((entry.code, entry.action, entry.changed_by), ('USD', 'Sửa', self.user))
        self.assertEqual(entry.old_values['buy_cash'], '25.900')
        self.assertEqual(entry.new_values['buy_cash'], '26.000')

    def test_resave_unchanged_adds_no_history(self):
        self.client.post(self.url, rate_post([usd_row(), eur_row()]))
        count = RateHistory.objects.count()
        self.client.post(self.url, rate_post([usd_row(), eur_row()]))
        self.assertEqual(RateHistory.objects.count(), count)

    def test_order_only_change_adds_no_history(self):
        self.client.post(self.url, rate_post([usd_row(), eur_row()]))
        count = RateHistory.objects.count()
        self.client.post(self.url, rate_post([usd_row(order=5), eur_row()]))
        self.assertEqual(RateHistory.objects.count(), count)

    def test_history_records_add_and_delete(self):
        self.client.post(self.url, rate_post([usd_row(), eur_row()]))
        new = {'code': 'JPY', 'order': 3, 'buy_cash': '165', 'sell_cash': '175',
               'buy_transfer': '166', 'sell_transfer': '175'}
        self.client.post(self.url, rate_post([usd_row(), {**eur_row(), 'DELETE': 'on'}, new]))
        actions = dict(RateHistory.objects.filter(code__in=['EUR', 'JPY']).exclude(action='Sửa')
                       .values_list('code', 'action'))
        self.assertEqual(actions, {'EUR': 'Xóa', 'JPY': 'Thêm'})
        deleted = RateHistory.objects.get(code='EUR', action='Xóa')
        self.assertEqual(deleted.old_values['buy_cash'], '30.100,50')

    def test_rejected_save_adds_no_history(self):
        self.client.post(self.url, rate_post([usd_row(buy_cash='27000'), eur_row()]))
        self.assertEqual(RateHistory.objects.count(), 0)

    def test_history_page_renders(self):
        self.client.post(self.url, rate_post([usd_row(), eur_row()]))
        self.client.post(self.url, rate_post([usd_row(buy_cash='26000'), eur_row()]))
        response = self.client.get(reverse('led_board:rate_history'))
        self.assertContains(response, '25.900')
        self.assertContains(response, '26.000')

    def test_history_requires_permission(self):
        self.client.force_login(User.objects.create_user('khac'))
        self.assertEqual(self.client.get(reverse('led_board:rate_history')).status_code, 403)


@override_settings(MEDIA_ROOT=MEDIA)
class SlideTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user('nv', password='x')
        self.user.user_permissions.add(Permission.objects.get(codename='change_exchangerate'))
        self.client.force_login(self.user)
        self.url = reverse('led_board:slide_settings')

    def save_post(self, slides=(), rate='25', slide='6', **extra):
        data = {
            'rate_seconds': rate, 'slide_seconds': slide, 'savings_seconds': '15',
            'board_width': '640', 'board_height': '192', 'remind_time': '08:30',
            'shutdown_time': '', 'ticker_text': '',
            'form-TOTAL_FORMS': len(slides), 'form-INITIAL_FORMS': len(slides),
            'form-MIN_NUM_FORMS': 0, 'form-MAX_NUM_FORMS': 1000,
        }
        for i, s in enumerate(slides):
            data[f'form-{i}-id'] = s.pk
            data[f'form-{i}-order'] = s.order
            data[f'form-{i}-is_active'] = 'on'
        data.update(extra)
        return data

    def upload(self):
        self.client.post(self.url, {'upload': '1', 'image': png()})
        return LedSlide.objects.latest('id')

    def test_page_renders_with_slide(self):
        self.upload()
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_upload_appears_on_board_and_is_public(self):
        slide = self.upload()
        payload = self.client.get(reverse('led_board:data')).json()
        url = reverse('led_board:slide_image', args=[slide.pk])
        self.assertEqual(payload['slides'], [{'url': url, 'seconds': 8}])
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        b''.join(response.streaming_content)

    def test_non_image_rejected(self):
        fake = SimpleUploadedFile('a.png', b'not an image', content_type='image/png')
        self.client.post(self.url, {'upload': '1', 'image': fake})
        self.assertEqual(LedSlide.objects.count(), 0)

    def test_svg_rejected(self):
        svg = SimpleUploadedFile('a.svg', b'<svg xmlns="http://www.w3.org/2000/svg"/>')
        self.client.post(self.url, {'upload': '1', 'image': svg})
        self.assertEqual(LedSlide.objects.count(), 0)

    def test_save_loop_seconds(self):
        self.assertRedirects(self.client.post(self.url, self.save_post()), self.url)
        setting = BoardSetting.load()
        self.assertEqual((setting.rate_seconds, setting.slide_seconds), (25, 6))

    def test_seconds_out_of_range_rejected(self):
        self.client.post(self.url, self.save_post(rate='1'))
        self.assertEqual(BoardSetting.load().rate_seconds, 20)

    def test_hidden_slide_leaves_board(self):
        slide = self.upload()
        data = self.save_post([slide])
        del data['form-0-is_active']
        self.client.post(self.url, data)
        self.assertEqual(self.client.get(reverse('led_board:data')).json()['slides'], [])

    def test_delete_removes_file(self):
        slide = self.upload()
        storage, name = slide.image.storage, slide.image.name
        self.assertTrue(storage.exists(name))
        self.client.post(self.url, self.save_post([slide], **{'form-0-DELETE': 'on'}))
        self.assertEqual(LedSlide.objects.count(), 0)
        self.assertFalse(storage.exists(name))

    def board_slides(self):
        return self.client.get(reverse('led_board:data')).json()['slides']

    def test_slide_own_seconds_override_default(self):
        slide = self.upload()
        self.client.post(self.url, self.save_post([slide], **{'form-0-seconds': '25'}))
        self.assertEqual(self.board_slides()[0]['seconds'], 25)

    def test_slide_seconds_out_of_range_rejected(self):
        slide = self.upload()
        self.client.post(self.url, self.save_post([slide], **{'form-0-seconds': '1'}))
        slide.refresh_from_db()
        self.assertIsNone(slide.seconds)

    def test_slide_date_window(self):
        slide = self.upload()
        today = timezone.localdate()
        day = timedelta(days=1)
        cases = [
            (None, None, 1), (today, today, 1), (today - day, today + day, 1),
            (today + day, None, 0), (None, today - day, 0),
        ]
        for start, end, expected in cases:
            LedSlide.objects.filter(pk=slide.pk).update(start_date=start, end_date=end)
            self.assertEqual(len(self.board_slides()), expected, (start, end))

    def test_slide_dates_saved_from_form(self):
        slide = self.upload()
        self.client.post(self.url, self.save_post(
            [slide], **{'form-0-start_date': '2026-11-01', 'form-0-end_date': '2026-11-30'},
        ))
        slide.refresh_from_db()
        self.assertEqual(slide.end_date, date(2026, 11, 30))

    def test_end_before_start_rejected(self):
        slide = self.upload()
        response = self.client.post(self.url, self.save_post(
            [slide], **{'form-0-start_date': '2026-11-30', 'form-0-end_date': '2026-11-01'},
        ))
        self.assertContains(response, 'Ngày kết thúc phải sau ngày bắt đầu')

    def test_settings_saved(self):
        product = SavingsProduct.objects.create(name='TK', code='TK')
        BoardSetting.objects.filter(pk=1).update(savings_product=product)
        self.client.post(self.url, self.save_post(
            shutdown_time='18:30', ticker_text='Chào',
            board_width='800', board_height='200', remind_time='09:00',
        ))
        setting = BoardSetting.load()
        self.assertEqual(setting.shutdown_time, time(18, 30))
        self.assertEqual(setting.remind_time, time(9, 0))
        self.assertEqual(setting.savings_product, product)
        self.assertEqual(setting.ticker_text, 'Chào')

    def test_crop_frame_uses_board_ratio(self):
        BoardSetting.objects.filter(pk=1).update(board_width=800, board_height=200)
        self.assertContains(self.client.get(self.url), 'aspect-ratio: 800 / 200')

    def test_missing_file_returns_404(self):
        slide = self.upload()
        slide.image.storage.delete(slide.image.name)
        response = self.client.get(reverse('led_board:slide_image', args=[slide.pk]))
        self.assertEqual(response.status_code, 404)

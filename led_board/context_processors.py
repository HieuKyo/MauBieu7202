from django.db.models import Max
from django.utils import timezone

from .models import BoardSetting, ExchangeRate


def rate_reminder(request):
    """Nhắc người có quyền khi đã qua giờ quy định mà hôm nay chưa bấm Lưu tỷ giá."""
    user = getattr(request, 'user', None)
    if user is None or not user.has_perm('led_board.change_exchangerate'):
        return {}
    now = timezone.localtime()
    if now.time() < BoardSetting.load().remind_time:
        return {}
    last = ExchangeRate.objects.aggregate(last=Max('updated_at'))['last']
    if last and timezone.localtime(last).date() == now.date():
        return {}
    return {'led_rate_reminder': True}

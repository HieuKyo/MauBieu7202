"""
Ghi lượt truy cập trang (menu) để superuser xem ở trang Thống kê truy cập.
"""
import logging

logger = logging.getLogger(__name__)


class MenuAccessLogMiddleware:
    """Chỉ ghi lượt mở trang thật của người đã đăng nhập: GET, trả về HTML thành công, trình duyệt yêu cầu HTML.
    Bỏ qua gọi API / fetch nền (kiểm tra tin nhắn, nhắc việc...) vì những request đó không gửi Accept: text/html."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        match = getattr(request, 'resolver_match', None)
        if (request.method == 'GET'
                and match is not None
                and response.status_code == 200
                and request.user.is_authenticated
                and 'text/html' in response.get('Content-Type', '')
                and 'text/html' in request.headers.get('Accept', '')):
            from .models import MenuAccessLog
            try:
                MenuAccessLog.objects.create(user=request.user, view_name=match.view_name[:150],
                                             path=request.path[:255])
            except Exception:
                # Ghi thống kê lỗi (vd. SQLite đang khóa) không được làm hỏng trang của người dùng
                logger.exception('Không ghi được lượt truy cập %s', request.path)
        return response

from django.conf import settings

# File VERSION do cap_nhat.bat ghi khi cập nhật trên máy LAN
try:
    APP_VERSION = (settings.BASE_DIR / 'VERSION').read_text(encoding='utf-8').strip() or '1.0'
except OSError:
    APP_VERSION = '1.0'


def app_version(request):
    return {'APP_VERSION': APP_VERSION}

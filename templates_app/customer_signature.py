"""
Ảnh chữ ký của khách hàng (chụp bằng webcam ở tab Khách hàng).
- Lưu NGOÀI thư mục media công khai: <BASE_DIR>/private_media/chu_ky/<id khách hàng>/chu_ky_<ngày giờ>.jpg
  (có thể đổi bằng settings.SIGNATURE_ROOT). Chỉ người đã đăng nhập mới xem / xóa được.
- Khi tạo file ZIP "Folder chữ ký", ảnh được đặt trong thư mục mang Mã khách hàng.
"""
import io
import re
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Customer

FILE_RE = re.compile(r'^chu_ky_\d{8}_\d{6}(_\d+)?\.jpg$')
MAX_UPLOAD = 10 * 1024 * 1024
MAX_SIDE = 3000


def signature_dir(customer_id):
    root = Path(getattr(settings, 'SIGNATURE_ROOT', Path(settings.BASE_DIR) / 'private_media' / 'chu_ky'))
    return root / str(int(customer_id))


def signature_files(customer_id):
    """Danh sách file ảnh chữ ký (cũ → mới)."""
    d = signature_dir(customer_id)
    return sorted(p for p in d.glob('chu_ky_*.jpg') if FILE_RE.match(p.name)) if d.is_dir() else []


def _payload(customer):
    return [{'name': p.name,
             'url': reverse('customer_signature_file', args=[customer.pk, p.name]),
             'delete_url': reverse('customer_signature_delete', args=[customer.pk, p.name])}
            for p in signature_files(customer.pk)]


@login_required
def customer_signatures_view(request, customer_id):
    """GET: danh sách ảnh chữ ký. POST (file 'image'): lưu ảnh chữ ký mới."""
    customer = get_object_or_404(Customer, pk=customer_id)
    if request.method == 'POST':
        upload = request.FILES.get('image')
        if not upload:
            return JsonResponse({'success': False, 'error': 'Không nhận được ảnh'}, status=400)
        if upload.size > MAX_UPLOAD:
            return JsonResponse({'success': False, 'error': 'Ảnh quá lớn (tối đa 10 MB)'}, status=400)
        from PIL import Image
        try:
            img = Image.open(upload)
            img.load()
        except Exception:
            return JsonResponse({'success': False, 'error': 'File không phải ảnh hợp lệ'}, status=400)
        img = img.convert('RGB')
        img.thumbnail((MAX_SIDE, MAX_SIDE))
        d = signature_dir(customer.pk)
        d.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path, n = d / f'chu_ky_{stamp}.jpg', 1
        while path.exists():                       # chụp 2 lần trong cùng 1 giây
            path, n = d / f'chu_ky_{stamp}_{n}.jpg', n + 1
        buf = io.BytesIO()
        img.save(buf, 'JPEG', quality=92)          # lưu lại dạng JPEG chuẩn (không giữ dữ liệu lạ trong file gốc)
        path.write_bytes(buf.getvalue())
    return JsonResponse({'success': True, 'ho_ten': customer.ho_ten, 'ma_khach_hang': customer.ma_khach_hang or '',
                         'files': _payload(customer)})


def _safe_path(customer_id, name):
    if not FILE_RE.match(name):
        raise Http404
    path = signature_dir(customer_id) / name
    if not path.is_file():
        raise Http404
    return path


@login_required
def customer_signature_file_view(request, customer_id, name):
    get_object_or_404(Customer, pk=customer_id)
    return FileResponse(open(_safe_path(customer_id, name), 'rb'), content_type='image/jpeg')


def delete_customer_signatures(sender, instance, **kwargs):
    """Xóa khách hàng (trang Khách hàng, Admin, xóa hàng loạt...) → xóa luôn thư mục ảnh chữ ký.
    Chỉ xóa sau khi lệnh xóa khách đã ghi xong vào DB (lỗi / hoàn tác thì ảnh vẫn còn)."""
    import shutil
    from django.db import transaction
    d = signature_dir(instance.pk)
    transaction.on_commit(lambda: shutil.rmtree(d, ignore_errors=True))


@login_required
@require_POST
def customer_signature_delete_view(request, customer_id, name):
    customer = get_object_or_404(Customer, pk=customer_id)
    _safe_path(customer_id, name).unlink()
    return JsonResponse({'success': True, 'files': _payload(customer)})

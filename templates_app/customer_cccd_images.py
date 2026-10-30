"""
Ảnh 2 mặt thẻ Căn cước / CCCD của khách hàng (học sinh chụp và gửi qua trang đăng ký online, đã mã hóa).
- Lưu NGOÀI thư mục media công khai: <BASE_DIR>/private_media/cccd_anh/<id khách hàng>/mat_truoc.jpg, mat_sau.jpg
  (có thể đổi bằng settings.CCCD_IMAGE_ROOT). Chỉ người đã đăng nhập mới xem được.
- Ảnh được lưu lại dạng JPEG chuẩn (bỏ dữ liệu ẩn trong file gốc như vị trí GPS).
- Xóa khách hàng → xóa luôn thư mục ảnh.
"""
import base64
import io
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404

from .models import Customer

SIDES = {'mat_truoc': 'Mặt trước', 'mat_sau': 'Mặt sau'}
MAX_SIDE = 2000


def cccd_image_dir(customer_id):
    root = Path(getattr(settings, 'CCCD_IMAGE_ROOT', Path(settings.BASE_DIR) / 'private_media' / 'cccd_anh'))
    return root / str(int(customer_id))


def cccd_image_sides(customer_id):
    """Các mặt đã có ảnh, vd. ['mat_truoc', 'mat_sau']."""
    d = cccd_image_dir(customer_id)
    return [s for s in SIDES if (d / f'{s}.jpg').is_file()]


def _clean_jpeg(data, max_side=MAX_SIDE, quality=90):
    """Mở ảnh (bytes) → JPEG chuẩn. Lỗi nếu không phải ảnh."""
    from PIL import Image
    img = Image.open(io.BytesIO(data))
    img.load()
    img = img.convert('RGB')
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=quality)
    return buf.getvalue()


def thumbnail_data_url(b64, size=260):
    """Ảnh nhỏ (data URL) để xem trước trên trang nhập danh sách."""
    try:
        return 'data:image/jpeg;base64,' + base64.b64encode(_clean_jpeg(base64.b64decode(b64), size, 75)).decode()
    except Exception:
        return ''


def save_cccd_images(customer_id, images):
    """images = {'mat_truoc': <base64 JPEG>, 'mat_sau': ...}; mặt nào có ảnh thì ghi đè ảnh cũ."""
    d = cccd_image_dir(customer_id)
    for side, b64 in images.items():
        if side in SIDES and b64:
            data = _clean_jpeg(base64.b64decode(b64))
            d.mkdir(parents=True, exist_ok=True)
            (d / f'{side}.jpg').write_bytes(data)


@login_required
def customer_cccd_image_view(request, customer_id, side):
    get_object_or_404(Customer, pk=customer_id)
    path = cccd_image_dir(customer_id) / f'{side}.jpg'
    if side not in SIDES or not path.is_file():
        raise Http404
    return FileResponse(open(path, 'rb'), content_type='image/jpeg')


def delete_customer_cccd_images(sender, instance, **kwargs):
    """Xóa khách hàng → xóa thư mục ảnh CCCD (sau khi lệnh xóa đã ghi xong vào DB)."""
    import shutil
    from django.db import transaction
    d = cccd_image_dir(instance.pk)
    transaction.on_commit(lambda: shutil.rmtree(d, ignore_errors=True))


def _is_card_shape(path):
    """Ảnh đã cắt theo thẻ (nằm ngang, tỉ lệ ~1,59)? Ảnh gốc chưa cắt (vd. ảnh dọc 1200x1600) → False."""
    from PIL import Image
    try:
        with Image.open(path) as img:
            w, h = img.size
        return 1.4 <= w / h <= 1.8
    except Exception:
        return False


@login_required
def cccd_batch_print_view(request):
    """In lô CCCD: mỗi khách 1 trang A5 ngang gồm 2 mặt thẻ + "ĐÃ ĐỐI CHIẾU KHỚP ĐÚNG VỚI BẢN GỐC"
    (giống nút Chụp 2 mặt). ids theo đúng thứ tự đã xem trước; khách chưa đủ 2 mặt ảnh thì bỏ qua và liệt kê."""
    from datetime import datetime
    from django.shortcuts import render
    from .customer_export import _class_name
    from .models import BranchConfig

    ids = [int(x) for x in request.GET.get('ids', '').split(',') if x.strip().isdigit()]
    by_id = {c.pk: c for c in Customer.objects.filter(pk__in=ids)}
    pages, missing = [], []
    for pk in ids:
        c = by_id.get(pk)
        if c is None:
            continue
        info = {'id': c.pk, 'ho_ten': c.ho_ten, 'lop': _class_name(c.ghi_chu)}
        if len(cccd_image_sides(pk)) < len(SIDES):
            missing.append(info)
            continue
        d = cccd_image_dir(pk)
        info['chua_cat'] = not all(_is_card_shape(d / f'{s}.jpg') for s in SIDES)
        pages.append(info)
    try:
        ngay = datetime.strptime(request.GET.get('ngay_in', ''), '%Y-%m-%d').date()
        ngay_ky = f'ngày {ngay:%d} tháng {ngay:%m} năm {ngay:%Y}'
    except ValueError:
        ngay_ky = 'ngày ...... tháng ...... năm ........'
    return render(request, 'templates_app/cccd_batch_print.html', {
        'pages': pages, 'missing': missing, 'ngay_ky': ngay_ky,
        'chua_cat': [p for p in pages if p['chua_cat']],
        'dia_danh': BranchConfig.get_for_user(request.user).dia_danh or '..................',
    })

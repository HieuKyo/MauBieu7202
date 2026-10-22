"""
Sau khi mở CIF trên hệ thống ngân hàng:
1. Upload file Excel kết quả → cập nhật "Mã khách hàng" cho khách đã có (ghép theo số CCCD). Có bước xem trước.
2. Tạo file ZIP gồm các thư mục rỗng, mỗi thư mục mang tên một Mã khách hàng (để lưu chữ ký).
"""
import io
import re
import unicodedata
import zipfile
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from .customer_export import _filtered_customers
from .models import Customer

HEADER_SCAN_ROWS = 15
CODE_LEN = 9          # Mã khách hàng có 9 chữ số


def _plain_lower(text):
    text = str(text or '').replace('đ', 'd').replace('Đ', 'D')
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', text.lower()).strip()


def _is_id_header(h):
    h = _plain_lower(h)
    if 'cu' in h.split() or 'old' in h:          # bỏ "Số ID cũ"
        return False
    return any(k in h for k in ('so id', 'cccd', 'cmnd', 'can cuoc', 'so giay to', 'regno', 'id number', 'giay to tuy than'))


def _is_code_header(h):
    h = _plain_lower(h)
    return any(k in h for k in ('ma kh', 'ma khach hang', 'cif', 'custno', 'customer no', 'customer code', 'ma so khach hang'))


def _digits(value):
    """Giá trị ô → chuỗi số (Excel có thể lưu số dạng 95099004096.0)."""
    if value is None:
        return ''
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return re.sub(r'\D', '', str(value).strip())


def _norm_id(value):
    """Số CCCD/CMND: khôi phục số 0 đầu bị Excel làm mất (CCCD 12 số, CMND 9 số)."""
    d = _digits(value)
    if len(d) == 11:
        d = '0' + d
    elif len(d) == 8:
        d = '0' + d
    return d


def _norm_code(value):
    """Mã KH 9 số: bù số 0 đầu bị Excel làm mất (vd. 699174 → 000699174). Sai độ dài → '' (không hợp lệ)."""
    d = _digits(value)
    if 0 < len(d) < CODE_LEN:
        d = d.zfill(CODE_LEN)
    return d if len(d) == CODE_LEN else ''


# Cột của file "Xuất Excel" danh sách khách hàng (customer_export._export_normal) → trường Customer.
# File có các cột này: khách chưa có trong danh sách được THÊM MỚI với đủ thông tin.
EXPORT_TEXT = {'ho va ten': 'ho_ten', 'gioi tinh': 'gioi_tinh', 'noi cap': 'noi_cap_cmnd', 'dia chi': 'dia_chi',
               'so dien thoai': 'so_dien_thoai', 'email': 'email', 'nghe nghiep': 'nghe_nghiep', 'noi lam viec': 'noi_lam_viec',
               'so tai khoan': 'so_tai_khoan', 'loai tai khoan': 'loai_tai_khoan', 'loai tien': 'loai_tien_te',
               'loai the': 'loai_the', 'hang the': 'hang_the', 'so the': 'so_the_atm', 'phan loai kh': 'ket_qua_phan_loai_kh',
               'ma cif': 'cif', 'lop': 'lop'}
EXPORT_DATE = {'ngay sinh': 'ngay_sinh', 'ngay cap': 'ngay_cap_cmnd', 'ngay het han': 'ngay_het_han_cmnd'}
EXPORT_YESNO = {'sms banking': 'dv_sms_banking', 'agribank plus': 'dv_bankplus', 'e-mobile': 'dv_e_mobile',
                'bao hiem abic': 'dv_abic'}


def _cell_text(value):
    if value is None:
        return ''
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value).strip()


def _cell_date(value):
    if isinstance(value, datetime):
        return value.date()
    text = _cell_text(value)
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def _row_data(header, row):
    """Dòng của file Xuất Excel → {trường: giá trị} (chỉ các cột có trong file)."""
    data = {}
    for j, h in header.items():
        v = row[j] if j < len(row) else None
        if h in EXPORT_TEXT:
            data[EXPORT_TEXT[h]] = _cell_text(v)
        elif h in EXPORT_DATE:
            data[EXPORT_DATE[h]] = _cell_date(v)
        elif h in EXPORT_YESNO:
            data[EXPORT_YESNO[h]] = _plain_lower(v) in ('co', 'x', '1', 'yes')
    return data


def _parse_rows(workbook, known_ids):
    """Trả về [(số CCCD, mã KH, 'sheet!dòng', thông tin khách)] đọc từ mọi sheet.
    Thông tin khách ({} nếu file không có cột Họ và tên) dùng để thêm khách chưa có trong danh sách."""
    found = []
    for ws in workbook.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        header_idx = id_col = code_col = None
        for i, row in enumerate(rows[:HEADER_SCAN_ROWS]):
            ids = [j for j, v in enumerate(row) if v is not None and _is_id_header(v)]
            codes = [j for j, v in enumerate(row) if v is not None and _is_code_header(v) and 'cif' not in _plain_lower(v)]
            codes += [j for j, v in enumerate(row) if v is not None and _is_code_header(v) and j not in codes]   # "Mã KH" trước "Mã CIF"
            if ids and codes:
                header_idx, id_col, code_col = i, ids[0], codes[0]
                break

        if header_idx is not None:
            # Có dòng tiêu đề: cột CCCD + Mã KH; file Xuất Excel (có cột Họ và tên) → đọc thêm thông tin khách
            header = {j: _plain_lower(v) for j, v in enumerate(rows[header_idx]) if v is not None}
            full = 'ho va ten' in header.values()
            for i, row in enumerate(rows[header_idx + 1:], start=header_idx + 2):
                if id_col < len(row) and code_col < len(row):
                    cccd, code = _norm_id(row[id_col]), _digits(row[code_col])
                    data = _row_data(header, row) if full else {}
                    if cccd and (code or data.get('ho_ten')):
                        found.append((cccd, code, f'{ws.title}!{i}', data))
        else:
            # Không có tiêu đề: ô trùng số CCCD đã có trong hệ thống + ô 9 chữ số khác (mã KH)
            for i, row in enumerate(rows, start=1):
                cells = [_digits(v) for v in row]
                cccd = next((_norm_id(c) for c in cells if _norm_id(c) in known_ids), '')
                code = next((c for c in cells if len(c) == CODE_LEN and c != cccd), '')
                if cccd and code:
                    found.append((cccd, code, f'{ws.title}!{i}', {}))
    return found


def _new_customer(data, cccd, code, user):
    """Khách mới từ 1 dòng file Xuất Excel (giá trị không hợp lệ với danh mục thì bỏ, giữ mặc định)."""
    from .student_registration import _set_class_note
    c = Customer(created_by=user, so_cmnd=cccd, ma_khach_hang=code)
    for field, value in data.items():
        if field == 'lop' or value in ('', None):
            continue
        f = Customer._meta.get_field(field)
        if f.choices and value not in {k for k, _ in f.flatchoices}:
            continue
        setattr(c, field, value)
    if not c.cif:
        c.cif = None                       # cột unique, cho phép trống
    if len(c.so_dien_thoai) == 9:
        c.so_dien_thoai = '0' + c.so_dien_thoai   # Excel làm mất số 0 đầu
    if data.get('lop'):
        c.ghi_chu = _set_class_note('', data['lop'], '')
    c.save()
    return c


@login_required
@require_POST
def customer_update_codes_view(request):
    """Xem trước (apply=0) hoặc cập nhật (apply=1) Mã khách hàng từ file Excel."""
    upload = request.FILES.get('excel_file')
    if not upload or not upload.name.lower().endswith(('.xlsx', '.xlsm')):
        return JsonResponse({'success': False, 'error': 'Vui lòng chọn file Excel .xlsx'}, status=400)
    apply = request.POST.get('apply') == '1'
    overwrite = request.POST.get('overwrite') == '1'

    import openpyxl
    try:
        wb = openpyxl.load_workbook(upload, data_only=True, read_only=True)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Không đọc được file Excel: {e}'}, status=400)

    known = {}
    for c in Customer.objects.exclude(so_cmnd='').only('id', 'so_cmnd', 'ho_ten', 'ma_khach_hang'):
        known.setdefault(_norm_id(c.so_cmnd), c)
    pairs = _parse_rows(wb, set(known))
    wb.close()
    if not pairs:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy cặp "Số CCCD" + "Mã khách hàng" nào trong file. '
                                                         'File cần có cột Số ID/CCCD và cột Mã KH/CIF.'}, status=400)

    rows, updated_ids, created_ids, seen = [], [], [], set()
    for cccd, raw_code, where, data in pairs:
        if cccd in seen:
            continue
        seen.add(cccd)
        c = known.get(cccd)
        code = _norm_code(raw_code)
        loi = ''
        if raw_code and not code:
            status = 'invalid'
            code = raw_code
        elif c is None:
            status = 'new' if data.get('ho_ten') else 'not_found'   # file Xuất Excel: thêm khách chưa có
        elif not code:
            status = 'no_code'
        elif (c.ma_khach_hang or '').strip() == code:
            status = 'same'
        elif (c.ma_khach_hang or '').strip() and not overwrite:
            status = 'conflict'
        else:
            status = 'update'
        if apply and status == 'update':
            Customer.objects.filter(pk=c.pk).update(ma_khach_hang=code)
            updated_ids.append(c.pk)
        elif apply and status == 'new':
            try:
                c = _new_customer(data, cccd, code, request.user)
                created_ids.append(c.pk)
                if code:
                    updated_ids.append(c.pk)
            except Exception as e:
                from .views import _customer_error_text
                status, loi, c = 'error', _customer_error_text(e), None
        rows.append({'cccd': cccd, 'ma_moi': code, 'nguon': where, 'trang_thai': status, 'loi': loi,
                     'ho_ten': c.ho_ten if c else data.get('ho_ten', ''), 'lop': data.get('lop', ''),
                     'ma_cu': (c.ma_khach_hang or '') if c and status != 'new' else '', 'id': c.pk if c else None})

    summary = {k: sum(r['trang_thai'] == k for r in rows)
               for k in ('update', 'new', 'same', 'no_code', 'conflict', 'not_found', 'invalid', 'error')}
    return JsonResponse({'success': True, 'applied': apply, 'rows': rows, 'summary': summary,
                         'updated_ids': updated_ids, 'created_ids': created_ids})


@login_required
def customer_signature_folders_view(request):
    """ZIP: mỗi Mã khách hàng (9 số) một thư mục, chứa sẵn ảnh chữ ký đã chụp (chưa chụp → thư mục rỗng).
    Chọn khách theo ids=..., hoặc theo tìm kiếm + khoảng ngày."""
    from .customer_signature import signature_files
    ids = [int(x) for x in request.GET.get('ids', '').split(',') if x.strip().isdigit()]
    customers = Customer.objects.filter(pk__in=ids) if ids else _filtered_customers(request)
    folders = {}                                   # mã KH → danh sách file ảnh chữ ký
    for c in customers:
        code = _norm_code(c.ma_khach_hang)
        if code:
            folders.setdefault(code, []).extend(signature_files(c.pk))
    if not folders:
        messages.warning(request, 'Không có khách hàng nào có Mã khách hàng để tạo folder chữ ký.')
        return redirect('customer_list')

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        for code in sorted(folders):
            info = zipfile.ZipInfo(f'{code}/', date_time=datetime.now().timetuple()[:6])
            info.external_attr = (0o40775 << 16) | 0x10   # cờ thư mục (Unix + MS-DOS) → Windows hiện là folder
            z.writestr(info, '')
            for path in folders[code]:
                z.write(path, f'{code}/{path.name}')
    response = HttpResponse(buf.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="Folder_chu_ky_{datetime.now():%Y%m%d_%H%M}.zip"'
    return response

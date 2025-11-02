# 📝 CÁC BƯỚC TIẾP THEO - Dashboard Mới

## ✅ Đã hoàn thành:

1. **Thêm trường `visible_field_groups` vào Category model**
   - Cho phép admin cấu hình field groups nào hiển thị cho từng category
   - Migration đã tạo và apply thành công

2. **Redesign dashboard hoàn toàn**
   - Flow mới: Chọn Category → Chọn Template → Nhập thông tin → Download
   - Giao diện wizard 4 bước với breadcrumb
   - Form động có thể ẩn/hiện field groups dựa trên category
   - Old dashboard được backup tại `dashboard_old_backup.html`

## ⚠️ CẦN LÀM TIẾP:

### 1. Tạo API endpoint: `/api/categories/<id>/templates/`

Thêm vào `templates_app/views.py`:

```python
@login_required
@require_http_methods(["GET"])
def category_templates_api(request, category_id):
    """
    API trả về danh sách templates và visible_field_groups của category
    """
    try:
        category = Category.objects.get(pk=category_id)

        # Get templates trong category (có quyền truy cập)
        user = request.user
        if user.is_superuser:
            templates = category.templates.filter(is_active=True)
        else:
            user_groups = user.groups.all()
            templates = category.templates.filter(
                is_active=True
            ).filter(
                Q(allowed_groups__isnull=True) |
                Q(allowed_groups__in=user_groups)
            ).distinct()

        templates_data = [{
            'id': t.id,
            'name': t.name,
            'description': t.description
        } for t in templates]

        return JsonResponse({
            'success': True,
            'templates': templates_data,
            'visible_field_groups': category.get_visible_field_groups()
        })
    except Category.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Category not found'}, status=404)
```

### 2. Tạo API endpoint: `/template/<id>/generate-direct/`

Thêm vào `templates_app/views.py`:

```python
from datetime import datetime

@login_required
@require_http_methods(["POST"])
def generate_document_direct(request, template_id):
    """
    Generate document trực tiếp từ form data (không cần lưu customer)
    """
    try:
        template = get_object_or_404(Template, pk=template_id)

        # Kiểm tra quyền
        if not template.user_has_access(request.user):
            return HttpResponse("Không có quyền truy cập", status=403)

        # Lấy GlobalConfig
        config = GlobalConfig.get_instance()

        # Build data dict from form
        data = {}

        # Personal info
        data['ma_khach_hang'] = request.POST.get('ma_khach_hang', '')
        data['cif'] = request.POST.get('cif', '')
        data['ho_ten'] = request.POST.get('ho_ten', '')
        data['ngay_sinh'] = request.POST.get('ngay_sinh', '')
        data['gioi_tinh'] = request.POST.get('gioi_tinh', '')

        # ID documents
        data['so_cmnd'] = request.POST.get('so_cmnd', '')
        data['ngay_cap_cmnd'] = request.POST.get('ngay_cap_cmnd', '')
        data['noi_cap_cmnd'] = request.POST.get('noi_cap_cmnd', '')

        # Contact
        data['dia_chi'] = request.POST.get('dia_chi', '')
        data['so_dien_thoai'] = request.POST.get('so_dien_thoai', '')
        data['email'] = request.POST.get('email', '')

        # Employment
        data['nghe_nghiep'] = request.POST.get('nghe_nghiep', '')
        data['noi_lam_viec'] = request.POST.get('noi_lam_viec', '')

        # Banking
        data['so_tai_khoan'] = request.POST.get('so_tai_khoan', '')
        data['loai_tai_khoan'] = request.POST.get('loai_tai_khoan', '')
        data['so_tai_khoan_yc'] = request.POST.get('so_tai_khoan_yc', '')
        data['loai_tien_te'] = request.POST.get('loai_tien_te', 'VND')

        # Card
        data['loai_the'] = request.POST.get('loai_the', '')
        data['hang_the'] = request.POST.get('hang_the', '')

        # Checkboxes - helper function
        def checkbox(value):
            return '☑' if value else '☐'

        data['phat_hanh_lan_dau'] = checkbox(request.POST.get('phat_hanh_lan_dau') == 'on')
        data['phat_hanh_lai'] = checkbox(request.POST.get('phat_hanh_lai') == 'on')

        # Service checkboxes
        data['dv_thu_ho_tien_nuoc'] = checkbox(request.POST.get('dv_thu_ho_tien_nuoc') == 'on')
        data['dv_thu_ho_tien_dien'] = checkbox(request.POST.get('dv_thu_ho_tien_dien') == 'on')
        data['dv_thu_ho_vien_thong'] = checkbox(request.POST.get('dv_thu_ho_vien_thong') == 'on')
        data['dv_sms_banking'] = checkbox(request.POST.get('dv_sms_banking') == 'on')
        data['dv_bankplus'] = checkbox(request.POST.get('dv_bankplus') == 'on')
        data['dv_e_mobile'] = checkbox(request.POST.get('dv_e_mobile') == 'on')
        data['kenh_mobile'] = checkbox(request.POST.get('kenh_mobile') == 'on')
        data['kenh_internet'] = checkbox(request.POST.get('kenh_internet') == 'on')

        # Special checkboxes
        data['the_hang_chuan'] = checkbox(data['hang_the'] == 'Hạng chuẩn')
        data['the_hang_vang'] = checkbox(data['hang_the'] == 'Hạng vàng')
        data['the_ghi_no_noi_dia'] = checkbox(data['loai_the'] == 'Thẻ Ghi nợ nội địa')
        data['tk_ngau_nhien'] = checkbox(data['loai_tai_khoan'] == 'Tài khoản ngẫu nhiên')
        data['tk_theo_yeu_cầu'] = checkbox(data['loai_tai_khoan'] == 'Tài khoản số theo yêu cầu')

        # Print info
        data['ngay_in'] = request.POST.get('ngay_in', '')

        # Date variables (from ngay_sinh)
        if data['ngay_sinh']:
            try:
                date_obj = datetime.strptime(data['ngay_sinh'], '%Y-%m-%d')
                date_str = date_obj.strftime('%d%m%Y')
                data['d1'], data['d2'] = date_str[0], date_str[1]
                data['m1'], data['m2'] = date_str[2], date_str[3]
                data['y1'], data['y2'], data['y3'], data['y4'] = date_str[4], date_str[5], date_str[6], date_str[7]
            except:
                pass

        # Branch data from GlobalConfig
        data['ten_chi_nhanh'] = config.ten_chi_nhanh
        data['ten_chi_nhanh_hoa'] = config.ten_chi_nhanh_hoa
        data['mst'] = config.mst
        data['giao_dich_vien'] = config.giao_dich_vien
        data['kiem_soat_vien'] = config.kiem_soat_vien
        data['giam_doc'] = config.giam_doc
        data['dia_chi_chi_nhanh'] = config.dia_chi_chi_nhanh

        # Custom variables
        if config.custom_variables:
            data.update(config.custom_variables)

        # Generate document
        output_file = render_word_template(template.file.path, data)

        # Return as download
        with open(output_file, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = f'attachment; filename="{template.name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx"'
            return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Lỗi: {str(e)}", status=500)
```

### 3. Cập nhật URL routes

Thêm vào `templates_app/urls.py`:

```python
# API for new dashboard
path('api/categories/<int:category_id>/templates/', views.category_templates_api, name='category_templates_api'),
path('template/<int:template_id>/generate-direct/', views.generate_document_direct, name='generate_document_direct'),
```

### 4. Cấu hình visible_field_groups cho Categories trong Admin

Truy cập Django Admin → Categories → Sửa từng category:

**Ví dụ cấu hình:**

**Category "Mở Tài Khoản"** - Hiển thị tất cả:
```json
["personal_info", "id_documents", "contact", "employment", "banking", "card", "services", "print_info"]
```

**Category "Dịch vụ Ngân hàng"** - Chỉ hiển thị một số:
```json
["personal_info", "id_documents", "banking", "services", "print_info"]
```

**Category "Thẻ"** - Chỉ thẻ:
```json
["personal_info", "id_documents", "card", "print_info"]
```

Nếu để trống `visible_field_groups`, sẽ hiển thị tất cả fields.

## 🧪 Testing

Sau khi thêm code:

1. Chạy server: `python manage.py runserver`
2. Truy cập dashboard
3. Test flow: Chọn category → Chọn template → Điền form → Download

## 📚 File Groups Available

- `personal_info`: Mã KH, CIF, Họ tên, Ngày sinh, Giới tính
- `id_documents`: CMND/CCCD, Ngày cấp, Nơi cấp
- `contact`: Địa chỉ, Điện thoại, Email
- `employment`: Nghề nghiệp, Nơi làm việc
- `banking`: Số TK, Loại TK, Loại tiền tệ
- `card`: Loại thẻ, Hạng thẻ, Phát hành
- `services`: Tất cả checkbox dịch vụ (Thu hộ, E-Banking, Kênh GD)
- `print_info`: Ngày in mẫu biểu

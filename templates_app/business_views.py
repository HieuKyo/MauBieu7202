"""
Views doanh nghiệp: danh sách, tìm kiếm, CRUD, nạp dữ liệu vào mẫu, nhập TSV.
"""

# Django imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods

# Local application imports
from .forms import BusinessForm
from .issueby_mapping import get_issueby_name
from .models import Template, Business, BranchConfig
from .utils import render_word_template
from .customer_views import parse_tsv_date


# ============================================
# Business (Doanh nghiệp) Views & APIs
# ============================================

@login_required
def business_list_view(request):
    """Danh sách doanh nghiệp với tìm kiếm"""
    search_query = request.GET.get('q', '')

    businesses = Business.objects.all()

    if search_query:
        businesses = businesses.filter(
            Q(ten_doanh_nghiep__icontains=search_query) |
            Q(cif__icontains=search_query) |
            Q(ma_so_thue__icontains=search_query) |
            Q(dien_thoai__icontains=search_query)
        )

    businesses = businesses.order_by('-created_at')

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(businesses, 20)  # 20 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'templates_app/business_list.html', context)


@login_required
def business_search_api(request):
    """API endpoint để tìm kiếm doanh nghiệp (cho AJAX)"""
    search_query = request.GET.get('q', '').strip()

    # If query is empty or too short, return all businesses (for debugging)
    if len(search_query) < 1:
        total_count = Business.objects.count()
        return JsonResponse({
            'businesses': [],
            'total_count': total_count,
            'message': f'Nhập ít nhất 1 ký tự để tìm kiếm. Tổng: {total_count} doanh nghiệp'
        })

    # Search with flexible matching
    businesses = Business.objects.filter(
        Q(ten_doanh_nghiep__icontains=search_query) |
        Q(cif__icontains=search_query) |
        Q(ma_so_thue__icontains=search_query) |
        Q(so_gcn__icontains=search_query)
    ).order_by('ten_doanh_nghiep')[:20]  # Giới hạn 20 kết quả

    business_list = [{
        'id': b.id,
        'ten_doanh_nghiep': b.ten_doanh_nghiep or '',
        'cif': b.cif or '',
        'ma_so_thue': b.ma_so_thue or '',
        'so_gcn': b.so_gcn or '',
        'display': f"{b.ten_doanh_nghiep} - CIF: {b.cif}"
    } for b in businesses]

    return JsonResponse({
        'businesses': business_list,
        'count': len(business_list),
        'query': search_query
    })


@login_required
def business_data_api(request, business_id):
    """API endpoint để lấy dữ liệu doanh nghiệp theo ID (cho auto-fill)"""
    try:
        business = Business.objects.get(id=business_id)
        return JsonResponse({
            'success': True,
            'data': business.get_data_dict()
        })
    except Business.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Không tìm thấy doanh nghiệp'
        }, status=404)


# ============================================
# Business (Doanh nghiệp) Dashboard & CRUD
# ============================================

@login_required
def business_dashboard(request):
    """Dashboard quản lý doanh nghiệp"""
    # Lấy danh sách doanh nghiệp
    businesses = Business.objects.all().order_by('-created_at')

    # Thống kê
    total_businesses = businesses.count()

    # Lấy danh sách templates liên quan đến doanh nghiệp
    user = request.user
    if user.is_superuser:
        templates = Template.objects.filter(
            is_active=True,
            name__icontains='doanh nghiệp'
        ).select_related('category').order_by('category__order', 'order', 'name')
    else:
        user_groups = user.groups.all()
        templates = Template.objects.filter(
            is_active=True,
            name__icontains='doanh nghiệp'
        ).filter(
            Q(allowed_groups__isnull=True) | Q(allowed_groups__in=user_groups)
        ).distinct().select_related('category').order_by('category__order', 'order', 'name')

    context = {
        'businesses': businesses,
        'total_businesses': total_businesses,
        'templates': templates,
    }
    return render(request, 'templates_app/business/dashboard.html', context)


@login_required
def business_create(request):
    """Tạo doanh nghiệp mới"""
    if request.method == 'POST':
        form = BusinessForm(request.POST)
        if form.is_valid():
            business = form.save()
            messages.success(request, f'Đã tạo doanh nghiệp "{business.ten_doanh_nghiep}" thành công')
            return redirect('business_dashboard')
        else:
            messages.error(request, 'Có lỗi khi tạo doanh nghiệp. Vui lòng kiểm tra lại.')
    else:
        form = BusinessForm()

    context = {
        'form': form,
        'action': 'create',
        'title': 'Tạo doanh nghiệp mới',
        # Địa danh in trên trang ảnh CCCD 2 mặt
        'dia_danh': BranchConfig.get_for_user(request.user).dia_danh,
    }
    return render(request, 'templates_app/business/form.html', context)


@login_required
def business_edit(request, business_id):
    """Sửa thông tin doanh nghiệp"""
    business = get_object_or_404(Business, pk=business_id)

    if request.method == 'POST':
        form = BusinessForm(request.POST, instance=business)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã cập nhật doanh nghiệp "{business.ten_doanh_nghiep}"')
            return redirect('business_dashboard')
        else:
            messages.error(request, 'Có lỗi khi cập nhật. Vui lòng kiểm tra lại.')
    else:
        form = BusinessForm(instance=business)

    context = {
        'form': form,
        'business': business,
        'action': 'edit',
        'title': f'Sửa doanh nghiệp: {business.ten_doanh_nghiep}',
        # Địa danh in trên trang ảnh CCCD 2 mặt
        'dia_danh': BranchConfig.get_for_user(request.user).dia_danh,
    }
    return render(request, 'templates_app/business/form.html', context)


@login_required
def business_delete(request, business_id):
    """Xóa doanh nghiệp"""
    business = get_object_or_404(Business, pk=business_id)
    ten_dn = business.ten_doanh_nghiep

    if request.method == 'POST':
        business.delete()
        messages.success(request, f'Đã xóa doanh nghiệp "{ten_dn}"')
        return redirect('business_dashboard')

    # Nếu GET, hiển thị confirm page
    context = {
        'business': business,
    }
    return render(request, 'templates_app/business/delete_confirm.html', context)


@login_required
def business_load_data(request, business_id, template_id):
    """Load dữ liệu doanh nghiệp vào template và tạo file Word"""
    # Lấy business
    business = get_object_or_404(Business, pk=business_id)

    # Lấy template và kiểm tra quyền
    template = get_object_or_404(Template, id=template_id, is_active=True)
    if not template.user_has_access(request.user):
        raise Http404("Bạn không có quyền truy cập mẫu biểu này")

    try:
        # Lấy dữ liệu từ business
        data = business.get_data_dict()

        # Thêm biến chung (chi nhánh + custom variables)
        branch_config = BranchConfig.get_for_user(request.user)
        data.update(branch_config.get_all_variables())

        # Render template Word với dữ liệu
        template_path = template.file.path
        output_stream = render_word_template(template_path, data)

        # Trả về file Word
        response = HttpResponse(
            output_stream.read(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        # Tạo filename với ngày tháng
        from datetime import datetime
        from urllib.parse import quote
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{template.name}_{business.ten_doanh_nghiep}_{business.cif}_{date_str}.docx"
        filename_encoded = quote(filename)
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{filename_encoded}"

        return response

    except Exception as e:
        messages.error(request, f"Lỗi khi tạo file Word: {str(e)}")
        return redirect('business_dashboard')


@login_required
@require_http_methods(["POST"])
def business_import_tsv(request):
    """
    Import doanh nghiệp từ TSV data (paste trực tiếp từ AGRIBANK)
    Hỗ trợ paste trực tiếp dữ liệu từ AGRIBANK vào textarea
    """
    # Get pasted TSV data from textarea
    tsv_data = request.POST.get('tsv_data', '').strip()

    if not tsv_data:
        return JsonResponse({
            'success': False,
            'error': 'Vui lòng paste dữ liệu TSV từ AGRIBANK'
        }, status=400)

    try:
        # Parse content
        lines = tsv_data.strip().split('\n')

        if len(lines) < 2:
            return JsonResponse({
                'success': False,
                'error': 'Dữ liệu không hợp lệ hoặc không có dữ liệu'
            }, status=400)

        # Parse header
        header = lines[0].strip().split('\t')

        success_count = 0
        error_count = 0
        errors = []
        updated_count = 0

        # Process each data line
        for line_num, line in enumerate(lines[1:], start=2):
            try:
                values = line.strip().split('\t')

                # Create dict from header and values
                data = {}
                for i, field in enumerate(header):
                    data[field] = values[i] if i < len(values) else ''

                # Clean values
                def clean(val):
                    return str(val).strip() if val else ''

                # Extract required fields
                custno = clean(data.get('custno', ''))
                nmloc = clean(data.get('nmloc', ''))  # Tên doanh nghiệp tiếng Việt
                busno = clean(data.get('busno', ''))  # Số GCN/ĐKKD từ busno
                taxno = clean(data.get('taxno', ''))  # Mã số thuế

                # Validate required fields
                if not custno:
                    errors.append(f'Dòng {line_num}: Thiếu mã CIF')
                    error_count += 1
                    continue

                if not nmloc:
                    errors.append(f'Dòng {line_num}: Thiếu tên doanh nghiệp')
                    error_count += 1
                    continue

                # Check if business already exists by CIF
                if Business.objects.filter(cif=custno).exists():
                    business = Business.objects.get(cif=custno)
                    update_mode = True
                else:
                    business = Business()
                    update_mode = False

                # Map basic fields
                business.cif = custno
                business.ten_doanh_nghiep = nmloc

                # Số tài khoản (nếu có)
                so_tai_khoan = clean(data.get('bkcd', ''))
                if so_tai_khoan:
                    business.so_tai_khoan = so_tai_khoan

                # Số GCN/ĐKKD từ busno
                # Đơn vị không có GPKD/MST (trường học...) phải lưu NULL, không lưu ''
                # vì so_gcn/ma_so_thue là unique -> '' thứ 2 sẽ bị lỗi UNIQUE
                if not business.so_gcn:
                    business.so_gcn = None
                if not business.ma_so_thue:
                    business.ma_so_thue = None
                if busno:
                    business.so_gcn = busno
                    # Xác định loại giấy tờ dựa trên custdtltpcd
                    custdtltpcd = clean(data.get('custdtltpcd', ''))
                    if 'TNHH' in custdtltpcd:
                        business.loai_giay_to = 'GCN'
                    else:
                        business.loai_giay_to = 'GCN'

                # Ngày cấp GCN (issuedt4)
                ngay_cap_gcn_str = clean(data.get('issuedt4', ''))
                if ngay_cap_gcn_str:
                    ngay_cap_gcn = parse_tsv_date(ngay_cap_gcn_str)
                    if ngay_cap_gcn:
                        business.ngay_cap_gcn = ngay_cap_gcn

                # Nơi cấp GCN (issueby4)
                noi_cap_gcn_code = clean(data.get('issueby4', ''))
                if noi_cap_gcn_code:
                    noi_cap_gcn_name = get_issueby_name(noi_cap_gcn_code)
                    business.noi_cap_gcn = noi_cap_gcn_name

                # Mã số thuế
                if taxno:
                    business.ma_so_thue = taxno

                # Ngày cấp MST (issuedt6)
                ngay_cap_mst_str = clean(data.get('issuedt6', ''))
                if ngay_cap_mst_str:
                    ngay_cap_mst = parse_tsv_date(ngay_cap_mst_str)
                    if ngay_cap_mst:
                        business.ngay_cap_mst = ngay_cap_mst

                # Nơi cấp MST (issueby6)
                noi_cap_mst_code = clean(data.get('issueby6', ''))
                if noi_cap_mst_code:
                    noi_cap_mst_name = get_issueby_name(noi_cap_mst_code)
                    business.noi_cap_mst = noi_cap_mst_name

                # Địa chỉ
                dia_chi = clean(data.get('addr1loc', ''))
                if dia_chi:
                    business.dia_chi = dia_chi

                # Điện thoại
                telno = clean(data.get('telno', ''))
                if telno:
                    business.dien_thoai = telno

                # Lĩnh vực kinh doanh (từ profnm hoặc custdtltpcd)
                linh_vuc = clean(data.get('profnm', ''))
                if not linh_vuc:
                    linh_vuc = clean(data.get('custdtltpcd', ''))
                if linh_vuc:
                    business.linh_vuc_kinh_doanh = linh_vuc

                # Save business
                business.save()

                if update_mode:
                    updated_count += 1
                else:
                    success_count += 1

            except Exception as e:
                error_count += 1
                errors.append(f'Dòng {line_num}: {str(e)}')
                continue

        return JsonResponse({
            'success': True,
            'message': f'Import thành công: {success_count} doanh nghiệp mới, {updated_count} cập nhật',
            'imported': success_count,
            'updated': updated_count,
            'errors': error_count,
            'error_details': errors[:10]  # Limit to 10 errors
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Lỗi khi xử lý dữ liệu: {str(e)}'
        }, status=500)

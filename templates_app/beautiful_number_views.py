"""
Views số đẹp: tra cứu phí, sinh và làm mới danh sách số đẹp, xuất CSV.
"""

# Django imports
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


# ====================
# Beautiful Number Fee Lookup Views
# ====================

@login_required
def beautiful_number_lookup(request):
    """
    Trang tra cứu phí số đẹp.
    Cho phép nhập số tài khoản hoặc số lượng số đẹp để tra cứu phí.
    """
    result = None
    error = None
    lookup_type = 'detailed'  # Default: Bảng 1 (chi tiết)

    if request.method == 'POST':
        lookup_type = request.POST.get('lookup_type', 'detailed')

        if lookup_type == 'detailed':
            # Tra cứu theo biểu phí chi tiết (Bảng 1)
            account_number = request.POST.get('account_number', '').strip()

            if not account_number:
                error = 'Vui lòng nhập số tài khoản'
            else:
                from .beautiful_number_services import get_detailed_fee
                result = get_detailed_fee(account_number)

        elif lookup_type == 'on_request':
            # Tra cứu theo biểu phí chọn số (Bảng 2)
            try:
                quantity = int(request.POST.get('quantity', 0))
                if quantity < 2:
                    error = 'Số lượng số đẹp phải từ 2 trở lên'
                else:
                    from .beautiful_number_services import get_on_request_fee
                    result = get_on_request_fee(quantity)
            except (ValueError, TypeError):
                error = 'Vui lòng nhập số lượng hợp lệ'

    # Lấy danh sách biểu phí để hiển thị
    from .models import DetailedFeeTier, OnRequestFeeTier

    detailed_tiers = DetailedFeeTier.objects.all().order_by('quantity', 'fee_type')
    on_request_tiers = OnRequestFeeTier.objects.all().order_by('min_quantity')

    context = {
        'result': result,
        'error': error,
        'lookup_type': lookup_type,
        'detailed_tiers': detailed_tiers,
        'on_request_tiers': on_request_tiers,
    }

    return render(request, 'templates_app/beautiful_number_lookup.html', context)


# ========== BEAUTIFUL NUMBER GENERATOR FUNCTIONS ==========

def get_price_tier_from_fee(fee_vat):
    """
    Map phí (có VAT) vào price_tier tương ứng.
    Các ngưỡng (1.1M/3.3M/5.5M/11M/22M) khớp với fee_max_vat của từng bậc trong
    OFFICIAL_FEE_TABLE — vì vậy PHẢI truyền `fee_max_vat` (không phải fee_min_vat),
    nếu không 2 bậc liền kề có cùng fee_min sẽ bị gộp nhầm vào 1 tier.

    Args:
        fee_vat: Phí tối đa (fee_max_vat) đã bao gồm VAT; dùng fee_min_vat nếu fee_max là None

    Returns:
        Price tier code (PRICE_500K_1M, PRICE_1M_3M, etc.)
    """
    from .models import BeautifulNumber

    if fee_vat <= 1_100_000:
        return BeautifulNumber.PRICE_500K_1M
    elif fee_vat <= 3_300_000:
        return BeautifulNumber.PRICE_1M_3M
    elif fee_vat <= 5_500_000:
        return BeautifulNumber.PRICE_3M_5M
    elif fee_vat <= 11_000_000:
        return BeautifulNumber.PRICE_5M_10M
    elif fee_vat <= 22_000_000:
        return BeautifulNumber.PRICE_10M_20M
    else:
        return BeautifulNumber.PRICE_20M_PLUS


def get_category_from_generator_type(gen_type, analysis):
    """
    Map loại generator và analysis sang category trong model

    Args:
        gen_type: 'lap', 'tien', 'ganh', 'lap_kep', 'ngau_nhien', 'loc_phat', 'phong_thuy', 'hop_tuoi', 'cao_cap'
        analysis: Kết quả từ analyze_account_number

    Returns:
        Category code
    """
    from .models import BeautifulNumber

    # Ưu tiên dựa vào analysis nếu là số đặc biệt
    if analysis.get('is_special'):
        return BeautifulNumber.CATEGORY_DAC_BIET

    # Map theo loại generator
    category_map = {
        'lap': BeautifulNumber.CATEGORY_SO_LAP,
        'tien': BeautifulNumber.CATEGORY_SO_TIEN,
        'ganh': BeautifulNumber.CATEGORY_SO_DOI_XUNG,
        'lap_kep': BeautifulNumber.CATEGORY_SO_LAP,
        'loc_phat': BeautifulNumber.CATEGORY_LOC_PHAT,
        'phong_thuy': BeautifulNumber.CATEGORY_PHONG_THUY,
        'hop_tuoi': BeautifulNumber.CATEGORY_HOP_TUOI,
        'cao_cap': BeautifulNumber.CATEGORY_DAC_BIET,  # Số cao cấp -> Đặc biệt
        'ngau_nhien': BeautifulNumber.CATEGORY_TAI_LOC,  # Số thường -> Tài lộc
    }

    return category_map.get(gen_type, BeautifulNumber.CATEGORY_TAI_LOC)


def generate_and_save_beautiful_numbers(count_per_type=50, clear_existing=False):
    """
    Tạo số đẹp tự động và lưu vào database

    Args:
        count_per_type: Số lượng mỗi loại (mặc định 50)
        clear_existing: Xóa các số hiện có trước khi tạo mới (mặc định False)

    Returns:
        Dict với thống kê kết quả
    """
    from .models import BeautifulNumber
    from . import beautiful_number_generator as bng
    from .beautiful_number_services import analyze_account_number

    stats = {
        'created': 0,
        'skipped': 0,
        'errors': 0,
        'by_type': {}
    }

    # Xóa số cũ nếu được yêu cầu
    if clear_existing:
        deleted_count = BeautifulNumber.objects.all().delete()[0]
        stats['deleted'] = deleted_count

    # Định nghĩa các loại generator
    generator_types = {
        'lap': (bng.gen_so_lap, 20),  # Chỉ có 20 số lặp tối đa
        'tien': (bng.gen_so_tien, 15),  # Chỉ có 15 số tiến
        'ganh': (bng.gen_so_ganh, count_per_type),
        'lap_kep': (bng.gen_so_lap_kep, count_per_type),
        'loc_phat': (bng.gen_so_loc_phat, count_per_type),  # Số Lộc Phát (6,8)
        'phong_thuy': (bng.gen_so_phong_thuy, count_per_type),  # Số Phong Thủy
        'hop_tuoi': (bng.gen_so_hop_tuoi, count_per_type),  # Số Hợp Tuổi
        'cao_cap': (bng.gen_so_cao_cap, min(count_per_type, 50)),  # Số cao cấp (giá cao)
        'ngau_nhien': (bng.gen_so_ngau_nhien, count_per_type),
    }

    # Tạo số cho từng loại
    for gen_type, (generator_func, count) in generator_types.items():
        type_stats = {
            'created': 0,
            'skipped': 0,
            'errors': 0
        }

        try:
            # Tạo số
            numbers = bng.generate_numbers(generator_func, count)

            for num in numbers:
                try:
                    # Phân tích số
                    analysis = analyze_account_number(num)

                    # Bỏ qua nếu có lỗi
                    if analysis.get('error'):
                        type_stats['errors'] += 1
                        continue

                    # Xác định category và price_tier
                    category = get_category_from_generator_type(gen_type, analysis)
                    price_tier = get_price_tier_from_fee(analysis['fee_max_vat'] or analysis['fee_min_vat'])

                    # Tạo hoặc cập nhật số trong database
                    beautiful_num, created = BeautifulNumber.objects.get_or_create(
                        account_number=num,
                        defaults={
                            'category': category,
                            'price_tier': price_tier,
                            'fee': analysis['fee_min_vat'],
                            'description': analysis['description'],
                            'is_available': True,
                        }
                    )

                    if created:
                        type_stats['created'] += 1
                        stats['created'] += 1
                    else:
                        type_stats['skipped'] += 1
                        stats['skipped'] += 1

                except Exception as e:
                    type_stats['errors'] += 1
                    stats['errors'] += 1
                    print(f"Error processing number {num}: {e}")

            stats['by_type'][gen_type] = type_stats

        except Exception as e:
            stats['by_type'][gen_type] = {
                'created': 0,
                'skipped': 0,
                'errors': count,
                'error_message': str(e)
            }
            stats['errors'] += count

    return stats


@login_required
@require_http_methods(["POST"])
def generate_beautiful_numbers_ajax(request):
    """
    AJAX endpoint để tạo số đẹp tự động
    """
    try:
        # Lấy tham số từ request
        count_per_type = int(request.POST.get('count_per_type', 50))
        clear_existing = request.POST.get('clear_existing', 'false').lower() == 'true'

        # Giới hạn số lượng để tránh quá tải
        count_per_type = min(count_per_type, 200)

        # Tạo số đẹp
        stats = generate_and_save_beautiful_numbers(count_per_type, clear_existing)

        return JsonResponse({
            'success': True,
            'message': f'Đã tạo {stats["created"]} số mới, bỏ qua {stats["skipped"]} số trùng',
            'stats': stats
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def refresh_beautiful_numbers_ajax(request):
    """
    AJAX endpoint để cập nhật lại category/price_tier/fee cho toàn bộ kho số đẹp
    theo engine tính phí hiện tại (không xóa/thêm số nào).
    """
    from .beautiful_number_generator import refresh_all_beautiful_numbers

    try:
        stats = refresh_all_beautiful_numbers(dry_run=False)
        return JsonResponse({
            'success': True,
            'message': (
                f'Đã kiểm tra {stats["total"]} số, cập nhật {stats["updated"]} số '
                f'({stats["changed_fee"]} đổi phí, {stats["changed_tier"]} đổi bậc giá, '
                f'{stats["changed_category"]} nâng lên Đặc biệt).'
            ),
            'stats': stats,
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=500)


def _filter_beautiful_numbers(request):
    """Áp dụng các filter (category/price/available/pattern) lên BeautifulNumber, trả về (queryset, filters)"""
    from .models import BeautifulNumber

    category_filter = request.GET.get('category', '')
    price_filter = request.GET.get('price', '')
    available_only = request.GET.get('available', 'true') == 'true'
    pattern_filter = request.GET.get('pattern', '').strip()

    numbers_queryset = BeautifulNumber.objects.all()

    if available_only:
        numbers_queryset = numbers_queryset.filter(is_available=True)

    if category_filter:
        numbers_queryset = numbers_queryset.filter(category=category_filter)

    if price_filter:
        numbers_queryset = numbers_queryset.filter(price_tier=price_filter)

    # Pattern search - convert * to regex wildcard
    # Example: "7202***777***" -> matches numbers with 777 in the middle
    if pattern_filter:
        regex_pattern = ''
        for char in pattern_filter:
            if char == '*':
                regex_pattern += r'\d'  # Match any single digit
            elif char.isdigit():
                regex_pattern += char
            # Ignore other characters

        if regex_pattern:
            numbers_queryset = numbers_queryset.filter(account_number__regex=f'^{regex_pattern}$')

    numbers_queryset = numbers_queryset.order_by('price_tier', 'category', 'account_number')

    filters = {
        'category_filter': category_filter,
        'price_filter': price_filter,
        'available_only': available_only,
        'pattern_filter': pattern_filter,
    }
    return numbers_queryset, filters


def _enrich_beautiful_numbers(numbers, request):
    """
    Gắn fee_min/fee_max (từ analyze_account_number) vào từng số, và nếu có tham số `dob`
    (ngày sinh khách hàng), tính mệnh + gắn menh_hop_count/menh_ky_count/menh_verdict.
    Nếu `menh_only=true`, chỉ giữ lại các số hợp mệnh (hop_count > ky_count).
    Trả về (numbers_đã_lọc, menh_info hoặc None, dob_str, menh_only).
    """
    from datetime import datetime
    from .beautiful_number_services import analyze_account_number
    from .menh_calculator import calculate_menh, menh_verdict

    dob_str = request.GET.get('dob', '').strip()
    menh_only = request.GET.get('menh_only', '') == 'true'
    menh_info = None
    if dob_str:
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            menh_info = calculate_menh(dob)
        except ValueError:
            dob_str = ''

    result = []
    for number in numbers:
        analysis = analyze_account_number(number.account_number)
        number.fee_min = int(analysis.get('fee_min_vat') or number.fee)
        fee_max_vat = analysis.get('fee_max_vat')
        number.fee_max = int(fee_max_vat) if fee_max_vat is not None else None

        if menh_info:
            suffix = number.account_number[4:]
            hop_count = sum(1 for c in suffix if int(c) in menh_info['hop_digits'])
            ky_count = sum(1 for c in suffix if int(c) in menh_info['ky_digits'])
            number.menh_hop_count = hop_count
            number.menh_ky_count = ky_count
            number.menh_verdict = menh_verdict(menh_info['hanh'], hop_count, ky_count)
            if menh_only and not (hop_count > ky_count):
                continue

        result.append(number)

    return result, menh_info, dob_str, menh_only


def _generate_menh_suggestions(menh_info, target_tier, limit=30):
    """
    Sinh danh sách gợi ý số hợp mệnh (chưa chắc có sẵn trong kho) theo mức phí mong muốn.
    Loại bỏ ứng viên đã tồn tại trong kho và đã bán (is_available=False).
    """
    from .beautiful_number_services import analyze_account_number, generate_menh_candidates
    from .models import BeautifulNumber

    candidates = generate_menh_candidates(menh_info['hop_digits'])
    full_numbers = ['7202' + c for c in candidates]

    existing = {
        bn.account_number: bn.is_available
        for bn in BeautifulNumber.objects.filter(account_number__in=full_numbers)
    }

    suggestions = []
    for full in full_numbers:
        if existing.get(full) is False:
            continue  # đã bán, không gợi ý

        analysis = analyze_account_number(full)
        if analysis.get('error'):
            continue

        tier = get_price_tier_from_fee(analysis['fee_max_vat'] or analysis['fee_min_vat'])
        if target_tier and tier != target_tier:
            continue

        suggestions.append({
            'account_number': full,
            'description': analysis['description'],
            'fee_min': analysis['fee_min_vat'],
            'fee_max': analysis['fee_max_vat'],
            'price_tier': tier,
            'in_stock': full in existing,
        })

    suggestions.sort(key=lambda s: (s['fee_min'], s['fee_max'] or 10 ** 12), reverse=True)
    return suggestions[:limit]


@login_required
def beautiful_number_list(request):
    """
    Trang danh sách số đẹp có sẵn để khách hàng chọn.
    Có filter theo giá, loại số đẹp, mẫu số, và tư vấn hợp mệnh theo năm sinh. Có thể in ra / xuất CSV.
    """
    from .models import BeautifulNumber

    numbers_queryset, filters = _filter_beautiful_numbers(request)
    numbers, menh_info, dob_str, menh_only = _enrich_beautiful_numbers(list(numbers_queryset), request)

    category_choices = BeautifulNumber.CATEGORY_CHOICES
    price_choices = BeautifulNumber.PRICE_TIER_CHOICES

    from collections import defaultdict
    numbers_by_price = defaultdict(list)
    for number in numbers:
        numbers_by_price[number.price_tier].append(number)

    suggest_price = request.GET.get('suggest_price', '')
    suggestions = _generate_menh_suggestions(menh_info, suggest_price) if menh_info else []

    context = {
        'numbers': numbers,
        'numbers_by_price': dict(numbers_by_price),
        'category_choices': category_choices,
        'price_choices': price_choices,
        'selected_category': filters['category_filter'],
        'selected_price': filters['price_filter'],
        'available_only': filters['available_only'],
        'pattern_filter': filters['pattern_filter'],
        'menh_info': menh_info,
        'dob': dob_str,
        'menh_only': menh_only,
        'suggestions': suggestions,
        'suggest_price': suggest_price,
    }

    return render(request, 'templates_app/beautiful_number_list.html', context)


@login_required
def beautiful_number_list_export_csv(request):
    """Xuất CSV danh sách số đẹp đang lọc trên trang beautiful_number_list (giữ nguyên filter hiện tại)"""
    import csv

    numbers_queryset, _filters = _filter_beautiful_numbers(request)
    numbers, menh_info, _dob_str, _menh_only = _enrich_beautiful_numbers(list(numbers_queryset), request)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="danh_sach_so_dep.csv"'
    response.write('﻿')  # BOM để Excel đọc đúng tiếng Việt

    writer = csv.writer(response)
    header = ['STT', 'Số tài khoản', 'Loại số đẹp', 'Phí tối thiểu (VNĐ)', 'Phí tối đa (VNĐ)', 'Trạng thái']
    if menh_info:
        header.append('Mức độ hợp mệnh')
    writer.writerow(header)

    for idx, number in enumerate(numbers, 1):
        row = [
            idx,
            f'="{number.account_number}"',
            number.get_category_display(),
            number.fee_min,
            number.fee_max if number.fee_max is not None else 'Thỏa thuận',
            'Còn' if number.is_available else 'Hết',
        ]
        if menh_info:
            row.append(getattr(number, 'menh_verdict', ''))
        writer.writerow(row)

    return response

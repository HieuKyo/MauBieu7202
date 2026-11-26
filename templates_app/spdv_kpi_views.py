"""
Thống kê chỉ tiêu Sản phẩm dịch vụ (SPDV) — Kế toán Ngân quỹ.
Tổng hợp 2 chỉ tiêu (Số lượng thẻ, Agribank Plus) theo GDV/phòng ban theo tháng/quý,
so sánh với chỉ tiêu do Trưởng phòng/Admin đặt.
"""
import calendar
import io
from datetime import date

import openpyxl
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from openpyxl.styles import Alignment, Font, PatternFill

from .models import SPDVKpiDetail, SPDVKpiRecord, SPDVKpiTarget, UserProfile
from .spdv_kpi_processor import (
    counts_from_df, emobile_count_for, filter_by_customer_codes, mobile_banking_count_for,
    parse_csp_file, parse_emobile_file, parse_loan_customers, parse_sms_file,
    parse_spdv_quarter_file, parse_visa_file, rows_for_user_period, the_count_for,
)

GROUP_KE_TOAN = "Phòng Kế toán Ngân quỹ"
GROUP_KHACH_HANG = "Phòng Khách hàng"
GROUP_PGD_LANG_TRON = "PGD Láng Tròn"
GROUP_PGD_P1 = "PGD Phường 1"
ALL_GROUPS = [GROUP_KE_TOAN, GROUP_KHACH_HANG, GROUP_PGD_LANG_TRON, GROUP_PGD_P1]


def spdv_group_of(profile):
    """Suy ra 'phòng' của 1 UserProfile từ branch (ưu tiên nếu là PGD) + department (nếu ở Hội sở)."""
    if not profile:
        return None
    if profile.branch == 'PGD_LANG_TRON':
        return GROUP_PGD_LANG_TRON
    if profile.branch == 'PGD_P1':
        return GROUP_PGD_P1
    if profile.branch == 'HOI_SO':
        if profile.department == 'KE_TOAN':
            return GROUP_KE_TOAN
        if profile.department == 'KHACH_HANG':
            return GROUP_KHACH_HANG
    return None


def check_spdv_view_scope(user):
    """
    Trả về danh sách 'phòng' mà user được xem, hoặc None nếu không có quyền xem gì.
    Admin/Ban giám đốc: xem tất cả. Trưởng/Phó phòng: chỉ xem phòng của họ.
    """
    if user.is_superuser:
        return ALL_GROUPS
    profile = getattr(user, 'profile', None)
    if not profile:
        return None
    if profile.department == 'BAN_GIAM_DOC':
        return ALL_GROUPS
    if profile.position in ('TRUONG_PHONG', 'PHO_PHONG'):
        own_group = spdv_group_of(profile)
        return [own_group] if own_group else None
    return None


def check_spdv_manage_scope(user):
    """Trả về danh sách 'phòng' mà user được đặt chỉ tiêu/import dữ liệu, hoặc None nếu không có quyền."""
    if user.is_superuser:
        return ALL_GROUPS
    profile = getattr(user, 'profile', None)
    if not profile:
        return None
    if profile.position == 'TRUONG_PHONG':
        own_group = spdv_group_of(profile)
        return [own_group] if own_group else None
    return None


def _spdv_target_profiles_qs():
    """
    Danh sách người được đặt/xem chỉ tiêu SPDV trong 1 phòng: GDV + Phó phòng
    (Trưởng phòng đặt chỉ tiêu cho toàn bộ phòng mình, bao gồm cả các phó phòng).
    """
    return UserProfile.objects.filter(
        Q(job_function='GIAO_DICH_VIEN') | Q(position='PHO_PHONG')
    ).select_related('user')


def _gdv_profiles_in_groups(groups):
    """Danh sách UserProfile (GDV + Phó phòng) thuộc các 'phòng' trong `groups`, đã gán vào đúng group."""
    profiles = _spdv_target_profiles_qs().order_by('full_name')

    result = {g: [] for g in groups}
    for p in profiles:
        g = spdv_group_of(p)
        if g in result:
            result[g].append(p)
    return result


def _month_list_for_period(year, month, quarter):
    """Trả về list các (year, month) cần cộng dồn — 1 tháng, hoặc cả quý nếu có `quarter`."""
    if quarter:
        start_month = (quarter - 1) * 3 + 1
        return [(year, m) for m in range(start_month, start_month + 3)]
    return [(year, month)]


def _date_range_for_periods(periods):
    """Khoảng ngày [đầu tháng đầu tiên, cuối tháng cuối cùng] bao trùm toàn bộ `periods`."""
    first_year, first_month = periods[0]
    last_year, last_month = periods[-1]
    start_date = date(first_year, first_month, 1)
    last_day = calendar.monthrange(last_year, last_month)[1]
    end_date = date(last_year, last_month, last_day)
    return start_date, end_date


def _parse_period_from_post(request):
    """Đọc year + (month hoặc quarter) từ POST, trả về (periods, error_message|None)."""
    try:
        year = int(request.POST.get('year'))
    except (ValueError, TypeError):
        return None, 'Năm không hợp lệ'

    quarter_str = (request.POST.get('quarter') or '').strip()
    if quarter_str:
        try:
            quarter = int(quarter_str)
        except ValueError:
            return None, 'Quý không hợp lệ'
        if not (1 <= quarter <= 4):
            return None, 'Quý phải từ 1 đến 4'
        return _month_list_for_period(year, None, quarter), None

    try:
        month = int(request.POST.get('month'))
    except (ValueError, TypeError):
        return None, 'Tháng không hợp lệ'
    if not (1 <= month <= 12):
        return None, 'Tháng phải từ 1 đến 12'
    return _month_list_for_period(year, month, None), None


@login_required
def spdv_kpi_dashboard(request):
    """Trang xem Thống kê chỉ tiêu SPDV theo phòng — Đạt / Chỉ tiêu / Còn thiếu."""
    view_scope = check_spdv_view_scope(request.user)
    if view_scope is None:
        messages.error(request, 'Bạn không có quyền truy cập trang này')
        return redirect('dashboard')

    today = date.today()

    # Lần đầu vào trang (không có tham số lọc nào trên URL) → mặc định hiển thị quý TRƯỚC,
    # thay vì tháng hiện tại.
    if not request.GET:
        current_quarter = (today.month - 1) // 3 + 1
        if current_quarter == 1:
            year, quarter, month = today.year - 1, 4, today.month
        else:
            year, quarter, month = today.year, current_quarter - 1, today.month
    else:
        try:
            year = int(request.GET.get('year', today.year))
        except (ValueError, TypeError):
            year = today.year
        quarter_str = request.GET.get('quarter', '').strip()
        quarter = None
        if quarter_str:
            try:
                q = int(quarter_str)
                if 1 <= q <= 4:
                    quarter = q
            except ValueError:
                pass
        try:
            month = int(request.GET.get('month', today.month))
            if not (1 <= month <= 12):
                month = today.month
        except (ValueError, TypeError):
            month = today.month

    periods = _month_list_for_period(year, month, quarter)
    manage_scope = check_spdv_manage_scope(request.user)

    groups_data = _gdv_profiles_in_groups(view_scope)
    groups = []
    for group_name in view_scope:
        gdv_rows = []
        for profile in groups_data.get(group_name, []):
            row = {'profile': profile, 'user_id': profile.user_id, 'metrics': {}}
            for metric_type, metric_label in SPDVKpiRecord.METRIC_CHOICES:
                actual = sum(
                    SPDVKpiRecord.objects.filter(
                        user=profile.user, metric_type=metric_type, year=y, month=m
                    ).values_list('quantity', flat=True).first() or 0
                    for y, m in periods
                )
                target = sum(
                    SPDVKpiTarget.objects.filter(
                        user=profile.user, metric_type=metric_type, year=y, month=m
                    ).values_list('target_quantity', flat=True).first() or 0
                    for y, m in periods
                )
                row['metrics'][metric_type] = {
                    'key': metric_type,
                    'label': metric_label,
                    'actual': actual,
                    'target': target,
                    'remaining': max(target - actual, 0),
                }
            # Danh sách theo đúng thứ tự METRIC_CHOICES, để template loop song song với metric_choices
            row['metrics_list'] = [row['metrics'][k] for k, _ in SPDVKpiRecord.METRIC_CHOICES]
            gdv_rows.append(row)

        # Hàng tổng cộng toàn phòng — cộng dồn Thực hiện/Chỉ tiêu theo từng chỉ tiêu qua tất cả GDV
        group_metric_totals = {}
        for metric_type, metric_label in SPDVKpiRecord.METRIC_CHOICES:
            actual = sum(r['metrics'][metric_type]['actual'] for r in gdv_rows)
            target = sum(r['metrics'][metric_type]['target'] for r in gdv_rows)
            group_metric_totals[metric_type] = {
                'key': metric_type,
                'label': metric_label,
                'actual': actual,
                'target': target,
                'remaining': max(target - actual, 0),
            }
        group_totals_list = [group_metric_totals[k] for k, _ in SPDVKpiRecord.METRIC_CHOICES]

        groups.append({
            'name': group_name,
            'can_manage': manage_scope is not None and group_name in manage_scope,
            'gdv_rows': gdv_rows,
            'totals_list': group_totals_list,
        })

    context = {
        'groups': groups,
        'year': year,
        'month': month,
        'quarter': quarter,
        'can_manage_any': manage_scope is not None,
        'year_range': range(today.year - 2, today.year + 1),
        'metric_choices': SPDVKpiRecord.METRIC_CHOICES,
    }
    return render(request, 'templates_app/spdv_kpi/dashboard.html', context)


@login_required
@require_http_methods(["POST"])
def spdv_kpi_import(request):
    """
    Import file CSP/Visa/E-Mobile/SMS Banking (+ danh sách khách hàng vay MSIT80 để loại trừ),
    theo 1 tháng hoặc cả quý (1 file phủ 3 tháng). Ghi đè kết quả SPDVKpiRecord cho từng tháng
    thực tế có trong khoảng đã chọn (không cộng dồn — an toàn khi import lại).
    """
    manage_scope = check_spdv_manage_scope(request.user)
    if manage_scope is None:
        messages.error(request, 'Bạn không có quyền import dữ liệu')
        return redirect('spdv_kpi_dashboard')

    periods, error = _parse_period_from_post(request)
    if error:
        messages.error(request, error)
        return redirect('spdv_kpi_dashboard')

    csp_file = request.FILES.get('csp_file')
    visa_file = request.FILES.get('visa_file')
    emobile_file = request.FILES.get('emobile_file')
    sms_file = request.FILES.get('sms_file')
    msit80_file = request.FILES.get('msit80_file')
    spdv_quarter_file = request.FILES.get('spdv_quarter_file')

    if not any([csp_file, visa_file, emobile_file, sms_file]):
        messages.error(request, 'Vui lòng chọn ít nhất 1 file để import')
        return redirect('spdv_kpi_dashboard')

    start_date, end_date = _date_range_for_periods(periods)

    try:
        excluded_customers = parse_loan_customers(msit80_file) if msit80_file else None
        csp_df = parse_csp_file(csp_file, start_date, end_date, excluded_customers) if csp_file else None
        visa_df = parse_visa_file(visa_file, start_date, end_date) if visa_file else None
        emobile_df = parse_emobile_file(emobile_file, start_date, end_date, excluded_customers) if emobile_file else None
        sms_df = parse_sms_file(sms_file, start_date, end_date, excluded_customers) if sms_file else None
        tk_plus_customers, ott_customers = parse_spdv_quarter_file(spdv_quarter_file) if spdv_quarter_file else (set(), set())
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('spdv_kpi_dashboard')

    csp_counts = counts_from_df(csp_df) if csp_df is not None else {}
    visa_counts = counts_from_df(visa_df) if visa_df is not None else {}
    emobile_counts = counts_from_df(emobile_df) if emobile_df is not None else {}
    sms_counts = counts_from_df(sms_df) if sms_df is not None else {}

    tk_plus_df = filter_by_customer_codes(emobile_df, tk_plus_customers) if emobile_file and spdv_quarter_file else None
    ott_df = filter_by_customer_codes(emobile_df, ott_customers) if emobile_file and spdv_quarter_file else None
    tk_plus_counts = counts_from_df(tk_plus_df) if tk_plus_df is not None else {}
    ott_counts = counts_from_df(ott_df) if ott_df is not None else {}

    profiles = _spdv_target_profiles_qs()
    the_updated = 0
    plus_updated = 0
    mobile_updated = 0
    tk_plus_updated = 0
    ott_updated = 0
    with transaction.atomic():
        for profile in profiles:
            if spdv_group_of(profile) not in manage_scope:
                continue

            for year, month in periods:
                if csp_file or visa_file:
                    the_qty = the_count_for(csp_counts, visa_counts, profile, year, month)
                    SPDVKpiRecord.objects.update_or_create(
                        user=profile.user, metric_type='THE', year=year, month=month,
                        defaults={'quantity': the_qty, 'updated_by': request.user}
                    )
                    the_updated += 1

                    SPDVKpiDetail.objects.filter(
                        user=profile.user, metric_type='THE', year=year, month=month
                    ).delete()
                    the_rows = []
                    if csp_df is not None and profile.csp_cuser:
                        the_rows += [
                            SPDVKpiDetail(
                                user=profile.user, metric_type='THE', year=year, month=month,
                                source='CSP', transaction_date=r['date'], customer_code=r['customer_code'],
                                customer_name=r['customer_name'], account_number=r['account_number'],
                            )
                            for r in rows_for_user_period(csp_df, profile.csp_cuser.strip().lower(), year, month)
                        ]
                    if visa_df is not None and profile.ipcas_user:
                        the_rows += [
                            SPDVKpiDetail(
                                user=profile.user, metric_type='THE', year=year, month=month,
                                source='VISA', transaction_date=r['date'], customer_code=r['customer_code'],
                                customer_name=r['customer_name'], account_number=r['account_number'],
                            )
                            for r in rows_for_user_period(visa_df, profile.ipcas_user.strip().lower(), year, month)
                        ]
                    if the_rows:
                        SPDVKpiDetail.objects.bulk_create(the_rows)

                if emobile_file:
                    plus_qty = emobile_count_for(emobile_counts, profile, year, month)
                    SPDVKpiRecord.objects.update_or_create(
                        user=profile.user, metric_type='AGRIBANK_PLUS', year=year, month=month,
                        defaults={'quantity': plus_qty, 'updated_by': request.user}
                    )
                    plus_updated += 1

                    SPDVKpiDetail.objects.filter(
                        user=profile.user, metric_type='AGRIBANK_PLUS', year=year, month=month
                    ).delete()
                    if emobile_df is not None and profile.ipcas_user:
                        plus_rows = [
                            SPDVKpiDetail(
                                user=profile.user, metric_type='AGRIBANK_PLUS', year=year, month=month,
                                source='EMOBILE', transaction_date=r['date'], customer_code=r['customer_code'],
                                customer_name=r['customer_name'], account_number=r['account_number'],
                            )
                            for r in rows_for_user_period(emobile_df, profile.ipcas_user.strip().lower(), year, month)
                        ]
                        if plus_rows:
                            SPDVKpiDetail.objects.bulk_create(plus_rows)

                if emobile_file or sms_file:
                    mobile_qty = mobile_banking_count_for(emobile_counts, sms_counts, profile, year, month)
                    SPDVKpiRecord.objects.update_or_create(
                        user=profile.user, metric_type='MOBILE_BANKING', year=year, month=month,
                        defaults={'quantity': mobile_qty, 'updated_by': request.user}
                    )
                    mobile_updated += 1

                    SPDVKpiDetail.objects.filter(
                        user=profile.user, metric_type='MOBILE_BANKING', year=year, month=month
                    ).delete()
                    mobile_rows = []
                    if profile.ipcas_user:
                        if emobile_df is not None:
                            mobile_rows += [
                                SPDVKpiDetail(
                                    user=profile.user, metric_type='MOBILE_BANKING', year=year, month=month,
                                    source='EMOBILE', transaction_date=r['date'], customer_code=r['customer_code'],
                                    customer_name=r['customer_name'], account_number=r['account_number'],
                                )
                                for r in rows_for_user_period(emobile_df, profile.ipcas_user.strip().lower(), year, month)
                            ]
                        if sms_df is not None:
                            mobile_rows += [
                                SPDVKpiDetail(
                                    user=profile.user, metric_type='MOBILE_BANKING', year=year, month=month,
                                    source='SMS', transaction_date=r['date'], customer_code=r['customer_code'],
                                    customer_name=r['customer_name'], account_number=r['account_number'],
                                )
                                for r in rows_for_user_period(sms_df, profile.ipcas_user.strip().lower(), year, month)
                            ]
                    if mobile_rows:
                        SPDVKpiDetail.objects.bulk_create(mobile_rows)

                if emobile_file and spdv_quarter_file:
                    tk_plus_qty = emobile_count_for(tk_plus_counts, profile, year, month)
                    SPDVKpiRecord.objects.update_or_create(
                        user=profile.user, metric_type='TK_PLUS', year=year, month=month,
                        defaults={'quantity': tk_plus_qty, 'updated_by': request.user}
                    )
                    tk_plus_updated += 1

                    SPDVKpiDetail.objects.filter(
                        user=profile.user, metric_type='TK_PLUS', year=year, month=month
                    ).delete()
                    if profile.ipcas_user:
                        tk_plus_rows = [
                            SPDVKpiDetail(
                                user=profile.user, metric_type='TK_PLUS', year=year, month=month,
                                source='EMOBILE', transaction_date=r['date'], customer_code=r['customer_code'],
                                customer_name=r['customer_name'], account_number=r['account_number'],
                            )
                            for r in rows_for_user_period(tk_plus_df, profile.ipcas_user.strip().lower(), year, month)
                        ]
                        if tk_plus_rows:
                            SPDVKpiDetail.objects.bulk_create(tk_plus_rows)

                    ott_qty = emobile_count_for(ott_counts, profile, year, month)
                    SPDVKpiRecord.objects.update_or_create(
                        user=profile.user, metric_type='OTT', year=year, month=month,
                        defaults={'quantity': ott_qty, 'updated_by': request.user}
                    )
                    ott_updated += 1

                    SPDVKpiDetail.objects.filter(
                        user=profile.user, metric_type='OTT', year=year, month=month
                    ).delete()
                    if profile.ipcas_user:
                        ott_rows = [
                            SPDVKpiDetail(
                                user=profile.user, metric_type='OTT', year=year, month=month,
                                source='EMOBILE', transaction_date=r['date'], customer_code=r['customer_code'],
                                customer_name=r['customer_name'], account_number=r['account_number'],
                            )
                            for r in rows_for_user_period(ott_df, profile.ipcas_user.strip().lower(), year, month)
                        ]
                        if ott_rows:
                            SPDVKpiDetail.objects.bulk_create(ott_rows)

    period_label = f"{len(periods)} tháng ({start_date.strftime('%m/%Y')} - {end_date.strftime('%m/%Y')})" \
        if len(periods) > 1 else f"{periods[0][1]}/{periods[0][0]}"
    exclusion_note = f' Đã loại trừ khách hàng vay: {len(excluded_customers)} mã.' if excluded_customers else ''

    # Tổng số dòng thực tế đọc được từ file (trước khi khớp theo GDV) — giúp chẩn đoán
    # nhanh khi kết quả ra 0: nếu tổng này cũng = 0 thì lỗi nằm ở file/khoảng ngày,
    # còn nếu tổng > 0 mà vẫn ra 0 theo GDV thì lỗi nằm ở csp_cuser/ipcas_user chưa khớp.
    raw_totals = []
    if csp_file:
        raw_totals.append(f"CSP đọc được {len(csp_df)} dòng")
    if visa_file:
        raw_totals.append(f"Visa đọc được {len(visa_df)} dòng")
    if emobile_file:
        raw_totals.append(f"E-Mobile đọc được {len(emobile_df)} dòng")
    if sms_file:
        raw_totals.append(f"SMS đọc được {len(sms_df)} dòng")
    if spdv_quarter_file:
        raw_totals.append(f"SPDV quý: {len(tk_plus_customers)} KH có Tài khoản Plus, {len(ott_customers)} KH có OTT")
    raw_totals_note = f" ({'; '.join(raw_totals)})" if raw_totals else ""

    tk_plus_note = f', {tk_plus_updated} lượt (Tài khoản Plus), {ott_updated} lượt (Đăng ký OTT)' \
        if emobile_file and spdv_quarter_file else \
        (' (bỏ qua Tài khoản Plus/OTT vì chưa có file SPDV quý)' if emobile_file and not spdv_quarter_file else '')

    messages.success(
        request,
        f'Đã import {period_label}: cập nhật {the_updated} lượt (Số lượng thẻ), '
        f'{plus_updated} lượt (Agribank Plus), {mobile_updated} lượt (Mobile Banking)'
        f'{tk_plus_note}.'
        f'{exclusion_note}{raw_totals_note}'
    )
    year, month = periods[-1]
    return redirect(f"/spdv-kpi/?year={year}&month={month}")


def _split_evenly(total, n):
    """Chia `total` thành `n` phần nguyên, chênh lệch tối đa 1 đơn vị (phần dư dồn vào các tháng đầu)."""
    base, remainder = divmod(total, n)
    return [base + 1 if i < remainder else base for i in range(n)]


@login_required
@require_http_methods(["POST"])
def spdv_kpi_target_set(request):
    """
    Lưu chỉ tiêu SPDV cho từng GDV (mỗi GDV 1 ô số theo từng chỉ tiêu).
    Nếu chọn quý: số nhập là chỉ tiêu cho CẢ QUÝ, chia đều cho 3 tháng.
    """
    manage_scope = check_spdv_manage_scope(request.user)
    if manage_scope is None:
        messages.error(request, 'Bạn không có quyền đặt chỉ tiêu')
        return redirect('spdv_kpi_dashboard')

    periods, error = _parse_period_from_post(request)
    if error:
        messages.error(request, error)
        return redirect('spdv_kpi_dashboard')

    profiles = _spdv_target_profiles_qs()
    saved = 0
    with transaction.atomic():
        for profile in profiles:
            if spdv_group_of(profile) not in manage_scope:
                continue
            for metric_type, _label in SPDVKpiRecord.METRIC_CHOICES:
                field_name = f'target_{metric_type}_{profile.user_id}'
                raw_value = request.POST.get(field_name, '').strip()
                if raw_value == '':
                    continue
                try:
                    total_qty = int(raw_value)
                except ValueError:
                    continue

                shares = _split_evenly(total_qty, len(periods))
                for (year, month), share in zip(periods, shares):
                    SPDVKpiTarget.objects.update_or_create(
                        user=profile.user, metric_type=metric_type, year=year, month=month,
                        defaults={'target_quantity': share, 'updated_by': request.user}
                    )
                saved += 1

    year, month = periods[-1]
    period_label = f"quý ({len(periods)} tháng {periods[0][1]}-{periods[-1][1]}/{year})" if len(periods) > 1 else f"tháng {month}/{year}"
    messages.success(request, f'Đã lưu chỉ tiêu {period_label} ({saved} mục).')
    return redirect(f"/spdv-kpi/?year={year}&month={month}")


def _parse_period_from_get(request):
    """Đọc year + (month hoặc quarter) từ GET, trả về (periods, error_message|None)."""
    try:
        year = int(request.GET.get('year'))
    except (ValueError, TypeError):
        return None, 'Năm không hợp lệ'

    quarter_str = (request.GET.get('quarter') or '').strip()
    if quarter_str:
        try:
            quarter = int(quarter_str)
        except ValueError:
            return None, 'Quý không hợp lệ'
        if not (1 <= quarter <= 4):
            return None, 'Quý phải từ 1 đến 4'
        return _month_list_for_period(year, None, quarter), None

    try:
        month = int(request.GET.get('month'))
    except (ValueError, TypeError):
        return None, 'Tháng không hợp lệ'
    if not (1 <= month <= 12):
        return None, 'Tháng phải từ 1 đến 12'
    return _month_list_for_period(year, month, None), None


def _spdv_detail_access(request, user_id, metric_type):
    """
    Kiểm tra quyền xem chi tiết chỉ tiêu của 1 GDV và trả về (target_profile, periods, error_message).
    `error_message` khác None nghĩa là không có quyền / tham số sai — gọi nơi gọi tự redirect.
    """
    view_scope = check_spdv_view_scope(request.user)
    if view_scope is None:
        return None, None, 'Bạn không có quyền truy cập trang này'

    if metric_type not in dict(SPDVKpiRecord.METRIC_CHOICES):
        return None, None, 'Chỉ tiêu không hợp lệ'

    target_user = get_object_or_404(User, pk=user_id)
    target_profile = getattr(target_user, 'profile', None)
    if not target_profile or spdv_group_of(target_profile) not in view_scope:
        return None, None, 'Bạn không có quyền xem chi tiết của GDV này'

    periods, error = _parse_period_from_get(request)
    if error:
        return None, None, error

    return target_profile, periods, None


@login_required
def spdv_kpi_gdv_detail(request, user_id, metric_type):
    """Danh sách chi tiết các giao dịch góp phần vào chỉ tiêu của 1 GDV trong 1 kỳ (tháng/quý)."""
    target_profile, periods, error = _spdv_detail_access(request, user_id, metric_type)
    if error:
        messages.error(request, error)
        return redirect('spdv_kpi_dashboard')

    years = {y for y, _m in periods}
    months = [m for _y, m in periods]
    details = SPDVKpiDetail.objects.filter(
        user=target_profile.user, metric_type=metric_type, year__in=years, month__in=months
    ).order_by('-transaction_date')

    metric_label = dict(SPDVKpiRecord.METRIC_CHOICES)[metric_type]
    year, month = periods[-1]
    quarter_str = (request.GET.get('quarter') or '').strip()
    period_label = f"Quý {quarter_str}/{year}" if quarter_str else f"Tháng {month}/{year}"
    account_label = 'Số tài khoản' if metric_type == 'THE' else 'Số điện thoại'

    context = {
        'profile': target_profile,
        'metric_type': metric_type,
        'metric_label': metric_label,
        'period_label': period_label,
        'details': details,
        'total': details.count(),
        'year': year,
        'month': month,
        'quarter': quarter_str,
        'account_label': account_label,
    }
    return render(request, 'templates_app/spdv_kpi/detail.html', context)


@login_required
def spdv_kpi_gdv_detail_export(request, user_id, metric_type):
    """Tải file Excel danh sách chi tiết các giao dịch góp phần vào chỉ tiêu của 1 GDV trong 1 kỳ."""
    target_profile, periods, error = _spdv_detail_access(request, user_id, metric_type)
    if error:
        messages.error(request, error)
        return redirect('spdv_kpi_dashboard')

    years = {y for y, _m in periods}
    months = [m for _y, m in periods]
    details = SPDVKpiDetail.objects.filter(
        user=target_profile.user, metric_type=metric_type, year__in=years, month__in=months
    ).order_by('-transaction_date')

    metric_label = dict(SPDVKpiRecord.METRIC_CHOICES)[metric_type]
    account_label = 'Số tài khoản' if metric_type == 'THE' else 'Số điện thoại'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Chi tiet chi tieu'

    header_fill = PatternFill('solid', fgColor='8B1E2D')
    bold_white = Font(bold=True, color='FFFFFF')
    headers = ['Ngày phát hành', 'Nguồn', 'Họ tên', account_label, 'Mã khách hàng']
    ws.append(headers)
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = bold_white
        cell.alignment = Alignment(horizontal='center', vertical='center')

    for d in details:
        ws.append([
            d.transaction_date.strftime('%d/%m/%Y'),
            d.get_source_display(),
            d.customer_name,
            d.account_number,
            d.customer_code,
        ])

    for col, w in enumerate([16, 20, 26, 18, 18], 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = w

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    year, month = periods[-1]
    resp = HttpResponse(
        buf.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    username = target_profile.user.username
    resp['Content-Disposition'] = (
        f'attachment; filename="ChiTiet_{metric_type}_{username}_{month}-{year}.xlsx"'
    )
    return resp

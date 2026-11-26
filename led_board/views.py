from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache

from savings_calculator.models import InterestRate, SavingsProduct

from .forms import (
    BoardSettingForm, ExchangeRateForm, SavingsProductPickForm, SavingsRateForm,
    SlideEditForm, SlideUploadForm,
)
from .models import RATE_FIELDS, BoardSetting, ExchangeRate, LedSlide, RateHistory

RateFormSet = modelformset_factory(ExchangeRate, form=ExchangeRateForm, extra=1, can_delete=True)
SavingsFormSet = modelformset_factory(InterestRate, form=SavingsRateForm, extra=1, can_delete=True)
SlideFormSet = modelformset_factory(LedSlide, form=SlideEditForm, extra=0, can_delete=True)

can_edit = permission_required('led_board.change_exchangerate', raise_exception=True)

SHUTDOWN_WINDOW_MINUTES = 10


def _format_rate(value):
    """25950.00 -> 25.950 ; 30100.50 -> 30.100,50"""
    if value is None:
        return '—'
    text = f'{value:,.2f}'.removesuffix('.00')
    return text.replace(',', ' ').replace('.', ',').replace(' ', '.')


def _rate_values(rate):
    return {f: _format_rate(getattr(rate, f)) for f in RATE_FIELDS}


def _term_label(rate):
    if rate.description:
        return rate.description
    if rate.term_month_min == rate.term_month_max:
        return f'{rate.term_month_min} tháng'
    return f'{rate.term_month_min}-{rate.term_month_max} tháng'


def _savings_payload(product, today):
    if product is None:
        return {'product': '', 'effective': '', 'rows': []}
    rates = list(
        InterestRate.objects.filter(product=product, is_active=True)
        .filter(Q(effective_date__isnull=True) | Q(effective_date__lte=today))
    )
    dates = [r.effective_date for r in rates if r.effective_date]
    return {
        'product': product.name,
        'effective': max(dates).strftime('%d/%m/%Y') if dates else '',
        'rows': [
            {'term': _term_label(r), 'rate': f'{r.interest_rate_yearly:.2f}'.replace('.', ',')}
            for r in rates
        ],
    }


def _board_payload():
    today = timezone.localdate()
    rates = list(ExchangeRate.objects.all())
    stamps = [r.updated_at for r in rates if r.updated_at]
    setting = BoardSetting.load()
    slides = LedSlide.objects.filter(is_active=True).filter(
        Q(start_date__isnull=True) | Q(start_date__lte=today),
        Q(end_date__isnull=True) | Q(end_date__gte=today),
    )
    return {
        'updated': timezone.localtime(max(stamps)).strftime('%H:%M %d/%m/%Y') if stamps else '',
        'rates': [{'code': r.code, **_rate_values(r)} for r in rates],
        'savings': _savings_payload(setting.savings_product, today),
        'slides': [
            {
                'url': reverse('led_board:slide_image', args=[s.pk]),
                'seconds': s.seconds or setting.slide_seconds,
            }
            for s in slides
        ],
        'rate_seconds': setting.rate_seconds,
        'savings_seconds': setting.savings_seconds,
        'ticker': setting.ticker_text.strip(),
    }


@never_cache
def board(request):
    return render(request, 'led_board/board.html', {'payload': _board_payload()})


@never_cache
def board_data(request):
    return JsonResponse(_board_payload())


@never_cache
def shutdown_signal(request):
    """PC LED hỏi mỗi phút; trả TAT trong vài phút sau giờ đã đặt để không lỡ lịch."""
    target = BoardSetting.load().shutdown_time
    now = timezone.localtime()
    if target is not None:
        passed = (now.hour * 60 + now.minute) - (target.hour * 60 + target.minute)
        if 0 <= passed < SHUTDOWN_WINDOW_MINUTES:
            return HttpResponse('TAT', content_type='text/plain')
    return HttpResponse('', content_type='text/plain')


def slide_image(request, pk):
    slide = get_object_or_404(LedSlide, pk=pk)
    try:
        response = FileResponse(slide.image.open('rb'))
    except FileNotFoundError:
        raise Http404
    response['Cache-Control'] = 'public, max-age=86400'
    return response


def _record_history(formset, old, deleted_pks, user):
    entries = [
        RateHistory(code=old[pk]['code'], action='Xóa', old_values=old[pk], changed_by=user)
        for pk in deleted_pks
    ]
    for rate in formset.new_objects:
        entries.append(RateHistory(
            code=rate.code, action='Thêm',
            new_values={'code': rate.code, **_rate_values(rate)}, changed_by=user,
        ))
    for rate, _fields in formset.changed_objects:
        new = {'code': rate.code, **_rate_values(rate)}
        if new != old[rate.pk]:
            entries.append(RateHistory(
                code=rate.code, action='Sửa', old_values=old[rate.pk], new_values=new,
                changed_by=user,
            ))
    RateHistory.objects.bulk_create(entries)


def _save_savings(formset, product):
    with transaction.atomic():
        rates = formset.save(commit=False)
        for rate in formset.deleted_objects:
            rate.delete()
        for rate in rates:
            rate.product = product
            rate.save()


@login_required
@can_edit
def rate_edit(request):
    setting = BoardSetting.load()
    # Chưa chọn thì vẫn mở sẵn sản phẩm đầu tiên để nhập; chỉ lên bảng sau khi bấm Lưu lãi suất.
    product = setting.savings_product or (
        SavingsProduct.objects.filter(is_active=True).order_by('order', 'id').first()
    )
    is_post = request.method == 'POST'
    is_pick = is_post and 'pick_product' in request.POST
    is_savings = is_post and 'save_savings' in request.POST and product is not None
    is_rates = is_post and not is_pick and not is_savings

    pick_form = SavingsProductPickForm(
        request.POST if is_pick else None, instance=setting,
        initial={'savings_product': product.pk if product else None},
    )
    if is_pick and pick_form.is_valid():
        pick_form.save()
        return redirect('led_board:rate_edit')

    savings_formset = SavingsFormSet(
        request.POST if is_savings else None, prefix='savings',
        queryset=InterestRate.objects.filter(product=product),
    )
    if is_savings and savings_formset.is_valid():
        _save_savings(savings_formset, product)
        setting.savings_product = product
        setting.save(update_fields=['savings_product'])
        messages.success(request, 'Đã lưu lãi suất. Bảng LED sẽ cập nhật trong vòng 5 phút.')
        return redirect('led_board:rate_edit')

    formset = RateFormSet(request.POST if is_rates else None, queryset=ExchangeRate.objects.all())
    if is_rates and formset.is_valid():
        old = {r.pk: {'code': r.code, **_rate_values(r)} for r in ExchangeRate.objects.all()}
        deleted_pks = [form.instance.pk for form in formset.deleted_forms if form.instance.pk]
        with transaction.atomic():
            formset.save()
            _record_history(formset, old, deleted_pks, request.user)
            # Đóng dấu cả bảng: bấm Lưu nghĩa là đã xác nhận tỷ giá hôm nay, kể cả số không đổi.
            ExchangeRate.objects.update(updated_at=timezone.now(), updated_by=request.user)
        messages.success(request, 'Đã lưu tỷ giá. Bảng LED sẽ cập nhật trong vòng 5 phút.')
        return redirect('led_board:rate_edit')
    return render(request, 'led_board/rate_edit.html', {
        'formset': formset, 'pick_form': pick_form,
        'savings_formset': savings_formset, 'product': product,
        'savings_on_board': setting.savings_product_id is not None,
    })


@login_required
@can_edit
def rate_history(request):
    labels = {f: ExchangeRate._meta.get_field(f).verbose_name for f in RATE_FIELDS}
    page = Paginator(
        RateHistory.objects.select_related('changed_by'), 50,
    ).get_page(request.GET.get('page'))
    for entry in page:
        old, new = entry.old_values or {}, entry.new_values or {}
        entry.cells = [
            {'old': old.get(f, ''), 'new': new.get(f, ''), 'changed': old.get(f) != new.get(f)}
            for f in RATE_FIELDS
        ]
    return render(request, 'led_board/rate_history.html', {
        'page': page, 'labels': labels.values(),
    })


@login_required
@can_edit
def slide_settings(request):
    setting = BoardSetting.load()
    is_upload = request.method == 'POST' and 'upload' in request.POST
    is_save = request.method == 'POST' and not is_upload

    upload_form = SlideUploadForm(request.POST if is_upload else None,
                                  request.FILES if is_upload else None)
    setting_form = BoardSettingForm(request.POST if is_save else None, instance=setting)
    formset = SlideFormSet(request.POST if is_save else None, queryset=LedSlide.objects.all())

    if is_upload and upload_form.is_valid():
        upload_form.save()
        messages.success(request, 'Đã thêm ảnh.')
        return redirect('led_board:slide_settings')
    if is_save and setting_form.is_valid() and formset.is_valid():
        setting_form.save()
        formset.save()
        messages.success(request, 'Đã lưu thiết lập. Bảng LED sẽ cập nhật trong vòng 5 phút.')
        return redirect('led_board:slide_settings')

    return render(request, 'led_board/slide_settings.html', {
        'upload_form': upload_form, 'setting_form': setting_form, 'formset': formset,
        'board_ratio': f'{setting.board_width} / {setting.board_height}',
    })

"""
Views cho tính năng "Đọc Cân đối" (Kế toán Ngân quỹ)
Import file Cân đối tài khoản (Excel) và hiển thị số liệu cốt yếu doanh thu phí dịch vụ.
"""
import os
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .can_doi_parser import CATEGORIES, MUC_III_DIEN_GIAI, MUC_IV_DIEN_GIAI, CanDoiParser
from .models import CanDoiUpload


@login_required
def can_doi_upload(request):
    """Trang upload file Cân đối tài khoản"""
    if request.method == 'POST' and request.FILES.get('can_doi_file'):
        uploaded_file = request.FILES['can_doi_file']
        original_name = uploaded_file.name
        ext = os.path.splitext(original_name)[1].lower()

        upload_dir = os.path.join(settings.MEDIA_ROOT, 'can_doi')
        os.makedirs(upload_dir, exist_ok=True)

        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(upload_dir, unique_name)

        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        try:
            parser = CanDoiParser(file_path)
            is_valid, error_msg = parser.validate_file()
            if not is_valid:
                messages.error(request, f'File không hợp lệ: {error_msg}')
                return redirect('can_doi_upload')

            result = parser.process()
            chi_tieu = result['chi_tieu']

            upload = CanDoiUpload.objects.create(
                file_name=original_name,
                uploaded_by=request.user,
                tt_trong_nuoc=chi_tieu['1.1'],
                tt_quoc_te=chi_tieu['1.2'],
                kieu_hoi=chi_tieu['1.3'],
                dich_vu_the=chi_tieu['1.4'],
                e_banking=chi_tieu['1.5'],
                uy_thac_dai_ly=chi_tieu['1.6'],
                bao_lanh=chi_tieu['1.7'],
                ngan_quy=chi_tieu['1.8'],
                thu_khac=chi_tieu['1.9'],
                kd_ngoai_hoi=chi_tieu['1.10'],
                dieu_tiet_noi_bo=result['muc_III'],
                tong_doanh_thu=result['tong_doanh_thu'],
            )

            messages.success(request, 'Đã đọc và tính toán số liệu Cân đối thành công!')
            return redirect('can_doi_result', upload_id=upload.id)

        except Exception as e:
            messages.error(request, f'Lỗi khi xử lý file: {str(e)}')
            return redirect('can_doi_upload')
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    uploads = CanDoiUpload.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')[:10]

    context = {
        'uploads': uploads,
    }
    return render(request, 'templates_app/can_doi_upload.html', context)


@login_required
def can_doi_result(request, upload_id):
    """Hiển thị số liệu cốt yếu đã đọc từ file Cân đối"""
    upload = get_object_or_404(CanDoiUpload, id=upload_id, uploaded_by=request.user)

    field_map = {
        '1.1': upload.tt_trong_nuoc,
        '1.2': upload.tt_quoc_te,
        '1.3': upload.kieu_hoi,
        '1.4': upload.dich_vu_the,
        '1.5': upload.e_banking,
        '1.6': upload.uy_thac_dai_ly,
        '1.7': upload.bao_lanh,
        '1.8': upload.ngan_quy,
        '1.9': upload.thu_khac,
        '1.10': upload.kd_ngoai_hoi,
    }
    rows = [
        {'stt': stt, 'label': label, 'dien_giai': dien_giai, 'value': field_map[stt]}
        for stt, label, dien_giai in CATEGORIES
    ]

    context = {
        'upload': upload,
        'rows': rows,
        'muc_III_dien_giai': MUC_III_DIEN_GIAI,
        'muc_IV_dien_giai': MUC_IV_DIEN_GIAI,
    }
    return render(request, 'templates_app/can_doi_result.html', context)

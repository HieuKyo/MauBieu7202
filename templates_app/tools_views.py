"""
Views tiện ích: tra cứu địa bàn hành chính, máy tính cầm tay, công cụ PDF, công cụ OCR.
"""
# Standard library imports
import os
import tempfile

# Django imports
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


def area_lookup(request):
    """
    Trang tra cứu thông tin địa bàn hành chính.
    Sử dụng AddressSelector component và dữ liệu từ dia_danh.json và chuyen_doi.json
    """
    return render(request, 'templates_app/area_lookup.html')


# ==============================================================================
# CALCULATOR
# ==============================================================================

@login_required
def calculator_view(request):
    return render(request, 'templates_app/calculator.html')


# ==============================================================================
# PDF TOOLS (Tách / Ghép PDF)
# ==============================================================================

@login_required
def pdf_tools_view(request):
    return render(request, 'templates_app/pdf_tools.html')


@login_required
@require_http_methods(['POST'])
def pdf_split_view(request):
    """
    Tách PDF theo lựa chọn:
    - mode=all  → tách từng trang thành file riêng, trả về ZIP
    - mode=pages → trích trang theo phạm vi, trả về PDF
    """
    from .pdf_tools_service import validate_pdf, split_to_zip, extract_pages, parse_page_ranges

    uploaded = request.FILES.get('pdf_file')
    if not uploaded:
        return JsonResponse({'error': 'Vui lòng chọn file PDF.'}, status=400)

    is_valid, err = validate_pdf(uploaded)
    if not is_valid:
        return JsonResponse({'error': err}, status=400)

    pdf_bytes = uploaded.read()
    mode = request.POST.get('mode', 'all')
    stem = uploaded.name.rsplit('.', 1)[0]

    try:
        if mode == 'all':
            zip_bytes, total = split_to_zip(pdf_bytes)
            response = HttpResponse(zip_bytes, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="tach_{stem}_{total}trang.zip"'
            return response
        else:
            ranges_str = request.POST.get('page_ranges', '')
            from pypdf import PdfReader
            import io as _io
            total_pages = len(PdfReader(_io.BytesIO(pdf_bytes)).pages)
            page_numbers = parse_page_ranges(ranges_str, total_pages)
            pdf_out = extract_pages(pdf_bytes, page_numbers)
            response = HttpResponse(
                pdf_out,
                content_type='application/pdf',
            )
            response['Content-Disposition'] = f'attachment; filename="trich_{stem}.pdf"'
            return response
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Lỗi xử lý: {str(e)}'}, status=500)


@login_required
@require_http_methods(['POST'])
def pdf_merge_view(request):
    """
    Ghép nhiều file PDF thành một.
    """
    from .pdf_tools_service import validate_pdf, merge_pdfs, MAX_MERGE_FILES

    files = request.FILES.getlist('pdf_files')
    if len(files) < 2:
        return JsonResponse({'error': 'Cần ít nhất 2 file PDF để ghép.'}, status=400)
    if len(files) > MAX_MERGE_FILES:
        return JsonResponse({'error': f'Tối đa {MAX_MERGE_FILES} file mỗi lần ghép.'}, status=400)

    pdf_bytes_list = []
    for f in files:
        is_valid, err = validate_pdf(f)
        if not is_valid:
            return JsonResponse({'error': f'{f.name}: {err}'}, status=400)
        pdf_bytes_list.append(f.read())

    try:
        merged = merge_pdfs(pdf_bytes_list)
    except Exception as e:
        return JsonResponse({'error': f'Lỗi ghép PDF: {str(e)}'}, status=500)

    response = HttpResponse(merged, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="gop_pdf.pdf"'
    return response


# ==============================================================================
# OCR TOOL
# ==============================================================================

@login_required
def ocr_tool_view(request):
    """
    Công cụ OCR: nhận file ảnh hoặc PDF, trích xuất văn bản,
    trả về file Word (.docx) có thể chỉnh sửa.
    POST được gọi bằng fetch (AJAX) — lỗi trả JSON, thành công trả file.
    """
    from .ocr_service import MAX_FILE_SIZE_MB, MAX_PDF_PAGES, validate_file, process_file, build_docx
    ctx = {'max_size': MAX_FILE_SIZE_MB, 'max_pages': MAX_PDF_PAGES}

    if request.method == 'GET':
        return render(request, 'templates_app/ocr_tool.html', ctx)

    def json_error(msg):
        return JsonResponse({'error': msg}, status=400)

    uploaded_file = request.FILES.get('ocr_file')
    if not uploaded_file:
        return json_error('Vui lòng chọn file trước khi gửi.')

    is_valid, error_msg = validate_file(uploaded_file)
    if not is_valid:
        return json_error(error_msg)

    original_name = uploaded_file.name
    ext = os.path.splitext(original_name)[1].lower()

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_file_path = os.path.join(tmp_dir, f'input{ext}')
            with open(tmp_file_path, 'wb+') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
            page_texts = process_file(tmp_file_path, ext)
        docx_bytes = build_docx(page_texts, original_name)
    except Exception as e:
        return json_error(f'Lỗi khi xử lý file: {str(e)}')

    stem = os.path.splitext(original_name)[0]
    output_filename = f'OCR_{stem}.docx'

    response = HttpResponse(
        docx_bytes,
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    )
    response['Content-Disposition'] = f'attachment; filename="{output_filename}"'
    return response

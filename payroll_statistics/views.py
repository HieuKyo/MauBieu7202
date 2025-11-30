"""
Views cho app Payroll Statistics
"""
import pandas as pd
import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView, ListView
from django.http import JsonResponse
from .models import PayingUnit, BeneficiaryAccount
from .forms import PayrollUploadForm


def is_collection_transaction(facno, tacno, remark, rsltremark):
    """
    Xác định giao dịch có phải là "Thu hộ/Khoản trừ" không

    Logic:
    - Điều kiện 1: rsltremark bắt đầu bằng dấu "-"
    - Điều kiện 2: remark chứa một trong các cụm: "THU NO", "THU HO", "KHOAN THU", "KHOAN TRU"
    - Nếu thỏa 1 trong 2 điều kiện => Là Thu hộ
    - Ngược lại => Là Chi lương

    Returns:
        bool: True nếu là Thu hộ, False nếu là Chi lương
    """
    remark_str = str(remark).strip().upper()
    rsltremark_str = str(rsltremark).strip()

    # Điều kiện 1: rsltremark bắt đầu bằng "-"
    if rsltremark_str.startswith('-'):
        return True

    # Điều kiện 2: remark chứa các cụm từ thu hộ
    thu_ho_keywords = ['THU NO', 'THU HO', 'KHOAN THU', 'KHOAN TRU']
    for keyword in thu_ho_keywords:
        if keyword in remark_str:
            return True

    return False


def process_import_file(file_obj):
    """
    Xử lý file import và lưu vào database

    Args:
        file_obj: File object từ upload

    Returns:
        dict: Kết quả import {success: bool, message: str, stats: dict}
    """
    try:
        # Đọc file
        file_name = file_obj.name.lower()

        if file_name.endswith('.csv'):
            # Đọc CSV
            df = pd.read_csv(file_obj)
        elif file_name.endswith('.xls'):
            df = pd.read_excel(file_obj, engine='xlrd')
        elif file_name.endswith('.xlsx'):
            df = pd.read_excel(file_obj, engine='openpyxl')
        else:
            return {
                'success': False,
                'message': 'File không đúng định dạng',
                'stats': {}
            }

        # Kiểm tra các cột bắt buộc
        required_columns = ['facno', 'tacno', 'remark']
        missing_cols = [col for col in required_columns if col not in df.columns]

        if missing_cols:
            return {
                'success': False,
                'message': f'File thiếu các cột: {", ".join(missing_cols)}',
                'stats': {}
            }

        # Thống kê
        total_rows = 0
        chi_luong_count = 0
        thu_ho_count = 0
        units_created = 0
        beneficiaries_created = 0
        errors = []

        # Duyệt qua từng dòng
        for idx, row in df.iterrows():
            try:
                facno = str(row.get('facno', '')).strip()
                tacno = str(row.get('tacno', '')).strip()
                remark = str(row.get('remark', '')).strip()
                rsltremark = str(row.get('rsltremark', '')).strip() if 'rsltremark' in df.columns else ''

                # Bỏ qua dòng trống
                if not facno or not tacno or facno == 'nan' or tacno == 'nan':
                    continue

                total_rows += 1

                # Bước 1: Xác định loại giao dịch
                is_collection = is_collection_transaction(facno, tacno, remark, rsltremark)

                # Bước 2: Mapping dữ liệu
                if is_collection:
                    # Thu hộ: tacno là PayingUnit, facno là BeneficiaryAccount
                    unit_account = tacno
                    beneficiary_account = facno
                    thu_ho_count += 1
                else:
                    # Chi lương: facno là PayingUnit, tacno là BeneficiaryAccount
                    unit_account = facno
                    beneficiary_account = tacno
                    chi_luong_count += 1

                # Bước 3: Lưu vào database
                # Lưu/Lấy PayingUnit
                unit, unit_created = PayingUnit.objects.get_or_create(
                    account_number=unit_account
                )
                if unit_created:
                    units_created += 1

                # Lưu/Lấy BeneficiaryAccount
                beneficiary, ben_created = BeneficiaryAccount.objects.get_or_create(
                    unit=unit,
                    account_number=beneficiary_account,
                    defaults={'remark_ref': remark}
                )
                if ben_created:
                    beneficiaries_created += 1
                elif remark and not beneficiary.remark_ref:
                    # Update remark nếu chưa có
                    beneficiary.remark_ref = remark
                    beneficiary.save()

            except Exception as e:
                errors.append(f"Dòng {idx + 2}: {str(e)}")
                continue

        # Tạo message kết quả
        if total_rows == 0:
            return {
                'success': False,
                'message': 'File không có dữ liệu hợp lệ',
                'stats': {}
            }

        stats = {
            'total_rows': total_rows,
            'chi_luong': chi_luong_count,
            'thu_ho': thu_ho_count,
            'units_created': units_created,
            'beneficiaries_created': beneficiaries_created,
            'errors': errors
        }

        message = f"""Import thành công {total_rows} giao dịch:
        - Chi lương: {chi_luong_count}
        - Thu hộ: {thu_ho_count}
        - Đơn vị mới: {units_created}
        - Nhân viên mới: {beneficiaries_created}"""

        if errors:
            message += f"\n- Có {len(errors)} lỗi"

        return {
            'success': True,
            'message': message,
            'stats': stats
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'Lỗi khi xử lý file: {str(e)}',
            'stats': {}
        }


def upload_view(request):
    """View upload file"""
    if request.method == 'POST':
        form = PayrollUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = request.FILES['file']
            result = process_import_file(file_obj)

            if result['success']:
                messages.success(request, result['message'])
                return redirect('payroll_statistics:statistics')
            else:
                messages.error(request, result['message'])
    else:
        form = PayrollUploadForm()

    return render(request, 'payroll_statistics/upload.html', {
        'form': form,
        'title': 'Upload File Lương/Thu Hộ'
    })


def statistics_view(request):
    """View hiển thị thống kê"""
    # Lấy tất cả dữ liệu
    beneficiaries = BeneficiaryAccount.objects.select_related('unit').all()

    # Thống kê tổng quan
    total_units = PayingUnit.objects.count()
    total_beneficiaries = beneficiaries.count()

    context = {
        'title': 'Thống Kê Lương/Thu Hộ',
        'total_units': total_units,
        'total_beneficiaries': total_beneficiaries,
        'beneficiaries': beneficiaries
    }

    return render(request, 'payroll_statistics/statistics.html', context)


def statistics_data_api(request):
    """API trả về dữ liệu cho DataTables (Ajax)"""
    beneficiaries = BeneficiaryAccount.objects.select_related('unit').all()

    data = []
    for ben in beneficiaries:
        data.append({
            'unit_account': ben.unit.account_number,
            'unit_name': ben.unit.name if ben.unit.name else '',
            'beneficiary_account': ben.account_number,
            'remark_ref': ben.remark_ref,
        })

    return JsonResponse({
        'data': data
    })

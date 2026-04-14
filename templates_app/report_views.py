"""
Views cho chức năng Báo cáo
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import MailEnvelopeTracking, ReportConfiguration
import pandas as pd
import openpyxl
import io
import json
import re
import traceback
from openpyxl.utils.dataframe import dataframe_to_rows
from copy import copy
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from datetime import datetime


@login_required
def report_hub(request):
    """Trang hub cho các loại báo cáo"""
    return render(request, 'templates_app/reports/report_hub.html')


@login_required
def lai_ton_dong_report_view(request):
    """Giao diện báo cáo Lãi tồn đọng"""
    return render(request, 'templates_app/reports/lai_ton_dong.html')


@login_required
@require_http_methods(["POST"])
def process_lai_ton_dong_report(request):
    """Xử lý báo cáo Lãi tồn đọng"""
    try:
        # Lấy cấu hình từ database
        try:
            config_obj = ReportConfiguration.objects.get(report_type='lai_ton_dong', is_active=True)
            ltd_config = config_obj.config_data
        except (ReportConfiguration.DoesNotExist, Exception):
            # Cấu hình mặc định
            ltd_config = {
                'allowed_acctcd': [701001, 701002, 701003],
                'template_row_index': 11,
                'start_row': 11
            }

        current_file = request.FILES.get('current_file')
        comparison_file = request.FILES.get('comparison_file')

        if not all([current_file, comparison_file]):
            messages.error(request, "Vui lòng tải lên đủ 2 file.")
            return redirect('lai_ton_dong_report')

        def process_raw_file(file):
            # Đọc custseq như text để tránh bị format thành số thập phân (7.20201)
            df = pd.read_excel(file, dtype={'custseq': str})

            allowed_acctcd = ltd_config.get('allowed_acctcd', [])
            if 'acctcd' in df.columns:
                df['acctcd'] = pd.to_numeric(df['acctcd'], errors='coerce')
                df = df[df['acctcd'].isin(allowed_acctcd)]

            if 'acrbamt' in df.columns:
                df['acrbamt'] = df['acrbamt'].abs()
            return df

        df_current = process_raw_file(current_file)
        df_comparison = process_raw_file(comparison_file)

        cols_to_keep = ['custseq', 'custnm', 'refno', 'acrbamt', 'bceqa']

        df_current_sel = df_current[cols_to_keep].rename(columns={
            'custseq': 'Mã khách hàng',
            'custnm': 'Tên khách hàng',
            'refno': 'LDS',
            'acrbamt': 'Dư nợ gốc kỳ này',
            'bceqa': 'Lãi kỳ này'
        })
        df_comparison_sel = df_comparison[cols_to_keep].rename(columns={
            'custseq': 'Mã khách hàng SS',
            'custnm': 'Tên khách hàng SS',
            'refno': 'LDS',
            'acrbamt': 'Dư nợ gốc kỳ SS',
            'bceqa': 'Lãi kỳ SS'
        })

        # OUTER JOIN để lấy tất cả LDS từ cả 2 kỳ
        merged_df = pd.merge(
            df_current_sel,
            df_comparison_sel,
            on='LDS',
            how='outer'
        )

        # Điền thông tin khách hàng: ưu tiên kỳ hiện tại, nếu không có thì lấy từ kỳ so sánh
        merged_df['Mã khách hàng'] = merged_df['Mã khách hàng'].fillna(merged_df['Mã khách hàng SS'])
        merged_df['Tên khách hàng'] = merged_df['Tên khách hàng'].fillna(merged_df['Tên khách hàng SS'])

        # Xóa cột tạm
        merged_df.drop(['Mã khách hàng SS', 'Tên khách hàng SS'], axis=1, inplace=True)

        # Điền 0 cho các giá trị số còn thiếu
        merged_df.fillna(0, inplace=True)

        merged_df['Lãi Tăng'] = (merged_df['Lãi kỳ này'] - merged_df['Lãi kỳ SS']).clip(lower=0)
        merged_df['Lãi Giảm'] = (merged_df['Lãi kỳ SS'] - merged_df['Lãi kỳ này']).clip(lower=0)

        final_df = merged_df[
            (merged_df['Dư nợ gốc kỳ này'] != 0) |
            (merged_df['Lãi kỳ này'] != 0) |
            (merged_df['Dư nợ gốc kỳ SS'] != 0) |
            (merged_df['Lãi kỳ SS'] != 0)
        ].copy()

        output_cols = [
            'Mã khách hàng', 'Tên khách hàng', 'LDS',
            'Dư nợ gốc kỳ SS', 'Lãi kỳ SS',
            'Dư nợ gốc kỳ này', 'Lãi kỳ này',
            'Lãi Tăng', 'Lãi Giảm'
        ]
        final_df = final_df[output_cols]

        # Tạo file Excel từ template
        template_path = 'packages/mau_lai_tondong.xlsx'  # Cần copy template vào đây
        try:
            workbook = openpyxl.load_workbook(template_path)
            sheet = workbook.active
        except FileNotFoundError:
            return HttpResponse("Không tìm thấy file mẫu. Vui lòng liên hệ quản trị viên.", status=500)

        template_row_index = ltd_config.get('template_row_index', 11)
        start_row = ltd_config.get('start_row', 11)

        # Xóa merged cells cũ
        merged_ranges = list(sheet.merged_cells.ranges)
        for merged_cell_range in merged_ranges:
            if merged_cell_range.min_row >= start_row:
                sheet.unmerge_cells(str(merged_cell_range))

        # Xóa dữ liệu cũ
        if sheet.max_row >= start_row:
            for row in sheet.iter_rows(min_row=start_row, max_row=sheet.max_row + 10):
                for cell in row:
                    cell.value = None

        # Copy style từ template row
        template_cells = sheet[template_row_index]
        rows_to_write = dataframe_to_rows(final_df, index=False, header=False)

        for r_idx, row_data in enumerate(rows_to_write, start_row):
            for c_idx, value in enumerate(row_data, 1):
                new_cell = sheet.cell(row=r_idx, column=c_idx)
                if c_idx <= len(template_cells):
                    template_cell = template_cells[c_idx - 1]
                    if template_cell.has_style:
                        new_cell.font = copy(template_cell.font)
                        new_cell.border = copy(template_cell.border)
                        new_cell.fill = copy(template_cell.fill)
                        new_cell.number_format = template_cell.number_format
                        new_cell.protection = copy(template_cell.protection)
                        new_cell.alignment = copy(template_cell.alignment)
                new_cell.value = value

        # Thêm dòng tổng
        total_row_index = start_row + len(final_df)
        sheet.cell(row=total_row_index, column=1, value='TỔNG CỘNG')
        numeric_cols_to_sum = ['Dư nợ gốc kỳ này', 'Lãi kỳ này', 'Dư nợ gốc kỳ SS', 'Lãi kỳ SS', 'Lãi Tăng', 'Lãi Giảm']
        col_index_map = {name: i+1 for i, name in enumerate(output_cols)}

        for col_name in numeric_cols_to_sum:
            col_sum = final_df[col_name].sum()
            if col_name in col_index_map:
                total_cell = sheet.cell(row=total_row_index, column=col_index_map[col_name])
                template_cell = template_cells[col_index_map[col_name] - 1]
                if template_cell.has_style:
                    total_cell.font = copy(template_cell.font)
                    total_cell.border = copy(template_cell.border)
                    total_cell.fill = copy(template_cell.fill)
                    total_cell.number_format = template_cell.number_format
                    total_cell.protection = copy(template_cell.protection)
                    total_cell.alignment = copy(template_cell.alignment)
                total_cell.value = col_sum

        # Xuất file
        output = io.BytesIO()
        workbook.save(output)
        output.seek(0)

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="BaoCao_SoSanh_LaiTonDong_KetQua.xlsx"'
        return response

    except Exception as e:
        traceback.print_exc()
        messages.error(request, f"Đã xảy ra lỗi: {e}")
        return redirect('lai_ton_dong_report')


@login_required
def phat_hanh_the_report_view(request):
    """Giao diện báo cáo Phát hành thẻ"""
    # Xóa session data cũ khi truy cập trang mới
    if 'phat_hanh_the_data' in request.session:
        del request.session['phat_hanh_the_data']
    return render(request, 'templates_app/reports/phat_hanh_the.html')


@login_required
@require_http_methods(["POST"])
@login_required
@require_http_methods(["POST"])
def process_phat_hanh_the_report(request):
    """Xử lý báo cáo Phát hành thẻ (ATM + Visa gộp chung)"""
    try:
        combined_df, pgd_user_map, err = _collect_phat_hanh_the_data(request)
        if err:
            messages.warning(request, err)
            return redirect('phat_hanh_the_report')

        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        output, sheets_created = _build_phat_hanh_the_excel(
            combined_df, pgd_user_map, start_date_str, end_date_str
        )
        if sheets_created == 0:
            messages.warning(request, "Không có dữ liệu nào để tạo báo cáo.")
            return redirect('phat_hanh_the_report')

        _save_phat_hanh_the_session(request, combined_df, pgd_user_map, start_date_str, end_date_str)

        output.seek(0)
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = (
            f'attachment; filename="BaoCao_PhatHanhThe_{start_date_str}_den_{end_date_str}.xlsx"'
        )
        return response

    except Exception as e:
        traceback.print_exc()
        messages.error(request, f"Đã xảy ra lỗi: {e}")
        return redirect('phat_hanh_the_report')


@login_required
@require_http_methods(["POST"])
def process_phat_hanh_the_for_print(request):
    """Xử lý báo cáo Phát hành thẻ (ATM + Visa) và chuyển tới trang in"""
    try:
        combined_df, pgd_user_map, err = _collect_phat_hanh_the_data(request)
        if err:
            messages.warning(request, err)
            return redirect('phat_hanh_the_report')

        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        _save_phat_hanh_the_session(request, combined_df, pgd_user_map, start_date_str, end_date_str)
        return redirect('phat_hanh_the_print_preview')

    except Exception as e:
        traceback.print_exc()
        messages.error(request, f"Đã xảy ra lỗi: {e}")
        return redirect('phat_hanh_the_report')


# ── Helpers dùng chung cho phát hành thẻ ──────────────────────────────────────

def _get_atm_pgd_config():
    """Cấu hình PGD cho thẻ ATM (user ID mới)"""
    try:
        config_obj = ReportConfiguration.objects.get(report_type='phat_hanh_the', is_active=True)
        return config_obj.config_data.get('pgd_user_map', {})
    except Exception:
        return {
            "PGD Phường 1": ["7202cthuclt", "7202CTHAOTLT"],
            "PGD Láng Tròn": ["7202canhsh", "7202CTHAOTN"],
            "Hội Sở": ["7202chieutt", "7202CSINHNT", "7202cnhitn", "7202CCHICA"],
        }


def _get_visa_pgd_config():
    """Cấu hình PGD cho thẻ Visa (user ID cũ)"""
    try:
        config_obj = ReportConfiguration.objects.get(report_type='visa_card', is_active=True)
        return config_obj.config_data.get('pgd_user_map', {})
    except Exception:
        return {
            "PGD Phường 1": ["GRALTHUC", "GRATTHAO"],
            "PGD Láng Tròn": ["GRANTHAO", "GRASHANH"],
            "Hội Sở": ["GRATNNHI", "GRANSINH", "GRATHIEU", "GRACACHI"],
        }


def _read_atm_normalized(data_file, start_date_str, end_date_str, pgd_user_map):
    """
    Đọc file ATM (cấu trúc mới), lọc theo ngày và PGD.
    Trả về DataFrame chuẩn hóa với cột:
      Họ tên | Số tài khoản | Loại thẻ | GDV phát hành | Ngày phát hành | PGD
    Hoặc None nếu không có dữ liệu / lỗi cột.
    """
    df = pd.read_excel(data_file)
    df.columns = df.columns.str.strip()

    for col in ['CDATE', 'CUSER', 'CUSTVIENAME', 'ACCOUNT', 'CARDTYPE']:
        if col not in df.columns:
            return None, f"File ATM không có cột '{col}'."

    df['ACCOUNT'] = df['ACCOUNT'].astype(str)
    df['_date'] = pd.to_datetime(df['CDATE'].astype(str).str[:10], format='%d/%m/%Y', errors='coerce').dt.normalize()

    start_dt = pd.to_datetime(start_date_str)
    end_dt   = pd.to_datetime(end_date_str)
    df = df[(df['_date'] >= start_dt) & (df['_date'] <= end_dt)].copy()

    user_map = {u: pgd for pgd, users in pgd_user_map.items() for u in users}
    df['PGD'] = df['CUSER'].map(user_map)
    df = df.dropna(subset=['PGD'])

    if df.empty:
        return None, None  # không lỗi, chỉ không có dữ liệu

    result = pd.DataFrame({
        'Họ tên':          df['CUSTVIENAME'].values,
        'Số tài khoản':    df['ACCOUNT'].values,
        'Loại thẻ':        df['CARDTYPE'].values,
        'GDV phát hành':   df['CUSER'].values,
        'Ngày phát hành':  df['_date'].dt.strftime('%d/%m/%Y').values,
        'PGD':             df['PGD'].values,
    })
    return result, None


def _read_visa_normalized(visa_file, start_date_str, end_date_str, pgd_user_map):
    """
    Đọc file Visa (cấu trúc cũ, có thể có header lặp), lọc theo ngày và PGD.
    Trả về DataFrame chuẩn hóa cùng cột như _read_atm_normalized.
    """
    df = pd.read_excel(visa_file)
    df.columns = df.columns.str.strip()

    # Loại bỏ các dòng header trùng lặp
    if 'custnm' in df.columns:
        df = df[df['custnm'] != 'custnm'].copy()

    for col in ['dlvrydt', 'dlvryusrid', 'custnm', 'cdtpcdnm', 'acctseq']:
        if col not in df.columns:
            return None, f"File Visa không có cột '{col}'."

    df['acctseq'] = df['acctseq'].astype(str)
    df['_date'] = pd.to_datetime(df['dlvrydt'], format='%d/%m/%Y', errors='coerce').dt.normalize()

    start_dt = pd.to_datetime(start_date_str)
    end_dt   = pd.to_datetime(end_date_str)
    df = df[(df['_date'] >= start_dt) & (df['_date'] <= end_dt)].copy()

    user_map = {u: pgd for pgd, users in pgd_user_map.items() for u in users}
    df['PGD'] = df['dlvryusrid'].map(user_map)
    df = df.dropna(subset=['PGD'])

    if df.empty:
        return None, None

    result = pd.DataFrame({
        'Họ tên':          df['custnm'].values,
        'Số tài khoản':    df['acctseq'].values,
        'Loại thẻ':        df['cdtpcdnm'].values,
        'GDV phát hành':   df['dlvryusrid'].values,
        'Ngày phát hành':  df['_date'].dt.strftime('%d/%m/%Y').values,
        'PGD':             df['PGD'].values,
    })
    return result, None


def _collect_phat_hanh_the_data(request):
    """
    Đọc file ATM (bắt buộc) và file Visa (tùy chọn) từ request,
    gộp lại thành 1 DataFrame chuẩn hóa.
    Trả về (combined_df, pgd_user_map, error_msg).
    """
    data_file    = request.FILES.get('data_file')
    visa_file    = request.FILES.get('visa_file')
    start_date_str = request.POST.get('start_date', '')
    end_date_str   = request.POST.get('end_date', '')

    if not start_date_str or not end_date_str:
        return None, None, "Vui lòng cung cấp khoảng thời gian."
    if not data_file and not visa_file:
        return None, None, "Vui lòng tải lên ít nhất một file dữ liệu."

    atm_pgd_map  = _get_atm_pgd_config()
    visa_pgd_map = _get_visa_pgd_config()

    # PGD master list — lấy từ ATM config (thứ tự sheet)
    pgd_user_map = atm_pgd_map

    frames = []
    warnings = []

    if data_file:
        atm_df, err = _read_atm_normalized(data_file, start_date_str, end_date_str, atm_pgd_map)
        if err:
            warnings.append(f"File ATM: {err}")
        elif atm_df is not None:
            frames.append(atm_df)

    if visa_file:
        visa_df, err = _read_visa_normalized(visa_file, start_date_str, end_date_str, visa_pgd_map)
        if err:
            warnings.append(f"File Visa: {err}")
        elif visa_df is not None:
            frames.append(visa_df)

    if warnings:
        # Chỉ là cảnh báo, không ngăn xử lý
        pass

    if not frames:
        msg = "Không có dữ liệu trong khoảng thời gian đã chọn."
        if warnings:
            msg += " (" + "; ".join(warnings) + ")"
        return None, None, msg

    combined_df = pd.concat(frames, ignore_index=True)
    return combined_df, pgd_user_map, "; ".join(warnings) if warnings else None


def _build_phat_hanh_the_excel(combined_df, pgd_user_map, start_date_str, end_date_str):
    """Tạo Excel nhiều sheet từ DataFrame đã chuẩn hóa"""
    output = io.BytesIO()
    sheets_created = 0

    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    highlight_fill = PatternFill(start_color="FFFFE0", end_color="FFFFE0", fill_type="solid")

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for pgd_name in pgd_user_map.keys():
            pgd_df = combined_df[combined_df['PGD'] == pgd_name]
            if pgd_df.empty:
                continue

            output_cols = ['Họ tên', 'Số tài khoản', 'Loại thẻ', 'GDV phát hành', 'Ngày phát hành']
            pgd_df_final = (
                pgd_df[output_cols]
                .assign(_sort_date=pd.to_datetime(pgd_df['Ngày phát hành'], format='%d/%m/%Y', errors='coerce'))
                .sort_values('_sort_date')
                .drop(columns=['_sort_date'])
                .reset_index(drop=True)
            )

            sheets_created += 1
            pgd_df_final.to_excel(writer, sheet_name=pgd_name, index=False, startrow=3)
            ws = writer.sheets[pgd_name]

            title = f"DANH SÁCH THẺ PHÁT HÀNH CỦA {pgd_name.upper()}"
            date_range_str = (
                f"Từ ngày {pd.to_datetime(start_date_str).strftime('%d/%m/%Y')} "
                f"đến ngày {pd.to_datetime(end_date_str).strftime('%d/%m/%Y')}"
            )

            ws['A1'] = title
            ws.merge_cells('A1:E1')
            ws['A1'].font = Font(bold=True, size=14)
            ws['A1'].alignment = Alignment(horizontal='center')

            ws['A2'] = date_range_str
            ws.merge_cells('A2:E2')
            ws['A2'].font = Font(italic=True, size=11)
            ws['A2'].alignment = Alignment(horizontal='center')

            # Border + highlight cho dữ liệu
            for row_idx in range(5, 5 + len(pgd_df_final)):
                loai_the = ws[f'C{row_idx}'].value or ''
                apply_highlight = loai_the not in ('PSuccess', '(486283)-Visa Gold Debit')
                for col_idx in range(1, 6):
                    cell = ws.cell(row=row_idx, column=col_idx)
                    cell.border = thin_border
                    if apply_highlight:
                        cell.fill = highlight_fill

            for cell in ws[4]:
                cell.border = thin_border

            # Auto-fit cột
            for col_idx in range(1, 6):
                col_letter = get_column_letter(col_idx)
                max_len = max(
                    (len(str(c.value)) for c in ws[col_letter] if c.row >= 4 and c.value),
                    default=10
                )
                ws.column_dimensions[col_letter].width = min(max_len + 2, 60)

            from openpyxl.worksheet.properties import PageSetupProperties
            ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
            ws.page_setup.fitToWidth = 1
            ws.page_setup.fitToHeight = 0

    return output, sheets_created


def _save_phat_hanh_the_session(request, combined_df, pgd_user_map, start_date_str, end_date_str):
    """Lưu thông tin PGD và số lượng thẻ vào session để dùng cho print preview"""
    pgd_counts = {
        pgd: len(combined_df[combined_df['PGD'] == pgd])
        for pgd in pgd_user_map.keys()
        if not combined_df[combined_df['PGD'] == pgd].empty
    }
    request.session['phat_hanh_the_data'] = {
        'pgd_list': pgd_counts,
        'start_date': pd.to_datetime(start_date_str).strftime('%d/%m/%Y'),
        'end_date':   pd.to_datetime(end_date_str).strftime('%d/%m/%Y'),
    }


# Giữ lại stub để URL không bị lỗi (2 URL cũ vẫn trỏ vào đây)
@login_required
@require_http_methods(["POST"])
def process_visa_card_report(request):
    return redirect('phat_hanh_the_report')


@login_required
@require_http_methods(["POST"])
def process_visa_card_for_print(request):
    return redirect('phat_hanh_the_report')


@login_required
def phat_hanh_the_print_preview(request):
    """Print preview cho nhãn bao thư phát hành thẻ"""
    # Lấy PGD name từ URL parameter
    pgd_name = request.GET.get('pgd', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # Nếu không có parameter, lấy từ session
    if not pgd_name or not start_date or not end_date:
        session_data = request.session.get('phat_hanh_the_data', {})
        if not session_data:
            messages.error(request, 'Không có dữ liệu để in. Vui lòng xử lý báo cáo trước.')
            return redirect('phat_hanh_the_report')

        start_date = session_data.get('start_date', '')
        end_date = session_data.get('end_date', '')
        pgd_list = session_data.get('pgd_list', {})

        # Nếu không chỉ định PGD, hiển thị tất cả PGD
        if not pgd_name:
            context = {
                'pgd_list': pgd_list,
                'start_date': start_date,
                'end_date': end_date,
                'show_all': True,
            }
            return render(request, 'templates_app/reports/phat_hanh_the_print_preview.html', context)

    context = {
        'pgd_name': pgd_name,
        'start_date': start_date,
        'end_date': end_date,
        'show_all': False,
    }

    return render(request, 'templates_app/reports/phat_hanh_the_print_preview.html', context)


@login_required
def mail_envelope_tracking_view(request):
    """Giao diện nhận bì thư"""
    # Lấy danh sách user từ cấu hình nếu có
    try:
        config_obj = ReportConfiguration.objects.get(report_type='phat_hanh_the', is_active=True)
        pgd_user_map = config_obj.config_data.get('pgd_user_map', {})
        all_users = sorted([user for users in pgd_user_map.values() for user in users])
    except:
        all_users = []

    return render(request, 'templates_app/reports/mail_envelope_tracking.html', {'all_users': all_users})


@login_required
@require_http_methods(["POST"])
def save_mail_envelope(request):
    """Lưu thông tin nhận bì thư"""
    try:
        data = json.loads(request.body)

        envelope = MailEnvelopeTracking.objects.create(
            envelope_code=data['ma_bithu'],
            receive_date=data['ngay_nhan'],
            receiver=data['nguoi_nhan']
        )

        return JsonResponse({'status': 'success', 'message': 'Đã lưu thành công!'}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def mail_envelope_report_view(request):
    """Báo cáo bì thư"""
    ma_bithu_search = request.GET.get('ma_bithu', '').strip()
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    records = []

    if ma_bithu_search:
        records = MailEnvelopeTracking.objects.filter(
            envelope_code__icontains=ma_bithu_search
        ).order_by('-receive_date', '-created_at')
    elif start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        records = MailEnvelopeTracking.objects.filter(
            receive_date__range=[start_date, end_date]
        ).order_by('-receive_date', '-created_at')

    context = {
        'records': records,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'ma_bithu_search': ma_bithu_search
    }

    return render(request, 'templates_app/reports/mail_envelope_report.html', context)


@login_required
def dien_luc_report_view(request):
    """Giao diện báo cáo Điện lực - xử lý client-side"""
    return render(request, 'templates_app/reports/dien_luc.html')


@login_required
@require_http_methods(["POST"])
def process_dien_luc_report(request):
    """Xử lý báo cáo Thu hộ tiền điện - xuất Excel bảng kê"""
    try:
        uploaded_file = request.FILES.get('dien_luc_file')
        start_date_str = request.POST.get('start_date', '').strip()
        end_date_str = request.POST.get('end_date', '').strip()

        if not uploaded_file:
            messages.error(request, 'Vui lòng chọn file Excel.')
            return redirect('dien_luc_report')

        if not start_date_str or not end_date_str:
            messages.error(request, 'Vui lòng nhập đầy đủ khoảng thời gian.')
            return redirect('dien_luc_report')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Đọc file Excel — không dùng dtype=str để giữ nguyên kiểu date và số
        file_bytes = uploaded_file.read()
        try:
            df = pd.read_excel(io.BytesIO(file_bytes))
        except Exception:
            # File .xls có corruption nhỏ — thử bỏ qua lỗi workbook
            import xlrd
            wb = xlrd.open_workbook(file_contents=file_bytes, ignore_workbook_corruption=True)
            df = pd.read_excel(wb)

        # Chuẩn hóa tên cột (strip whitespace)
        df.columns = [c.strip() for c in df.columns]

        required_cols = ['NGAY_NOP', 'TONG_NOP']
        for col in required_cols:
            if col not in df.columns:
                messages.error(request, f'File thiếu cột bắt buộc: {col}. Các cột hiện có: {", ".join(df.columns)}')
                return redirect('dien_luc_report')

        # Parse NGAY_NOP — thử nhiều format, ưu tiên DD/MM/YYYY
        raw = df['NGAY_NOP']
        if pd.api.types.is_datetime64_any_dtype(raw):
            df['ngay_parsed'] = raw
        else:
            s = raw.astype(str).str.strip().str[:10]
            # Thử lần lượt các format phổ biến
            for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y'):
                parsed = pd.to_datetime(s, format=fmt, errors='coerce')
                ok = parsed.notna().sum()
                if ok > len(df) * 0.5:
                    df['ngay_parsed'] = parsed
                    break
            else:
                df['ngay_parsed'] = pd.NaT

        df = df.dropna(subset=['ngay_parsed'])
        if df.empty:
            messages.error(request, 'Không thể parse cột NGAY_NOP. Kiểm tra lại định dạng ngày trong file.')
            return redirect('dien_luc_report')

        df['ngay_date'] = df['ngay_parsed'].dt.date

        # Debug: show sample parsed dates and range
        sample_dates = sorted(df['ngay_date'].unique())[:5]
        sample_str = ', '.join(d.strftime('%d/%m/%Y') for d in sample_dates)

        # Filter by date range
        df_filtered = df[(df['ngay_date'] >= start_date) & (df['ngay_date'] <= end_date)]

        if df_filtered.empty:
            messages.warning(request,
                f'Không có dữ liệu trong khoảng {start_date.strftime("%d/%m/%Y")} – {end_date.strftime("%d/%m/%Y")}. '
                f'File có {len(df)} dòng, ngày đầu tiên parse được: {sample_str}')
            return redirect('dien_luc_report')

        df = df_filtered

        # Parse TONG_NOP as numeric — strip spaces/commas nếu là string
        tong_nop_raw = df['TONG_NOP'].astype(str).str.strip().str.replace(',', '', regex=False)
        df['tong_nop_num'] = pd.to_numeric(tong_nop_raw, errors='coerce').fillna(0)

        # Đếm số hóa đơn bằng size (đếm tất cả các dòng, không bỏ NaN)
        size_by_date = df.groupby('ngay_date').size().rename('so_luong')
        sum_by_date = df.groupby('ngay_date')['tong_nop_num'].sum().rename('so_tien')
        grouped = (
            pd.concat([size_by_date, sum_by_date], axis=1)
            .reset_index()
            .sort_values('ngay_date')
        )

        # Build Excel with openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Bảng kê tiền điện'

        # Fit tất cả cột vào 1 trang khi in
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0  # 0 = không giới hạn số trang dọc
        ws.page_setup.orientation = 'portrait'

        # --- Styles ---
        bold_font = Font(name='Times New Roman', bold=True, size=12)
        normal_font = Font(name='Times New Roman', size=12)
        center = Alignment(horizontal='center', vertical='center', wrap_text=True)
        left = Alignment(horizontal='left', vertical='center', wrap_text=True)
        right = Alignment(horizontal='right', vertical='center')

        thin = Side(border_style='thin', color='000000')
        all_border = Border(left=thin, right=thin, top=thin, bottom=thin)

        header_fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')

        # Column widths: A(STT), B(Ngày), C(Số HĐ), D(Số tiền), E(Ghi chú)
        ws.column_dimensions['A'].width = 8
        ws.column_dimensions['B'].width = 18
        ws.column_dimensions['C'].width = 22
        ws.column_dimensions['D'].width = 22
        ws.column_dimensions['E'].width = 25

        row = 1

        # Row 1: bank name (left A:C) + CHXHCNVN (right D:E)
        ws.merge_cells(f'A{row}:C{row}')
        c = ws.cell(row=row, column=1,
                    value='NGÂN HÀNG NÔNG NGHIỆP\nVÀ PHÁT TRIỂN NÔNG THÔN VIỆT NAM')
        c.font = Font(name='Times New Roman', bold=True, size=11)
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws.row_dimensions[row].height = 32

        ws.merge_cells(f'D{row}:E{row}')
        c2 = ws.cell(row=row, column=4,
                     value='CỘNG HOÀ XÃ HỘI CHỦ NGHĨA VIỆT NAM')
        c2.font = Font(name='Times New Roman', bold=True, size=11)
        c2.alignment = center
        row += 1

        # Row 2: Chi nhánh (left A:C) + Độc lập (right D:E)
        ws.merge_cells(f'A{row}:C{row}')
        c = ws.cell(row=row, column=1, value='CHI NHÁNH GIÁ RAI BẠC LIÊU')
        c.font = Font(name='Times New Roman', bold=True, underline='single', size=11)
        c.alignment = center

        ws.merge_cells(f'D{row}:E{row}')
        c2 = ws.cell(row=row, column=4, value='Độc lập - Tự do - Hạnh phúc')
        c2.font = Font(name='Times New Roman', bold=True, underline='single', size=11)
        c2.alignment = center
        ws.row_dimensions[row].height = 18
        row += 1

        # Empty row
        row += 1

        # Title row
        start_fmt = start_date.strftime('%d/%m/%Y')
        end_fmt = end_date.strftime('%d/%m/%Y')
        title = f'BẢNG KÊ THANH TOÁN HOÁ ĐƠN TIỀN ĐIỆN\nTỪ NGÀY {start_fmt} ĐẾN NGÀY {end_fmt}'
        ws.merge_cells(f'A{row}:E{row}')
        c = ws.cell(row=row, column=1, value=title)
        c.font = Font(name='Times New Roman', bold=True, size=14)
        c.alignment = center
        ws.row_dimensions[row].height = 46
        row += 1

        # Empty row
        row += 1

        # Table header
        headers = ['STT', 'Ngày', 'Số lượng Hoá Đơn', 'Số tiền', 'Ghi Chú']
        for col_idx, h in enumerate(headers, start=1):
            c = ws.cell(row=row, column=col_idx, value=h)
            c.font = bold_font
            c.alignment = center
            c.border = all_border
            c.fill = header_fill
        ws.row_dimensions[row].height = 22
        row += 1

        # Data rows
        total_so_luong = 0
        total_so_tien = 0

        for i, data_row in enumerate(grouped.itertuples(), start=1):
            ngay_str = data_row.ngay_date.strftime('%d/%m/%Y')
            so_luong = int(data_row.so_luong)
            so_tien = float(data_row.so_tien)
            total_so_luong += so_luong
            total_so_tien += so_tien

            values = [i, ngay_str, so_luong, so_tien, '']
            aligns = [center, center, center, right, left]
            for col_idx, (val, aln) in enumerate(zip(values, aligns), start=1):
                c = ws.cell(row=row, column=col_idx, value=val)
                c.font = normal_font
                c.alignment = aln
                c.border = all_border
                if col_idx == 4:
                    c.number_format = '#,##0'
            ws.row_dimensions[row].height = 18
            row += 1

        # Total row
        total_values = ['', 'TỔNG CỘNG', total_so_luong, total_so_tien, '']
        total_aligns = [center, center, center, right, left]
        for col_idx, (val, aln) in enumerate(zip(total_values, total_aligns), start=1):
            c = ws.cell(row=row, column=col_idx, value=val)
            c.font = bold_font
            c.alignment = aln
            c.border = all_border
            if col_idx == 4:
                c.number_format = '#,##0'
        ws.row_dimensions[row].height = 18
        row += 1

        # Empty row before signatures
        row += 1

        # Signature title row: LẬP BẢNG / KIỂM SOÁT
        ws.merge_cells(f'B{row}:C{row}')
        c = ws.cell(row=row, column=2, value='LẬP BẢNG')
        c.font = bold_font
        c.alignment = center

        ws.merge_cells(f'D{row}:E{row}')
        c2 = ws.cell(row=row, column=4, value='KIỂM SOÁT')
        c2.font = bold_font
        c2.alignment = center
        ws.row_dimensions[row].height = 18
        row += 1

        # Sub-label row: (Ký, ghi rõ họ tên) — directly below, no extra gap
        ws.merge_cells(f'B{row}:C{row}')
        c = ws.cell(row=row, column=2, value='(Ký, ghi rõ họ tên)')
        c.font = normal_font
        c.alignment = center

        ws.merge_cells(f'D{row}:E{row}')
        c2 = ws.cell(row=row, column=4, value='(Ký, ghi rõ họ tên)')
        c2.font = normal_font
        c2.alignment = center
        ws.row_dimensions[row].height = 18
        row += 1

        # Empty rows for actual signature space
        ws.row_dimensions[row].height = 50
        row += 1

        # Output
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        filename = f'bang_ke_tien_dien_{start_fmt.replace("/","")}-{end_fmt.replace("/","")}.xlsx'
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        messages.error(request, f'Lỗi xử lý file: {str(e)}')
        return redirect('dien_luc_report')


@login_required
def atm_fund_balance_view(request):
    """Giao diện báo cáo Tồn quỹ ATM - xử lý client-side"""
    return render(request, 'templates_app/reports/atm_fund_balance.html')


# ===== ATM TRANSACTION REPORT VIEWS =====

def parse_atm_filename_date(filename):
    """
    Parse tên file để lấy tháng và năm
    Format: MMYYYY.xls hoặc MMYYYY.xlsx
    VD: 122025.xls -> tháng 12, năm 2025

    Returns:
        tuple: (month, year) hoặc (None, None) nếu không hợp lệ
    """
    # Loại bỏ extension
    name_without_ext = filename.rsplit('.', 1)[0]

    # Pattern: 1-2 chữ số tháng + 4 chữ số năm
    pattern = r'^(\d{1,2})(\d{4})$'
    match = re.match(pattern, name_without_ext)

    if match:
        month = int(match.group(1))
        year = int(match.group(2))

        # Validate tháng (1-12)
        if 1 <= month <= 12:
            return month, year

    return None, None


def import_atm_excel(excel_file, user):
    """
    Import dữ liệu từ file Excel và lưu vào database

    Args:
        excel_file: File object từ form upload
        user: User object của người upload

    Returns:
        dict: {'success': bool, 'message': str, 'upload_id': int, 'record_count': int}
    """
    from .models import ATMTransactionReport, ATMReportUpload
    from decimal import Decimal

    try:
        # Parse tên file để lấy tháng/năm
        filename = excel_file.name
        month, year = parse_atm_filename_date(filename)

        if month is None or year is None:
            return {
                'success': False,
                'message': f'Tên file không hợp lệ: "{filename}". Vui lòng đặt theo mẫu MMYYYY.xls (VD: 122025.xls)',
                'upload_id': None,
                'record_count': 0
            }

        # Tạo report_period (ngày đầu tiên của tháng)
        report_period = datetime(year, month, 1).date()

        # Kiểm tra xem đã có dữ liệu của tháng này chưa
        existing_upload = ATMReportUpload.objects.filter(report_period=report_period).first()
        if existing_upload:
            return {
                'success': False,
                'message': f'Dữ liệu tháng {month}/{year} đã tồn tại. Vui lòng xóa dữ liệu cũ trước khi import lại.',
                'upload_id': existing_upload.id,
                'record_count': existing_upload.record_count,
                'existing': True
            }

        # Đọc file Excel
        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            return {
                'success': False,
                'message': f'Không thể đọc file Excel: {str(e)}',
                'upload_id': None,
                'record_count': 0
            }

        # Kiểm tra các cột bắt buộc
        required_columns = ['Branch_Code', 'ATM_No', 'Tx_Code', 'Tx_Count', 'Tx_Amount', 'Tx_Fee', 'vatamt']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return {
                'success': False,
                'message': f'File thiếu các cột: {", ".join(missing_columns)}',
                'upload_id': None,
                'record_count': 0
            }

        # Bắt đầu transaction để đảm bảo tính toàn vẹn dữ liệu
        from django.db import transaction
        with transaction.atomic():
            # Tạo ATMReportUpload record
            upload = ATMReportUpload.objects.create(
                file_name=filename,
                report_period=report_period,
                uploaded_by=user,
                record_count=0
            )

            # Import từng dòng
            records_to_create = []
            for idx, row in df.iterrows():
                try:
                    # Chuyển đổi giá trị số, xử lý NaN
                    tx_count = int(row['Tx_Count']) if pd.notna(row['Tx_Count']) else 0
                    tx_amount = Decimal(str(row['Tx_Amount'])) if pd.notna(row['Tx_Amount']) else Decimal('0')
                    tx_fee = Decimal(str(row['Tx_Fee'])) if pd.notna(row['Tx_Fee']) else Decimal('0')
                    vatamt = Decimal(str(row['vatamt'])) if pd.notna(row['vatamt']) else Decimal('0')

                    record = ATMTransactionReport(
                        upload=upload,
                        branch_code=str(row['Branch_Code']),
                        atm_no=str(row['ATM_No']),
                        tx_code=str(row['Tx_Code']),
                        tx_count=tx_count,
                        tx_amount=tx_amount,
                        tx_fee=tx_fee,
                        vatamt=vatamt,
                        report_period=report_period
                    )
                    records_to_create.append(record)

                except Exception as e:
                    # Log lỗi nhưng tiếp tục
                    print(f"Lỗi tại dòng {idx + 2}: {str(e)}")
                    continue

            # Bulk create để tăng performance
            if records_to_create:
                ATMTransactionReport.objects.bulk_create(records_to_create)
                upload.record_count = len(records_to_create)
                upload.save()
            else:
                return {
                    'success': False,
                    'message': 'Không có dữ liệu hợp lệ để import',
                    'upload_id': None,
                    'record_count': 0
                }

        return {
            'success': True,
            'message': f'Import thành công {len(records_to_create)} bản ghi cho tháng {month}/{year}',
            'upload_id': upload.id,
            'record_count': len(records_to_create)
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'Lỗi không xác định: {str(e)}',
            'upload_id': None,
            'record_count': 0
        }


@login_required
def atm_transaction_report(request):
    """Dashboard hiển thị báo cáo ATM với bộ lọc nâng cao"""
    from .models import ATMTransactionReport, ATMReportUpload
    from django.db.models import Sum, Count, Q, Case, When, IntegerField, DecimalField
    from dateutil.relativedelta import relativedelta

    # Định nghĩa mã giao dịch cho từng loại
    DEPOSIT_CODES = ['0210']  # Nộp tiền
    WITHDRAWAL_CODES = ['ATM Withdrawal']  # Rút tiền
    TRANSFER_CODES = ['ATM Transfer Debit', 'ATM IBFT Debit']  # Chuyển khoản
    # GD khác: Tất cả các mã còn lại

    # Lấy tham số filter từ request
    selected_period = request.GET.get('period', '')
    selected_atm = request.GET.get('atm', '')
    selected_branch = request.GET.get('branch', '')
    period_type = request.GET.get('period_type', 'month')  # month, 6months, quarter, year
    tx_type_filter = request.GET.get('tx_type', '')  # deposit, withdrawal, transfer, other

    # Lấy danh sách các kỳ báo cáo có sẵn
    available_periods = ATMReportUpload.objects.all().order_by('-report_period')

    # Tổng hợp danh sách năm và quý từ dữ liệu có sẵn
    from django.db.models.functions import TruncYear, TruncQuarter
    available_years = (
        ATMReportUpload.objects.annotate(nam=TruncYear('report_period'))
        .values('nam').distinct().order_by('-nam')
    )
    available_quarters = (
        ATMReportUpload.objects.annotate(quy=TruncQuarter('report_period'))
        .values('quy').distinct().order_by('-quy')
    )
    available_quarters_list = []
    for row in available_quarters:
        m = row['quy'].month
        available_quarters_list.append({
            'value': row['quy'].strftime('%Y-%m-%d'),
            'label': f"Q{(m-1)//3+1}/{row['quy'].year}",
        })

    # Lấy danh sách ATM và chi nhánh để làm filter
    all_atms = ATMTransactionReport.objects.values('atm_no').distinct().order_by('atm_no')
    all_branches = ATMTransactionReport.objects.values('branch_code').distinct().order_by('branch_code')

    # Base queryset
    queryset = ATMTransactionReport.objects.all()

    # Filter theo period
    if selected_period:
        try:
            period_date = datetime.strptime(selected_period, '%Y-%m-%d').date()

            if period_type == '6months':
                start_date = period_date - relativedelta(months=5)
                queryset = queryset.filter(
                    report_period__gte=start_date,
                    report_period__lte=period_date
                )
            elif period_type == 'quarter':
                # Lấy toàn bộ quý chứa tháng được chọn
                q_month = ((period_date.month - 1) // 3) * 3 + 1
                import datetime as dt
                q_start = period_date.replace(month=q_month, day=1)
                q_end_month = q_month + 2
                q_end_year = period_date.year + (1 if q_end_month > 12 else 0)
                q_end_month = q_end_month if q_end_month <= 12 else q_end_month - 12
                import calendar
                q_end = dt.date(q_end_year, q_end_month, calendar.monthrange(q_end_year, q_end_month)[1])
                queryset = queryset.filter(
                    report_period__gte=q_start,
                    report_period__lte=q_end
                )
            elif period_type == 'year':
                # Lấy toàn bộ năm của tháng được chọn
                queryset = queryset.filter(report_period__year=period_date.year)
            else:
                # Chỉ lấy tháng được chọn
                queryset = queryset.filter(report_period=period_date)
        except ValueError:
            messages.error(request, 'Định dạng thời gian không hợp lệ')

    # Filter theo ATM
    if selected_atm:
        queryset = queryset.filter(atm_no=selected_atm)

    # Filter theo chi nhánh
    if selected_branch:
        queryset = queryset.filter(branch_code=selected_branch)

    # Filter theo loại giao dịch
    if tx_type_filter == 'deposit':
        queryset = queryset.filter(tx_code__in=DEPOSIT_CODES)
    elif tx_type_filter == 'transfer':
        queryset = queryset.filter(tx_code__in=TRANSFER_CODES)
    elif tx_type_filter == 'withdrawal':
        queryset = queryset.filter(tx_code__in=WITHDRAWAL_CODES)
    elif tx_type_filter == 'other':
        # GD khác: không phải deposit, transfer, withdrawal
        all_known_codes = DEPOSIT_CODES + TRANSFER_CODES + WITHDRAWAL_CODES
        queryset = queryset.exclude(tx_code__in=all_known_codes)

    # Group by ATM_No và tính tổng riêng cho từng loại giao dịch
    report_data = queryset.values('atm_no', 'branch_code').annotate(
        # Giao dịch nộp tiền
        deposit_count=Sum(
            Case(
                When(tx_code__in=DEPOSIT_CODES, then='tx_count'),
                default=0,
                output_field=IntegerField()
            )
        ),
        deposit_amount=Sum(
            Case(
                When(tx_code__in=DEPOSIT_CODES, then='tx_amount'),
                default=0,
                output_field=DecimalField()
            )
        ),
        # Giao dịch rút tiền
        withdrawal_count=Sum(
            Case(
                When(tx_code__in=WITHDRAWAL_CODES, then='tx_count'),
                default=0,
                output_field=IntegerField()
            )
        ),
        withdrawal_amount=Sum(
            Case(
                When(tx_code__in=WITHDRAWAL_CODES, then='tx_amount'),
                default=0,
                output_field=DecimalField()
            )
        ),
        # Giao dịch chuyển khoản
        transfer_count=Sum(
            Case(
                When(tx_code__in=TRANSFER_CODES, then='tx_count'),
                default=0,
                output_field=IntegerField()
            )
        ),
        transfer_amount=Sum(
            Case(
                When(tx_code__in=TRANSFER_CODES, then='tx_amount'),
                default=0,
                output_field=DecimalField()
            )
        ),
        # Giao dịch khác
        other_count=Sum(
            Case(
                When(
                    ~Q(tx_code__in=DEPOSIT_CODES + TRANSFER_CODES + WITHDRAWAL_CODES),
                    then='tx_count'
                ),
                default=0,
                output_field=IntegerField()
            )
        ),
        other_amount=Sum(
            Case(
                When(
                    ~Q(tx_code__in=DEPOSIT_CODES + TRANSFER_CODES + WITHDRAWAL_CODES),
                    then='tx_amount'
                ),
                default=0,
                output_field=DecimalField()
            )
        ),
        # Tổng cộng
        total_tx_count=Sum('tx_count'),
        total_tx_amount=Sum('tx_amount'),
        total_tx_fee=Sum('tx_fee'),
        total_vatamt=Sum('vatamt'),
        transaction_types=Count('tx_code', distinct=True)
    ).order_by('branch_code', 'atm_no')

    # Tính tổng cộng toàn bộ
    totals = queryset.aggregate(
        grand_deposit_count=Sum(
            Case(
                When(tx_code__in=DEPOSIT_CODES, then='tx_count'),
                default=0,
                output_field=IntegerField()
            )
        ),
        grand_deposit_amount=Sum(
            Case(
                When(tx_code__in=DEPOSIT_CODES, then='tx_amount'),
                default=0,
                output_field=DecimalField()
            )
        ),
        grand_withdrawal_count=Sum(
            Case(
                When(tx_code__in=WITHDRAWAL_CODES, then='tx_count'),
                default=0,
                output_field=IntegerField()
            )
        ),
        grand_withdrawal_amount=Sum(
            Case(
                When(tx_code__in=WITHDRAWAL_CODES, then='tx_amount'),
                default=0,
                output_field=DecimalField()
            )
        ),
        grand_transfer_count=Sum(
            Case(
                When(tx_code__in=TRANSFER_CODES, then='tx_count'),
                default=0,
                output_field=IntegerField()
            )
        ),
        grand_transfer_amount=Sum(
            Case(
                When(tx_code__in=TRANSFER_CODES, then='tx_amount'),
                default=0,
                output_field=DecimalField()
            )
        ),
        grand_other_count=Sum(
            Case(
                When(
                    ~Q(tx_code__in=DEPOSIT_CODES + TRANSFER_CODES + WITHDRAWAL_CODES),
                    then='tx_count'
                ),
                default=0,
                output_field=IntegerField()
            )
        ),
        grand_other_amount=Sum(
            Case(
                When(
                    ~Q(tx_code__in=DEPOSIT_CODES + TRANSFER_CODES + WITHDRAWAL_CODES),
                    then='tx_amount'
                ),
                default=0,
                output_field=DecimalField()
            )
        ),
        grand_total_count=Sum('tx_count'),
        grand_total_amount=Sum('tx_amount'),
        grand_total_fee=Sum('tx_fee'),
        grand_total_vat=Sum('vatamt')
    )

    context = {
        'available_periods': available_periods,
        'available_years': available_years,
        'available_quarters': available_quarters_list,
        'all_atms': all_atms,
        'all_branches': all_branches,
        'selected_period': selected_period,
        'selected_atm': selected_atm,
        'selected_branch': selected_branch,
        'period_type': period_type,
        'tx_type_filter': tx_type_filter,
        'report_data': report_data,
        'totals': totals,
        'record_count': report_data.count()
    }

    return render(request, 'templates_app/reports/atm_transaction_report.html', context)


@login_required
def atm_transaction_import(request):
    """View xử lý upload và import file Excel"""
    from .models import ATMReportUpload
    from .forms import ATMReportUploadForm

    if request.method == 'POST':
        form = ATMReportUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']

            # Import dữ liệu
            result = import_atm_excel(excel_file, request.user)

            if result['success']:
                messages.success(request, result['message'])
                return redirect('atm_transaction_report')
            else:
                # Kiểm tra nếu là trường hợp đã tồn tại
                if result.get('existing'):
                    messages.warning(request, result['message'])
                else:
                    messages.error(request, result['message'])
    else:
        form = ATMReportUploadForm()

    context = {
        'form': form,
        'upload_history': ATMReportUpload.objects.all().order_by('-upload_date')[:10]
    }

    return render(request, 'templates_app/reports/atm_transaction_import.html', context)


@login_required
def atm_transaction_delete(request, upload_id):
    """Xóa dữ liệu báo cáo đã upload"""
    from .models import ATMReportUpload

    if request.method == 'POST':
        try:
            upload = ATMReportUpload.objects.get(id=upload_id)
            period_str = upload.report_period.strftime('%m/%Y')

            # Xóa upload sẽ cascade xóa tất cả transactions
            upload.delete()

            messages.success(request, f'Đã xóa dữ liệu tháng {period_str}')
        except ATMReportUpload.DoesNotExist:
            messages.error(request, 'Không tìm thấy dữ liệu')

    return redirect('atm_transaction_report')


@login_required
def atm_transaction_detail(request, atm_no):
    """Xem chi tiết giao dịch của một máy ATM"""
    from .models import ATMTransactionReport
    from django.db.models import Sum

    selected_period = request.GET.get('period', '')

    queryset = ATMTransactionReport.objects.filter(atm_no=atm_no)

    if selected_period:
        try:
            period_date = datetime.strptime(selected_period, '%Y-%m-%d').date()
            queryset = queryset.filter(report_period=period_date)
        except ValueError:
            messages.error(request, 'Định dạng thời gian không hợp lệ')

    transactions = queryset.order_by('tx_code')

    # Tính tổng cho máy ATM này
    totals = queryset.aggregate(
        total_count=Sum('tx_count'),
        total_amount=Sum('tx_amount'),
        total_fee=Sum('tx_fee'),
        total_vat=Sum('vatamt')
    )

    context = {
        'atm_no': atm_no,
        'selected_period': selected_period,
        'transactions': transactions,
        'totals': totals
    }

    return render(request, 'templates_app/reports/atm_transaction_detail.html', context)


# ─────────────────────────────────────────────────────────────────────────────
# BÁO CÁO ĐÓNG/MỞ TÀI KHOẢN
# ─────────────────────────────────────────────────────────────────────────────

import math

def _to_json_safe(obj):
    """Chuyển đổi đệ quy các kiểu dữ liệu pandas/numpy thành kiểu JSON thuần."""
    import numpy as np
    if isinstance(obj, dict):
        return {k: _to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_json_safe(i) for i in obj]
    if isinstance(obj, pd.Timestamp):
        return obj.strftime('%d/%m/%Y') if not pd.isnull(obj) else None
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        return None if math.isnan(v) else v
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if obj is pd.NaT:
        return None
    return obj

# Danh mục phân loại
_LOAI_CA_NHAN = [
    'TG KKH Cá nhân (Số đẹp)',
    'TG KKH CB lương Ngân sách',
    'Tiền gửi thanh toán cá nhân',
    'TG thanh toán cá nhân eKYC',
]
_LOAI_TO_CHUC = [
    'Tg KKH TCKT (Số đẹp)',
    'TG KKH TCKT',
    'TKTT Hộ kinh doanh',
]
# locdpnm dùng để nhận diện HSSV (phải là CA NHÂN loại này)
_LOCDPNM_HSSV = 'Tiền gửi thanh toán cá nhân'

# Các tên cột số tài khoản có thể có trong file mở TK (theo thứ tự ưu tiên)
_POSSIBLE_ACCTNO_COLS = ['idxacno', 'acctno', 'acctcd', 'acctseq', 'so_tai_khoan', 'account_no']


def _find_col(df_cols, candidates):
    """Tìm tên cột trong df theo danh sách ứng viên (case-insensitive)."""
    lower_map = {c.lower(): c for c in df_cols}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None


@login_required
def dong_mo_tai_khoan_report_view(request):
    """Giao diện báo cáo Đóng/Mở tài khoản"""
    from .models import DongMoTaiKhoanHistory
    from django.db.models import Sum
    from django.db.models.functions import TruncYear, TruncQuarter, TruncMonth

    # Xóa session cũ nếu sai format
    old = request.session.get('dmtk_result')
    if old and 'has_dong_tk_file' not in old:
        del request.session['dmtk_result']

    # Lịch sử theo tháng
    history_monthly = list(
        DongMoTaiKhoanHistory.objects.order_by('-report_month').values(
            'report_month', 'tong_mo', 'ca_nhan_count', 'to_chuc_count',
            'the_mien_phi_count', 'hssv_count',
            'dong_tk_count', 'dong_he_thong_count', 'dong_tai_quay_count'
        )
    )

    # Tổng hợp theo quý
    history_quarterly = list(
        DongMoTaiKhoanHistory.objects
        .annotate(quy=TruncQuarter('report_month'))
        .values('quy')
        .annotate(
            tong_mo=Sum('tong_mo'),
            ca_nhan_count=Sum('ca_nhan_count'),
            to_chuc_count=Sum('to_chuc_count'),
            the_mien_phi_count=Sum('the_mien_phi_count'),
            hssv_count=Sum('hssv_count'),
            dong_tk_count=Sum('dong_tk_count'),
            dong_he_thong_count=Sum('dong_he_thong_count'),
            dong_tai_quay_count=Sum('dong_tai_quay_count'),
        )
        .order_by('-quy')
    )
    # Tính số quý từ tháng đầu quý
    for row in history_quarterly:
        m = row['quy'].month
        row['quy_label'] = f"Q{(m-1)//3+1}/{row['quy'].year}"

    # Tổng hợp theo năm
    history_yearly = list(
        DongMoTaiKhoanHistory.objects
        .annotate(nam=TruncYear('report_month'))
        .values('nam')
        .annotate(
            tong_mo=Sum('tong_mo'),
            ca_nhan_count=Sum('ca_nhan_count'),
            to_chuc_count=Sum('to_chuc_count'),
            the_mien_phi_count=Sum('the_mien_phi_count'),
            hssv_count=Sum('hssv_count'),
            dong_tk_count=Sum('dong_tk_count'),
            dong_he_thong_count=Sum('dong_he_thong_count'),
            dong_tai_quay_count=Sum('dong_tai_quay_count'),
        )
        .order_by('-nam')
    )

    return render(request, 'templates_app/reports/dong_mo_tai_khoan.html', {
        'history_monthly': history_monthly,
        'history_quarterly': history_quarterly,
        'history_yearly': history_yearly,
    })


@login_required
@require_http_methods(["POST"])
def process_dong_mo_tai_khoan_report(request):
    """Xử lý báo cáo Đóng/Mở tài khoản"""
    try:
        mo_tk_file   = request.FILES.get('mo_tk_file')
        dong_tk_file = request.FILES.get('dong_tk_file')  # tùy chọn
        the_file     = request.FILES.get('the_file')      # tùy chọn

        if not mo_tk_file:
            messages.error(request, "Vui lòng tải lên file Mở tài khoản.")
            return redirect('dong_mo_tai_khoan_report')

        # ── Đọc file mở tài khoản ──────────────────────────────────────────
        try:
            df_mo = pd.read_excel(mo_tk_file)
            df_mo.columns = df_mo.columns.str.strip()
        except Exception as e:
            messages.error(request, f"Không đọc được file Mở tài khoản: {e}")
            return redirect('dong_mo_tai_khoan_report')

        # Kiểm tra cột bắt buộc locdpnm
        locdpnm_col = _find_col(df_mo.columns, ['locdpnm', 'loai_sp', 'loai_tk', 'product_name'])
        if locdpnm_col is None:
            messages.error(
                request,
                f"Không tìm thấy cột 'locdpnm' trong file Mở tài khoản. "
                f"Các cột hiện có: {', '.join(df_mo.columns.tolist())}"
            )
            return redirect('dong_mo_tai_khoan_report')

        df_mo[locdpnm_col] = df_mo[locdpnm_col].astype(str).str.strip()

        # ── Phân loại cơ bản ───────────────────────────────────────────────
        mask_cn  = df_mo[locdpnm_col].isin(_LOAI_CA_NHAN)
        mask_tc  = df_mo[locdpnm_col].isin(_LOAI_TO_CHUC)

        df_ca_nhan  = df_mo[mask_cn].copy()
        df_to_chuc  = df_mo[mask_tc].copy()

        # ── Nhận diện Thẻ miễn phí và HSSV qua file phát hành thẻ ──────────
        the_mien_phi_count   = 0
        the_mien_phi_records = []
        hssv_count           = 0
        hssv_records         = []
        join_col_mo          = None
        join_warning         = None

        if the_file:
            try:
                df_the = pd.read_excel(the_file)
                df_the.columns = df_the.columns.str.strip()

                # Kiểm tra cột bắt buộc của file thẻ
                missing_the_cols = [c for c in ['ISSUE_TYPE', 'HASFEE_DES']
                                    if _find_col(df_the.columns, [c]) is None]
                if missing_the_cols:
                    join_warning = (
                        f"File phát hành thẻ thiếu cột: {', '.join(missing_the_cols)}. "
                        f"Không thể xác định HSSV."
                    )
                else:
                    issue_col  = _find_col(df_the.columns, ['ISSUE_TYPE'])
                    hasfee_col = _find_col(df_the.columns, ['HASFEE_DES'])

                    # Lọc thẻ HSSV: CSP_New + MIỄN PHÍ PHT
                    mask_hssv_the = (
                        (df_the[issue_col].astype(str).str.strip() == 'CSP_New') &
                        (df_the[hasfee_col].astype(str).str.strip().str.upper() == 'MIỄN PHÍ PHT')
                    )
                    df_the_hssv = df_the[mask_hssv_the].copy()

                    # Tìm cột số tài khoản để join
                    join_col_the = _find_col(df_the.columns, ['ACCOUNT', 'idxacno', 'acctseq', 'acctno', 'acctcd', 'so_tai_khoan'])
                    join_col_mo  = _find_col(df_mo.columns,  _POSSIBLE_ACCTNO_COLS)

                    # Mapping CUSER → Phòng giao dịch
                    _CUSER_PGD_MAP = {
                        '7202canhsh':   'PGD Láng Tròn',
                        '7202cthaotn':  'PGD Láng Tròn',
                        '7202cthuclt':  'PGD Giá Rai',
                        '7202cthaotlt': 'PGD Giá Rai',
                        '7202chieutt':  'Hội sở Giá Rai',
                        '7202csinhnt':  'Hội sở Giá Rai',
                        '7202cchica':   'Hội sở Giá Rai',
                        '7202cnhitn':   'Hội sở Giá Rai',
                    }

                    if join_col_the and join_col_mo:
                        # Chuẩn hóa key join — chuyển về string, bỏ khoảng trắng, bỏ .0 cuối (nếu số)
                        def _norm_acct(s):
                            s = str(s).strip()
                            if s.endswith('.0'):
                                s = s[:-2]
                            return s

                        df_the_hssv = df_the_hssv.copy()
                        df_the_hssv['_key'] = df_the_hssv[join_col_the].apply(_norm_acct)

                        # Cột thông tin bổ sung từ file thẻ
                        custviename_col  = _find_col(df_the.columns, ['CUSTVIENAME'])
                        cdate_col        = _find_col(df_the.columns, ['CDATE'])
                        cuser_col        = _find_col(df_the.columns, ['CUSER'])
                        birthdate_col    = _find_col(df_the.columns, ['CUSTBIRTHDATE'])

                        # ── Thẻ miễn phí: toàn bộ CSP_New + MIỄN PHÍ PHT ──
                        tmp_acct_set = set(df_the_hssv['_key'])
                        mask_tmp = df_mo[join_col_mo].apply(_norm_acct).isin(tmp_acct_set)
                        df_tmp = df_mo[mask_tmp].copy()
                        df_tmp['_key'] = df_tmp[join_col_mo].apply(_norm_acct)
                        the_lookup_all = df_the_hssv.set_index('_key')

                        def _get_info(acct, lookup):
                            if acct not in lookup.index:
                                return {'ho_ten': '', 'ngay_mo_the': '', 'cuser': '', 'pgd': '', 'ngay_sinh': '', 'tuoi': ''}
                            row = lookup.loc[acct]
                            if isinstance(row, pd.DataFrame):
                                row = row.iloc[0]
                            cuser_val = str(row[cuser_col]).strip() if cuser_col else ''
                            # Tính tuổi
                            ngay_sinh_str = ''
                            tuoi_str = ''
                            if birthdate_col:
                                raw_bd = row[birthdate_col]
                                try:
                                    import datetime
                                    if pd.isna(raw_bd):
                                        pass
                                    else:
                                        bd = pd.to_datetime(raw_bd, dayfirst=True, errors='coerce')
                                        if pd.notna(bd):
                                            today = datetime.date.today()
                                            tuoi = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
                                            ngay_sinh_str = bd.strftime('%d/%m/%Y')
                                            tuoi_str = str(tuoi)
                                except Exception:
                                    pass
                            return {
                                'ho_ten':      str(row[custviename_col]).strip() if custviename_col else '',
                                'ngay_mo_the': str(row[cdate_col]).strip()       if cdate_col       else '',
                                'cuser':       cuser_val,
                                'pgd':         _CUSER_PGD_MAP.get(cuser_val.lower(), cuser_val),
                                'ngay_sinh':   ngay_sinh_str,
                                'tuoi':        tuoi_str,
                            }

                        def _build_records(df_joined, lookup):
                            records = []
                            for _, row in df_joined.head(500).iterrows():
                                acct = str(row[join_col_mo]).strip()
                                if acct.endswith('.0'):
                                    acct = acct[:-2]
                                info = _get_info(acct, lookup)
                                records.append({
                                    'so_tai_khoan': acct,
                                    'ho_ten':       info['ho_ten'],
                                    'ngay_mo_the':  info['ngay_mo_the'],
                                    'ngay_sinh':    info['ngay_sinh'],
                                    'tuoi':         info['tuoi'],
                                    'cuser':        info['cuser'],
                                    'pgd':          info['pgd'],
                                })
                            return records

                        the_mien_phi_count   = len(df_tmp)
                        the_mien_phi_records = _build_records(df_tmp, the_lookup_all)

                        # ── HSSV: thêm điều kiện tuổi < 18 ──────────────────
                        if birthdate_col:
                            import datetime
                            today = datetime.date.today()

                            def _is_under_18(acct):
                                if acct not in the_lookup_all.index:
                                    return False
                                row = the_lookup_all.loc[acct]
                                if isinstance(row, pd.DataFrame):
                                    row = row.iloc[0]
                                raw_bd = row[birthdate_col]
                                try:
                                    if pd.isna(raw_bd):
                                        return False
                                    bd = pd.to_datetime(raw_bd, dayfirst=True, errors='coerce')
                                    if pd.isna(bd):
                                        return False
                                    tuoi = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
                                    return tuoi < 18
                                except Exception:
                                    return False

                            mask_hssv = df_tmp['_key'].apply(_is_under_18)
                            df_hssv_new = df_tmp[mask_hssv].copy()
                            hssv_count   = len(df_hssv_new)
                            hssv_records = _build_records(df_hssv_new, the_lookup_all)
                        else:
                            join_warning = "File thẻ thiếu cột CUSTBIRTHDATE — không thể lọc HSSV theo tuổi."

                        if the_mien_phi_count == 0:
                            join_warning = (
                                f"[Debug] Thẻ lọc được: {len(df_the_hssv)} | "
                                f"Cột join thẻ: '{join_col_the}' | Cột join mở TK: '{join_col_mo}' | "
                                f"Mẫu TK thẻ: {list(tmp_acct_set)[:3]} | "
                                f"Mẫu TK mở TK: {[_norm_acct(v) for v in df_mo[join_col_mo].head(3).tolist()]}"
                            )
                    else:
                        missing = []
                        if not join_col_the: missing.append("file thẻ thiếu cột số tài khoản")
                        if not join_col_mo:  missing.append(f"file mở TK thiếu cột số tài khoản (thử: {', '.join(_POSSIBLE_ACCTNO_COLS)})")
                        join_warning = "Không thể join: " + "; ".join(missing)

            except Exception as e:
                join_warning = f"Lỗi khi xử lý file phát hành thẻ: {e}"

        # ── Xử lý file Đóng tài khoản ─────────────────────────────────────
        dong_tk_count       = 0
        dong_he_thong_count = 0
        dong_tai_quay_count = 0
        dong_tk_records     = []
        dong_col_labels     = []

        if dong_tk_file:
            try:
                df_dong = pd.read_excel(dong_tk_file)
                df_dong.columns = df_dong.columns.str.strip()

                teller_col_dong = _find_col(df_dong.columns, ['tellernm', 'teller', 'teller_name'])
                _DONG_WANT_COLS   = ['idxacno', 'custnm', 'locdpnm', 'clsdt', 'tellernm']
                _DONG_WANT_LABELS = ['Số tài khoản', 'Họ tên', 'Loại sản phẩm', 'Ngày đóng', 'Teller']

                dong_actual_cols = []
                for col_key, col_label in zip(_DONG_WANT_COLS, _DONG_WANT_LABELS):
                    actual = _find_col(df_dong.columns, [col_key])
                    if actual:
                        dong_actual_cols.append((actual, col_label))
                dong_col_labels = [lbl for _, lbl in dong_actual_cols]

                def _loai_dong(teller_val):
                    t = str(teller_val).strip().upper()
                    if t == '7202DP':
                        return 'Hệ thống tự đóng'
                    elif t.startswith('GRA'):
                        return 'KH đóng tại quầy'
                    return str(teller_val).strip()

                def _norm_val(v):
                    if v is None:
                        return ''
                    try:
                        import math
                        if isinstance(v, float) and math.isnan(v):
                            return ''
                    except Exception:
                        pass
                    return str(v)

                dong_tk_count = len(df_dong)
                if teller_col_dong:
                    dong_he_thong_count = int((df_dong[teller_col_dong].astype(str).str.strip().str.upper() == '7202DP').sum())
                    dong_tai_quay_count = int(df_dong[teller_col_dong].astype(str).str.strip().str.upper().str.startswith('GRA').sum())

                for _, row in df_dong.head(500).iterrows():
                    vals = [_norm_val(row[col]) for col, _ in dong_actual_cols]
                    loai = _loai_dong(row[teller_col_dong]) if teller_col_dong else ''
                    dong_tk_records.append({'vals': vals, 'loai_dong': loai})

            except Exception as e:
                messages.warning(request, f"Lỗi đọc file Đóng tài khoản: {e}")

        # ── Thống kê chi tiết theo locdpnm ────────────────────────────────
        def _breakdown(df):
            return (
                df[locdpnm_col]
                .value_counts()
                .reset_index()
                .rename(columns={locdpnm_col: 'loai', 'count': 'so_luong'})
                .to_dict('records')
            )

        # ── Cột hiển thị bảng chi tiết (list of lists để template iterate) ─
        _WANT_COLS   = ['idxacno', 'custnm', 'locdpnm', 'opndt', 'curbal', 'onofftp', 'tellernm']
        _WANT_LABELS = ['Số tài khoản', 'Họ tên', 'Loại sản phẩm', 'Ngày mở', 'Số dư hiện tại', 'Đơn vị', 'Teller']

        actual_view_cols = []
        view_col_labels  = []
        for col_key, col_label in zip(_WANT_COLS, _WANT_LABELS):
            actual = _find_col(df_mo.columns, [col_key])
            if actual:
                actual_view_cols.append(actual)
                view_col_labels.append(col_label)

        def _to_list_records(df, limit=500):
            rows = []
            for _, row in df.head(limit).iterrows():
                rows.append([
                    '' if (row[c] is None or (hasattr(row[c], '__class__') and str(type(row[c])) == "<class 'float'>" and str(row[c]) == 'nan')) else str(row[c])
                    for c in actual_view_cols
                ])
            return rows

        # ── Tổng hợp kết quả ──────────────────────────────────────────────
        result = {
            'tong_mo': len(df_mo),
            'ca_nhan_count': len(df_ca_nhan),
            'the_mien_phi_count': the_mien_phi_count,
            'hssv_count': hssv_count,
            'to_chuc_count': len(df_to_chuc),
            'ca_nhan_breakdown': _breakdown(df_ca_nhan),
            'to_chuc_breakdown': _breakdown(df_to_chuc),
            'ca_nhan_records': _to_list_records(df_ca_nhan),
            'to_chuc_records': _to_list_records(df_to_chuc),
            'view_col_labels': view_col_labels,
            'the_mien_phi_records': the_mien_phi_records,
            'hssv_records': hssv_records,
            'join_warning': join_warning,
            'has_the_file': the_file is not None,
            'has_dong_tk_file': dong_tk_file is not None,
            'dong_tk_count': dong_tk_count,
            'dong_he_thong_count': dong_he_thong_count,
            'dong_tai_quay_count': dong_tai_quay_count,
            'dong_tk_records': dong_tk_records,
            'dong_col_labels': dong_col_labels,
        }

        request.session['dmtk_result'] = _to_json_safe(result)

        # Lưu lịch sử nếu có chọn kỳ báo cáo
        report_month_str = request.POST.get('report_month', '').strip()
        if report_month_str:
            try:
                from .models import DongMoTaiKhoanHistory
                import datetime
                report_month = datetime.date.fromisoformat(report_month_str).replace(day=1)
                DongMoTaiKhoanHistory.objects.update_or_create(
                    report_month=report_month,
                    defaults={
                        'tong_mo': result['tong_mo'],
                        'ca_nhan_count': result['ca_nhan_count'],
                        'to_chuc_count': result['to_chuc_count'],
                        'the_mien_phi_count': result['the_mien_phi_count'],
                        'hssv_count': result['hssv_count'],
                        'dong_tk_count': result['dong_tk_count'],
                        'dong_he_thong_count': result['dong_he_thong_count'],
                        'dong_tai_quay_count': result['dong_tai_quay_count'],
                    }
                )
                messages.success(request, f"Đã lưu thống kê kỳ {report_month.strftime('%m/%Y')} vào lịch sử.")
            except Exception as e:
                messages.warning(request, f"Không thể lưu lịch sử: {e}")

        return redirect('dong_mo_tai_khoan_report')

    except Exception as e:
        traceback.print_exc()
        messages.error(request, f"Đã xảy ra lỗi: {e}")
        return redirect('dong_mo_tai_khoan_report')

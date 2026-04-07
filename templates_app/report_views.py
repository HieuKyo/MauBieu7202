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
def process_phat_hanh_the_report(request):
    """Xử lý báo cáo Phát hành thẻ"""
    try:
        # Lấy cấu hình từ database
        try:
            config_obj = ReportConfiguration.objects.get(report_type='phat_hanh_the', is_active=True)
            pht_config = config_obj.config_data
        except (ReportConfiguration.DoesNotExist, Exception):
            # Cấu hình mặc định
            pht_config = {
                'pgd_user_map': {
                    "PGD Phường 1": ["GRALTHUC", "GRATTHAO"],
                    "PGD Láng Tròn": ["GRANTHAO", "GRASHANH"],
                    "Hội Sở": ["GRATNNHI", "GRANSINH", "GRATHIEU", "GRACACHI", "Yến Mi"]
                }
            }
            messages.info(request, "Sử dụng cấu hình mặc định vì chưa có cấu hình trong database.")

        data_file = request.FILES.get('data_file')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        if not all([data_file, start_date_str, end_date_str]):
            messages.error(request, "Vui lòng cung cấp đủ file và khoảng thời gian.")
            return redirect('phat_hanh_the_report')

        df = pd.read_excel(data_file)

        # Debug: Kiểm tra columns
        print(f"DEBUG: Columns in file: {df.columns.tolist()}")
        print(f"DEBUG: Total rows: {len(df)}")

        if 'acctseq' in df.columns:
            df['acctseq'] = df['acctseq'].astype(str)

        # Kiểm tra cột dlvrydt tồn tại
        if 'dlvrydt' not in df.columns:
            messages.error(request, "File không có cột 'dlvrydt' (Ngày phát hành). Vui lòng kiểm tra lại file Excel.")
            return redirect('phat_hanh_the_report')

        df['dlvrydt_datetime'] = pd.to_datetime(df['dlvrydt'], format='%d/%m/%Y', errors='coerce').dt.normalize()

        start_date = pd.to_datetime(start_date_str)
        end_date = pd.to_datetime(end_date_str)

        mask = (df['dlvrydt_datetime'] >= start_date) & (df['dlvrydt_datetime'] <= end_date)
        filtered_df = df.loc[mask].copy()

        print(f"DEBUG: Filtered rows (by date): {len(filtered_df)}")

        if filtered_df.empty:
            messages.warning(request, "Không có dữ liệu phát hành thẻ trong khoảng thời gian đã chọn.")
            return redirect('phat_hanh_the_report')

        pgd_user_map = pht_config.get('pgd_user_map', {})
        print(f"DEBUG: PGD user map: {pgd_user_map}")

        user_to_pgd_map = {user: pgd for pgd, users in pgd_user_map.items() for user in users}
        print(f"DEBUG: User to PGD map: {user_to_pgd_map}")

        # Kiểm tra cột dlvryusrid tồn tại
        if 'dlvryusrid' not in filtered_df.columns:
            messages.error(request, "File không có cột 'dlvryusrid' (User phát hành). Vui lòng kiểm tra lại file Excel.")
            return redirect('phat_hanh_the_report')

        filtered_df['PGD'] = filtered_df['dlvryusrid'].map(user_to_pgd_map)
        final_df = filtered_df.dropna(subset=['PGD'])

        print(f"DEBUG: Final rows (after PGD mapping): {len(final_df)}")
        print(f"DEBUG: Unique users in data: {filtered_df['dlvryusrid'].unique().tolist()}")

        if final_df.empty:
            messages.warning(request, f"Không có dữ liệu nào khớp với các user trong cấu hình. Users trong file: {filtered_df['dlvryusrid'].unique().tolist()}")
            return redirect('phat_hanh_the_report')

        # Tạo Excel với nhiều sheet
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for pgd_name in pgd_user_map.keys():
                pgd_df = final_df[final_df['PGD'] == pgd_name]

                if not pgd_df.empty:
                    pgd_df_to_output = pgd_df.copy()
                    pgd_df_to_output['dlvrydt_str'] = pgd_df_to_output['dlvrydt_datetime'].dt.strftime('%d/%m/%Y')

                    # Kiểm tra các cột cần thiết
                    required_cols = ['custnm', 'acctseq', 'cdtpcdnm', 'dlvryusrid']
                    missing_cols = [col for col in required_cols if col not in pgd_df_to_output.columns]
                    if missing_cols:
                        print(f"WARNING: Missing columns for PGD {pgd_name}: {missing_cols}")
                        continue

                    output_cols = ['custnm', 'acctseq', 'cdtpcdnm', 'dlvryusrid', 'dlvrydt_str']
                    pgd_df_final = pgd_df_to_output[output_cols].rename(columns={
                        'custnm': 'Họ tên',
                        'acctseq': 'Số tài khoản',
                        'cdtpcdnm': 'Loại thẻ',
                        'dlvryusrid': 'User phát hành',
                        'dlvrydt_str': 'Ngày phát hành'
                    })

                    print(f"DEBUG: Creating sheet for {pgd_name} with {len(pgd_df_final)} rows")

                    pgd_df_final.to_excel(writer, sheet_name=pgd_name, index=False, startrow=3)

                    worksheet = writer.sheets[pgd_name]

                    title = f"DANH SÁCH THẺ PHÁT HÀNH CỦA {pgd_name.upper()}"
                    date_range_str = f"Từ ngày {pd.to_datetime(start_date_str).strftime('%d/%m/%Y')} đến ngày {pd.to_datetime(end_date_str).strftime('%d/%m/%Y')}"

                    worksheet['A1'] = title
                    worksheet.merge_cells('A1:E1')
                    worksheet['A1'].font = Font(bold=True, size=14)
                    worksheet['A1'].alignment = Alignment(horizontal='center')

                    worksheet['A2'] = date_range_str
                    worksheet.merge_cells('A2:E2')
                    worksheet['A2'].font = Font(italic=True, size=11)
                    worksheet['A2'].alignment = Alignment(horizontal='center')

                    thin_border = Border(
                        left=Side(style='thin'),
                        right=Side(style='thin'),
                        top=Side(style='thin'),
                        bottom=Side(style='thin')
                    )

                    highlight_fill = PatternFill(
                        start_color="FFFFE0",
                        end_color="FFFFE0",
                        fill_type="solid"
                    )

                    start_data_row = 5
                    end_data_row = start_data_row + len(pgd_df_final) - 1

                    for row_idx in range(start_data_row, end_data_row + 1):
                        loai_the_cell = worksheet[f'C{row_idx}']
                        apply_highlight = False
                        if loai_the_cell.value != "(97040509)- The PLUS SUCCESS":
                            apply_highlight = True

                        for col_idx in range(1, len(pgd_df_final.columns) + 1):
                            cell = worksheet.cell(row=row_idx, column=col_idx)
                            cell.border = thin_border
                            if apply_highlight:
                                cell.fill = highlight_fill

                    for cell in worksheet[4]:
                        cell.border = thin_border

                    for col_idx in range(1, len(pgd_df_final.columns) + 1):
                        column_letter = get_column_letter(col_idx)
                        max_length = 0
                        for cell in worksheet[column_letter]:
                            if cell.row < 4:
                                continue
                            try:
                                if cell.value:
                                    cell_length = len(str(cell.value))
                                    if cell_length > max_length:
                                        max_length = cell_length
                            except:
                                pass
                        adjusted_width = min((max_length + 2), 60)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

                    # Fit sheet on one page when printing
                    worksheet.page_setup.fitToPage = True
                    worksheet.page_setup.fitToWidth = 1
                    worksheet.page_setup.fitToHeight = 0  # 0 = không giới hạn chiều cao, co dãn theo chiều rộng
                    if worksheet.sheet_properties.pageSetUpPr is None:
                        from openpyxl.worksheet.properties import PageSetupProperties
                        worksheet.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
                    else:
                        worksheet.sheet_properties.pageSetUpPr.fitToPage = True

        # Kiểm tra xem có sheet nào được tạo không
        if not writer.sheets:
            messages.warning(request, "Không có dữ liệu nào để tạo báo cáo. Vui lòng kiểm tra lại file và cấu hình.")
            return redirect('phat_hanh_the_report')

        print(f"DEBUG: Total sheets created: {len(writer.sheets)}")

        # Lưu dữ liệu vào session để sử dụng cho print preview
        pgd_data_for_session = {}
        for pgd_name in pgd_user_map.keys():
            pgd_df = final_df[final_df['PGD'] == pgd_name]
            if not pgd_df.empty:
                pgd_data_for_session[pgd_name] = len(pgd_df)

        request.session['phat_hanh_the_data'] = {
            'pgd_list': pgd_data_for_session,
            'start_date': pd.to_datetime(start_date_str).strftime('%d/%m/%Y'),
            'end_date': pd.to_datetime(end_date_str).strftime('%d/%m/%Y'),
        }

        output.seek(0)
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="BaoCao_PhatHanhThe_{start_date_str}_den_{end_date_str}.xlsx"'

        print("DEBUG: Returning file response")
        return response

    except Exception as e:
        traceback.print_exc()
        messages.error(request, f"Đã xảy ra lỗi: {e}")
        return redirect('phat_hanh_the_report')


@login_required
@require_http_methods(["POST"])
def process_phat_hanh_the_for_print(request):
    """Xử lý báo cáo Phát hành thẻ và chuyển tới trang in preview"""
    try:
        # Lấy cấu hình từ database
        try:
            config_obj = ReportConfiguration.objects.get(report_type='phat_hanh_the', is_active=True)
            pht_config = config_obj.config_data
        except (ReportConfiguration.DoesNotExist, Exception):
            pht_config = {
                'pgd_user_map': {
                    "PGD Phường 1": ["GRALTHUC", "GRATTHAO"],
                    "PGD Láng Tròn": ["GRANTHAO", "GRASHANH"],
                    "Hội Sở": ["GRATNNHI", "GRANSINH", "GRATHIEU", "GRACACHI", "Yến Mi"]
                }
            }

        data_file = request.FILES.get('data_file')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        if not all([data_file, start_date_str, end_date_str]):
            messages.error(request, "Vui lòng cung cấp đủ file và khoảng thời gian.")
            return redirect('phat_hanh_the_report')

        df = pd.read_excel(data_file)

        if 'acctseq' in df.columns:
            df['acctseq'] = df['acctseq'].astype(str)

        if 'dlvrydt' not in df.columns:
            messages.error(request, "File không có cột 'dlvrydt'. Vui lòng kiểm tra lại file Excel.")
            return redirect('phat_hanh_the_report')

        df['dlvrydt_datetime'] = pd.to_datetime(df['dlvrydt'], format='%d/%m/%Y', errors='coerce').dt.normalize()

        start_date = pd.to_datetime(start_date_str)
        end_date = pd.to_datetime(end_date_str)

        mask = (df['dlvrydt_datetime'] >= start_date) & (df['dlvrydt_datetime'] <= end_date)
        filtered_df = df.loc[mask].copy()

        if filtered_df.empty:
            messages.warning(request, "Không có dữ liệu phát hành thẻ trong khoảng thời gian đã chọn.")
            return redirect('phat_hanh_the_report')

        pgd_user_map = pht_config.get('pgd_user_map', {})
        user_to_pgd_map = {user: pgd for pgd, users in pgd_user_map.items() for user in users}

        if 'dlvryusrid' not in filtered_df.columns:
            messages.error(request, "File không có cột 'dlvryusrid'. Vui lòng kiểm tra lại file Excel.")
            return redirect('phat_hanh_the_report')

        filtered_df['PGD'] = filtered_df['dlvryusrid'].map(user_to_pgd_map)
        final_df = filtered_df.dropna(subset=['PGD'])

        if final_df.empty:
            messages.warning(request, f"Không có dữ liệu nào khớp với các user trong cấu hình.")
            return redirect('phat_hanh_the_report')

        # Lưu dữ liệu vào session
        pgd_data_for_session = {}
        for pgd_name in pgd_user_map.keys():
            pgd_df = final_df[final_df['PGD'] == pgd_name]
            if not pgd_df.empty:
                pgd_data_for_session[pgd_name] = len(pgd_df)

        request.session['phat_hanh_the_data'] = {
            'pgd_list': pgd_data_for_session,
            'start_date': pd.to_datetime(start_date_str).strftime('%d/%m/%Y'),
            'end_date': pd.to_datetime(end_date_str).strftime('%d/%m/%Y'),
        }

        return redirect('phat_hanh_the_print_preview')

    except Exception as e:
        traceback.print_exc()
        messages.error(request, f"Đã xảy ra lỗi: {e}")
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
    period_type = request.GET.get('period_type', 'month')  # month hoặc 6months
    tx_type_filter = request.GET.get('tx_type', '')  # deposit, withdrawal, transfer, other

    # Lấy danh sách các kỳ báo cáo có sẵn
    available_periods = ATMReportUpload.objects.all().order_by('-report_period')

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
                # Lấy 6 tháng gần nhất tính từ tháng được chọn
                start_date = period_date - relativedelta(months=5)
                queryset = queryset.filter(
                    report_period__gte=start_date,
                    report_period__lte=period_date
                )
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
    # Xóa session cũ nếu sai format
    old = request.session.get('dmtk_result')
    if old and 'has_dong_tk_file' not in old:
        del request.session['dmtk_result']
    return render(request, 'templates_app/reports/dong_mo_tai_khoan.html')


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
        return redirect('dong_mo_tai_khoan_report')

    except Exception as e:
        traceback.print_exc()
        messages.error(request, f"Đã xảy ra lỗi: {e}")
        return redirect('dong_mo_tai_khoan_report')

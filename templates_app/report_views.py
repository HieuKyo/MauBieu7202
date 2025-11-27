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
            df = pd.read_excel(file)

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
            'Dư nợ gốc kỳ này', 'Lãi kỳ này',
            'Dư nợ gốc kỳ SS', 'Lãi kỳ SS',
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

        # Kiểm tra xem có sheet nào được tạo không
        if not writer.sheets:
            messages.warning(request, "Không có dữ liệu nào để tạo báo cáo. Vui lòng kiểm tra lại file và cấu hình.")
            return redirect('phat_hanh_the_report')

        print(f"DEBUG: Total sheets created: {len(writer.sheets)}")

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
def salary_conversion_view(request):
    """Giao diện chuyển đổi file lương"""
    # Lấy cấu hình từ database
    try:
        config_obj = ReportConfiguration.objects.get(report_type='luong', is_active=True)
        don_vi_map = config_obj.config_data.get('don_vi_chi_tra', {})
    except:
        don_vi_map = {}

    return render(request, 'templates_app/reports/salary_conversion.html', {'don_vi_map': don_vi_map})


@login_required
@require_http_methods(["POST"])
def process_salary_conversion(request):
    """Xử lý chuyển đổi file lương"""
    try:
        # Lấy cấu hình từ database
        try:
            config_obj = ReportConfiguration.objects.get(report_type='luong', is_active=True)
            luong_config = config_obj.config_data
        except:
            luong_config = {
                'don_vi_chi_tra': {
                    "7202201001629": "Agribank CHI NHANH GIA RAI BAC LIEU"
                }
            }

        salary_file = request.FILES.get('salary_file')
        payer_account = request.POST.get('payer_account')

        if not salary_file or not payer_account:
            messages.error(request, "Vui lòng cung cấp đủ thông tin.")
            return redirect('salary_conversion')

        don_vi_map = luong_config.get('don_vi_chi_tra', {})
        payer_name = don_vi_map.get(payer_account, "KHONG TIM THAY")

        if payer_name == "KHONG TIM THAY":
            messages.error(request, f"Số tài khoản {payer_account} không được tìm thấy trong cấu hình.")
            return redirect('salary_conversion')

        # Đọc toàn bộ file vào DataFrame
        df_full = pd.read_excel(salary_file, header=None)

        # Tìm dòng đầu tiên có STT = 1
        start_row_index = -1
        for index, row in df_full.iterrows():
            stt_value = pd.to_numeric(row.iloc[0], errors='coerce')
            if stt_value == 1:
                start_row_index = index
                break

        if start_row_index == -1:
            messages.error(request, "Không tìm thấy dòng bắt đầu của bảng dữ liệu (dòng có STT = 1).")
            return redirect('salary_conversion')

        # Cắt DataFrame để chỉ lấy phần bảng dữ liệu thực sự
        df_data = df_full.iloc[start_row_index:].copy()
        df_data.columns = range(df_data.shape[1])
        df_data.dropna(how='all', inplace=True)

        if df_data.shape[1] < 5:
            messages.error(request, "Bảng dữ liệu không có đủ 5 cột (A, B, C, D, E).")
            return redirect('salary_conversion')

        # Tạo DataFrame mới theo định dạng file CSV lô
        output_df = pd.DataFrame()
        output_df['Payer_Account'] = payer_account
        output_df['Payee_Account'] = df_data[2]  # Cột C - Số tài khoản
        output_df['Amount'] = df_data[4]          # Cột E - Số tiền
        output_df['Description'] = f"Chuyển lương {payer_name}"

        # Chuyển đổi DataFrame thành CSV
        csv_output = output_df.to_csv(index=False, header=False, encoding='utf-8-sig')

        response = HttpResponse(csv_output, content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="salary_batch_{payer_account}.csv"'
        return response

    except Exception as e:
        traceback.print_exc()
        messages.error(request, f"Đã xảy ra lỗi: {e}")
        return redirect('salary_conversion')

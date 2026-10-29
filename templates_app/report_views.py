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
    return render(request, 'templates_app/reports/phat_hanh_the.html', {'current_month': datetime.now().strftime('%Y-%m')})


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


def _read_excel_safe(file_obj, **kwargs):
    """Đọc file Excel, tự bỏ qua workbook corruption cho file .xls cũ.
    Truyền usecols=... để chỉ đọc cột cần thiết, giảm bộ nhớ cho file lớn."""
    file_bytes = file_obj.read() if hasattr(file_obj, 'read') else file_obj
    try:
        return pd.read_excel(io.BytesIO(file_bytes), **kwargs)
    except Exception:
        import xlrd
        wb = xlrd.open_workbook(file_contents=file_bytes, ignore_workbook_corruption=True)
        return pd.read_excel(wb, **kwargs)


def _read_csv_robust(file_obj, usecols=None):
    """
    Đọc file .csv thử qua nhiều encoding (file xuất từ IPCAS thường là Windows-1258/ANSI
    tiếng Việt, không phải UTF-8) kết hợp dấu phẩy/tab làm dấu phân cách — ưu tiên kết quả
    đọc ra nhiều hơn 1 cột. Tự giải mã bytes → text trước để tránh lỗi nội bộ của pandas khi
    kết hợp tự dò encoding/delimiter trực tiếp trên file object nhị phân.
    """
    raw = file_obj.read() if hasattr(file_obj, 'read') else file_obj
    if isinstance(raw, str):
        raw = raw.encode('utf-8')

    best = None
    last_err = None
    for encoding in ('utf-8', 'utf-8-sig', 'cp1258', 'latin1'):
        try:
            text = raw.decode(encoding)
        except UnicodeDecodeError as e:
            last_err = e
            continue
        for sep in (',', '\t'):
            try:
                df = pd.read_csv(io.StringIO(text), sep=sep)
            except pd.errors.ParserError as e:
                last_err = e
                continue
            if df.shape[1] > 1:
                df.columns = [str(c).strip() for c in df.columns]
                return df[usecols] if usecols else df
            if best is None:
                best = df
    if best is not None:
        best.columns = [str(c).strip() for c in best.columns]
        return best[usecols] if usecols else best
    raise last_err


def _strip_text_marker(series):
    """Bỏ dấu ' ở đầu giá trị (marker buộc kiểu text khi export CSV từ IPCAS) và khoảng trắng dư."""
    return series.astype(str).str.strip().str.lstrip("'").str.strip()


def _read_atm_normalized(data_file, start_date_str, end_date_str, pgd_user_map):
    """
    Đọc file ATM (cấu trúc mới), lọc theo ngày và PGD.
    Trả về DataFrame chuẩn hóa với cột:
      Họ tên | Số tài khoản | Loại thẻ | GDV phát hành | Ngày phát hành | PGD
    Hoặc None nếu không có dữ liệu / lỗi cột.
    """
    df = _read_excel_safe(data_file)
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
    df = _read_excel_safe(visa_file)
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


_THE_OUTPUT_COLS = ['Họ tên', 'Số tài khoản', 'Loại thẻ', 'GDV phát hành', 'Ngày phát hành']


def _write_the_sheet(writer, sheet_name, df, title, subtitle, highlight=True, then_sort_by=()):
    """
    Ghi 1 sheet danh sách thẻ với tiêu đề, border, auto-fit.
    Sắp theo ngày phát hành, rồi lần lượt theo các cột trong then_sort_by (không phân biệt hoa/thường).
    """
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    highlight_fill = PatternFill(start_color="FFFFE0", end_color="FFFFE0", fill_type="solid")
    no_card_fill = PatternFill(start_color="FCE4E4", end_color="FCE4E4", fill_type="solid")

    df_final = (
        df.assign(_sort_date=pd.to_datetime(df['Ngày phát hành'], format='%d/%m/%Y', errors='coerce'))
        .sort_values(
            ['_sort_date', *then_sort_by], kind='stable',
            key=lambda s: s.astype(str).str.lower() if s.name in then_sort_by else s
        )
        .drop(columns=['_sort_date'])
        .reset_index(drop=True)
    )
    n_cols = len(df_final.columns)
    last_col = get_column_letter(n_cols)

    df_final.to_excel(writer, sheet_name=sheet_name, index=False, startrow=3)
    ws = writer.sheets[sheet_name]

    ws['A1'] = title
    ws.merge_cells(f'A1:{last_col}1')
    ws['A1'].font = Font(bold=True, size=14)
    ws['A1'].alignment = Alignment(horizontal='center')

    ws['A2'] = subtitle
    ws.merge_cells(f'A2:{last_col}2')
    ws['A2'].font = Font(italic=True, size=11)
    ws['A2'].alignment = Alignment(horizontal='center')

    # Border + highlight cho dữ liệu
    for row_idx in range(5, 5 + len(df_final)):
        loai_the = ws[f'C{row_idx}'].value or ''
        if loai_the == _NO_CARD_LABEL:
            fill = no_card_fill
        elif highlight and loai_the not in ('PSuccess', '(486283)-Visa Gold Debit'):
            fill = highlight_fill
        else:
            fill = None
        for col_idx in range(1, n_cols + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.border = thin_border
            if fill:
                cell.fill = fill

    for cell in ws[4]:
        cell.border = thin_border

    # Auto-fit cột
    for col_idx in range(1, n_cols + 1):
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


def _build_phat_hanh_the_excel(combined_df, pgd_user_map, start_date_str, end_date_str):
    """Tạo Excel nhiều sheet từ DataFrame đã chuẩn hóa"""
    output = io.BytesIO()
    sheets_created = 0

    date_range_str = (
        f"Từ ngày {pd.to_datetime(start_date_str).strftime('%d/%m/%Y')} "
        f"đến ngày {pd.to_datetime(end_date_str).strftime('%d/%m/%Y')}"
    )

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for pgd_name in pgd_user_map.keys():
            pgd_df = combined_df[combined_df['PGD'] == pgd_name]
            if pgd_df.empty:
                continue

            sheets_created += 1
            _write_the_sheet(
                writer, pgd_name, pgd_df[_THE_OUTPUT_COLS],
                f"DANH SÁCH THẺ PHÁT HÀNH CỦA {pgd_name.upper()}", date_range_str
            )

    return output, sheets_created


def _read_csp_free_cards(file_bytes, start_date_str, end_date_str, pgd_user_map):
    """
    Đọc file CSP, lấy toàn bộ thẻ miễn phí trong kỳ — không lọc theo GDV.
    Miễn phí: FEEISSUECARD = 0 (hoặc trống) và IS_DEBIT khác 'TTT Báo nợ'.
    Trả về DataFrame cột _THE_OUTPUT_COLS + 'Đơn vị' (GDV ngoài cấu hình ghi 'Khác').
    """
    df = _read_excel_safe(file_bytes)
    df.columns = df.columns.str.strip()

    for col in ['CDATE', 'CUSER', 'CUSTVIENAME', 'ACCOUNT', 'CARDTYPE', 'FEEISSUECARD', 'IS_DEBIT']:
        if col not in df.columns:
            return None, f"File CSP không có cột '{col}'."

    df['_date'] = pd.to_datetime(df['CDATE'].astype(str).str[:10], format='%d/%m/%Y', errors='coerce').dt.normalize()
    df = df[(df['_date'] >= pd.to_datetime(start_date_str)) & (df['_date'] <= pd.to_datetime(end_date_str))]

    fee = pd.to_numeric(
        df['FEEISSUECARD'].astype(str).str.replace(',', '', regex=False).str.strip(), errors='coerce'
    ).fillna(0)
    is_debit = df['IS_DEBIT'].astype(str).str.strip().str.lower() == 'ttt báo nợ'
    df = df[(fee == 0) & ~is_debit]

    user_map = {u: pgd for pgd, users in pgd_user_map.items() for u in users}
    result = pd.DataFrame({
        'Họ tên':          df['CUSTVIENAME'].values,
        'Số tài khoản':    df['ACCOUNT'].astype(str).values,
        'Loại thẻ':        df['CARDTYPE'].values,
        'GDV phát hành':   df['CUSER'].values,
        'Ngày phát hành':  df['_date'].dt.strftime('%d/%m/%Y').values,
        'Đơn vị':          df['CUSER'].map(user_map).fillna('Khác').values,
    })
    return result, None


_NO_CARD_LABEL = 'Mở TK - chưa phát hành thẻ'
_DPDA19_EXCLUDED_TYPES = {'tktt hộ kinh doanh', 'tg thanh toán cá nhân ekyc', 'tg kkh tckt (số đẹp)', 'tg kkh tckt'}


def _norm_account(series):
    """Chuẩn hóa số TK về chuỗi để so khớp giữa các file (bỏ '.0' khi Excel đọc thành số)."""
    return series.astype(str).str.strip().str.replace(r'\.0$', '', regex=True)


# User CSP → user IPCAS (GRA...) cho GDV chưa khai trong hồ sơ người dùng (UserProfile được ưu tiên)
_CSP_TO_IPCAS_FALLBACK = {
    '7202cthuclt': 'GRALTHUC',
    '7202cthaotlt': 'GRATTHAO',
    '7202canhsh': 'GRASHANH',
    '7202cthaotn': 'GRANTHAO',
}


def _csp_to_ipcas_user_map():
    """Map user CSP (chữ thường) → user IPCAS: lấy từ UserProfile, bổ sung bằng _CSP_TO_IPCAS_FALLBACK."""
    from .models import UserProfile
    user_map = dict(_CSP_TO_IPCAS_FALLBACK)
    for csp_user, ipcas_user in (UserProfile.objects.exclude(csp_cuser='').exclude(ipcas_user='')
                                 .values_list('csp_cuser', 'ipcas_user')):
        user_map[csp_user.strip().lower()] = ipcas_user.strip()
    return user_map


def _read_accounts(file_bytes, col):
    """Tập số TK (đã chuẩn hóa) trong cột col của file Excel."""
    df = _read_excel_safe(file_bytes, dtype=str)
    df.columns = df.columns.str.strip()
    return set(_norm_account(df[col].dropna()))


def _read_dpda19_no_card(file_bytes, start_date_str, end_date_str, pgd_user_map, card_accounts):
    """
    Đọc file DPDA19 - OPEN, lấy TK mở trong kỳ (bỏ TK đóng ngay trong ngày mở: clsdt = opndt)
    mà số TK không có trong card_accounts (chưa phát hành thẻ).
    Bỏ các loại TK trong _DPDA19_EXCLUDED_TYPES; GDV mở TK (tellernm) map PGD theo user ID cũ.
    Trả về DataFrame cùng cột như _read_atm_normalized, Loại thẻ = _NO_CARD_LABEL.
    """
    df = _read_excel_safe(file_bytes, dtype={'idxacno': str})
    df.columns = df.columns.str.strip()

    for col in ['idxacno', 'custnm', 'opndt', 'locdpnm', 'tellernm', 'clsdt']:
        if col not in df.columns:
            return None, f"File DPDA19 không có cột '{col}'."

    def parse_date(col):
        if pd.api.types.is_datetime64_any_dtype(col):
            return col.dt.normalize()
        s = col.astype(str).str.strip().str[:10]
        return pd.to_datetime(s, format='%d/%m/%Y', errors='coerce').fillna(
            pd.to_datetime(s, format='%Y-%m-%d', errors='coerce'))

    df['_date'] = parse_date(df['opndt'])
    df = df[(df['_date'] >= pd.to_datetime(start_date_str)) & (df['_date'] <= pd.to_datetime(end_date_str))]

    # Bỏ TK mở xong đóng ngay trong ngày (clsdt = opndt)
    df = df[parse_date(df['clsdt']) != df['_date']]

    df = df[~df['locdpnm'].astype(str).str.strip().str.lower().isin(_DPDA19_EXCLUDED_TYPES)]
    df['_acct'] = _norm_account(df['idxacno'])
    df = df[~df['_acct'].isin(card_accounts)]

    user_map = {u: pgd for pgd, users in pgd_user_map.items() for u in users}
    df['PGD'] = df['tellernm'].astype(str).str.strip().map(user_map)
    df = df.dropna(subset=['PGD'])

    result = pd.DataFrame({
        'Họ tên':          df['custnm'].values,
        'Số tài khoản':    df['_acct'].values,
        'Loại thẻ':        _NO_CARD_LABEL,
        'GDV phát hành':   df['tellernm'].values,
        'Ngày phát hành':  df['_date'].dt.strftime('%d/%m/%Y').values,
        'PGD':             df['PGD'].values,
    })
    return result, None


@login_required
@require_http_methods(["POST"])
def process_phat_hanh_the_thang(request):
    """
    Báo cáo phát hành thẻ theo Tháng (chọn tháng/năm: từ ngày 1 đến ngày cuối tháng).
    Sheet đơn vị (Hội Sở trước, rồi các PGD) gộp CSP + Visa + TK mở chưa có thẻ (DPDA19, tùy chọn);
    sheet cuối: thẻ miễn phí CSP toàn chi nhánh.
    """
    try:
        csp_file = request.FILES.get('data_file')
        visa_file = request.FILES.get('visa_file')
        dpda19_file = request.FILES.get('dpda19_file')
        try:
            year, month = (int(x) for x in request.POST.get('thang', '').split('-'))
        except ValueError:
            messages.warning(request, "Vui lòng chọn tháng báo cáo.")
            return redirect('phat_hanh_the_report')

        if not csp_file:
            messages.warning(request, "Vui lòng tải lên file thẻ CSP.")
            return redirect('phat_hanh_the_report')

        start_dt = pd.Timestamp(year=year, month=month, day=1)
        end_dt = start_dt + pd.offsets.MonthEnd(0)
        start_date_str, end_date_str = start_dt.strftime('%Y-%m-%d'), end_dt.strftime('%Y-%m-%d')
        file_suffix = f"Thang{month:02d}_{year}"
        subtitle = (
            f"Tháng {month} năm {year} - Từ ngày {start_dt.strftime('%d/%m/%Y')} "
            f"đến ngày {end_dt.strftime('%d/%m/%Y')}"
        )

        csp_bytes = csp_file.read()
        atm_pgd_map = _get_atm_pgd_config()

        frames = []
        atm_df, err = _read_atm_normalized(csp_bytes, start_date_str, end_date_str, atm_pgd_map)
        if err:
            messages.warning(request, f"File CSP: {err}")
            return redirect('phat_hanh_the_report')
        if atm_df is not None:
            frames.append(atm_df)

        visa_bytes = visa_file.read() if visa_file else None
        if visa_bytes:
            visa_df, err = _read_visa_normalized(visa_bytes, start_date_str, end_date_str, _get_visa_pgd_config())
            if err:
                messages.warning(request, f"File Visa: {err}")
                return redirect('phat_hanh_the_report')
            if visa_df is not None:
                frames.append(visa_df)

        if dpda19_file:
            # Số TK đã có thẻ: toàn bộ file CSP + Visa (không lọc ngày/GDV)
            card_accounts = _read_accounts(csp_bytes, 'ACCOUNT')
            if visa_bytes:
                card_accounts |= _read_accounts(visa_bytes, 'acctseq')
            no_card_df, err = _read_dpda19_no_card(
                dpda19_file.read(), start_date_str, end_date_str, _get_visa_pgd_config(), card_accounts
            )
            if err:
                messages.warning(request, err)
                return redirect('phat_hanh_the_report')
            frames.append(no_card_df)

        free_df, err = _read_csp_free_cards(csp_bytes, start_date_str, end_date_str, atm_pgd_map)
        if err:
            messages.warning(request, err)
            return redirect('phat_hanh_the_report')

        combined_df = (
            pd.concat(frames, ignore_index=True) if frames
            else pd.DataFrame(columns=_THE_OUTPUT_COLS + ['PGD'])
        )

        # Đồng bộ tên GDV về user IPCAS (GRA...); user không có trong map giữ nguyên
        ipcas_map = _csp_to_ipcas_user_map()
        for df in (combined_df, free_df):
            df['GDV phát hành'] = df['GDV phát hành'].map(
                lambda u: ipcas_map.get(str(u).strip().lower(), u)
            )

        output = io.BytesIO()
        pgd_names = sorted(atm_pgd_map.keys(), key=lambda n: 'hội sở' not in n.lower())
        sort_by = ('GDV phát hành', 'Loại thẻ')
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for pgd_name in pgd_names:
                pgd_df = combined_df[combined_df['PGD'] == pgd_name]
                _write_the_sheet(
                    writer, pgd_name, pgd_df[_THE_OUTPUT_COLS],
                    f"DANH SÁCH THẺ PHÁT HÀNH CỦA {pgd_name.upper()}", subtitle,
                    then_sort_by=sort_by
                )
            _write_the_sheet(
                writer, 'Thẻ miễn phí', free_df,
                "DANH SÁCH THẺ MIỄN PHÍ ĐÃ PHÁT HÀNH CỦA CHI NHÁNH", subtitle, highlight=False,
                then_sort_by=sort_by
            )

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="BaoCao_PhatHanhThe_{file_suffix}.xlsx"'
        return response

    except Exception as e:
        traceback.print_exc()
        messages.error(request, f"Đã xảy ra lỗi: {e}")
        return redirect('phat_hanh_the_report')


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
    except Exception:
        all_users = []

    return render(request, 'templates_app/reports/mail_envelope_tracking.html', {'all_users': all_users})


@login_required
@require_http_methods(["POST"])
def save_mail_envelope(request):
    """Lưu thông tin nhận bì thư"""
    try:
        data = json.loads(request.body)

        MailEnvelopeTracking.objects.create(
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


# Nhãn hiển thị cho từng chỉ tiêu
_TKTL_LABELS = {
    'tong_kh':              'Tổng KH có tài khoản',
    'tk_tiet_kiem':         'Danh sách TK tiết kiệm',
    'kh_tiet_kiem':         'KH gửi tiết kiệm',
    'kh_lanh_lai_dinh_ky':  'KH tiết kiệm lãnh lãi định kỳ',
    'kh_tietkiem_co_tt':    'KH tiết kiệm có TK thanh toán',
    'kh_tra_lai_qua_tk':    'KH trả lãi qua TKTGTT',
    'kh_dinh_ky_qua_tk':    'KH định kỳ trả lãi qua TKTGTT',
    'kh_15_tuoi_co_tk':     'KH trên 15 tuổi có tài khoản',
    'kh_15_tuoi_hoatdong':  'KH trên 15 tuổi có tài khoản đang hoạt động',
    'tk_tt_ca_nhan':        'TK thanh toán - Khách hàng cá nhân',
    'tk_tt_to_chuc':        'TK thanh toán - Khách hàng tổ chức',
    'tk_tt_ca_nhan_hoatdong': 'TK thanh toán đang hoạt động - Khách hàng cá nhân',
    'tk_tt_to_chuc_hoatdong': 'TK thanh toán đang hoạt động - Khách hàng tổ chức',
}

# Chỉ đọc các cột cần thiết để giảm bộ nhớ với file lớn
_RT13_COLS = ['MA_KH', 'TEN_KH', 'SO_TK_TIEN_GUI', 'LOAI_KY_HAN', 'TEN_LOAI_KH', 'MA_CN']
_DPDA08_COLS = ['idxacno', 'custseq', 'custnm', 'termdptp', 'altacctno']


def _store_detail(request, key, df, cols_rename):
    """Lưu DataFrame vào session dưới dạng JSON nén (gzip+base64)."""
    import gzip
    import base64
    df_out = df[list(cols_rename.keys())].rename(columns=cols_rename).copy()
    raw = df_out.to_json(orient='records', force_ascii=False)
    compressed = base64.b64encode(gzip.compress(raw.encode('utf-8'))).decode('ascii')
    request.session[f'tktl_{key}'] = compressed


def _load_detail(request, key):
    """Đọc lại detail từ session, trả về list of dicts hoặc None."""
    import gzip
    import base64
    compressed = request.session.get(f'tktl_{key}')
    if not compressed:
        return None
    raw = gzip.decompress(base64.b64decode(compressed.encode('ascii'))).decode('utf-8')
    return json.loads(raw)


@login_required
def tiet_kiem_tra_lai_view(request):
    """Báo cáo KH tiết kiệm trả lãi qua tài khoản tiền gửi thanh toán"""
    context = {}

    if request.method != 'POST':
        return render(request, 'templates_app/reports/tiet_kiem_tra_lai.html', context)

    tg_file = request.FILES.get('tg_file')
    dp_file = request.FILES.get('dp_file')

    if not tg_file or not dp_file:
        messages.error(request, 'Vui lòng tải lên cả 2 file (RT13 và DPDA08).')
        return render(request, 'templates_app/reports/tiet_kiem_tra_lai.html', context)

    try:
        # RT13 là file .csv; DPDA08 vẫn là Excel như cũ
        df_tg = _read_csv_robust(tg_file, usecols=_RT13_COLS)
        df_dp = _read_excel_safe(dp_file, usecols=_DPDA08_COLS)

        df_dp.columns = df_dp.columns.str.strip()

        # Chuẩn hóa cột RT13 — các cột text có dấu ' ở đầu (marker ép kiểu text khi xuất CSV)
        df_tg['_custno'] = _strip_text_marker(df_tg['MA_KH'])
        df_tg['Customer_Name'] = df_tg['TEN_KH'].astype(str).str.strip()
        df_tg['Account_Number'] = _strip_text_marker(df_tg['SO_TK_TIEN_GUI'])
        df_tg['_cust_name'] = _strip_text_marker(df_tg['TEN_LOAI_KH'])
        df_tg['Tr_Office_Name'] = _strip_text_marker(df_tg['MA_CN'])
        # LOAI_KY_HAN tương đương Month_Term của file TG cũ: > 0 là tiết kiệm (có kỳ hạn), = 0 là TK thanh toán
        df_tg['_month_term'] = pd.to_numeric(
            _strip_text_marker(df_tg['LOAI_KY_HAN']), errors='coerce'
        ).fillna(0)

        # Debug: Hiển thị các giá trị unique của các cột quan trọng
        import logging
        logger = logging.getLogger(__name__)
        logger.info("=== DEBUG RT13 FILE ===")
        logger.info(f"Total rows in RT13: {len(df_tg)}")
        logger.info(f"Unique TEN_LOAI_KH values: {df_tg['_cust_name'].unique()[:20]}")
        logger.info(f"LOAI_KY_HAN = 0 count: {(df_tg['_month_term'] == 0).sum()}")
        logger.info("=====================")

        # Chuẩn hóa cột dp
        df_dp['_termdptp']  = df_dp['termdptp'].astype(str).str.strip()
        df_dp['_custseq']   = df_dp['custseq'].astype(str).str.strip()
        df_dp['_altacctno'] = df_dp['altacctno'].astype(str).str.strip()
        df_dp['_idxacno']   = df_dp['idxacno'].astype(str).str.strip()

        # ── 1. Tổng KH có TK ──────────────────────────────────────────────
        df_tong_kh = df_tg.drop_duplicates('_custno')[['_custno', 'Customer_Name']]
        _store_detail(request, 'tong_kh', df_tong_kh,
                      {'_custno': 'Mã KH', 'Customer_Name': 'Tên KH'})

        # ── 2. TK tiết kiệm: LOAI_KY_HAN > 0 (tương đương Month_Term > 0 của file TG cũ) ───
        is_savings = df_tg['_month_term'] > 0
        df_savings = df_tg[is_savings].copy()
        _store_detail(request, 'tk_tiet_kiem', df_savings,
                      {'_custno': 'Mã KH', 'Customer_Name': 'Tên KH',
                       'Account_Number': 'Số TK', 'Tr_Office_Name': 'Đơn vị'})

        # ── 2b. KH tiết kiệm (unique) ─────────────────────────────────────
        df_kh_tietkiem = df_savings.drop_duplicates('_custno')[['_custno', 'Customer_Name']]
        _store_detail(request, 'kh_tiet_kiem', df_kh_tietkiem,
                      {'_custno': 'Mã KH', 'Customer_Name': 'Tên KH'})

        # ── 2c. KH lãnh lãi định kỳ ───────────────────────────────────────
        df_dinh_ky = df_dp[df_dp['_termdptp'] == 'Trả lãi sau định kỳ']
        df_dk_unique = df_dinh_ky.drop_duplicates('_custseq')[
            ['_idxacno', '_custseq', 'custnm', '_termdptp']
        ]
        _store_detail(request, 'kh_lanh_lai_dinh_ky', df_dk_unique,
                      {'_idxacno': 'Số TK TK', '_custseq': 'Mã KH',
                       'custnm': 'Tên KH', '_termdptp': 'Hình thức'})

        # ── 3. KH tiết kiệm có TK thanh toán ─────────────────────────────
        savings_custnos = set(df_savings['_custno'].unique())
        payment_custnos = set(df_tg[~is_savings]['_custno'].unique())
        both_custnos = savings_custnos & payment_custnos
        df_co_tt = df_kh_tietkiem[df_kh_tietkiem['_custno'].isin(both_custnos)]
        _store_detail(request, 'kh_tietkiem_co_tt', df_co_tt,
                      {'_custno': 'Mã KH', 'Customer_Name': 'Tên KH'})

        # ── 4. KH trả lãi qua TK thanh toán ──────────────────────────────
        has_altacct = (
            df_dp['_altacctno'].notna() &
            ~df_dp['_altacctno'].isin(['', 'nan', '0'])
        )
        df_qua_tk = df_dp[has_altacct]
        df_qua_tk_unique = df_qua_tk.drop_duplicates('_custseq')[
            ['_idxacno', '_custseq', 'custnm', '_altacctno', '_termdptp']
        ]
        _store_detail(request, 'kh_tra_lai_qua_tk', df_qua_tk_unique,
                      {'_idxacno': 'Số TK TK', '_custseq': 'Mã KH',
                       'custnm': 'Tên KH', '_altacctno': 'TK nhận lãi',
                       '_termdptp': 'Hình thức'})

        # ── 4a. Trong đó: định kỳ qua TK ─────────────────────────────────
        df_dk_qua_tk = df_qua_tk[
            df_qua_tk['_termdptp'].isin(['Thanh toán hàng tháng', 'Trả lãi sau định kỳ'])
        ]
        df_dk_qua_tk_unique = df_dk_qua_tk.drop_duplicates('_custseq')[
            ['_idxacno', '_custseq', 'custnm', '_altacctno', '_termdptp']
        ]
        _store_detail(request, 'kh_dinh_ky_qua_tk', df_dk_qua_tk_unique,
                      {'_idxacno': 'Số TK TK', '_custseq': 'Mã KH',
                       'custnm': 'Tên KH', '_altacctno': 'TK nhận lãi',
                       '_termdptp': 'Hình thức'})

        # ── 5. Tổng số khách hàng trên 15 tuổi có tài khoản ─────────────────
        # Lọc: LOAI_KY_HAN = 0 (TK thanh toán), TEN_LOAI_KH = "Cá nhân"
        # (RT13 không có cột trạng thái TK như acc_st của file TG cũ — xem như mọi dòng
        # trong RT13 đều là TK đang hoạt động, nên không lọc thêm điều kiện trạng thái)
        df_kh_15_tuoi = df_tg[
            (df_tg['_month_term'] == 0) &
            (df_tg['_cust_name'].str.lower() == 'cá nhân')
        ].copy()
        logger.info(f"DEBUG: KH 15+ tuổi có TK - Before dedup: {len(df_kh_15_tuoi)} rows")
        df_kh_15_tuoi_unique = df_kh_15_tuoi.drop_duplicates('_custno')[['_custno', 'Customer_Name']]
        logger.info(f"DEBUG: KH 15+ tuổi có TK - After dedup: {len(df_kh_15_tuoi_unique)} unique customers")
        _store_detail(request, 'kh_15_tuoi_co_tk', df_kh_15_tuoi_unique,
                      {'_custno': 'Mã KH', 'Customer_Name': 'Tên KH'})

        # ── 6. Tổng số khách hàng trên 15 tuổi có tài khoản đang hoạt động ─────
        # RT13 không phân biệt được trạng thái TK — dùng chung kết quả với mục 5
        df_kh_15_tuoi_hoatdong_unique = df_kh_15_tuoi_unique
        _store_detail(request, 'kh_15_tuoi_hoatdong', df_kh_15_tuoi_hoatdong_unique,
                      {'_custno': 'Mã KH', 'Customer_Name': 'Tên KH'})

        # ── 7. Tổng số lượng tài khoản thanh toán ─────────────────────────────
        # Khách hàng cá nhân: LOAI_KY_HAN = 0, TEN_LOAI_KH = "Cá nhân"
        df_tk_tt_ca_nhan = df_tg[
            (df_tg['_month_term'] == 0) &
            (df_tg['_cust_name'].str.lower() == 'cá nhân')
        ].copy()
        logger.info(f"DEBUG: TK thanh toán cá nhân: {len(df_tk_tt_ca_nhan)} accounts")
        _store_detail(request, 'tk_tt_ca_nhan', df_tk_tt_ca_nhan,
                      {'_custno': 'Mã KH', 'Customer_Name': 'Tên KH',
                       'Account_Number': 'Số TK', 'Tr_Office_Name': 'Đơn vị'})

        # Khách hàng tổ chức: LOAI_KY_HAN = 0, bỏ "Cá nhân"/"Hộ gia đình"
        df_tk_tt_to_chuc = df_tg[
            (df_tg['_month_term'] == 0) &
            (~df_tg['_cust_name'].str.lower().isin(['cá nhân', 'hộ gia đình']))
        ].copy()
        logger.info(f"DEBUG: TK thanh toán tổ chức: {len(df_tk_tt_to_chuc)} accounts")
        _store_detail(request, 'tk_tt_to_chuc', df_tk_tt_to_chuc,
                      {'_custno': 'Mã KH', 'Customer_Name': 'Tên KH',
                       'Account_Number': 'Số TK', 'Tr_Office_Name': 'Đơn vị',
                       '_cust_name': 'Loại KH'})

        # ── 8. Tổng số lượng tài khoản thanh toán đang hoạt động ───────────────
        # RT13 không phân biệt được trạng thái TK — dùng chung kết quả với mục 7
        df_tk_tt_ca_nhan_hoatdong = df_tk_tt_ca_nhan
        _store_detail(request, 'tk_tt_ca_nhan_hoatdong', df_tk_tt_ca_nhan_hoatdong,
                      {'_custno': 'Mã KH', 'Customer_Name': 'Tên KH',
                       'Account_Number': 'Số TK', 'Tr_Office_Name': 'Đơn vị'})

        df_tk_tt_to_chuc_hoatdong = df_tk_tt_to_chuc
        _store_detail(request, 'tk_tt_to_chuc_hoatdong', df_tk_tt_to_chuc_hoatdong,
                      {'_custno': 'Mã KH', 'Customer_Name': 'Tên KH',
                       'Account_Number': 'Số TK', 'Tr_Office_Name': 'Đơn vị',
                       '_cust_name': 'Loại KH'})

        context['result'] = {
            'tong_kh':              len(df_tong_kh),
            'tong_tk_tiet_kiem':    len(df_savings),
            'so_kh_tiet_kiem':      len(df_kh_tietkiem),
            'so_kh_lanh_lai_dinh_ky': len(df_dk_unique),
            'so_kh_tietkiem_co_tt': len(df_co_tt),
            'so_kh_tra_lai_qua_tk': len(df_qua_tk_unique),
            'so_kh_dinh_ky_qua_tk': len(df_dk_qua_tk_unique),
            'so_kh_15_tuoi_co_tk': len(df_kh_15_tuoi_unique),
            'so_kh_15_tuoi_hoatdong': len(df_kh_15_tuoi_hoatdong_unique),
            'so_tk_tt_ca_nhan': len(df_tk_tt_ca_nhan),
            'so_tk_tt_to_chuc': len(df_tk_tt_to_chuc),
            'so_tk_tt_ca_nhan_hoatdong': len(df_tk_tt_ca_nhan_hoatdong),
            'so_tk_tt_to_chuc_hoatdong': len(df_tk_tt_to_chuc_hoatdong),
        }

    except Exception as e:
        messages.error(request, f'Lỗi xử lý: {str(e)}')
        import traceback
        traceback.print_exc()

    return render(request, 'templates_app/reports/tiet_kiem_tra_lai.html', context)


@login_required
def tiet_kiem_tra_lai_detail(request, metric_key):
    """AJAX: trả về JSON preview (200 dòng đầu) cho một chỉ tiêu."""
    if metric_key not in _TKTL_LABELS:
        return JsonResponse({'error': 'Chỉ tiêu không hợp lệ.'}, status=400)
    data = _load_detail(request, metric_key)
    if data is None:
        return JsonResponse({'error': 'Chưa có dữ liệu. Vui lòng xử lý lại.'}, status=404)
    return JsonResponse({
        'label': _TKTL_LABELS[metric_key],
        'total': len(data),
        'rows': data[:200],
        'headers': list(data[0].keys()) if data else [],
    })


@login_required
def tiet_kiem_tra_lai_download(request, metric_key):
    """Download Excel cho một chỉ tiêu."""
    if metric_key not in _TKTL_LABELS:
        messages.error(request, 'Chỉ tiêu không hợp lệ.')
        return redirect('tiet_kiem_tra_lai')
    data = _load_detail(request, metric_key)
    if not data:
        messages.error(request, 'Chưa có dữ liệu. Vui lòng xử lý lại.')
        return redirect('tiet_kiem_tra_lai')

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Danh sách', index=False)
        ws = writer.sheets['Danh sách']
        for col in ws.columns:
            max_len = max((len(str(c.value or '')) for c in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 50)
    output.seek(0)

    filename = f'{metric_key}.xlsx'
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


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

        # Đọc file Excel — dùng helper tự xử lý corruption cho .xls cũ
        df = _read_excel_safe(uploaded_file)

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
# Dùng chung cho báo cáo Đóng/Mở TK, Đối chiếu HĐV, đăng ký HĐV/QR
def _find_col(df_cols, candidates):
    """Tìm tên cột trong df theo danh sách ứng viên (case-insensitive, bỏ qua khoảng trắng thừa)."""
    lower_map = {c.strip().lower(): c for c in df_cols}
    for cand in candidates:
        key = cand.strip().lower()
        if key in lower_map:
            return lower_map[key]
    return None

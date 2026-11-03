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
from copy import copy
from datetime import datetime, timedelta


@login_required
def report_hub(request):
    """Trang hub cho các loại báo cáo"""
    return render(request, 'templates_app/reports/report_hub.html')


@login_required
def lai_ton_dong_report_view(request):
    """Giao diện báo cáo Lãi tồn đọng (GLST07) và Lãi dự thu 6 tháng (GLST80)"""
    # Mặc định kỳ báo cáo = ngày cuối tháng trước, kỳ so sánh = ngày cuối tháng trước nữa
    default_report_date = datetime.now().replace(day=1) - timedelta(days=1)
    default_comparison_date = default_report_date.replace(day=1) - timedelta(days=1)
    return render(request, 'templates_app/reports/lai_ton_dong.html', {
        'default_report_date': default_report_date.strftime('%Y-%m-%d'),
        'default_comparison_date': default_comparison_date.strftime('%Y-%m-%d'),
    })


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
            }

        current_file = request.FILES.get('current_file')
        comparison_file = request.FILES.get('comparison_file')
        report_date_str = request.POST.get('report_date', '')
        comparison_date_str = request.POST.get('comparison_date', '')

        if not all([current_file, comparison_file, report_date_str, comparison_date_str]):
            messages.error(request, "Vui lòng tải lên đủ 2 file và chọn ngày của 2 kỳ.")
            return redirect('lai_ton_dong_report')
        report_date = datetime.strptime(report_date_str, '%Y-%m-%d')
        comparison_date = datetime.strptime(comparison_date_str, '%Y-%m-%d')

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

        final_df = merged_df[
            (merged_df['Dư nợ gốc kỳ này'] != 0) |
            (merged_df['Lãi kỳ này'] != 0) |
            (merged_df['Dư nợ gốc kỳ SS'] != 0) |
            (merged_df['Lãi kỳ SS'] != 0)
        ].copy()

        # KHDN lên trước, trong nhóm giữ thứ tự theo LDS (merge outer đã sắp theo LDS)
        name_upper = final_df['Tên khách hàng'].astype(str).str.upper()
        final_df['is_khdn'] = name_upper.apply(lambda n: any(k in n for k in KHDN_NAME_KEYWORDS))
        final_df = final_df.sort_values('is_khdn', ascending=False, kind='stable')

        try:
            workbook = openpyxl.load_workbook('packages/mau_lai_tondong.xlsx')
        except FileNotFoundError:
            return HttpResponse("Không tìm thấy file mẫu. Vui lòng liên hệ quản trị viên.", status=500)
        sheet = workbook.active
        # B5 và G6 trong mẫu là công thức lấy ngày kỳ báo cáo từ K1
        sheet['K1'] = report_date.strftime('%d/%m/%Y')
        sheet['E6'] = f"Kỳ {comparison_date.strftime('%d/%m/%Y')}"

        # Mẫu: dòng 9 = dòng dữ liệu, 10-12 = Cộng KHCN / Cộng KHDN / Cộng
        data_style = _capture_row(sheet, 9, 2, 10)
        total_styles = [_capture_row(sheet, r, 2, 10) for r in (10, 11, 12)]
        sheet.delete_rows(9, 4)

        # KHDN đã được xếp liền nhau ở đầu nên Cộng KHDN/KHCN là SUM theo đoạn dòng của từng nhóm
        row = 9
        ranges = {}
        for is_khdn, label in ((True, 'KHDN'), (False, 'KHCN')):
            first = row
            for rec in final_df[final_df['is_khdn'] == is_khdn].to_dict('records'):
                _write_row(sheet, row, data_style, {
                    2: rec['Mã khách hàng'], 3: rec['Tên khách hàng'], 4: rec['LDS'],
                    5: rec['Dư nợ gốc kỳ SS'], 6: rec['Lãi kỳ SS'],
                    7: rec['Dư nợ gốc kỳ này'], 8: rec['Lãi kỳ này'],
                    9: f'=IF(H{row}>F{row},H{row}-F{row},0)',
                    10: f'=IF(F{row}>H{row},F{row}-H{row},0)',
                })
                row += 1
            ranges[label] = (first, row - 1) if row > first else None

        khcn_row, khdn_row, sum_row = row, row + 1, row + 2
        for r, style in zip((khcn_row, khdn_row, sum_row), total_styles):
            _write_row(sheet, r, style)
        for c in 'EFGHIJ':
            for r, label in ((khcn_row, 'KHCN'), (khdn_row, 'KHDN')):
                rng = ranges[label]
                sheet[f'{c}{r}'] = f'=SUM({c}{rng[0]}:{c}{rng[1]})' if rng else 0
            sheet[f'{c}{sum_row}'] = f'={c}{khcn_row}+{c}{khdn_row}'

        # Xuất file
        output = io.BytesIO()
        workbook.save(output)
        output.seek(0)

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = (
            f'attachment; filename="BaoCao_LaiTonDong_{report_date.strftime("%d%m%Y")}'
            f'_ss_{comparison_date.strftime("%d%m%Y")}.xlsx"'
        )
        return response

    except Exception as e:
        traceback.print_exc()
        messages.error(request, f"Đã xảy ra lỗi: {e}")
        return redirect('lai_ton_dong_report')


# Tên KH chứa các cụm này được xếp vào nhóm KHDN, còn lại là KHCN (file GLST80 không có cột loại KH)
KHDN_NAME_KEYWORDS = ('CONG TY', 'CTY', 'TNHH', 'CTCP', 'DNTN', 'DOANH NGHIEP', 'HTX', 'HOP TAC XA')


def _capture_row(sheet, r, first_col, last_col):
    """Lưu style + giá trị mặc định của 1 dòng mẫu (cột first_col..last_col) và chiều cao dòng"""
    cells = {c: (copy(sheet.cell(r, c)._style), sheet.cell(r, c).value) for c in range(first_col, last_col + 1)}
    return cells, sheet.row_dimensions[r].height


def _write_row(sheet, r, captured, values=None):
    """Ghi 1 dòng theo dòng mẫu đã lưu; values {cột: giá trị} ghi đè giá trị mặc định"""
    cells, height = captured
    for c, (style, default) in cells.items():
        cell = sheet.cell(r, c)
        cell._style = copy(style)
        cell.value = (values or {}).get(c, default)
    sheet.row_dimensions[r].height = height


@login_required
@require_http_methods(["POST"])
def process_lai_du_thu_6_thang_report(request):
    """Báo cáo Lãi dự thu trên 6 tháng (GLST80): lấy các LDS của kỳ hiện tại, so với dư nợ kỳ trước"""
    try:
        current_file = request.FILES.get('ldt_current_file')
        previous_file = request.FILES.get('ldt_previous_file')
        report_date_str = request.POST.get('ldt_report_date', '')

        if not all([current_file, previous_file, report_date_str]):
            messages.error(request, "Vui lòng tải lên đủ 2 file và chọn ngày báo cáo.")
            return redirect('lai_ton_dong_report')
        report_date = datetime.strptime(report_date_str, '%Y-%m-%d')

        cols = ['custseq', 'custnm', 'refno', 'acrbamt', 'bceqa']
        df_cur = _read_excel_safe(current_file, dtype={'custseq': str, 'refno': str})
        df_prev = _read_excel_safe(previous_file, dtype={'custseq': str, 'refno': str})
        missing = [c for c in cols if c not in df_cur.columns or c not in df_prev.columns]
        if missing:
            messages.error(request, f"File thiếu cột: {', '.join(missing)}")
            return redirect('lai_ton_dong_report')

        df_cur = df_cur[cols].dropna(subset=['refno'])
        df_prev = df_prev[['refno', 'acrbamt', 'bceqa']].dropna(subset=['refno'])
        df_prev = df_prev.drop_duplicates('refno').rename(columns={'acrbamt': 'acrbamt_ss', 'bceqa': 'bceqa_ss'})

        # Chỉ giữ LDS có ở kỳ hiện tại; LDS mới phát sinh thì số kỳ trước = 0
        merged = df_cur.merge(df_prev, on='refno', how='left').fillna({'acrbamt_ss': 0, 'bceqa_ss': 0})
        merged['custseq'] = merged['custseq'].str.strip()
        merged = merged.sort_values(['custseq', 'refno'], kind='stable')
        name_upper = merged['custnm'].fillna('').str.upper()
        merged['is_khdn'] = name_upper.apply(lambda n: any(k in n for k in KHDN_NAME_KEYWORDS))

        try:
            workbook = openpyxl.load_workbook('packages/mau_lai_du_thu_6_thang.xlsx')
        except FileNotFoundError:
            return HttpResponse("Không tìm thấy file mẫu. Vui lòng liên hệ quản trị viên.", status=500)
        sheet = workbook.active
        sheet['C6'] = f"KỲ {report_date.strftime('%d-%m-%Y')}"

        # Mẫu: dòng 8 = nhãn KHDN, 9 = nhãn KHCN, 10 = dòng dữ liệu, 11-13 = Cộng KHCN / Cộng KHDN / Cộng
        label_style = _capture_row(sheet, 8, 2, 9)
        data_style = _capture_row(sheet, 10, 2, 9)
        total_styles = [_capture_row(sheet, r, 2, 9) for r in (11, 12, 13)]
        sheet.delete_rows(8, 6)

        row = 8
        ranges = {}
        for is_khdn, label in ((True, 'KHDN'), (False, 'KHCN')):
            _write_row(sheet, row, label_style, {3: label})
            row += 1
            group = merged[merged['is_khdn'] == is_khdn]
            first = row
            for stt, rec in enumerate(group.itertuples(index=False), 1):
                _write_row(sheet, row, data_style, {
                    2: stt, 3: rec.custseq, 4: rec.custnm, 5: rec.refno,
                    6: rec.acrbamt, 7: rec.bceqa, 8: rec.acrbamt_ss, 9: rec.bceqa_ss,
                })
                row += 1
            ranges[label] = (first, row - 1) if row > first else None

        khcn_row, khdn_row, sum_row = row, row + 1, row + 2
        for r, style in zip((khcn_row, khdn_row, sum_row), total_styles):
            _write_row(sheet, r, style)
        for c in 'FGHI':
            for r, label in ((khcn_row, 'KHCN'), (khdn_row, 'KHDN')):
                rng = ranges[label]
                sheet[f'{c}{r}'] = f'=SUM({c}{rng[0]}:{c}{rng[1]})' if rng else 0
            sheet[f'{c}{sum_row}'] = f'={c}{khcn_row}+{c}{khdn_row}'

        output = io.BytesIO()
        workbook.save(output)
        output.seek(0)
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = (
            f'attachment; filename="BaoCao_LaiDuThu6Thang_{report_date.strftime("%d%m%Y")}.xlsx"'
        )
        return response

    except Exception as e:
        traceback.print_exc()
        messages.error(request, f"Đã xảy ra lỗi: {e}")
        return redirect('lai_ton_dong_report')


# ── Helpers đọc file dùng chung cho các báo cáo (report_*_views.py) ──────────

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


# Dùng chung cho báo cáo Đóng/Mở TK, Đối chiếu HĐV, đăng ký HĐV/QR
def _find_col(df_cols, candidates):
    """Tìm tên cột trong df theo danh sách ứng viên (case-insensitive, bỏ qua khoảng trắng thừa)."""
    lower_map = {c.strip().lower(): c for c in df_cols}
    for cand in candidates:
        key = cand.strip().lower()
        if key in lower_map:
            return lower_map[key]
    return None

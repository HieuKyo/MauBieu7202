"""
Báo cáo Phát hành thẻ (ATM, Visa, CSP miễn phí, mở TK chưa phát hành thẻ) và bản in.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import ReportConfiguration
import pandas as pd
import io
import traceback
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from datetime import datetime
from .report_views import _read_excel_safe


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

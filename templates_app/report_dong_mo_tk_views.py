"""
Báo cáo Đóng/Mở tài khoản.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import math
import pandas as pd
import re
import traceback
import unicodedata
from .report_views import _find_col


# ─────────────────────────────────────────────────────────────────────────────
# BÁO CÁO ĐÓNG/MỞ TÀI KHOẢN
# ─────────────────────────────────────────────────────────────────────────────

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


@login_required
def dong_mo_tai_khoan_report_view(request):
    """Giao diện báo cáo Đóng/Mở tài khoản"""
    from .models import DongMoTaiKhoanHistory
    from django.db.models import Sum
    from django.db.models.functions import TruncYear, TruncQuarter

    # Xóa session cũ nếu sai format
    old = request.session.get('dmtk_result')
    if old and 'has_dong_tk_file' not in old:
        del request.session['dmtk_result']

    # Lịch sử theo tháng
    history_monthly = list(
        DongMoTaiKhoanHistory.objects.order_by('-report_month').values(
            'report_month', 'tong_mo', 'ca_nhan_count', 'to_chuc_count',
            'the_mien_phi_count', 'hssv_count',
            'dong_tk_count', 'dong_he_thong_count', 'dong_tai_quay_count',
            'dong_ca_nhan_count', 'dong_to_chuc_count'
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
            dong_ca_nhan_count=Sum('dong_ca_nhan_count'),
            dong_to_chuc_count=Sum('dong_to_chuc_count'),
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
            dong_ca_nhan_count=Sum('dong_ca_nhan_count'),
            dong_to_chuc_count=Sum('dong_to_chuc_count'),
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

                    def _norm_text(s):
                        """Chuẩn hóa text để so sánh: gộp dấu Unicode (NFC), bỏ khoảng trắng thừa, hoa hết.
                        File Excel xuất từ IPCAS có thể lưu tiếng Việt ở dạng NFD (dấu tách rời) khiến
                        so sánh trực tiếp với chuỗi hardcode NFC luôn sai dù nhìn giống hệt nhau."""
                        return unicodedata.normalize('NFC', str(s)).strip().upper()

                    # Lọc thẻ HSSV: CSP_New + MIỄN PHÍ PHT (so sánh không phân biệt hoa/thường,
                    # chuẩn hóa Unicode để tránh lệch do dấu tiếng Việt tách rời)
                    mask_hssv_the = (
                        (df_the[issue_col].apply(_norm_text) == 'CSP_NEW') &
                        (df_the[hasfee_col].apply(_norm_text) == 'MIỄN PHÍ PHT')
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
                        # Chuẩn hóa key join: bỏ khoảng trắng/ký tự lạ, bỏ .0 cuối (Excel đọc thành số thực),
                        # bỏ số 0 ở đầu — vì 2 file có thể lưu số tài khoản khác định dạng
                        # (VD: file này là số "123456", file kia là text "0123456").
                        def _norm_acct(s):
                            s = str(s).strip()
                            if s.endswith('.0'):
                                s = s[:-2]
                            digits = re.sub(r'\D', '', s)
                            if digits:
                                return digits.lstrip('0') or '0'
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
                        if not join_col_the:
                            missing.append("file thẻ thiếu cột số tài khoản")
                        if not join_col_mo:
                            missing.append(f"file mở TK thiếu cột số tài khoản (thử: {', '.join(_POSSIBLE_ACCTNO_COLS)})")
                        join_warning = "Không thể join: " + "; ".join(missing)

            except Exception as e:
                join_warning = f"Lỗi khi xử lý file phát hành thẻ: {e}"

        # ── Xử lý file Đóng tài khoản ─────────────────────────────────────
        dong_tk_count       = 0
        dong_he_thong_count = 0
        dong_tai_quay_count = 0
        dong_tk_records     = []
        dong_col_labels     = []

        # Phân loại theo loại khách hàng
        dong_ca_nhan_count           = 0
        dong_ca_nhan_tu_dong         = 0
        dong_ca_nhan_tai_quay        = 0
        dong_to_chuc_count           = 0
        dong_to_chuc_tu_dong         = 0
        dong_to_chuc_tai_quay        = 0

        if dong_tk_file:
            try:
                df_dong = pd.read_excel(dong_tk_file)
                df_dong.columns = df_dong.columns.str.strip()

                teller_col_dong = _find_col(df_dong.columns, ['tellernm', 'teller', 'teller_name'])
                locdpnm_col_dong = _find_col(df_dong.columns, ['locdpnm', 'loai_sp', 'loai_tk', 'product_name'])

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

                # Phân loại theo loại khách hàng
                if locdpnm_col_dong:
                    df_dong['_locdpnm'] = df_dong[locdpnm_col_dong].astype(str).str.strip()

                    # Lọc khách hàng cá nhân
                    df_dong_ca_nhan = df_dong[df_dong['_locdpnm'].isin(_LOAI_CA_NHAN)].copy()
                    dong_ca_nhan_count = len(df_dong_ca_nhan)

                    if teller_col_dong:
                        dong_ca_nhan_tu_dong = int((df_dong_ca_nhan[teller_col_dong].astype(str).str.strip().str.upper() == '7202DP').sum())
                        dong_ca_nhan_tai_quay = int(df_dong_ca_nhan[teller_col_dong].astype(str).str.strip().str.upper().str.startswith('GRA').sum())

                    # Lọc khách hàng tổ chức
                    df_dong_to_chuc = df_dong[df_dong['_locdpnm'].isin(_LOAI_TO_CHUC)].copy()
                    dong_to_chuc_count = len(df_dong_to_chuc)

                    if teller_col_dong:
                        dong_to_chuc_tu_dong = int((df_dong_to_chuc[teller_col_dong].astype(str).str.strip().str.upper() == '7202DP').sum())
                        dong_to_chuc_tai_quay = int(df_dong_to_chuc[teller_col_dong].astype(str).str.strip().str.upper().str.startswith('GRA').sum())

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
            # Phân loại đóng TK theo loại khách hàng
            'dong_ca_nhan_count': dong_ca_nhan_count,
            'dong_ca_nhan_tu_dong': dong_ca_nhan_tu_dong,
            'dong_ca_nhan_tai_quay': dong_ca_nhan_tai_quay,
            'dong_to_chuc_count': dong_to_chuc_count,
            'dong_to_chuc_tu_dong': dong_to_chuc_tu_dong,
            'dong_to_chuc_tai_quay': dong_to_chuc_tai_quay,
        }

        request.session['dmtk_result'] = _to_json_safe(result)

        # Lưu lịch sử nếu có chọn kỳ báo cáo
        report_month_str = request.POST.get('report_month', '').strip()
        if report_month_str:
            try:
                from .models import DongMoTaiKhoanHistory
                import datetime
                # Input type="month" gửi định dạng "YYYY-MM" (không có ngày), fromisoformat không parse được
                report_month = datetime.datetime.strptime(report_month_str, '%Y-%m').date().replace(day=1)
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
                        'dong_ca_nhan_count': result['dong_ca_nhan_count'],
                        'dong_ca_nhan_tu_dong': result['dong_ca_nhan_tu_dong'],
                        'dong_ca_nhan_tai_quay': result['dong_ca_nhan_tai_quay'],
                        'dong_to_chuc_count': result['dong_to_chuc_count'],
                        'dong_to_chuc_tu_dong': result['dong_to_chuc_tu_dong'],
                        'dong_to_chuc_tai_quay': result['dong_to_chuc_tai_quay'],
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

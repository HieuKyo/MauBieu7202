"""
Báo cáo KH Tiết kiệm trả lãi qua TKTGTT.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
import pandas as pd
import io
import json
from .report_views import _read_csv_robust, _read_excel_safe, _strip_text_marker


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

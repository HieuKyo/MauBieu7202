"""
Phân tích danh mục tín dụng MSIT80 — hoàn toàn offline, không cần internet.
Tất cả tính toán thực hiện cục bộ bằng pandas theo nghiệp vụ AGRIBANK.
"""
import warnings
from datetime import date, datetime

import pandas as pd


REQUIRED_COLS = [
    'custnm', 'ofcnm', 'custseq', 'apprseq', 'apprdt', 'apprmatdt',
    'appramt', 'dsbsseq', 'dsbsdt', 'dsbsmatdt', 'dsbsbal', 'sprd',
    'grpno', 'nxtintschddt', 'nxtrpmtschddt', 'custtpnm',
]

# Cột tùy chọn (có thì dùng, không có thì bỏ qua)
OPTIONAL_COLS = ['udpcd1', 'lprd', 'aqccdfin', 'brcd']


# ---------------------------------------------------------------------------
# Đọc file
# ---------------------------------------------------------------------------

def load_msit80(file_path: str) -> pd.DataFrame:
    """Đọc file XLS/XLSX MSIT80, chuẩn hóa kiểu dữ liệu."""
    warnings.filterwarnings('ignore')
    try:
        df = pd.read_excel(file_path, header=0, engine='xlrd')
    except Exception:
        df = pd.read_excel(file_path, header=0, engine='openpyxl')

    df.columns = [str(c).strip().lower() for c in df.columns]

    # File MSIT80 xuất mặc định: cột custseq chứa mã chi nhánh (brcd),
    # cột brcd chứa mã khách hàng thực sự → hoán đổi lại.
    if 'brcd' in df.columns and 'custseq' in df.columns:
        df = df.rename(columns={'custseq': 'brcd', 'brcd': 'custseq'})

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"File thiếu cột bắt buộc: {missing}")

    date_cols = ['apprdt', 'apprmatdt', 'dsbsdt', 'dsbsmatdt',
                 'nxtintschddt', 'nxtrpmtschddt']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')

    for col in ['dsbsbal', 'appramt', 'sprd', 'lprd', 'pstintamt']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # aqccdfin = Phân loại nợ cuối cùng theo CIC/NHNN (nhóm 1-5) — ưu tiên hơn grpno
    if 'aqccdfin' in df.columns:
        df['grpno'] = pd.to_numeric(df['aqccdfin'], errors='coerce').fillna(1).astype(int)
    else:
        df['grpno'] = pd.to_numeric(df['grpno'], errors='coerce').fillna(1).astype(int)
    # Clamp về 1-5
    df['grpno'] = df['grpno'].clip(lower=1, upper=5)

    # Bỏ các khoản dư nợ = 0 (xử lý rủi ro, không phải khoản vay thực)
    df = df[df['dsbsbal'] > 0].reset_index(drop=True)

    extra_cols = [c for c in df.columns if c not in REQUIRED_COLS]
    return df[REQUIRED_COLS + extra_cols]


# ---------------------------------------------------------------------------
# Helpers tính toán
# ---------------------------------------------------------------------------

def _parse_date(val) -> date | None:
    if val is None or str(val) in ('nan', 'NaT', 'None', ''):
        return None
    try:
        return datetime.strptime(str(val)[:10], '%Y-%m-%d').date()
    except Exception:
        return None


def _days_diff(val, today: date):
    """Số ngày còn lại: dương = chưa đến hạn, âm = quá hạn."""
    d = _parse_date(val)
    return (d - today).days if d else None


def _risk_score(row: dict, today: date, counts_per_kh: dict) -> int:
    """Tính điểm rủi ro cộng dồn theo bảng nghiệp vụ AGRIBANK."""
    score = 0
    ngay_ls  = _days_diff(row.get('nxtintschddt'), today)
    ngay_goc = _days_diff(row.get('nxtrpmtschddt'), today)
    grpno    = int(row.get('grpno') or 1)
    dsbsbal  = float(row.get('dsbsbal') or 0)
    custseq  = str(row.get('custseq', ''))

    if ngay_ls is not None and ngay_ls < 0:
        score += 20
    if ngay_goc is not None and ngay_goc < 0:
        score += 30
    if (ngay_ls is not None and ngay_ls < -30) or (ngay_goc is not None and ngay_goc < -30):
        score += 50
    if (ngay_ls is not None and ngay_ls < -90) or (ngay_goc is not None and ngay_goc < -90):
        score += 100

    if   grpno == 2: score += 20
    elif grpno == 3: score += 50
    elif grpno == 4: score += 80
    elif grpno >= 5: score += 120

    if   dsbsbal > 5_000_000_000: score += 40
    elif dsbsbal > 2_000_000_000: score += 20
    elif dsbsbal > 1_000_000_000: score += 10

    if counts_per_kh.get(custseq, 0) >= 3:
        score += 10

    return score


def _risk_level(score: int) -> str:
    if score == 0:    return 'Xanh'
    if score <= 50:   return 'Vàng'
    if score <= 100:  return 'Cam'
    if score <= 150:  return 'Đỏ'
    return 'Đỏ đậm'


def _trang_thai(row: dict) -> str:
    """Phân loại trạng thái khoản vay."""
    ngay_mon  = row.get('_ngay_mon')
    ngay_hd   = row.get('_ngay_hd')
    ngay_ls   = row.get('_ngay_ls')
    ngay_goc  = row.get('_ngay_goc')
    grpno     = int(row.get('grpno') or 1)

    if grpno >= 3:
        return 'XLRR'
    if ngay_mon is not None and ngay_mon < 0 and ngay_ls is not None and ngay_ls < 0:
        return 'Quá hạn gốc và lãi'
    if ngay_mon is not None and ngay_mon < 0:
        return 'Quá hạn'
    if ngay_hd is not None and ngay_hd < 0:
        return 'HĐ hết hạn'
    if ngay_mon is not None and 0 <= ngay_mon <= 30:
        return 'Đến hạn'
    return 'Bình thường'


def _canh_bao(score: int, grpno: int) -> str:
    """Phân loại mức cảnh báo."""
    if grpno >= 3:
        return 'XLRR'
    level = _risk_level(score)
    return {
        'Xanh':    'Bình thường',
        'Vàng':    'Theo dõi',
        'Cam':     'Cần xử lý',
        'Đỏ':      'Cao',
        'Đỏ đậm':  'Đặc biệt',
    }.get(level, 'Bình thường')


def _compute_nim(sprd: float, ma_goi: str, ftp_map: dict, default_cfg: dict | None) -> float | None:
    """Tính NIM từ lãi suất vay và bảng FTPConfig."""
    cfg = ftp_map.get(str(ma_goi).strip()) or default_cfg
    if not cfg:
        return None
    cach = cfg.get('cach_tinh', 'SPRD-FTP+DIEU_CHINH')
    ftp  = cfg.get('ftp_pct', 5.0)
    bd   = cfg.get('bien_do_pct', 0.0)
    nim_cd = cfg.get('nim_co_dinh_pct', 0.0)
    if cach == 'NIM_CO_DINH':
        return nim_cd
    if cach == 'SPRD-FTP+DIEU_CHINH':
        return round(sprd - ftp + bd, 4)
    if cach == 'SPRD-FTP-DIEU_CHINH':
        return round(sprd - ftp - bd, 4)
    return round(sprd - ftp, 4)


# ---------------------------------------------------------------------------
# Chuyển số sang chữ tiếng Việt (đơn vị tỷ đồng)
# ---------------------------------------------------------------------------

_ONES  = ['', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín']
_TEENS = ['mười', 'mười một', 'mười hai', 'mười ba', 'mười bốn', 'mười lăm',
          'mười sáu', 'mười bảy', 'mười tám', 'mười chín']
_TENS  = ['', '', 'hai mươi', 'ba mươi', 'bốn mươi', 'năm mươi',
          'sáu mươi', 'bảy mươi', 'tám mươi', 'chín mươi']


def _group3(n: int, has_higher: bool = False) -> str:
    if n == 0:
        return ''
    h, r = divmod(n, 100)
    t, u = divmod(r, 10)
    parts = []
    if h:
        parts.append(_ONES[h] + ' trăm')
    if r == 0:
        pass
    elif r < 10:
        parts.append(('lẻ ' if h or has_higher else '') + _ONES[r])
    elif r < 20:
        parts.append(_TEENS[r - 10])
    else:
        unit = '' if u == 0 else (' mốt' if u == 1 else (' lăm' if u == 5 else ' ' + _ONES[u]))
        parts.append(_TENS[t] + unit)
    return ' '.join(parts)


def _so_thanh_chu_ty(so_ty: float) -> str:
    n = int(round(so_ty))
    if n == 0:
        return 'Không tỷ đồng'
    nghin, rem = divmod(n, 1000)
    parts = []
    if nghin:
        parts.append(_group3(nghin) + ' nghìn')
    if rem:
        parts.append(_group3(rem, has_higher=bool(nghin)))
    return ' '.join(p for p in parts if p).capitalize() + ' tỷ đồng'


# ---------------------------------------------------------------------------
# Phân tích chính (offline)
# ---------------------------------------------------------------------------

def analyze_portfolio(df: pd.DataFrame, ftp_configs: list | None = None) -> dict:
    """
    Phân tích danh mục tín dụng hoàn toàn offline bằng pandas.

    ftp_configs: list of dict từ FTPConfig.objects.values() để tính NIM.
    """
    today     = date.today()
    today_str = today.strftime('%d/%m/%Y')

    # Xây dựng FTP map để tra nhanh
    ftp_map: dict = {}
    default_ftp_cfg: dict | None = None
    if ftp_configs:
        for cfg in ftp_configs:
            if cfg.get('is_default'):
                default_ftp_cfg = cfg
            else:
                ftp_map[str(cfg.get('ma_goi', '')).strip()] = cfg
        if default_ftp_cfg is None and ftp_configs:
            default_ftp_cfg = ftp_configs[0]

    records = df.to_dict(orient='records')

    counts_per_kh = {
        str(k): v
        for k, v in df.groupby('custseq').size().to_dict().items()
    }

    # Làm giàu từng record
    enriched = []
    for row in records:
        score     = _risk_score(row, today, counts_per_kh)
        ngay_mon  = _days_diff(row.get('dsbsmatdt'), today)
        ngay_hd   = _days_diff(row.get('apprmatdt'), today)
        ngay_ls   = _days_diff(row.get('nxtintschddt'), today)
        ngay_goc  = _days_diff(row.get('nxtrpmtschddt'), today)
        grpno     = int(row.get('grpno') or 1)
        sprd_val  = float(row.get('sprd') or 0)
        ma_goi    = str(row.get('udpcd1') or '').strip()

        e = {
            **row,
            '_score':    score,
            '_level':    _risk_level(score),
            '_ngay_mon': ngay_mon,
            '_ngay_hd':  ngay_hd,
            '_ngay_ls':  ngay_ls,
            '_ngay_goc': ngay_goc,
        }
        e['_trangthai'] = _trang_thai(e)
        e['_canh_bao']  = _canh_bao(score, grpno)
        e['_nim']       = _compute_nim(sprd_val, ma_goi, ftp_map, default_ftp_cfg)
        enriched.append(e)

    def bal(r):     return float(r.get('dsbsbal') or 0)
    def bal_ty(r):  return bal(r) / 1e9
    def grp(r):     return int(r.get('grpno') or 1)
    def sprd_v(r):  return float(r.get('sprd') or 0)

    total_rows   = len(enriched)
    total_bal    = sum(bal(r) for r in enriched)
    total_bal_ty = total_bal / 1e9

    so_lds = total_rows
    so_kh  = len({str(r.get('custseq', '')).strip() for r in enriched
                  if str(r.get('custseq', '')).strip() not in ('', 'nan', 'None')})
    so_hd  = len({str(r.get('apprseq', '')).strip() for r in enriched
                  if str(r.get('apprseq', '')).strip() not in ('', 'nan', 'None')})

    # Đến hạn: dsbsmatdt trong 30 ngày tới (kể cả đã qua)
    den_han_rows = [r for r in enriched if r['_ngay_mon'] is not None and r['_ngay_mon'] <= 30]
    den_han_cnt  = len(den_han_rows)

    # Quá hạn: nxtrpmtschddt < today HOẶC nxtintschddt < today
    qua_han_rows = [
        r for r in enriched
        if (r['_ngay_goc'] is not None and r['_ngay_goc'] < 0)
        or (r['_ngay_ls'] is not None and r['_ngay_ls'] < 0)
    ]
    qua_han_cnt  = len(qua_han_rows)
    qua_han_bal  = sum(bal_ty(r) for r in qua_han_rows)

    nhom2_rows = [r for r in enriched if grp(r) == 2]
    nhom35_rows = [r for r in enriched if grp(r) >= 3]
    kh_dac_biet_rows = [r for r in enriched if r['_score'] > 150]
    xlrr_rows = [r for r in enriched if grp(r) >= 3]

    # HĐ tín dụng cần theo dõi: apprmatdt trong 30 ngày
    hd_theo_doi = [r for r in enriched if r['_ngay_hd'] is not None and r['_ngay_hd'] <= 30]

    # Lãi suất bình quân gia quyền
    valid_sprd = [(sprd_v(r), bal(r)) for r in enriched if 0 < sprd_v(r) <= 50]
    if valid_sprd:
        w_bal = sum(b for _, b in valid_sprd)
        ls_bq = sum(s * b for s, b in valid_sprd) / w_bal if w_bal else 0
        ls_tv = sorted(s for s, _ in valid_sprd)[len(valid_sprd) // 2]
    else:
        ls_bq = ls_tv = 0.0

    du_no_bq_trieu = (total_bal / 1e6 / total_rows) if total_rows else 0.0

    # ── Phân loại nợ ──
    def nhom_stat(n):
        rows = [r for r in enriched if grp(r) == n]
        return len(rows), sum(bal_ty(r) for r in rows)

    n1_cnt, n1_bal = nhom_stat(1)
    n2_cnt, n2_bal = nhom_stat(2)
    n3_cnt, n3_bal = nhom_stat(3)
    n4_cnt, n4_bal = nhom_stat(4)
    n5_rows        = [r for r in enriched if grp(r) >= 5]
    n5_cnt         = len(n5_rows)
    n5_bal         = sum(bal_ty(r) for r in n5_rows)

    nx_cnt = n3_cnt + n4_cnt + n5_cnt
    nx_bal = n3_bal + n4_bal + n5_bal
    ty_le_nx = (nx_bal / total_bal_ty * 100) if total_bal_ty else 0.0
    ty_le_qh = (qua_han_bal / total_bal_ty * 100) if total_bal_ty else 0.0

    # ── Quá hạn chi tiết (dùng _ngay_mon cho phân loại kỳ hạn) ──
    qh_mon_rows  = [r for r in enriched if r['_ngay_mon'] is not None and r['_ngay_mon'] < 0]
    qh_gt90      = [r for r in qh_mon_rows if r['_ngay_mon'] < -90]
    qh_30_90     = [r for r in qh_mon_rows if -90 <= r['_ngay_mon'] < -30]
    lai_qh       = [r for r in enriched if r['_ngay_ls'] is not None and r['_ngay_ls'] < 0]
    goc_qh       = [r for r in enriched if r['_ngay_goc'] is not None and r['_ngay_goc'] < 0]
    lai_7ngay    = [r for r in enriched if r['_ngay_ls'] is not None and 0 <= r['_ngay_ls'] <= 7]
    sap_30       = [r for r in enriched if r['_ngay_mon'] is not None and 0 <= r['_ngay_mon'] <= 30]

    # ── Hợp đồng ──
    hd_het  = [r for r in enriched if r['_ngay_hd'] is not None and r['_ngay_hd'] < 0]
    hd_10   = [r for r in enriched if r['_ngay_hd'] is not None and 0 <= r['_ngay_hd'] <= 10]
    hd_30   = [r for r in enriched if r['_ngay_hd'] is not None and 0 <= r['_ngay_hd'] <= 30]

    # ── Rủi ro ──
    def level_stat(lvl):
        rows = [r for r in enriched if r['_level'] == lvl]
        return len(rows), sum(bal_ty(r) for r in rows)

    xanh_cnt,  xanh_bal  = level_stat('Xanh')
    vang_cnt,  vang_bal  = level_stat('Vàng')
    cam_cnt,   cam_bal   = level_stat('Cam')
    do_cnt,    do_bal    = level_stat('Đỏ')
    dodam_cnt, dodam_bal = level_stat('Đỏ đậm')

    scores      = [r['_score'] for r in enriched]
    diem_rr_tb  = sum(scores) / len(scores) if scores else 0.0
    diem_rr_max = max(scores) if scores else 0

    # ── Cán bộ tín dụng ──
    cbtd_map: dict = {}
    for r in enriched:
        name = str(r.get('ofcnm') or '').strip() or 'Không xác định'
        if name not in cbtd_map:
            cbtd_map[name] = {'rows': [], 'scores': [], 'sprd_w': [], 'nim_w': []}
        cbtd_map[name]['rows'].append(r)
        cbtd_map[name]['scores'].append(r['_score'])
        if 0 < sprd_v(r) <= 50:
            cbtd_map[name]['sprd_w'].append((sprd_v(r), bal(r)))
        if r['_nim'] is not None and bal(r) > 0:
            cbtd_map[name]['nim_w'].append((r['_nim'], bal(r)))

    can_bo_list = []
    for name, d in sorted(cbtd_map.items(), key=lambda x: -sum(bal(r) for r in x[1]['rows'])):
        rows  = d['rows']
        qh_m  = [r for r in rows if (r['_ngay_goc'] is not None and r['_ngay_goc'] < 0)
                 or (r['_ngay_ls'] is not None and r['_ngay_ls'] < 0)]
        qh_mon = [r for r in rows if r['_ngay_mon'] is not None and r['_ngay_mon'] < 0]
        den_han_cb = [r for r in rows if r['_ngay_mon'] is not None and 0 <= r['_ngay_mon'] <= 30]
        ty_qh = (len(qh_m) / len(rows) * 100) if rows else 0.0
        sw    = d['sprd_w']
        nw    = d['nim_w']
        ls_cb = (sum(s * b for s, b in sw) / sum(b for _, b in sw)) if sw else 0.0
        nim_cb = (sum(n * b for n, b in nw) / sum(b for _, b in nw)) if nw else None
        if ty_qh < 5:     danh_gia = 'Tốt'
        elif ty_qh <= 15: danh_gia = 'Cần chú ý'
        else:             danh_gia = 'Rủi ro cao'

        nhom2_cb  = sum(1 for r in rows if grp(r) == 2)
        nhom35_cb = sum(1 for r in rows if grp(r) >= 3)
        so_kh_cb  = len({str(r.get('custseq', '')).strip() for r in rows
                         if str(r.get('custseq', '')).strip() not in ('', 'nan', 'None')})

        can_bo_list.append({
            'ten_cbtd':               name,
            'so_mon':                 len(rows),
            'so_kh':                  so_kh_cb,
            'du_no_ty':               round(sum(bal_ty(r) for r in rows), 3),
            'den_han':                len(den_han_cb),
            'so_mon_qua_han':         len(qh_m),
            'ty_le_qua_han_phan_tram': round(ty_qh, 2),
            'nhom2':                  nhom2_cb,
            'nhom35':                 nhom35_cb,
            'diem_rr_trung_binh':     round(sum(d['scores']) / len(d['scores']), 1),
            'lai_suat_bq_phan_tram':  round(ls_cb, 2),
            'nim_bq':                 round(nim_cb, 2) if nim_cb is not None else None,
            'danh_gia':               danh_gia,
        })

    # ── Cảnh báo từng CBTD (Tab "Cảnh báo hiện tại") ──
    canh_bao_cbtd = []
    for cb in can_bo_list:
        if cb['so_mon_qua_han'] > 0 or cb['nhom2'] > 0 or cb['nhom35'] > 0:
            parts = []
            if cb['so_mon_qua_han'] > 0:
                parts.append(f"{cb['so_mon_qua_han']} khoản quá hạn")
            if cb['nhom2'] > 0 or cb['nhom35'] > 0:
                parts.append("có nợ nhóm 2-5")
            hd_cb = sum(1 for r in enriched
                        if str(r.get('ofcnm', '')).strip() == cb['ten_cbtd']
                        and r['_ngay_hd'] is not None and 0 <= r['_ngay_hd'] <= 30)
            if hd_cb > 0:
                parts.append(f"{hd_cb} HĐ cần theo dõi")
            if cb['diem_rr_trung_binh'] > 50:
                parts.append(f"điểm rủi ro TB {cb['diem_rr_trung_binh']}")
            canh_bao_cbtd.append({
                'muc':     'CBTD cần chú ý',
                'noi_dung': f"{cb['ten_cbtd']}: {'; '.join(parts)}",
            })

    # ── Cảnh báo khách hàng (top 20) ──
    canh_bao_rows = sorted(
        [r for r in enriched
         if r['_score'] > 100
         or (bal(r) > 0 and ((r['_ngay_goc'] is not None and r['_ngay_goc'] < 0)
                              or (r['_ngay_ls'] is not None and r['_ngay_ls'] < 0)))],
        key=lambda r: -r['_score']
    )[:20]

    canh_bao_list = []
    for r in canh_bao_rows:
        ly_do = []
        if grp(r) >= 3:
            ly_do.append(f"Nhóm nợ {grp(r)}")
        if r['_ngay_goc'] is not None and r['_ngay_goc'] < 0:
            ly_do.append(f"Quá hạn gốc {abs(r['_ngay_goc'])} ngày")
        if r['_ngay_ls'] is not None and r['_ngay_ls'] < 0:
            ly_do.append("Lãi quá hạn")
        canh_bao_list.append({
            'ten_kh':           str(r.get('custnm') or ''),
            'ten_cbtd':         str(r.get('ofcnm') or ''),
            'du_no_ty':         round(bal_ty(r), 3),
            'nhom_no':          grp(r),
            'ngay_con_lai_mon': r['_ngay_mon'] if r['_ngay_mon'] is not None else 0,
            'diem_rui_ro':      r['_score'],
            'muc_rui_ro':       r['_level'],
            'ly_do':            '; '.join(ly_do) or 'Điểm rủi ro cao',
        })

    # ── Hôm nay cần làm gì? ──
    hom_nay = []
    if qua_han_cnt > 0:
        hom_nay.append({
            'muc_do': 'Cao',
            'cong_viec': 'Khoản vay quá hạn cần xử lý',
            'so_luong': qua_han_cnt,
            'huong_xu_ly': 'Lọc Trạng thái = Quá hạn để xử lý',
        })
    if den_han_cnt > 0:
        hom_nay.append({
            'muc_do': 'Trung bình',
            'cong_viec': 'Khoản vay đến hạn cần theo dõi',
            'so_luong': den_han_cnt,
            'huong_xu_ly': 'Kiểm tra lịch trả gốc/lãi',
        })
    if nx_cnt > 0:
        hom_nay.append({
            'muc_do': 'Cao',
            'cong_viec': 'Khoản thuộc Nhóm 3–5',
            'so_luong': nx_cnt,
            'huong_xu_ly': 'Rà soát chất lượng tín dụng',
        })
    if n2_cnt > 0:
        hom_nay.append({
            'muc_do': 'Trung bình',
            'cong_viec': 'Khoản thuộc Nhóm 2',
            'so_luong': n2_cnt,
            'huong_xu_ly': 'Theo dõi khả năng trả nợ',
        })
    if len(hd_theo_doi) > 0:
        hom_nay.append({
            'muc_do': 'Trung bình',
            'cong_viec': 'Hợp đồng tín dụng cần theo dõi',
            'so_luong': len(hd_theo_doi),
            'huong_xu_ly': 'Kiểm tra HĐ sắp/đã hết hạn',
        })
    if len(kh_dac_biet_rows) > 0:
        hom_nay.append({
            'muc_do': 'Cao',
            'cong_viec': 'Khách hàng rủi ro đặc biệt',
            'so_luong': len(kh_dac_biet_rows),
            'huong_xu_ly': 'Lọc Cảnh báo = Đặc biệt để kiểm tra',
        })
    if len(hd_het) > 0:
        hom_nay.append({
            'muc_do': 'Cao',
            'cong_viec': 'Hợp đồng đã hết hạn chưa gia hạn',
            'so_luong': len(hd_het),
            'huong_xu_ly': 'Khẩn trương gia hạn hoặc thu hồi',
        })

    # ── Tổng kết văn bản ──
    van_de = []
    if ty_le_nx > 3:
        van_de.append(f"Tỷ lệ nợ xấu {ty_le_nx:.2f}% vượt ngưỡng 3% — cần xử lý {nx_cnt} món nợ xấu")
    if len(qh_gt90) > 0:
        van_de.append(f"{len(qh_gt90)} món quá hạn trên 90 ngày — nguy cơ chuyển nợ xấu")
    if qua_han_cnt > 0:
        van_de.append(f"{qua_han_cnt} món quá hạn (dư nợ {qua_han_bal:.3f} tỷ, tỷ lệ {ty_le_qh:.2f}%)")
    if len(hd_het) > 0:
        van_de.append(f"{len(hd_het)} hợp đồng đã hết hạn chưa được gia hạn")
    if len(sap_30) > 0:
        van_de.append(
            f"{len(sap_30)} món sắp đáo hạn trong 30 ngày "
            f"(dư nợ {sum(bal_ty(r) for r in sap_30):.3f} tỷ)"
        )
    if dodam_cnt > 0:
        van_de.append(f"{dodam_cnt} món có điểm rủi ro Đỏ đậm (>150 điểm)")
    if not van_de:
        van_de.append("Danh mục ổn định, không phát sinh vấn đề nghiêm trọng")

    khuyen_nghi = []
    if qh_gt90:
        khuyen_nghi.append("Rà soát và đôn đốc thu hồi ngay các khoản quá hạn trên 90 ngày")
    if hd_het:
        khuyen_nghi.append("Khẩn trương gia hạn hoặc thu hồi các hợp đồng đã hết hạn")
    if sap_30:
        khuyen_nghi.append(
            "Liên hệ khách hàng có món vay đáo hạn trong 30 ngày để chuẩn bị phương án trả nợ"
        )
    if ty_le_nx > 3:
        khuyen_nghi.append("Tăng cường kiểm soát chất lượng tín dụng, xem xét trích lập dự phòng rủi ro")
    if not khuyen_nghi:
        khuyen_nghi.append(
            "Tiếp tục duy trì chất lượng danh mục, theo dõi định kỳ các khoản vay gần đáo hạn"
        )

    nhan_xet = (
        f"Tính đến ngày {today_str}, danh mục tín dụng gồm {so_lds} món vay "
        f"với tổng dư nợ {total_bal_ty:.3f} tỷ đồng, "
        f"lãi suất bình quân {ls_bq:.2f}%/năm. "
    )
    if ty_le_nx > 0:
        nhan_xet += f"Tỷ lệ nợ xấu {ty_le_nx:.2f}% ({nx_cnt} món). "
    if qua_han_cnt > 0:
        nhan_xet += f"Có {qua_han_cnt} món quá hạn, tỷ lệ {ty_le_qh:.2f}%. "
    if dodam_cnt > 0:
        nhan_xet += f"Đặc biệt lưu ý {dodam_cnt} món có điểm rủi ro rất cao."

    # ── Records rút gọn (cho bảng chi tiết + bộ lọc) ──
    records_condensed = []
    for r in enriched:
        records_condensed.append({
            'custnm':        str(r.get('custnm') or ''),
            'ofcnm':         str(r.get('ofcnm') or '').strip(),
            'custseq':       str(r.get('custseq') or ''),
            'custtpnm':      str(r.get('custtpnm') or ''),
            'dsbsseq':       str(r.get('dsbsseq') or ''),
            'apprseq':       str(r.get('apprseq') or ''),
            'dsbsbal':       round(bal(r), 0),
            'sprd':          round(sprd_v(r), 2),
            'grpno':         grp(r),
            'dsbsdt':        str(r.get('dsbsdt') or ''),
            'dsbsmatdt':     str(r.get('dsbsmatdt') or ''),
            'apprmatdt':     str(r.get('apprmatdt') or ''),
            'nxtintschddt':  str(r.get('nxtintschddt') or ''),
            'nxtrpmtschddt': str(r.get('nxtrpmtschddt') or ''),
            'udpcd1':        str(r.get('udpcd1') or ''),
            '_score':        r['_score'],
            '_level':        r['_level'],
            '_trangthai':    r['_trangthai'],
            '_canh_bao':     r['_canh_bao'],
            '_ngay_mon':     r['_ngay_mon'],
            '_ngay_hd':      r['_ngay_hd'],
            '_ngay_ls':      r['_ngay_ls'],
            '_ngay_goc':     r['_ngay_goc'],
            '_nim':          r['_nim'],
        })

    # Danh sách CBTD và gói ưu đãi (cho dropdown)
    cbtd_list  = sorted({str(r.get('ofcnm') or '') for r in enriched if r.get('ofcnm')})
    goi_list   = sorted({str(r.get('udpcd1') or '') for r in enriched if r.get('udpcd1')})

    return {
        'kpi': {
            'tong_du_no':        int(total_bal),
            'tong_du_no_ty':     round(total_bal_ty, 3),
            'tong_du_no_chu':    _so_thanh_chu_ty(total_bal_ty),
            'so_lds':            so_lds,
            'so_kh':             so_kh,
            'so_hd':             so_hd,
            'den_han':           den_han_cnt,
            'qua_han':           qua_han_cnt,
            'du_no_qua_han_ty':  round(qua_han_bal, 3),
            'ty_le_qua_han':     round(ty_le_qh, 2),
            'nhom2':             n2_cnt,
            'nhom35':            nx_cnt,
            'kh_dac_biet':       len(kh_dac_biet_rows),
            'xlrr':              len(xlrr_rows),
            'hd_theo_doi':       len(hd_theo_doi),
        },
        'phan_tich_danh_muc': {
            'ngay_phan_tich':              today_str,
            'tong_du_no_ty':               round(total_bal_ty, 3),
            'tong_du_no_chu':              _so_thanh_chu_ty(total_bal_ty),
            'so_mon_vay':                  so_lds,
            'so_khach_hang':               so_kh,
            'du_no_bq_trieu':              round(du_no_bq_trieu, 1),
            'lai_suat_bq_phan_tram':       round(ls_bq, 2),
            'lai_suat_trung_vi_phan_tram': round(ls_tv, 2),
        },
        'phan_loai_no': {
            'nhom1_so_mon': n1_cnt, 'nhom1_du_no_ty': round(n1_bal, 3),
            'nhom2_so_mon': n2_cnt, 'nhom2_du_no_ty': round(n2_bal, 3),
            'nhom3_so_mon': n3_cnt, 'nhom3_du_no_ty': round(n3_bal, 3),
            'nhom4_so_mon': n4_cnt, 'nhom4_du_no_ty': round(n4_bal, 3),
            'nhom5_so_mon': n5_cnt, 'nhom5_du_no_ty': round(n5_bal, 3),
            'no_xau_so_mon': nx_cnt, 'no_xau_du_no_ty': round(nx_bal, 3),
            'ty_le_no_xau_phan_tram': round(ty_le_nx, 2),
        },
        'qua_han': {
            'mon_qua_han_so_luong':       qua_han_cnt,
            'mon_qua_han_du_no_ty':       round(qua_han_bal, 3),
            'ty_le_qua_han_phan_tram':    round(ty_le_qh, 2),
            'qua_han_gt90_so_mon':        len(qh_gt90),
            'qua_han_gt90_du_no_ty':      round(sum(bal_ty(r) for r in qh_gt90), 3),
            'qua_han_30_90_so_mon':       len(qh_30_90),
            'qua_han_30_90_du_no_ty':     round(sum(bal_ty(r) for r in qh_30_90), 3),
            'lai_qua_han_so_mon':         len(lai_qh),
            'goc_qua_han_so_mon':         len(goc_qh),
            'lai_den_han_7_ngay_so_mon':  len(lai_7ngay),
            'lai_den_han_7_ngay_du_no_ty': round(sum(bal_ty(r) for r in lai_7ngay), 3),
            'sap_dao_han_30_so_mon':      len(sap_30),
            'sap_dao_han_30_du_no_ty':    round(sum(bal_ty(r) for r in sap_30), 3),
        },
        'hop_dong': {
            'hd_het_han_so_luong':    len(hd_het),
            'hd_sap_het_10_so_luong': len(hd_10),
            'hd_sap_het_30_so_luong': len(hd_30),
        },
        'rui_ro': {
            'diem_rr_trung_binh':   round(diem_rr_tb, 1),
            'diem_rr_cao_nhat':     diem_rr_max,
            'muc_xanh_so_mon':  xanh_cnt,  'muc_xanh_du_no_ty':  round(xanh_bal, 3),
            'muc_vang_so_mon':  vang_cnt,  'muc_vang_du_no_ty':  round(vang_bal, 3),
            'muc_cam_so_mon':   cam_cnt,   'muc_cam_du_no_ty':   round(cam_bal, 3),
            'muc_do_so_mon':    do_cnt,    'muc_do_du_no_ty':    round(do_bal, 3),
            'muc_do_dam_so_mon': dodam_cnt, 'muc_do_dam_du_no_ty': round(dodam_bal, 3),
        },
        'can_bo_tin_dung':      can_bo_list,
        'canh_bao_cbtd':        canh_bao_cbtd,
        'canh_bao_khach_hang':  canh_bao_list,
        'hom_nay':              hom_nay,
        'tong_ket_van_ban': {
            'nhan_xet_tong_the':  nhan_xet.strip(),
            'cac_van_de_uu_tien': van_de,
            'khuyen_nghi':        khuyen_nghi,
        },
        'records':    records_condensed,
        'cbtd_list':  cbtd_list,
        'goi_list':   goi_list,
    }


# ---------------------------------------------------------------------------
# So sánh với snapshot kỳ trước
# ---------------------------------------------------------------------------

def compute_so_sanh(current_kpi: dict, prev_snapshot: dict | None) -> dict:
    """Tính delta KPI so với kỳ trước."""
    if not prev_snapshot:
        return {}
    prev = prev_snapshot
    keys = ['tong_du_no_ty', 'so_lds', 'so_kh', 'so_hd',
            'qua_han', 'nhom2', 'nhom35', 'kh_dac_biet']
    result = {}
    for k in keys:
        cur_val = current_kpi.get(k, 0)
        pre_val = prev.get(k, 0)
        delta   = cur_val - pre_val if (isinstance(cur_val, (int, float)) and isinstance(pre_val, (int, float))) else None
        result[k] = {'cur': cur_val, 'pre': pre_val, 'delta': delta}
    return result


# ---------------------------------------------------------------------------
# Chuyển kết quả sang biến Jinja2 cho mẫu biểu Word
# ---------------------------------------------------------------------------

def analysis_to_template_vars(analysis: dict) -> dict:
    """Chuyển JSON phân tích → dict biến Jinja2 cho JinjaWordTemplateProcessor."""
    dm = analysis.get('phan_tich_danh_muc', {})
    no = analysis.get('phan_loai_no', {})
    qh = analysis.get('qua_han', {})
    hd = analysis.get('hop_dong', {})
    rr = analysis.get('rui_ro', {})
    tk = analysis.get('tong_ket_van_ban', {})
    kpi = analysis.get('kpi', {})

    def fmt(v, dec=3):
        try:
            return f"{float(v):,.{dec}f}"
        except Exception:
            return str(v)

    return {
        'td_ngay_phan_tich':         dm.get('ngay_phan_tich', ''),
        'td_tong_du_no_ty':          fmt(dm.get('tong_du_no_ty', 0)),
        'td_tong_du_no_chu':         dm.get('tong_du_no_chu', ''),
        'td_so_mon_vay':             str(dm.get('so_mon_vay', 0)),
        'td_so_khach_hang':          str(dm.get('so_khach_hang', 0)),
        'td_so_hd_tin_dung':         str(kpi.get('so_hd', 0)),
        'td_du_no_bq_trieu':         fmt(dm.get('du_no_bq_trieu', 0), 1),
        'td_lai_suat_bq':            fmt(dm.get('lai_suat_bq_phan_tram', 0), 2),
        'td_lai_suat_trung_vi':      fmt(dm.get('lai_suat_trung_vi_phan_tram', 0), 2),
        'td_nhom1_so_mon':           str(no.get('nhom1_so_mon', 0)),
        'td_nhom1_du_no':            fmt(no.get('nhom1_du_no_ty', 0)),
        'td_nhom2_so_mon':           str(no.get('nhom2_so_mon', 0)),
        'td_nhom2_du_no':            fmt(no.get('nhom2_du_no_ty', 0)),
        'td_nhom3_so_mon':           str(no.get('nhom3_so_mon', 0)),
        'td_nhom3_du_no':            fmt(no.get('nhom3_du_no_ty', 0)),
        'td_nhom4_so_mon':           str(no.get('nhom4_so_mon', 0)),
        'td_nhom4_du_no':            fmt(no.get('nhom4_du_no_ty', 0)),
        'td_nhom5_so_mon':           str(no.get('nhom5_so_mon', 0)),
        'td_nhom5_du_no':            fmt(no.get('nhom5_du_no_ty', 0)),
        'td_no_xau_so_mon':          str(no.get('no_xau_so_mon', 0)),
        'td_no_xau_du_no':           fmt(no.get('no_xau_du_no_ty', 0)),
        'td_ty_le_no_xau':           fmt(no.get('ty_le_no_xau_phan_tram', 0), 2),
        'td_mon_qua_han':            str(qh.get('mon_qua_han_so_luong', 0)),
        'td_mon_qua_han_du_no':      fmt(qh.get('mon_qua_han_du_no_ty', 0)),
        'td_ty_le_qua_han':          fmt(qh.get('ty_le_qua_han_phan_tram', 0), 2),
        'td_qua_han_gt90':           str(qh.get('qua_han_gt90_so_mon', 0)),
        'td_qua_han_gt90_du_no':     fmt(qh.get('qua_han_gt90_du_no_ty', 0)),
        'td_qua_han_30_90':          str(qh.get('qua_han_30_90_so_mon', 0)),
        'td_lai_qua_han':            str(qh.get('lai_qua_han_so_mon', 0)),
        'td_goc_qua_han':            str(qh.get('goc_qua_han_so_mon', 0)),
        'td_sap_dao_han_30':         str(qh.get('sap_dao_han_30_so_mon', 0)),
        'td_sap_dao_han_30_du_no':   fmt(qh.get('sap_dao_han_30_du_no_ty', 0)),
        'td_hd_het_han':             str(hd.get('hd_het_han_so_luong', 0)),
        'td_hd_sap_het_10':          str(hd.get('hd_sap_het_10_so_luong', 0)),
        'td_hd_sap_het_30':          str(hd.get('hd_sap_het_30_so_luong', 0)),
        'td_diem_rr_tb':             fmt(rr.get('diem_rr_trung_binh', 0), 1),
        'td_diem_rr_cao_nhat':       str(rr.get('diem_rr_cao_nhat', 0)),
        'td_muc_xanh':               str(rr.get('muc_xanh_so_mon', 0)),
        'td_muc_xanh_du_no':         fmt(rr.get('muc_xanh_du_no_ty', 0)),
        'td_muc_vang':               str(rr.get('muc_vang_so_mon', 0)),
        'td_muc_vang_du_no':         fmt(rr.get('muc_vang_du_no_ty', 0)),
        'td_muc_cam':                str(rr.get('muc_cam_so_mon', 0)),
        'td_muc_cam_du_no':          fmt(rr.get('muc_cam_du_no_ty', 0)),
        'td_muc_do':                 str(rr.get('muc_do_so_mon', 0)),
        'td_muc_do_du_no':           fmt(rr.get('muc_do_du_no_ty', 0)),
        'td_muc_do_dam':             str(rr.get('muc_do_dam_so_mon', 0)),
        'td_muc_do_dam_du_no':       fmt(rr.get('muc_do_dam_du_no_ty', 0)),
        'td_nhan_xet_tong_the':      tk.get('nhan_xet_tong_the', ''),
        'td_van_de_uu_tien':         '\n'.join(f'- {v}' for v in tk.get('cac_van_de_uu_tien', [])),
        'td_khuyen_nghi':            '\n'.join(f'- {v}' for v in tk.get('khuyen_nghi', [])),
        'td_bang_cbtd':              _format_cbtd_table(analysis.get('can_bo_tin_dung', [])),
        'td_canh_bao_kh':            _format_canh_bao(analysis.get('canh_bao_khach_hang', [])),
    }


def _format_cbtd_table(cbtd_list: list) -> str:
    lines = [
        'STT | Cán bộ TD           | Dư nợ (tỷ) | Món | QH | Tỷ lệ QH | Điểm RR | LS BQ  | Đánh giá',
        '-' * 95,
    ]
    for i, cb in enumerate(cbtd_list, 1):
        lines.append(
            f"{i:2}. {cb.get('ten_cbtd', ''):20} | {cb.get('du_no_ty', 0):10.3f} | "
            f"{cb.get('so_mon', 0):3} | {cb.get('so_mon_qua_han', 0):2} | "
            f"{cb.get('ty_le_qua_han_phan_tram', 0):7.1f}% | "
            f"{cb.get('diem_rr_trung_binh', 0):7.1f} | "
            f"{cb.get('lai_suat_bq_phan_tram', 0):5.2f}% | {cb.get('danh_gia', '')}"
        )
    return '\n'.join(lines)


def _format_canh_bao(kh_list: list) -> str:
    lines = [
        'STT | Khách hàng                  | CBTD               | Dư nợ (tỷ) | Nhóm | Điểm RR | Lý do',
        '-' * 105,
    ]
    for i, kh in enumerate(kh_list, 1):
        lines.append(
            f"{i:2}. {kh.get('ten_kh', ''):28} | {kh.get('ten_cbtd', ''):18} | "
            f"{kh.get('du_no_ty', 0):10.3f} | N{kh.get('nhom_no', 1)}    | "
            f"{kh.get('diem_rui_ro', 0):7} | {kh.get('ly_do', '')}"
        )
    return '\n'.join(lines)

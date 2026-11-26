"""
Tính toán Bảng kê thanh toán công tác phí + Giấy đi đường cho Ban quản lý ATM.
Chỉ áp dụng cho 2 máy ATM04 (PGD Láng Tròn) và ATM06 (Chi cục Thuế Giá Rai).
"""
from datetime import date, timedelta

from .models import ATMReplenishment, ATMManagementBoard, VehicleDutySchedule

ATM_TRIP_CONFIG = {
    '7202ATM04': {'label': 'PGD Láng Tròn', 'destination': 'Máy ATM04 (PGD Láng Tròn)', 'unit_price': 50000, 'priority': 1},
    '7202ATM06': {'label': 'Chi cục Thuế Giá Rai', 'destination': 'Máy ATM06 ( Chi cục thuế )', 'unit_price': 30000, 'priority': 2},
}

BOARD_POSITIONS = ['team_leader', 'treasury_head', 'atm_officer']

MAX_TRIPS_PER_SHEET = 6


def get_counted_trips(start_date, end_date):
    """
    Trả về list ATMReplenishment trong khoảng ngày, chỉ cho ATM04/ATM06.
    Nếu 1 ngày có cả 2 máy, chỉ giữ ATM04 (ưu tiên cao hơn = xa hơn).
    """
    replenishments = list(
        ATMReplenishment.objects.filter(
            atm_id__in=ATM_TRIP_CONFIG.keys(),
            replenishment_date__range=(start_date, end_date),
        ).select_related('atm', 'driver', 'vehicle').order_by('replenishment_date', 'atm_id')
    )

    by_date = {}
    for r in replenishments:
        by_date.setdefault(r.replenishment_date, []).append(r)

    counted = []
    for day, items in by_date.items():
        machines_today = {r.atm_id for r in items}
        if len(machines_today) > 1:
            keep_machine = min(machines_today, key=lambda mid: ATM_TRIP_CONFIG[mid]['priority'])
            items = [r for r in items if r.atm_id == keep_machine]
        counted.extend(items)

    counted.sort(key=lambda r: (r.replenishment_date, r.atm_id))
    return counted


def _covers(record, on_date):
    """Bản ghi có khoảng hiệu lực (ít nhất 1 đầu) chứa on_date."""
    if not (record.effective_from or record.effective_to):
        return False
    if record.effective_from and record.effective_from > on_date:
        return False
    if record.effective_to and record.effective_to < on_date:
        return False
    return True


def _pick_holder(records, on_date):
    for record in records:
        if _covers(record, on_date):
            return record
    # Fallback: không có bản ghi nào có khoảng ngày khớp -> dùng bản ghi is_active
    return next((r for r in records if r.is_active), None)


def get_position_holder(position, on_date):
    """Tra người giữ vị trí `position` tại ngày `on_date`."""
    return _pick_holder(list(ATMManagementBoard.objects.filter(position=position)), on_date)


def _board_records():
    return {p: list(ATMManagementBoard.objects.filter(position=p)) for p in BOARD_POSITIONS}


def _days(start_date, end_date):
    d = start_date
    while d <= end_date:
        yield d
        d += timedelta(days=1)


def board_segments(start_date, end_date):
    """
    Chia [start_date, end_date] thành các giai đoạn mà cả Ban (Trưởng ban, Phó ban/TP KTNQ,
    CB phụ trách ATM) không đổi người. Mỗi phần tử: {start, end, holders: [(chức vụ, tên)]}.
    """
    records = _board_records()
    labels = dict(ATMManagementBoard.POSITION_CHOICES)
    segments = []
    for d in _days(start_date, end_date):
        holders = [_pick_holder(records[p], d) for p in BOARD_POSITIONS]
        key = tuple(getattr(h, 'pk', None) for h in holders)
        if segments and segments[-1]['key'] == key:
            segments[-1]['end'] = d
        else:
            segments.append({
                'key': key, 'start': d, 'end': d,
                'holders': [(labels[p], h.full_name if h else '(chưa có)')
                            for p, h in zip(BOARD_POSITIONS, holders)],
            })
    return segments


def _fmt(d):
    return d.strftime('%d/%m/%Y')


def _ranges(days):
    """List ngày tăng dần → list (từ, đến) liên tục."""
    out = []
    for d in days:
        if out and out[-1][1] + timedelta(days=1) == d:
            out[-1][1] = d
        else:
            out.append([d, d])
    return out


def board_warnings(start_date, end_date, rows):
    """Cảnh báo dữ liệu Ban quản lý ATM / số tài khoản trước khi xuất."""
    warnings = []
    labels = dict(ATMManagementBoard.POSITION_CHOICES)
    records = _board_records()
    for position in BOARD_POSITIONS:
        recs, label = records[position], labels[position]
        dated = [r for r in recs if r.effective_from or r.effective_to]
        undated_active = [r for r in recs if not (r.effective_from or r.effective_to) and r.is_active]
        # Chỉ mơ hồ khi còn người khác cùng chức vụ có thể được chọn (đang hoạt động hoặc có ngày hiệu lực)
        if len(dated) + len(undated_active) > 1:
            for r in undated_active:
                warnings.append(f'{label} {r.full_name}: chưa nhập "Hiệu lực từ / đến ngày" — có nhiều người '
                                f'cùng chức vụ nên chương trình không xác định được ai giữ chức vụ vào ngày nào.')
        for i, a in enumerate(dated):
            for b in dated[i + 1:]:
                lo = max(a.effective_from or date.min, b.effective_from or date.min)
                hi = min(a.effective_to or date.max, b.effective_to or date.max)
                if lo <= hi and lo <= end_date and hi >= start_date:
                    warnings.append(f'{label}: nhiệm kỳ của {a.full_name} và {b.full_name} chồng nhau '
                                    f'({_fmt(max(lo, start_date))} – {_fmt(min(hi, end_date))}).')
        if not recs:
            warnings.append(f'Chưa khai báo {label} trong Ban quản lý ATM.')
            continue
        if dated:
            uncovered = [d for d in _days(start_date, end_date) if not any(_covers(r, d) for r in dated)]
            fallback = next((r for r in recs if r.is_active), None)
            for lo, hi in _ranges(uncovered):
                if fallback:
                    warnings.append(f'{label}: {_fmt(lo)} – {_fmt(hi)} không có nhiệm kỳ nào khớp, '
                                    f'đang tạm lấy người "Đang hoạt động" ({fallback.full_name}).')
                else:
                    warnings.append(f'{label}: {_fmt(lo)} – {_fmt(hi)} không có ai giữ chức vụ.')
    for row in rows:
        if row['total'] and not row['account_number']:
            warnings.append(f"{row['position_display']} {row['full_name']}: chưa có số tài khoản (được thanh toán {row['total']:,}đ).")
    return warnings


def _duty_by_date(start_date, end_date):
    """{ngày: id tài xế trực}"""
    return {
        s.date: s.driver_id
        for s in VehicleDutySchedule.objects.filter(date__range=(start_date, end_date))
    }


def get_duty_excluded_trips(start_date, end_date):
    """Chuyến (đã tính) mà tài xế đi chính là tài xế trực ngày đó -> tài xế không được tính tiền."""
    duty = _duty_by_date(start_date, end_date)
    return [t for t in get_counted_trips(start_date, end_date)
            if t.driver_id and duty.get(t.replenishment_date) == t.driver_id]


def _term_ranges_for_position(position, start_date, end_date):
    """
    Trả về list (holder, term_start, term_end) cắt về [start_date, end_date],
    mỗi phần tử ứng với 1 nhiệm kỳ (bản ghi ATMManagementBoard) chồng lấp khoảng thời gian.
    """
    records = ATMManagementBoard.objects.filter(position=position)
    terms = []
    for record in records:
        if not record.effective_from and not record.effective_to:
            # Không có khoảng hiệu lực -> chỉ tính nếu đang đương nhiệm (dữ liệu cũ chưa gán ngày)
            if not record.is_active:
                continue
        rec_start = record.effective_from or start_date
        rec_end = record.effective_to or end_date
        if rec_start > end_date or rec_end < start_date:
            continue
        terms.append((record, max(rec_start, start_date), min(rec_end, end_date)))

    if not terms:
        holder = records.filter(is_active=True).first()
        if holder:
            terms.append((holder, start_date, end_date))

    terms.sort(key=lambda t: t[1])
    return terms


def build_payment_statement_rows(start_date, end_date):
    """
    Trả về (rows, totals) cho Bảng kê thanh toán.
    rows: list dict {full_name, title, account_number, trips_atm04, trips_atm06,
                      amount_atm04, amount_atm06, total}
    """
    trips = get_counted_trips(start_date, end_date)

    rows = []
    totals = {'trips_atm04': 0, 'trips_atm06': 0, 'amount_atm04': 0, 'amount_atm06': 0, 'total': 0}

    for position in BOARD_POSITIONS:
        for holder, term_start, term_end in _term_ranges_for_position(position, start_date, end_date):
            trips_atm04 = 0
            trips_atm06 = 0
            for trip in trips:
                if not (term_start <= trip.replenishment_date <= term_end):
                    continue
                if get_position_holder(position, trip.replenishment_date) != holder:
                    continue
                if trip.atm_id == '7202ATM04':
                    trips_atm04 += 1
                elif trip.atm_id == '7202ATM06':
                    trips_atm06 += 1

            amount_atm04 = trips_atm04 * ATM_TRIP_CONFIG['7202ATM04']['unit_price']
            amount_atm06 = trips_atm06 * ATM_TRIP_CONFIG['7202ATM06']['unit_price']
            row = {
                'position': position,
                'position_display': holder.get_position_display() if holder else '',
                'full_name': holder.full_name if holder else '',
                'title': holder.title if holder else '',
                'account_number': holder.account_number if holder else '',
                'trips_atm04': trips_atm04,
                'trips_atm06': trips_atm06,
                'amount_atm04': amount_atm04,
                'amount_atm06': amount_atm06,
                'total': amount_atm04 + amount_atm06,
                'term_start': term_start,
                'term_end': term_end,
            }
            rows.append(row)

            totals['trips_atm04'] += trips_atm04
            totals['trips_atm06'] += trips_atm06
            totals['amount_atm04'] += amount_atm04
            totals['amount_atm06'] += amount_atm06
            totals['total'] += row['total']

    # Tài xế: chỉ tính tiền cho chuyến mà tài xế đi KHÔNG PHẢI là tài xế trực ngày đó
    # (tài xế trực đã được trả tiền trực rồi, đi tiếp quỹ thêm không cộng dồn)
    duty_by_date = _duty_by_date(start_date, end_date)

    driver_counts = {}
    for trip in trips:
        if not trip.driver:
            continue
        if duty_by_date.get(trip.replenishment_date) == trip.driver_id:
            continue  # tài xế trực hôm đó đi tiếp quỹ -> không tính thêm tiền

        counts = driver_counts.setdefault(trip.driver, {'trips_atm04': 0, 'trips_atm06': 0})
        if trip.atm_id == '7202ATM04':
            counts['trips_atm04'] += 1
        elif trip.atm_id == '7202ATM06':
            counts['trips_atm06'] += 1

    for driver, counts in driver_counts.items():
        amount_atm04 = counts['trips_atm04'] * ATM_TRIP_CONFIG['7202ATM04']['unit_price']
        amount_atm06 = counts['trips_atm06'] * ATM_TRIP_CONFIG['7202ATM06']['unit_price']
        row = {
            'position': 'driver',
            'position_display': 'Tài xế',
            'full_name': driver.full_name,
            'title': 'Tài xế',
            'account_number': driver.account_number,
            'trips_atm04': counts['trips_atm04'],
            'trips_atm06': counts['trips_atm06'],
            'amount_atm04': amount_atm04,
            'amount_atm06': amount_atm06,
            'total': amount_atm04 + amount_atm06,
            'term_start': start_date,
            'term_end': end_date,
        }
        rows.append(row)

        totals['trips_atm04'] += counts['trips_atm04']
        totals['trips_atm06'] += counts['trips_atm06']
        totals['amount_atm04'] += amount_atm04
        totals['amount_atm06'] += amount_atm06
        totals['total'] += row['total']

    return rows, totals


def build_travel_log_groups(start_date, end_date):
    """
    Trả về list "tờ" giấy đi đường, mỗi tờ tối đa MAX_TRIPS_PER_SHEET chuyến,
    gộp chung Ban quản lý ATM + tài xế của các chuyến đó vào 1 tờ.
    Gom nhóm theo (thành viên Ban, machine_id, driver) — đổi bất kỳ thành viên Ban nào
    (Trưởng ban, Phó ban/TP KTNQ, CB phụ trách ATM) hoặc đổi tài xế thì tách tờ riêng:
    mỗi tờ chỉ có 1 người cho mỗi chức vụ.
    Mỗi tờ: {machine_id, machine_label, driver_name, recipients: [{role, name, title}],
             trips: [...], sheet_index, sheet_count}
    """
    trips = get_counted_trips(start_date, end_date)

    # (id người giữ từng chức vụ, machine_id, driver_id) -> list trip
    groups = {}
    for trip in trips:
        board = tuple(
            getattr(get_position_holder(position, trip.replenishment_date), 'pk', None)
            for position in BOARD_POSITIONS
        )
        groups.setdefault((board, trip.atm_id, trip.driver_id), []).append(trip)

    sheets = []
    for (board, machine_id, driver_id), machine_trips in groups.items():
        machine_trips.sort(key=lambda t: t.replenishment_date)
        chunks = [
            machine_trips[i:i + MAX_TRIPS_PER_SHEET]
            for i in range(0, len(machine_trips), MAX_TRIPS_PER_SHEET)
        ]
        for idx, chunk in enumerate(chunks, 1):
            recipients = []
            seen = set()
            for position in BOARD_POSITIONS:
                for trip in chunk:
                    holder = get_position_holder(position, trip.replenishment_date)
                    if holder and (position, holder.full_name) not in seen:
                        seen.add((position, holder.full_name))
                        recipients.append({
                            'role': holder.get_position_display(),
                            'name': holder.full_name,
                            'title': holder.title,
                        })
            driver = chunk[0].driver
            if driver:
                recipients.append({
                    'role': 'Tài xế',
                    'name': driver.full_name,
                    'title': 'Tài xế',
                })

            sheets.append({
                'first_date': chunk[0].replenishment_date,
                'machine_id': machine_id,
                'machine_label': ATM_TRIP_CONFIG[machine_id]['label'],
                'driver_name': driver.full_name if driver else '',
                'recipients': recipients,
                'trips': chunk,
                'sheet_index': idx,
                'sheet_count': len(chunks),
            })

    # Đánh lại số tờ trong từng nhóm (machine, driver) xuyên suốt các nhiệm kỳ để tên file không trùng
    sheets.sort(key=lambda s: (s['machine_id'], s['driver_name'], s['first_date']))
    counters = {}
    for s in sheets:
        key = (s['machine_id'], s['driver_name'])
        counters[key] = counters.get(key, 0) + 1
        s['sheet_index'] = counters[key]
    return sheets

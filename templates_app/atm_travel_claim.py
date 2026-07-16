"""
Tính toán Bảng kê thanh toán công tác phí + Giấy đi đường cho Ban quản lý ATM.
Chỉ áp dụng cho 2 máy ATM04 (PGD Láng Tròn) và ATM06 (Chi cục Thuế Giá Rai).
"""
from .models import ATMReplenishment, ATMManagementBoard

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


def get_position_holder(position, on_date):
    """Tra người giữ vị trí `position` tại ngày `on_date`."""
    qs = ATMManagementBoard.objects.filter(position=position)
    for record in qs:
        if record.effective_from and record.effective_from > on_date:
            continue
        if record.effective_to and record.effective_to < on_date:
            continue
        if record.effective_from or record.effective_to:
            return record
    # Fallback: không có bản ghi nào có khoảng ngày khớp -> dùng bản ghi is_active
    return qs.filter(is_active=True).first()


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

    return rows, totals


def build_travel_log_groups(start_date, end_date):
    """
    Trả về list "tờ" giấy đi đường, mỗi tờ tối đa MAX_TRIPS_PER_SHEET chuyến,
    gộp chung Ban quản lý ATM + tài xế của các chuyến đó vào 1 tờ.
    Gom nhóm theo (machine_id, driver) — đổi tài xế thì tách tờ riêng.
    Mỗi tờ: {machine_id, machine_label, driver_name, recipients: [{role, name, title}],
             trips: [...], sheet_index, sheet_count}
    """
    trips = get_counted_trips(start_date, end_date)

    # (machine_id, driver_id) -> list trip
    groups = {}
    for trip in trips:
        driver_id = trip.driver_id
        groups.setdefault((trip.atm_id, driver_id), []).append(trip)

    sheets = []
    for (machine_id, driver_id), machine_trips in groups.items():
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
                'machine_id': machine_id,
                'machine_label': ATM_TRIP_CONFIG[machine_id]['label'],
                'driver_name': driver.full_name if driver else '',
                'recipients': recipients,
                'trips': chunk,
                'sheet_index': idx,
                'sheet_count': len(chunks),
            })

    sheets.sort(key=lambda s: (s['machine_id'], s['driver_name'], s['sheet_index']))
    return sheets

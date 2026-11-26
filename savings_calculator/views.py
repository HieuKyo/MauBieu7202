import json
from datetime import date

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .models import SavingsProduct, InterestRate


def calculator_view(request):
    """Trang chính: giao diện tính lãi tiết kiệm."""
    products = SavingsProduct.objects.filter(is_active=True)
    return render(request, "savings_calculator/calculator.html", {
        "products": products,
    })


@require_GET
def api_get_rates(request):
    """API: Trả về danh sách lãi suất theo sản phẩm được chọn."""
    product_id = request.GET.get("product_id")
    if not product_id:
        return JsonResponse({"error": "Thiếu product_id"}, status=400)

    rates = InterestRate.objects.filter(
        product_id=product_id, is_active=True
    ).order_by("term_month_min")

    data = [
        {
            "id": r.id,
            "term_month_min": r.term_month_min,
            "term_month_max": r.term_month_max,
            "interest_rate_yearly": r.interest_rate_yearly,
            "description": r.description,
        }
        for r in rates
    ]
    return JsonResponse({"rates": data})


@require_POST
def api_calculate(request):
    """API: Tính toán lãi tiết kiệm chi tiết."""
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Dữ liệu không hợp lệ"}, status=400)

    principal = body.get("principal", 0)
    term_months = body.get("term_months", 0)
    yearly_rate = body.get("yearly_rate", 0)
    deposit_date_str = body.get("deposit_date", "")

    if principal <= 0 or term_months <= 0 or yearly_rate <= 0:
        return JsonResponse(
            {"error": "Số tiền, kỳ hạn và lãi suất phải lớn hơn 0"}, status=400
        )

    # Parse ngày gửi
    try:
        deposit_date = date.fromisoformat(deposit_date_str) if deposit_date_str else date.today()
    except ValueError:
        deposit_date = date.today()

    # Tính lãi: Tiền lãi = Gốc * (Lãi suất %/năm / 100) / 12 * Số tháng
    monthly_rate = yearly_rate / 100 / 12
    total_interest = principal * monthly_rate * term_months

    # Bảng dòng tiền chi tiết theo từng tháng
    cashflow = []
    cumulative_interest = 0
    for month in range(1, term_months + 1):
        month_interest = principal * monthly_rate
        cumulative_interest += month_interest
        cashflow.append({
            "month": month,
            "interest": round(month_interest, 0),
            "cumulative_interest": round(cumulative_interest, 0),
        })

    # Ngày đáo hạn
    maturity_date = deposit_date
    total_months = term_months
    new_year = maturity_date.year + (maturity_date.month - 1 + total_months) // 12
    new_month = (maturity_date.month - 1 + total_months) % 12 + 1
    try:
        maturity_date = maturity_date.replace(year=new_year, month=new_month)
    except ValueError:
        # Xử lý trường hợp ngày không hợp lệ (VD: 31/01 + 1 tháng)
        import calendar
        last_day = calendar.monthrange(new_year, new_month)[1]
        maturity_date = maturity_date.replace(year=new_year, month=new_month, day=last_day)

    result = {
        "principal": principal,
        "term_months": term_months,
        "yearly_rate": yearly_rate,
        "total_interest": round(total_interest, 0),
        "total_receive": round(principal + total_interest, 0),
        "deposit_date": deposit_date.strftime("%d/%m/%Y"),
        "maturity_date": maturity_date.strftime("%d/%m/%Y"),
        "cashflow": cashflow,
    }
    return JsonResponse(result)


def bond_calculator_view(request):
    """Trang tính lãi trái phiếu (lãi suất thả nổi, tái đầu tư lãi vào tiết kiệm 12 tháng)."""
    products = SavingsProduct.objects.filter(is_active=True)
    return render(request, "savings_calculator/bond_calculator.html", {
        "products": products,
    })


def _bond_margin_for_year(year_index):
    """Biên độ áp dụng theo năm: +2.0%/năm cho 5 năm đầu, +2.5%/năm cho các năm tiếp theo."""
    return 2.0 if year_index <= 5 else 2.5


@require_POST
def api_bond_calculate(request):
    """API: Tính lãi trái phiếu lãi suất thả nổi, tái đầu tư lãi hằng năm vào tiết kiệm 12 tháng."""
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Dữ liệu không hợp lệ"}, status=400)

    principal = body.get("principal", 0)
    tax_rate_percent = body.get("tax_rate", 5)
    reinvest_rate_percent = body.get("reinvest_rate", 0)
    start_date_str = body.get("start_date", "")
    reference_rates = body.get("reference_rates", [])

    if principal <= 0 or not reference_rates:
        return JsonResponse(
            {"error": "Số tiền mua trái phiếu và lãi suất tham chiếu từng năm phải hợp lệ"}, status=400
        )

    try:
        start_date = date.fromisoformat(start_date_str) if start_date_str else date.today()
    except ValueError:
        start_date = date.today()

    tax_rate = tax_rate_percent / 100
    reinvest_rate = reinvest_rate_percent / 100

    rows = []
    reinvest_balance = 0.0
    total_gross_interest = 0.0
    total_tax = 0.0

    for year_index, ref_rate in enumerate(reference_rates, start=1):
        margin = _bond_margin_for_year(year_index)
        applied_rate = ref_rate + margin

        gross_interest = principal * applied_rate / 100
        tax = gross_interest * tax_rate
        coupon_net = gross_interest - tax

        reinvest_interest_gross = reinvest_balance * reinvest_rate
        reinvest_interest_tax = reinvest_interest_gross * tax_rate
        reinvest_interest_net = reinvest_interest_gross - reinvest_interest_tax

        net_received = coupon_net + reinvest_interest_net
        reinvest_balance += coupon_net + reinvest_interest_net
        year_end_balance = principal + reinvest_balance

        total_gross_interest += gross_interest
        total_tax += tax

        rows.append({
            "year": year_index,
            "reference_rate": ref_rate,
            "margin": margin,
            "applied_rate": round(applied_rate, 3),
            "gross_interest": round(gross_interest, 0),
            "tax": round(tax, 0),
            "reinvest_interest_net": round(reinvest_interest_net, 0),
            "net_received": round(net_received, 0),
            "year_end_balance": round(year_end_balance, 0),
        })

    term_years = len(reference_rates)
    try:
        maturity_date = start_date.replace(year=start_date.year + term_years)
    except ValueError:
        # 29/02 rơi vào năm không nhuận
        maturity_date = start_date.replace(year=start_date.year + term_years, day=28)

    total_value = principal + reinvest_balance
    total_net_interest = total_value - principal

    result = {
        "principal": principal,
        "tax_rate": tax_rate_percent,
        "reinvest_rate": reinvest_rate_percent,
        "start_date": start_date.strftime("%d/%m/%Y"),
        "maturity_date": maturity_date.strftime("%d/%m/%Y"),
        "rows": rows,
        "total_gross_interest": round(total_gross_interest, 0),
        "total_tax": round(total_tax, 0),
        "total_net_interest": round(total_net_interest, 0),
        "total_value": round(total_value, 0),
    }
    return JsonResponse(result)

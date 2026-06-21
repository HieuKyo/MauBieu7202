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

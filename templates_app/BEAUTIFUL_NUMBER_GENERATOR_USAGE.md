# Hướng dẫn sử dụng Beautiful Number Generator

## Tổng quan

Module `beautiful_number_generator.py` cung cấp các hàm tự động tạo số đẹp cho Agribank Giá Rai theo các tiêu chí:

- **Số lặp** (Repeating): 888888888, 777777
- **Số tiến** (Progressive): 123456789, 112233
- **Số gánh** (Symmetrical): 123454321, 123321
- **Số lặp kép** (Double Repeat): 123123123, 123123
- **Số ngẫu nhiên** (Random): Lấy phí sàn

## Cài đặt & Import

```python
from templates_app import beautiful_number_generator as bng
from templates_app.beautiful_number_services import analyze_account_number
```

## Sử dụng cơ bản

### 1. Tạo số lặp

```python
# Tạo 10 số lặp
lap_numbers = bng.generate_numbers(bng.gen_so_lap, 10)

# Kết quả:
# ['7202000000000', '7202111111111', '7202222222222', ...]
```

### 2. Tạo số tiến

```python
# Tạo 15 số tiến
tien_numbers = bng.generate_numbers(bng.gen_so_tien, 15)

# Kết quả:
# ['7202012345678', '7202123456789', '7202236012345', ...]
```

### 3. Tạo số gánh

```python
# Tạo 20 số gánh
ganh_numbers = bng.generate_numbers(bng.gen_so_ganh, 20)

# Kết quả:
# ['7202123454321', '7202236123321', ...]
```

### 4. Tạo số lặp kép

```python
# Tạo 25 số lặp kép
lap_kep_numbers = bng.generate_numbers(bng.gen_so_lap_kep, 25)

# Kết quả:
# ['7202123123123', '7202236121212', ...]
```

### 5. Tạo số ngẫu nhiên

```python
# Tạo 50 số ngẫu nhiên
random_numbers = bng.generate_numbers(bng.gen_so_ngau_nhien, 50)

# Kết quả:
# ['7202198273645', '7202236198472', ...]
```

## Sử dụng nâng cao

### Tạo tất cả các loại cùng lúc

```python
# Tạo 20 số cho mỗi loại
all_numbers = bng.generate_all_types(20)

print(f"Số lặp: {len(all_numbers['lap'])}")
print(f"Số tiến: {len(all_numbers['tien'])}")
print(f"Số gánh: {len(all_numbers['ganh'])}")
print(f"Số lặp kép: {len(all_numbers['lap_kep'])}")
print(f"Số ngẫu nhiên: {len(all_numbers['ngau_nhien'])}")
```

### Tạo số kèm phân tích phí

```python
# Tạo 10 số lặp kèm phân tích
analyzed_numbers = bng.generate_with_analysis(bng.gen_so_lap, 10)

for item in analyzed_numbers:
    print(f"Số: {item['number']}")
    print(f"Mô tả: {item['analysis']['description']}")
    print(f"Phí: {item['analysis']['fee_min_vat']:,} - {item['analysis']['fee_max_vat']:,} VNĐ")
    print("-" * 60)
```

## Ví dụ sử dụng trong Views

### Ví dụ 1: Hiển thị danh sách số đẹp

```python
# templates_app/views.py
from django.shortcuts import render
from . import beautiful_number_generator as bng
from .beautiful_number_services import analyze_account_number

def beautiful_numbers_view(request):
    # Tạo 50 số gánh
    ganh_numbers = bng.generate_numbers(bng.gen_so_ganh, 50)

    # Phân tích giá cho các số
    analyzed_list = []
    for num in ganh_numbers:
        analysis = analyze_account_number(num)
        analyzed_list.append({
            'number': num,
            'description': analysis['description'],
            'fee_min': analysis['fee_min_vat'],
            'fee_max': analysis['fee_max_vat'],
        })

    return render(request, 'beautiful_numbers.html', {
        'numbers': analyzed_list
    })
```

### Ví dụ 2: Tạo số theo yêu cầu

```python
def generate_numbers_by_type(request, number_type):
    """
    Tạo số theo loại được chọn

    Args:
        number_type: 'lap', 'tien', 'ganh', 'lap_kep', 'ngau_nhien'
    """
    generator_map = {
        'lap': bng.gen_so_lap,
        'tien': bng.gen_so_tien,
        'ganh': bng.gen_so_ganh,
        'lap_kep': bng.gen_so_lap_kep,
        'ngau_nhien': bng.gen_so_ngau_nhien,
    }

    generator = generator_map.get(number_type)
    if not generator:
        return JsonResponse({'error': 'Invalid type'}, status=400)

    # Tạo 100 số
    numbers = bng.generate_numbers(generator, 100)

    return JsonResponse({
        'type': number_type,
        'count': len(numbers),
        'numbers': numbers
    })
```

### Ví dụ 3: Tạo số và lưu vào database

```python
from .models import BeautifulNumber

def seed_beautiful_numbers(request):
    """Tạo và lưu số đẹp vào database"""

    # Tạo tất cả các loại số (50 mỗi loại)
    all_numbers = bng.generate_all_types(50)

    created_count = 0

    for number_type, numbers in all_numbers.items():
        for num in numbers:
            # Phân tích số
            analysis = analyze_account_number(num)

            # Tạo object trong database
            BeautifulNumber.objects.get_or_create(
                account_number=num,
                defaults={
                    'number_type': number_type,
                    'description': analysis['description'],
                    'fee_min': analysis['fee_min_vat'],
                    'fee_max': analysis['fee_max_vat'],
                    'is_special': analysis['is_special'],
                }
            )
            created_count += 1

    return JsonResponse({
        'message': f'Created {created_count} beautiful numbers',
        'success': True
    })
```

## Template Example

```html
<!-- templates/beautiful_numbers.html -->
<div class="beautiful-numbers-list">
    <h2>Danh sách số đẹp</h2>

    <table class="table">
        <thead>
            <tr>
                <th>STT</th>
                <th>Số tài khoản</th>
                <th>Mô tả</th>
                <th>Phí (VNĐ)</th>
            </tr>
        </thead>
        <tbody>
            {% for item in numbers %}
            <tr>
                <td>{{ forloop.counter }}</td>
                <td><strong>{{ item.number }}</strong></td>
                <td>{{ item.description }}</td>
                <td>{{ item.fee_min|intcomma }} - {{ item.fee_max|intcomma }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

## API Reference

### Hàm chính

#### `generate_numbers(generator_func, num_to_gen)`
Tạo số từ generator function.

**Parameters:**
- `generator_func`: Hàm generator (gen_so_lap, gen_so_tien, etc.)
- `num_to_gen`: Số lượng cần tạo

**Returns:** List các số tài khoản

---

#### `gen_so_lap()`
Generator tạo số lặp.

**Yields:** 20 số (10 số 9-chữ-số + 10 số 6-chữ-số)

---

#### `gen_so_tien()`
Generator tạo số tiến.

**Yields:** 15 số tiến

---

#### `gen_so_ganh(num_to_gen=100)`
Generator tạo số gánh/đối xứng.

**Parameters:**
- `num_to_gen`: Số lượng cần tạo (mặc định 100)

**Yields:** Số gánh theo số lượng yêu cầu

---

#### `gen_so_lap_kep(num_to_gen=100)`
Generator tạo số lặp kép.

**Parameters:**
- `num_to_gen`: Số lượng cần tạo (mặc định 100)

**Yields:** Số lặp kép theo số lượng yêu cầu

---

#### `gen_so_ngau_nhien(num_to_gen=100)`
Generator tạo số ngẫu nhiên.

**Parameters:**
- `num_to_gen`: Số lượng cần tạo (mặc định 100)

**Yields:** Số ngẫu nhiên theo số lượng yêu cầu

---

#### `generate_all_types(count_per_type=20)`
Tạo tất cả các loại số cùng lúc.

**Parameters:**
- `count_per_type`: Số lượng mỗi loại (mặc định 20)

**Returns:** Dict chứa tất cả loại số

---

#### `generate_with_analysis(generator_func, num_to_gen, analyzer=None)`
Tạo số và phân tích phí ngay lập tức.

**Parameters:**
- `generator_func`: Hàm generator
- `num_to_gen`: Số lượng cần tạo
- `analyzer`: Hàm phân tích (mặc định dùng analyze_account_number)

**Returns:** List dict chứa số và phân tích

## Tiền tố số tài khoản

- **Số 9 chữ số** (Phí sàn 1.1M): `7202` + 9 số
  - Ví dụ: `7202888888888`

- **Số 6 chữ số** (Phí sàn 550k): `7202236` + 6 số
  - Ví dụ: `7202236888888`

## Lưu ý

1. Các số được tạo ra tuân thủ logic phí V2.5
2. Số ngẫu nhiên 9-chữ-số sẽ **không bắt đầu bằng '236'** để tránh nhầm lẫn với mã 6-số
3. Số gánh và số lặp kép được tạo ngẫu nhiên, có thể chạy nhiều lần để có kết quả khác nhau
4. Hàm `generate_with_analysis` sẽ tự động import `analyze_account_number` nếu không cung cấp analyzer

## Testing

Chạy test để kiểm tra các hàm:

```bash
python test_generator_simple.py
```

## Đóng góp & Báo lỗi

Nếu phát hiện lỗi hoặc có đề xuất cải tiến, vui lòng tạo issue hoặc pull request.

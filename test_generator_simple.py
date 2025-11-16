"""
Script test đơn giản để kiểm tra các hàm tạo số đẹp (không cần Django)
"""

import sys
sys.path.insert(0, '/home/user/MauBieu7202/templates_app')

from beautiful_number_generator import (
    generate_numbers,
    gen_so_lap,
    gen_so_tien,
    gen_so_ganh,
    gen_so_lap_kep,
    gen_so_ngau_nhien,
    generate_all_types
)


def test_so_lap():
    """Test tạo số lặp"""
    print("\n" + "="*60)
    print("TEST SỐ LẶP (REPEATING)")
    print("="*60)

    numbers = generate_numbers(gen_so_lap, 20)
    print(f"Đã tạo {len(numbers)} số lặp")
    print(f"Mẫu 5 số đầu:")
    for i, num in enumerate(numbers[:5], 1):
        print(f"  {i}. {num}")

    # Kiểm tra tính đúng
    assert len(numbers) == 20, f"Phải tạo 20 số, nhưng chỉ có {len(numbers)}"
    assert all(num.startswith('7202') for num in numbers), "Tất cả số phải bắt đầu bằng 7202"
    print("✓ Test passed!")


def test_so_tien():
    """Test tạo số tiến"""
    print("\n" + "="*60)
    print("TEST SỐ TIẾN (PROGRESSIVE)")
    print("="*60)

    numbers = generate_numbers(gen_so_tien, 20)
    print(f"Đã tạo {len(numbers)} số tiến")
    print(f"Mẫu 5 số đầu:")
    for i, num in enumerate(numbers[:5], 1):
        print(f"  {i}. {num}")

    # Kiểm tra
    assert all(num.startswith('7202') for num in numbers), "Tất cả số phải bắt đầu bằng 7202"
    print("✓ Test passed!")


def test_so_ganh():
    """Test tạo số gánh"""
    print("\n" + "="*60)
    print("TEST SỐ GÁNH (SYMMETRICAL)")
    print("="*60)

    numbers = generate_numbers(gen_so_ganh, 20)
    print(f"Đã tạo {len(numbers)} số gánh")
    print(f"Mẫu 5 số đầu:")
    for i, num in enumerate(numbers[:5], 1):
        print(f"  {i}. {num}")

    # Kiểm tra tính đối xứng
    for num in numbers[:3]:
        if num.startswith('7202236'):
            # Số 6 chữ số
            part = num[7:]
            assert part == part[::-1], f"Số {num} không đối xứng"
        else:
            # Số 9 chữ số
            part = num[4:]
            # Kiểm tra cấu trúc abcdXdcba
            assert part[0:4] == part[5:9][::-1], f"Số {num} không đối xứng"

    print("✓ Test passed!")


def test_so_lap_kep():
    """Test tạo số lặp kép"""
    print("\n" + "="*60)
    print("TEST SỐ LẶP KÉP (DOUBLE REPEAT)")
    print("="*60)

    numbers = generate_numbers(gen_so_lap_kep, 20)
    print(f"Đã tạo {len(numbers)} số lặp kép")
    print(f"Mẫu 5 số đầu:")
    for i, num in enumerate(numbers[:5], 1):
        print(f"  {i}. {num}")

    # Kiểm tra
    assert all(num.startswith('7202') for num in numbers), "Tất cả số phải bắt đầu bằng 7202"
    print("✓ Test passed!")


def test_so_ngau_nhien():
    """Test tạo số ngẫu nhiên"""
    print("\n" + "="*60)
    print("TEST SỐ NGẪU NHIÊN (RANDOM)")
    print("="*60)

    numbers = generate_numbers(gen_so_ngau_nhien, 20)
    print(f"Đã tạo {len(numbers)} số ngẫu nhiên")
    print(f"Mẫu 5 số đầu:")
    for i, num in enumerate(numbers[:5], 1):
        print(f"  {i}. {num}")

    # Kiểm tra
    assert all(num.startswith('7202') for num in numbers), "Tất cả số phải bắt đầu bằng 7202"
    print("✓ Test passed!")


def test_generate_all_types():
    """Test tạo tất cả loại"""
    print("\n" + "="*60)
    print("TEST TẠO TẤT CẢ CÁC LOẠI")
    print("="*60)

    all_numbers = generate_all_types(10)

    print(f"\nKết quả:")
    for type_name, numbers in all_numbers.items():
        print(f"  - {type_name}: {len(numbers)} số")

    # Kiểm tra
    assert len(all_numbers) == 5, "Phải có 5 loại số"
    print("✓ Test passed!")


def test_prefix_validation():
    """Test kiểm tra tiền tố"""
    print("\n" + "="*60)
    print("TEST KIỂM TRA TIỀN TỐ")
    print("="*60)

    # Tạo mẫu từ mỗi loại
    all_numbers = []
    all_numbers.extend(generate_numbers(gen_so_lap, 5))
    all_numbers.extend(generate_numbers(gen_so_tien, 5))
    all_numbers.extend(generate_numbers(gen_so_ganh, 5))
    all_numbers.extend(generate_numbers(gen_so_lap_kep, 5))
    all_numbers.extend(generate_numbers(gen_so_ngau_nhien, 5))

    # Kiểm tra độ dài
    count_9_digit = sum(1 for n in all_numbers if not n.startswith('7202236'))
    count_6_digit = sum(1 for n in all_numbers if n.startswith('7202236'))

    print(f"Tổng số: {len(all_numbers)}")
    print(f"  - Loại 9 số (7202XXXXXXXXX): {count_9_digit}")
    print(f"  - Loại 6 số (7202236XXXXXX): {count_6_digit}")

    # Kiểm tra độ dài chính xác
    for num in all_numbers:
        assert len(num) == 13, f"Số {num} không đúng 13 chữ số"

    print("✓ Test passed!")


if __name__ == '__main__':
    print("\n" + "="*70)
    print(" "*15 + "BẮT ĐẦU TEST BEAUTIFUL NUMBER GENERATOR")
    print("="*70)

    try:
        test_so_lap()
        test_so_tien()
        test_so_ganh()
        test_so_lap_kep()
        test_so_ngau_nhien()
        test_generate_all_types()
        test_prefix_validation()

        print("\n" + "="*70)
        print(" "*20 + "✓ HOÀN THÀNH TẤT CẢ TESTS")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

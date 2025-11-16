"""
Script test để kiểm tra các hàm tạo số đẹp
"""

import sys
import os

# Thêm đường dẫn để import Django models
sys.path.insert(0, '/home/user/MauBieu7202')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MauBieu.settings')

import django
django.setup()

from templates_app import beautiful_number_generator as bng
from templates_app.beautiful_number_services import analyze_account_number


def test_so_lap():
    """Test tạo số lặp"""
    print("\n" + "="*60)
    print("TEST SỐ LẶP (REPEATING)")
    print("="*60)

    numbers = bng.generate_numbers(bng.gen_so_lap, 20)
    print(f"Đã tạo {len(numbers)} số lặp")

    for i, num in enumerate(numbers[:5], 1):
        analysis = analyze_account_number(num)
        print(f"\n{i}. {num}")
        print(f"   Mô tả: {analysis['description']}")
        print(f"   Phí: {analysis['fee_min_vat']:,} - {analysis['fee_max_vat']:,} VNĐ")


def test_so_tien():
    """Test tạo số tiến"""
    print("\n" + "="*60)
    print("TEST SỐ TIẾN (PROGRESSIVE)")
    print("="*60)

    numbers = bng.generate_numbers(bng.gen_so_tien, 20)
    print(f"Đã tạo {len(numbers)} số tiến")

    for i, num in enumerate(numbers[:5], 1):
        analysis = analyze_account_number(num)
        print(f"\n{i}. {num}")
        print(f"   Mô tả: {analysis['description']}")
        print(f"   Phí: {analysis['fee_min_vat']:,} - {analysis['fee_max_vat']:,} VNĐ")


def test_so_ganh():
    """Test tạo số gánh"""
    print("\n" + "="*60)
    print("TEST SỐ GÁNH (SYMMETRICAL)")
    print("="*60)

    numbers = bng.generate_numbers(bng.gen_so_ganh, 20)
    print(f"Đã tạo {len(numbers)} số gánh")

    for i, num in enumerate(numbers[:5], 1):
        analysis = analyze_account_number(num)
        print(f"\n{i}. {num}")
        print(f"   Mô tả: {analysis['description']}")
        print(f"   Phí: {analysis['fee_min_vat']:,} - {analysis['fee_max_vat']:,} VNĐ")


def test_so_lap_kep():
    """Test tạo số lặp kép"""
    print("\n" + "="*60)
    print("TEST SỐ LẶP KÉP (DOUBLE REPEAT)")
    print("="*60)

    numbers = bng.generate_numbers(bng.gen_so_lap_kep, 20)
    print(f"Đã tạo {len(numbers)} số lặp kép")

    for i, num in enumerate(numbers[:5], 1):
        analysis = analyze_account_number(num)
        print(f"\n{i}. {num}")
        print(f"   Mô tả: {analysis['description']}")
        print(f"   Phí: {analysis['fee_min_vat']:,} - {analysis['fee_max_vat']:,} VNĐ")


def test_so_ngau_nhien():
    """Test tạo số ngẫu nhiên"""
    print("\n" + "="*60)
    print("TEST SỐ NGẪU NHIÊN (RANDOM)")
    print("="*60)

    numbers = bng.generate_numbers(bng.gen_so_ngau_nhien, 20)
    print(f"Đã tạo {len(numbers)} số ngẫu nhiên")

    for i, num in enumerate(numbers[:5], 1):
        analysis = analyze_account_number(num)
        print(f"\n{i}. {num}")
        print(f"   Mô tả: {analysis['description']}")
        print(f"   Phí: {analysis['fee_min_vat']:,} - {analysis['fee_max_vat']:,} VNĐ")


def test_generate_all_types():
    """Test tạo tất cả loại"""
    print("\n" + "="*60)
    print("TEST TẠO TẤT CẢ CÁC LOẠI")
    print("="*60)

    all_numbers = bng.generate_all_types(10)

    print(f"\nKết quả:")
    for type_name, numbers in all_numbers.items():
        print(f"  - {type_name}: {len(numbers)} số")


def test_generate_with_analysis():
    """Test tạo số kèm phân tích"""
    print("\n" + "="*60)
    print("TEST TẠO SỐ KÈM PHÂN TÍCH")
    print("="*60)

    analyzed = bng.generate_with_analysis(bng.gen_so_lap, 5)

    for item in analyzed:
        print(f"\n{item['number']}")
        print(f"  Mô tả: {item['analysis']['description']}")
        print(f"  Phí: {item['analysis']['fee_min_vat']:,} - {item['analysis']['fee_max_vat']:,} VNĐ")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("BẮT ĐẦU TEST BEAUTIFUL NUMBER GENERATOR")
    print("="*60)

    test_so_lap()
    test_so_tien()
    test_so_ganh()
    test_so_lap_kep()
    test_so_ngau_nhien()
    test_generate_all_types()
    test_generate_with_analysis()

    print("\n" + "="*60)
    print("HOÀN THÀNH TẤT CẢ TESTS")
    print("="*60 + "\n")

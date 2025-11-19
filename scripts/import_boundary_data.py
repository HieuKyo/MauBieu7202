#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script import dữ liệu địa bàn sáp nhập từ file Excel/CSV
Chuyển đổi sang định dạng JSON để tra cứu offline

Cách sử dụng:
1. Tạo file Excel với cấu trúc theo mẫu
2. Chạy: python scripts/import_boundary_data.py <đường_dẫn_file_excel>

Cấu trúc file Excel:
- Sheet "provinces": Mã tỉnh, Tên tỉnh, Số đơn vị mới
- Sheet "changes": Tỉnh, Đơn vị cũ 1, Đơn vị cũ 2, Đơn vị mới, Ngày hiệu lực
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Thêm thư mục gốc vào path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Thư mục lưu dữ liệu
DATA_DIR = BASE_DIR / "data" / "boundary_changes"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def create_sample_excel():
    """Tạo file Excel mẫu để nhập liệu"""
    try:
        import pandas as pd
    except ImportError:
        print("Cần cài đặt pandas: pip install pandas openpyxl")
        return None

    # Dữ liệu mẫu cho provinces
    provinces_data = {
        'Mã tỉnh': ['01', '38', '40', '48'],
        'Tên tỉnh': ['Hà Nội', 'Thanh Hóa', 'Nghệ An', 'Đà Nẵng'],
        'Số đơn vị mới': [126, 156, 143, 45]
    }

    # Dữ liệu mẫu cho changes
    changes_data = {
        'Tỉnh': ['Hà Nội', 'Hà Nội', 'Thanh Hóa'],
        'Đơn vị cũ 1': ['Phường Phú La', 'Xã Đại Mỗ', 'Xã Đông Hòa'],
        'Đơn vị cũ 2': ['Phường Yên Nghĩa', 'Xã Trung Văn', 'Xã Đông Yên'],
        'Đơn vị cũ 3': ['', '', ''],
        'Đơn vị mới': ['Phường Phú Yên', 'Phường Đại Trung', 'Xã Đông Hòa Yên'],
        'Ngày hiệu lực': ['2025-07-01', '2025-07-01', '2025-07-01']
    }

    # Tạo file Excel
    sample_file = DATA_DIR / "mau_nhap_lieu.xlsx"

    with pd.ExcelWriter(sample_file, engine='openpyxl') as writer:
        pd.DataFrame(provinces_data).to_excel(writer, sheet_name='provinces', index=False)
        pd.DataFrame(changes_data).to_excel(writer, sheet_name='changes', index=False)

    print(f"✓ Đã tạo file mẫu: {sample_file}")
    return sample_file


def import_from_excel(excel_path):
    """Import dữ liệu từ file Excel"""
    try:
        import pandas as pd
    except ImportError:
        print("Cần cài đặt pandas: pip install pandas openpyxl")
        return None

    if not os.path.exists(excel_path):
        print(f"❌ Không tìm thấy file: {excel_path}")
        return None

    print(f"Đang đọc file: {excel_path}")

    # Đọc dữ liệu provinces
    try:
        provinces_df = pd.read_excel(excel_path, sheet_name='provinces')
        provinces = []
        for _, row in provinces_df.iterrows():
            provinces.append({
                "code": str(row.get('Mã tỉnh', '')).zfill(2),
                "name": str(row.get('Tên tỉnh', '')),
                "new_wards_count": int(row.get('Số đơn vị mới', 0))
            })
        print(f"✓ Đọc được {len(provinces)} tỉnh/thành")
    except Exception as e:
        print(f"⚠ Lỗi đọc sheet provinces: {e}")
        provinces = []

    # Đọc dữ liệu changes
    try:
        changes_df = pd.read_excel(excel_path, sheet_name='changes')
        changes = []
        for _, row in changes_df.iterrows():
            # Thu thập các đơn vị cũ
            old_units = []
            for i in range(1, 6):  # Hỗ trợ tối đa 5 đơn vị cũ
                col_name = f'Đơn vị cũ {i}' if i > 1 else 'Đơn vị cũ 1'
                if col_name in row and pd.notna(row[col_name]) and str(row[col_name]).strip():
                    old_units.append(str(row[col_name]).strip())

            if old_units and pd.notna(row.get('Đơn vị mới')):
                changes.append({
                    "province": str(row.get('Tỉnh', '')),
                    "type": "merge",
                    "old_units": old_units,
                    "new_unit": str(row.get('Đơn vị mới', '')),
                    "effective_date": str(row.get('Ngày hiệu lực', '2025-07-01'))
                })
        print(f"✓ Đọc được {len(changes)} thay đổi địa bàn")
    except Exception as e:
        print(f"⚠ Lỗi đọc sheet changes: {e}")
        changes = []

    return {
        "provinces": provinces,
        "changes": changes
    }


def import_from_csv(csv_path):
    """Import dữ liệu từ file CSV đơn giản"""
    try:
        import pandas as pd
    except ImportError:
        print("Cần cài đặt pandas: pip install pandas")
        return None

    if not os.path.exists(csv_path):
        print(f"❌ Không tìm thấy file: {csv_path}")
        return None

    print(f"Đang đọc file: {csv_path}")

    df = pd.read_csv(csv_path, encoding='utf-8')
    changes = []

    for _, row in df.iterrows():
        old_units = []
        # Tìm các cột đơn vị cũ
        for col in df.columns:
            if 'cũ' in col.lower() and pd.notna(row[col]) and str(row[col]).strip():
                old_units.append(str(row[col]).strip())

        new_unit_col = [c for c in df.columns if 'mới' in c.lower()]
        if old_units and new_unit_col:
            changes.append({
                "province": str(row.get('Tỉnh', row.get('tỉnh', ''))),
                "type": "merge",
                "old_units": old_units,
                "new_unit": str(row[new_unit_col[0]]),
                "effective_date": str(row.get('Ngày hiệu lực', '2025-07-01'))
            })

    print(f"✓ Đọc được {len(changes)} thay đổi địa bàn")
    return {"provinces": [], "changes": changes}


def merge_with_existing(new_data):
    """Gộp dữ liệu mới với dữ liệu hiện có"""
    json_file = DATA_DIR / "boundary_changes.json"

    # Đọc dữ liệu hiện có
    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)
    else:
        existing = {
            "metadata": {},
            "statistics": {},
            "provinces_with_changes": [],
            "sample_changes": [],
            "data_sources": []
        }

    # Gộp provinces
    existing_codes = {p['code'] for p in existing.get('provinces_with_changes', [])}
    for province in new_data.get('provinces', []):
        if province['code'] not in existing_codes:
            existing['provinces_with_changes'].append(province)
            existing_codes.add(province['code'])

    # Gộp changes
    existing_changes = {
        (c['province'], c['new_unit'])
        for c in existing.get('sample_changes', [])
    }
    for change in new_data.get('changes', []):
        key = (change['province'], change['new_unit'])
        if key not in existing_changes:
            existing['sample_changes'].append(change)
            existing_changes.add(key)

    # Cập nhật metadata
    existing['metadata']['updated_at'] = datetime.now().isoformat()
    existing['statistics']['total_provinces_with_changes'] = len(existing['provinces_with_changes'])

    return existing


def save_data(data):
    """Lưu dữ liệu ra file JSON"""
    json_file = DATA_DIR / "boundary_changes.json"

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Đã lưu dữ liệu vào: {json_file}")
    print(f"  - Số tỉnh/thành: {len(data.get('provinces_with_changes', []))}")
    print(f"  - Số thay đổi: {len(data.get('sample_changes', []))}")


def main():
    print("\n" + "=" * 60)
    print("CÔNG CỤ IMPORT DỮ LIỆU ĐỊA BÀN SÁP NHẬP")
    print("=" * 60 + "\n")

    if len(sys.argv) < 2:
        print("Sử dụng:")
        print("  python import_boundary_data.py <file_excel_hoặc_csv>")
        print("  python import_boundary_data.py --create-sample")
        print("\nVí dụ:")
        print("  python import_boundary_data.py dulieu_sapnhap.xlsx")
        print("  python import_boundary_data.py --create-sample")
        return 1

    if sys.argv[1] == '--create-sample':
        sample_file = create_sample_excel()
        if sample_file:
            print(f"\nBạn có thể mở file và nhập dữ liệu vào, sau đó chạy:")
            print(f"  python import_boundary_data.py {sample_file}")
        return 0

    file_path = sys.argv[1]

    # Import dữ liệu
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        new_data = import_from_excel(file_path)
    elif file_path.endswith('.csv'):
        new_data = import_from_csv(file_path)
    else:
        print("❌ Chỉ hỗ trợ file .xlsx, .xls, .csv")
        return 1

    if not new_data:
        return 1

    # Gộp và lưu
    merged_data = merge_with_existing(new_data)
    save_data(merged_data)

    print("\n" + "=" * 60)
    print("HOÀN THÀNH!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())

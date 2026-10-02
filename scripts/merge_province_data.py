#!/usr/bin/env python3
"""
Script to merge province data into main dia_danh.json and chuyen_doi.json files
"""

import json

# Paths
DIA_DANH_PATH = '/home/user/MauBieu7202/templates_app/static/data/dia_danh.json'
CHUYEN_DOI_PATH = '/home/user/MauBieu7202/templates_app/static/data/chuyen_doi.json'

def merge_data():
    # Load main files
    with open(DIA_DANH_PATH, 'r', encoding='utf-8') as f:
        dia_danh = json.load(f)

    with open(CHUYEN_DOI_PATH, 'r', encoding='utf-8') as f:
        chuyen_doi = json.load(f)

    print(f"Current dia_danh provinces: {len(dia_danh)}")
    print(f"Current chuyen_doi mappings: {len(chuyen_doi)}")

    # Load Bắc Ninh data
    with open('/home/user/MauBieu7202/templates_app/static/data/bacninh_dia_danh.json', 'r', encoding='utf-8') as f:
        bacninh_dia_danh = json.load(f)

    with open('/home/user/MauBieu7202/templates_app/static/data/bacninh_chuyen_doi.json', 'r', encoding='utf-8') as f:
        bacninh_chuyen_doi = json.load(f)

    # Load Cà Mau data
    with open('/home/user/MauBieu7202/templates_app/static/data/camau_dia_danh.json', 'r', encoding='utf-8') as f:
        camau_dia_danh = json.load(f)

    with open('/home/user/MauBieu7202/templates_app/static/data/camau_chuyen_doi.json', 'r', encoding='utf-8') as f:
        camau_chuyen_doi = json.load(f)

    # Merge dia_danh
    for province, data in bacninh_dia_danh.items():
        dia_danh[province] = data
        print(f"Added to dia_danh: {province}")

    for province, data in camau_dia_danh.items():
        dia_danh[province] = data
        print(f"Added to dia_danh: {province}")

    # Merge chuyen_doi
    chuyen_doi.update(bacninh_chuyen_doi)
    chuyen_doi.update(camau_chuyen_doi)

    print("\nAfter merge:")
    print(f"  dia_danh provinces: {len(dia_danh)}")
    print(f"  chuyen_doi mappings: {len(chuyen_doi)}")

    # Save updated files
    with open(DIA_DANH_PATH, 'w', encoding='utf-8') as f:
        json.dump(dia_danh, f, ensure_ascii=False, indent=2)

    with open(CHUYEN_DOI_PATH, 'w', encoding='utf-8') as f:
        json.dump(chuyen_doi, f, ensure_ascii=False, indent=2)

    print("\nFiles updated successfully!")
    print(f"  - {DIA_DANH_PATH}")
    print(f"  - {CHUYEN_DOI_PATH}")

if __name__ == "__main__":
    merge_data()

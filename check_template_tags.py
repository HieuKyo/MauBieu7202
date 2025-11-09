#!/usr/bin/env python
"""
Script kiểm tra các Content Control tags trong template
"""

import sys
from pathlib import Path
from docx import Document

def check_template_tags(template_path):
    """Kiểm tra tất cả Content Control tags trong template"""
    doc = Document(template_path)

    NSMAP = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'w14': 'http://schemas.microsoft.com/office/word/2010/wordml'
    }

    print(f"\n{'='*80}")
    print(f"CHECKING TEMPLATE TAGS")
    print(f"{'='*80}\n")
    print(f"File: {template_path}\n")

    checkboxes = {}
    textboxes = {}

    for sdt in doc.element.findall('.//w:sdt', namespaces=NSMAP):
        tag_element = sdt.find('.//w:tag', namespaces=NSMAP)
        tag_name = tag_element.get(f'{{{NSMAP["w"]}}}val') if tag_element is not None else "(no tag)"

        if tag_name == "(no tag)":
            continue

        # Check type
        checkbox_element = sdt.find('.//w14:checkbox', namespaces=NSMAP)
        sym_element = sdt.find('.//w:sym', namespaces=NSMAP)

        if checkbox_element is not None or sym_element is not None:
            checkboxes[tag_name] = checkboxes.get(tag_name, 0) + 1
        else:
            textboxes[tag_name] = textboxes.get(tag_name, 0) + 1

    # Print checkboxes
    print(f"CHECKBOXES ({len(checkboxes)} unique tags):")
    if checkboxes:
        for tag, count in sorted(checkboxes.items()):
            print(f"  - {tag} ({count}x)")
    else:
        print("  (none)")

    print(f"\nTEXTBOXES ({len(textboxes)} unique tags):")
    if textboxes:
        for tag, count in sorted(textboxes.items()):
            print(f"  - {tag} ({count}x)")
    else:
        print("  (none)")

    # Check for specific tags user mentioned
    print(f"\n{'='*80}")
    print("CHECKING SPECIFIC TAGS:")
    print(f"{'='*80}\n")

    tags_to_check = {
        'nghe_nghiep': 'Nghề nghiệp',
        'tk_theo_yeu_cau': 'Tài khoản theo yêu cầu',
        'tk_ngau_nhien': 'Tài khoản ngẫu nhiên',
        'dv_e_mobile': 'Dịch vụ E-Mobile',
        'dv_bankplus': 'Dịch vụ Bankplus/Agribank Plus',
    }

    for tag, description in tags_to_check.items():
        if tag in checkboxes:
            print(f"  ✓ {description}: CHECKBOX ({checkboxes[tag]}x)")
        elif tag in textboxes:
            print(f"  ✓ {description}: TEXTBOX ({textboxes[tag]}x)")
        else:
            print(f"  ✗ {description}: NOT FOUND")

    print()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python check_template_tags.py <template.docx>")
        print("\nExample:")
        print("  python check_template_tags.py C:\\Users\\hoang\\motkmoi.docx")
        sys.exit(1)

    template_path = sys.argv[1]
    check_template_tags(template_path)

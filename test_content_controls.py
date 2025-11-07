#!/usr/bin/env python
"""
Script test để kiểm tra Content Control (checkbox và textbox) trong Word template
"""

import sys
from pathlib import Path
from docx import Document

def analyze_content_controls(template_path):
    """Phân tích tất cả Content Controls trong template"""
    doc = Document(template_path)

    NSMAP = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'w14': 'http://schemas.microsoft.com/office/word/2010/wordml'
    }

    print(f"\n{'='*80}")
    print(f"Analyzing: {template_path}")
    print(f"{'='*80}\n")

    controls = []

    for idx, sdt in enumerate(doc.element.findall('.//w:sdt', namespaces=NSMAP), 1):
        # Get tag
        tag_element = sdt.find('.//w:tag', namespaces=NSMAP)
        tag_name = tag_element.get(f'{{{NSMAP["w"]}}}val') if tag_element is not None else "(no tag)"

        # Get alias
        alias_element = sdt.find('.//w:alias', namespaces=NSMAP)
        alias_name = alias_element.get(f'{{{NSMAP["w"]}}}val') if alias_element is not None else "(no alias)"

        # Determine type
        checkbox_element = sdt.find('.//w14:checkbox', namespaces=NSMAP)
        sym_element = sdt.find('.//w:sym', namespaces=NSMAP)

        if checkbox_element is not None:
            control_type = "Checkbox (w14:checkbox)"
            # Get checked state
            checked_element = checkbox_element.find('.//w14:checked', namespaces=NSMAP)
            checked_state = checked_element.get(f'{{{NSMAP["w14"]}}}val') if checked_element is not None else "unknown"
        elif sym_element is not None:
            control_type = "Checkbox (Wingdings)"
            char_code = sym_element.get(f'{{{NSMAP["w"]}}}char')
            checked_state = f"char={char_code}"
        else:
            control_type = "Text/Other"
            # Get current text
            text_elements = sdt.findall('.//w:t', namespaces=NSMAP)
            current_text = ''.join([t.text or '' for t in text_elements])
            checked_state = f"text='{current_text}'"

        control_info = {
            'index': idx,
            'type': control_type,
            'tag': tag_name,
            'alias': alias_name,
            'state': checked_state
        }
        controls.append(control_info)

        print(f"Content Control #{idx}")
        print(f"  Type:  {control_type}")
        print(f"  Tag:   {tag_name}")
        print(f"  Alias: {alias_name}")
        print(f"  State: {checked_state}")
        print()

    print(f"\n{'='*80}")
    print(f"Total Content Controls: {len(controls)}")
    print(f"{'='*80}\n")

    # Summary by type
    from collections import Counter
    type_counts = Counter([c['type'] for c in controls])
    print("\nSummary by Type:")
    for control_type, count in type_counts.items():
        print(f"  {control_type}: {count}")

    return controls


def test_render_content_controls(template_path, output_path):
    """Test rendering Content Controls với dữ liệu mẫu"""
    from templates_app.utils import JinjaWordTemplateProcessor

    print(f"\n{'='*80}")
    print(f"Testing Content Control Rendering")
    print(f"{'='*80}\n")

    # Tạo test data
    test_data = {
        # Checkbox variables
        'gioi_tinh_nam': '☑',
        'gioi_tinh_nu': '☐',
        'the_hang_chuan': '☐',
        'the_hang_vang': '☑',
        'the_hang_bach_kim': '☐',
        'the_ghi_no_noi_dia': '☐',
        'the_ghi_no_quoc_te': '☑',
        'the_tin_dung': '☐',
        'loai_the_jcb': '☐',
        'loai_the_visa': '☑',
        'loai_the_mastercard': '☐',
        'loai_the_khac': '☐',
        'loai_tien_vnd': '☑',
        'loai_tien_usd': '☐',
        'loai_tien_eur': '☐',
        'tk_ngau_nhien': '☐',
        'tk_theo_yeu_cau': '☑',
        'phat_hanh_lan_dau': '☑',
        'phat_hanh_lai': '☐',
        'dv_sms_banking': '☑',
        'dv_e_mobile': '☑',
        'dv_bankplus': '☐',
        'dv_e_commerce': '☑',
        'dv_soft_otp': '☐',
        'dv_smart_otp': '☑',
        'dv_retail_ebanking': '☐',
        'dv_thu_ho_tien_nuoc': '☑',
        'dv_thu_ho_tien_dien': '☑',
        'dv_thu_ho_vien_thong': '☐',
        'dv_thu_ho_hoc_phi': '☑',
        'dv_thu_ho_bao_hiem': '☐',
        'kenh_mobile': '☑',
        'kenh_internet': '☑',

        # Text variables (if any)
        'ho_ten': 'NGUYỄN VĂN A',
        'so_cmnd': '001234567890',
        'dia_chi': '123 Đường ABC, Quận 1, TP.HCM',
        'so_dien_thoai': '0901234567',
        'email': 'nguyenvana@example.com',
    }

    print("Test data:")
    print(f"  Checkboxes: {sum(1 for k, v in test_data.items() if v in ['☑', '☐'])} variables")
    print(f"  Text fields: {sum(1 for k, v in test_data.items() if v not in ['☑', '☐'])} variables")
    print()

    # Render template
    print("Rendering template...")
    processor = JinjaWordTemplateProcessor(template_path)
    processor.render(test_data)
    processor.save(output_path)

    print(f"✓ Saved to: {output_path}")
    print("\nNow analyzing output file...\n")

    # Analyze output
    analyze_content_controls(output_path)


if __name__ == '__main__':
    # Detect project root
    SCRIPT_DIR = Path(__file__).resolve().parent
    sys.path.insert(0, str(SCRIPT_DIR))

    if len(sys.argv) < 2:
        print("Usage:")
        print("  1. Analyze only:  python test_content_controls.py <template.docx>")
        print("  2. Test render:   python test_content_controls.py <template.docx> <output.docx>")
        sys.exit(1)

    template_path = sys.argv[1]

    if len(sys.argv) == 2:
        # Analyze only
        analyze_content_controls(template_path)
    else:
        # Test render
        output_path = sys.argv[2]
        print("\n" + "="*80)
        print("BEFORE RENDERING")
        print("="*80)
        analyze_content_controls(template_path)

        print("\n" + "="*80)
        print("RENDERING")
        print("="*80)
        test_render_content_controls(template_path, output_path)

#!/usr/bin/env python3
"""
Script test đơn giản để kiểm tra Content Control checkbox
KHÔNG cần Django - chỉ cần python-docx
"""
import sys
from pathlib import Path

try:
    from docx import Document
except ImportError:
    print("❌ Lỗi: Cần cài đặt python-docx")
    print("   Chạy: pip install python-docx")
    sys.exit(1)

def test_content_controls(template_path):
    """
    Test tìm Content Controls trong template
    """
    print("=" * 80)
    print("TEST CONTENT CONTROL CHECKBOXES")
    print("=" * 80)

    template_path = Path(template_path)

    if not template_path.exists():
        print(f"❌ File không tồn tại: {template_path}")
        return

    print(f"\n📄 Template: {template_path}")

    try:
        doc = Document(template_path)
        print("✅ Đã mở template thành công")
    except Exception as e:
        print(f"❌ Lỗi khi mở template: {e}")
        return

    print("\n🔍 Đang tìm Content Controls...")
    print("-" * 80)

    # Namespace cho Word XML
    NSMAP = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'w14': 'http://schemas.microsoft.com/office/word/2010/wordml'
    }

    controls_found = 0
    checkboxes_found = 0

    # Tìm tất cả Structured Document Tags (Content Controls)
    for sdt in doc.element.findall('.//w:sdt', namespaces=NSMAP):
        controls_found += 1

        # Lấy tag name
        tag_element = sdt.find('.//w:tag', namespaces=NSMAP)
        if tag_element is not None:
            tag_name = tag_element.get(f'{{{NSMAP["w"]}}}val')
        else:
            tag_name = "(no tag)"

        # Lấy alias/title
        alias_element = sdt.find('.//w:alias', namespaces=NSMAP)
        if alias_element is not None:
            alias = alias_element.get(f'{{{NSMAP["w"]}}}val')
        else:
            alias = "(no alias)"

        # Kiểm tra loại Content Control
        checkbox_element = sdt.find('.//w14:checkbox', namespaces=NSMAP)
        sym_element = sdt.find('.//w:sym', namespaces=NSMAP)

        if checkbox_element is not None:
            control_type = "✓ Checkbox (w14:checkbox)"
            checkboxes_found += 1

            # Kiểm tra trạng thái hiện tại
            checked_element = checkbox_element.find('.//w14:checked', namespaces=NSMAP)
            if checked_element is not None:
                checked_value = checked_element.get(f'{{{NSMAP["w14"]}}}val')
                current_state = "☑ CHECKED" if checked_value == '1' else "☐ UNCHECKED"
            else:
                current_state = "? Unknown"
        elif sym_element is not None:
            control_type = "✓ Legacy Checkbox (Wingdings)"
            checkboxes_found += 1
            char = sym_element.get(f'{{{NSMAP["w"]}}}char')
            if char == 'F0FE':
                current_state = "☑ CHECKED"
            elif char == 'F0A3':
                current_state = "☐ UNCHECKED"
            else:
                current_state = f"? Unknown ({char})"
        else:
            control_type = "○ Other Control (not checkbox)"
            current_state = "N/A"

        print(f"\n#{controls_found}:")
        print(f"   Type:         {control_type}")
        print(f"   Tag:          {tag_name}")
        print(f"   Title/Alias:  {alias}")
        print(f"   Current:      {current_state}")

    print("-" * 80)
    print(f"\n📊 SUMMARY:")
    print(f"   Total Content Controls found: {controls_found}")
    print(f"   Checkboxes found:             {checkboxes_found}")

    if controls_found == 0:
        print("\n⚠️  KHÔNG TìM THẤY CONTENT CONTROLS!")
        print("\n💡 Hướng dẫn:")
        print("   1. Mở template trong Word")
        print("   2. Bật tab Developer: File → Options → Customize Ribbon → ✓ Developer")
        print("   3. Insert checkbox: Developer → Check Box Content Control")
        print("   4. Click checkbox → Properties → Nhập Tag name")
        print("   5. Lưu file và test lại")
    elif checkboxes_found == 0:
        print("\n⚠️  Tìm thấy Content Controls nhưng KHÔNG phải checkbox!")
        print("   Hãy dùng 'Check Box Content Control' từ tab Developer")
    else:
        print("\n✅ Tìm thấy checkbox! Hãy kiểm tra Tag names có đúng không.")
        print("\n📋 Tag names cần dùng:")
        print("   - gioi_tinh_nam, gioi_tinh_nu")
        print("   - dv_sms_banking, dv_e_mobile, dv_bankplus")
        print("   - dv_thu_ho_tien_dien, dv_thu_ho_tien_nuoc")
        print("   - tk_ngau_nhien, tk_theo_yeu_cau")
        print("   - the_hang_chuan, the_hang_vang")
        print("   - phat_hanh_lan_dau, phat_hanh_lai")

    # Test rendering với dummy data
    print("\n" + "=" * 80)
    print("TEST RENDERING VỚI DUMMY DATA")
    print("=" * 80)

    dummy_data = {
        'ho_ten': 'NGUYỄN VĂN A',
        'gioi_tinh': 'Nam',
        'gioi_tinh_nam': '☑',
        'gioi_tinh_nu': '☐',
        'dv_e_mobile': '☑',
        'dv_sms_banking': '☐',
        'dv_bankplus': '☑',
        'dv_thu_ho_tien_dien': '☑',
        'dv_thu_ho_tien_nuoc': '☐',
        'tk_ngau_nhien': '☐',
        'tk_theo_yeu_cau': '☑',
        'the_hang_chuan': '☐',
        'the_hang_vang': '☑',
        'phat_hanh_lan_dau': '☑',
        'phat_hanh_lai': '☐',
    }

    print("\n📋 Dummy data:")
    for key in ['gioi_tinh_nam', 'gioi_tinh_nu', 'dv_e_mobile', 'dv_sms_banking']:
        if key in dummy_data:
            print(f"   {key}: {dummy_data[key]}")

    print("\n🔄 Processing...")

    def parse_checkbox_value(value):
        """Parse checkbox value"""
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            return value == '☑'
        elif isinstance(value, (int, float)):
            return value != 0
        else:
            return False

    processed = 0

    # Process checkboxes
    for sdt in doc.element.findall('.//w:sdt', namespaces=NSMAP):
        tag_element = sdt.find('.//w:tag', namespaces=NSMAP)
        if tag_element is None:
            continue

        tag_name = tag_element.get(f'{{{NSMAP["w"]}}}val')
        if not tag_name or tag_name not in dummy_data:
            continue

        value = dummy_data[tag_name]
        is_checked = parse_checkbox_value(value)

        print(f"   {tag_name}: {value} → {'☑' if is_checked else '☐'}")

        # Set checkbox
        checkbox_element = sdt.find('.//w14:checkbox', namespaces=NSMAP)
        if checkbox_element is not None:
            checked_element = checkbox_element.find('.//w14:checked', namespaces=NSMAP)
            if checked_element is not None:
                checked_element.set(f'{{{NSMAP["w14"]}}}val', '1' if is_checked else '0')
                processed += 1
        else:
            sym_element = sdt.find('.//w:sym', namespaces=NSMAP)
            if sym_element is not None:
                char_code = 'F0FE' if is_checked else 'F0A3'
                sym_element.set(f'{{{NSMAP["w"]}}}char', char_code)
                processed += 1

    # Save output
    output_path = template_path.parent / (template_path.stem + '_TEST_OUTPUT.docx')
    doc.save(str(output_path))

    print(f"\n✅ Processed {processed} checkboxes")
    print(f"📁 Output: {output_path}")
    print("\n💡 Mở file output để xem kết quả!")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Cách dùng: python test_checkbox_simple.py <path_to_template.docx>")
        print("\nVí dụ:")
        print("  python test_checkbox_simple.py C:\\Users\\hoang\\template.docx")
        print("  python test_checkbox_simple.py media/templates/test.docx")
        sys.exit(1)

    template_path = sys.argv[1]
    test_content_controls(template_path)

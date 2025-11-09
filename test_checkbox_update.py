#!/usr/bin/env python
"""
Test update checkbox và phân tích kỹ hơn
"""

import sys
from pathlib import Path
from docx import Document
from lxml import etree

def compare_before_after(before_path, after_path, tag_name):
    """So sánh file trước và sau khi update"""

    NSMAP = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'w14': 'http://schemas.microsoft.com/office/word/2010/wordml'
    }

    def get_checkbox_info(doc_path):
        doc = Document(doc_path)
        for sdt in doc.element.findall('.//w:sdt', namespaces=NSMAP):
            tag_element = sdt.find('.//w:tag', namespaces=NSMAP)
            if tag_element is None:
                continue

            current_tag = tag_element.get(f'{{{NSMAP["w"]}}}val')
            if current_tag != tag_name:
                continue

            checkbox_element = sdt.find('.//w14:checkbox', namespaces=NSMAP)
            if checkbox_element is None:
                return None

            checked_element = checkbox_element.find('.//w14:checked', namespaces=NSMAP)
            checked_val = checked_element.get(f'{{{NSMAP["w14"]}}}val') if checked_element is not None else "N/A"

            # Get text content inside checkbox
            text_elements = sdt.findall('.//w:t', namespaces=NSMAP)
            text_content = ''.join([t.text or '' for t in text_elements])

            return {
                'checked_val': checked_val,
                'text_content': text_content,
                'full_xml': etree.tostring(sdt, pretty_print=True, encoding='unicode')
            }

        return None

    print(f"\n{'='*80}")
    print(f"COMPARING: {tag_name}")
    print(f"{'='*80}\n")

    before_info = get_checkbox_info(before_path)
    after_info = get_checkbox_info(after_path)

    if before_info is None:
        print(f"❌ Checkbox '{tag_name}' not found in BEFORE file")
        return

    if after_info is None:
        print(f"❌ Checkbox '{tag_name}' not found in AFTER file")
        return

    print("BEFORE:")
    print(f"  w14:checked value: {before_info['checked_val']}")
    print(f"  Text content: '{before_info['text_content']}'")
    print()

    print("AFTER:")
    print(f"  w14:checked value: {after_info['checked_val']}")
    print(f"  Text content: '{after_info['text_content']}'")
    print()

    if before_info['checked_val'] != after_info['checked_val']:
        print(f"✅ w14:checked CHANGED: {before_info['checked_val']} → {after_info['checked_val']}")
    else:
        print(f"❌ w14:checked NOT CHANGED (still {before_info['checked_val']})")

    if before_info['text_content'] != after_info['text_content']:
        print(f"✅ Text content CHANGED: '{before_info['text_content']}' → '{after_info['text_content']}'")
    else:
        print(f"ℹ️  Text content NOT CHANGED (still '{before_info['text_content']}')")

    print("\n" + "="*80)
    print("FULL XML OF AFTER:")
    print("="*80)
    print(after_info['full_xml'])


def test_update_with_text_change(template_path, output_path, tag_name):
    """Test update checkbox VÀ text content bên trong"""
    doc = Document(template_path)

    NSMAP = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'w14': 'http://schemas.microsoft.com/office/word/2010/wordml'
    }

    print(f"\n{'='*80}")
    print(f"TEST: Updating checkbox '{tag_name}' + text content")
    print(f"{'='*80}\n")

    for sdt in doc.element.findall('.//w:sdt', namespaces=NSMAP):
        tag_element = sdt.find('.//w:tag', namespaces=NSMAP)
        if tag_element is None:
            continue

        current_tag = tag_element.get(f'{{{NSMAP["w"]}}}val')
        if current_tag != tag_name:
            continue

        print(f"Found Content Control with tag '{tag_name}'")

        # Update w14:checked
        checkbox_element = sdt.find('.//w14:checkbox', namespaces=NSMAP)
        if checkbox_element is not None:
            checked_element = checkbox_element.find('.//w14:checked', namespaces=NSMAP)
            if checked_element is not None:
                old_val = checked_element.get(f'{{{NSMAP["w14"]}}}val')
                new_val = '1'
                checked_element.set(f'{{{NSMAP["w14"]}}}val', new_val)
                print(f"  ✓ Updated w14:checked: {old_val} → {new_val}")

        # Also try updating text content (some checkboxes display text)
        text_elements = sdt.findall('.//w:t', namespaces=NSMAP)
        if text_elements:
            old_text = text_elements[0].text
            # Try different checkbox symbols
            text_elements[0].text = '☑'  # Unicode checked box
            print(f"  ✓ Updated text content: '{old_text}' → '☑'")

        break

    doc.save(output_path)
    print(f"\n✓ Saved to: {output_path}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  1. Compare before/after: python test_checkbox_update.py <before.docx> <after.docx> <tag_name>")
        print("  2. Test update:          python test_checkbox_update.py <template.docx> <output.docx> <tag_name> update")
        print("\nExample:")
        print("  python test_checkbox_update.py original.docx test_output.docx gioi_tinh_nam")
        print("  python test_checkbox_update.py original.docx test_output2.docx gioi_tinh_nam update")
        sys.exit(1)

    if len(sys.argv) == 4:
        # Compare mode
        before_path = sys.argv[1]
        after_path = sys.argv[2]
        tag_name = sys.argv[3]
        compare_before_after(before_path, after_path, tag_name)
    elif len(sys.argv) == 5 and sys.argv[4] == 'update':
        # Update mode
        template_path = sys.argv[1]
        output_path = sys.argv[2]
        tag_name = sys.argv[3]
        test_update_with_text_change(template_path, output_path, tag_name)

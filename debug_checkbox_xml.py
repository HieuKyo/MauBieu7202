#!/usr/bin/env python
"""
Script debug chi tiết để xem cấu trúc XML của checkbox
"""

import sys
from pathlib import Path
from docx import Document
from lxml import etree

def debug_checkbox_xml(template_path, tag_to_inspect=None):
    """Debug chi tiết cấu trúc XML của checkbox"""
    doc = Document(template_path)

    NSMAP = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'w14': 'http://schemas.microsoft.com/office/word/2010/wordml'
    }

    print(f"\n{'='*80}")
    print(f"DEBUG: Checkbox XML Structure")
    print(f"{'='*80}\n")

    for idx, sdt in enumerate(doc.element.findall('.//w:sdt', namespaces=NSMAP), 1):
        # Get tag
        tag_element = sdt.find('.//w:tag', namespaces=NSMAP)
        tag_name = tag_element.get(f'{{{NSMAP["w"]}}}val') if tag_element is not None else "(no tag)"

        # Skip if not the tag we're looking for
        if tag_to_inspect and tag_name != tag_to_inspect:
            continue

        # Check if this is a checkbox
        checkbox_element = sdt.find('.//w14:checkbox', namespaces=NSMAP)
        sym_element = sdt.find('.//w:sym', namespaces=NSMAP)

        if checkbox_element is not None or sym_element is not None:
            print(f"\n{'='*80}")
            print(f"Content Control #{idx}: {tag_name}")
            print(f"{'='*80}\n")

            if checkbox_element is not None:
                print("✓ Found w14:checkbox element")

                # Get checked element
                checked_element = checkbox_element.find('.//w14:checked', namespaces=NSMAP)
                if checked_element is not None:
                    checked_val = checked_element.get(f'{{{NSMAP["w14"]}}}val')
                    print(f"  - Current checked value: {checked_val}")
                else:
                    print("  - WARNING: No w14:checked element found!")

                # Get checkedState element
                checked_state = checkbox_element.find('.//w14:checkedState', namespaces=NSMAP)
                if checked_state is not None:
                    checked_state_val = checked_state.get(f'{{{NSMAP["w14"]}}}val')
                    print(f"  - checkedState value: {checked_state_val}")

                # Get uncheckedState element
                unchecked_state = checkbox_element.find('.//w14:uncheckedState', namespaces=NSMAP)
                if unchecked_state is not None:
                    unchecked_state_val = unchecked_state.get(f'{{{NSMAP["w14"]}}}val')
                    print(f"  - uncheckedState value: {unchecked_state_val}")

                # Print full XML structure
                print("\nFull w14:checkbox XML:")
                print(etree.tostring(checkbox_element, pretty_print=True, encoding='unicode'))

            if sym_element is not None:
                print("✓ Found w:sym element (Wingdings)")
                char_code = sym_element.get(f'{{{NSMAP["w"]}}}char')
                font = sym_element.get(f'{{{NSMAP["w"]}}}font')
                print(f"  - Current char code: {char_code}")
                print(f"  - Font: {font}")

                # Print full XML structure
                print("\nFull w:sym XML:")
                print(etree.tostring(sym_element, pretty_print=True, encoding='unicode'))

            # Print parent SDT properties
            sdt_pr = sdt.find('.//w:sdtPr', namespaces=NSMAP)
            if sdt_pr is not None:
                print("\nFull w:sdtPr (SDT Properties) XML:")
                print(etree.tostring(sdt_pr, pretty_print=True, encoding='unicode'))

            # If specific tag, stop after finding it
            if tag_to_inspect:
                break

    if tag_to_inspect:
        print(f"\nSearched for tag: '{tag_to_inspect}'")


def test_update_checkbox(template_path, output_path, tag_name, should_check=True):
    """Test update một checkbox cụ thể"""
    doc = Document(template_path)

    NSMAP = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'w14': 'http://schemas.microsoft.com/office/word/2010/wordml'
    }

    print(f"\n{'='*80}")
    print(f"TEST: Updating checkbox '{tag_name}' to {'CHECKED' if should_check else 'UNCHECKED'}")
    print(f"{'='*80}\n")

    updated = False

    for sdt in doc.element.findall('.//w:sdt', namespaces=NSMAP):
        tag_element = sdt.find('.//w:tag', namespaces=NSMAP)
        if tag_element is None:
            continue

        current_tag = tag_element.get(f'{{{NSMAP["w"]}}}val')
        if current_tag != tag_name:
            continue

        print(f"Found Content Control with tag '{tag_name}'")

        # Try w14:checkbox
        checkbox_element = sdt.find('.//w14:checkbox', namespaces=NSMAP)
        if checkbox_element is not None:
            print("  - Type: w14:checkbox")
            checked_element = checkbox_element.find('.//w14:checked', namespaces=NSMAP)
            if checked_element is not None:
                old_val = checked_element.get(f'{{{NSMAP["w14"]}}}val')
                new_val = '1' if should_check else '0'
                checked_element.set(f'{{{NSMAP["w14"]}}}val', new_val)
                print(f"  - Updated: {old_val} → {new_val}")
                updated = True
            else:
                print("  - ERROR: No w14:checked element found!")

        # Try w:sym
        sym_element = sdt.find('.//w:sym', namespaces=NSMAP)
        if sym_element is not None:
            print("  - Type: w:sym (Wingdings)")
            old_char = sym_element.get(f'{{{NSMAP["w"]}}}char')
            new_char = 'F0FE' if should_check else 'F0A3'
            sym_element.set(f'{{{NSMAP["w"]}}}char', new_char)
            print(f"  - Updated: {old_char} → {new_char}")
            updated = True

        break

    if updated:
        doc.save(output_path)
        print(f"\n✓ Saved to: {output_path}")
        print("\nNow inspect the output file to see if checkbox changed.")
    else:
        print("\n✗ Failed to update checkbox!")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  1. Debug all checkboxes:     python debug_checkbox_xml.py <template.docx>")
        print("  2. Debug specific tag:       python debug_checkbox_xml.py <template.docx> <tag_name>")
        print("  3. Test update checkbox:     python debug_checkbox_xml.py <template.docx> <tag_name> <output.docx>")
        print("\nExample:")
        print("  python debug_checkbox_xml.py template.docx gioi_tinh_nam")
        print("  python debug_checkbox_xml.py template.docx gioi_tinh_nam output.docx")
        sys.exit(1)

    template_path = sys.argv[1]

    if len(sys.argv) == 2:
        # Debug all checkboxes
        debug_checkbox_xml(template_path)
    elif len(sys.argv) == 3:
        # Debug specific tag
        tag_name = sys.argv[2]
        debug_checkbox_xml(template_path, tag_name)
    else:
        # Test update
        tag_name = sys.argv[2]
        output_path = sys.argv[3]
        debug_checkbox_xml(template_path, tag_name)
        test_update_checkbox(template_path, output_path, tag_name, should_check=True)

"""
Script chuyển đổi template Word từ format cũ sang mới
Chuyển đổi: [BienCu] → {{ bien_moi }}

Cách sử dụng:
    python convert_old_templates.py input.docx output.docx
    python convert_old_templates.py folder_cu/ folder_moi/

Yêu cầu:
    pip install python-docx
"""

import sys
import os
import re
from pathlib import Path
from docx import Document
from templates_app.variable_mapping import OLD_TO_NEW_MAPPING


def convert_text_with_mapping(text):
    """
    Chuyển đổi text từ [BienCu] sang {{ bien_moi }}

    Args:
        text (str): Text chứa biến cũ

    Returns:
        str: Text với biến mới
    """
    if not text:
        return text

    # Convert từng biến
    converted_text = text
    for old_var, new_var in OLD_TO_NEW_MAPPING.items():
        if old_var in converted_text:
            # Replace [BienCu] → {{ bien_moi }}
            converted_text = converted_text.replace(old_var, f"{{{{ {new_var} }}}}")
            print(f"  ✓ Converted: {old_var} → {{{{ {new_var} }}}}")

    return converted_text


def convert_docx_file(input_path, output_path):
    """
    Chuyển đổi file .docx từ format cũ sang mới

    Args:
        input_path (str): Đường dẫn file input
        output_path (str): Đường dẫn file output
    """
    print(f"\n{'='*60}")
    print(f"Converting: {input_path}")
    print(f"Output to: {output_path}")
    print(f"{'='*60}\n")

    try:
        # Load document
        doc = Document(input_path)

        conversion_count = 0

        # Convert paragraphs
        print("Converting paragraphs...")
        for i, paragraph in enumerate(doc.paragraphs):
            original_text = paragraph.text
            if not original_text.strip():
                continue

            converted_text = convert_text_with_mapping(original_text)

            if original_text != converted_text:
                # Xóa toàn bộ runs cũ
                for run in paragraph.runs:
                    run.text = ''

                # Thêm text mới vào run đầu tiên
                if paragraph.runs:
                    paragraph.runs[0].text = converted_text
                else:
                    paragraph.add_run(converted_text)

                conversion_count += 1

        # Convert tables
        print("\nConverting tables...")
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        original_text = paragraph.text
                        if not original_text.strip():
                            continue

                        converted_text = convert_text_with_mapping(original_text)

                        if original_text != converted_text:
                            # Xóa toàn bộ runs cũ
                            for run in paragraph.runs:
                                run.text = ''

                            # Thêm text mới
                            if paragraph.runs:
                                paragraph.runs[0].text = converted_text
                            else:
                                paragraph.add_run(converted_text)

                            conversion_count += 1

        # Convert headers
        print("\nConverting headers...")
        for section in doc.sections:
            # Header
            for paragraph in section.header.paragraphs:
                original_text = paragraph.text
                if original_text.strip():
                    converted_text = convert_text_with_mapping(original_text)
                    if original_text != converted_text:
                        for run in paragraph.runs:
                            run.text = ''
                        if paragraph.runs:
                            paragraph.runs[0].text = converted_text
                        conversion_count += 1

            # Footer
            for paragraph in section.footer.paragraphs:
                original_text = paragraph.text
                if original_text.strip():
                    converted_text = convert_text_with_mapping(original_text)
                    if original_text != converted_text:
                        for run in paragraph.runs:
                            run.text = ''
                        if paragraph.runs:
                            paragraph.runs[0].text = converted_text
                        conversion_count += 1

        # Save output
        doc.save(output_path)

        print(f"\n{'='*60}")
        print(f"✅ SUCCESS!")
        print(f"Total conversions: {conversion_count}")
        print(f"Output saved to: {output_path}")
        print(f"{'='*60}\n")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def convert_folder(input_folder, output_folder):
    """
    Chuyển đổi tất cả file .docx trong folder

    Args:
        input_folder (str): Folder chứa file cũ
        output_folder (str): Folder output
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)

    # Tạo output folder nếu chưa có
    output_path.mkdir(parents=True, exist_ok=True)

    # Tìm tất cả file .docx
    docx_files = list(input_path.glob("*.docx"))

    if not docx_files:
        print(f"⚠ No .docx files found in {input_folder}")
        return

    print(f"\nFound {len(docx_files)} .docx files")
    print(f"Input folder: {input_folder}")
    print(f"Output folder: {output_folder}\n")

    success_count = 0
    fail_count = 0

    for i, input_file in enumerate(docx_files, 1):
        print(f"\n[{i}/{len(docx_files)}] Processing: {input_file.name}")

        output_file = output_path / input_file.name

        if convert_docx_file(str(input_file), str(output_file)):
            success_count += 1
        else:
            fail_count += 1

    print(f"\n{'='*60}")
    print(f"BATCH CONVERSION COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Success: {success_count} files")
    print(f"❌ Failed: {fail_count} files")
    print(f"{'='*60}\n")


def main():
    """Main function"""
    if len(sys.argv) < 3:
        print("="*60)
        print("SCRIPT CHUYỂN ĐỔI TEMPLATE WORD")
        print("Chuyển đổi: [BienCu] → {{ bien_moi }}")
        print("="*60)
        print("\nCách sử dụng:")
        print("  1. Convert 1 file:")
        print("     python convert_old_templates.py input.docx output.docx")
        print("\n  2. Convert cả folder:")
        print("     python convert_old_templates.py folder_cu/ folder_moi/")
        print("\nVí dụ:")
        print("  python convert_old_templates.py templates_cu/mau_1.docx templates_moi/mau_1.docx")
        print("  python convert_old_templates.py templates_cu/ templates_moi/")
        print("="*60)
        sys.exit(1)

    input_arg = sys.argv[1]
    output_arg = sys.argv[2]

    # Check if input is file or folder
    if os.path.isfile(input_arg):
        # Convert single file
        convert_docx_file(input_arg, output_arg)
    elif os.path.isdir(input_arg):
        # Convert folder
        convert_folder(input_arg, output_arg)
    else:
        print(f"❌ ERROR: {input_arg} is not a valid file or folder")
        sys.exit(1)


if __name__ == "__main__":
    main()

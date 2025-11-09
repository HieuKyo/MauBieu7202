#!/usr/bin/env python
"""
Script batch convert tất cả template Word trong folder
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from docx import Document
from convert_old_templates import CHECKBOX_TAG_MAPPING, convert_checkbox_tags

def batch_convert_templates(folder_path, recursive=False):
    """
    Convert tất cả file .docx trong folder

    Args:
        folder_path: Đường dẫn folder chứa templates
        recursive: True để convert cả subfolder
    """
    folder = Path(folder_path)

    if not folder.exists():
        print(f"❌ Folder không tồn tại: {folder_path}")
        return

    if not folder.is_dir():
        print(f"❌ Không phải folder: {folder_path}")
        return

    # Tìm tất cả file .docx
    if recursive:
        docx_files = list(folder.rglob('*.docx'))
    else:
        docx_files = list(folder.glob('*.docx'))

    # Loại bỏ file backup và temp
    docx_files = [f for f in docx_files if not f.name.startswith('~$') and '_backup_' not in f.name]

    if not docx_files:
        print(f"❌ Không tìm thấy file .docx nào trong: {folder_path}")
        return

    print(f"\n{'='*80}")
    print(f"BATCH CONVERT TEMPLATES")
    print(f"{'='*80}\n")
    print(f"Folder: {folder_path}")
    print(f"Found: {len(docx_files)} file(s)")
    print(f"Recursive: {'Yes' if recursive else 'No'}")
    print()

    # Confirm
    response = input("Bạn có muốn tiếp tục? (y/n): ")
    if response.lower() not in ['y', 'yes']:
        print("Đã hủy.")
        return

    print()

    # Convert từng file
    total_converted = 0
    total_tags_replaced = 0
    failed_files = []

    for idx, docx_file in enumerate(docx_files, 1):
        print(f"[{idx}/{len(docx_files)}] {docx_file.name}")

        try:
            # Tạo backup
            backup_name = docx_file.stem + f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx'
            backup_path = docx_file.parent / backup_name

            import shutil
            shutil.copy2(docx_file, backup_path)
            print(f"  ✓ Backup: {backup_name}")

            # Load document
            doc = Document(str(docx_file))

            # Convert checkbox tags
            tag_replacements = convert_checkbox_tags(doc)

            if tag_replacements:
                # Save document
                doc.save(str(docx_file))

                total_converted += 1
                tags_count = sum(tag_replacements.values())
                total_tags_replaced += tags_count

                print(f"  ✓ Converted {tags_count} checkbox tag(s)")
                for old_tag, count in sorted(tag_replacements.items()):
                    new_tag = CHECKBOX_TAG_MAPPING[old_tag]
                    print(f"    - {old_tag} → {new_tag} ({count}x)")
            else:
                print(f"  ℹ️  No old tags found (already converted or no checkboxes)")
                # Delete backup if nothing changed
                backup_path.unlink()

        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed_files.append(str(docx_file))

        print()

    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}\n")
    print(f"Total files processed: {len(docx_files)}")
    print(f"Successfully converted: {total_converted}")
    print(f"Total tags replaced: {total_tags_replaced}")
    print(f"Failed: {len(failed_files)}")

    if failed_files:
        print(f"\nFailed files:")
        for f in failed_files:
            print(f"  - {f}")

    print(f"\nBackup files created in the same folder with '_backup_YYYYMMDD_HHMMSS.docx' suffix")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python batch_convert_templates.py <folder_path> [--recursive]")
        print("\nExample:")
        print("  python batch_convert_templates.py C:\\Templates")
        print("  python batch_convert_templates.py C:\\Templates --recursive")
        print("\nNote: Backup files will be created automatically before conversion")
        sys.exit(1)

    folder_path = sys.argv[1]
    recursive = '--recursive' in sys.argv or '-r' in sys.argv

    batch_convert_templates(folder_path, recursive)

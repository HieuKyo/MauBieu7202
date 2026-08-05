"""
Dịch vụ tách và ghép file PDF.
Yêu cầu: pip install pypdf
"""

import io
import zipfile

ALLOWED_EXT = {'.pdf'}
MAX_FILE_SIZE_MB = 100
MAX_MERGE_FILES = 20


def validate_pdf(uploaded_file):
    """
    Kiểm tra file upload là PDF và không quá giới hạn kích thước.
    Returns (True, '') hoặc (False, error_msg).
    """
    import os
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_EXT:
        return False, 'Chỉ chấp nhận file PDF (.pdf)'
    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f'File quá lớn ({size_mb:.1f} MB). Giới hạn: {MAX_FILE_SIZE_MB} MB'
    return True, ''


def parse_page_ranges(ranges_str, total_pages):
    """
    Chuyển chuỗi phạm vi trang như "1,3,5-8" thành danh sách số trang (1-indexed).
    Ví dụ: "1,3,5-7" với total_pages=10 → [1, 3, 5, 6, 7]

    Raises:
        ValueError: Nếu chuỗi không hợp lệ hoặc trang nằm ngoài tài liệu.
    """
    if not ranges_str.strip():
        raise ValueError('Vui lòng nhập số trang cần trích xuất.')

    pages = set()
    for part in ranges_str.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            bounds = part.split('-')
            if len(bounds) != 2:
                raise ValueError(f'Phạm vi không hợp lệ: "{part}"')
            start, end = int(bounds[0]), int(bounds[1])
            if start > end:
                raise ValueError(f'Trang bắt đầu phải nhỏ hơn trang kết thúc: "{part}"')
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))

    invalid = [p for p in pages if p < 1 or p > total_pages]
    if invalid:
        raise ValueError(
            f'Số trang {sorted(invalid)} nằm ngoài tài liệu (tổng {total_pages} trang).'
        )

    return sorted(pages)


def split_to_zip(pdf_bytes):
    """
    Tách mỗi trang PDF thành file riêng, nén vào ZIP.

    Args:
        pdf_bytes (bytes): Nội dung file PDF.

    Returns:
        (bytes, int): Nội dung ZIP và tổng số trang.
    """
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(io.BytesIO(pdf_bytes))
    total = len(reader.pages)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            page_buf = io.BytesIO()
            writer.write(page_buf)
            zf.writestr(f'trang_{i + 1:03d}.pdf', page_buf.getvalue())

    return zip_buffer.getvalue(), total


def extract_pages(pdf_bytes, page_numbers):
    """
    Trích xuất các trang cụ thể từ PDF thành một PDF mới.

    Args:
        pdf_bytes (bytes): Nội dung file PDF gốc.
        page_numbers (list[int]): Danh sách số trang cần lấy (1-indexed).

    Returns:
        bytes: Nội dung PDF mới chứa các trang được chọn.
    """
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()

    for n in page_numbers:
        writer.add_page(reader.pages[n - 1])

    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def merge_pdfs(pdf_bytes_list):
    """
    Ghép nhiều PDF thành một, theo thứ tự danh sách.

    Args:
        pdf_bytes_list (list[bytes]): Danh sách nội dung các file PDF.

    Returns:
        bytes: Nội dung PDF đã ghép.
    """
    from pypdf import PdfReader, PdfWriter

    writer = PdfWriter()
    for pdf_bytes in pdf_bytes_list:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            writer.add_page(page)

    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()

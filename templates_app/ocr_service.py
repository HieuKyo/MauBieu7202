"""
Dịch vụ OCR: Trích xuất văn bản từ ảnh hoặc PDF, xuất ra file Word.

Yêu cầu cài đặt bên ngoài (Windows):
  1. Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
     - Cài đặt gói ngôn ngữ tiếng Việt (vie) khi cài.
     - Mặc định cài vào: C:\Program Files\Tesseract-OCR\
  2. Poppler (chỉ cần để đọc PDF): https://github.com/oschwartz10612/poppler-windows/releases
     - Giải nén và đặt vào: C:\poppler\Library\bin\
"""

import io
import os
import re
import tempfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from PIL import Image, ImageEnhance, ImageFilter

# ---------------------------------------------------------------------------
# Cấu hình đường dẫn (thay đổi nếu cài đặt ở vị trí khác)
# ---------------------------------------------------------------------------
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'C:\poppler\Library\bin'

# Áp dụng đường dẫn Tesseract nếu tồn tại (bỏ qua nếu đã có trong PATH)
try:
    import pytesseract
    if os.path.exists(TESSERACT_CMD):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
except ImportError:
    pytesseract = None  # Sẽ báo lỗi rõ ràng khi gọi hàm OCR

# ---------------------------------------------------------------------------
# Hằng số cấu hình
# ---------------------------------------------------------------------------
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.pdf'}
MAX_FILE_SIZE_MB = 50
MAX_PDF_PAGES = 30
OCR_LANG = 'vie+eng'           # Tiếng Việt + Tiếng Anh
OCR_CONFIG = '--psm 3 --oem 1' # PSM 3: tự động phân tích layout; OEM 1: LSTM (chính xác hơn)


# ---------------------------------------------------------------------------
# 1. Kiểm tra file đầu vào
# ---------------------------------------------------------------------------
def validate_file(uploaded_file):
    """
    Xác thực file upload: đuôi file và kích thước.

    Args:
        uploaded_file: InMemoryUploadedFile từ Django request.FILES

    Returns:
        (True, '') nếu hợp lệ
        (False, error_message) nếu không hợp lệ
    """
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        allowed_str = ', '.join(sorted(ALLOWED_EXTENSIONS))
        return False, f"Định dạng không hỗ trợ. Chấp nhận: {allowed_str}"

    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"File quá lớn ({size_mb:.1f} MB). Giới hạn: {MAX_FILE_SIZE_MB} MB"

    return True, ''


# ---------------------------------------------------------------------------
# 2. Gộp các dòng bị ngắt giữa câu
# ---------------------------------------------------------------------------
# Dấu hiệu nhận biết đầu đoạn mới (số thứ tự, gạch đầu dòng, chữ số La Mã)
_NEW_PARA_RE = re.compile(r'^(\d+[\.\)]\s+|[-•*]\s+|[IVX]+[\.\)]\s+)')
# Ký tự kết thúc câu — dòng kết thúc bằng những ký tự này thì KHÔNG ghép tiếp
_TERMINAL = set('.!?')


def _join_broken_lines(text):
    """
    Gộp các dòng bị ngắt giữa câu do Tesseract nhận diện từng dòng vật lý.

    Quy tắc:
    - Dòng rỗng → giữ nguyên, đánh dấu ranh giới đoạn văn.
    - Dòng kết thúc bằng '.' '!' '?' → KHÔNG ghép (câu đã kết thúc).
    - Dòng tiếp theo bắt đầu bằng số thứ tự / gạch đầu dòng → KHÔNG ghép (đoạn mới).
    - Các trường hợp còn lại → ghép bằng dấu cách.
    """
    lines = text.split('\n')
    result = []
    buffer = ''

    for line in lines:
        stripped = line.strip()

        if not stripped:
            # Dòng rỗng → flush buffer, giữ dòng trống
            if buffer:
                result.append(buffer)
                buffer = ''
            result.append('')
            continue

        is_new_para = bool(_NEW_PARA_RE.match(stripped))

        if buffer:
            last_char = buffer[-1]
            if last_char in _TERMINAL or is_new_para:
                result.append(buffer)
                buffer = stripped
            else:
                buffer = buffer + ' ' + stripped
        else:
            buffer = stripped

    if buffer:
        result.append(buffer)

    # Thu gọn nhiều dòng trống liên tiếp thành tối đa 1
    cleaned = re.sub(r'\n{3,}', '\n\n', '\n'.join(result))
    return cleaned.strip()


# ---------------------------------------------------------------------------
# 3. Tiền xử lý ảnh để tăng độ chính xác OCR
# ---------------------------------------------------------------------------
def _preprocess_image(img):
    """
    Chuẩn hóa ảnh trước khi OCR:
    - Chuyển sang grayscale (ảnh màu làm Tesseract nhầm dấu tiếng Việt)
    - Tăng độ tương phản để chữ rõ hơn
    - Tăng kích thước nếu ảnh quá nhỏ (DPI thấp làm mất dấu)
    """
    # Chuyển sang grayscale
    img = img.convert('L')

    # Tăng kích thước nếu chiều rộng dưới 1500px (ảnh chụp điện thoại thường nhỏ)
    w, h = img.size
    if w < 1500:
        scale = 1500 / w
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    # Tăng độ tương phản
    img = ImageEnhance.Contrast(img).enhance(1.8)

    # Làm sắc nét nhẹ
    img = img.filter(ImageFilter.SHARPEN)

    return img


# ---------------------------------------------------------------------------
# 4. OCR một file ảnh
# ---------------------------------------------------------------------------
def _ocr_image_file(image_path):
    """
    Chạy OCR trên một file ảnh và trả về chuỗi văn bản.
    Đóng Image ngay sau khi xử lý để tránh memory leak.

    Args:
        image_path (str): Đường dẫn tuyệt đối đến file ảnh.

    Returns:
        str: Văn bản trích xuất được (có thể rỗng).
    """
    if pytesseract is None:
        raise RuntimeError(
            "Thư viện pytesseract chưa được cài đặt. Chạy: pip install pytesseract"
        )

    img = None
    try:
        img = Image.open(image_path)
        img = _preprocess_image(img)
        text = pytesseract.image_to_string(img, lang=OCR_LANG, config=OCR_CONFIG)
        return text.strip()
    finally:
        if img:
            img.close()


# ---------------------------------------------------------------------------
# 5. Trích xuất text từ PDF có text selectable (không cần OCR)
# ---------------------------------------------------------------------------
# Ngưỡng tối thiểu: nếu trung bình mỗi trang ít hơn 50 ký tự thì coi là PDF scan
_MIN_CHARS_PER_PAGE = 50


def _extract_pdf_text_direct(pdf_path):
    """
    Dùng pdfplumber để đọc text trực tiếp từ PDF có text selectable.
    Tốt hơn nhiều so với OCR cho tài liệu chứa bảng biểu, cột, ký tự đặc biệt.

    Returns:
        list[str] nếu PDF có text (một phần tử = một trang),
        None nếu PDF là ảnh scan hoặc pdfplumber chưa cài.
    """
    try:
        import pdfplumber
    except ImportError:
        return None

    texts = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:MAX_PDF_PAGES]:
                # extract_text giữ khoảng cách giữa các từ theo tọa độ thực
                text = page.extract_text(x_tolerance=3, y_tolerance=3) or ''
                texts.append(text.strip())
    except Exception:
        return None

    # Kiểm tra có đủ text không (PDF scan sẽ trả về rỗng)
    total_chars = sum(len(t) for t in texts)
    avg = total_chars / max(len(texts), 1)
    if avg < _MIN_CHARS_PER_PAGE:
        return None  # Likely scanned — fall back to OCR

    return texts


# ---------------------------------------------------------------------------
# 6. Chuyển PDF sang ảnh để OCR (fallback cho PDF scan)
# ---------------------------------------------------------------------------
def _pdf_to_image_paths(pdf_path, output_dir):
    """
    Chuyển từng trang PDF thành ảnh PNG riêng biệt trong output_dir.
    Giải phóng bộ nhớ từng trang ngay sau khi lưu.

    Returns:
        list[str]: Danh sách đường dẫn ảnh theo thứ tự trang.
    """
    try:
        from pdf2image import convert_from_path
        from pdf2image.exceptions import PDFInfoNotInstalledError
    except ImportError:
        raise ImportError(
            "Thư viện pdf2image chưa được cài đặt. Chạy: pip install pdf2image"
        )

    poppler_path = POPPLER_PATH if os.path.isdir(POPPLER_PATH) else None

    try:
        pages = convert_from_path(
            pdf_path,
            dpi=200,
            output_folder=output_dir,
            fmt='png',
            first_page=1,
            last_page=MAX_PDF_PAGES,
            poppler_path=poppler_path,
        )
    except PDFInfoNotInstalledError:
        raise RuntimeError(
            "Poppler chưa được cài đặt hoặc không tìm thấy. "
            "Tải tại: https://github.com/oschwartz10612/poppler-windows/releases "
            f"và giải nén vào {POPPLER_PATH}"
        )

    image_paths = []
    for i, page_img in enumerate(pages):
        img_path = os.path.join(output_dir, f'page_{i + 1:03d}.png')
        page_img.save(img_path, 'PNG')
        page_img.close()
        image_paths.append(img_path)

    return image_paths


# ---------------------------------------------------------------------------
# 7. Xử lý file chính: ưu tiên text trực tiếp, fallback sang OCR
# ---------------------------------------------------------------------------
def process_file(file_path, ext):
    """
    Điều phối xử lý file:
    - PDF có text selectable → pdfplumber (chính xác, giữ đúng cấu trúc bảng)
    - PDF scan / ảnh → Tesseract OCR (fallback)

    Returns:
        list[str]: Danh sách văn bản đã làm sạch, mỗi phần tử là một trang.
    """
    ext = ext.lower()

    if ext == '.pdf':
        # Thử trích xuất trực tiếp trước (nhanh hơn, chính xác hơn OCR)
        direct_texts = _extract_pdf_text_direct(file_path)
        if direct_texts is not None:
            return [_join_broken_lines(t) for t in direct_texts]

        # Fallback: PDF là ảnh scan → dùng OCR
        with tempfile.TemporaryDirectory() as tmp_img_dir:
            image_paths = _pdf_to_image_paths(file_path, tmp_img_dir)
            if not image_paths:
                return ['(Không đọc được trang nào từ file PDF này)']
            texts = [_join_broken_lines(_ocr_image_file(p)) for p in image_paths]
        return texts

    else:
        # File ảnh → OCR trực tiếp
        text = _join_broken_lines(_ocr_image_file(file_path))
        return [text]


# ---------------------------------------------------------------------------
# 7. Tạo file Word từ kết quả OCR
# ---------------------------------------------------------------------------
def build_docx(page_texts, source_filename):
    """
    Tạo tài liệu Word từ danh sách văn bản OCR.
    Mỗi đoạn văn (phân cách bằng dòng trống) là một paragraph riêng trong Word.

    Args:
        page_texts (list[str]): Văn bản đã làm sạch của từng trang.
        source_filename (str): Tên file gốc (dùng trong tiêu đề tài liệu).

    Returns:
        bytes: Nội dung file .docx dạng bytes.
    """
    doc = Document()

    title = doc.add_heading(f'Kết quả OCR: {source_filename}', level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    total_pages = len(page_texts)
    for i, text in enumerate(page_texts, start=1):
        if total_pages > 1:
            doc.add_heading(f'Trang {i}', level=2)

        if not text:
            doc.add_paragraph('(Không trích xuất được văn bản từ trang này)')
        else:
            # Tách theo đoạn văn (dòng trống), thêm từng đoạn thành paragraph riêng
            paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
            for para_text in paragraphs:
                para = doc.add_paragraph(para_text)
                for run in para.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(13)

        if i < total_pages:
            doc.add_page_break()

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

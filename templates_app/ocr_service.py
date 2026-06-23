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
    Chuẩn hóa ảnh trước khi OCR.

    Xử lý watermark ảnh (bán trong suốt):
    - Contrast 2.5× (tăng từ 1.8) làm chữ mờ/watermark nhạt biến mất
    - Nhị phân hóa (binarize) với ngưỡng 155/255:
        pixel < 155 → đen (chữ thật, đậm)
        pixel ≥ 155 → trắng (nền, watermark nhạt màu)
    Watermark in đậm/cùng màu với chữ không thể loại bằng cách này
    vì không phân biệt được về mặt cường độ pixel.
    """
    img = img.convert('L')

    w, h = img.size
    if w < 1500:
        scale = 1500 / w
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    # Tăng contrast mạnh hơn: watermark mờ nhạt màu (gray) → trắng
    img = ImageEnhance.Contrast(img).enhance(2.5)

    # Nhị phân hóa: loại bỏ watermark bán trong suốt còn sót lại
    img = img.point(lambda x: 0 if x < 155 else 255)

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
                # Lọc bỏ ký tự bị xoay nghiêng (watermark chéo 45° trong PDF)
                # Watermark dạng text layer thường có upright=False (xoay ~45°)
                page_clean = page.filter(
                    lambda obj: obj.get('object_type') != 'char'
                    or obj.get('upright', True)
                )
                text = page_clean.extract_text(x_tolerance=3, y_tolerance=3) or ''
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
# 6. Đếm trang PDF bằng pypdf (pure Python, không cần Poppler)
# ---------------------------------------------------------------------------
def _count_pdf_pages(pdf_path):
    """
    Đếm số trang PDF dùng pypdf (không cần pdfinfo/Poppler).
    Trả về None nếu không đọc được (PDF lỗi/mã hoá).
    """
    try:
        from pypdf import PdfReader
        return len(PdfReader(pdf_path).pages)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 7. Chuyển PDF sang ảnh để OCR (fallback cho PDF scan)
# ---------------------------------------------------------------------------
_PDF_BATCH_SIZE = 5   # Số trang xử lý mỗi lượt — giữ RAM ổn định
_PDF_DPI_SHORT  = 180 # DPI cho PDF ≤10 trang
_PDF_DPI_LONG   = 150 # DPI cho PDF dài — đủ chính xác, nhanh hơn


def _pdf_to_image_paths(pdf_path, output_dir):
    """
    Chuyển từng trang PDF thành ảnh PNG, xử lý theo batch để tránh tràn RAM.

    Chiến lược fallback khi gặp PDFPageCountError:
    1. Thử dùng pdftocairo (thay vì pdftoppm mặc định) — ổn định hơn
       với PDF không chuẩn, password-protect nhẹ, đường dẫn đặc biệt.
    2. Nếu vẫn lỗi → bỏ qua batch đó, tiếp tục batch tiếp theo.

    Returns:
        list[str]: Danh sách đường dẫn ảnh theo thứ tự trang.
    """
    try:
        from pdf2image import convert_from_path
        from pdf2image.exceptions import PDFInfoNotInstalledError, PDFPageCountError
    except ImportError:
        raise ImportError(
            "Thư viện pdf2image chưa được cài đặt. Chạy: pip install pdf2image"
        )

    poppler_path = POPPLER_PATH if os.path.isdir(POPPLER_PATH) else None

    # Đếm trang bằng pypdf trước — tránh phụ thuộc vào pdfinfo
    total = _count_pdf_pages(pdf_path)
    last_page = min(total, MAX_PDF_PAGES) if total else MAX_PDF_PAGES
    dpi = _PDF_DPI_SHORT if last_page <= 10 else _PDF_DPI_LONG

    image_paths = []

    for batch_start in range(1, last_page + 1, _PDF_BATCH_SIZE):
        batch_end = min(batch_start + _PDF_BATCH_SIZE - 1, last_page)

        pages = _convert_batch(
            pdf_path, batch_start, batch_end, dpi, output_dir, poppler_path
        )
        if pages is None:
            continue  # Batch lỗi → bỏ qua, không crash toàn bộ

        for i, page_img in enumerate(pages):
            page_num = batch_start + i
            img_path = os.path.join(output_dir, f'page_{page_num:03d}.png')
            page_img.save(img_path, 'PNG')
            page_img.close()
            image_paths.append(img_path)

    return sorted(image_paths)


def _convert_batch(pdf_path, first, last, dpi, output_dir, poppler_path):
    """
    Chuyển một batch trang PDF sang ảnh.
    Thử pdftocairo trước, fallback sang pdftoppm, trả None nếu cả hai đều lỗi.
    """
    from pdf2image import convert_from_path
    from pdf2image.exceptions import PDFInfoNotInstalledError, PDFPageCountError

    common = dict(
        dpi=dpi,
        output_folder=output_dir,
        fmt='png',
        first_page=first,
        last_page=last,
        poppler_path=poppler_path,
        grayscale=True,  # Tiết kiệm RAM, Tesseract cũng cần grayscale
    )

    # Lần thử 1: dùng pdftocairo (không gọi pdfinfo → tránh PDFPageCountError)
    try:
        return convert_from_path(pdf_path, use_pdftocairo=True, **common)
    except PDFInfoNotInstalledError:
        raise RuntimeError(
            f"Poppler chưa được cài đặt hoặc không tìm thấy tại {POPPLER_PATH}. "
            "Tải tại: https://github.com/oschwartz10612/poppler-windows/releases"
        )
    except Exception:
        pass

    # Lần thử 2: pdftoppm (mặc định)
    try:
        return convert_from_path(pdf_path, use_pdftocairo=False, **common)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 8. Xử lý file chính: ưu tiên text trực tiếp, fallback sang OCR
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
# 9. Tạo file Word từ kết quả OCR
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

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
def _otsu_threshold(img):
    """
    Tính ngưỡng Otsu từ histogram ảnh grayscale (pure Python, không cần numpy).
    Otsu tìm ngưỡng tối ưu phân tách chữ (tối) và nền + watermark (sáng hơn).
    Trả về giá trị ngưỡng 0-255.
    """
    hist = img.histogram()          # 256 bucket, bucket[i] = số pixel có giá trị i
    total = sum(hist)
    if total == 0:
        return 128

    sum_total = sum(i * h for i, h in enumerate(hist))
    sum_bg = weight_bg = 0
    best_thresh = best_var = 0

    for t in range(256):
        weight_bg += hist[t]
        if weight_bg == 0 or weight_bg == total:
            continue
        weight_fg = total - weight_bg
        sum_bg += t * hist[t]
        mean_bg = sum_bg / weight_bg
        mean_fg = (sum_total - sum_bg) / weight_fg
        var = weight_bg * weight_fg * (mean_bg - mean_fg) ** 2
        if var > best_var:
            best_var, best_thresh = var, t

    return best_thresh


def _preprocess_image(img):
    """
    Chuẩn hóa ảnh trước khi OCR.

    Xử lý watermark:
    - Ngưỡng Otsu thay vì cố định: tự thích ứng với từng trang (sáng/tối khác nhau).
    - Đẩy ngưỡng lên thêm +20 để loại watermark tương đối tối (ví dụ: con dấu mờ,
      chữ stamp xám đậm). Watermark in đậm cùng màu chữ thật không thể loại được.
    """
    img = img.convert('L')

    w, h = img.size
    if w < 1500:
        scale = 1500 / w
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    img = ImageEnhance.Contrast(img).enhance(2.5)

    # Ngưỡng Otsu + bias +20 để loại watermark xám còn sót
    thresh = min(_otsu_threshold(img) + 20, 210)
    img = img.point(lambda x: 0 if x < thresh else 255)

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

        # Lần 1: PSM 3 — tự động phân tích layout (tốt cho văn bản đa cột)
        text = pytesseract.image_to_string(img, lang=OCR_LANG, config=OCR_CONFIG)
        text = text.strip()

        # Nếu PSM 3 cho ít ký tự (trang bảng biểu, layout phức tạp) → thử PSM 6
        # PSM 6: coi toàn bộ trang là một khối văn bản đồng nhất — tốt hơn cho bảng
        if len(text) < 80:
            cfg6 = OCR_CONFIG.replace('--psm 3', '--psm 6')
            text2 = pytesseract.image_to_string(img, lang=OCR_LANG, config=cfg6).strip()
            if len(text2) > len(text):
                text = text2

        return text
    finally:
        if img:
            img.close()


# ---------------------------------------------------------------------------
# 5. Trích xuất text từ PDF có text selectable (không cần OCR)
# ---------------------------------------------------------------------------
# Ngưỡng tối thiểu: nếu trung bình mỗi trang ít hơn 50 ký tự thì coi là PDF scan
_MIN_CHARS_PER_PAGE = 50


def _extract_pdf_text_direct(pdf_path, _diag=None):
    """
    Dùng pdfplumber để đọc text trực tiếp từ PDF có text selectable.
    Tốt hơn nhiều so với OCR cho tài liệu chứa bảng biểu, cột, ký tự đặc biệt.

    _diag: nếu truyền vào list, sẽ thu thập thông báo lỗi để chẩn đoán.

    Returns:
        list[str] nếu PDF có text (một phần tử = một trang),
        None nếu PDF là ảnh scan hoặc pdfplumber chưa cài.
    """
    try:
        import pdfplumber
    except ImportError:
        if _diag is not None:
            _diag.append('pdfplumber chưa được cài đặt')
        return None

    texts = []
    good_pages = 0
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:MAX_PDF_PAGES]:
                try:
                    # Lọc watermark dạng ký tự xoay nghiêng (upright=False ~ 45°)
                    page_clean = page.filter(
                        lambda obj: obj.get('object_type') != 'char'
                        or obj.get('upright', True)
                    )
                    text = page_clean.extract_text(x_tolerance=3, y_tolerance=3) or ''
                    # Một số PDF lưu upright=False cho tất cả chars (khác bản pdfplumber) →
                    # filter xoá hết text thật. Fallback về đọc thẳng nếu kết quả rỗng.
                    if not text.strip():
                        text = page.extract_text(x_tolerance=3, y_tolerance=3) or ''
                except Exception as filter_exc:
                    # filter() không tương thích hoặc lỗi cấu trúc PDF → đọc thẳng không lọc
                    if _diag is not None:
                        _diag.append(f'page.filter() lỗi: {filter_exc}')
                    try:
                        text = page.extract_text(x_tolerance=3, y_tolerance=3) or ''
                    except Exception:
                        text = ''
                text = text.strip()
                texts.append(text)
                if len(text) >= _MIN_CHARS_PER_PAGE:
                    good_pages += 1
    except Exception as exc:
        if _diag is not None:
            _diag.append(f'pdfplumber.open() lỗi: {exc}')
        return None

    min_good = max(1, len(texts) // 3)
    if good_pages < min_good:
        if _diag is not None:
            _diag.append(
                f'pdfplumber trả về quá ít text: {good_pages}/{len(texts)} trang đủ ký tự '
                f'(cần ít nhất {min_good})'
            )
        return None

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


def _pdf_to_image_paths(pdf_path, output_dir, _diag=None):
    """
    Chuyển từng trang PDF thành ảnh PNG cho OCR.

    Ưu tiên PyMuPDF (fitz) — không cần cài Poppler, MuPDF bundled trong wheel.
    Fallback sang pdf2image+Poppler nếu PyMuPDF chưa được cài.

    Returns:
        list[str]: Danh sách đường dẫn ảnh theo thứ tự trang.
    """
    try:
        import fitz  # PyMuPDF
        return _pdf_to_images_pymupdf(pdf_path, output_dir, _diag)
    except ImportError:
        if _diag is not None:
            _diag.append('PyMuPDF chưa cài, thử pdf2image+Poppler')

    return _pdf_to_images_pdf2image(pdf_path, output_dir, _diag)


def _pdf_to_images_pymupdf(pdf_path, output_dir, _diag=None):
    """
    Dùng PyMuPDF (fitz) render PDF → ảnh grayscale PNG.
    Không cần Poppler hay bất kỳ binary ngoài nào.
    """
    import fitz

    total = _count_pdf_pages(pdf_path)
    n_pages = min(total, MAX_PDF_PAGES) if total else MAX_PDF_PAGES
    dpi = _PDF_DPI_SHORT if n_pages <= 10 else _PDF_DPI_LONG
    scale = dpi / 72  # fitz dùng 72 dpi làm cơ sở

    image_paths = []
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        if _diag is not None:
            _diag.append(f'PyMuPDF không mở được PDF: {e}')
        return []

    try:
        for i in range(min(len(doc), MAX_PDF_PAGES)):
            page = doc[i]
            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat, colorspace=fitz.csGRAY)
            img_path = os.path.join(output_dir, f'page_{i + 1:03d}.png')
            pix.save(img_path)
            pix = None  # giải phóng bộ nhớ
            image_paths.append(img_path)
    except Exception as e:
        if _diag is not None:
            _diag.append(f'PyMuPDF render lỗi: {type(e).__name__}: {e}')
    finally:
        doc.close()

    return sorted(image_paths)


def _pdf_to_images_pdf2image(pdf_path, output_dir, _diag=None):
    """
    Fallback dùng pdf2image + Poppler khi PyMuPDF chưa cài.
    Xử lý theo batch để tránh tràn RAM với PDF dài.
    """
    try:
        from pdf2image import convert_from_path
        from pdf2image.exceptions import PDFInfoNotInstalledError, PDFPageCountError
    except ImportError:
        raise ImportError("Thư viện pdf2image chưa được cài đặt.")

    poppler_path = POPPLER_PATH if os.path.isdir(POPPLER_PATH) else None
    if _diag is not None:
        _diag.append(
            f'pdf2image | Poppler: "{POPPLER_PATH}" — '
            + ('tìm thấy' if poppler_path else 'KHÔNG TÌM THẤY')
        )

    total = _count_pdf_pages(pdf_path)
    last_page = min(total, MAX_PDF_PAGES) if total else MAX_PDF_PAGES
    dpi = _PDF_DPI_SHORT if last_page <= 10 else _PDF_DPI_LONG

    image_paths = []

    for batch_start in range(1, last_page + 1, _PDF_BATCH_SIZE):
        batch_end = min(batch_start + _PDF_BATCH_SIZE - 1, last_page)
        pages = _convert_batch_pdf2image(
            pdf_path, batch_start, batch_end, dpi, output_dir, poppler_path, _diag
        )
        if pages is None:
            continue

        for j, page_img in enumerate(pages):
            page_num = batch_start + j
            img_path = os.path.join(output_dir, f'page_{page_num:03d}.png')
            page_img.save(img_path, 'PNG')
            page_img.close()
            image_paths.append(img_path)

    return sorted(image_paths)


def _convert_batch_pdf2image(pdf_path, first, last, dpi, output_dir, poppler_path, _diag=None):
    """Chuyển một batch trang qua pdf2image, thử pdftocairo rồi pdftoppm."""
    from pdf2image import convert_from_path
    from pdf2image.exceptions import PDFInfoNotInstalledError, PDFPageCountError

    common = dict(
        dpi=dpi,
        output_folder=output_dir,
        fmt='png',
        first_page=first,
        last_page=last,
        poppler_path=poppler_path,
        grayscale=True,
    )

    try:
        return convert_from_path(pdf_path, use_pdftocairo=True, **common)
    except PDFInfoNotInstalledError:
        raise RuntimeError(
            f"Poppler không tìm thấy tại {POPPLER_PATH}. "
            "Cài PyMuPDF (pip install PyMuPDF) để không cần Poppler."
        )
    except Exception as e:
        if _diag is not None:
            _diag.append(f'pdftocairo {first}-{last}: {type(e).__name__}: {e}')

    try:
        return convert_from_path(pdf_path, use_pdftocairo=False, **common)
    except Exception as e:
        if _diag is not None:
            _diag.append(f'pdftoppm {first}-{last}: {type(e).__name__}: {e}')
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
        # Thu thập thông tin chẩn đoán để hiển thị khi thất bại
        diag = []

        # Thử trích xuất trực tiếp trước (nhanh hơn, chính xác hơn OCR)
        direct_texts = _extract_pdf_text_direct(file_path, diag)
        if direct_texts is not None:
            return [_join_broken_lines(t) for t in direct_texts]

        # Fallback: PDF là ảnh scan → dùng OCR
        with tempfile.TemporaryDirectory() as tmp_img_dir:
            image_paths = _pdf_to_image_paths(file_path, tmp_img_dir, diag)
            if not image_paths:
                diag_str = ' | '.join(diag) if diag else 'không có thông tin bổ sung'
                return [f'(Không đọc được trang nào từ file PDF này. Chẩn đoán: {diag_str})']
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

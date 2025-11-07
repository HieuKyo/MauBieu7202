"""
Utility để thay thế biến trong file Word template
Thay thế cho docxtpl do vấn đề cài đặt dependency
"""
import re
from docx import Document
from io import BytesIO
from jinja2 import Environment, BaseLoader, TemplateSyntaxError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


def number_format(value):
    """
    Custom Jinja2 filter để format số tiền theo định dạng Việt Nam
    Ví dụ: 165000 -> 165,000
    """
    try:
        return "{:,}".format(int(value))
    except (ValueError, TypeError):
        return value


def date_diff_years(date1, date2):
    """
    Tính số năm giữa 2 ngày
    """
    if not date1 or not date2:
        return 0
    if isinstance(date1, str):
        date1 = datetime.strptime(date1, '%Y-%m-%d').date()
    if isinstance(date2, str):
        date2 = datetime.strptime(date2, '%Y-%m-%d').date()
    return relativedelta(date2, date1).years


def date_diff_days(date1, date2):
    """
    Tính số ngày giữa 2 ngày
    """
    if not date1 or not date2:
        return 0
    if isinstance(date1, str):
        date1 = datetime.strptime(date1, '%Y-%m-%d').date()
    if isinstance(date2, str):
        date2 = datetime.strptime(date2, '%Y-%m-%d').date()
    return (date2 - date1).days


class JinjaWordTemplateProcessor:
    """
    Xử lý template Word với hỗ trợ đầy đủ Jinja2 syntax
    Hỗ trợ: {{ variable }}, {% if %}, {% set %}, filters, expressions, v.v.
    """

    def __init__(self, template_path):
        """
        Khởi tạo processor với đường dẫn template

        Args:
            template_path: Đường dẫn đến file .docx template
        """
        self.document = Document(template_path)
        # Thiết lập Jinja2 environment với custom filters
        self.jinja_env = Environment(loader=BaseLoader())
        self.jinja_env.filters['number_format'] = number_format
        self.jinja_env.filters['date_diff_years'] = date_diff_years
        self.jinja_env.filters['date_diff_days'] = date_diff_days

    def render(self, context):
        """
        Render template với Jinja2 syntax đầy đủ

        Args:
            context: Dictionary chứa các biến và dữ liệu

        Returns:
            Document object đã được render
        """
        # Thêm Date object cho calculations nếu chưa có
        # NOTE: ngay_hien_tai (string dd/mm/yyyy) đã có trong GlobalConfig.get_all_variables()
        if 'ngay_hien_tai_obj' not in context:
            context['ngay_hien_tai_obj'] = datetime.now().date()

        # Process paragraphs
        for paragraph in self.document.paragraphs:
            self._render_paragraph(paragraph, context)

        # Process tables
        for table in self.document.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        self._render_paragraph(paragraph, context)

        # Process headers
        for section in self.document.sections:
            for paragraph in section.header.paragraphs:
                self._render_paragraph(paragraph, context)

            # Process footers
            for paragraph in section.footer.paragraphs:
                self._render_paragraph(paragraph, context)

        # Process Content Control checkboxes
        self._render_content_control_checkboxes(context)

        # Process Content Control textboxes
        self._render_content_control_textboxes(context)

        return self.document

    def _render_paragraph(self, paragraph, context):
        """
        Render một paragraph với Jinja2

        Args:
            paragraph: Paragraph object
            context: Dictionary chứa các biến
        """
        full_text = paragraph.text

        # Kiểm tra nếu có Jinja2 syntax
        if not ('{%' in full_text or '{{' in full_text):
            return

        try:
            # Render text qua Jinja2
            template = self.jinja_env.from_string(full_text)
            rendered_text = template.render(context)

            # Replace text trong paragraph (giữ formatting của run đầu tiên)
            # Xóa tất cả runs
            for run in paragraph.runs:
                run.text = ''

            # Thêm text mới vào run đầu tiên
            if paragraph.runs:
                paragraph.runs[0].text = rendered_text
            else:
                paragraph.add_run(rendered_text)

        except TemplateSyntaxError as e:
            # Nếu có lỗi syntax, giữ nguyên text và thêm warning
            print(f"Jinja2 syntax error in paragraph: {e}")
            # Giữ nguyên text gốc

    def _render_content_control_checkboxes(self, context):
        """
        Render Content Control checkboxes trong document
        Tìm tất cả checkbox có Tag và set trạng thái dựa vào context

        Hỗ trợ nhiều loại giá trị:
        - Boolean: True/False
        - String: '☑'/'☐'
        - Integer: 1/0

        Args:
            context: Dictionary chứa các biến checkbox
        """
        # Namespace cho Word XML
        NSMAP = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'w14': 'http://schemas.microsoft.com/office/word/2010/wordml'
        }

        def parse_checkbox_value(value):
            """
            Parse giá trị checkbox từ nhiều định dạng
            Returns: True nếu checked, False nếu unchecked
            """
            if isinstance(value, bool):
                return value
            elif isinstance(value, str):
                # Unicode checkbox characters
                if value == '☑':
                    return True
                elif value == '☐':
                    return False
                # String representation
                elif value.lower() in ('true', 'yes', '1', 'checked'):
                    return True
                else:
                    return False
            elif isinstance(value, (int, float)):
                return value != 0
            else:
                return False

        # Count checkboxes processed
        checkboxes_updated = 0

        # Tìm tất cả Structured Document Tags (Content Controls)
        for sdt in self.document.element.findall('.//w:sdt', namespaces=NSMAP):
            # Lấy tag name từ properties
            tag_element = sdt.find('.//w:tag', namespaces=NSMAP)
            if tag_element is None:
                continue

            tag_name = tag_element.get(f'{{{NSMAP["w"]}}}val')
            if not tag_name:
                continue

            # Kiểm tra xem tag có trong context không
            if tag_name not in context:
                continue

            # Parse giá trị checkbox
            value = context[tag_name]
            is_checked = parse_checkbox_value(value)

            # Tìm checkbox element trong Content Control
            # Checkbox có thể là w14:checkbox hoặc w:sym (Wingdings)

            # Phương pháp 1: Word 2010+ checkbox (w14:checkbox)
            checkbox_element = sdt.find('.//w14:checkbox', namespaces=NSMAP)
            if checkbox_element is not None:
                # Tìm checked state element
                checked_element = checkbox_element.find('.//w14:checked', namespaces=NSMAP)
                if checked_element is not None:
                    # Set giá trị: 1 = checked, 0 = unchecked
                    checked_element.set(f'{{{NSMAP["w14"]}}}val', '1' if is_checked else '0')
                    checkboxes_updated += 1
                continue

            # Phương pháp 2: Legacy checkbox sử dụng Wingdings font
            sym_element = sdt.find('.//w:sym', namespaces=NSMAP)
            if sym_element is not None:
                # Wingdings font codes:
                # F0FE (&#xF0FE;) = checked box ☑
                # F0A3 (&#xF0A3;) = unchecked box ☐
                char_code = 'F0FE' if is_checked else 'F0A3'
                sym_element.set(f'{{{NSMAP["w"]}}}char', char_code)
                checkboxes_updated += 1

        # Debug: print số checkboxes đã update
        if checkboxes_updated > 0:
            print(f"[DEBUG] Updated {checkboxes_updated} checkboxes")

    def _render_content_control_textboxes(self, context):
        """
        Render Content Control textboxes (Plain Text, Rich Text, etc.) trong document
        Tìm tất cả Content Control có Tag và điền text từ context

        Args:
            context: Dictionary chứa các biến textbox
        """
        # Namespace cho Word XML
        NSMAP = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'w14': 'http://schemas.microsoft.com/office/word/2010/wordml'
        }

        # Count textboxes processed
        textboxes_updated = 0

        # Tìm tất cả Structured Document Tags (Content Controls)
        for sdt in self.document.element.findall('.//w:sdt', namespaces=NSMAP):
            # Lấy tag name từ properties
            tag_element = sdt.find('.//w:tag', namespaces=NSMAP)
            if tag_element is None:
                continue

            tag_name = tag_element.get(f'{{{NSMAP["w"]}}}val')
            if not tag_name:
                continue

            # Kiểm tra xem tag có trong context không
            if tag_name not in context:
                continue

            # Kiểm tra xem đây có phải là checkbox không (skip nếu là checkbox)
            checkbox_element = sdt.find('.//w14:checkbox', namespaces=NSMAP)
            sym_element = sdt.find('.//w:sym', namespaces=NSMAP)
            if checkbox_element is not None or sym_element is not None:
                # Đây là checkbox, skip (đã xử lý ở _render_content_control_checkboxes)
                continue

            # Lấy giá trị từ context
            value = context[tag_name]

            # Convert to string
            if value is None:
                value = ''
            else:
                value = str(value)

            # Tìm tất cả text elements (w:t) trong Content Control
            # Content Control có structure: w:sdt -> w:sdtContent -> w:p -> w:r -> w:t
            text_elements = sdt.findall('.//w:t', namespaces=NSMAP)

            if text_elements:
                # Nếu có text elements, update text element đầu tiên và xóa các text elements khác
                text_elements[0].text = value

                # Xóa text của các elements còn lại (nếu có)
                for text_elem in text_elements[1:]:
                    text_elem.text = ''

                textboxes_updated += 1
            else:
                # Nếu không có text element nào, log warning
                print(f"[WARNING] Content Control '{tag_name}' không có text element")

        # Debug: print số textboxes đã update
        if textboxes_updated > 0:
            print(f"[DEBUG] Updated {textboxes_updated} textboxes")

    def save(self, output_path):
        """
        Lưu document đã render ra file

        Args:
            output_path: Đường dẫn file output
        """
        self.document.save(output_path)

    def save_to_stream(self):
        """
        Lưu document vào BytesIO stream

        Returns:
            BytesIO object chứa nội dung file Word
        """
        stream = BytesIO()
        self.document.save(stream)
        stream.seek(0)
        return stream


class WordTemplateProcessor:
    """
    Xử lý template Word với cú pháp Jinja2 đơn giản
    Hỗ trợ: {{ variable_name }}
    """

    def __init__(self, template_path):
        """
        Khởi tạo processor với đường dẫn template

        Args:
            template_path: Đường dẫn đến file .docx template
        """
        self.document = Document(template_path)

    def render(self, context):
        """
        Thay thế tất cả biến trong document với giá trị từ context

        Args:
            context: Dictionary chứa các cặp key-value để thay thế

        Returns:
            Document object đã được render
        """
        # Thay thế trong paragraphs
        for paragraph in self.document.paragraphs:
            self._replace_in_paragraph(paragraph, context)

        # Thay thế trong tables
        for table in self.document.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        self._replace_in_paragraph(paragraph, context)

        # Thay thế trong headers
        for section in self.document.sections:
            for paragraph in section.header.paragraphs:
                self._replace_in_paragraph(paragraph, context)

            # Thay thế trong footers
            for paragraph in section.footer.paragraphs:
                self._replace_in_paragraph(paragraph, context)

        return self.document

    def _replace_in_paragraph(self, paragraph, context):
        """
        Thay thế biến trong một paragraph

        Args:
            paragraph: Paragraph object
            context: Dictionary chứa các cặp key-value
        """
        # Lấy toàn bộ text của paragraph
        full_text = paragraph.text

        # Tìm tất cả các biến dạng {{ variable }}
        pattern = r'\{\{\s*(\w+)\s*\}\}'
        matches = re.finditer(pattern, full_text)

        # Nếu không có biến nào, return
        if not list(re.finditer(pattern, full_text)):
            return

        # Tạo text mới với các biến đã được thay thế
        new_text = full_text
        for match in re.finditer(pattern, full_text):
            var_name = match.group(1)
            var_value = context.get(var_name, f'[{var_name}]')  # Nếu không tìm thấy, giữ nguyên trong []
            new_text = new_text.replace(match.group(0), str(var_value))

        # Xóa tất cả runs hiện tại
        for run in paragraph.runs:
            run.text = ''

        # Thêm text mới vào run đầu tiên (hoặc tạo mới nếu không có)
        if paragraph.runs:
            paragraph.runs[0].text = new_text
        else:
            paragraph.add_run(new_text)

    def save(self, output_path):
        """
        Lưu document đã render ra file

        Args:
            output_path: Đường dẫn file output
        """
        self.document.save(output_path)

    def save_to_stream(self):
        """
        Lưu document vào BytesIO stream

        Returns:
            BytesIO object chứa nội dung file Word
        """
        stream = BytesIO()
        self.document.save(stream)
        stream.seek(0)
        return stream


def detect_jinja2_syntax(template_path):
    """
    Kiểm tra xem template có sử dụng Jinja2 advanced syntax không
    ({% if %}, {% set %}, {% for %}, etc.)

    Args:
        template_path: Đường dẫn đến file template

    Returns:
        True nếu template có Jinja2 advanced syntax, False nếu chỉ có {{ }}
    """
    doc = Document(template_path)

    # Kiểm tra trong paragraphs
    for paragraph in doc.paragraphs:
        if '{%' in paragraph.text:
            return True

    # Kiểm tra trong tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    if '{%' in paragraph.text:
                        return True

    # Kiểm tra trong headers và footers
    for section in doc.sections:
        for paragraph in section.header.paragraphs:
            if '{%' in paragraph.text:
                return True
        for paragraph in section.footer.paragraphs:
            if '{%' in paragraph.text:
                return True

    return False


def render_word_template(template_path, context, use_jinja=None):
    """
    Hàm tiện ích để render template Word một cách nhanh chóng
    Tự động detect và chọn processor phù hợp (Jinja2 hoặc simple)

    Args:
        template_path: Đường dẫn đến file template .docx
        context: Dictionary chứa các biến cần thay thế
        use_jinja: None (auto-detect), True (force Jinja2), False (force simple)

    Returns:
        BytesIO object chứa file Word đã render

    Example:
        >>> context = {'ho_ten': 'Nguyễn Văn A', 'ngay_sinh': '01/01/1990'}
        >>> output_stream = render_word_template('template.docx', context)

        >>> # Force sử dụng Jinja2
        >>> output_stream = render_word_template('template.docx', context, use_jinja=True)
    """
    # Auto-detect nếu không chỉ định
    if use_jinja is None:
        use_jinja = detect_jinja2_syntax(template_path)

    # Chọn processor phù hợp
    if use_jinja:
        processor = JinjaWordTemplateProcessor(template_path)
    else:
        processor = WordTemplateProcessor(template_path)

    processor.render(context)
    return processor.save_to_stream()

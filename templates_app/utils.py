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

        # Process card name tables (tên trên thẻ)
        self._render_card_name_tables(context)

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

            # Replace text trong paragraph, giữ formatting của run có text
            # Tìm run đầu tiên có text không rỗng để giữ formatting
            target_run_index = 0
            for i, run in enumerate(paragraph.runs):
                if run.text.strip():
                    target_run_index = i
                    break

            # Xóa text của tất cả runs
            for run in paragraph.runs:
                run.text = ''

            # Set text mới vào run có text gốc (giữ formatting)
            if paragraph.runs:
                paragraph.runs[target_run_index].text = rendered_text
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

                # IMPORTANT: Cũng phải update text content và font!
                # Lấy thông tin từ checkedState/uncheckedState
                if is_checked:
                    state_element = checkbox_element.find('.//w14:checkedState', namespaces=NSMAP)
                else:
                    state_element = checkbox_element.find('.//w14:uncheckedState', namespaces=NSMAP)

                if state_element is not None:
                    # Lấy character code và font
                    char_code = state_element.get(f'{{{NSMAP["w14"]}}}val')
                    font_name = state_element.get(f'{{{NSMAP["w14"]}}}font')

                    if char_code and font_name:
                        # Convert hex code to character
                        char = chr(int(char_code, 16))

                        # Update text content
                        text_elements = sdt.findall('.//w:t', namespaces=NSMAP)
                        if text_elements:
                            text_elements[0].text = char

                            # Update font in run properties
                            run_element = text_elements[0].getparent()  # w:r
                            if run_element is not None:
                                rPr = run_element.find('.//w:rPr', namespaces=NSMAP)
                                if rPr is not None:
                                    rFonts = rPr.find('.//w:rFonts', namespaces=NSMAP)
                                    if rFonts is not None:
                                        # Update all font attributes
                                        rFonts.set(f'{{{NSMAP["w"]}}}ascii', font_name)
                                        rFonts.set(f'{{{NSMAP["w"]}}}eastAsia', font_name)
                                        rFonts.set(f'{{{NSMAP["w"]}}}hAnsi', font_name)

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

    def _render_card_name_tables(self, context):
        """
        Tìm và điền tên thẻ vào tables (tên trên thẻ)
        Tìm tables có 15+ columns và điền từng ký tự vào từng cell
        Quét cả main body, headers và footers

        Args:
            context: Dictionary chứa biến ten_the_1 và ten_the_2
        """
        # FIX: Get card names from ten_the_1 and ten_the_2
        # These are auto-filled from ten_tieng_anh in views.py
        ten_the_1 = (context.get('ten_the_1') or '').strip().upper()
        ten_the_2 = (context.get('ten_the_2') or '').strip().upper()

        # Fallback to legacy logic if ten_the_1/2 not available
        if not ten_the_1 and not ten_the_2:
            ho_ten_tieng_anh = (context.get('ho_ten_tieng_anh') or '').strip()
            ten_tieng_anh = (context.get('ten_tieng_anh') or '').strip()
            if ho_ten_tieng_anh:
                ten_the_1 = ho_ten_tieng_anh.upper()
            elif ten_tieng_anh:
                ten_the_1 = ten_tieng_anh  # Already uppercase
            else:
                ten_the_1 = (context.get('ho_ten', '') or '').upper()
            ten_the_2 = ten_the_1  # Use same name for both tables

        if not ten_the_1:
            return

        # List to hold card names for tables (first table uses ten_the_1, second uses ten_the_2)
        card_names = [ten_the_1, ten_the_2] if ten_the_2 else [ten_the_1]
        current_card_table_index = 0  # Track which card name table we're on
        tables_filled = 0
        tables_found = []

        def fill_table_with_name(table, card_name, location='body'):
            """Helper function to fill a single table with a specific card name"""
            nonlocal tables_filled
            if not table.rows:
                return False

            num_cols = len(table.columns)
            tables_found.append(f"{location}:{num_cols}cols")

            # Check if this is a card name table (15+ columns)
            if num_cols >= 15:
                # Fill first row with card name characters
                row = table.rows[0]

                # Fill characters, starting from first non-empty or empty cell
                filled_count = 0
                for cell_idx, cell in enumerate(row.cells):
                    if filled_count < len(card_name):
                        # Fill with character
                        cell.text = card_name[filled_count]
                        filled_count += 1
                    else:
                        # Clear remaining cells
                        cell.text = ''

                tables_filled += 1
                return True
            return False

        # Fill tables in main body
        for table in self.document.tables:
            if current_card_table_index < len(card_names):
                if fill_table_with_name(table, card_names[current_card_table_index], 'body'):
                    current_card_table_index += 1

        # Fill tables in headers and footers
        for section in self.document.sections:
            # Headers
            for table in section.header.tables:
                if current_card_table_index < len(card_names):
                    if fill_table_with_name(table, card_names[current_card_table_index], 'header'):
                        current_card_table_index += 1

            # Footers
            for table in section.footer.tables:
                if current_card_table_index < len(card_names):
                    if fill_table_with_name(table, card_names[current_card_table_index], 'footer'):
                        current_card_table_index += 1

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

        # Process Content Control checkboxes (IMPORTANT!)
        self._render_content_control_checkboxes(context)

        # Process Content Control textboxes (IMPORTANT!)
        self._render_content_control_textboxes(context)

        # Process card name tables (tên trên thẻ)
        self._render_card_name_tables(context)

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

        # Tìm run đầu tiên có text không rỗng để giữ formatting
        target_run_index = 0
        for i, run in enumerate(paragraph.runs):
            if run.text.strip():
                target_run_index = i
                break

        # Xóa text của tất cả runs
        for run in paragraph.runs:
            run.text = ''

        # Set text mới vào run có text gốc (giữ formatting)
        if paragraph.runs:
            paragraph.runs[target_run_index].text = new_text
        else:
            paragraph.add_run(new_text)

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

                # IMPORTANT: Cũng phải update text content và font!
                # Lấy thông tin từ checkedState/uncheckedState
                if is_checked:
                    state_element = checkbox_element.find('.//w14:checkedState', namespaces=NSMAP)
                else:
                    state_element = checkbox_element.find('.//w14:uncheckedState', namespaces=NSMAP)

                if state_element is not None:
                    # Lấy character code và font
                    char_code = state_element.get(f'{{{NSMAP["w14"]}}}val')
                    font_name = state_element.get(f'{{{NSMAP["w14"]}}}font')

                    if char_code and font_name:
                        # Convert hex code to character
                        char = chr(int(char_code, 16))

                        # Update text content
                        text_elements = sdt.findall('.//w:t', namespaces=NSMAP)
                        if text_elements:
                            text_elements[0].text = char

                            # Update font in run properties
                            run_element = text_elements[0].getparent()  # w:r
                            if run_element is not None:
                                rPr = run_element.find('.//w:rPr', namespaces=NSMAP)
                                if rPr is not None:
                                    rFonts = rPr.find('.//w:rFonts', namespaces=NSMAP)
                                    if rFonts is not None:
                                        # Update all font attributes
                                        rFonts.set(f'{{{NSMAP["w"]}}}ascii', font_name)
                                        rFonts.set(f'{{{NSMAP["w"]}}}eastAsia', font_name)
                                        rFonts.set(f'{{{NSMAP["w"]}}}hAnsi', font_name)

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

    def _render_card_name_tables(self, context):
        """
        Tìm và điền tên thẻ vào tables (tên trên thẻ)
        Tìm tables có 15+ columns và điền từng ký tự vào từng cell
        Quét cả main body, headers và footers

        Args:
            context: Dictionary chứa biến ten_the_1 và ten_the_2
        """
        # FIX: Get card names from ten_the_1 and ten_the_2
        # These are auto-filled from ten_tieng_anh in views.py
        ten_the_1 = (context.get('ten_the_1') or '').strip().upper()
        ten_the_2 = (context.get('ten_the_2') or '').strip().upper()

        # Fallback to legacy logic if ten_the_1/2 not available
        if not ten_the_1 and not ten_the_2:
            ho_ten_tieng_anh = (context.get('ho_ten_tieng_anh') or '').strip()
            ten_tieng_anh = (context.get('ten_tieng_anh') or '').strip()
            if ho_ten_tieng_anh:
                ten_the_1 = ho_ten_tieng_anh.upper()
            elif ten_tieng_anh:
                ten_the_1 = ten_tieng_anh  # Already uppercase
            else:
                ten_the_1 = (context.get('ho_ten', '') or '').upper()
            ten_the_2 = ten_the_1  # Use same name for both tables

        if not ten_the_1:
            return

        # List to hold card names for tables (first table uses ten_the_1, second uses ten_the_2)
        card_names = [ten_the_1, ten_the_2] if ten_the_2 else [ten_the_1]
        current_card_table_index = 0  # Track which card name table we're on
        tables_filled = 0
        tables_found = []

        def fill_table_with_name(table, card_name, location='body'):
            """Helper function to fill a single table with a specific card name"""
            nonlocal tables_filled
            if not table.rows:
                return False

            num_cols = len(table.columns)
            tables_found.append(f"{location}:{num_cols}cols")

            # Check if this is a card name table (15+ columns)
            if num_cols >= 15:
                # Fill first row with card name characters
                row = table.rows[0]

                # Fill characters, starting from first non-empty or empty cell
                filled_count = 0
                for cell_idx, cell in enumerate(row.cells):
                    if filled_count < len(card_name):
                        # Fill with character
                        cell.text = card_name[filled_count]
                        filled_count += 1
                    else:
                        # Clear remaining cells
                        cell.text = ''

                tables_filled += 1
                return True
            return False

        # Fill tables in main body
        for table in self.document.tables:
            if current_card_table_index < len(card_names):
                if fill_table_with_name(table, card_names[current_card_table_index], 'body'):
                    current_card_table_index += 1

        # Fill tables in headers and footers
        for section in self.document.sections:
            # Headers
            for table in section.header.tables:
                if current_card_table_index < len(card_names):
                    if fill_table_with_name(table, card_names[current_card_table_index], 'header'):
                        current_card_table_index += 1

            # Footers
            for table in section.footer.tables:
                if current_card_table_index < len(card_names):
                    if fill_table_with_name(table, card_names[current_card_table_index], 'footer'):
                        current_card_table_index += 1

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

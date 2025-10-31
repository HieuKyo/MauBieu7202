"""
Utility để thay thế biến trong file Word template
Thay thế cho docxtpl do vấn đề cài đặt dependency
"""
import re
from docx import Document
from io import BytesIO


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


def render_word_template(template_path, context):
    """
    Hàm tiện ích để render template Word một cách nhanh chóng

    Args:
        template_path: Đường dẫn đến file template .docx
        context: Dictionary chứa các biến cần thay thế

    Returns:
        BytesIO object chứa file Word đã render

    Example:
        >>> context = {'ho_ten': 'Nguyễn Văn A', 'ngay_sinh': '01/01/1990'}
        >>> output_stream = render_word_template('template.docx', context)
    """
    processor = WordTemplateProcessor(template_path)
    processor.render(context)
    return processor.save_to_stream()

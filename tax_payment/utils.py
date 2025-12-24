"""
Utility functions cho tax_payment app
"""


def number_to_vietnamese_words(number):
    """
    Chuyển đổi số thành chữ bằng tiếng Việt

    Args:
        number: Số cần chuyển đổi (int hoặc float)

    Returns:
        str: Số bằng chữ (tiếng Việt)

    Example:
        >>> number_to_vietnamese_words(123456)
        'Một trăm hai mươi ba nghìn bốn trăm năm mươi sáu'
    """
    if not isinstance(number, (int, float)):
        try:
            number = int(number)
        except (ValueError, TypeError):
            return ""

    number = int(number)

    if number == 0:
        return "Không"

    if number < 0:
        return "Âm " + number_to_vietnamese_words(-number)

    # Đơn vị
    ones = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]

    # Hàm đọc số có 1 chữ số
    def read_one_digit(n):
        return ones[n]

    # Hàm đọc số có 2 chữ số
    def read_two_digits(n):
        if n < 10:
            return read_one_digit(n)
        elif n == 10:
            return "mười"
        elif n < 20:
            return "mười " + read_one_digit(n % 10)
        else:
            tens = n // 10
            units = n % 10
            result = ones[tens] + " mươi"
            if units == 1:
                result += " mốt"
            elif units == 5 and tens >= 1:
                result += " lăm"
            elif units > 0:
                result += " " + ones[units]
            return result

    # Hàm đọc số có 3 chữ số
    def read_three_digits(n):
        if n < 100:
            return read_two_digits(n)

        hundreds = n // 100
        remainder = n % 100

        result = ones[hundreds] + " trăm"

        if remainder == 0:
            return result
        elif remainder < 10:
            result += " lẻ " + ones[remainder]
        else:
            result += " " + read_two_digits(remainder)

        return result

    # Đơn vị lớn
    units_large = ["", "nghìn", "triệu", "tỷ", "nghìn tỷ", "triệu tỷ"]

    # Chia số thành các nhóm 3 chữ số
    groups = []
    while number > 0:
        groups.append(number % 1000)
        number //= 1000

    # Đọc từng nhóm
    result_parts = []
    for i in range(len(groups) - 1, -1, -1):
        if groups[i] > 0:
            group_text = read_three_digits(groups[i])
            if i > 0:
                group_text += " " + units_large[i]
            result_parts.append(group_text)

    result = " ".join(result_parts)

    # Viết hoa chữ cái đầu
    if result:
        result = result[0].upper() + result[1:]

    return result


def format_currency_vnd(amount):
    """
    Format số tiền theo định dạng VNĐ

    Args:
        amount: Số tiền (int, float, Decimal)

    Returns:
        str: Số tiền đã format (VD: "1.500.000")
    """
    try:
        amount = int(amount)
        return f"{amount:,}".replace(',', '.')
    except (ValueError, TypeError):
        return "0"


# Alias cho tên hàm tiếng Việt
doc_so_thanh_chu = number_to_vietnamese_words


def date_to_vietnamese_text(date_obj):
    """
    Chuyển đổi ngày sang định dạng text tiếng Việt

    Args:
        date_obj: Đối tượng datetime.date hoặc datetime.datetime

    Returns:
        str: Ngày dạng text (VD: "Ngày 24 tháng 12 năm 2025")

    Example:
        >>> from datetime import date
        >>> date_to_vietnamese_text(date(2025, 12, 24))
        'Ngày 24 tháng 12 năm 2025'
    """
    if not date_obj:
        return ""

    try:
        day = date_obj.day
        month = date_obj.month
        year = date_obj.year

        return f"Ngày {day} tháng {month} năm {year}"
    except (AttributeError, ValueError):
        return ""

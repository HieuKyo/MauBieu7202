"""
Hàm xử lý chữ tiếng Việt dùng chung cho các model: bỏ dấu, đọc số thành chữ.
"""


def remove_vietnamese_diacritics(text):
    """
    Loại bỏ dấu tiếng Việt và trả về chữ không dấu
    VD: 'Nguyễn Văn A' -> 'NGUYEN VAN A'
    """
    if not text:
        return ''

    # Vietnamese character mapping
    vietnamese_map = {
        'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'đ': 'd',
        'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
        'À': 'A', 'Á': 'A', 'Ả': 'A', 'Ã': 'A', 'Ạ': 'A',
        'Ă': 'A', 'Ằ': 'A', 'Ắ': 'A', 'Ẳ': 'A', 'Ẵ': 'A', 'Ặ': 'A',
        'Â': 'A', 'Ầ': 'A', 'Ấ': 'A', 'Ẩ': 'A', 'Ẫ': 'A', 'Ậ': 'A',
        'Đ': 'D',
        'È': 'E', 'É': 'E', 'Ẻ': 'E', 'Ẽ': 'E', 'Ẹ': 'E',
        'Ê': 'E', 'Ề': 'E', 'Ế': 'E', 'Ể': 'E', 'Ễ': 'E', 'Ệ': 'E',
        'Ì': 'I', 'Í': 'I', 'Ỉ': 'I', 'Ĩ': 'I', 'Ị': 'I',
        'Ò': 'O', 'Ó': 'O', 'Ỏ': 'O', 'Õ': 'O', 'Ọ': 'O',
        'Ô': 'O', 'Ồ': 'O', 'Ố': 'O', 'Ổ': 'O', 'Ỗ': 'O', 'Ộ': 'O',
        'Ơ': 'O', 'Ờ': 'O', 'Ớ': 'O', 'Ở': 'O', 'Ỡ': 'O', 'Ợ': 'O',
        'Ù': 'U', 'Ú': 'U', 'Ủ': 'U', 'Ũ': 'U', 'Ụ': 'U',
        'Ư': 'U', 'Ừ': 'U', 'Ứ': 'U', 'Ử': 'U', 'Ữ': 'U', 'Ự': 'U',
        'Ỳ': 'Y', 'Ý': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y', 'Ỵ': 'Y',
    }

    result = []
    for char in text:
        if char in vietnamese_map:
            result.append(vietnamese_map[char])
        else:
            result.append(char)

    return ''.join(result).upper()

def num_to_vietnamese_words(num):
    """Chuyển đổi số thành chữ tiếng Việt"""
    if num == 0:
        return "Không đồng"

    units = ["", "nghìn", "triệu", "tỷ"]

    def read_group(n):
        """Đọc nhóm 3 chữ số"""
        hundred = n // 100
        ten = (n % 100) // 10
        unit = n % 10

        result = []

        if hundred > 0:
            result.append(f"{read_digit(hundred)} trăm")

        if ten > 1:
            result.append(f"{read_digit(ten)} mươi")
            if unit == 1:
                result.append("mốt")
            elif unit > 0:
                result.append(read_digit(unit))
        elif ten == 1:
            result.append("mười")
            if unit > 0:
                result.append(read_digit(unit))
        else:
            if hundred > 0 and unit > 0:
                result.append("lẻ")
            if unit > 0:
                result.append(read_digit(unit))

        return " ".join(result)

    def read_digit(d):
        """Đọc một chữ số"""
        digits = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
        return digits[d]

    # Chia số thành các nhóm 3 chữ số
    groups = []
    temp = num
    while temp > 0:
        groups.append(temp % 1000)
        temp //= 1000

    # Đọc từng nhóm
    result = []
    for i in range(len(groups) - 1, -1, -1):
        if groups[i] > 0:
            group_text = read_group(groups[i])
            if i > 0:
                group_text += f" {units[i]}"
            result.append(group_text)

    # Viết hoa chữ cái đầu và thêm "đồng"
    final_result = " ".join(result)
    return final_result.capitalize() + " đồng"

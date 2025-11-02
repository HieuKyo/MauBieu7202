"""
Bảng mapping mã nơi cấp CMND/CCCD từ hệ thống AGRIBANK
"""

ISSUEBY_MAPPING = {
    '145': 'Cục Cảnh sát ĐKQL cư trú và DLQG về dân cư',
    '146': 'Cục CSQLHC về TTXH',
    '001': 'Bộ Công An',
    '002': 'Công an TP Hà Nội',
    '003': 'Công an TP Hồ Chí Minh',
    '004': 'Công an tỉnh An Giang',
    '005': 'Công an tỉnh Bà Rịa - Vũng Tàu',
    '006': 'Công an tỉnh Bắc Giang',
    '007': 'Công an tỉnh Bắc Kạn',
    '008': 'Công an tỉnh Bạc Liêu',
    '009': 'Công an tỉnh Bắc Ninh',
    '010': 'Công an tỉnh Bến Tre',
    '011': 'Công an tỉnh Bình Định',
    '012': 'Công an tỉnh Bình Dương',
    '013': 'Công an tỉnh Bình Phước',
    '014': 'Công an tỉnh Bình Thuận',
    '015': 'Công an tỉnh Cà Mau',
    '016': 'Công an tỉnh Cao Bằng',
    '017': 'Công an tỉnh Đắk Lắk',
    '018': 'Công an tỉnh Đắk Nông',
    '019': 'Công an tỉnh Điện Biên',
    '020': 'Công an tỉnh Đồng Nai',
    '021': 'Công an tỉnh Đồng Tháp',
    '022': 'Công an tỉnh Gia Lai',
    '023': 'Công an tỉnh Hà Giang',
    '024': 'Công an tỉnh Hà Nam',
    '025': 'Công an tỉnh Hà Tĩnh',
    '026': 'Công an tỉnh Hải Dương',
    '027': 'Công an tỉnh Hải Phòng',
    '028': 'Công an tỉnh Hậu Giang',
    '029': 'Công an tỉnh Hòa Bình',
    '030': 'Công an tỉnh Hưng Yên',
    '031': 'Công an tỉnh Khánh Hòa',
    '032': 'Công an tỉnh Kiên Giang',
    '033': 'Công an tỉnh Kon Tum',
    '034': 'Công an tỉnh Lai Châu',
    '035': 'Công an tỉnh Lâm Đồng',
    '036': 'Công an tỉnh Lạng Sơn',
    '037': 'Công an tỉnh Lào Cai',
    '038': 'Công an tỉnh Long An',
    '039': 'Công an tỉnh Nam Định',
    '040': 'Công an tỉnh Nghệ An',
    '041': 'Công an tỉnh Ninh Bình',
    '042': 'Công an tỉnh Ninh Thuận',
    '043': 'Công an tỉnh Phú Thọ',
    '044': 'Công an tỉnh Phú Yên',
    '045': 'Công an tỉnh Quảng Bình',
    '046': 'Công an tỉnh Quảng Nam',
    '047': 'Công an tỉnh Quảng Ngãi',
    '048': 'Công an tỉnh Quảng Ninh',
    '049': 'Công an tỉnh Quảng Trị',
    '050': 'Công an tỉnh Sóc Trăng',
    '051': 'Công an tỉnh Sơn La',
    '052': 'Công an tỉnh Tây Ninh',
    '053': 'Công an tỉnh Thái Bình',
    '054': 'Công an tỉnh Thái Nguyên',
    '055': 'Công an tỉnh Thanh Hóa',
    '056': 'Công an tỉnh Thừa Thiên Huế',
    '057': 'Công an tỉnh Tiền Giang',
    '058': 'Công an tỉnh Trà Vinh',
    '059': 'Công an tỉnh Tuyên Quang',
    '060': 'Công an tỉnh Vĩnh Long',
    '061': 'Công an tỉnh Vĩnh Phúc',
    '062': 'Công an tỉnh Yên Bái',
    '063': 'Công an tỉnh Cần Thơ',
    '064': 'Công an tỉnh Đà Nẵng',
}


def get_issueby_name(code):
    """
    Lấy tên nơi cấp từ mã
    Args:
        code: Mã nơi cấp (str hoặc int)
    Returns:
        Tên nơi cấp (str) hoặc code nếu không tìm thấy
    """
    code_str = str(code).strip()
    return ISSUEBY_MAPPING.get(code_str, f'Mã {code_str}')

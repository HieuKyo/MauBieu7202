"""
Checkbox utilities for handling checkbox conversion between boolean and Unicode characters.

This module provides centralized functions for checkbox value handling, reducing code duplication
across models.py and views.py.
"""

# Checkbox character constants
CHECKBOX_CHECKED = '☑'
CHECKBOX_UNCHECKED = '☐'


def bool_to_checkbox(value):
    """
    Convert boolean value to checkbox character.

    Args:
        value: Boolean, string, or any truthy/falsy value

    Returns:
        str: '☑' for truthy values, '☐' for falsy values

    Examples:
        >>> bool_to_checkbox(True)
        '☑'
        >>> bool_to_checkbox(False)
        '☐'
        >>> bool_to_checkbox('yes')
        '☑'
        >>> bool_to_checkbox('')
        '☐'
    """
    if isinstance(value, str):
        # Handle string values like 'yes', 'no', 'true', 'false'
        value_lower = value.lower().strip()
        return CHECKBOX_CHECKED if value_lower in ('yes', 'true', '1', 'có', CHECKBOX_CHECKED) else CHECKBOX_UNCHECKED

    # Handle boolean and other truthy/falsy values
    return CHECKBOX_CHECKED if value else CHECKBOX_UNCHECKED


def checkbox_to_bool(value):
    """
    Convert checkbox character to boolean.

    Args:
        value: Checkbox character ('☑' or '☐') or any value

    Returns:
        bool: True if checked, False otherwise

    Examples:
        >>> checkbox_to_bool('☑')
        True
        >>> checkbox_to_bool('☐')
        False
        >>> checkbox_to_bool(True)
        True
    """
    if isinstance(value, str):
        return value == CHECKBOX_CHECKED
    return bool(value)


def get_checkbox_display(value):
    """
    Get display-friendly checkbox representation.

    Args:
        value: Any checkbox value (boolean, string, checkbox char)

    Returns:
        str: Checkbox character for display

    Examples:
        >>> get_checkbox_display(True)
        '☑'
        >>> get_checkbox_display('no')
        '☐'
    """
    return bool_to_checkbox(value)


def convert_service_checkboxes(data):
    """
    Convert all service-related boolean fields to checkbox characters.

    This is commonly used for banking service fields like SMS Banking, Agribank Plus, etc.

    Args:
        data: Dictionary containing service fields (modifies in-place)

    Returns:
        dict: The same dictionary with checkbox fields converted

    Example:
        >>> data = {'dv_sms_banking': True, 'dv_bankplus': False}
        >>> convert_service_checkboxes(data)
        {'dv_sms_banking': '☑', 'dv_bankplus': '☐'}
    """
    # List of common service fields that use checkboxes
    service_fields = [
        'dv_sms_banking',
        'dv_bankplus',
        'dv_e_commerce',
        'dv_soft_otp',
        'dv_smart_otp',
        'dv_thu_ho_tien_dien',
        'dv_thu_ho_tien_nuoc',
        'dv_thu_ho_internet',
        'dv_thu_ho_truyen_hinh',
        'dv_thu_ho_dien_thoai',
        'dv_thu_ho_hoc_phi',
        'dv_thu_ho_bao_hiem',
        'dv_thu_ho_khac',
        'dang_ky_internet_banking',
        'dang_ky_mobile_banking',
        'nhan_the_tai_nha',
        'nhan_the_tai_chi_nhanh',
    ]

    for field in service_fields:
        if field in data:
            data[field] = bool_to_checkbox(data[field])

    return data


def batch_convert_checkboxes(fields_dict, field_names):
    """
    Convert multiple fields to checkbox characters in batch.

    Args:
        fields_dict: Dictionary containing the fields (modifies in-place)
        field_names: List of field names to convert

    Returns:
        dict: The same dictionary with specified fields converted

    Example:
        >>> data = {'field1': True, 'field2': False, 'field3': 'yes'}
        >>> batch_convert_checkboxes(data, ['field1', 'field2', 'field3'])
        {'field1': '☑', 'field2': '☐', 'field3': '☑'}
    """
    for field_name in field_names:
        if field_name in fields_dict:
            fields_dict[field_name] = bool_to_checkbox(fields_dict[field_name])

    return fields_dict

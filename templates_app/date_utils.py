"""
Date utilities for parsing and formatting dates.

This module provides centralized date handling functions to reduce code duplication
and improve error handling across the application.
"""

from datetime import datetime


def parse_date_with_fallback(date_string, formats=None):
    """
    Parse date string with multiple format fallbacks.

    Args:
        date_string: String representation of date
        formats: List of date formats to try (optional)

    Returns:
        date object if successful, None otherwise

    Examples:
        >>> parse_date_with_fallback('15/11/2024')
        datetime.date(2024, 11, 15)
        >>> parse_date_with_fallback('2024-11-15')
        datetime.date(2024, 11, 15)
    """
    if not date_string:
        return None

    if formats is None:
        # Default formats to try
        formats = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d']

    for date_format in formats:
        try:
            return datetime.strptime(str(date_string), date_format).date()
        except (ValueError, TypeError):
            continue

    return None


def format_date_with_parts(date_obj):
    """
    Format date object with individual digit parts for template filling.

    Args:
        date_obj: date object or date string

    Returns:
        Dictionary with formatted date and individual digit parts

    Example:
        >>> format_date_with_parts(date(2024, 11, 15))
        {
            'formatted': '15/11/2024',
            'd1': '1', 'd2': '5',
            'm1': '1', 'm2': '1',
            'y1': '2', 'y2': '0', 'y3': '2', 'y4': '4'
        }
    """
    if not date_obj:
        return None

    # Convert string to date if needed
    if isinstance(date_obj, str):
        date_obj = parse_date_with_fallback(date_obj)
        if not date_obj:
            return None

    # Format date
    date_str = date_obj.strftime('%d%m%Y')

    return {
        'formatted': date_obj.strftime('%d/%m/%Y'),
        'd1': date_str[0],
        'd2': date_str[1],
        'm1': date_str[2],
        'm2': date_str[3],
        'y1': date_str[4],
        'y2': date_str[5],
        'y3': date_str[6],
        'y4': date_str[7],
    }


def parse_and_format_date(date_string, input_format='%Y-%m-%d', output_format='%d/%m/%Y'):
    """
    Parse date string and return formatted string and date object.

    Args:
        date_string: Date string to parse
        input_format: Expected input format (default: '%Y-%m-%d')
        output_format: Desired output format (default: '%d/%m/%Y')

    Returns:
        Tuple of (formatted_string, date_object) or (None, None) if parsing fails

    Example:
        >>> parse_and_format_date('2024-11-15')
        ('15/11/2024', datetime.date(2024, 11, 15))
    """
    if not date_string:
        return None, None

    try:
        date_obj = datetime.strptime(date_string, input_format).date()
        formatted = date_obj.strftime(output_format)
        return formatted, date_obj
    except (ValueError, TypeError):
        return None, None


def add_date_parts_to_data(data, date_field_name, prefix=''):
    """
    Add individual date digit parts to data dictionary for a specific date field.

    This is used for template filling where individual date digits are needed
    (e.g., for ID card dates with separate boxes for each digit).

    Args:
        data: Dictionary to modify (modifies in-place)
        date_field_name: Name of the date field in data
        prefix: Prefix for the digit field names (e.g., 'cc' for ngay_cap_cmnd)

    Returns:
        dict: The same dictionary with added digit fields

    Example:
        >>> data = {'ngay_cap_cmnd': '2024-11-15'}
        >>> add_date_parts_to_data(data, 'ngay_cap_cmnd', prefix='cc')
        # Adds: dcc1, dcc2, mcc1, mcc2, ycc1, ycc2, ycc3, ycc4
        # Also converts ngay_cap_cmnd to '15/11/2024' and adds ngay_cap_cmnd_obj
    """
    date_value = data.get(date_field_name)
    if not date_value:
        data[f'{date_field_name}_obj'] = None
        return data

    try:
        # Parse date
        date_obj = datetime.strptime(date_value, '%Y-%m-%d')

        # Store formatted string and date object
        data[date_field_name] = date_obj.strftime('%d/%m/%Y')
        data[f'{date_field_name}_obj'] = date_obj.date()

        # Add individual digit parts
        date_str = date_obj.strftime('%d%m%Y')
        data[f'd{prefix}1'] = date_str[0]
        data[f'd{prefix}2'] = date_str[1]
        data[f'm{prefix}1'] = date_str[2]
        data[f'm{prefix}2'] = date_str[3]
        data[f'y{prefix}1'] = date_str[4]
        data[f'y{prefix}2'] = date_str[5]
        data[f'y{prefix}3'] = date_str[6]
        data[f'y{prefix}4'] = date_str[7]

    except (ValueError, TypeError):
        # Invalid date format - set object to None
        data[f'{date_field_name}_obj'] = None

    return data


def process_birth_date_parts(data):
    """
    Process birth date (ngay_sinh) and add all required parts to data.

    Args:
        data: Dictionary containing 'ngay_sinh' field (modifies in-place)

    Returns:
        dict: Data with added date parts (d1, d2, m1, m2, y1-y4, ngay_sinh_obj)
    """
    return add_date_parts_to_data(data, 'ngay_sinh', prefix='')


def process_issue_date_parts(data):
    """
    Process issue date (ngay_cap_cmnd) and add all required parts to data.

    Args:
        data: Dictionary containing 'ngay_cap_cmnd' field (modifies in-place)

    Returns:
        dict: Data with added date parts (dcc1-dcc2, mcc1-mcc2, ycc1-ycc4, ngay_cap_cmnd_obj)
    """
    return add_date_parts_to_data(data, 'ngay_cap_cmnd', prefix='cc')


def process_expiry_date_parts(data):
    """
    Process expiry date (ngay_het_han_cmnd) and add all required parts to data.

    Args:
        data: Dictionary containing 'ngay_het_han_cmnd' field (modifies in-place)

    Returns:
        dict: Data with added date parts (dhh1-dhh2, mhh1-mhh2, yhh1-yhh4, ngay_het_han_cmnd_obj)
    """
    return add_date_parts_to_data(data, 'ngay_het_han_cmnd', prefix='hh')


def get_current_date_formatted():
    """
    Get current date in Vietnamese format.

    Returns:
        dict: Dictionary with various current date formats

    Example:
        >>> get_current_date_formatted()
        {
            'ngay_hien_tai': '15/11/2024',
            'ngay_hien_tai_obj': datetime.date(2024, 11, 15),
            'ngay': '15',
            'thang': '11',
            'nam': '2024'
        }
    """
    now = datetime.now()
    return {
        'ngay_hien_tai': now.strftime('%d/%m/%Y'),
        'ngay_hien_tai_obj': now.date(),
        'ngay': now.strftime('%d'),
        'thang': now.strftime('%m'),
        'nam': now.strftime('%Y'),
    }

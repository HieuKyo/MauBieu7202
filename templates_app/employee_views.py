"""
Views quản lý nhân viên: danh sách, nhập/xuất Excel, thêm/sửa/xóa thủ công.
"""

# Django imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

# Local application imports
from .models import BranchConfig, AppProgram


# ====================
# Employee Management Views
# ====================

def check_employee_import_permission(user):
    """
    Kiểm tra quyền import nhân viên
    Chỉ Superuser có quyền
    """
    return user.is_superuser


@login_required
def download_employee_template(request):
    """
    Tải về file Excel mẫu để import nhân viên
    """
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    from django.http import HttpResponse

    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Danh sách nhân viên"

    # Define headers (Vietnamese names that the import function looks for)
    headers = [
        'Username',
        'Họ và tên',
        'Mã nhân viên',
        'Ngày sinh',
        'Giới tính',
        'Điện thoại',
        'Địa chỉ',
        'Số CCCD',
        'Ngày cấp CCCD',
        'Nơi cấp CCCD',
        'Chi nhánh',
        'Phòng ban',
        'Chức vụ',
        'Nghiệp vụ',
        'Mã chứng thư số',
        'CTS từ ngày',
        'CTS đến ngày',
        'Tài khoản IPCAS',
        'Địa chỉ MAC',
        'Địa chỉ IP',
        'Phần mềm cấp phép'
    ]

    # Write headers with styling
    header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF', size=11)

    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')

    # Add sample data rows
    sample_data = [
        [
            'nguyenvana',
            'Nguyễn Văn A',
            'NV001',
            '15/01/1990',
            'Nam',
            '0912345678',
            '123 Đường ABC, Phường 1, TP. Bạc Liêu',
            '001234567890',
            '01/01/2020',
            'Cục Cảnh sát ĐKQL cư trú và DLQG về dân cư',
            'HOI_SO',
            'KE_TOAN',
            'TRUONG_PHONG',
            'KIEM_SOAT_VIEN',
            'CTS-NV001-2024',
            '01/01/2024',
            '31/12/2025',
            'nguyenvana_ipcas',
            'AA:BB:CC:DD:EE:01',
            '192.168.1.101',
            'Phần mềm kế toán, Email nội bộ'
        ],
        [
            'tranthib',
            'Trần Thị B',
            'NV002',
            '20/05/1995',
            'Nữ',
            '0987654321',
            '456 Đường XYZ, Phường 2, TP. Bạc Liêu',
            '002345678901',
            '15/03/2021',
            'Cục Cảnh sát ĐKQL cư trú và DLQG về dân cư',
            'PGD_P1',
            'KHACH_HANG',
            'NHAN_VIEN',
            'GIAO_DICH_VIEN',
            'CTS-NV002-2024',
            '15/06/2024',
            '14/06/2025',
            'tranthib_ipcas',
            'AA:BB:CC:DD:EE:02',
            '192.168.1.102',
            'Email nội bộ'
        ],
        [
            'levanc',
            'Lê Văn C',
            'NV003',
            '10/12/1988',
            'Nam',
            '0901234567',
            '789 Đường DEF, Láng Tròn, TP. Bạc Liêu',
            '003456789012',
            '20/07/2019',
            'Cục Cảnh sát ĐKQL cư trú và DLQG về dân cư',
            'PGD_LANG_TRON',
            'TONG_HOP',
            'PHO_PHONG',
            'TONG_HOP_VIEN',
            'CTS-NV003-2023',
            '01/07/2023',
            '30/06/2024',
            '',
            '',
            '',
            ''
        ],
    ]

    for row_idx, row_data in enumerate(sample_data, start=2):
        for col_idx, value in enumerate(row_data, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.alignment = Alignment(horizontal='left', vertical='center')

    # Adjust column widths
    column_widths = [15, 25, 15, 15, 12, 15, 35, 18, 15, 45, 20, 25, 25, 20, 20, 15, 15, 20, 20, 18, 35]
    for col_idx, width in enumerate(column_widths, start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = width

    # Add instruction sheet
    ws_instructions = wb.create_sheet(title="Hướng dẫn")
    instructions = [
        ['HƯỚNG DẪN IMPORT NHÂN VIÊN'],
        [''],
        ['1. Các cột bắt buộc:'],
        ['   - Username: Tên đăng nhập (không trùng)'],
        ['   - Họ và tên: Họ tên đầy đủ'],
        ['   - Mã nhân viên: Mã nhân viên (không trùng)'],
        [''],
        ['2. Thông tin cá nhân (tùy chọn):'],
        ['   - Ngày sinh: Định dạng dd/mm/yyyy (ví dụ: 15/01/1990)'],
        ['   - Giới tính: Nam, Nữ, hoặc Khác'],
        ['   - Điện thoại: Số điện thoại liên hệ'],
        ['   - Địa chỉ: Địa chỉ nơi ở hiện tại'],
        [''],
        ['3. Thông tin CCCD (tùy chọn):'],
        ['   - Số CCCD: Số căn cước công dân (12 chữ số)'],
        ['   - Ngày cấp CCCD: Định dạng dd/mm/yyyy (ví dụ: 01/01/2020)'],
        ['   - Nơi cấp CCCD: Nơi cấp CCCD (ví dụ: Cục Cảnh sát ĐKQL cư trú và DLQG về dân cư)'],
        [''],
        ['4. Thông tin công việc (tùy chọn):'],
        ['   - Chi nhánh: HOI_SO, PGD_P1, PGD_LANG_TRON'],
        ['   - Phòng ban: KE_TOAN, KHACH_HANG, BAN_GIAM_DOC, TONG_HOP'],
        ['   - Chức vụ: GIAM_DOC, PHO_GIAM_DOC, TRUONG_PHONG, PHO_PHONG, GD_PGD, PGD_PGD, NHAN_VIEN'],
        ['   - Nghiệp vụ: GIAO_DICH_VIEN, KIEM_SOAT_VIEN, HAU_KIEM_VIEN, TONG_HOP_VIEN'],
        [''],
        ['5. Thông tin chứng thư số (tùy chọn):'],
        ['   - Mã chứng thư số: Mã số chứng thư (ví dụ: CTS-NV001-2024)'],
        ['   - CTS từ ngày: Ngày bắt đầu hiệu lực, định dạng dd/mm/yyyy'],
        ['   - CTS đến ngày: Ngày hết hạn hiệu lực, định dạng dd/mm/yyyy'],
        [''],
        ['6. Thông tin hệ thống (tùy chọn):'],
        ['   - Tài khoản IPCAS: Tên đăng nhập hệ thống IPCAS (ví dụ: nguyenvana_ipcas)'],
        ['   - Địa chỉ MAC: Định dạng XX:XX:XX:XX:XX:XX (ví dụ: AA:BB:CC:DD:EE:01)'],
        ['   - Địa chỉ IP: Địa chỉ IPv4 (ví dụ: 192.168.1.101)'],
        ['   - Phần mềm cấp phép: Tên các phần mềm cách nhau bằng dấu phẩy (phải khớp đúng tên trong hệ thống)'],
        ['     Ví dụ: Phần mềm kế toán, Email nội bộ'],
        [''],
        ['7. Lưu ý quan trọng:'],
        ['   - Không xóa dòng tiêu đề (dòng đầu tiên)'],
        ['   - Mật khẩu mặc định cho user mới: Csi@123'],
        ['   - Nếu Username đã tồn tại, hệ thống sẽ cập nhật thông tin nhân viên'],
        ['   - Các cột Chi nhánh, Phòng ban, Chức vụ, Nghiệp vụ phải sử dụng đúng mã như trên'],
        ['   - Ngày tháng phải đúng định dạng dd/mm/yyyy'],
        ['   - Hệ thống sẽ cảnh báo khi chứng thư số hết hạn trong vòng 20 ngày'],
    ]

    title_font = Font(bold=True, size=14, color='366092')
    for row_idx, instruction in enumerate(instructions, start=1):
        cell = ws_instructions.cell(row=row_idx, column=1, value=instruction[0])
        if row_idx == 1:
            cell.font = title_font
        cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)

    ws_instructions.column_dimensions['A'].width = 80

    # Prepare response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="Mau_Import_Nhan_Vien.xlsx"'
    wb.save(response)

    return response


@login_required
@require_http_methods(["GET", "POST"])
def employee_import_excel(request):
    """
    View để import nhân viên từ file Excel
    Chỉ Superuser có quyền
    """
    if not check_employee_import_permission(request.user):
        messages.error(request, 'Bạn không có quyền import nhân viên')
        return redirect('dashboard')
    if request.method == 'POST' and request.FILES.get('excel_file'):
        try:
            import openpyxl
            from datetime import datetime
            from .models import UserProfile

            excel_file = request.FILES['excel_file']

            # Validate file extension
            if not excel_file.name.endswith(('.xlsx', '.xls')):
                messages.error(request, 'File phải có định dạng .xlsx hoặc .xls')
                return redirect('employee_import_excel')

            wb = openpyxl.load_workbook(excel_file, data_only=True)
            ws = wb.active

            # Dòng đầu tiên là header
            headers = [cell.value for cell in ws[1]]

            success_count = 0
            error_count = 0
            errors = []

            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                try:
                    data = {}
                    for col_idx, value in enumerate(row):
                        if col_idx < len(headers) and headers[col_idx]:
                            data[headers[col_idx]] = value if value else ''

                    # Extract required fields
                    username = str(data.get('Username', '')).strip()
                    full_name = str(data.get('Full Name', '') or data.get('Họ và tên', '')).strip()
                    employee_code = str(data.get('Employee Code', '') or data.get('Mã nhân viên', '')).strip()

                    # Validate required fields
                    if not username or not employee_code:
                        errors.append(f"Dòng {row_idx}: Thiếu Username hoặc Mã nhân viên")
                        error_count += 1
                        continue

                    # Check if user exists
                    user = User.objects.filter(username=username).first()
                    if not user:
                        # Create new user with default password Csi@123
                        user = User.objects.create_user(
                            username=username,
                            password='Csi@123',
                            first_name=full_name.split()[0] if full_name else '',
                            last_name=' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''
                        )

                    # Get or create UserProfile
                    profile, created = UserProfile.objects.get_or_create(user=user)

                    # Update profile fields
                    if employee_code:
                        profile.employee_code = employee_code
                    if full_name:
                        profile.full_name = full_name

                    # Optional fields
                    if data.get('Branch') or data.get('Chi nhánh'):
                        branch_value = str(data.get('Branch') or data.get('Chi nhánh', '')).strip()
                        # Map value to choice
                        profile.branch = branch_value

                    if data.get('Department') or data.get('Phòng ban'):
                        dept_value = str(data.get('Department') or data.get('Phòng ban', '')).strip()
                        profile.department = dept_value

                    if data.get('Position') or data.get('Chức vụ'):
                        pos_value = str(data.get('Position') or data.get('Chức vụ', '')).strip()
                        profile.position = pos_value

                    if data.get('Job Function') or data.get('Nghiệp vụ'):
                        job_value = str(data.get('Job Function') or data.get('Nghiệp vụ', '')).strip()
                        profile.job_function = job_value

                    if data.get('Phone') or data.get('Điện thoại'):
                        profile.phone = str(data.get('Phone') or data.get('Điện thoại', '')).strip()

                    # Gender
                    if data.get('Gender') or data.get('Giới tính'):
                        gender_value = str(data.get('Gender') or data.get('Giới tính', '')).strip()
                        if gender_value:
                            profile.gender = gender_value

                    # Address
                    if data.get('Address') or data.get('Địa chỉ'):
                        address_value = str(data.get('Address') or data.get('Địa chỉ', '')).strip()
                        if address_value:
                            profile.address = address_value

                    # ID Card (CCCD) fields
                    if data.get('ID Card Number') or data.get('Số CCCD'):
                        id_card_num = str(data.get('ID Card Number') or data.get('Số CCCD', '')).strip()
                        if id_card_num:
                            profile.id_card_number = id_card_num

                    if data.get('ID Card Place') or data.get('Nơi cấp CCCD'):
                        id_card_place = str(data.get('ID Card Place') or data.get('Nơi cấp CCCD', '')).strip()
                        if id_card_place:
                            profile.id_card_place = id_card_place

                    # Parse date fields
                    dob_value = data.get('DOB') or data.get('Ngày sinh')
                    if dob_value:
                        if isinstance(dob_value, datetime):
                            profile.dob = dob_value.date()
                        elif isinstance(dob_value, str):
                            try:
                                profile.dob = datetime.strptime(dob_value, '%d/%m/%Y').date()
                            except (ValueError, TypeError):
                                try:
                                    profile.dob = datetime.strptime(dob_value, '%Y-%m-%d').date()
                                except (ValueError, TypeError):
                                    pass

                    # ID Card Date
                    id_card_date_value = data.get('ID Card Date') or data.get('Ngày cấp CCCD')
                    if id_card_date_value:
                        if isinstance(id_card_date_value, datetime):
                            profile.id_card_date = id_card_date_value.date()
                        elif isinstance(id_card_date_value, str):
                            try:
                                profile.id_card_date = datetime.strptime(id_card_date_value, '%d/%m/%Y').date()
                            except (ValueError, TypeError):
                                try:
                                    profile.id_card_date = datetime.strptime(id_card_date_value, '%Y-%m-%d').date()
                                except (ValueError, TypeError):
                                    pass

                    # IPCAS account
                    ipcas_value = str(data.get('IPCAS User') or data.get('Tài khoản IPCAS') or '').strip()
                    if ipcas_value:
                        profile.ipcas_user = ipcas_value

                    # MAC address
                    mac_value = str(data.get('MAC Address') or data.get('Địa chỉ MAC') or '').strip()
                    if mac_value:
                        profile.mac_address = mac_value

                    # IP address
                    ip_value = str(data.get('IP Address') or data.get('Địa chỉ IP') or '').strip()
                    if ip_value:
                        profile.ip_address = ip_value

                    # Digital Certificate fields
                    if data.get('Certificate Code') or data.get('Mã chứng thư số'):
                        cert_code = str(data.get('Certificate Code') or data.get('Mã chứng thư số', '')).strip()
                        if cert_code:
                            profile.certificate_code = cert_code

                    # Certificate Start Date
                    cert_start_value = data.get('Certificate Start Date') or data.get('CTS từ ngày')
                    if cert_start_value:
                        if isinstance(cert_start_value, datetime):
                            profile.certificate_start_date = cert_start_value.date()
                        elif isinstance(cert_start_value, str):
                            try:
                                profile.certificate_start_date = datetime.strptime(cert_start_value, '%d/%m/%Y').date()
                            except (ValueError, TypeError):
                                try:
                                    profile.certificate_start_date = datetime.strptime(cert_start_value, '%Y-%m-%d').date()
                                except (ValueError, TypeError):
                                    pass

                    # Certificate End Date
                    cert_end_value = data.get('Certificate End Date') or data.get('CTS đến ngày')
                    if cert_end_value:
                        if isinstance(cert_end_value, datetime):
                            profile.certificate_end_date = cert_end_value.date()
                        elif isinstance(cert_end_value, str):
                            try:
                                profile.certificate_end_date = datetime.strptime(cert_end_value, '%d/%m/%Y').date()
                            except (ValueError, TypeError):
                                try:
                                    profile.certificate_end_date = datetime.strptime(cert_end_value, '%Y-%m-%d').date()
                                except (ValueError, TypeError):
                                    pass

                    profile.save()

                    # App permissions (M2M) — xử lý sau save()
                    perm_value = str(data.get('App Permissions') or data.get('Phần mềm cấp phép') or '').strip()
                    if perm_value:
                        from .models import AppProgram
                        program_names = [n.strip() for n in perm_value.split(',') if n.strip()]
                        programs = AppProgram.objects.filter(name__in=program_names)
                        profile.app_permissions.set(programs)

                    success_count += 1

                except Exception as e:
                    error_count += 1
                    errors.append(f"Dòng {row_idx}: {str(e)}")

            # Show results
            if success_count > 0:
                messages.success(request, f'Đã import thành công {success_count} nhân viên')
            if error_count > 0:
                for error in errors[:10]:
                    messages.warning(request, error)
                if len(errors) > 10:
                    messages.warning(request, f'... và {len(errors) - 10} lỗi khác')

            return redirect('employee_import_excel')

        except Exception as e:
            import traceback
            traceback.print_exc()
            messages.error(request, f'Lỗi khi xử lý file: {str(e)}')
            return redirect('employee_import_excel')

    # GET request - show form
    context = {
        'title': 'Import nhân viên từ Excel',
    }
    return render(request, 'templates_app/employee_import.html', context)


@login_required
def employee_export_excel(request):
    """
    View để export danh sách nhân viên ra file Excel
    Chỉ Superuser có quyền
    """
    if not check_employee_import_permission(request.user):
        messages.error(request, 'Bạn không có quyền export nhân viên')
        return redirect('dashboard')

    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
        from django.http import HttpResponse
        from .models import UserProfile
        from datetime import datetime

        branch_display_map = dict(UserProfile.BRANCH_CHOICES)

        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Danh sách nhân viên"

        # Define headers
        headers = [
            'STT',
            'Mã NV',
            'Họ và tên',
            'Username',
            'Ngày sinh',
            'Giới tính',
            'Điện thoại',
            'Địa chỉ',
            'Số CCCD',
            'Ngày cấp CCCD',
            'Nơi cấp CCCD',
            'Chi nhánh',
            'Phòng ban',
            'Chức vụ',
            'Nghiệp vụ',
            'Mã CTS',
            'CTS từ ngày',
            'CTS đến ngày',
            'Trạng thái CTS',
            'Tài khoản IPCAS',
            'Địa chỉ MAC',
            'Địa chỉ IP',
            'Phần mềm cấp phép'
        ]

        # Write headers
        ws.append(headers)

        # Style headers
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for col_num in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment

        # Get all employees
        employees = UserProfile.objects.select_related('user').prefetch_related('app_permissions').all().order_by('employee_code')

        # Write data
        for idx, emp in enumerate(employees, start=2):
            # Determine certificate status
            cert_status = '-'
            if emp.certificate_code:
                if emp.is_certificate_expired():
                    cert_status = 'Hết hạn'
                elif emp.is_certificate_expiring_soon():
                    cert_status = f'Còn {emp.days_until_certificate_expiry()} ngày'
                elif emp.days_until_certificate_expiry() and emp.days_until_certificate_expiry() > 36500:
                    cert_status = 'Vĩnh viễn'
                else:
                    cert_status = 'Hiệu lực'
            else:
                cert_status = 'Chưa có'

            row_data = [
                idx - 1,  # STT
                emp.employee_code or '',
                emp.full_name or '',
                emp.user.username if emp.user else '',
                emp.dob.strftime('%d/%m/%Y') if emp.dob else '',
                emp.gender or '',
                emp.phone or '',
                emp.address or '',
                emp.id_card_number or '',
                emp.id_card_date.strftime('%d/%m/%Y') if emp.id_card_date else '',
                emp.id_card_place or '',
                branch_display_map.get(emp.branch, emp.branch) or '',
                emp.get_department_display() or '',
                emp.get_position_display() or '',
                emp.get_job_function_display() or '',
                emp.certificate_code or '',
                emp.certificate_start_date.strftime('%d/%m/%Y') if emp.certificate_start_date else '',
                emp.certificate_end_date.strftime('%d/%m/%Y') if emp.certificate_end_date else '',
                cert_status,
                emp.ipcas_user or '',
                emp.mac_address or '',
                str(emp.ip_address) if emp.ip_address else '',
                ', '.join(ap.name for ap in emp.app_permissions.all()),
            ]
            ws.append(row_data)

        # Auto-adjust column widths
        column_widths = {
            'A': 6,   # STT
            'B': 12,  # Mã NV
            'C': 25,  # Họ và tên
            'D': 15,  # Username
            'E': 12,  # Ngày sinh
            'F': 10,  # Giới tính
            'G': 13,  # Điện thoại
            'H': 30,  # Địa chỉ
            'I': 13,  # Số CCCD
            'J': 13,  # Ngày cấp CCCD
            'K': 20,  # Nơi cấp CCCD
            'L': 20,  # Chi nhánh
            'M': 20,  # Phòng ban
            'N': 20,  # Chức vụ
            'O': 18,  # Nghiệp vụ
            'P': 15,  # Mã CTS
            'Q': 13,  # CTS từ ngày
            'R': 13,  # CTS đến ngày
            'S': 15,  # Trạng thái CTS
            'T': 20,  # Tài khoản IPCAS
            'U': 20,  # Địa chỉ MAC
            'V': 16,  # Địa chỉ IP
            'W': 35,  # Phần mềm cấp phép
        }

        for col, width in column_widths.items():
            ws.column_dimensions[col].width = width

        # Set row height for header
        ws.row_dimensions[1].height = 30

        # Apply borders and alignment to all cells
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=len(headers)):
            for cell in row:
                cell.border = thin_border
                if cell.row > 1:  # Not header
                    cell.alignment = Alignment(vertical="center", wrap_text=True)

        # Prepare response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f'DanhSachNhanVien_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        # Save workbook to response
        wb.save(response)

        return response

    except Exception as e:
        messages.error(request, f'Lỗi khi export: {str(e)}')
        return redirect('employee_list')


@login_required
def employee_list(request):
    """
    Hiển thị danh sách nhân viên và form thêm/sửa
    Chỉ Superuser có quyền
    """
    if not check_employee_import_permission(request.user):
        messages.error(request, 'Bạn không có quyền quản lý nhân viên')
        return redirect('dashboard')

    from .models import UserProfile
    from datetime import date, timedelta

    employees = UserProfile.objects.select_related('user').prefetch_related('app_permissions').all()

    # Get filter parameters
    filter_department = request.GET.get('department', '')
    filter_position = request.GET.get('position', '')
    filter_branch = request.GET.get('branch', '')
    filter_cert_status = request.GET.get('cert_status', '')

    # Apply filters
    if filter_department:
        employees = employees.filter(department=filter_department)
    if filter_position:
        employees = employees.filter(position=filter_position)
    if filter_branch:
        employees = employees.filter(branch=filter_branch)

    # Filter by certificate status
    today = date.today()
    warning_date = today + timedelta(days=20)

    if filter_cert_status == 'expiring':
        # Certificates expiring within 20 days
        employees = employees.filter(
            certificate_end_date__lte=warning_date,
            certificate_end_date__gte=today
        )
    elif filter_cert_status == 'expired':
        # Already expired certificates
        employees = employees.filter(certificate_end_date__lt=today)
    elif filter_cert_status == 'valid':
        # Valid certificates (not expiring soon)
        employees = employees.filter(certificate_end_date__gt=warning_date)
    elif filter_cert_status == 'no_cert':
        # No certificate
        employees = employees.filter(certificate_code='')

    employees = employees.order_by('employee_code')

    # Count warnings for display
    expiring_count = UserProfile.objects.filter(
        certificate_end_date__lte=warning_date,
        certificate_end_date__gte=today
    ).count()
    expired_count = UserProfile.objects.filter(certificate_end_date__lt=today).count()

    # Get unique values for filter dropdowns
    departments = UserProfile.DEPARTMENT_CHOICES
    positions = UserProfile.POSITION_CHOICES
    branches = BranchConfig.objects.filter(is_active=True).order_by('branch_code').values_list('branch_code', 'ten_chi_nhanh')
    app_programs = AppProgram.objects.filter(is_active=True).order_by('order', 'name')

    context = {
        'title': 'Quản lý nhân viên',
        'employees': employees,
        'filter_department': filter_department,
        'filter_position': filter_position,
        'filter_branch': filter_branch,
        'filter_cert_status': filter_cert_status,
        'departments': departments,
        'positions': positions,
        'branches': branches,
        'app_programs': app_programs,
        'expiring_count': expiring_count,
        'expired_count': expired_count,
    }
    return render(request, 'templates_app/employee_list.html', context)


@login_required
@require_http_methods(["POST"])
def employee_create_manual(request):
    """
    Tạo nhân viên mới thủ công
    Chỉ Superuser có quyền
    """
    if not check_employee_import_permission(request.user):
        return JsonResponse({'success': False, 'error': 'Bạn không có quyền'}, status=403)

    from .models import UserProfile
    from datetime import datetime

    try:
        # Required fields
        username = request.POST.get('username', '').strip()
        employee_code = request.POST.get('employee_code', '').strip()
        full_name = request.POST.get('full_name', '').strip()

        if not username or not employee_code or not full_name:
            return JsonResponse({'success': False, 'error': 'Thiếu thông tin bắt buộc'}, status=400)

        # Check if username exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': f'Username "{username}" đã tồn tại'}, status=400)

        # Check if employee_code exists
        if UserProfile.objects.filter(employee_code=employee_code).exists():
            return JsonResponse({'success': False, 'error': f'Mã nhân viên "{employee_code}" đã tồn tại'}, status=400)

        # Create user
        user = User.objects.create_user(
            username=username,
            password=request.POST.get('password', 'Csi@123'),
            first_name=full_name.split()[0] if full_name else '',
            last_name=' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''
        )

        # Create profile
        profile = UserProfile.objects.create(
            user=user,
            employee_code=employee_code,
            full_name=full_name
        )

        # Optional fields
        if request.POST.get('dob'):
            try:
                profile.dob = datetime.strptime(request.POST.get('dob'), '%Y-%m-%d').date()
            except Exception:
                pass

        profile.gender = request.POST.get('gender', 'Nam')
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.id_card_number = request.POST.get('id_card_number', '')

        if request.POST.get('id_card_date'):
            try:
                profile.id_card_date = datetime.strptime(request.POST.get('id_card_date'), '%Y-%m-%d').date()
            except Exception:
                pass

        profile.id_card_place = request.POST.get('id_card_place', '')
        profile.branch = request.POST.get('branch', '')
        profile.department = request.POST.get('department', '')
        profile.position = request.POST.get('position', '')
        profile.job_function = request.POST.get('job_function', '')

        # System info
        profile.ipcas_user = request.POST.get('ipcas_user', '')
        profile.csp_cuser = request.POST.get('csp_cuser', '')
        profile.mac_address = request.POST.get('mac_address', '')
        profile.ip_address = request.POST.get('ip_address') or None

        # Digital certificate fields
        profile.certificate_code = request.POST.get('certificate_code', '')

        if request.POST.get('certificate_start_date'):
            try:
                profile.certificate_start_date = datetime.strptime(request.POST.get('certificate_start_date'), '%Y-%m-%d').date()
            except Exception:
                pass

        if request.POST.get('certificate_end_date'):
            try:
                profile.certificate_end_date = datetime.strptime(request.POST.get('certificate_end_date'), '%Y-%m-%d').date()
            except Exception:
                pass

        profile.save()

        # App permissions (M2M - save after profile.save())
        app_ids = request.POST.getlist('app_permissions')
        if app_ids:
            from .models import AppProgram
            profile.app_permissions.set(AppProgram.objects.filter(id__in=app_ids))
        else:
            profile.app_permissions.clear()

        return JsonResponse({
            'success': True,
            'message': f'Đã thêm nhân viên {full_name} thành công'
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def employee_update_manual(request, employee_id):
    """
    Cập nhật thông tin nhân viên
    Chỉ Superuser có quyền
    """
    if not check_employee_import_permission(request.user):
        return JsonResponse({'success': False, 'error': 'Bạn không có quyền'}, status=403)

    from .models import UserProfile
    from datetime import datetime

    try:
        profile = UserProfile.objects.get(id=employee_id)

        # Update fields
        full_name = request.POST.get('full_name', '').strip()
        if full_name:
            profile.full_name = full_name

        if request.POST.get('dob'):
            try:
                profile.dob = datetime.strptime(request.POST.get('dob'), '%Y-%m-%d').date()
            except Exception:
                pass

        profile.gender = request.POST.get('gender', profile.gender)
        profile.phone = request.POST.get('phone', profile.phone)
        profile.address = request.POST.get('address', profile.address)
        profile.id_card_number = request.POST.get('id_card_number', profile.id_card_number)

        if request.POST.get('id_card_date'):
            try:
                profile.id_card_date = datetime.strptime(request.POST.get('id_card_date'), '%Y-%m-%d').date()
            except Exception:
                pass

        profile.id_card_place = request.POST.get('id_card_place', profile.id_card_place)
        profile.branch = request.POST.get('branch', profile.branch)
        profile.department = request.POST.get('department', profile.department)
        profile.position = request.POST.get('position', profile.position)
        profile.job_function = request.POST.get('job_function', profile.job_function)

        # System info
        profile.ipcas_user = request.POST.get('ipcas_user', profile.ipcas_user)
        profile.csp_cuser = request.POST.get('csp_cuser', profile.csp_cuser)
        profile.mac_address = request.POST.get('mac_address', profile.mac_address)
        ip_val = request.POST.get('ip_address', '')
        profile.ip_address = ip_val if ip_val else None

        # Digital certificate fields
        profile.certificate_code = request.POST.get('certificate_code', profile.certificate_code)

        if request.POST.get('certificate_start_date'):
            try:
                profile.certificate_start_date = datetime.strptime(request.POST.get('certificate_start_date'), '%Y-%m-%d').date()
            except Exception:
                pass

        if request.POST.get('certificate_end_date'):
            try:
                profile.certificate_end_date = datetime.strptime(request.POST.get('certificate_end_date'), '%Y-%m-%d').date()
            except Exception:
                pass

        profile.save()

        # App permissions
        app_ids = request.POST.getlist('app_permissions')
        from .models import AppProgram
        profile.app_permissions.set(AppProgram.objects.filter(id__in=app_ids))

        return JsonResponse({
            'success': True,
            'message': f'Đã cập nhật thông tin nhân viên {profile.full_name}'
        })

    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy nhân viên'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def employee_delete_manual(request, employee_id):
    """
    Xóa nhân viên
    Chỉ Superuser có quyền
    """
    if not check_employee_import_permission(request.user):
        return JsonResponse({'success': False, 'error': 'Bạn không có quyền'}, status=403)

    from .models import UserProfile

    try:
        profile = UserProfile.objects.get(id=employee_id)
        full_name = profile.full_name
        user = profile.user

        # Delete profile and user
        profile.delete()
        user.delete()

        return JsonResponse({
            'success': True,
            'message': f'Đã xóa nhân viên {full_name}'
        })

    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy nhân viên'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ====================

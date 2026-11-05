"""
Model quản lý ATM: máy ATM, ban quản lý, xe, nhân sự, tiếp quỹ, lịch trực xe, thừa thiếu quỹ.
"""
from django.db import models
from django.contrib.auth.models import User
import uuid
from .text_utils import num_to_vietnamese_words


# ============================================================================
# ATM Management Models
# ============================================================================

class ATM(models.Model):
    """Quản lý máy ATM"""
    machine_id = models.CharField(
        max_length=50,
        primary_key=True,
        verbose_name="ID Máy ATM"
    )
    serial_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Số Serial máy"
    )
    address = models.CharField(
        max_length=500,
        verbose_name="Địa chỉ máy"
    )
    machine_type = models.CharField(
        max_length=100,
        verbose_name="Loại máy"
    )
    machine_line = models.CharField(
        max_length=100,
        verbose_name="Dòng máy"
    )
    installation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Ngày lắp đặt"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang hoạt động"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Máy ATM"
        verbose_name_plural = "Máy ATM"
        ordering = ['machine_id']

    def __str__(self):
        return f"{self.machine_id} - {self.address}"


class ATMManagementBoard(models.Model):
    """Ban quản lý ATM"""
    POSITION_CHOICES = [
        ('team_leader', 'Trưởng Ban'),
        ('treasury_head', 'Trưởng phòng KTNQ'),
        ('atm_officer', 'Cán bộ phụ trách ATM'),
    ]

    position = models.CharField(
        max_length=50,
        choices=POSITION_CHOICES,
        verbose_name="Chức vụ"
    )
    full_name = models.CharField(
        max_length=200,
        verbose_name="Họ và tên"
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Chức danh"
    )
    decision_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Số quyết định"
    )
    decision_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Ngày quyết định thành lập"
    )
    account_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Số tài khoản"
    )
    effective_from = models.DateField(
        null=True,
        blank=True,
        verbose_name="Hiệu lực từ ngày"
    )
    effective_to = models.DateField(
        null=True,
        blank=True,
        verbose_name="Hiệu lực đến ngày (bỏ trống nếu đang đương nhiệm)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang hoạt động"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Ban quản lý ATM"
        verbose_name_plural = "Ban quản lý ATM"
        ordering = ['position']

    def __str__(self):
        return f"{self.get_position_display()} - {self.full_name}"


class Vehicle(models.Model):
    """Phương tiện vận chuyển tiền"""
    license_plate = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Biển số xe"
    )
    vehicle_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Loại xe"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang hoạt động"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Phương tiện"
        verbose_name_plural = "Phương tiện"
        ordering = ['license_plate']

    def __str__(self):
        return self.license_plate


class Person(models.Model):
    """Base model cho nhân viên vận chuyển (tài xế, bảo vệ)"""
    PERSON_TYPE_CHOICES = [
        ('driver', 'Tài xế'),
        ('guard', 'Bảo vệ'),
    ]

    person_type = models.CharField(
        max_length=20,
        choices=PERSON_TYPE_CHOICES,
        verbose_name="Loại nhân viên"
    )
    full_name = models.CharField(
        max_length=200,
        verbose_name="Họ và tên"
    )
    id_number = models.CharField(
        max_length=50,
        verbose_name="Số CCCD"
    )
    id_issue_date = models.DateField(
        verbose_name="Ngày cấp"
    )
    id_issue_place = models.CharField(
        max_length=200,
        verbose_name="Nơi cấp"
    )
    account_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Số tài khoản"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang hoạt động"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Nhân viên vận chuyển"
        verbose_name_plural = "Nhân viên vận chuyển"
        ordering = ['person_type', 'full_name']
        unique_together = ['id_number', 'person_type']

    def __str__(self):
        return f"{self.get_person_type_display()} - {self.full_name}"


class ATMReplenishment(models.Model):
    """Phiếu tiếp quỹ ATM"""
    atm = models.ForeignKey(
        ATM,
        on_delete=models.PROTECT,
        verbose_name="Máy ATM"
    )
    replenishment_date = models.DateField(
        verbose_name="Ngày tiếp quỹ"
    )

    # Số lượng tờ tiền theo mệnh giá
    bills_50k = models.IntegerField(
        default=0,
        verbose_name="Số tờ 50.000đ"
    )
    bills_100k = models.IntegerField(
        default=0,
        verbose_name="Số tờ 100.000đ"
    )
    bills_200k = models.IntegerField(
        default=0,
        verbose_name="Số tờ 200.000đ"
    )
    bills_500k = models.IntegerField(
        default=0,
        verbose_name="Số tờ 500.000đ"
    )

    # Lệnh điều chuyển
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        verbose_name="Phương tiện"
    )
    driver = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name='replenishments_as_driver',
        limit_choices_to={'person_type': 'driver'},
        verbose_name="Tài xế"
    )
    guard = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name='replenishments_as_guard',
        limit_choices_to={'person_type': 'guard'},
        verbose_name="Bảo vệ"
    )

    # Số văn bản giấy đi đường — tự động tăng dần theo từng năm (sang năm mới reset về 1),
    # gán 1 lần duy nhất khi tạo phiếu, dựa theo năm của ngày tiếp quỹ
    travel_order_number = models.PositiveIntegerField(
        null=True, blank=True, editable=False,
        verbose_name="Số văn bản giấy đi đường"
    )
    travel_order_year = models.PositiveIntegerField(
        null=True, blank=True, editable=False,
        verbose_name="Năm của số văn bản giấy đi đường"
    )

    # Thông tin người tạo
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Người tạo"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Phiếu tiếp quỹ ATM"
        verbose_name_plural = "Phiếu tiếp quỹ ATM"
        ordering = ['-replenishment_date', '-created_at']
        unique_together = [('travel_order_year', 'travel_order_number')]

    def __str__(self):
        return f"Tiếp quỹ {self.atm.machine_id} - {self.replenishment_date.strftime('%d/%m/%Y')}"

    def save(self, *args, **kwargs):
        if self.travel_order_number is None:
            year = self.replenishment_date.year
            last = ATMReplenishment.objects.filter(travel_order_year=year).aggregate(
                models.Max('travel_order_number')
            )
            self.travel_order_number = (last['travel_order_number__max'] or 0) + 1
            self.travel_order_year = year
        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        """Tính tổng số tiền tiếp quỹ"""
        return (
            self.bills_50k * 50000 +
            self.bills_100k * 100000 +
            self.bills_200k * 200000 +
            self.bills_500k * 500000
        )

    def get_amount_in_words(self):
        """Chuyển số tiền sang chữ"""
        return num_to_vietnamese_words(self.total_amount)

    def get_data_dict(self):
        """
        Trả về dictionary chứa thông tin phiếu tiếp quỹ ATM
        Dùng để tạo mẫu biểu Word
        """
        # Date variables cho ngày tiếp quỹ
        tq_d1, tq_d2, tq_m1, tq_m2, tq_y1, tq_y2, tq_y3, tq_y4 = '', '', '', '', '', '', '', ''
        if self.replenishment_date:
            date_str = self.replenishment_date.strftime('%d%m%Y')
            if len(date_str) == 8:
                tq_d1, tq_d2 = date_str[0], date_str[1]
                tq_m1, tq_m2 = date_str[2], date_str[3]
                tq_y1, tq_y2, tq_y3, tq_y4 = date_str[4], date_str[5], date_str[6], date_str[7]

        # Date variables cho ngày lắp đặt ATM
        ld_d1, ld_d2, ld_m1, ld_m2, ld_y1, ld_y2, ld_y3, ld_y4 = '', '', '', '', '', '', '', ''
        if self.atm.installation_date:
            date_str = self.atm.installation_date.strftime('%d%m%Y')
            if len(date_str) == 8:
                ld_d1, ld_d2 = date_str[0], date_str[1]
                ld_m1, ld_m2 = date_str[2], date_str[3]
                ld_y1, ld_y2, ld_y3, ld_y4 = date_str[4], date_str[5], date_str[6], date_str[7]

        # Date variables cho ngày cấp CCCD tài xế
        tx_d1, tx_d2, tx_m1, tx_m2, tx_y1, tx_y2, tx_y3, tx_y4 = '', '', '', '', '', '', '', ''
        if self.driver.id_issue_date:
            date_str = self.driver.id_issue_date.strftime('%d%m%Y')
            if len(date_str) == 8:
                tx_d1, tx_d2 = date_str[0], date_str[1]
                tx_m1, tx_m2 = date_str[2], date_str[3]
                tx_y1, tx_y2, tx_y3, tx_y4 = date_str[4], date_str[5], date_str[6], date_str[7]

        # Date variables cho ngày cấp CCCD bảo vệ
        bv_d1, bv_d2, bv_m1, bv_m2, bv_y1, bv_y2, bv_y3, bv_y4 = '', '', '', '', '', '', '', ''
        if self.guard.id_issue_date:
            date_str = self.guard.id_issue_date.strftime('%d%m%Y')
            if len(date_str) == 8:
                bv_d1, bv_d2 = date_str[0], date_str[1]
                bv_m1, bv_m2 = date_str[2], date_str[3]
                bv_y1, bv_y2, bv_y3, bv_y4 = date_str[4], date_str[5], date_str[6], date_str[7]

        # Lấy thông tin ban quản lý ATM
        team_leader = ATMManagementBoard.objects.filter(position='team_leader', is_active=True).first()
        treasury_head = ATMManagementBoard.objects.filter(position='treasury_head', is_active=True).first()
        atm_officer = ATMManagementBoard.objects.filter(position='atm_officer', is_active=True).first()

        # Tính tiền cho từng mệnh giá
        amount_50k = self.bills_50k * 50000
        amount_100k = self.bills_100k * 100000
        amount_200k = self.bills_200k * 200000
        amount_500k = self.bills_500k * 500000

        data = {
            # Thông tin máy ATM
            'atm_machine_id': self.atm.machine_id,
            'atm_serial_number': self.atm.serial_number or '',
            'atm_address': self.atm.address,
            'atm_machine_type': self.atm.machine_type,
            'atm_machine_line': self.atm.machine_line,
            'atm_installation_date': self.atm.installation_date.strftime('%d/%m/%Y') if self.atm.installation_date else '',

            # Date variables cho ngày lắp đặt
            'atm_ld_d1': ld_d1, 'atm_ld_d2': ld_d2,
            'atm_ld_m1': ld_m1, 'atm_ld_m2': ld_m2,
            'atm_ld_y1': ld_y1, 'atm_ld_y2': ld_y2, 'atm_ld_y3': ld_y3, 'atm_ld_y4': ld_y4,

            # Thông tin tiếp quỹ
            'replenishment_date': self.replenishment_date.strftime('%d/%m/%Y'),

            # Date variables cho ngày tiếp quỹ
            'tq_d1': tq_d1, 'tq_d2': tq_d2,
            'tq_m1': tq_m1, 'tq_m2': tq_m2,
            'tq_y1': tq_y1, 'tq_y2': tq_y2, 'tq_y3': tq_y3, 'tq_y4': tq_y4,

            # Số lượng tờ tiền
            'bills_50k': str(self.bills_50k),
            'bills_100k': str(self.bills_100k),
            'bills_200k': str(self.bills_200k),
            'bills_500k': str(self.bills_500k),

            # Thành tiền từng mệnh giá
            'amount_50k': f"{amount_50k:,}",
            'amount_100k': f"{amount_100k:,}",
            'amount_200k': f"{amount_200k:,}",
            'amount_500k': f"{amount_500k:,}",

            # Tổng tiền
            'total_amount': f"{self.total_amount:,}",
            'total_amount_words': self.get_amount_in_words(),

            # Thông tin phương tiện
            'vehicle_license_plate': self.vehicle.license_plate,
            'vehicle_type': self.vehicle.vehicle_type or '',

            # Thông tin tài xế
            'driver_full_name': self.driver.full_name,
            'driver_id_number': self.driver.id_number,
            'driver_id_issue_date': self.driver.id_issue_date.strftime('%d/%m/%Y'),
            'driver_id_issue_place': self.driver.id_issue_place,

            # Date variables cho tài xế
            'tx_d1': tx_d1, 'tx_d2': tx_d2,
            'tx_m1': tx_m1, 'tx_m2': tx_m2,
            'tx_y1': tx_y1, 'tx_y2': tx_y2, 'tx_y3': tx_y3, 'tx_y4': tx_y4,

            # Thông tin bảo vệ
            'guard_full_name': self.guard.full_name,
            'guard_id_number': self.guard.id_number,
            'guard_id_issue_date': self.guard.id_issue_date.strftime('%d/%m/%Y'),
            'guard_id_issue_place': self.guard.id_issue_place,

            # Date variables cho bảo vệ
            'bv_d1': bv_d1, 'bv_d2': bv_d2,
            'bv_m1': bv_m1, 'bv_m2': bv_m2,
            'bv_y1': bv_y1, 'bv_y2': bv_y2, 'bv_y3': bv_y3, 'bv_y4': bv_y4,

            # Ban quản lý ATM
            'team_leader_name': team_leader.full_name if team_leader else '',
            'team_leader_title': team_leader.title if team_leader else '',
            'treasury_head_name': treasury_head.full_name if treasury_head else '',
            'treasury_head_title': treasury_head.title if treasury_head else '',
            'atm_officer_name': atm_officer.full_name if atm_officer else '',
            'atm_officer_title': atm_officer.title if atm_officer else '',
            'board_decision_number': team_leader.decision_number if team_leader else '',
            'board_decision_date': (
                f"ngày {team_leader.decision_date.day:02d} tháng {team_leader.decision_date.month:02d} năm {team_leader.decision_date.year}"
                if (team_leader and team_leader.decision_date) else ''
            ),

            # Số văn bản giấy đi đường — tự tăng dần theo từng phiếu tiếp quỹ
            'travel_order_number': str(self.travel_order_number) if self.travel_order_number else '',

            # Thông tin người tạo
            'created_by': self.created_by.username,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M'),
        }

        return data


class VehicleDutySchedule(models.Model):
    """Lịch trực xe hàng ngày — mỗi ngày có 1 tài xế trực (đã được trả tiền trực từ cơ quan)"""
    date = models.DateField(unique=True, verbose_name="Ngày trực")
    driver = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        limit_choices_to={'person_type': 'driver'},
        verbose_name="Tài xế trực"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Lịch trực xe"
        verbose_name_plural = "Lịch trực xe"
        ordering = ['date']

    def __str__(self):
        return f"{self.date.strftime('%d/%m/%Y')} - {self.driver.full_name}"


class ATMDiscrepancy(models.Model):
    """Quản lý các giao dịch thừa/thiếu quỹ ATM"""

    DISCREPANCY_TYPES = [
        ('surplus', 'Thừa'),
        ('deficit', 'Thiếu'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('resolved', 'Đã xử lý'),
        ('escalated', 'Đã báo cáo lên'),
    ]

    atm = models.ForeignKey(
        ATM,
        on_delete=models.PROTECT,
        related_name='discrepancies',
        verbose_name="Máy ATM"
    )
    full_name = models.CharField(max_length=200, verbose_name="Họ tên")
    account_number = models.CharField(max_length=50, verbose_name="Số tài khoản")
    card_number = models.CharField(max_length=50, blank=True, verbose_name="Số thẻ")
    trace_number = models.CharField(max_length=100, blank=True, verbose_name="Số trace")
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name="ID giao dịch")

    discrepancy_type = models.CharField(
        max_length=10,
        choices=DISCREPANCY_TYPES,
        verbose_name="Loại"
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name="Số tiền"
    )

    audit_cycle_start = models.DateField(verbose_name="Chu kỳ kiểm quỹ từ ngày")
    audit_cycle_end = models.DateField(verbose_name="Chu kỳ kiểm quỹ đến ngày")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái"
    )
    notes = models.TextField(blank=True, verbose_name="Ghi chú")

    group_id = models.UUIDField(
        default=uuid.uuid4,
        db_index=True,
        verbose_name="Mã nhóm chu kỳ"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='atm_discrepancies_created',
        verbose_name="Người tạo"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Giao dịch thừa/thiếu quỹ ATM"
        verbose_name_plural = "Giao dịch thừa/thiếu quỹ ATM"
        ordering = ['-audit_cycle_end', '-created_at']

    def __str__(self):
        type_display = "Thừa" if self.discrepancy_type == 'surplus' else "Thiếu"
        return f"{self.atm.machine_id} - {type_display} {self.amount:,}đ - {self.full_name}"

    def get_amount_in_words(self):
        """Chuyển số tiền thành chữ"""
        return num_to_vietnamese_words(int(self.amount))

    def get_data_dict(self):
        """Trả về dictionary chứa tất cả biến cho Word template"""
        # Phân tách ngày bắt đầu chu kỳ
        acs_d1 = self.audit_cycle_start.strftime('%d')[0]
        acs_d2 = self.audit_cycle_start.strftime('%d')[1]
        acs_m1 = self.audit_cycle_start.strftime('%m')[0]
        acs_m2 = self.audit_cycle_start.strftime('%m')[1]
        acs_y1 = self.audit_cycle_start.strftime('%Y')[0]
        acs_y2 = self.audit_cycle_start.strftime('%Y')[1]
        acs_y3 = self.audit_cycle_start.strftime('%Y')[2]
        acs_y4 = self.audit_cycle_start.strftime('%Y')[3]

        # Phân tách ngày kết thúc chu kỳ
        ace_d1 = self.audit_cycle_end.strftime('%d')[0]
        ace_d2 = self.audit_cycle_end.strftime('%d')[1]
        ace_m1 = self.audit_cycle_end.strftime('%m')[0]
        ace_m2 = self.audit_cycle_end.strftime('%m')[1]
        ace_y1 = self.audit_cycle_end.strftime('%Y')[0]
        ace_y2 = self.audit_cycle_end.strftime('%Y')[1]
        ace_y3 = self.audit_cycle_end.strftime('%Y')[2]
        ace_y4 = self.audit_cycle_end.strftime('%Y')[3]

        # Lấy thông tin ban quản lý ATM
        team_leader = ATMManagementBoard.objects.filter(
            position='team_leader', is_active=True
        ).first()
        treasury_head = ATMManagementBoard.objects.filter(
            position='treasury_head', is_active=True
        ).first()
        atm_officer = ATMManagementBoard.objects.filter(
            position='atm_officer', is_active=True
        ).first()

        data = {
            # Thông tin máy ATM
            'disc_atm_machine_id': self.atm.machine_id,
            'disc_atm_serial_number': self.atm.serial_number or '',
            'disc_atm_address': self.atm.address,
            'disc_atm_machine_type': self.atm.machine_type,
            'disc_atm_machine_line': self.atm.machine_line,

            # Thông tin khách hàng/giao dịch
            'disc_full_name': self.full_name,
            'disc_account_number': self.account_number,
            'disc_card_number': self.card_number,
            'disc_trace_number': self.trace_number,
            'disc_transaction_id': self.transaction_id,

            # Thông tin số tiền
            'disc_type': self.get_discrepancy_type_display(),
            'disc_type_lower': self.get_discrepancy_type_display().lower(),
            'disc_amount': f"{self.amount:,}",
            'disc_amount_words': self.get_amount_in_words(),

            # Chu kỳ kiểm quỹ
            'disc_audit_cycle_start': self.audit_cycle_start.strftime('%d/%m/%Y'),
            'disc_audit_cycle_end': self.audit_cycle_end.strftime('%d/%m/%Y'),

            # Date variables cho ngày bắt đầu chu kỳ
            'acs_d1': acs_d1, 'acs_d2': acs_d2,
            'acs_m1': acs_m1, 'acs_m2': acs_m2,
            'acs_y1': acs_y1, 'acs_y2': acs_y2, 'acs_y3': acs_y3, 'acs_y4': acs_y4,

            # Date variables cho ngày kết thúc chu kỳ
            'ace_d1': ace_d1, 'ace_d2': ace_d2,
            'ace_m1': ace_m1, 'ace_m2': ace_m2,
            'ace_y1': ace_y1, 'ace_y2': ace_y2, 'ace_y3': ace_y3, 'ace_y4': ace_y4,

            # Trạng thái
            'disc_status': self.get_status_display(),
            'disc_notes': self.notes or '',

            # Ban quản lý ATM
            'disc_team_leader_name': team_leader.full_name if team_leader else '',
            'disc_team_leader_title': team_leader.title if team_leader else '',
            'disc_treasury_head_name': treasury_head.full_name if treasury_head else '',
            'disc_treasury_head_title': treasury_head.title if treasury_head else '',
            'disc_atm_officer_name': atm_officer.full_name if atm_officer else '',
            'disc_atm_officer_title': atm_officer.title if atm_officer else '',
            'disc_board_decision_number': team_leader.decision_number if team_leader else '',
            'disc_board_decision_date': (
                f"ngày {team_leader.decision_date.day:02d} tháng {team_leader.decision_date.month:02d} năm {team_leader.decision_date.year}"
                if (team_leader and team_leader.decision_date) else ''
            ),

            # Thông tin người tạo
            'disc_created_by': self.created_by.username,
            'disc_created_at': self.created_at.strftime('%d/%m/%Y %H:%M'),
        }

        return data

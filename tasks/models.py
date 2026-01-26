from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    """Model quản lý công việc/Todo với tính năng lặp lại tự động."""

    # Choices cho Priority
    PRIORITY_NORMAL = 'normal'
    PRIORITY_URGENT = 'urgent'
    PRIORITY_CHOICES = [
        (PRIORITY_NORMAL, 'Bình thường'),
        (PRIORITY_URGENT, 'Gấp'),
    ]

    # Choices cho Category
    CATEGORY_MONTHLY = 'monthly'
    CATEGORY_QUARTERLY = 'quarterly'
    CATEGORY_AD_HOC = 'ad_hoc'
    CATEGORY_CHOICES = [
        (CATEGORY_MONTHLY, 'Tháng'),
        (CATEGORY_QUARTERLY, 'Quý'),
        (CATEGORY_AD_HOC, 'Phát sinh'),
    ]

    # Choices cho Recurring Type
    RECURRING_NONE = 'none'
    RECURRING_MONTHLY = 'monthly'
    RECURRING_QUARTERLY = 'quarterly'
    RECURRING_CHOICES = [
        (RECURRING_NONE, 'Không lặp'),
        (RECURRING_MONTHLY, 'Hàng tháng'),
        (RECURRING_QUARTERLY, 'Hàng quý'),
    ]

    # Trường cơ bản
    title = models.CharField('Tiêu đề', max_length=255)
    description = models.TextField('Mô tả', blank=True, null=True)
    due_date = models.DateField('Hạn chót', blank=True, null=True)
    is_completed = models.BooleanField('Hoàn thành', default=False)

    # Priority và Category
    priority = models.CharField(
        'Độ ưu tiên',
        max_length=10,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_NORMAL
    )
    category = models.CharField(
        'Phân loại',
        max_length=15,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_AD_HOC
    )

    # Recurring Logic
    recurring_type = models.CharField(
        'Loại lặp',
        max_length=15,
        choices=RECURRING_CHOICES,
        default=RECURRING_NONE
    )

    # Giao việc (Assignment)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='Người được giao'
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tasks',
        verbose_name='Người tạo'
    )
    created_at = models.DateTimeField('Ngày tạo', auto_now_add=True)
    updated_at = models.DateTimeField('Ngày cập nhật', auto_now=True)
    completed_at = models.DateTimeField('Ngày hoàn thành', blank=True, null=True)

    class Meta:
        verbose_name = 'Công việc'
        verbose_name_plural = 'Danh sách công việc'
        ordering = ['-priority', 'due_date', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Cập nhật completed_at khi task được đánh dấu hoàn thành
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.is_completed:
            self.completed_at = None
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Kiểm tra task đã quá hạn chưa."""
        if self.due_date and not self.is_completed:
            return self.due_date < timezone.now().date()
        return False

    @property
    def priority_display_class(self):
        """Trả về class CSS dựa trên priority."""
        if self.priority == self.PRIORITY_URGENT:
            return 'table-danger'
        return ''

    @property
    def category_badge_class(self):
        """Trả về class badge dựa trên category."""
        classes = {
            self.CATEGORY_MONTHLY: 'bg-primary',
            self.CATEGORY_QUARTERLY: 'bg-success',
            self.CATEGORY_AD_HOC: 'bg-secondary',
        }
        return classes.get(self.category, 'bg-secondary')

    @property
    def recurring_badge_class(self):
        """Trả về class badge dựa trên recurring type."""
        classes = {
            self.RECURRING_NONE: 'bg-light text-dark',
            self.RECURRING_MONTHLY: 'bg-info',
            self.RECURRING_QUARTERLY: 'bg-warning text-dark',
        }
        return classes.get(self.recurring_type, 'bg-light text-dark')

    def is_owner(self, user):
        """Kiểm tra user có phải là người tạo task không."""
        return self.created_by == user

    def is_assignee(self, user):
        """Kiểm tra user có phải là người được giao task không."""
        return self.assigned_to == user

    def get_task_type_for_user(self, user):
        """
        Trả về loại task đối với user:
        - 'own': Task do user tạo
        - 'assigned': Task được giao cho user
        - 'both': User vừa tạo vừa được giao (tự giao cho mình)
        """
        is_owner = self.is_owner(user)
        is_assignee = self.is_assignee(user)

        if is_owner and is_assignee:
            return 'both'
        elif is_owner:
            return 'own'
        elif is_assignee:
            return 'assigned'
        return None

    @property
    def created_by_display(self):
        """Hiển thị tên người tạo kèm chức vụ."""
        if not self.created_by:
            return 'N/A'
        try:
            profile = self.created_by.profile
            position = profile.get_position_display() if profile.position else ''
            name = profile.full_name or self.created_by.username
            if position:
                return f"{name} - {position}"
            return name
        except Exception:
            return self.created_by.username

    @property
    def assigned_to_display(self):
        """Hiển thị tên người được giao kèm chức vụ."""
        if not self.assigned_to:
            return None
        try:
            profile = self.assigned_to.profile
            position = profile.get_position_display() if profile.position else ''
            name = profile.full_name or self.assigned_to.username
            if position:
                return f"{name} - {position}"
            return name
        except Exception:
            return self.assigned_to.username

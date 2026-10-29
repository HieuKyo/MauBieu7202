"""
Model E-Learning: khóa học và ghi danh học viên.
"""
from django.db import models
from django.contrib.auth.models import User


# ====================
# E-Learning System Models
# ====================

class Course(models.Model):
    """Khóa học E-Learning"""
    name = models.CharField(
        max_length=200,
        verbose_name="Tên khóa học"
    )
    start_date = models.DateField(
        verbose_name="Ngày bắt đầu"
    )
    end_date = models.DateField(
        verbose_name="Ngày kết thúc"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Ghi chú"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Khóa học"
        verbose_name_plural = "Khóa học"
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def get_completion_stats(self):
        """Trả về thống kê hoàn thành (completed / total)"""
        total = self.enrollments.count()
        completed = self.enrollments.filter(is_completed=True).count()
        return {'completed': completed, 'total': total}


class CourseEnrollment(models.Model):
    """Ghi danh khóa học - Học viên"""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="Khóa học"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='course_enrollments',
        verbose_name="Người học"
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name="Đã hoàn thành"
    )
    completion_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Ngày hoàn thành"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày ghi danh")

    class Meta:
        verbose_name = "Ghi danh khóa học"
        verbose_name_plural = "Ghi danh khóa học"
        unique_together = ['course', 'user']
        ordering = ['course', 'user__username']

    def __str__(self):
        return f"{self.course.name} - {self.user.username}"

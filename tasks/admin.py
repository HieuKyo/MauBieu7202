from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'priority',
        'category',
        'due_date',
        'is_completed',
        'recurring_type',
        'created_by',
        'created_at',
    ]
    list_filter = [
        'priority',
        'category',
        'is_completed',
        'recurring_type',
        'created_at',
    ]
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
    ordering = ['-priority', 'due_date', '-created_at']

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('title', 'description', 'due_date')
        }),
        ('Phân loại', {
            'fields': ('priority', 'category', 'recurring_type')
        }),
        ('Trạng thái', {
            'fields': ('is_completed', 'completed_at')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at', 'completed_at']

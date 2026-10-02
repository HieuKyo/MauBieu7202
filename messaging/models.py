from django.contrib.auth.models import User, Group
from django.db import models


class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.CASCADE, related_name='received_messages'
    )
    recipient_group = models.ForeignKey(
        Group, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='group_messages'
    )
    subject = models.CharField('Tiêu đề', max_length=200, blank=True)
    content = models.TextField('Nội dung')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient_group', '-created_at']),
        ]

    def __str__(self):
        target = self.recipient or self.recipient_group
        return f'{self.sender} → {target}: {self.subject or self.content[:30]}'

    @property
    def display_recipient(self):
        if self.recipient:
            return self.recipient.get_full_name() or self.recipient.username
        if self.recipient_group:
            return f'[Nhóm] {self.recipient_group.name}'
        return '—'


class MessageRead(models.Model):
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name='reads'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['message', 'user']
        indexes = [models.Index(fields=['user', 'message'])]
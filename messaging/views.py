from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import Message, MessageRead


def _inbox_qs(user):
    """Trả về QuerySet tất cả tin nhắn mà user được nhận (DM + nhóm)."""
    return Message.objects.filter(
        Q(recipient=user) | Q(recipient_group__in=user.groups.all())
    ).distinct().select_related('sender', 'recipient', 'recipient_group')


def _read_ids(user, qs):
    return set(
        MessageRead.objects.filter(user=user, message__in=qs)
        .values_list('message_id', flat=True)
    )


@login_required
def inbox_view(request):
    user = request.user
    received = _inbox_qs(user).order_by('-created_at')
    sent = Message.objects.filter(sender=user).select_related(
        'recipient', 'recipient_group'
    ).order_by('-created_at')

    read_ids = _read_ids(user, received)
    unread_count = received.exclude(id__in=read_ids).count()

    inbox_items = [
        {'msg': m, 'is_read': m.id in read_ids}
        for m in received
    ]

    users = User.objects.exclude(pk=user.pk).filter(is_active=True).order_by('username')
    groups = Group.objects.all().order_by('name')

    return render(request, 'messaging/inbox.html', {
        'inbox_items': inbox_items,
        'sent': sent,
        'unread_count': unread_count,
        'users': users,
        'groups': groups,
    })


@login_required
@require_POST
def send_message(request):
    content = request.POST.get('content', '').strip()
    subject = request.POST.get('subject', '').strip()
    recipient_type = request.POST.get('recipient_type', 'user')

    if not content:
        return JsonResponse({'error': 'Nội dung không được để trống.'}, status=400)

    msg = Message(sender=request.user, subject=subject, content=content)

    if recipient_type == 'user':
        rid = request.POST.get('recipient_id')
        if not rid:
            return JsonResponse({'error': 'Chưa chọn người nhận.'}, status=400)
        msg.recipient = get_object_or_404(User, pk=rid)
    else:
        gid = request.POST.get('group_id')
        if not gid:
            return JsonResponse({'error': 'Chưa chọn nhóm.'}, status=400)
        msg.recipient_group = get_object_or_404(Group, pk=gid)

    msg.save()
    return JsonResponse({'success': True})


@login_required
@require_POST
def mark_read(request, message_id):
    user = request.user
    msg = get_object_or_404(_inbox_qs(user), pk=message_id)
    MessageRead.objects.get_or_create(message=msg, user=user)
    return JsonResponse({'success': True})


@login_required
@require_POST
def delete_message(request, message_id):
    """Xóa tin nhắn (chỉ người gửi hoặc người nhận của DM)."""
    user = request.user
    msg = get_object_or_404(
        Message,
        Q(sender=user) | Q(recipient=user) | Q(recipient_group__in=user.groups.all()),
        pk=message_id
    )
    # Nếu là DM và user là người nhận → chỉ đánh dấu đã xóa bằng cách tạo read
    # Nếu là người gửi → xóa hẳn
    if msg.sender == user:
        msg.delete()
    else:
        # Người nhận xóa → chỉ mark read (không xóa cho bên kia)
        MessageRead.objects.get_or_create(message=msg, user=user)
    return JsonResponse({'success': True})


@login_required
def api_check(request):
    """
    Polling endpoint: trả về số tin chưa đọc và danh sách tin mới
    kể từ timestamp 'since' (milliseconds).
    """
    user = request.user
    received = _inbox_qs(user)
    read_ids = _read_ids(user, received)
    unread_count = received.exclude(id__in=read_ids).count()

    new_messages = []
    since_ms = request.GET.get('since')
    if since_ms:
        from datetime import datetime, timezone
        since_dt = datetime.fromtimestamp(float(since_ms) / 1000, tz=timezone.utc)
        fresh = received.filter(created_at__gt=since_dt).exclude(
            id__in=read_ids
        ).exclude(sender=user)[:5]
        new_messages = [
            {
                'id': m.id,
                'sender': m.sender.get_full_name() or m.sender.username,
                'subject': m.subject or '',
                'content': m.content,
            }
            for m in fresh
        ]

    return JsonResponse({'unread_count': unread_count, 'new_messages': new_messages})
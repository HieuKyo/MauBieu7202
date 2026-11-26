"""Ghi chú cập nhật: hiển thị docs/GHI_CHU_CAP_NHAT.md (mỗi mục "## " là một bản cập nhật)."""
import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.html import escape

from .context_processors import APP_VERSION

GHI_CHU_FILE = settings.BASE_DIR / 'docs' / 'GHI_CHU_CAP_NHAT.md'


def _inline(text):
    """**đậm** và `mã` → HTML (đã escape trước)."""
    text = escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    return re.sub(r'`(.+?)`', r'<code>\1</code>', text)


def _parse(md):
    """→ [{'tieu_de', 'phien_ban', 'muc': [{'ten', 'dong': [(cấp lùi, html)]}]}]"""
    ban = []
    for line in md.splitlines():
        if line.startswith('## '):
            tieu_de = line[3:].strip()
            ban.append({'tieu_de': tieu_de, 'phien_ban': tieu_de.split(' ')[0], 'muc': []})
        elif not ban:
            continue  # phần giới thiệu đầu file
        elif line.startswith('### '):
            ban[-1]['muc'].append({'ten': line[4:].strip(), 'dong': []})
        elif line.lstrip().startswith('- ') and ban[-1]['muc']:
            cap = (len(line) - len(line.lstrip())) // 2
            ban[-1]['muc'][-1]['dong'].append((cap, _inline(line.lstrip()[2:])))
    return ban


@login_required
def ghi_chu_cap_nhat(request):
    try:
        md = GHI_CHU_FILE.read_text(encoding='utf-8')
    except FileNotFoundError:
        md = ''
    return render(request, 'templates_app/ghi_chu_cap_nhat.html', {
        'ban_list': _parse(md),
        'phien_ban_may': APP_VERSION,
    })

"""
Custom Storage Backend cho Template Files
Hỗ trợ fallback từ folder offline (maubieumoi) sang media folder
"""
import os
import shutil
from pathlib import Path
from django.core.files.storage import FileSystemStorage
from django.conf import settings


class HybridTemplateStorage(FileSystemStorage):
    """
    Custom storage với fallback mechanism:
    1. Ưu tiên đọc từ OFFLINE_TEMPLATE_PATH (folder maubieumoi)
    2. Nếu không tìm thấy → Fallback sang MEDIA_ROOT/templates/docx/
    3. Auto-copy từ offline sang media để cache (optional)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Đường dẫn tới folder offline (maubieumoi)
        # Có thể config qua settings.py hoặc environment variable
        self.offline_path = getattr(
            settings,
            'OFFLINE_TEMPLATE_PATH',
            '/home/user/maubieumoi'  # Default path
        )

        # Enable auto-cache (copy từ offline sang media)
        self.auto_cache = getattr(
            settings,
            'TEMPLATE_AUTO_CACHE',
            True  # Default: enabled
        )

    def _get_offline_full_path(self, name):
        """
        Lấy đường dẫn đầy đủ trong offline folder
        HỖ TRỢ TÌM KIẾM TRONG SUBDIRECTORIES (ATM, DICHVU, DIENTOAN, ...)

        Args:
            name: Tên file (ví dụ: "template.docx" hoặc "templates/docx/template.docx")

        Returns:
            Path object hoặc None nếu không tìm thấy
        """
        # Lấy base filename (bỏ qua "templates/docx/" prefix)
        base_name = os.path.basename(name)
        offline_root = Path(self.offline_path)

        # Trước tiên, thử tìm ở root folder
        direct_path = offline_root / base_name
        if direct_path.exists():
            return direct_path

        # Nếu không có, tìm trong tất cả subdirectories (ATM, DICHVU, ...)
        # Dùng recursive glob để tìm trong tất cả folder con
        try:
            matches = list(offline_root.rglob(base_name))
            if matches:
                # Nếu tìm thấy, trả về file đầu tiên
                return matches[0]
        except Exception as e:
            print(f"⚠ Warning: Error searching in subdirectories: {e}")

        # Không tìm thấy → Trả về path mặc định (sẽ báo lỗi sau)
        return offline_root / base_name

    def _get_media_full_path(self, name):
        """Lấy đường dẫn đầy đủ trong media folder"""
        return Path(self.location) / name

    def _open(self, name, mode='rb'):
        """
        Override _open để hỗ trợ fallback:
        1. Thử đọc từ offline folder trước
        2. Nếu không có → Đọc từ media folder
        3. Nếu tìm thấy trong offline và auto_cache=True → Copy sang media
        """
        offline_path = self._get_offline_full_path(name)
        media_path = self._get_media_full_path(name)

        # Priority 1: Offline folder (maubieumoi)
        if offline_path.exists():
            print(f"✓ Template found in offline folder: {offline_path}")

            # Auto-cache: Copy sang media folder để lần sau nhanh hơn
            if self.auto_cache and not media_path.exists():
                try:
                    media_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(offline_path, media_path)
                    print(f"✓ Cached to media folder: {media_path}")
                except Exception as e:
                    print(f"⚠ Warning: Could not cache file: {e}")

            # Return file từ offline folder
            return open(offline_path, mode)

        # Priority 2: Media folder (fallback)
        if media_path.exists():
            print(f"✓ Template found in media folder: {media_path}")
            return open(media_path, mode)

        # File không tồn tại ở cả 2 nơi
        raise FileNotFoundError(
            f"Template not found in both offline ({offline_path}) "
            f"and media ({media_path}) folders"
        )

    def exists(self, name):
        """
        Kiểm tra file có tồn tại không (check cả 2 nơi)
        """
        offline_path = self._get_offline_full_path(name)
        media_path = self._get_media_full_path(name)

        return offline_path.exists() or media_path.exists()

    def path(self, name):
        """
        Trả về đường dẫn tới file (ưu tiên offline)
        """
        offline_path = self._get_offline_full_path(name)
        if offline_path.exists():
            return str(offline_path)

        media_path = self._get_media_full_path(name)
        if media_path.exists():
            return str(media_path)

        # Return media path as default (để FileField có thể save vào đó)
        return str(media_path)

    def url(self, name):
        """
        Trả về URL để download file
        (Luôn dùng media URL vì offline folder không serve qua web)
        """
        # Nếu file chưa có trong media, copy từ offline
        offline_path = self._get_offline_full_path(name)
        media_path = self._get_media_full_path(name)

        if offline_path.exists() and not media_path.exists():
            try:
                media_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(offline_path, media_path)
            except Exception as e:
                print(f"⚠ Warning: Could not copy file for URL: {e}")

        # Return standard media URL
        return super().url(name)


class OfflineOnlyStorage(FileSystemStorage):
    """
    Storage chỉ đọc từ offline folder (không fallback)

    Sử dụng khi:
    - Muốn force tất cả templates phải nằm trong maubieumoi
    - Không muốn cache vào media folder
    """

    def __init__(self, *args, **kwargs):
        # Override location thành offline path
        offline_path = getattr(
            settings,
            'OFFLINE_TEMPLATE_PATH',
            '/home/user/maubieumoi'
        )
        kwargs['location'] = offline_path
        super().__init__(*args, **kwargs)

"""Tạo gói cập nhật cho máy LAN (chạy trên máy dev qua tao_ban_cap_nhat.bat).

- Lấy các file đã đổi trong git từ bản phát hành trước (tag release-*) tới HEAD.
  Chưa có tag nào, hoặc chạy với --full -> đóng gói toàn bộ code.
- Gói là thư mục CapNhat_MauBieu_<phiên bản>/ (cap_nhat.bat, khoi_phuc.bat, apply_update.py,
  manifest.json, files.zip). Không cần giải nén trên máy LAN -> tránh lỗi tên file tiếng Việt.
- Tự tìm USB đang cắm để ghi gói; không có USB -> lưu vào ban_cap_nhat/.
- Đóng gói xong mới gắn tag release-<phiên bản> vào HEAD.
"""
import ctypes
import io
import json
import shutil
import string
import subprocess
import sys
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE_DIR = Path(__file__).resolve().parent
LOCAL_OUT = ROOT / 'ban_cap_nhat'
USB_FOLDER = 'CapNhat_MauBieu'
KEEP_LOCAL = 3

# Không bao giờ đưa vào gói (dữ liệu riêng của từng máy)
EXCLUDE_PREFIXES = ('db.sqlite3', 'media/', 'private_media/', 'staticfiles/', 'venv/',
                    '.env', 'samples/', 'backups/', 'ban_cap_nhat/', '.claude/', 'VERSION')
PIP_TRIGGERS = ('requirements.txt', 'packages/')


def git(*args, binary=False):
    out = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, check=True).stdout
    return out if binary else out.decode('utf-8')


def ask(prompt, default='n'):
    ans = input(prompt).strip().lower()
    return (ans or default) == 'y'


def is_excluded(path):
    return path.startswith(EXCLUDE_PREFIXES) or '.bak' in path.rsplit('/', 1)[-1]


def last_release_tag():
    try:
        return git('describe', '--tags', '--abbrev=0', '--match', 'release-*', 'HEAD').strip()
    except subprocess.CalledProcessError:
        return None


def next_version():
    base = datetime.now().strftime('%Y.%m.%d')
    existing = set(git('tag', '--list', f'release-{base}*').split())
    version, n = base, 1
    while f'release-{version}' in existing:
        n += 1
        version = f'{base}.{n}'
    return version


def collect_changes(tag, full):
    if full:
        files = [p for p in git('ls-tree', '-r', '-z', '--name-only', 'HEAD').split('\0') if p]
        return files, []
    parts = [p for p in git('diff', '--name-status', '-z', '--no-renames', tag, 'HEAD').split('\0') if p]
    changed, deleted = [], []
    for status, path in zip(parts[0::2], parts[1::2]):
        (deleted if status == 'D' else changed).append(path)
    return changed, deleted


def removable_drives():
    """Các ổ USB đang cắm: [(gốc ổ, tên ổ, dung lượng trống)]."""
    k32 = ctypes.windll.kernel32
    drives = []
    mask = k32.GetLogicalDrives()
    for i, letter in enumerate(string.ascii_uppercase):
        if not mask & (1 << i) or letter in 'AB':
            continue
        root = f'{letter}:\\'
        if k32.GetDriveTypeW(root) != 2:  # DRIVE_REMOVABLE
            continue
        label = ctypes.create_unicode_buffer(261)
        if not k32.GetVolumeInformationW(root, label, 261, None, None, None, None, 0):
            continue  # khe thẻ nhớ trống
        drives.append((root, label.value or 'USB', shutil.disk_usage(root).free))
    return drives


def choose_destination():
    drives = removable_drives()
    if len(drives) == 1:
        root, label, _ = drives[0]
        print(f'Tìm thấy USB: {label} ({root})')
        return Path(root) / USB_FOLDER
    if len(drives) > 1:
        print('Có nhiều USB đang cắm:')
        for i, (root, label, free) in enumerate(drives, 1):
            print(f'  {i}. {label} ({root}) - trống {free / 2**30:.1f} GB')
        print('  0. Không dùng USB, lưu vào thư mục ban_cap_nhat')
        while True:
            choice = input('Chọn số: ').strip()
            if choice == '0':
                return LOCAL_OUT
            if choice.isdigit() and 1 <= int(choice) <= len(drives):
                return Path(drives[int(choice) - 1][0]) / USB_FOLDER
    print('Không tìm thấy USB nào -> lưu vào thư mục ban_cap_nhat của dự án.')
    return LOCAL_OUT


def build_payload(version, base_version, full, changed, deleted):
    pip_install = any(p.startswith(PIP_TRIGGERS) for p in changed + deleted)
    manifest = {
        'version': version,
        'base': base_version,
        'full': full,
        'commit': git('rev-parse', '--short', 'HEAD').strip(),
        'created': datetime.now().isoformat(timespec='seconds'),
        'changed': changed,
        'deleted': deleted,
        'pip_install': pip_install,
    }

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        wanted = set(changed)
        if wanted:
            tar_bytes = git('archive', '--format=tar', 'HEAD', binary=True)
            with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tf:
                for member in tf:
                    if member.isfile() and member.name in wanted:
                        zf.writestr(member.name, tf.extractfile(member).read())
                        wanted.discard(member.name)
        if wanted:
            raise RuntimeError(f'Không lấy được {len(wanted)} file từ git: {sorted(wanted)[:5]}')
    return manifest, buf.getvalue()


def main():
    full = '--full' in sys.argv[1:]
    print('=' * 60)
    print(' TẠO GÓI CẬP NHẬT MauBieu7202')
    print('=' * 60)

    dirty = [l for l in git('status', '--porcelain').splitlines() if l.strip()]
    if dirty:
        print(f'\nCẢNH BÁO: còn {len(dirty)} file chưa commit. Gói chỉ lấy theo commit mới nhất,')
        print('các thay đổi chưa commit sẽ KHÔNG có trong gói:')
        for line in dirty[:15]:
            print('   ', line)
        if len(dirty) > 15:
            print(f'    ... và {len(dirty) - 15} file khác')
        if not ask('Vẫn tạo gói? [y/N]: '):
            return 1

    tag = last_release_tag()
    if tag is None and not full:
        print('\nChưa có bản phát hành nào -> đóng gói TOÀN BỘ code (lần đầu).')
        full = True
    if tag and not full and git('rev-parse', tag + '^{commit}') == git('rev-parse', 'HEAD'):
        print(f'\nKhông có commit mới kể từ bản {tag[8:]}. Không cần tạo gói.')
        return 0

    base_version = tag[8:] if tag else None
    version = next_version()
    changed, deleted = collect_changes(tag, full)
    changed = [p for p in changed if not is_excluded(p)]
    deleted = [p for p in deleted if not is_excluded(p)]
    if not changed and not deleted:
        print('\nCác commit mới không có file nào cần cập nhật.')
        return 0

    print(f'\nPhiên bản mới : {version}')
    print(f'Dựa trên bản  : {base_version or "(không - gói đầy đủ)"}{"  [gói đầy đủ]" if full and base_version else ""}')
    print(f'File thêm/sửa : {len(changed)}')
    print(f'File xóa      : {len(deleted)}')

    manifest, data = build_payload(version, base_version, full, changed, deleted)
    if manifest['pip_install']:
        print('Có thay đổi thư viện -> máy LAN sẽ tự cài lại từ packages/.')

    dest = choose_destination()
    dest.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(dest).free < len(data) + 1_000_000:
        print(f'\nLỖI: {dest} không đủ chỗ trống (cần {len(data) / 2**20:.1f} MB).')
        return 1
    target = dest / f'CapNhat_MauBieu_{version}'
    tmp = dest / f'{target.name}.dang_tao'
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir()
    (tmp / 'files.zip').write_bytes(data)
    (tmp / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    for name in ('apply_update.py', 'cap_nhat.bat', 'khoi_phuc.bat'):
        shutil.copy2(RELEASE_DIR / name, tmp / name)
    shutil.rmtree(target, ignore_errors=True)
    tmp.rename(target)

    git('tag', '-a', f'release-{version}', '-m', f'Gói cập nhật LAN {version}')

    if dest == LOCAL_OUT:
        old = sorted(LOCAL_OUT.glob('CapNhat_MauBieu_*'), key=lambda p: p.stat().st_mtime)
        for p in old[:-KEEP_LOCAL]:
            shutil.rmtree(p, ignore_errors=True)

    print('\n' + '=' * 60)
    print(f' ĐÃ TẠO GÓI: {target}')
    print(f' Dung lượng : {len(data) / 2**20:.1f} MB')
    print('=' * 60)
    print('Trên máy LAN: chép thư mục này từ USB vào máy -> tắt server -> chạy cap_nhat.bat')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as e:
        print('LỖI git:', (e.stderr or b'').decode('utf-8', 'replace'))
        sys.exit(1)

"""Áp dụng gói cập nhật trên máy LAN (cap_nhat.bat) hoặc quay về bản trước (khoi_phuc.bat --restore).

Cập nhật: sao lưu db.sqlite3 + các file sắp bị thay vào backups/<thời gian>_<phiên bản>/,
chép file mới, xóa file cũ, cài thư viện (nếu cần), migrate, collectstatic, ghi VERSION.
Lỗi ở bất kỳ bước nào -> tự khôi phục từ bản sao lưu vừa tạo.
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parent
PORT = 8888
KEEP_BACKUPS = 5
SAVED_PATH = Path(os.environ.get('APPDATA', Path.home())) / 'MauBieu7202' / 'install_path.txt'

log_file = None


def log(msg=''):
    print(msg)
    if log_file:
        log_file.write(msg + '\n')
        log_file.flush()


def ask(prompt, default='n'):
    ans = input(prompt).strip().lower()
    return (ans or default) == 'y'


def is_install_dir(p):
    return (p / 'manage.py').is_file() and (p / 'wordgen' / 'settings.py').is_file()


def find_install_dir():
    candidates = []
    if SAVED_PATH.is_file():
        candidates.append(Path(SAVED_PATH.read_text(encoding='utf-8').strip()))
    candidates += [PKG_DIR.parent, PKG_DIR.parent.parent, Path.cwd()]
    for c in candidates:
        if c and is_install_dir(c):
            return c
    while True:
        raw = input('Không tìm thấy thư mục cài đặt MauBieu7202.\n'
                    'Nhập đường dẫn (thư mục chứa manage.py, có thể kéo thả vào đây): ').strip().strip('"')
        p = Path(raw)
        if is_install_dir(p):
            return p
        print('  -> Không phải thư mục MauBieu7202 (thiếu manage.py).')


def remember_install_dir(p):
    try:
        SAVED_PATH.parent.mkdir(parents=True, exist_ok=True)
        SAVED_PATH.write_text(str(p), encoding='utf-8')
    except OSError:
        pass


def wait_server_stopped():
    while True:
        with socket.socket() as s:
            s.settimeout(0.5)
            if s.connect_ex(('127.0.0.1', PORT)) != 0:
                return
        print(f'\nServer đang chạy (cổng {PORT}). Hãy tắt cửa sổ run.bat (Ctrl+C) rồi bấm Enter.')
        input()


def read_version(target):
    try:
        return (target / 'VERSION').read_text(encoding='utf-8').strip() or None
    except OSError:
        return None


def run(target, *args):
    log(f'\n> python {" ".join(args)}')
    proc = subprocess.run([sys.executable, *args], cwd=target, capture_output=True,
                          text=True, encoding='utf-8', errors='replace')
    out = (proc.stdout + proc.stderr).strip()
    if out:
        log(out)
    if proc.returncode != 0:
        raise RuntimeError(f'Lệnh "python {" ".join(args)}" bị lỗi (mã {proc.returncode}).')


def restore(target, backup):
    """Trả lại db, file và VERSION như trước khi cập nhật."""
    info = json.loads((backup / 'restore.json').read_text(encoding='utf-8'))
    for rel in info['added']:
        p = target / rel
        if p.is_file():
            p.unlink()
    for rel in info['existed']:
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup / 'files' / rel, dst)
    if info['db']:
        shutil.copy2(backup / 'db.sqlite3', target / 'db.sqlite3')
    if info['old_version']:
        (target / 'VERSION').write_text(info['old_version'], encoding='utf-8')
    elif (target / 'VERSION').exists():
        (target / 'VERSION').unlink()
    try:
        run(target, 'manage.py', 'collectstatic', '--noinput')
    except RuntimeError as e:
        log(f'Cảnh báo: {e}')
    (backup / 'restore.json').rename(backup / 'restored.json')


def do_update(target):
    global log_file
    manifest = json.loads((PKG_DIR / 'manifest.json').read_text(encoding='utf-8'))
    new_ver, base, full = manifest['version'], manifest['base'], manifest['full']
    changed, deleted = manifest['changed'], manifest['deleted']
    cur_ver = read_version(target)

    print(f'Thư mục cài đặt : {target}')
    print(f'Bản đang chạy   : {cur_ver or "chưa rõ (bản cũ)"}')
    print(f'Bản cập nhật    : {new_ver}{"  [gói đầy đủ]" if full else ""}')
    print(f'File thêm/sửa   : {len(changed)}')
    print(f'File xóa        : {len(deleted)}')
    if manifest['pip_install']:
        print('Thư viện        : có thay đổi, sẽ cài lại từ packages/')

    if cur_ver == new_ver:
        print(f'\nMáy này ĐÃ ở bản {new_ver}.')
        if not ask('Chạy lại cập nhật? [y/N]: '):
            return 0
    elif not full and cur_ver != base:
        print(f'\nCẢNH BÁO: gói này cập nhật từ bản {base}, nhưng máy đang ở bản {cur_ver or "chưa rõ"}.')
        print('Có thể đã bỏ sót gói cập nhật trước đó. Nên chạy các gói còn thiếu,')
        print('hoặc tạo gói đầy đủ (tao_ban_cap_nhat.bat --full) trên máy dev.')
        if not ask('Vẫn tiếp tục? [y/N]: '):
            return 0
    if not ask('\nBắt đầu cập nhật? [Y/n]: ', default='y'):
        return 0

    wait_server_stopped()

    backup = target / 'backups' / f'{datetime.now():%Y%m%d_%H%M%S}_{new_ver}'
    (backup / 'files').mkdir(parents=True)
    log_file = open(backup / 'log.txt', 'w', encoding='utf-8')
    log(f'Cập nhật {cur_ver or "?"} -> {new_ver} lúc {datetime.now():%d/%m/%Y %H:%M:%S}')

    # 1. Sao lưu
    log('\n[1/5] Sao lưu dữ liệu và file cũ...')
    db = target / 'db.sqlite3'
    if db.exists():
        shutil.copy2(db, backup / 'db.sqlite3')
    existed, added = [], []
    for rel in changed + deleted:
        src = target / rel
        if src.is_file():
            dst = backup / 'files' / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            existed.append(rel)
        elif rel in changed:
            added.append(rel)
    (backup / 'restore.json').write_text(json.dumps({
        'from_version': cur_ver, 'to_version': new_ver, 'old_version': cur_ver,
        'db': db.exists(), 'existed': existed, 'added': added,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    log(f'      Đã sao lưu vào: {backup}')

    try:
        # 2. Chép file mới, xóa file cũ
        log('\n[2/5] Chép file mới...')
        with zipfile.ZipFile(PKG_DIR / 'files.zip') as zf:
            for rel in changed:
                dst = target / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(rel) as src, open(dst, 'wb') as out:
                    shutil.copyfileobj(src, out)
        for rel in deleted:
            p = target / rel
            if p.is_file():
                p.unlink()
        log(f'      {len(changed)} file đã chép, {len(deleted)} file đã xóa.')

        # 3. Thư viện
        log('\n[3/5] Thư viện...')
        if manifest['pip_install']:
            run(target, '-m', 'pip', 'install', '--no-index', '--find-links=packages', '-r', 'requirements.txt')
        else:
            log('      Không thay đổi, bỏ qua.')

        # 4. Database
        log('\n[4/5] Cập nhật database (migrate)...')
        run(target, 'manage.py', 'migrate', '--noinput')

        # 5. Static files
        log('\n[5/5] Cập nhật static files...')
        run(target, 'manage.py', 'collectstatic', '--noinput')

        (target / 'VERSION').write_text(new_ver, encoding='utf-8')
    except Exception as e:
        log(f'\nLỖI: {e}')
        log('Đang khôi phục lại bản trước...')
        restore(target, backup)
        log(f'Đã khôi phục về bản {cur_ver or "cũ"}. Hệ thống vẫn chạy được như trước khi cập nhật.')
        log(f'Chi tiết lỗi: {backup / "log.txt"}')
        return 1

    # Mỗi bản sao lưu chứa cả database (~300MB) -> chỉ giữ vài bản gần nhất
    for old in sorted((target / 'backups').iterdir())[:-KEEP_BACKUPS]:
        shutil.rmtree(old, ignore_errors=True)

    log('\n' + '=' * 60)
    log(f' CẬP NHẬT THÀNH CÔNG -> phiên bản {new_ver}')
    log('=' * 60)
    log('Chạy run.bat để khởi động lại server.')
    log('Nếu dùng thấy lỗi, chạy khoi_phuc.bat để quay về bản trước.')
    return 0


def do_restore(target):
    global log_file
    backups = sorted((target / 'backups').glob('*/restore.json'), reverse=True)
    if not backups:
        print('Không có bản sao lưu nào để khôi phục.')
        return 1
    backup = backups[0].parent
    info = json.loads(backups[0].read_text(encoding='utf-8'))
    print(f'Bản hiện tại   : {read_version(target) or "chưa rõ"}')
    print(f'Quay về bản    : {info["from_version"] or "cũ (trước khi có số phiên bản)"}')
    print(f'Bản sao lưu lúc: {backup.name[:15]}')
    if info['db']:
        print('\nLƯU Ý: database sẽ trả về lúc sao lưu. Dữ liệu nhập sau thời điểm đó sẽ mất')
        print('(database hiện tại được giữ lại trong thư mục sao lưu: db_truoc_khoi_phuc.sqlite3).')
    if not ask('\nKhôi phục? [y/N]: '):
        return 0

    wait_server_stopped()
    log_file = open(backup / 'log_khoi_phuc.txt', 'w', encoding='utf-8')
    if info['db'] and (target / 'db.sqlite3').exists():
        shutil.copy2(target / 'db.sqlite3', backup / 'db_truoc_khoi_phuc.sqlite3')
    restore(target, backup)
    log(f'\nĐÃ KHÔI PHỤC về bản {info["from_version"] or "cũ"}. Chạy run.bat để khởi động lại server.')
    return 0


def main():
    target = find_install_dir()
    remember_install_dir(target)
    print('=' * 60)
    if '--restore' in sys.argv[1:]:
        print(' KHÔI PHỤC BẢN TRƯỚC - MauBieu7202')
        print('=' * 60)
        return do_restore(target)
    print(' CẬP NHẬT MauBieu7202')
    print('=' * 60)
    return do_update(target)


if __name__ == '__main__':
    try:
        code = main()
    except KeyboardInterrupt:
        code = 1
    finally:
        if log_file:
            log_file.close()
    sys.exit(code)

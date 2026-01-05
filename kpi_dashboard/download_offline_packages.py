"""
Download Offline Packages Script
=================================
Script để download tất cả dependencies cần thiết cho offline deployment
Chạy script này trên máy có Internet, sau đó copy toàn bộ sang server offline
"""

import subprocess
import os
import sys
from pathlib import Path


def main():
    """
    Download tất cả packages cần thiết cho offline deployment
    """
    print("=" * 70)
    print("  KPI Dashboard - Offline Package Downloader")
    print("=" * 70)
    print()
    print("Script này sẽ download tất cả dependencies cần thiết")
    print("để chạy KPI Dashboard trong môi trường OFFLINE/LAN")
    print()

    # Tạo thư mục packages
    packages_dir = Path("offline_packages")
    packages_dir.mkdir(exist_ok=True)

    print(f"📁 Thư mục lưu packages: {packages_dir.absolute()}")
    print()

    # Danh sách packages cần thiết
    required_packages = [
        "streamlit>=1.28.0",
        "pandas>=1.5.0",
        "openpyxl>=3.1.0",
        "xlrd>=2.0.0",
        "xlsxwriter>=3.0.0",
        "python-dateutil>=2.9.0",
        "pillow>=10.0.0"
    ]

    print("📦 Đang download packages:")
    for pkg in required_packages:
        print(f"  - {pkg}")
    print()

    # Download packages
    try:
        print("🔄 Bắt đầu download...")
        print("-" * 70)

        cmd = [
            sys.executable,
            "-m",
            "pip",
            "download",
            "--dest", str(packages_dir)
        ] + required_packages

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        print(result.stdout)

        print("-" * 70)
        print()
        print("✅ Download hoàn tất!")
        print()

        # Liệt kê các file đã download
        files = list(packages_dir.glob("*.whl")) + list(packages_dir.glob("*.tar.gz"))
        print(f"📊 Đã download {len(files)} packages:")
        for f in sorted(files):
            size = f.stat().st_size / 1024 / 1024  # MB
            print(f"  - {f.name} ({size:.2f} MB)")

        print()
        print("=" * 70)
        print("  Hướng dẫn sử dụng")
        print("=" * 70)
        print()
        print("1. Copy toàn bộ thư mục 'offline_packages' sang server offline")
        print()
        print("2. Trên server offline, chạy lệnh:")
        print()
        print("   Windows:")
        print("   pip install --no-index --find-links=offline_packages -r requirements.txt")
        print()
        print("   Linux/Mac:")
        print("   pip install --no-index --find-links=offline_packages -r requirements.txt")
        print()
        print("3. Hoặc cài từng package:")
        print("   pip install --no-index --find-links=offline_packages streamlit pandas openpyxl")
        print()
        print("=" * 70)
        print()
        print("✅ Sẵn sàng cho offline deployment!")
        print()

    except subprocess.CalledProcessError as e:
        print()
        print("❌ Lỗi khi download packages:")
        print(e.stderr)
        print()
        print("Vui lòng kiểm tra:")
        print("  - Kết nối Internet")
        print("  - pip đã được cài đặt")
        print("  - Quyền ghi file")
        sys.exit(1)

    except Exception as e:
        print()
        print(f"❌ Lỗi: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

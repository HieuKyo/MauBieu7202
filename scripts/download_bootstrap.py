"""
Download Bootstrap and Bootstrap Icons for offline use
This script downloads the necessary CSS and JS files for Bootstrap
"""

import urllib.request
import os
import sys

def download_file(url, filepath):
    """Download a file from URL to filepath"""
    try:
        print(f"Downloading: {url}")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Add headers to avoid being blocked
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read()

        with open(filepath, 'wb') as f:
            f.write(content)

        file_size = os.path.getsize(filepath)
        print(f"  ✓ Downloaded: {filepath} ({file_size:,} bytes)")
        return True

    except Exception as e:
        print(f"  ✗ Error downloading {url}: {e}")
        return False

def main():
    """Download all required static files"""

    print("=" * 60)
    print("Downloading Bootstrap 5.3.0 and Bootstrap Icons 1.11.0")
    print("=" * 60)
    print()

    # Base directory for static files
    base_dir = "templates_app/static/vendor"

    # Files to download
    files_to_download = [
        # Bootstrap CSS
        {
            'url': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
            'path': f'{base_dir}/bootstrap/css/bootstrap.min.css'
        },
        # Bootstrap JS Bundle
        {
            'url': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
            'path': f'{base_dir}/bootstrap/js/bootstrap.bundle.min.js'
        },
        # Bootstrap Icons CSS
        {
            'url': 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.min.css',
            'path': f'{base_dir}/bootstrap-icons/css/bootstrap-icons.min.css'
        },
        # Bootstrap Icons Fonts
        {
            'url': 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/fonts/bootstrap-icons.woff',
            'path': f'{base_dir}/bootstrap-icons/fonts/bootstrap-icons.woff'
        },
        {
            'url': 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/fonts/bootstrap-icons.woff2',
            'path': f'{base_dir}/bootstrap-icons/fonts/bootstrap-icons.woff2'
        }
    ]

    # Download all files
    success_count = 0
    failed_count = 0

    for file_info in files_to_download:
        if download_file(file_info['url'], file_info['path']):
            success_count += 1
        else:
            failed_count += 1
        print()

    # Summary
    print("=" * 60)
    print("Download Summary")
    print("=" * 60)
    print(f"Successful: {success_count}")
    print(f"Failed: {failed_count}")
    print()

    if failed_count > 0:
        print("⚠ Some files failed to download.")
        print("Please check your internet connection and try again.")
        print()
        print("Alternative: Download manually from:")
        print("  - Bootstrap: https://getbootstrap.com/docs/5.3/getting-started/download/")
        print("  - Bootstrap Icons: https://icons.getbootstrap.com/")
        sys.exit(1)
    else:
        print("✓ All files downloaded successfully!")
        print()
        print("Next steps:")
        print("  1. Run: python manage.py collectstatic")
        print("  2. Restart your server")
        print()

if __name__ == '__main__':
    main()

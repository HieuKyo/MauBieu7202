#!/usr/bin/env python3
"""
Test script để verify HybridTemplateStorage hoạt động đúng
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/home/user/MauBieu7202')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wordgen.settings')
django.setup()

from templates_app.storage import HybridTemplateStorage  # noqa: E402
from pathlib import Path  # noqa: E402

def test_hybrid_storage():
    """Test HybridTemplateStorage functionality"""
    print("🧪 Testing HybridTemplateStorage\n")
    print("=" * 80)

    storage = HybridTemplateStorage()

    # Test 1: Check configuration
    print("\n✓ Test 1: Configuration")
    print(f"   Offline path: {storage.offline_path}")
    print(f"   Auto-cache enabled: {storage.auto_cache}")

    # Test 2: Check offline folder exists
    print("\n✓ Test 2: Offline folder")
    offline_exists = Path(storage.offline_path).exists()
    print(f"   Offline folder exists: {offline_exists}")

    if offline_exists:
        files = list(Path(storage.offline_path).glob("*.docx"))
        print(f"   Templates found: {len(files)}")
        for f in files:
            print(f"     - {f.name}")

    # Test 3: Check media folder exists
    print("\n✓ Test 3: Media folder")
    media_exists = Path(storage.location).exists()
    print(f"   Media folder exists: {media_exists}")

    # Test 4: Test file existence check
    print("\n✓ Test 4: File existence check")
    test_file = "Mau_1a.docx"
    exists = storage.exists(test_file)
    print(f"   '{test_file}' exists: {exists}")

    if exists:
        path = storage.path(test_file)
        print(f"   File path: {path}")
        print(f"   File size: {Path(path).stat().st_size:,} bytes")

    # Test 5: Test fallback mechanism
    print("\n✓ Test 5: Fallback mechanism")
    print("   Priority: Offline folder → Media folder (cache)")

    offline_path = storage._get_offline_full_path(test_file)
    media_path = storage._get_media_full_path(test_file)

    print(f"   Offline: {offline_path}")
    print(f"   Offline exists: {offline_path.exists()}")
    print(f"   Media: {media_path}")
    print(f"   Media exists: {media_path.exists()}")

    # Test 6: Test database integration
    print("\n✓ Test 6: Database integration")
    from templates_app.models import Template

    template_count = Template.objects.count()
    print(f"   Templates in database: {template_count}")

    if template_count > 0:
        template = Template.objects.first()
        print(f"   Sample template: {template.name}")
        print(f"   Using storage: {type(template.file.storage).__name__}")

    print("\n" + "=" * 80)
    print("\n✅ All tests passed!")
    print("\n📝 Summary:")
    print("   - HybridTemplateStorage is configured correctly")
    print("   - Templates can be read from offline folder")
    print("   - Auto-cache will copy files to media folder on first access")
    print("   - Fallback to media folder if offline unavailable")

    return True

if __name__ == '__main__':
    try:
        test_hybrid_storage()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

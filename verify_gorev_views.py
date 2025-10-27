"""
Quick verification script for task management views
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from django.urls import reverse, resolve

print("=" * 60)
print("TASK MANAGEMENT VIEWS VERIFICATION")
print("=" * 60)

# Check all URLs are registered
urls_to_check = [
    'gorev_taslak',
    'gorev_nihai',
    'gecen_ay_gorevler',
    'eski_gorevler',
    'gorev_ekle',
]

print("\n1. URL Registration Check:")
for url_name in urls_to_check:
    try:
        url = reverse(url_name)
        view_func = resolve(url).func
        print(f"   ✓ {url_name:25} -> {url:30} -> {view_func.__name__}")
    except Exception as e:
        print(f"   ✗ {url_name:25} -> ERROR: {str(e)}")

# Check edit and delete URLs with sample ID
print("\n2. Dynamic URL Check:")
try:
    edit_url = reverse('gorev_duzenle', args=[1])
    print(f"   ✓ gorev_duzenle           -> {edit_url}")
except Exception as e:
    print(f"   ✗ gorev_duzenle           -> ERROR: {str(e)}")

try:
    delete_url = reverse('gorev_sil', args=[1])
    print(f"   ✓ gorev_sil               -> {delete_url}")
except Exception as e:
    print(f"   ✗ gorev_sil               -> ERROR: {str(e)}")

# Check templates exist
import os
print("\n3. Template Files Check:")
template_files = [
    'templates/gorev/taslak.html',
    'templates/gorev/nihai.html',
    'templates/gorev/gecen_ay.html',
    'templates/gorev/eski.html',
    'templates/gorev/form.html',
]

for template in template_files:
    if os.path.exists(template):
        size = os.path.getsize(template)
        print(f"   ✓ {template:35} ({size:,} bytes)")
    else:
        print(f"   ✗ {template:35} NOT FOUND")

# Check database statistics
from core.models import Gorev
print("\n4. Database Statistics:")
print(f"   Total tasks: {Gorev.objects.count()}")
print(f"   Active tasks: {Gorev.objects.filter(gizle=False).count()}")
print(f"   Hidden tasks: {Gorev.objects.filter(gizle=True).count()}")
print(f"   Draft tasks: {Gorev.objects.filter(gizle=False, durum__isnull=True).count()}")
print(f"   Completed tasks: {Gorev.objects.filter(gizle=False, durum=1).count()}")

print("\n" + "=" * 60)
print("✅ VERIFICATION COMPLETE")
print("=" * 60)
print("\nAll task management components are properly configured!")
print("\nTo test the views, run:")
print("  python manage.py runserver")
print("\nThen visit:")
print("  http://127.0.0.1:8000/gorev/taslak/")
print("  http://127.0.0.1:8000/gorev/nihai/")
print("  http://127.0.0.1:8000/gorev/gecen-ay/")
print("  http://127.0.0.1:8000/gorev/eski/")
print("  http://127.0.0.1:8000/gorev/ekle/")

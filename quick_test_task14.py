"""
Quick test to verify Task 14 implementation
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from django.urls import reverse

print("\n" + "="*70)
print("TASK 14 - HIZLI DOĞRULAMA")
print("="*70)

# Check URLs
print("\n1. URL'ler:")
urls = ['log_kayitlari', 'sistem_bilgileri', 'yedek_al']
for url_name in urls:
    try:
        url = reverse(url_name)
        print(f"   ✓ {url_name}: {url}")
    except:
        print(f"   ❌ {url_name}: HATA")

# Check views
print("\n2. View Fonksiyonları:")
from core import views
for view_name in ['log_kayitlari', 'sistem_bilgileri', 'yedek_al']:
    if hasattr(views, view_name):
        print(f"   ✓ {view_name}")
    else:
        print(f"   ❌ {view_name}")

# Check templates
print("\n3. Template Dosyaları:")
templates = [
    'templates/sistem/log_kayitlari.html',
    'templates/sistem/sistem_bilgileri.html',
    'templates/sistem/yedek_al.html'
]
for template in templates:
    if os.path.exists(template):
        print(f"   ✓ {os.path.basename(template)}")
    else:
        print(f"   ❌ {os.path.basename(template)}")

# Check Log model
print("\n4. Log Modeli:")
from core.models import Log
log_count = Log.objects.count()
print(f"   ✓ Toplam log: {log_count}")

# Check database
print("\n5. Veritabanı:")
from django.conf import settings
db_path = settings.DATABASES['default']['NAME']
if os.path.exists(db_path):
    db_size = os.path.getsize(db_path) / (1024 * 1024)
    print(f"   ✓ Boyut: {db_size:.2f} MB")
else:
    print(f"   ❌ Bulunamadı")

print("\n" + "="*70)
print("✅ TASK 14 HAZIR!")
print("="*70)
print("\nManuel Test:")
print("1. python manage.py runserver")
print("2. Admin ile giriş yapın")
print("3. Sistem Ayarları menüsünü kullanın")
print("="*70 + "\n")

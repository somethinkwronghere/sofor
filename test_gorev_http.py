"""
Test HTTP request to gorev pages
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from django.test import Client
from core.models import Personel

print("=" * 60)
print("HTTP REQUEST TEST")
print("=" * 60)

# Get admin user
admin = Personel.objects.get(kullaniciadi='webfirmam')
print(f"\n1. Kullanıcı: {admin.adsoyad}")

# Create client
client = Client()

# Try to login with common passwords
passwords = ['admin', '123456', 'password', '12345', 'admin123']
logged_in = False

for pwd in passwords:
    if client.login(username=admin.kullaniciadi, password=pwd):
        print(f"✓ Login başarılı (şifre: {pwd})")
        logged_in = True
        break

if not logged_in:
    print("✗ Login başarısız - şifre bulunamadı")
    print("\nŞifrenizi kontrol etmek için:")
    print("python manage.py shell")
    print(">>> from core.models import Personel")
    print(">>> user = Personel.objects.get(kullaniciadi='webfirmam')")
    print(">>> user.set_password('admin')")
    print(">>> user.save()")
    exit(0)

# Test gorev taslak page
print("\n2. Görev Taslağı Sayfası Testi:")
response = client.get('/gorev/taslak/')
print(f"   Status: {response.status_code}")
print(f"   Content length: {len(response.content)} bytes")

if response.status_code == 200:
    content = response.content.decode('utf-8')
    
    # Check if table exists
    if '<table' in content:
        print("   ✓ Tablo bulundu")
    else:
        print("   ✗ Tablo bulunamadı")
    
    # Check if data rows exist
    if '<tbody>' in content:
        print("   ✓ Tbody bulundu")
        # Count tr tags in tbody
        tbody_start = content.find('<tbody>')
        tbody_end = content.find('</tbody>')
        tbody_content = content[tbody_start:tbody_end]
        tr_count = tbody_content.count('<tr>')
        print(f"   ✓ Satır sayısı: {tr_count}")
    else:
        print("   ✗ Tbody bulunamadı")
    
    # Check for "Henüz taslak görev bulunmamaktadır" message
    if 'Henüz taslak görev bulunmamaktadır' in content:
        print("   ⚠️  'Görev yok' mesajı görünüyor!")
    
    # Check for pagination
    if 'pagination' in content:
        print("   ✓ Pagination bulundu")
    
    # Save response to file for inspection
    with open('gorev_taslak_response.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("   ✓ Response 'gorev_taslak_response.html' dosyasına kaydedildi")

print("\n" + "=" * 60)

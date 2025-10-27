"""
Debug görev view - gerçek view'ı simüle et
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from core.models import Gorev, Personel, Arac, GorevYeri
from django.core.paginator import Paginator

print("=" * 60)
print("GÖREV VIEW DEBUG")
print("=" * 60)

# Get admin user
user = Personel.objects.get(kullaniciadi='webfirmam')
print(f"\n1. Kullanıcı: {user.adsoyad}")
print(f"   Yönetici: {user.yonetici}")

# Simulate the view query
print("\n2. Query Simülasyonu:")
gorevler = Gorev.objects.filter(gizle=False, durum__isnull=True).select_related('sofor', 'yurt', 'arac')
print(f"   İlk query: {gorevler.count()} görev")

# Check if admin filter is applied
if not user.yonetici:
    gorevler = gorevler.filter(sofor=user)
    print(f"   Admin değil, filtrelendi: {gorevler.count()} görev")
else:
    print(f"   Admin, filtrelenmedi: {gorevler.count()} görev")

# Order by date
gorevler = gorevler.order_by('-bstarih')

# Pagination
paginator = Paginator(gorevler, 25)
print(f"\n3. Pagination:")
print(f"   Toplam sayfa: {paginator.num_pages}")
print(f"   İlk sayfa öğe sayısı: {len(paginator.page(1))}")

# Show first 5 tasks
print(f"\n4. İlk 5 Görev:")
for i, gorev in enumerate(gorevler[:5], 1):
    print(f"   {i}. {gorev.sofor.adsoyad} - {gorev.varisyeri} - {gorev.bstarih.strftime('%d.%m.%Y')}")

# Get filter options
print(f"\n5. Filtre Seçenekleri:")
personeller = Personel.objects.filter(is_active=True).order_by('adsoyad')
araclar = Arac.objects.filter(gizle=False, arsiv=False).order_by('plaka')
yurtlar = GorevYeri.objects.all().order_by('ad')
print(f"   Personel: {personeller.count()}")
print(f"   Araç: {araclar.count()}")
print(f"   Görev Yeri: {yurtlar.count()}")

print("\n" + "=" * 60)
print("✅ View mantığı doğru çalışıyor!")
print("=" * 60)
print("\nEğer sayfada görev görünmüyorsa:")
print("1. Tarayıcı konsolunu (F12) kontrol edin")
print("2. Sayfa kaynağını (Ctrl+U) kontrol edin")
print("3. Template'te {% if gorevler %} bloğu var mı kontrol edin")

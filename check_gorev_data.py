"""
Check if tasks are visible in the views
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from core.models import Gorev, Personel, GorevYeri, Arac
from django.utils import timezone
from datetime import timedelta

print("=" * 60)
print("GÖREV VERİLERİ KONTROLÜ")
print("=" * 60)

# Check draft tasks
print("\n1. TASLAK GÖREVLER (durum=NULL):")
taslak = Gorev.objects.filter(gizle=False, durum__isnull=True).order_by('-bstarih')[:5]
print(f"   Toplam: {Gorev.objects.filter(gizle=False, durum__isnull=True).count()}")
for g in taslak:
    print(f"   - {g.sofor.adsoyad} | {g.varisyeri} | {g.bstarih.strftime('%d.%m.%Y')}")

# Check completed tasks
print("\n2. TAMAMLANMIŞ GÖREVLER (durum=1):")
now = timezone.now()
current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
tamamlanmis = Gorev.objects.filter(
    gizle=False, 
    durum=1,
    bstarih__gte=current_month_start
).order_by('-bstarih')[:5]
print(f"   Bu ay tamamlanan: {Gorev.objects.filter(gizle=False, durum=1, bstarih__gte=current_month_start).count()}")
for g in tamamlanmis:
    print(f"   - {g.sofor.adsoyad} | {g.varisyeri} | {g.bstarih.strftime('%d.%m.%Y')}")

# Check last month
print("\n3. GEÇEN AY GÖREVLERİ:")
last_month_end = current_month_start - timedelta(days=1)
last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
gecen_ay = Gorev.objects.filter(
    gizle=False,
    bstarih__gte=last_month_start,
    bstarih__lte=last_month_end
).count()
print(f"   Toplam: {gecen_ay}")
print(f"   Tarih aralığı: {last_month_start.strftime('%d.%m.%Y')} - {last_month_end.strftime('%d.%m.%Y')}")

# Check old tasks
print("\n4. ESKİ GÖREVLER (2+ ay önce):")
from dateutil.relativedelta import relativedelta
two_months_ago = now - relativedelta(months=2)
eski = Gorev.objects.filter(
    gizle=False,
    bstarih__lt=two_months_ago
).count()
print(f"   Toplam: {eski}")
print(f"   {two_months_ago.strftime('%d.%m.%Y')} tarihinden önceki görevler")

# Check filter options
print("\n5. FİLTRE SEÇENEKLERİ:")
print(f"   Aktif personel: {Personel.objects.filter(is_active=True).count()}")
print(f"   Aktif araçlar: {Arac.objects.filter(gizle=False, arsiv=False).count()}")
print(f"   Görev yerleri: {GorevYeri.objects.count()}")

# Sample data for testing
print("\n6. ÖRNEK VERİ:")
sample = Gorev.objects.filter(gizle=False).first()
if sample:
    print(f"   ID: {sample.id}")
    print(f"   Personel: {sample.sofor.adsoyad}")
    print(f"   Görev Yeri: {sample.yurt.ad}")
    print(f"   Varış: {sample.varisyeri}")
    print(f"   Araç: {sample.arac.plaka if sample.arac else 'Yok'}")
    print(f"   Tarih: {sample.bstarih}")
    print(f"   Durum: {'Tamamlandı' if sample.durum == 1 else 'Taslak'}")
    print(f"   Gizli: {sample.gizle}")

print("\n" + "=" * 60)
print("✅ Veriler veritabanında mevcut!")
print("=" * 60)

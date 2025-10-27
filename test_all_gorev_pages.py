"""
Test all gorev pages with current date logic
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from core.models import Gorev
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import timedelta

print("=" * 60)
print("TÜM GÖREV SAYFALARI TEST")
print("=" * 60)

now = timezone.now()
print(f"\nŞu anki tarih: {now.strftime('%d.%m.%Y %H:%M')}")

# 1. TASLAK GÖREVLER (durum=NULL)
print("\n1. GÖREV TASLAĞI (durum=NULL):")
taslak = Gorev.objects.filter(gizle=False, durum__isnull=True)
print(f"   Toplam: {taslak.count()}")
if taslak.exists():
    first = taslak.order_by('-bstarih').first()
    print(f"   En yeni: {first.bstarih.strftime('%d.%m.%Y')} - {first.varisyeri}")
    last = taslak.order_by('bstarih').first()
    print(f"   En eski: {last.bstarih.strftime('%d.%m.%Y')} - {last.varisyeri}")

# 2. NİHAİ LİSTE (durum=1, bu ay)
print("\n2. NİHAİ LİSTE (durum=1, bu ay):")
current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
nihai = Gorev.objects.filter(gizle=False, durum=1, bstarih__gte=current_month_start)
print(f"   Bu ay başlangıç: {current_month_start.strftime('%d.%m.%Y')}")
print(f"   Toplam: {nihai.count()}")
if nihai.exists():
    first = nihai.order_by('-bstarih').first()
    print(f"   Örnek: {first.bstarih.strftime('%d.%m.%Y')} - {first.varisyeri}")

# 3. GEÇEN AY
print("\n3. GEÇEN AY GÖREVLERİ:")
last_month_end = current_month_start - timedelta(days=1)
last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
gecen_ay = Gorev.objects.filter(
    gizle=False,
    bstarih__gte=last_month_start,
    bstarih__lte=last_month_end
)
print(f"   Tarih aralığı: {last_month_start.strftime('%d.%m.%Y')} - {last_month_end.strftime('%d.%m.%Y')}")
print(f"   Toplam: {gecen_ay.count()}")
if gecen_ay.exists():
    first = gecen_ay.order_by('-bstarih').first()
    print(f"   Örnek: {first.bstarih.strftime('%d.%m.%Y')} - {first.varisyeri}")

# 4. ESKİ GÖREVLER (geçen aydan önce)
print("\n4. ESKİ GÖREVLER (geçen aydan önce):")
eski = Gorev.objects.filter(gizle=False, bstarih__lt=last_month_start)
print(f"   {last_month_start.strftime('%d.%m.%Y')} tarihinden önce")
print(f"   Toplam: {eski.count()}")
if eski.exists():
    first = eski.order_by('-bstarih').first()
    print(f"   En yeni: {first.bstarih.strftime('%d.%m.%Y')} - {first.varisyeri}")
    last = eski.order_by('bstarih').first()
    print(f"   En eski: {last.bstarih.strftime('%d.%m.%Y')} - {last.varisyeri}")

# Tüm görevlerin tarih dağılımı
print("\n5. TÜM GÖREVLERİN TARİH DAĞILIMI:")
all_gorevler = Gorev.objects.filter(gizle=False).order_by('bstarih')
if all_gorevler.exists():
    first_date = all_gorevler.first().bstarih
    last_date = all_gorevler.last().bstarih
    print(f"   İlk görev: {first_date.strftime('%d.%m.%Y')}")
    print(f"   Son görev: {last_date.strftime('%d.%m.%Y')}")
    print(f"   Toplam: {all_gorevler.count()}")

print("\n" + "=" * 60)
print("ÖNERİ:")
print("=" * 60)
print("Eğer görevler görünmüyorsa, tarihleri kontrol edin.")
print("Görevleriniz gelecekte olabilir (Kasım 2025).")
print("Bu durumda 'Görev Taslağı' sayfasında görünmelidir.")

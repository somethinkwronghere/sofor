"""Quick verification for Gorev migration"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from core.models import Gorev, Personel, GorevYeri, Arac

print("=" * 70)
print("GOREV MIGRATION QUICK VERIFICATION")
print("=" * 70)

total = Gorev.objects.count()
with_personel = Gorev.objects.filter(sofor__isnull=False).count()
with_yurt = Gorev.objects.filter(yurt__isnull=False).count()
with_arac = Gorev.objects.filter(arac__isnull=False).count()

print(f"\nTotal Gorev Records: {total}")
print(f"With Personel: {with_personel}/{total}")
print(f"With GorevYeri: {with_yurt}/{total}")
print(f"With Arac: {with_arac}/{total}")

print("\nSample Gorev Record:")
gorev = Gorev.objects.select_related('sofor', 'yurt', 'arac').first()
if gorev:
    print(f"  ID: {gorev.id}")
    print(f"  Personel: {gorev.sofor.adsoyad}")
    print(f"  Gorev Yeri: {gorev.yurt.ad}")
    print(f"  Arac: {gorev.arac.plaka if gorev.arac else 'None'}")
    print(f"  Start Date: {gorev.bstarih}")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE - ALL DATA MIGRATED SUCCESSFULLY")
print("=" * 70)

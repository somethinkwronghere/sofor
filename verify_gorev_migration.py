"""
Verification script for Gorev (Task) migration
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from core.models import Gorev, Personel, GorevYeri, Arac
from django.db.models import Count, Q

def verify_gorev_migration():
    """Verify Gorev data migration"""
    print("=" * 70)
    print("GÖREV MİGRASYONU DOĞRULAMA RAPORU")
    print("=" * 70)
    
    # Basic counts
    total_gorev = Gorev.objects.count()
    print(f"\n✓ Toplam Görev Sayısı: {total_gorev}")
    
    # Check foreign key relationships
    gorev_with_personel = Gorev.objects.filter(sofor__isnull=False).count()
    gorev_with_gorev_yeri = Gorev.objects.filter(yurt__isnull=False).count()
    gorev_with_arac = Gorev.objects.filter(arac__isnull=False).count()
    gorev_without_arac = Gorev.objects.filter(arac__isnull=True).count()
    
    print(f"\n✓ Personel İlişkisi Olan Görevler: {gorev_with_personel}")
    print(f"✓ Görev Yeri İlişkisi Olan Görevler: {gorev_with_gorev_yeri}")
    print(f"✓ Araç İlişkisi Olan Görevler: {gorev_with_arac}")
    print(f"✓ Araç İlişkisi Olmayan Görevler: {gorev_without_arac}")
    
    # Check date fields
    gorev_with_bstarih = Gorev.objects.filter(bstarih__isnull=False).count()
    gorev_with_bttarih = Gorev.objects.filter(bttarih__isnull=False).count()
    
    print(f"\n✓ Başlangıç Tarihi Olan Görevler: {gorev_with_bstarih}")
    print(f"✓ Bitiş Tarihi Olan Görevler: {gorev_with_bttarih}")
    
    # Check status fields
    gorev_gizli = Gorev.objects.filter(gizle=True).count()
    gorev_aktif = Gorev.objects.filter(gizle=False).count()
    
    print(f"\n✓ Gizli Görevler: {gorev_gizli}")
    print(f"✓ Aktif Görevler: {gorev_aktif}")
    
    # Check durum field
    durum_stats = Gorev.objects.values('durum').annotate(count=Count('id')).order_by('durum')
    print(f"\n✓ Durum Dağılımı:")
    for stat in durum_stats:
        durum = stat['durum'] if stat['durum'] is not None else 'NULL'
        print(f"  - Durum {durum}: {stat['count']} görev")
    
    # Sample data check
    print(f"\n✓ İlk 5 Görev Örneği:")
    for gorev in Gorev.objects.all()[:5]:
        print(f"  - ID: {gorev.id}, Personel: {gorev.sofor.adsoyad if gorev.sofor else 'N/A'}, "
              f"Görev Yeri: {gorev.yurt.ad if gorev.yurt else 'N/A'}, "
              f"Araç: {gorev.arac.plaka if gorev.arac else 'Yok'}, "
              f"Başlangıç: {gorev.bstarih.strftime('%Y-%m-%d %H:%M') if gorev.bstarih else 'N/A'}")
    
    # Check for orphaned records (foreign key issues)
    print(f"\n✓ Veri Bütünlüğü Kontrolleri:")
    
    # All gorev should have personel
    gorev_without_personel = Gorev.objects.filter(sofor__isnull=True).count()
    if gorev_without_personel > 0:
        print(f"  ⚠ UYARI: {gorev_without_personel} görev personel ilişkisi olmadan!")
    else:
        print(f"  ✓ Tüm görevlerin personel ilişkisi var")
    
    # All gorev should have gorev_yeri
    gorev_without_yurt = Gorev.objects.filter(yurt__isnull=True).count()
    if gorev_without_yurt > 0:
        print(f"  ⚠ UYARI: {gorev_without_yurt} görev görev yeri ilişkisi olmadan!")
    else:
        print(f"  ✓ Tüm görevlerin görev yeri ilişkisi var")
    
    # All gorev should have bstarih
    gorev_without_bstarih = Gorev.objects.filter(bstarih__isnull=True).count()
    if gorev_without_bstarih > 0:
        print(f"  ⚠ UYARI: {gorev_without_bstarih} görev başlangıç tarihi olmadan!")
    else:
        print(f"  ✓ Tüm görevlerin başlangıç tarihi var")
    
    # Statistics by personel
    print(f"\n✓ Personel Bazında Görev Dağılımı (İlk 10):")
    personel_stats = Gorev.objects.values('sofor__adsoyad').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    for stat in personel_stats:
        personel_name = stat['sofor__adsoyad'] if stat['sofor__adsoyad'] else 'Bilinmeyen'
        print(f"  - {personel_name}: {stat['count']} görev")
    
    # Statistics by gorev_yeri
    print(f"\n✓ Görev Yeri Bazında Görev Dağılımı (İlk 10):")
    yurt_stats = Gorev.objects.values('yurt__ad').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    for stat in yurt_stats:
        yurt_name = stat['yurt__ad'] if stat['yurt__ad'] else 'Bilinmeyen'
        print(f"  - {yurt_name}: {stat['count']} görev")
    
    # Statistics by year
    print(f"\n✓ Yıl Bazında Görev Dağılımı:")
    from django.db.models.functions import ExtractYear
    year_stats = Gorev.objects.annotate(
        year=ExtractYear('bstarih')
    ).values('year').annotate(count=Count('id')).order_by('year')
    
    for stat in year_stats:
        year = stat['year'] if stat['year'] else 'Tarih Yok'
        print(f"  - {year}: {stat['count']} görev")
    
    print("\n" + "=" * 70)
    print("DOĞRULAMA TAMAMLANDI")
    print("=" * 70)

if __name__ == '__main__':
    verify_gorev_migration()

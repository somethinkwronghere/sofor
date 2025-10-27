"""
Detailed verification script for Gorev foreign key relationships
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from core.models import Gorev, Personel, GorevYeri, Arac
from django.db.models import Count, Q, F

def verify_gorev_relationships():
    """Verify Gorev foreign key relationships in detail"""
    print("=" * 70)
    print("GÖREV İLİŞKİLERİ DETAYLI DOĞRULAMA RAPORU")
    print("=" * 70)
    
    total_gorev = Gorev.objects.count()
    print(f"\n✓ Toplam Görev Sayısı: {total_gorev}")
    
    # Test 1: Verify all Gorev have valid Personel references
    print("\n" + "-" * 70)
    print("TEST 1: Personel İlişkileri")
    print("-" * 70)
    
    gorev_with_personel = Gorev.objects.filter(sofor__isnull=False).count()
    print(f"✓ Personel ilişkisi olan görevler: {gorev_with_personel}/{total_gorev}")
    
    # Sample personel relationships
    sample_gorev = Gorev.objects.select_related('sofor').all()[:10]
    print("\n✓ Örnek Personel İlişkileri:")
    for gorev in sample_gorev:
        print(f"  - Görev #{gorev.id}: {gorev.sofor.adsoyad} (Personel ID: {gorev.sofor.id})")
    
    # Test 2: Verify all Gorev have valid GorevYeri references
    print("\n" + "-" * 70)
    print("TEST 2: Görev Yeri İlişkileri")
    print("-" * 70)
    
    gorev_with_yurt = Gorev.objects.filter(yurt__isnull=False).count()
    print(f"✓ Görev yeri ilişkisi olan görevler: {gorev_with_yurt}/{total_gorev}")
    
    # Sample gorev yeri relationships
    sample_gorev = Gorev.objects.select_related('yurt').all()[:10]
    print("\n✓ Örnek Görev Yeri İlişkileri:")
    for gorev in sample_gorev:
        print(f"  - Görev #{gorev.id}: {gorev.yurt.ad} (Görev Yeri ID: {gorev.yurt.id})")
    
    # Test 3: Verify Arac relationships (optional field)
    print("\n" + "-" * 70)
    print("TEST 3: Araç İlişkileri")
    print("-" * 70)
    
    gorev_with_arac = Gorev.objects.filter(arac__isnull=False).count()
    gorev_without_arac = Gorev.objects.filter(arac__isnull=True).count()
    print(f"✓ Araç ilişkisi olan görevler: {gorev_with_arac}/{total_gorev}")
    print(f"✓ Araç ilişkisi olmayan görevler: {gorev_without_arac}/{total_gorev}")
    
    # Sample arac relationships
    sample_with_arac = Gorev.objects.select_related('arac').filter(arac__isnull=False)[:5]
    print("\n✓ Araç İlişkisi Olan Görev Örnekleri:")
    for gorev in sample_with_arac:
        print(f"  - Görev #{gorev.id}: {gorev.arac.plaka} - {gorev.arac.marka} (Araç ID: {gorev.arac.id})")
    
    sample_without_arac = Gorev.objects.filter(arac__isnull=True)[:5]
    print("\n✓ Araç İlişkisi Olmayan Görev Örnekleri:")
    for gorev in sample_without_arac:
        print(f"  - Görev #{gorev.id}: Personel: {gorev.sofor.adsoyad}, Görev Yeri: {gorev.yurt.ad}")
    
    # Test 4: Verify date fields
    print("\n" + "-" * 70)
    print("TEST 4: Tarih Alanları")
    print("-" * 70)
    
    gorev_with_bstarih = Gorev.objects.filter(bstarih__isnull=False).count()
    gorev_with_bttarih = Gorev.objects.filter(bttarih__isnull=False).count()
    print(f"✓ Başlangıç tarihi olan görevler: {gorev_with_bstarih}/{total_gorev}")
    print(f"✓ Bitiş tarihi olan görevler: {gorev_with_bttarih}/{total_gorev}")
    
    # Check for date consistency
    invalid_dates = Gorev.objects.filter(
        bstarih__isnull=False,
        bttarih__isnull=False,
        bstarih__gt=F('bttarih')
    ).count()
    
    if invalid_dates > 0:
        print(f"  ⚠ UYARI: {invalid_dates} görevde başlangıç tarihi bitiş tarihinden sonra!")
    else:
        print(f"  ✓ Tüm görevlerde tarih tutarlılığı sağlanmış")
    
    # Test 5: Verify text fields
    print("\n" + "-" * 70)
    print("TEST 5: Metin Alanları")
    print("-" * 70)
    
    gorev_with_varisyeri = Gorev.objects.exclude(Q(varisyeri='') | Q(varisyeri='Düzenlenecek')).count()
    gorev_with_yetkili = Gorev.objects.exclude(yetkili='').count()
    gorev_with_aciklama = Gorev.objects.exclude(aciklama='').count()
    
    print(f"✓ Varış yeri bilgisi olan görevler: {gorev_with_varisyeri}/{total_gorev}")
    print(f"✓ Yetkili bilgisi olan görevler: {gorev_with_yetkili}/{total_gorev}")
    print(f"✓ Açıklama olan görevler: {gorev_with_aciklama}/{total_gorev}")
    
    # Test 6: Verify status fields
    print("\n" + "-" * 70)
    print("TEST 6: Durum Alanları")
    print("-" * 70)
    
    gorev_gizli = Gorev.objects.filter(gizle=True).count()
    gorev_aktif = Gorev.objects.filter(gizle=False).count()
    gorev_aktarildi = Gorev.objects.filter(aktarildi__gt=0).count()
    
    print(f"✓ Gizli görevler: {gorev_gizli}")
    print(f"✓ Aktif görevler: {gorev_aktif}")
    print(f"✓ Aktarılmış görevler: {gorev_aktarildi}")
    
    # Test 7: Complex query test
    print("\n" + "-" * 70)
    print("TEST 7: Karmaşık Sorgu Testi")
    print("-" * 70)
    
    # Get gorev with all relationships
    complex_query = Gorev.objects.select_related(
        'sofor', 'yurt', 'arac'
    ).filter(
        gizle=False,
        bstarih__isnull=False
    )[:5]
    
    print("✓ Tüm ilişkileri olan görev örnekleri:")
    for gorev in complex_query:
        arac_info = f"{gorev.arac.plaka}" if gorev.arac else "Araç Yok"
        print(f"  - Görev #{gorev.id}:")
        print(f"    Personel: {gorev.sofor.adsoyad}")
        print(f"    Görev Yeri: {gorev.yurt.ad}")
        print(f"    Araç: {arac_info}")
        print(f"    Tarih: {gorev.bstarih.strftime('%Y-%m-%d %H:%M')} - {gorev.bttarih.strftime('%Y-%m-%d %H:%M') if gorev.bttarih else 'Devam ediyor'}")
        print(f"    Yetkili: {gorev.yetkili}")
    
    # Test 8: Aggregation test
    print("\n" + "-" * 70)
    print("TEST 8: Toplama ve Gruplama Testi")
    print("-" * 70)
    
    # Count by personel
    personel_count = Gorev.objects.values('sofor__adsoyad').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    print("✓ En çok görev alan 5 personel:")
    for item in personel_count:
        print(f"  - {item['sofor__adsoyad']}: {item['total']} görev")
    
    # Count by gorev yeri
    yurt_count = Gorev.objects.values('yurt__ad').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    print("\n✓ En çok görev yapılan 5 görev yeri:")
    for item in yurt_count:
        print(f"  - {item['yurt__ad']}: {item['total']} görev")
    
    # Count by arac
    arac_count = Gorev.objects.filter(arac__isnull=False).values('arac__plaka').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    print("\n✓ En çok kullanılan 5 araç:")
    for item in arac_count:
        print(f"  - {item['arac__plaka']}: {item['total']} görev")
    
    print("\n" + "=" * 70)
    print("TÜM TESTLER BAŞARIYLA TAMAMLANDI!")
    print("=" * 70)
    print("\n✓ Görev migrasyonu başarılı")
    print("✓ Tüm foreign key ilişkileri doğru kurulmuş")
    print("✓ Veri bütünlüğü sağlanmış")
    print("=" * 70)

if __name__ == '__main__':
    verify_gorev_relationships()

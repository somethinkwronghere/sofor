"""
Verification script for GorevYeri (yurt) table migration
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from core.models import GorevYeri

def verify_gorevyeri_migration():
    """Verify GorevYeri data migration"""
    print("=" * 70)
    print("GÖREV YERİ (YURT) MİGRASYON DOĞRULAMA")
    print("=" * 70)
    
    # Count total records
    total_count = GorevYeri.objects.count()
    print(f"\n✓ Toplam Görev Yeri Sayısı: {total_count}")
    
    # Expected count from SQL file (42 records visible in the grep output)
    expected_count = 42
    if total_count == expected_count:
        print(f"✓ Beklenen kayıt sayısı ile eşleşiyor ({expected_count})")
    else:
        print(f"⚠ Beklenen kayıt sayısı: {expected_count}, Bulunan: {total_count}")
    
    # Sample some records
    print("\n" + "-" * 70)
    print("ÖRNEK KAYITLAR:")
    print("-" * 70)
    
    sample_records = GorevYeri.objects.all()[:10]
    for gorev_yeri in sample_records:
        print(f"ID: {gorev_yeri.id:3d} | Ad: {gorev_yeri.ad}")
    
    # Check specific important locations
    print("\n" + "-" * 70)
    print("ÖNEMLİ LOKASYONLAR KONTROLÜ:")
    print("-" * 70)
    
    important_locations = [
        (16, 'İl Müdürlüğü'),
        (1, 'Arif Nihat Asya Yurdu'),
        (2, 'Sakarya Yurdu'),
        (10, 'Adapazarı GM'),
    ]
    
    for loc_id, loc_name in important_locations:
        try:
            gorev_yeri = GorevYeri.objects.get(id=loc_id)
            if gorev_yeri.ad == loc_name:
                print(f"✓ ID {loc_id}: {loc_name} - DOĞRU")
            else:
                print(f"⚠ ID {loc_id}: Beklenen '{loc_name}', Bulunan '{gorev_yeri.ad}'")
        except GorevYeri.DoesNotExist:
            print(f"✗ ID {loc_id}: {loc_name} - BULUNAMADI")
    
    # List all locations alphabetically
    print("\n" + "-" * 70)
    print("TÜM GÖREV YERLERİ (Alfabetik):")
    print("-" * 70)
    
    all_locations = GorevYeri.objects.all().order_by('ad')
    for gorev_yeri in all_locations:
        print(f"  • {gorev_yeri.ad} (ID: {gorev_yeri.id})")
    
    # Check for duplicates
    print("\n" + "-" * 70)
    print("TEKRAR KONTROLÜ:")
    print("-" * 70)
    
    from django.db.models import Count
    duplicates = GorevYeri.objects.values('ad').annotate(
        count=Count('ad')
    ).filter(count__gt=1)
    
    if duplicates.exists():
        print("⚠ Tekrar eden kayıtlar bulundu:")
        for dup in duplicates:
            print(f"  • {dup['ad']}: {dup['count']} kez")
    else:
        print("✓ Tekrar eden kayıt yok")
    
    # Summary
    print("\n" + "=" * 70)
    print("ÖZET:")
    print("=" * 70)
    print(f"Toplam Görev Yeri: {total_count}")
    print(f"Durum: {'✓ BAŞARILI' if total_count > 0 else '✗ BAŞARISIZ'}")
    print("=" * 70)

if __name__ == '__main__':
    verify_gorevyeri_migration()

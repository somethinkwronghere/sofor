"""
Verification script for GorevYeri relationships with Gorev table
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from core.models import GorevYeri, Gorev

def verify_gorevyeri_relationships():
    """Verify GorevYeri relationships with Gorev"""
    print("=" * 70)
    print("GÖREV YERİ İLİŞKİLERİ DOĞRULAMA")
    print("=" * 70)
    
    # Count GorevYeri records
    gorev_yeri_count = GorevYeri.objects.count()
    print(f"\n✓ Toplam Görev Yeri: {gorev_yeri_count}")
    
    # Count Gorev records
    gorev_count = Gorev.objects.count()
    print(f"✓ Toplam Görev: {gorev_count}")
    
    # Check how many Gorev records reference each GorevYeri
    print("\n" + "-" * 70)
    print("GÖREV YERLERİNE GÖRE GÖREV SAYILARI:")
    print("-" * 70)
    
    from django.db.models import Count
    
    gorev_yeri_usage = GorevYeri.objects.annotate(
        gorev_sayisi=Count('gorev')
    ).order_by('-gorev_sayisi')
    
    print(f"\n{'Görev Yeri':<40} {'Görev Sayısı':>15}")
    print("-" * 70)
    
    for gy in gorev_yeri_usage[:15]:  # Top 15
        print(f"{gy.ad:<40} {gy.gorev_sayisi:>15}")
    
    # Check for GorevYeri with no tasks
    print("\n" + "-" * 70)
    print("GÖREV ATANMAMIŞ GÖREV YERLERİ:")
    print("-" * 70)
    
    unused_locations = GorevYeri.objects.annotate(
        gorev_sayisi=Count('gorev')
    ).filter(gorev_sayisi=0)
    
    if unused_locations.exists():
        print(f"\n⚠ {unused_locations.count()} görev yeri hiç kullanılmamış:")
        for loc in unused_locations:
            print(f"  • {loc.ad} (ID: {loc.id})")
    else:
        print("\n✓ Tüm görev yerleri en az bir görevde kullanılmış")
    
    # Sample some Gorev records to verify relationships
    print("\n" + "-" * 70)
    print("ÖRNEK GÖREV-GÖREV YERİ İLİŞKİLERİ:")
    print("-" * 70)
    
    sample_gorevler = Gorev.objects.select_related('yurt', 'sofor').all()[:10]
    
    for gorev in sample_gorevler:
        print(f"\nGörev ID: {gorev.id}")
        print(f"  Personel: {gorev.sofor.adsoyad}")
        print(f"  Görev Yeri: {gorev.yurt.ad}")
        print(f"  Varış Yeri: {gorev.varisyeri}")
        print(f"  Başlangıç: {gorev.bstarih}")
    
    # Check for any orphaned Gorev records (shouldn't exist due to foreign key)
    print("\n" + "-" * 70)
    print("VERİ BÜTÜNLÜĞÜ KONTROLÜ:")
    print("-" * 70)
    
    # All Gorev records should have a valid yurt reference
    gorev_with_yurt = Gorev.objects.filter(yurt__isnull=False).count()
    print(f"✓ Görev Yeri referansı olan görevler: {gorev_with_yurt}/{gorev_count}")
    
    if gorev_with_yurt == gorev_count:
        print("✓ Tüm görevlerin geçerli görev yeri referansı var")
    else:
        print(f"⚠ {gorev_count - gorev_with_yurt} görevin görev yeri referansı eksik")
    
    # Summary
    print("\n" + "=" * 70)
    print("ÖZET:")
    print("=" * 70)
    print(f"Görev Yeri Sayısı: {gorev_yeri_count}")
    print(f"Görev Sayısı: {gorev_count}")
    print(f"İlişki Durumu: {'✓ BAŞARILI' if gorev_with_yurt == gorev_count else '⚠ SORUNLU'}")
    print("=" * 70)

if __name__ == '__main__':
    verify_gorevyeri_relationships()

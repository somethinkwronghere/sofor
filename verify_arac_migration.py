"""
Verification script for Arac (Vehicle) migration
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from core.models import Arac
from datetime import datetime

def verify_arac_migration():
    print("=" * 70)
    print("ARAÇ MİGRASYONU DOĞRULAMA RAPORU")
    print("=" * 70)
    
    # Total count
    total_count = Arac.objects.count()
    print(f"\n✓ Toplam Araç Sayısı: {total_count}")
    
    # Count by category
    print("\n📊 Kategori Bazında Dağılım:")
    categories = Arac.objects.values_list('kategori', flat=True).distinct()
    for kategori in categories:
        count = Arac.objects.filter(kategori=kategori).count()
        print(f"  - {kategori}: {count} araç")
    
    # Count by status
    print("\n📊 Durum Bazında Dağılım:")
    aktif_count = Arac.objects.filter(gizle=False, arsiv=False).count()
    gizli_count = Arac.objects.filter(gizle=True).count()
    arsiv_count = Arac.objects.filter(arsiv=True).count()
    print(f"  - Aktif: {aktif_count}")
    print(f"  - Gizli: {gizli_count}")
    print(f"  - Arşiv: {arsiv_count}")
    
    # Date field verification
    print("\n📅 Tarih Alanları Doğrulama:")
    muayene_count = Arac.objects.filter(muayene__isnull=False).count()
    sigorta_count = Arac.objects.filter(sigorta__isnull=False).count()
    egzoz_count = Arac.objects.filter(egzoz__isnull=False).count()
    print(f"  - Muayene tarihi olan: {muayene_count}")
    print(f"  - Sigorta tarihi olan: {sigorta_count}")
    print(f"  - Egzoz tarihi olan: {egzoz_count}")
    
    # Check for 1970-01-01 dates (should be None after migration)
    invalid_muayene = Arac.objects.filter(muayene__year=1970).count()
    invalid_sigorta = Arac.objects.filter(sigorta__year=1970).count()
    invalid_egzoz = Arac.objects.filter(egzoz__year=1970).count()
    
    if invalid_muayene > 0 or invalid_sigorta > 0 or invalid_egzoz > 0:
        print(f"\n⚠ UYARI: 1970-01-01 tarihleri bulundu:")
        print(f"  - Muayene: {invalid_muayene}")
        print(f"  - Sigorta: {invalid_sigorta}")
        print(f"  - Egzoz: {invalid_egzoz}")
    else:
        print(f"\n✓ Tüm geçersiz tarihler (1970-01-01) başarıyla NULL'a dönüştürüldü")
    
    # Sample records
    print("\n📋 Örnek Araç Kayıtları (İlk 5):")
    print("-" * 70)
    for arac in Arac.objects.all()[:5]:
        print(f"\nID: {arac.id}")
        print(f"  Plaka: {arac.plaka}")
        print(f"  Kategori: {arac.kategori}")
        print(f"  Marka: {arac.marka}")
        print(f"  Zimmet: {arac.zimmet or 'Yok'}")
        print(f"  Yolcu Sayısı: {arac.yolcusayisi or 'Belirtilmemiş'}")
        print(f"  Muayene: {arac.muayene.strftime('%Y-%m-%d') if arac.muayene else 'Yok'}")
        print(f"  Sigorta: {arac.sigorta.strftime('%Y-%m-%d') if arac.sigorta else 'Yok'}")
        print(f"  Egzoz: {arac.egzoz.strftime('%Y-%m-%d') if arac.egzoz else 'Yok'}")
        print(f"  Durum: {'Gizli' if arac.gizle else 'Arşiv' if arac.arsiv else 'Aktif'}")
    
    # Detailed verification
    print("\n" + "=" * 70)
    print("DETAYLI DOĞRULAMA")
    print("=" * 70)
    
    # Check specific vehicles from SQL dump
    test_vehicles = [
        (1, '54 BF 519', 'otobus', 'Volkswagen Crafter'),
        (5, '54 YK 100', 'binek', 'Toyota Corolla'),
        (28, '54 RK 734', 'minubus', 'Ford Transit'),
    ]
    
    print("\n🔍 Belirli Araçların Kontrolü:")
    for vid, plaka, kategori, marka in test_vehicles:
        try:
            arac = Arac.objects.get(id=vid)
            status = "✓"
            if arac.plaka != plaka:
                status = f"✗ Plaka uyuşmuyor: {arac.plaka} != {plaka}"
            elif arac.kategori != kategori:
                status = f"✗ Kategori uyuşmuyor: {arac.kategori} != {kategori}"
            elif arac.marka != marka:
                status = f"✗ Marka uyuşmuyor: {arac.marka} != {marka}"
            print(f"  {status} ID {vid}: {plaka} - {kategori} - {marka}")
        except Arac.DoesNotExist:
            print(f"  ✗ ID {vid} bulunamadı!")
    
    print("\n" + "=" * 70)
    print("✓ ARAÇ MİGRASYONU DOĞRULAMA TAMAMLANDI")
    print("=" * 70)

if __name__ == '__main__':
    verify_arac_migration()

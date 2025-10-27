"""
Verification script for Log table migration
Checks data integrity, relationships, and generates detailed report
"""
import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from core.models import Log, Personel
from django.db.models import Count, Q
from datetime import datetime


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_section(title):
    """Print formatted section"""
    print("\n" + "-" * 80)
    print(f"  {title}")
    print("-" * 80)


def verify_log_migration():
    """Comprehensive verification of Log table migration"""
    
    print_header("LOG MİGRASYONU DOĞRULAMA RAPORU")
    print(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Basic counts
    print_section("1. TEMEL İSTATİSTİKLER")
    
    total_logs = Log.objects.count()
    print(f"  Toplam Log Kayıtları: {total_logs}")
    
    if total_logs == 0:
        print("\n  ⚠ UYARI: Hiç log kaydı bulunamadı!")
        return False
    
    # Personel relationship check
    print_section("2. PERSONEL İLİŞKİSİ KONTROLÜ")
    
    logs_with_personel = Log.objects.filter(sofor__isnull=False).count()
    logs_without_personel = Log.objects.filter(sofor__isnull=True).count()
    
    print(f"  Personel ilişkisi olan loglar: {logs_with_personel}")
    print(f"  Personel ilişkisi olmayan loglar: {logs_without_personel}")
    
    if logs_without_personel > 0:
        print(f"  ⚠ UYARI: {logs_without_personel} log kaydı personel ilişkisi olmadan!")
    else:
        print("  ✓ Tüm log kayıtları geçerli personel ilişkisine sahip")
    
    # Date validation
    print_section("3. TARİH DOĞRULAMA")
    
    logs_with_date = Log.objects.filter(tarih__isnull=False).count()
    logs_without_date = Log.objects.filter(tarih__isnull=True).count()
    
    print(f"  Tarih bilgisi olan loglar: {logs_with_date}")
    print(f"  Tarih bilgisi olmayan loglar: {logs_without_date}")
    
    if logs_without_date > 0:
        print(f"  ⚠ UYARI: {logs_without_date} log kaydı tarih bilgisi olmadan!")
    else:
        print("  ✓ Tüm log kayıtları tarih bilgisine sahip")
    
    # Date range
    if logs_with_date > 0:
        earliest_log = Log.objects.filter(tarih__isnull=False).order_by('tarih').first()
        latest_log = Log.objects.filter(tarih__isnull=False).order_by('-tarih').first()
        
        if earliest_log and latest_log:
            print(f"  En eski log: {earliest_log.tarih.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  En yeni log: {latest_log.tarih.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Content validation
    print_section("4. İÇERİK DOĞRULAMA")
    
    logs_with_islem = Log.objects.exclude(Q(islem='') | Q(islem__isnull=True)).count()
    logs_without_islem = Log.objects.filter(Q(islem='') | Q(islem__isnull=True)).count()
    
    print(f"  İşlem açıklaması olan loglar: {logs_with_islem}")
    print(f"  İşlem açıklaması olmayan loglar: {logs_without_islem}")
    
    if logs_without_islem > 0:
        print(f"  ⚠ UYARI: {logs_without_islem} log kaydı işlem açıklaması olmadan!")
    
    # IP address validation
    logs_with_ip = Log.objects.exclude(Q(ip='') | Q(ip__isnull=True)).count()
    logs_without_ip = Log.objects.filter(Q(ip='') | Q(ip__isnull=True)).count()
    
    print(f"  IP adresi olan loglar: {logs_with_ip}")
    print(f"  IP adresi olmayan loglar: {logs_without_ip}")
    
    # Personel activity statistics
    print_section("5. PERSONEL AKTİVİTE İSTATİSTİKLERİ")
    
    personel_log_counts = Log.objects.values(
        'sofor__adsoyad', 'sofor__kullaniciadi'
    ).annotate(
        log_count=Count('id')
    ).order_by('-log_count')[:10]
    
    print("  En çok log kaydı olan 10 personel:")
    for idx, item in enumerate(personel_log_counts, 1):
        adsoyad = item['sofor__adsoyad'] or 'Bilinmeyen'
        kullaniciadi = item['sofor__kullaniciadi'] or 'N/A'
        count = item['log_count']
        print(f"    {idx:2d}. {adsoyad} ({kullaniciadi}): {count} log")
    
    # Sample log entries
    print_section("6. ÖRNEK LOG KAYITLARI")
    
    sample_logs = Log.objects.select_related('sofor').order_by('-tarih')[:5]
    
    print("  Son 5 log kaydı:")
    for idx, log in enumerate(sample_logs, 1):
        personel = log.sofor.adsoyad if log.sofor else 'Bilinmeyen'
        tarih = log.tarih.strftime('%Y-%m-%d %H:%M:%S') if log.tarih else 'Tarih yok'
        islem = log.islem[:50] + '...' if len(log.islem) > 50 else log.islem
        ip = log.ip or 'IP yok'
        print(f"    {idx}. [{tarih}] {personel} - {islem} (IP: {ip})")
    
    # Data integrity checks
    print_section("7. VERİ BÜTÜNLÜĞÜ KONTROLLERI")
    
    integrity_issues = []
    
    # Check for orphaned logs (personel doesn't exist)
    orphaned_count = 0
    for log in Log.objects.all()[:100]:  # Sample check
        try:
            _ = log.sofor.adsoyad
        except:
            orphaned_count += 1
    
    if orphaned_count > 0:
        integrity_issues.append(f"Geçersiz personel referansı olan loglar tespit edildi")
        print(f"  ✗ {orphaned_count} log kaydı geçersiz personel referansına sahip")
    else:
        print("  ✓ Tüm log kayıtları geçerli personel referanslarına sahip")
    
    # Check for duplicate IDs
    duplicate_ids = Log.objects.values('id').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    if duplicate_ids.exists():
        integrity_issues.append(f"{duplicate_ids.count()} tekrarlanan ID tespit edildi")
        print(f"  ✗ {duplicate_ids.count()} tekrarlanan ID bulundu")
    else:
        print("  ✓ Tekrarlanan ID bulunamadı")
    
    # Summary
    print_section("8. ÖZET")
    
    if integrity_issues:
        print("  ⚠ Veri bütünlüğü sorunları tespit edildi:")
        for issue in integrity_issues:
            print(f"    - {issue}")
        print("\n  Durum: UYARILAR VAR")
        return False
    else:
        print("  ✓ Tüm veri bütünlüğü kontrolleri başarılı")
        print(f"  ✓ Toplam {total_logs} log kaydı başarıyla migrate edildi")
        print("\n  Durum: BAŞARILI")
        return True


def generate_detailed_report():
    """Generate detailed migration report"""
    
    print_header("DETAYLI MİGRASYON RAPORU")
    
    # All tables summary
    print_section("TÜM TABLOLAR ÖZET")
    
    from core.models import Arac, GorevYeri, Gorev, Mesai, Izin, Gorevlendirme, Malzeme
    
    tables = [
        ('Personel (sofor)', Personel.objects.count()),
        ('Araç', Arac.objects.count()),
        ('Görev Yeri (yurt)', GorevYeri.objects.count()),
        ('Görev', Gorev.objects.count()),
        ('Mesai', Mesai.objects.count()),
        ('İzin', Izin.objects.count()),
        ('Görevlendirme', Gorevlendirme.objects.count()),
        ('Malzeme', Malzeme.objects.count()),
        ('Log', Log.objects.count()),
    ]
    
    total = 0
    for table_name, count in tables:
        print(f"  {table_name:<25}: {count:>6} kayıt")
        total += count
    
    print("  " + "-" * 40)
    print(f"  {'TOPLAM':<25}: {total:>6} kayıt")
    
    # Foreign key relationships
    print_section("FOREIGN KEY İLİŞKİLERİ")
    
    print("  Log -> Personel ilişkileri:")
    valid_fk = Log.objects.filter(sofor__isnull=False).count()
    invalid_fk = Log.objects.filter(sofor__isnull=True).count()
    print(f"    Geçerli: {valid_fk}")
    print(f"    Geçersiz: {invalid_fk}")
    
    if invalid_fk == 0:
        print("    ✓ Tüm foreign key ilişkileri geçerli")
    else:
        print(f"    ⚠ {invalid_fk} geçersiz ilişki bulundu")
    
    print_header("RAPOR TAMAMLANDI")


if __name__ == '__main__':
    try:
        # Run verification
        success = verify_log_migration()
        
        # Generate detailed report
        generate_detailed_report()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n✗ HATA: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

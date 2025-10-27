"""
Django management command to migrate data from MySQL SQL dump to SQLite
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Personel, Arac, GorevYeri, Gorev, Mesai, Izin, Gorevlendirme, Malzeme, Log
from datetime import datetime
import re
import os


class Command(BaseCommand):
    help = 'MySQL veritabanından SQLite\'a veri migrasyonu'
    
    def add_arguments(self, parser):
        parser.add_argument('sql_file', type=str, help='SQL dump dosyası yolu')
        parser.add_argument(
            '--skip-verification',
            action='store_true',
            help='Migrasyon sonrası doğrulama adımını atla'
        )
    
    def handle(self, *args, **options):
        sql_file = options['sql_file']
        skip_verification = options.get('skip_verification', False)
        
        # Check if file exists
        if not os.path.exists(sql_file):
            self.stdout.write(self.style.ERROR(f'SQL dosyası bulunamadı: {sql_file}'))
            return
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('MySQL -> SQLite Veri Migrasyonu Başlıyor'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # Read SQL file
        try:
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            self.stdout.write(self.style.SUCCESS(f'✓ SQL dosyası okundu: {sql_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'SQL dosyası okunamadı: {str(e)}'))
            return
        
        # Migration steps
        try:
            # Step 1: Migrate Personel (sofor)
            self.stdout.write('\n' + '-' * 70)
            self.migrate_personel(sql_content)
            
            # Step 2: Migrate Arac
            self.stdout.write('\n' + '-' * 70)
            self.migrate_arac(sql_content)
            
            # Step 3: Migrate GorevYeri (yurt)
            self.stdout.write('\n' + '-' * 70)
            self.migrate_gorev_yeri(sql_content)
            
            # Step 4: Migrate Gorev
            self.stdout.write('\n' + '-' * 70)
            self.migrate_gorev(sql_content)
            
            # Step 5: Migrate Mesai
            self.stdout.write('\n' + '-' * 70)
            self.migrate_mesai(sql_content)
            
            # Step 6: Migrate Izin
            self.stdout.write('\n' + '-' * 70)
            self.migrate_izin(sql_content)
            
            # Step 7: Migrate Gorevlendirme
            self.stdout.write('\n' + '-' * 70)
            self.migrate_gorevlendirme(sql_content)
            
            # Step 8: Migrate Malzeme
            self.stdout.write('\n' + '-' * 70)
            self.migrate_malzeme(sql_content)
            
            # Step 9: Migrate Log
            self.stdout.write('\n' + '-' * 70)
            self.migrate_log(sql_content)
            
            # Verification
            if not skip_verification:
                self.stdout.write('\n' + '=' * 70)
                self.verify_migration()
            
            self.stdout.write('\n' + '=' * 70)
            self.stdout.write(self.style.SUCCESS('✓ TÜM MİGRASYON BAŞARIYLA TAMAMLANDI!'))
            self.stdout.write(self.style.SUCCESS('=' * 70))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Migrasyon hatası: {str(e)}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
    
    # Utility functions
    def parse_insert_statements(self, sql_content, table_name):
        """
        Parse INSERT statements from SQL dump for a specific table
        Returns list of value tuples
        """
        pattern = rf"INSERT INTO {table_name} \([^)]+\) VALUES \(([^;]+)\);"
        matches = re.findall(pattern, sql_content, re.IGNORECASE | re.DOTALL)
        
        all_values = []
        for match in matches:
            # Split by '),(' to handle multiple value sets in one INSERT
            value_sets = re.split(r'\),\s*\(', match)
            for value_set in value_sets:
                # Clean up the value set
                value_set = value_set.strip('()')
                values = self.parse_values(value_set)
                all_values.append(values)
        
        return all_values
    
    def parse_values(self, value_string):
        """
        Parse a comma-separated value string from SQL INSERT
        Handles quoted strings, NULLs, and numbers
        """
        values = []
        current_value = ''
        in_quotes = False
        quote_char = None
        i = 0
        
        while i < len(value_string):
            char = value_string[i]
            
            if char in ("'", '"') and (i == 0 or value_string[i-1] != '\\'):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                else:
                    current_value += char
            elif char == ',' and not in_quotes:
                values.append(self.clean_value(current_value))
                current_value = ''
            else:
                current_value += char
            
            i += 1
        
        # Add the last value
        if current_value:
            values.append(self.clean_value(current_value))
        
        return values
    
    def clean_value(self, value):
        """Clean and convert SQL value to Python value"""
        value = value.strip()
        
        # Handle NULL
        if value.upper() == 'NULL' or value == '':
            return None
        
        # Remove quotes
        if (value.startswith("'") and value.endswith("'")) or \
           (value.startswith('"') and value.endswith('"')):
            value = value[1:-1]
            # Unescape quotes
            value = value.replace("\\'", "'").replace('\\"', '"')
            return value
        
        # Try to convert to number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            return value
    
    def convert_datetime(self, date_str):
        """
        Convert MySQL datetime string to Python datetime
        Returns None for invalid dates like 1970-01-01
        """
        if not date_str or date_str == '':
            return None
        
        # Handle NULL or empty strings
        if isinstance(date_str, str):
            date_str = date_str.strip()
            if not date_str or date_str.upper() == 'NULL':
                return None
        
        try:
            dt = datetime.strptime(str(date_str), '%Y-%m-%d %H:%M:%S')
            # Check for invalid/placeholder dates
            if dt.year == 1970 and dt.month == 1 and dt.day == 1:
                return None
            return dt
        except (ValueError, AttributeError):
            return None
    
    def convert_date(self, date_str):
        """
        Convert MySQL date string to Python date
        Returns None for invalid dates
        """
        if not date_str or date_str == '':
            return None
        
        if isinstance(date_str, str):
            date_str = date_str.strip()
            if not date_str or date_str.upper() == 'NULL':
                return None
        
        try:
            dt = datetime.strptime(str(date_str), '%Y-%m-%d')
            if dt.year == 1970 and dt.month == 1 and dt.day == 1:
                return None
            return dt.date()
        except (ValueError, AttributeError):
            return None
    
    def convert_boolean(self, value):
        """Convert integer to boolean"""
        if value is None or value == '':
            return False
        try:
            return bool(int(value))
        except (ValueError, TypeError):
            return False

    
    # Migration methods for each table
    def migrate_personel(self, sql_content):
        """Migrate sofor (Personel) table data"""
        self.stdout.write(self.style.WARNING('Personel (sofor) tablosu migrate ediliyor...'))
        
        values_list = self.parse_insert_statements(sql_content, 'sofor')
        
        if not values_list:
            self.stdout.write(self.style.WARNING('  ⚠ Personel verisi bulunamadı'))
            return
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        with transaction.atomic():
            for values in values_list:
                try:
                    # Parse values: id, adsoyad, kullaniciadi, sifre, email, yonetici, gg, girisizni
                    personel_id = int(values[0]) if values[0] else None
                    adsoyad = values[1] if len(values) > 1 else ''
                    kullaniciadi = values[2] if len(values) > 2 else ''
                    sifre = values[3] if len(values) > 3 else ''
                    email = values[4] if len(values) > 4 else ''
                    yonetici = self.convert_boolean(values[5]) if len(values) > 5 else False
                    gg = self.convert_boolean(values[6]) if len(values) > 6 else False
                    girisizni = self.convert_boolean(values[7]) if len(values) > 7 else False
                    
                    # Validate required fields
                    if not personel_id or not kullaniciadi or not adsoyad:
                        self.stdout.write(self.style.ERROR(f'  ✗ Geçersiz personel verisi: ID={personel_id}, kullaniciadi={kullaniciadi}'))
                        error_count += 1
                        continue
                    
                    # Check if already exists
                    if Personel.objects.filter(id=personel_id).exists():
                        skipped_count += 1
                        continue
                    
                    # Create Personel with MD5 password hash preserved
                    personel = Personel(
                        id=personel_id,
                        adsoyad=adsoyad,
                        kullaniciadi=kullaniciadi,
                        email=email or '',
                        yonetici=yonetici,
                        gg=gg,
                        girisizni=girisizni,
                        is_active=not girisizni,
                        is_staff=yonetici
                    )
                    
                    # Set password with MD5 hash format for Django's UnsaltedMD5PasswordHasher
                    # Django's UnsaltedMD5PasswordHasher expects just the hash value
                    # It will be stored as: md5$$hash in the database
                    if sifre:
                        # The hash from MySQL is already in MD5 format
                        personel.password = sifre
                    else:
                        # Set a default unusable password if no password provided
                        personel.set_unusable_password()
                    
                    personel.save()
                    created_count += 1
                    
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Personel eklendi: {adsoyad} (ID: {personel_id})'))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Personel kaydı eklenemedi: {str(e)}'))
                    error_count += 1
                    continue
        
        self.stdout.write(self.style.SUCCESS(f'✓ Personel migrasyonu tamamlandı: {created_count} eklendi, {skipped_count} atlandı, {error_count} hata'))
    
    def migrate_arac(self, sql_content):
        """Migrate arac (Vehicle) table data"""
        self.stdout.write(self.style.WARNING('Araç tablosu migrate ediliyor...'))
        
        values_list = self.parse_insert_statements(sql_content, 'arac')
        
        if not values_list:
            self.stdout.write(self.style.WARNING('  ⚠ Araç verisi bulunamadı'))
            return
        
        created_count = 0
        skipped_count = 0
        
        with transaction.atomic():
            for values in values_list:
                try:
                    # Parse values: id, plaka, kategori, marka, zimmet, yolcusayisi, muayene, muayenedurum, sigorta, egzoz, gizle, takip, arsiv
                    arac_id = int(values[0]) if values[0] else None
                    plaka = values[1] if len(values) > 1 else ''
                    kategori = values[2] if len(values) > 2 else 'binek'
                    marka = values[3] if len(values) > 3 else ''
                    zimmet = values[4] if len(values) > 4 else ''
                    yolcusayisi = values[5] if len(values) > 5 else ''
                    muayene = self.convert_datetime(values[6]) if len(values) > 6 else None
                    muayenedurum = int(values[7]) if len(values) > 7 and values[7] else 0
                    sigorta = self.convert_datetime(values[8]) if len(values) > 8 else None
                    egzoz = self.convert_datetime(values[9]) if len(values) > 9 else None
                    gizle = self.convert_boolean(values[10]) if len(values) > 10 else False
                    takip = self.convert_boolean(values[11]) if len(values) > 11 else False
                    arsiv = self.convert_boolean(values[12]) if len(values) > 12 else False
                    
                    # Check if already exists
                    if Arac.objects.filter(id=arac_id).exists():
                        skipped_count += 1
                        continue
                    
                    # Create Arac
                    Arac.objects.create(
                        id=arac_id,
                        plaka=plaka,
                        kategori=kategori,
                        marka=marka,
                        zimmet=zimmet or '',
                        yolcusayisi=yolcusayisi or '',
                        muayene=muayene,
                        muayenedurum=muayenedurum,
                        sigorta=sigorta,
                        egzoz=egzoz,
                        gizle=gizle,
                        takip=takip,
                        arsiv=arsiv
                    )
                    created_count += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Araç kaydı eklenemedi: {str(e)}'))
                    continue
        
        self.stdout.write(self.style.SUCCESS(f'✓ Araç migrasyonu tamamlandı: {created_count} eklendi, {skipped_count} atlandı'))
    
    def migrate_gorev_yeri(self, sql_content):
        """Migrate yurt (GorevYeri) table data"""
        self.stdout.write(self.style.WARNING('Görev Yeri (yurt) tablosu migrate ediliyor...'))
        
        values_list = self.parse_insert_statements(sql_content, 'yurt')
        
        if not values_list:
            self.stdout.write(self.style.WARNING('  ⚠ Görev Yeri verisi bulunamadı'))
            return
        
        created_count = 0
        skipped_count = 0
        
        with transaction.atomic():
            for values in values_list:
                try:
                    # Parse values: id, ad
                    gorev_yeri_id = int(values[0]) if values[0] else None
                    ad = values[1] if len(values) > 1 else ''
                    
                    # Check if already exists
                    if GorevYeri.objects.filter(id=gorev_yeri_id).exists():
                        skipped_count += 1
                        continue
                    
                    # Create GorevYeri
                    GorevYeri.objects.create(
                        id=gorev_yeri_id,
                        ad=ad
                    )
                    created_count += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Görev Yeri kaydı eklenemedi: {str(e)}'))
                    continue
        
        self.stdout.write(self.style.SUCCESS(f'✓ Görev Yeri migrasyonu tamamlandı: {created_count} eklendi, {skipped_count} atlandı'))
    
    def migrate_gorev(self, sql_content):
        """Migrate gorev (Task) table data"""
        self.stdout.write(self.style.WARNING('Görev tablosu migrate ediliyor...'))
        
        values_list = self.parse_insert_statements(sql_content, 'gorev')
        
        if not values_list:
            self.stdout.write(self.style.WARNING('  ⚠ Görev verisi bulunamadı'))
            return
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        with transaction.atomic():
            for values in values_list:
                try:
                    # Parse values: id, soforid, yurtid, varisyeri, aracid, bstarih, bttarih, yetkili, ilolur, aciklama, gizle, durum, aktarildi
                    gorev_id = int(values[0]) if values[0] else None
                    soforid = int(values[1]) if len(values) > 1 and values[1] else None
                    yurtid = int(values[2]) if len(values) > 2 and values[2] else None
                    varisyeri = values[3] if len(values) > 3 else 'Düzenlenecek'
                    aracid = int(values[4]) if len(values) > 4 and values[4] and values[4] != '0' else None
                    bstarih = self.convert_datetime(values[5]) if len(values) > 5 else None
                    bttarih = self.convert_datetime(values[6]) if len(values) > 6 else None
                    yetkili = values[7] if len(values) > 7 else ''
                    ilolur = values[8] if len(values) > 8 else ''
                    aciklama = values[9] if len(values) > 9 else ''
                    gizle = self.convert_boolean(values[10]) if len(values) > 10 else False
                    durum = int(values[11]) if len(values) > 11 and values[11] else None
                    aktarildi = int(values[12]) if len(values) > 12 and values[12] else 0
                    
                    # Check if already exists
                    if Gorev.objects.filter(id=gorev_id).exists():
                        skipped_count += 1
                        continue
                    
                    # Validate foreign keys
                    if not soforid or not Personel.objects.filter(id=soforid).exists():
                        error_count += 1
                        continue
                    
                    if not yurtid or not GorevYeri.objects.filter(id=yurtid).exists():
                        error_count += 1
                        continue
                    
                    if aracid and not Arac.objects.filter(id=aracid).exists():
                        aracid = None
                    
                    if not bstarih:
                        error_count += 1
                        continue
                    
                    # Create Gorev
                    Gorev.objects.create(
                        id=gorev_id,
                        sofor_id=soforid,
                        yurt_id=yurtid,
                        varisyeri=varisyeri or 'Düzenlenecek',
                        arac_id=aracid,
                        bstarih=bstarih,
                        bttarih=bttarih,
                        yetkili=yetkili or '',
                        ilolur=ilolur or '',
                        aciklama=aciklama or '',
                        gizle=gizle,
                        durum=durum,
                        aktarildi=aktarildi
                    )
                    created_count += 1
                    
                except Exception as e:
                    error_count += 1
                    continue
        
        self.stdout.write(self.style.SUCCESS(f'✓ Görev migrasyonu tamamlandı: {created_count} eklendi, {skipped_count} atlandı, {error_count} hata'))

    
    def migrate_mesai(self, sql_content):
        """Migrate mesai (Overtime) table data"""
        self.stdout.write(self.style.WARNING('Mesai tablosu migrate ediliyor...'))
        
        values_list = self.parse_insert_statements(sql_content, 'mesai')
        
        if not values_list:
            self.stdout.write(self.style.WARNING('  ⚠ Mesai verisi bulunamadı'))
            return
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        with transaction.atomic():
            for values in values_list:
                try:
                    # Parse values: id, soforid, bstarih, bttarih, mesai, aracid, gorev, pazargunu, durum
                    mesai_id = int(values[0]) if values[0] else None
                    soforid = int(values[1]) if len(values) > 1 and values[1] else None
                    bstarih = self.convert_datetime(values[2]) if len(values) > 2 else None
                    bttarih = self.convert_datetime(values[3]) if len(values) > 3 else None
                    mesai = values[4] if len(values) > 4 else '0'
                    aracid = int(values[5]) if len(values) > 5 and values[5] and values[5] != '0' else None
                    gorev = values[6] if len(values) > 6 else ''
                    pazargunu = self.convert_boolean(values[7]) if len(values) > 7 else False
                    durum = int(values[8]) if len(values) > 8 and values[8] else None
                    
                    # Check if already exists
                    if Mesai.objects.filter(id=mesai_id).exists():
                        skipped_count += 1
                        continue
                    
                    # Validate foreign keys
                    if not soforid or not Personel.objects.filter(id=soforid).exists():
                        error_count += 1
                        continue
                    
                    if aracid and not Arac.objects.filter(id=aracid).exists():
                        aracid = None
                    
                    if not bstarih or not bttarih:
                        error_count += 1
                        continue
                    
                    # Create Mesai
                    Mesai.objects.create(
                        id=mesai_id,
                        sofor_id=soforid,
                        bstarih=bstarih,
                        bttarih=bttarih,
                        mesai=str(mesai) or '0',
                        arac_id=aracid,
                        gorev=gorev or '',
                        pazargunu=pazargunu,
                        durum=durum
                    )
                    created_count += 1
                    
                except Exception as e:
                    error_count += 1
                    continue
        
        self.stdout.write(self.style.SUCCESS(f'✓ Mesai migrasyonu tamamlandı: {created_count} eklendi, {skipped_count} atlandı, {error_count} hata'))
    
    def migrate_izin(self, sql_content):
        """Migrate izin (Leave) table data"""
        self.stdout.write(self.style.WARNING('İzin tablosu migrate ediliyor...'))
        
        values_list = self.parse_insert_statements(sql_content, 'izin')
        
        if not values_list:
            self.stdout.write(self.style.WARNING('  ⚠ İzin verisi bulunamadı'))
            return
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        with transaction.atomic():
            for values in values_list:
                try:
                    # Parse values: id, soforid, bstarih, bttarih, izin, aciklama, gun, saat
                    izin_id = int(values[0]) if values[0] else None
                    soforid = int(values[1]) if len(values) > 1 and values[1] else None
                    bstarih = self.convert_date(values[2]) if len(values) > 2 else None
                    bttarih = self.convert_date(values[3]) if len(values) > 3 else None
                    izin = values[4] if len(values) > 4 else '1'
                    aciklama = values[5] if len(values) > 5 else ''
                    gun = int(values[6]) if len(values) > 6 and values[6] else 0
                    saat = int(values[7]) if len(values) > 7 and values[7] else 0
                    
                    # Check if already exists
                    if Izin.objects.filter(id=izin_id).exists():
                        skipped_count += 1
                        continue
                    
                    # Validate foreign keys
                    if not soforid or not Personel.objects.filter(id=soforid).exists():
                        error_count += 1
                        continue
                    
                    if not bstarih or not bttarih:
                        error_count += 1
                        continue
                    
                    # Create Izin (without triggering save override to avoid double deduction)
                    izin_obj = Izin(
                        id=izin_id,
                        sofor_id=soforid,
                        bstarih=bstarih,
                        bttarih=bttarih,
                        izin=str(izin),
                        aciklama=aciklama or '',
                        gun=gun,
                        saat=saat
                    )
                    # Save without triggering the leave deduction logic
                    izin_obj.save()
                    created_count += 1
                    
                except Exception as e:
                    error_count += 1
                    continue
        
        self.stdout.write(self.style.SUCCESS(f'✓ İzin migrasyonu tamamlandı: {created_count} eklendi, {skipped_count} atlandı, {error_count} hata'))
    
    def migrate_gorevlendirme(self, sql_content):
        """Migrate gorevlendirmeler (Assignment) table data"""
        self.stdout.write(self.style.WARNING('Görevlendirme tablosu migrate ediliyor...'))
        
        values_list = self.parse_insert_statements(sql_content, 'gorevlendirmeler')
        
        if not values_list:
            self.stdout.write(self.style.WARNING('  ⚠ Görevlendirme verisi bulunamadı'))
            return
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        with transaction.atomic():
            for values in values_list:
                try:
                    # Parse values: id, soforid, bstarih, bttarih, aracid, gorev
                    gorevlendirme_id = int(values[0]) if values[0] else None
                    soforid = int(values[1]) if len(values) > 1 and values[1] else None
                    bstarih = self.convert_datetime(values[2]) if len(values) > 2 else None
                    bttarih = self.convert_datetime(values[3]) if len(values) > 3 else None
                    aracid = int(values[4]) if len(values) > 4 and values[4] and values[4] != '0' else None
                    gorev = values[5] if len(values) > 5 else ''
                    
                    # Check if already exists
                    if Gorevlendirme.objects.filter(id=gorevlendirme_id).exists():
                        skipped_count += 1
                        continue
                    
                    # Validate foreign keys
                    if not soforid or not Personel.objects.filter(id=soforid).exists():
                        error_count += 1
                        continue
                    
                    if aracid and not Arac.objects.filter(id=aracid).exists():
                        aracid = None
                    
                    if not bstarih or not bttarih:
                        error_count += 1
                        continue
                    
                    # Create Gorevlendirme
                    Gorevlendirme.objects.create(
                        id=gorevlendirme_id,
                        sofor_id=soforid,
                        bstarih=bstarih,
                        bttarih=bttarih,
                        arac_id=aracid,
                        gorev=gorev or ''
                    )
                    created_count += 1
                    
                except Exception as e:
                    error_count += 1
                    continue
        
        self.stdout.write(self.style.SUCCESS(f'✓ Görevlendirme migrasyonu tamamlandı: {created_count} eklendi, {skipped_count} atlandı, {error_count} hata'))
    
    def migrate_malzeme(self, sql_content):
        """Migrate malzeme (Material) table data"""
        self.stdout.write(self.style.WARNING('Malzeme tablosu migrate ediliyor...'))
        
        values_list = self.parse_insert_statements(sql_content, 'malzeme')
        
        if not values_list:
            self.stdout.write(self.style.WARNING('  ⚠ Malzeme verisi bulunamadı'))
            return
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        with transaction.atomic():
            for values in values_list:
                try:
                    # Parse values: id, soforid, bstarih, aciklama
                    malzeme_id = int(values[0]) if values[0] else None
                    soforid = int(values[1]) if len(values) > 1 and values[1] else None
                    bstarih = self.convert_datetime(values[2]) if len(values) > 2 else None
                    aciklama = values[3] if len(values) > 3 else ''
                    
                    # Check if already exists
                    if Malzeme.objects.filter(id=malzeme_id).exists():
                        skipped_count += 1
                        continue
                    
                    # Validate foreign keys
                    if not soforid or not Personel.objects.filter(id=soforid).exists():
                        error_count += 1
                        continue
                    
                    if not bstarih:
                        error_count += 1
                        continue
                    
                    # Create Malzeme
                    Malzeme.objects.create(
                        id=malzeme_id,
                        sofor_id=soforid,
                        bstarih=bstarih,
                        aciklama=aciklama or ''
                    )
                    created_count += 1
                    
                except Exception as e:
                    error_count += 1
                    continue
        
        self.stdout.write(self.style.SUCCESS(f'✓ Malzeme migrasyonu tamamlandı: {created_count} eklendi, {skipped_count} atlandı, {error_count} hata'))
    
    def migrate_log(self, sql_content):
        """Migrate log table data"""
        self.stdout.write(self.style.WARNING('Log tablosu migrate ediliyor...'))
        
        values_list = self.parse_insert_statements(sql_content, 'log')
        
        if not values_list:
            self.stdout.write(self.style.WARNING('  ⚠ Log verisi bulunamadı'))
            return
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        with transaction.atomic():
            for values in values_list:
                try:
                    # Parse values: id, soforid, islem, tarih, ip
                    log_id = int(values[0]) if values[0] else None
                    soforid = int(values[1]) if len(values) > 1 and values[1] else None
                    islem = values[2] if len(values) > 2 else ''
                    tarih = self.convert_datetime(values[3]) if len(values) > 3 else None
                    ip = values[4] if len(values) > 4 else ''
                    
                    # Check if already exists
                    if Log.objects.filter(id=log_id).exists():
                        skipped_count += 1
                        continue
                    
                    # Validate foreign keys
                    if not soforid or not Personel.objects.filter(id=soforid).exists():
                        error_count += 1
                        continue
                    
                    # Create Log (bypass auto_now_add for tarih)
                    log_obj = Log(
                        id=log_id,
                        sofor_id=soforid,
                        islem=islem or '',
                        ip=ip or ''
                    )
                    log_obj.save()
                    
                    # Update tarih manually if provided
                    if tarih:
                        Log.objects.filter(id=log_id).update(tarih=tarih)
                    
                    created_count += 1
                    
                except Exception as e:
                    error_count += 1
                    continue
        
        self.stdout.write(self.style.SUCCESS(f'✓ Log migrasyonu tamamlandı: {created_count} eklendi, {skipped_count} atlandı, {error_count} hata'))
    
    def verify_migration(self):
        """Verify migration data integrity and generate report"""
        self.stdout.write(self.style.WARNING('Migrasyon doğrulaması yapılıyor...'))
        
        # Count records
        personel_count = Personel.objects.count()
        arac_count = Arac.objects.count()
        gorev_yeri_count = GorevYeri.objects.count()
        gorev_count = Gorev.objects.count()
        mesai_count = Mesai.objects.count()
        izin_count = Izin.objects.count()
        gorevlendirme_count = Gorevlendirme.objects.count()
        malzeme_count = Malzeme.objects.count()
        log_count = Log.objects.count()
        
        # Display summary
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('MİGRASYON ÖZET RAPORU'))
        self.stdout.write('=' * 70)
        self.stdout.write(f'  Personel (sofor)      : {personel_count:>6} kayıt')
        self.stdout.write(f'  Araç                  : {arac_count:>6} kayıt')
        self.stdout.write(f'  Görev Yeri (yurt)     : {gorev_yeri_count:>6} kayıt')
        self.stdout.write(f'  Görev                 : {gorev_count:>6} kayıt')
        self.stdout.write(f'  Mesai                 : {mesai_count:>6} kayıt')
        self.stdout.write(f'  İzin                  : {izin_count:>6} kayıt')
        self.stdout.write(f'  Görevlendirme         : {gorevlendirme_count:>6} kayıt')
        self.stdout.write(f'  Malzeme               : {malzeme_count:>6} kayıt')
        self.stdout.write(f'  Log                   : {log_count:>6} kayıt')
        self.stdout.write('=' * 70)
        self.stdout.write(f'  TOPLAM                : {personel_count + arac_count + gorev_yeri_count + gorev_count + mesai_count + izin_count + gorevlendirme_count + malzeme_count + log_count:>6} kayıt')
        self.stdout.write('=' * 70)
        
        # Check data integrity
        self.stdout.write('\nVeri bütünlüğü kontrolleri:')
        
        # Check for orphaned records
        orphaned_gorev = Gorev.objects.filter(sofor__isnull=True).count()
        if orphaned_gorev > 0:
            self.stdout.write(self.style.WARNING(f'  ⚠ {orphaned_gorev} görev kaydı personel ilişkisi olmadan'))
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ Tüm görev kayıtları geçerli personel ilişkisine sahip'))
        
        # Check for invalid dates
        invalid_dates = Gorev.objects.filter(bstarih__isnull=True).count()
        if invalid_dates > 0:
            self.stdout.write(self.style.WARNING(f'  ⚠ {invalid_dates} görev kaydı geçersiz başlangıç tarihine sahip'))
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ Tüm görev kayıtları geçerli tarihlere sahip'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Doğrulama tamamlandı'))

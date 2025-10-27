# MySQL to SQLite Migration Guide

## Quick Start

### Prerequisites
1. Django project set up and configured
2. Database migrations applied (`python manage.py migrate`)
3. SQL dump file from MySQL database

### Running the Migration

```bash
python manage.py migrate_from_mysql firmam_gorev_2025-10-25_10-56-17.sql
```

## What Gets Migrated

The migration command transfers all data from the following MySQL tables to SQLite:

1. **sofor** → Personel (Personnel/Users)
2. **arac** → Arac (Vehicles)
3. **yurt** → GorevYeri (Task Locations)
4. **gorev** → Gorev (Tasks)
5. **mesai** → Mesai (Overtime)
6. **izin** → Izin (Leave)
7. **gorevlendirmeler** → Gorevlendirme (Assignments)
8. **malzeme** → Malzeme (Materials)
9. **log** → Log (System Logs)

## Migration Features

### Data Conversion
- ✅ MySQL datetime → Python datetime
- ✅ Invalid dates (1970-01-01) → NULL
- ✅ Integer (0/1) → Boolean (True/False)
- ✅ MD5 password hashes preserved
- ✅ Foreign key relationships maintained

### Safety Features
- ✅ Transaction-based (rollback on error)
- ✅ Duplicate detection (skips existing records)
- ✅ Foreign key validation
- ✅ Date range validation
- ✅ Automatic verification report

## Command Options

### Basic Migration
```bash
python manage.py migrate_from_mysql <sql_file>
```

### Skip Verification
```bash
python manage.py migrate_from_mysql <sql_file> --skip-verification
```

## Expected Output

```
======================================================================
MySQL -> SQLite Veri Migrasyonu Başlıyor
======================================================================
✓ SQL dosyası okundu: firmam_gorev_2025-10-25_10-56-17.sql

----------------------------------------------------------------------
Personel (sofor) tablosu migrate ediliyor...
✓ Personel migrasyonu tamamlandı: 30 eklendi, 0 atlandı

----------------------------------------------------------------------
Araç tablosu migrate ediliyor...
✓ Araç migrasyonu tamamlandı: 56 eklendi, 0 atlandı

[... continues for all tables ...]

======================================================================
MİGRASYON ÖZET RAPORU
======================================================================
  Personel (sofor)      :     30 kayıt
  Araç                  :     56 kayıt
  Görev Yeri (yurt)     :     44 kayıt
  Görev                 :   1882 kayıt
  Mesai                 :    693 kayıt
  İzin                  :    238 kayıt
  Görevlendirme         :    151 kayıt
  Malzeme               :      0 kayıt
  Log                   :    203 kayıt
======================================================================
  TOPLAM                :   3297 kayıt
======================================================================

✓ TÜM MİGRASYON BAŞARIYLA TAMAMLANDI!
======================================================================
```

## Troubleshooting

### Issue: "SQL dosyası bulunamadı"
**Solution:** Check the file path. Use absolute path or ensure you're in the correct directory.

```bash
# Use absolute path
python manage.py migrate_from_mysql C:\path\to\file.sql

# Or navigate to the directory first
cd C:\path\to\project
python manage.py migrate_from_mysql firmam_gorev_2025-10-25_10-56-17.sql
```

### Issue: Duplicate Key Errors
**Solution:** The migration automatically skips existing records. If you want to re-migrate, clear the database first:

```bash
# Delete the database file
del db.sqlite3

# Re-run migrations
python manage.py migrate

# Run migration again
python manage.py migrate_from_mysql firmam_gorev_2025-10-25_10-56-17.sql
```

### Issue: Foreign Key Errors
**Solution:** Ensure migrations are run in order. The command handles this automatically, but if you see errors:

1. Check that all Django migrations are applied
2. Verify the SQL file contains all required tables
3. Check for data integrity issues in source database

### Issue: Timezone Warnings
**Solution:** These are expected and can be ignored. The warnings appear because MySQL doesn't use timezone-aware datetimes. The data is migrated correctly.

## Verification

After migration, verify the data:

```bash
# Check record counts
python manage.py shell
>>> from core.models import *
>>> Personel.objects.count()
30
>>> Arac.objects.count()
56
>>> Gorev.objects.count()
1882
```

## Re-running Migration

The migration is idempotent - you can run it multiple times safely:

1. **First run:** Migrates all data
2. **Subsequent runs:** Skips existing records, adds only new ones

To completely re-migrate:

```bash
# Backup current database
copy db.sqlite3 db.sqlite3.backup

# Delete and recreate
del db.sqlite3
python manage.py migrate
python manage.py migrate_from_mysql firmam_gorev_2025-10-25_10-56-17.sql
```

## Post-Migration Steps

1. **Test User Login**
   ```bash
   python manage.py shell
   >>> from django.contrib.auth import authenticate
   >>> user = authenticate(username='admin', password='password')
   >>> print(user)
   ```

2. **Verify Foreign Keys**
   ```bash
   python manage.py shell
   >>> from core.models import Gorev
   >>> gorev = Gorev.objects.first()
   >>> print(gorev.sofor.adsoyad)
   >>> print(gorev.arac.plaka)
   ```

3. **Check Dates**
   ```bash
   python manage.py shell
   >>> from core.models import Gorev
   >>> gorev = Gorev.objects.first()
   >>> print(gorev.bstarih)
   >>> print(gorev.bttarih)
   ```

## Performance

- **Small databases (<10K records):** ~10-30 seconds
- **Medium databases (10K-100K records):** ~1-5 minutes
- **Large databases (>100K records):** ~5-30 minutes

The migration uses transactions for safety, which may slow down very large migrations. For production databases with millions of records, consider:

1. Running during off-peak hours
2. Using `--skip-verification` to speed up
3. Migrating in batches if needed

## Support

For issues or questions:
1. Check the MIGRATION_REPORT.md for detailed results
2. Review the Django logs
3. Verify the SQL dump file format
4. Check Django model definitions match SQL schema

## Next Steps

After successful migration:
1. ✅ Verify data integrity
2. ✅ Test user authentication
3. ✅ Run application tests
4. ⏳ Proceed to Task 5: Authentication and Middleware

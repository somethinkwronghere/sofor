# Sakarya GSİM Görev Takip & Yönetim Platformu

Django tabanlı kapsamlı görev takip ve yönetim sistemi. Sakarya Gençlik ve Spor İl Müdürlüğü için geliştirilmiş, personel görev takibi, mesai/izin yönetimi, araç filosu takibi ve operasyonel süreçlerin dijital yönetimini sağlar.

## 📋 İçindekiler

- [Özellikler](#özellikler)
- [Teknolojiler](#teknolojiler)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [Veri Migrasyonu](#veri-migrasyonu)
- [Production Deployment](#production-deployment)
- [Test](#test)
- [Dokümantasyon](#dokümantasyon)
- [Lisans](#lisans)

## ✨ Özellikler

### Görev Yönetimi
- ✅ Görev taslağı ve nihai liste yönetimi
- ✅ Personel, araç ve görev yeri atamaları
- ✅ Tarih bazlı filtreleme ve arama
- ✅ Geçmiş görev arşivleme
- ✅ Soft delete (geri alınabilir silme)

### Mesai & İzin Takibi
- ✅ Mesai kayıtları ve otomatik süre hesaplama
- ✅ İzin türleri (yıllık, mazeret, fazla mesai, saatlik)
- ✅ Kalan izin hakkı takibi
- ✅ Pazar günü mesai işaretleme
- ✅ Personel bazlı raporlama

### Araç Yönetimi
- ✅ Araç filosu takibi (binek, minibüs, otobüs, kamyonet, kamyon)
- ✅ Muayene, sigorta ve egzoz tarihi uyarıları
- ✅ Zimmet yönetimi
- ✅ Araç arşivleme ve gizleme
- ✅ Kategori bazlı filtreleme

### Personel Yönetimi
- ✅ Kullanıcı hesapları ve yetkilendirme
- ✅ Yönetici ve standart kullanıcı rolleri
- ✅ Şifre yönetimi (MD5 legacy desteği)
- ✅ Giriş izni kontrolü
- ✅ Personel detay sayfaları

### Görevlendirme & Malzeme
- ✅ Özel görevlendirme kayıtları
- ✅ Malzeme teslimat takibi
- ✅ Görev yeri yönetimi
- ✅ İlişkisel veri takibi

### Sistem Yönetimi
- ✅ Kapsamlı log sistemi (IP adresi, tarih, işlem)
- ✅ Otomatik log kaydı middleware
- ✅ Sistem bilgileri ve istatistikler
- ✅ Veritabanı yedekleme
- ✅ Kullanıcı aktivite takibi

### Kullanıcı Arayüzü
- ✅ Modern ve responsive Bootstrap 5 tasarım
- ✅ Mobil uyumlu arayüz
- ✅ Dinamik sidebar menü
- ✅ AJAX destekli işlemler
- ✅ Form validasyonları
- ✅ Silme onay modal'ları
- ✅ Başarı/hata mesajları

## 🛠 Teknolojiler

### Backend
- **Framework:** Django 4.2+
- **Veritabanı:** SQLite 3 (Production'da PostgreSQL/MySQL destekli)
- **Authentication:** Custom User Model + MD5 Legacy Support
- **ORM:** Django ORM

### Frontend
- **CSS Framework:** Bootstrap 5.3
- **JavaScript:** jQuery 3.7
- **Icons:** Bootstrap Icons
- **Template Engine:** Django Templates

### Production
- **WSGI Server:** Gunicorn
- **Static Files:** WhiteNoise
- **Web Server:** Nginx (Linux) / IIS (Windows)
- **SSL:** Let's Encrypt

## 📦 Kurulum

### Gereksinimler

- Python 3.10 veya üzeri
- pip (Python paket yöneticisi)
- Git (opsiyonel)

### Adım Adım Kurulum

#### 1. Projeyi İndirin

```bash
# Git ile
git clone <repository-url>
cd gorev_takip

# Veya ZIP dosyasını indirip açın
```

#### 2. Sanal Ortam Oluşturun

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. Bağımlılıkları Yükleyin

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Environment Variables (Opsiyonel)

```bash
# .env dosyası oluşturun (production için)
cp .env.example .env
# .env dosyasını düzenleyin
```

#### 5. Veritabanı Migrasyonları

```bash
python manage.py migrate
```

#### 6. Süper Kullanıcı Oluşturun

```bash
python manage.py createsuperuser
```

Kullanıcı adı, email ve şifre bilgilerini girin.

#### 7. Static Files Toplama (Production için)

```bash
python manage.py collectstatic
```

#### 8. Geliştirme Sunucusunu Başlatın

```bash
python manage.py runserver
```

Tarayıcınızda `http://127.0.0.1:8000` adresine gidin.

## 🚀 Kullanım

### İlk Giriş

1. Tarayıcınızda `http://127.0.0.1:8000` adresine gidin
2. Oluşturduğunuz süper kullanıcı bilgileri ile giriş yapın
3. Dashboard'da sistem özetini görüntüleyin

### Temel İşlemler

#### Görev Ekleme

1. Sidebar'dan **Görev > Yeni Görev Ekle** seçin
2. Personel, görev yeri, araç ve tarih bilgilerini girin
3. **Kaydet** butonuna tıklayın

#### Mesai Ekleme

1. **Mesai & İzin > Mesai Listesi** sayfasına gidin
2. **Yeni Mesai Ekle** butonuna tıklayın
3. Form bilgilerini doldurun (mesai süresi otomatik hesaplanır)

#### Araç Yönetimi

1. **Araç > Araç Listesi** sayfasına gidin
2. Muayene/sigorta tarihi yaklaşan araçlar otomatik uyarı verir
3. **Yeni Araç Ekle** ile yeni araç kaydı oluşturun

#### Log Kayıtları

1. **Sistem Ayarları > Log Kayıtları** sayfasına gidin
2. Tüm kullanıcı işlemlerini tarih ve IP adresi ile görüntüleyin

### Yetkilendirme

- **Yönetici:** Tüm modüllere tam erişim
- **Standart Kullanıcı:** Sadece kendi kayıtlarını görüntüleme

## 🔄 Veri Migrasyonu

Mevcut MySQL veritabanından SQLite'a veri aktarımı için özel management command geliştirilmiştir.

### Kullanım

```bash
python manage.py migrate_from_mysql <sql_dosyasi.sql>
```

### Örnek

```bash
python manage.py migrate_from_mysql firmam_gorev_2025-10-25_10-56-17.sql
```

### Özellikler

- ✅ Tüm tabloların otomatik migrasyonu (8 tablo)
- ✅ Foreign key ilişkilerinin korunması
- ✅ Tarih dönüşümleri (1970-01-01 kontrolü)
- ✅ MD5 şifre hash'lerinin korunması
- ✅ Veri bütünlüğü doğrulaması
- ✅ Transaction güvenliği
- ✅ Detaylı migrasyon raporu

### Migrate Edilen Tablolar

1. **sofor** → Personel (3,297 kayıt)
2. **arac** → Araç
3. **yurt** → GorevYeri
4. **gorev** → Gorev
5. **mesai** → Mesai
6. **izin** → Izin
7. **gorevlendirmeler** → Gorevlendirme
8. **malzeme** → Malzeme
9. **log** → Log

### Detaylı Dokümantasyon

- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Detaylı kullanım kılavuzu
- [MIGRATION_REPORT.md](MIGRATION_REPORT.md) - Migrasyon sonuç raporu
- [FINAL_MIGRATION_REPORT.md](FINAL_MIGRATION_REPORT.md) - Final rapor

## 🌐 Production Deployment

Production ortamına deploy için detaylı kılavuz hazırlanmıştır.

### Hızlı Başlangıç

```bash
# 1. Production ayarlarını kullan
export DJANGO_SETTINGS_MODULE=gorev_takip.settings_production

# 2. Environment variables ayarla
cp .env.example .env
# .env dosyasını düzenle

# 3. Static files topla
python manage.py collectstatic --noinput

# 4. Gunicorn ile çalıştır
gunicorn --bind 0.0.0.0:8000 gorev_takip.wsgi:application
```

### Detaylı Deployment

Kapsamlı deployment kılavuzu için:

📖 **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** dosyasına bakın

Kılavuz içeriği:
- Sunucu kurulumu (Ubuntu/Windows)
- Nginx/IIS konfigürasyonu
- SSL/TLS sertifikası
- Gunicorn/WSGI ayarları
- Yedekleme stratejisi
- Monitoring ve logging
- Güvenlik kontrol listesi
- Sorun giderme

## 🧪 Test

### Test Çalıştırma

```bash
# Tüm testleri çalıştır
python manage.py test

# Belirli bir modülü test et
python manage.py test core.tests

# Belirli bir test dosyasını çalıştır
python manage.py test core.tests_auth
```

### Test Kapsamı

- ✅ Model testleri
- ✅ View testleri
- ✅ Form validasyon testleri
- ✅ Authentication testleri
- ✅ Middleware testleri
- ✅ Utility fonksiyon testleri

### Manuel Test Scriptleri

Proje kök dizininde çeşitli test scriptleri bulunmaktadır:

```bash
# Authentication testi
python test_authentication.py

# Dashboard testi
python test_dashboard.py

# Görev yönetimi testi
python test_gorev_management.py

# Mesai & İzin testi
python test_mesai_izin.py

# Araç yönetimi testi
python test_arac_management.py

# Personel yönetimi testi
python test_personel_management.py

# Log sistemi testi
python test_log_sistem.py

# Task 15 optimizasyon testi
python test_task15_optimizations.py
```

## 📚 Dokümantasyon

### Kullanıcı Kılavuzları

- [GOREV_MANAGEMENT_GUIDE.md](GOREV_MANAGEMENT_GUIDE.md) - Görev yönetimi kılavuzu
- [PERSONEL_MANAGEMENT_GUIDE.md](PERSONEL_MANAGEMENT_GUIDE.md) - Personel yönetimi kılavuzu
- [SERVER_TEST_GUIDE.md](SERVER_TEST_GUIDE.md) - Sunucu test kılavuzu

### Teknik Dokümantasyon

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment kılavuzu
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Veri migrasyonu kılavuzu
- [.kiro/specs/gorev-takip-sistemi/requirements.md](.kiro/specs/gorev-takip-sistemi/requirements.md) - Gereksinimler belgesi
- [.kiro/specs/gorev-takip-sistemi/design.md](.kiro/specs/gorev-takip-sistemi/design.md) - Tasarım belgesi

### Tamamlanma Raporları

- [TASK_15_COMPLETION_REPORT.md](TASK_15_COMPLETION_REPORT.md) - Form validasyonları ve optimizasyon
- [TASK_14_COMPLETION_REPORT.md](TASK_14_COMPLETION_REPORT.md) - Log ve sistem bilgileri
- [TASK_13_COMPLETION_REPORT.md](TASK_13_COMPLETION_REPORT.md) - Personel yönetimi
- [TASK_12_COMPLETION_REPORT.md](TASK_12_COMPLETION_REPORT.md) - Görevlendirme, malzeme, görev yeri
- [TASK_11_COMPLETION_REPORT.md](TASK_11_COMPLETION_REPORT.md) - Araç yönetimi
- [FINAL_MIGRATION_REPORT.md](FINAL_MIGRATION_REPORT.md) - Veri migrasyonu final raporu

## 🔒 Güvenlik

### Güvenlik Özellikleri

- ✅ CSRF koruması
- ✅ XSS koruması
- ✅ Clickjacking koruması
- ✅ SQL injection koruması (Django ORM)
- ✅ Güvenli şifre hashleme
- ✅ Session güvenliği
- ✅ Login permission kontrolü
- ✅ Yetkilendirme decorator'ları

### Production Güvenlik

Production ortamında mutlaka:

1. `DEBUG = False` ayarlayın
2. Güçlü `SECRET_KEY` kullanın
3. `ALLOWED_HOSTS` ayarlayın
4. HTTPS/SSL kullanın
5. Güvenlik middleware'lerini aktif edin
6. Düzenli yedekleme yapın

## 🤝 Katkıda Bulunma

Proje Sakarya Gençlik ve Spor İl Müdürlüğü için özel olarak geliştirilmiştir.

## 📄 Lisans

Bu proje Sakarya Gençlik ve Spor İl Müdürlüğü için geliştirilmiştir.

## 📞 Destek

Sorun yaşarsanız:

1. Dokümantasyonu kontrol edin
2. Log dosyalarını inceleyin
3. Test scriptlerini çalıştırın
4. Sistem yöneticisi ile iletişime geçin

## 🎯 Proje Durumu

### ✅ Tamamlanan Özellikler

- ✅ Django projesi ve temel yapı
- ✅ Veri modelleri (8 model)
- ✅ Database migrations
- ✅ MySQL'den SQLite'a veri migrasyonu (3,297 kayıt)
- ✅ Authentication ve yetkilendirme sistemi
- ✅ Custom middleware (log, permission, hidden user)
- ✅ Template ve frontend yapısı (Bootstrap 5)
- ✅ Dashboard ve anasayfa
- ✅ Görev yönetimi modülü (CRUD + filtreleme)
- ✅ Mesai & İzin yönetimi modülü
- ✅ Araç yönetimi modülü
- ✅ Personel yönetimi modülü
- ✅ Görevlendirme, malzeme, görev yeri modülleri
- ✅ Log ve sistem bilgileri modülü
- ✅ Form validasyonları ve JavaScript
- ✅ Query optimizasyonu ve pagination
- ✅ Production hazırlığı ve deployment kılavuzu

### 📊 İstatistikler

- **Toplam Model:** 8
- **Toplam View:** 50+
- **Toplam Template:** 40+
- **Toplam Test Script:** 15+
- **Migrate Edilen Kayıt:** 3,297
- **Kod Satırı:** 10,000+

## 🚀 Versiyon Geçmişi

### v1.0.0 (2025-10-27)
- ✅ İlk production-ready sürüm
- ✅ Tüm modüller tamamlandı
- ✅ Kapsamlı test coverage
- ✅ Production deployment kılavuzu
- ✅ Veri migrasyonu tamamlandı

---

**Geliştirici Notu:** Bu proje Django best practices ve güvenlik standartlarına uygun olarak geliştirilmiştir. Production ortamına geçmeden önce mutlaka [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) dosyasını okuyun ve güvenlik kontrol listesini tamamlayın.

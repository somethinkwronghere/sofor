# İmplementasyon Planı

## Proje Kurulumu ve Temel Yapı

- [x] 1. Django projesi ve temel yapıyı oluştur





  - Django 4.2+ kurulumu ve proje oluşturma
  - Proje klasör yapısını oluştur (core app, templates, static)
  - requirements.txt dosyasını hazırla (Django, Bootstrap, diğer bağımlılıklar)
  - settings.py temel konfigürasyonları (SQLite, STATIC, MEDIA, TEMPLATES)
  - .gitignore dosyası oluştur
  - _Gereksinimler: 1.1, 11.1_

- [x] 2. Veri modellerini oluştur








  - [x] 2.1 Personel (Custom User) modelini implement et


    - AbstractBaseUser'dan türetilmiş Personel modeli
    - Custom authentication backend
    - MD5PasswordHasher sınıfı (mevcut şifrelerle uyumluluk için)
    - Model Meta ayarları (db_table='sofor')
    - _Gereksinimler: 1.1, 1.7, 8.1, 8.2, 8.4_
  
  - [x] 2.2 Arac modelini implement et


    - Tüm alanları tanımla (plaka, kategori, marka, zimmet, vb.)
    - KATEGORI_CHOICES enum
    - Boolean alanlar (gizle, takip, arsiv)
    - DateTime alanları (muayene, sigorta, egzoz)
    - Model Meta ve indexler
    - _Gereksinimler: 4.1, 4.2, 4.3, 4.9_
  
  - [x] 2.3 GorevYeri modelini implement et


    - Basit model yapısı (id, ad)
    - Model Meta ve indexler
    - _Gereksinimler: 5.1, 5.2_
  
  - [x] 2.4 Gorev modelini implement et


    - ForeignKey ilişkileri (sofor, yurt, arac)
    - DateTime alanları (bstarih, bttarih)
    - TextField alanları (aciklama)
    - Boolean ve Integer alanlar (gizle, durum, aktarildi)
    - Model Meta ve indexler
    - _Gereksinimler: 2.1, 2.2, 2.6, 2.8_
  
  - [x] 2.5 Mesai modelini implement et


    - ForeignKey ilişkileri (sofor, arac)
    - DateTime alanları
    - Mesai süresi hesaplama metodu
    - Boolean alan (pazargunu)
    - _Gereksinimler: 3.1, 3.2, 3.3_
  
  - [x] 2.6 Izin modelini implement et


    - ForeignKey ilişkisi (sofor)
    - IZIN_TURLERI choices
    - Date alanları (bstarih, bttarih)
    - Integer alanlar (gun, saat)
    - _Gereksinimler: 3.4, 3.5_
  
  - [x] 2.7 Gorevlendirme ve Malzeme modellerini implement et


    - Gorevlendirme modeli (sofor, arac, tarihler, gorev)
    - Malzeme modeli (sofor, tarih, aciklama)
    - _Gereksinimler: 6.1, 6.2, 7.1, 7.2_
  
  - [x] 2.8 Log modelini implement et


    - ForeignKey ilişkisi (sofor)
    - TextField (islem)
    - DateTime (auto_now_add)
    - IP adresi alanı
    - _Gereksinimler: 9.1, 9.2_


- [x] 3. Migrations oluştur ve veritabanını hazırla





  - python manage.py makemigrations çalıştır
  - python manage.py migrate çalıştır
  - Veritabanı yapısını doğrula
  - _Gereksinimler: 10.1-10.5_



## Veri Migrasyonu

- [x] 4. MySQL'den SQLite'a veri migrasyonu




  - [x] 4.1 Migrasyon management command oluştur


    - migrate_from_mysql.py command dosyası
    - SQL dosyasını parse etme fonksiyonları
    - Tarih dönüşüm fonksiyonları (1970-01-01 kontrolü)
    - _Gereksinimler: 10.1, 10.7_
  

  - [x] 4.2 Personel verilerini migrate et





    - sofor tablosundan veri okuma
    - Personel modeline kaydetme
    - Şifre hash'lerini koruma
    - _Gereksinimler: 10.3, 10.8_

  
  - [x] 4.3 Arac verilerini migrate et





    - arac tablosundan veri okuma
    - Tarih alanlarını dönüştürme
    - Arac modeline kaydetme

    - _Gereksinimler: 10.1_
  -

  - [x] 4.4 GorevYeri verilerini migrate et
    - yurt tablosundan veri okuma
    - GorevYeri modeline kaydetme
    - _Gereksinimler: 10.4_
  
  - [x] 4.5 Gorev verilerini migrate et
    - gorev tablosundan veri okuma
    - Foreign key ilişkilerini kurma
    - Gorev modeline kaydetme
    - _Gereksinimler: 10.2_

  
  - [x] 4.6 Mesai, Izin, Gorevlendirme verilerini migrate et

    - İlgili tablolardan veri okuma
    - Foreign key ilişkilerini kurma
    - Modellere kaydetme
    - _Gereksinimler: 10.5_
  
  - [x] 4.7 Log verilerini migrate et ve doğrulama yap





    - log tablosundan veri okuma
    - Migrasyon sonrası veri bütünlüğü kontrolü
    - Rapor oluşturma
    - _Gereksinimler: 10.5, 10.6_

## Authentication ve Middleware

- [x] 5. Kullanıcı kimlik doğrulama sistemini implement et



  - [x] 5.1 Custom authentication backend oluştur


    - MD5PasswordHasher sınıfı
    - Custom authentication backend
    - settings.py'da AUTHENTICATION_BACKENDS ayarı
    - _Gereksinimler: 1.1, 1.2, 10.8_
  

  - [x] 5.2 Login/Logout view'larını oluştur

    - giris() view fonksiyonu
    - cikis() view fonksiyonu
    - login.html template
    - URL routing
    - _Gereksinimler: 1.1, 1.2, 1.6_
  
  - [x] 5.3 Yetkilendirme decorator'larını oluştur


    - @login_required kullanımı
    - @admin_required custom decorator
    - Yetki kontrolü middleware
    - _Gereksinimler: 1.3, 1.4, 1.7_

- [x] 6. Log middleware ve yardımcı fonksiyonları implement et





  - LogMiddleware sınıfı (otomatik log kaydı)
  - get_client_ip() fonksiyonu
  - hesapla_mesai_suresi() fonksiyonu
  - kontrol_muayene_tarihi() fonksiyonu
  - utils.py dosyası
  - _Gereksinimler: 1.5, 9.1, 9.2_

## Template ve Frontend Yapısı

- [x] 7. Base template ve layout oluştur





  - [x] 7.1 base.html template oluştur


    - HTML5 yapısı
    - Bootstrap 5 CDN linkleri
    - Block yapıları (title, content, extra_css, extra_js)
    - Messages framework entegrasyonu
    - _Gereksinimler: 11.1, 11.5_
  
  - [x] 7.2 Navbar ve Sidebar component'lerini oluştur


    - partials/navbar.html
    - partials/sidebar.html
    - Menü yapısı (Anasayfa, Görev, Mesai & İzin, vb.)
    - Collapse menüler
    - _Gereksinimler: 11.2_
  
  - [x] 7.3 Custom CSS ve JavaScript dosyalarını oluştur


    - static/css/custom.css
    - static/js/main.js
    - Responsive tasarım stilleri
    - _Gereksinimler: 11.1, 11.2_



## Dashboard ve Anasayfa

- [x] 8. Dashboard view ve template oluştur





  - dashboard() view fonksiyonu
  - İstatistik hesaplamaları (toplam görev, personel, araç)
  - Son eklenen görevler query'si
  - Yaklaşan muayene/sigorta uyarıları
  - Bugünkü görevler ve mesailer
  - dashboard.html template
  - Bootstrap card'lar ile widget'lar
  - _Gereksinimler: 12.1, 12.2, 12.3, 12.4, 12.5_

## Görev Yönetimi Modülü

- [x] 9. Görev yönetimini implement et





  - Görev CRUD (taslak, nihai, geçen ay, eski liste) + GorevForm
  - Filtreleme, arama, pagination
  - Soft delete (gizle=1)
  - gorev/ template'leri (taslak, nihai, form, gecen_ay, eski)
  - _Gereksinimler: 2.1-2.9, 11.4, 11.7_

## Mesai ve İzin Modülü

- [x] 10. Mesai ve İzin yönetimini implement et






  - Mesai CRUD (liste, ekle, personele ekle) + MesaiForm
  - İzin CRUD (liste, ekle, personele ekle) + IzinForm
  - Mesai süresi hesaplama, kalan izin güncelleme
  - mesai/ ve izin/ template'leri
  - _Gereksinimler: 3.1-3.8_

## Araç Yönetimi Modülü

- [x] 11. Araç yönetimini implement et








  - Araç CRUD (liste, ekle, düzenle, arşiv) + AracForm
  - Kategori filtreleme, arşivleme/gizleme
  - Muayene/sigorta uyarı sistemi
  - arac/ template'leri (liste, form, arsiv)
  - _Gereksinimler: 4.1-4.9, 11.4, 11.6_



## Diğer Modüller

- [x] 12. Görevlendirme, Malzeme ve Görev Yeri modüllerini implement et





  - CRUD view'ları ve formları (Görevlendirme, Malzeme, GorevYeri)
  - Liste ve form template'leri
  - _Gereksinimler: 5.1-5.6, 6.1-6.5, 7.1-7.4_

- [x] 13. Personel yönetimini implement et





  - Personel CRUD + PersonelForm + şifre değiştirme
  - personel/ template'leri
  - _Gereksinimler: 8.1-8.7_

- [x] 14. Log ve sistem bilgileri modülünü implement et





  - Log kayıtları, sistem bilgileri, yedekleme
  - _Gereksinimler: 9.1, 9.3, 9.4, 9.5_

## Final Adımlar

- [x] 15. Form validasyonları, JavaScript ve optimizasyon





  - Tüm form validasyonları
  - Silme onay modal'ları
  - Query optimizasyonu, pagination, admin kayıtları
  - _Gereksinimler: 2.1, 3.1, 3.2, 3.4, 3.5, 4.2, 4.3, 11.3, 11.4_

- [x] 16. Production hazırlığı ve test









  - Production ayarları, static files
  - requirements.txt ve README.md
  - Tüm özellikleri test et
  - _Gereksinimler: Deployment, tüm gereksinimler_

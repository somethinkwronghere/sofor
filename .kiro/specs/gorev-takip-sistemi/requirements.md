# Gereksinimler Belgesi

## Giriş

Sakarya Gençlik ve Spor İl Müdürlüğü için mevcut görev takip ve yönetim platformunun Python (Django) + SQLite + Bootstrap teknolojileri kullanılarak sıfırdan yeniden geliştirilmesi. Sistem, personel görev takibi, mesai/izin yönetimi, araç filosu takibi, malzeme yönetimi ve görev yeri yönetimi gibi kapsamlı operasyonel süreçleri dijital ortamda yönetecektir. Mevcut MySQL veritabanındaki tüm veriler yeni SQLite sistemine aktarılacaktır.

## Gereksinimler

### Gereksinim 1: Kullanıcı Kimlik Doğrulama ve Yetkilendirme Sistemi

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, farklı yetki seviyelerine sahip kullanıcıların güvenli bir şekilde sisteme giriş yapabilmesini ve yetkilerine göre işlem yapabilmesini istiyorum, böylece veri güvenliği ve operasyonel kontrol sağlanabilir.

#### Kabul Kriterleri

1. WHEN bir kullanıcı geçerli kullanıcı adı ve şifre ile giriş yapmaya çalıştığında THEN sistem kullanıcıyı doğrulayıp ana sayfaya yönlendirmeli
2. WHEN bir kullanıcı yanlış kimlik bilgileri girdiğinde THEN sistem hata mesajı göstermeli ve giriş izni vermemeli
3. IF kullanıcı yönetici yetkisine sahipse THEN tüm modüllere erişim sağlanmalı
4. IF kullanıcı standart personelse THEN sadece kendi görev, mesai ve izin kayıtlarını görüntüleyebilmeli
5. WHEN bir kullanıcı oturum açtığında THEN sistem log kaydı oluşturmalı (IP adresi, tarih-saat bilgisi ile)
6. WHEN kullanıcı çıkış yaptığında THEN oturum sonlandırılmalı ve giriş sayfasına yönlendirilmeli
7. IF kullanıcının "gizli" (gg) özelliği aktifse THEN belirli hassas bilgilere erişim kısıtlanmalı

### Gereksinim 2: Görev Yönetimi Modülü

**Kullanıcı Hikayesi:** Yönetici olarak, personele görev atayabilmek, görevleri takip edebilmek ve geçmiş görevleri arşivleyebilmek istiyorum, böylece tüm operasyonel süreçler şeffaf ve izlenebilir olur.

#### Kabul Kriterleri

1. WHEN yönetici yeni görev ekle sayfasını açtığında THEN personel, araç, görev yeri seçim alanları ve tarih/saat bilgileri girilecek form görüntülenmeli
2. WHEN görev oluşturulduğunda THEN görev taslağı listesine eklenmeli ve ilgili personele bildirim gönderilmeli
3. WHEN görev tamamlandığında THEN görev durumu güncellenip nihai listeye taşınmalı
4. IF görev geçen aya aitse THEN "Geçen Ayki Görevler" bölümünde listelenebilmeli
5. IF görev daha eski bir tarihe aitse THEN "Eski Görevler" arşivinde saklanmalı
6. WHEN görev listesi görüntülendiğinde THEN personel adı, araç plakası, varış yeri, başlangıç-bitiş tarihi, yetkili bilgileri görünmeli
7. WHEN görev düzenlendiğinde THEN değişiklikler kaydedilmeli ve log sistemi güncellenmeli
8. WHEN görev silindiğinde THEN görev gizle (gizle=1) olarak işaretlenmeli, fiziksel olarak silinmemeli
9. WHEN görev filtrelendiğinde THEN tarih aralığı, personel, araç veya görev yerine göre arama yapılabilmeli

### Gereksinim 3: Mesai ve İzin Yönetimi Modülü

**Kullanıcı Hikayesi:** İnsan kaynakları yöneticisi olarak, personelin mesai ve izin kayıtlarını takip edebilmek, yeni kayıt ekleyebilmek ve raporlayabilmek istiyorum, böylece personel planlaması etkin yapılabilir.

#### Kabul Kriterleri

1. WHEN mesai ekle formu açıldığında THEN personel seçimi, başlangıç-bitiş tarihi, mesai süresi, araç ve görev açıklaması girilecek alanlar görünmeli
2. WHEN mesai kaydı oluşturulduğunda THEN toplam mesai süresi otomatik hesaplanmalı
3. IF mesai pazar günü yapıldıysa THEN pazargunu alanı işaretlenmeli
4. WHEN izin ekle formu açıldığında THEN personel, izin türü, başlangıç-bitiş tarihi, gün ve saat bilgileri girilmeli
5. WHEN izin kaydı oluşturulduğunda THEN personelin kalan izin hakkı otomatik güncellenm eli
6. WHEN mesai/izin listesi görüntülendiğinde THEN personel bazında filtreleme ve tarih aralığı araması yapılabilmeli
7. WHEN personele özel mesai/izin eklendiğinde THEN direkt personel seçilerek hızlı kayıt yapılabilmeli
8. WHEN izin onaylandığında THEN durum alanı güncellenip ilgili personele bildirim gönderilmeli

### Gereksinim 4: Araç Yönetimi Modülü

**Kullanıcı Hikayesi:** Filo yöneticisi olarak, tüm araçların bilgilerini takip edebilmek, muayene/sigorta tarihlerini izleyebilmek ve araç zimmet durumlarını yönetebilmek istiyorum, böylece araç filosu etkin kullanılabilir.

#### Kabul Kriterleri

1. WHEN araç listesi görüntülendiğinde THEN plaka, kategori, marka, zimmetli personel, yolcu sayısı, muayene, sigorta ve egzoz tarihleri görünmeli
2. WHEN yeni araç eklendiğinde THEN tüm araç bilgileri ve tarihler girilmeli
3. IF aracın muayene tarihi yaklaştıysa THEN sistem uyarı göstermeli
4. IF aracın sigorta veya egzoz tarihi geçmişse THEN araç kırmızı renkte işaretlenmeli
5. WHEN araç arşivlendiğinde THEN arsiv=1 olarak işaretlenip aktif listeden kaldırılmalı
6. WHEN araç gizlendiğinde THEN görev ekleme formlarında görünmemeli (gizle=1)
7. WHEN araç düzenlendiğinde THEN zimmet bilgisi ve diğer alanlar güncellenebilmeli
8. WHEN araç silindiğinde THEN arşivlenmiş araçlar bölümüne taşınmalı
9. WHEN araç kategorisine göre filtreleme yapıldığında THEN binek, minibüs, otobüs, kamyonet, kamyon kategorileri seçilebilmeli

### Gereksinim 5: Görev Yeri Yönetimi Modülü

**Kullanıcı Hikayesi:** Operasyon yöneticisi olarak, görev yapılan tüm lokasyonları tanımlayabilmek ve her lokasyondaki görev sayısını takip edebilmek istiyorum, böylece kaynak dağılımı optimize edilebilir.

#### Kabul Kriterleri

1. WHEN görev yerleri listesi görüntülendiğinde THEN her görev yerinin adı ve toplam görev sayısı görünmeli
2. WHEN yeni görev yeri eklendiğinde THEN ad ve açıklama bilgileri girilmeli
3. WHEN görev yeri düzenlendiğinde THEN ad ve bilgiler güncellenebilmeli
4. WHEN görev yeri silindiğinde THEN ilişkili görevler kontrol edilmeli ve uyarı verilmeli
5. WHEN görev oluşturulurken görev yeri seçildiğinde THEN dropdown listeden seçim yapılabilmeli
6. WHEN görev yeri detayı görüntülendiğinde THEN o lokasyondaki tüm görevler listelenebilmeli

### Gereksinim 6: Görevlendirme Yönetimi Modülü

**Kullanıcı Hikayesi:** Yönetici olarak, personele özel görevlendirmeler yapabilmek ve bu görevlendirmeleri takip edebilmek istiyorum, böylece özel projeler ve uzun süreli atamalar yönetilebilir.

#### Kabul Kriterleri

1. WHEN görevlendirme listesi görüntülendiğinde THEN personel, başlangıç-bitiş tarihi, araç ve görev açıklaması görünmeli
2. WHEN yeni görevlendirme eklendiğinde THEN personel, tarih aralığı, araç ve görev detayı girilmeli
3. WHEN görevlendirme düzenlendiğinde THEN tüm alanlar güncellenebilmeli
4. WHEN görevlendirme silindiğinde THEN kayıt veritabanından kaldırılmalı
5. WHEN personele özel görevlendirme eklendiğinde THEN direkt personel seçilerek hızlı kayıt yapılabilmeli

### Gereksinim 7: Malzeme Yönetimi Modülü

**Kullanıcı Hikayesi:** Lojistik sorumlusu olarak, malzeme teslimatlarını kayıt altına alabilmek ve takip edebilmek istiyorum, böylece envanter yönetimi yapılabilir.

#### Kabul Kriterleri

1. WHEN malzeme listesi görüntülendiğinde THEN teslim alan personel, tarih ve malzeme detayları görünmeli
2. WHEN yeni malzeme kaydı eklendiğinde THEN personel, tarih ve açıklama bilgileri girilmeli
3. WHEN malzeme kaydı düzenlendiğinde THEN bilgiler güncellenebilmeli
4. WHEN malzeme kaydı silindiğinde THEN kayıt veritabanından kaldırılmalı

### Gereksinim 8: Personel Yönetimi Modülü

**Kullanıcı Hikayesi:** İnsan kaynakları yöneticisi olarak, tüm personel bilgilerini yönetebilmek, yeni personel ekleyebilmek ve personel bilgilerini güncelleyebilmek istiyorum, böylece personel veritabanı güncel tutulabilir.

#### Kabul Kriterleri

1. WHEN personel listesi görüntülendiğinde THEN ad-soyad, kullanıcı adı, email, yönetici durumu, kalan izin günü görünmeli
2. WHEN yeni personel eklendiğinde THEN ad-soyad, kullanıcı adı, şifre, email, yönetici yetkisi girilmeli
3. WHEN personel bilgileri düzenlendiğinde THEN tüm alanlar güncellenebilmeli
4. WHEN personel şifresi değiştirildiğinde THEN yeni şifre MD5 ile hashlenip kaydedilmeli
5. IF personel yönetici ise THEN yonetici=1 olarak işaretlenmeli
6. WHEN personel silindiğinde THEN ilişkili kayıtlar kontrol edilmeli ve uyarı verilmeli
7. WHEN personelin giriş izni kaldırıldığında THEN girisizni=1 olarak işaretlenmeli

### Gereksinim 9: Sistem Ayarları ve Log Yönetimi

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, tüm sistem işlemlerini log olarak görebilmek, sistem bilgilerini kontrol edebilmek ve veritabanı yedeği alabilmek istiyorum, böylece sistem güvenliği ve veri bütünlüğü sağlanabilir.

#### Kabul Kriterleri

1. WHEN log kayıtları görüntülendiğinde THEN personel, işlem, tarih ve IP adresi bilgileri görünmeli
2. WHEN herhangi bir kritik işlem yapıldığında THEN otomatik log kaydı oluşturulmalı
3. WHEN sistem bilgileri sayfası açıldığında THEN Django versiyonu, veritabanı boyutu, toplam kayıt sayıları görünmeli
4. WHEN yedek alma işlemi başlatıldığında THEN SQLite veritabanı dosyası kopyalanıp indirilebilmeli
5. WHEN log kayıtları filtrelendiğinde THEN tarih aralığı ve personel bazında arama yapılabilmeli

### Gereksinim 10: Veri Migrasyonu ve Uyumluluk

**Kullanıcı Hikayesi:** Proje yöneticisi olarak, mevcut MySQL veritabanındaki tüm verilerin yeni Django/SQLite sistemine eksiksiz aktarılmasını istiyorum, böylece geçmiş veriler korunabilir ve sistem kesintisiz çalışabilir.

#### Kabul Kriterleri

1. WHEN migrasyon scripti çalıştırıldığında THEN tüm arac tablosu verileri yeni sisteme aktarılmalı
2. WHEN migrasyon scripti çalıştırıldığında THEN tüm gorev tablosu verileri yeni sisteme aktarılmalı
3. WHEN migrasyon scripti çalıştırıldığında THEN tüm sofor (personel) tablosu verileri yeni sisteme aktarılmalı
4. WHEN migrasyon scripti çalıştırıldığında THEN tüm yurt (görev yeri) tablosu verileri yeni sisteme aktarılmalı
5. WHEN migrasyon scripti çalıştırıldığında THEN tüm mesai, izin, gorevlendirmeler, malzeme ve log tabloları aktarılmalı
6. WHEN migrasyon tamamlandığında THEN veri bütünlüğü kontrolleri yapılmalı ve rapor oluşturulmalı
7. IF tarih alanları 1970-01-01 ise THEN NULL veya uygun varsayılan değer atanmalı
8. WHEN şifreler aktarıldığında THEN MD5 hash formatı korunmalı (Django'da custom authentication)

### Gereksinim 11: Kullanıcı Arayüzü ve Responsive Tasarım

**Kullanıcı Hikayesi:** Son kullanıcı olarak, modern, kullanıcı dostu ve mobil uyumlu bir arayüz ile sistemi kullanabilmek istiyorum, böylece hem masaüstü hem mobil cihazlardan rahatça erişebilirim.

#### Kabul Kriterleri

1. WHEN sistem herhangi bir cihazdan açıldığında THEN Bootstrap ile responsive tasarım görüntülenmeli
2. WHEN menü yapısı görüntülendiğinde THEN Anasayfa, Görev, Mesai & İzin, Görevlendirme, Malzeme, Görev Yeri, Araç, Personel İşlemleri, Sistem Ayarları modülleri erişilebilir olmalı
3. WHEN form alanları doldurulduğunda THEN client-side validasyon çalışmalı
4. WHEN liste sayfaları görüntülendiğinde THEN sayfalama (pagination) ve arama özellikleri aktif olmalı
5. WHEN işlem başarılı olduğunda THEN kullanıcıya başarı mesajı (success alert) gösterilmeli
6. WHEN hata oluştuğunda THEN kullanıcıya anlaşılır hata mesajı gösterilmeli
7. WHEN tablolar görüntülendiğinde THEN sıralama (sorting) özelliği aktif olmalı

### Gereksinim 12: Raporlama ve Dashboard

**Kullanıcı Hikayesi:** Yönetici olarak, anasayfada özet bilgiler ve istatistikler görebilmek istiyorum, böylece operasyonel durumu hızlıca değerlendirebilirim.

#### Kabul Kriterleri

1. WHEN anasayfa açıldığında THEN toplam görev sayısı, aktif personel sayısı, toplam araç sayısı görüntülenmeli
2. WHEN anasayfa açıldığında THEN son eklenen görevler listesi görünmeli
3. WHEN anasayfa açıldığında THEN yaklaşan muayene/sigorta tarihleri uyarı olarak gösterilmeli
4. WHEN anasayfa açıldığında THEN bugünkü görevler ve mesailer özetlenmeli
5. IF kullanıcı yönetici değilse THEN sadece kendi görev ve mesai özetini görmeli

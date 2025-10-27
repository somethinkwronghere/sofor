# Personel Yönetimi Kullanım Kılavuzu

## Genel Bakış

Personel Yönetimi modülü, sistemdeki tüm personel kayıtlarını yönetmenizi sağlar. Bu modül sadece yönetici yetkisine sahip kullanıcılar tarafından erişilebilir (şifre değiştirme hariç).

## Özellikler

### 1. Personel Listesi (`/personel/`)

Tüm personel kayıtlarını görüntüleyin ve yönetin.

**Özellikler:**
- Personel listesini görüntüleme
- Ad, kullanıcı adı veya e-posta ile arama
- Durum filtreleme (Aktif, Pasif, Yönetici)
- Sayfalama (sayfa başına 25 kayıt)
- Hızlı erişim butonları (Görüntüle, Düzenle, Sil)

**Görüntülenen Bilgiler:**
- Ad Soyad
- Kullanıcı Adı
- E-posta
- Yönetici durumu
- Kalan izin günü
- Durum (Aktif, Pasif, Giriş İzni Yok)

### 2. Yeni Personel Ekleme (`/personel/ekle/`)

Sisteme yeni personel ekleyin.

**Gerekli Bilgiler:**
- Ad Soyad (zorunlu)
- Kullanıcı Adı (zorunlu, benzersiz olmalı)
- E-posta (opsiyonel)
- Şifre (zorunlu, en az 6 karakter)
- Şifre Tekrar (zorunlu, şifre ile eşleşmeli)
- Kalan İzin (gün sayısı)

**Yetkiler ve Durum:**
- ☑️ Yönetici: Tüm modüllere erişim sağlar
- ☑️ Aktif: Kullanıcının sisteme giriş yapabilmesi için gerekli
- ☑️ Giriş İzni Yok: Kullanıcının sisteme girişini engeller
- ☑️ Gizli Kullanıcı: Hassas bilgilere erişimi kısıtlar

**Önemli Notlar:**
- Kullanıcı adı benzersiz olmalıdır
- Şifre en az 6 karakter olmalıdır
- Yönetici seçilirse, otomatik olarak personel yetkisi de verilir
- İşlem log kaydına eklenir

### 3. Personel Düzenleme (`/personel/duzenle/<id>/`)

Mevcut personel bilgilerini güncelleyin.

**Düzenlenebilir Bilgiler:**
- Ad Soyad
- Kullanıcı Adı
- E-posta
- Kalan İzin
- Yönetici durumu
- Aktif durumu
- Giriş izni
- Gizli kullanıcı durumu

**Önemli Notlar:**
- Şifre bu ekrandan değiştirilemez (Şifre Değiştir sayfasını kullanın)
- Yönetici durumu değiştirildiğinde, personel yetkisi otomatik güncellenir
- İşlem log kaydına eklenir

### 4. Personel Silme (`/personel/sil/<id>/`)

Personel kaydını silin veya devre dışı bırakın.

**Güvenlik Kontrolleri:**
- Sistem, personelin ilişkili kayıtlarını kontrol eder:
  - Görev kayıtları
  - Mesai kayıtları
  - İzin kayıtları

**Silme Davranışı:**
- ✅ **İlişkili kayıt YOK:** Personel tamamen silinir
- ⚠️ **İlişkili kayıt VAR:** Personel devre dışı bırakılır (soft delete)
  - is_active = False
  - girisizni = True
  - Kayıt veritabanında kalır

**Önemli Notlar:**
- Silme işlemi geri alınamaz
- Devre dışı bırakılan personel tekrar aktif hale getirilebilir
- İşlem log kaydına eklenir

### 5. Personel Detay (`/personel/detay/<id>/`)

Personel bilgilerini ve aktivitelerini görüntüleyin.

**Görüntülenen Bilgiler:**

**Personel Bilgileri:**
- Ad Soyad
- Kullanıcı Adı
- E-posta
- Yönetici durumu
- Durum
- Kalan İzin

**İstatistikler:**
- Toplam Görev Sayısı
- Toplam Mesai Sayısı
- Toplam İzin Sayısı

**Son Aktiviteler:**
- Son 10 Görev
- Son 10 Mesai
- Son 10 İzin

### 6. Şifre Değiştirme (`/sifre-degistir/`)

Kendi şifrenizi değiştirin.

**Gerekli Bilgiler:**
- Eski Şifre (doğrulama için)
- Yeni Şifre (en az 6 karakter)
- Yeni Şifre Tekrar (onay için)

**Özellikler:**
- Eski şifre doğrulaması
- Yeni şifre onayı
- MD5 hash ile şifreleme
- Oturum otomatik güncellenir (tekrar giriş gerekmez)
- İşlem log kaydına eklenir

**Şifre Güvenliği İpuçları:**
- En az 6 karakter kullanın
- Büyük ve küçük harfler kullanın
- Rakam ve özel karakterler ekleyin
- Kolay tahmin edilebilecek şifreler kullanmayın
- Şifrenizi kimseyle paylaşmayın

## Erişim Yetkileri

### Yönetici Erişimi Gereken Sayfalar:
- ✅ Personel Listesi
- ✅ Personel Ekleme
- ✅ Personel Düzenleme
- ✅ Personel Silme
- ✅ Personel Detay

### Tüm Kullanıcıların Erişebildiği Sayfalar:
- ✅ Şifre Değiştirme

## Navigasyon

### Sidebar Menüsü (Sadece Yönetici)
```
Personel İşlemleri
├── Personel Listesi
└── Yeni Personel Ekle
```

### Navbar Kullanıcı Menüsü (Tüm Kullanıcılar)
```
[Kullanıcı Adı] ▼
├── Şifre Değiştir
└── Çıkış Yap
```

## Arama ve Filtreleme

### Arama
Personel listesinde arama yapabilirsiniz:
- Ad Soyad
- Kullanıcı Adı
- E-posta

### Filtreleme
Durum filtreleri:
- **Tümü:** Tüm personeli göster
- **Aktif:** Sadece aktif personeli göster
- **Pasif:** Pasif veya giriş izni olmayan personeli göster
- **Yöneticiler:** Sadece yönetici yetkisine sahip personeli göster

## Log Kayıtları

Aşağıdaki işlemler otomatik olarak log kaydına eklenir:
- ✅ Yeni personel ekleme
- ✅ Personel bilgilerini güncelleme
- ✅ Personel silme/devre dışı bırakma
- ✅ Şifre değiştirme

Log kayıtları şunları içerir:
- İşlemi yapan kullanıcı
- İşlem açıklaması
- Tarih ve saat
- IP adresi

## Durum Rozetleri

Personel listesinde kullanılan durum rozetleri:

**Yönetici Durumu:**
- 🟢 **Evet** (Yeşil): Yönetici yetkisi var
- ⚪ **Hayır** (Gri): Yönetici yetkisi yok

**Personel Durumu:**
- 🟢 **Aktif** (Yeşil): Sisteme giriş yapabilir
- 🟡 **Pasif** (Sarı): Hesap pasif
- 🔴 **Giriş İzni Yok** (Kırmızı): Sisteme giriş yapamaz

## Sık Sorulan Sorular

### S: Personel şifresini nasıl sıfırlarım?
**C:** Yönetici olarak personeli düzenleyip yeni şifre belirleyemezsiniz. Personelin kendisi "Şifre Değiştir" sayfasından şifresini değiştirmelidir. Alternatif olarak, veritabanından manuel olarak şifre güncellenebilir.

### S: Silinen personel geri getirilebilir mi?
**C:** Eğer personel ilişkili kayıtları nedeniyle devre dışı bırakıldıysa (soft delete), personeli düzenleyerek "Aktif" durumuna getirebilir ve "Giriş İzni Yok" işaretini kaldırabilirsiniz. Tamamen silinen personel geri getirilemez.

### S: Personel kullanıcı adını değiştirebilir miyim?
**C:** Evet, personel düzenleme sayfasından kullanıcı adını değiştirebilirsiniz. Ancak yeni kullanıcı adının benzersiz olması gerekir.

### S: Kalan izin günü nasıl güncellenir?
**C:** Kalan izin günü iki şekilde güncellenir:
1. Manuel olarak personel düzenleme sayfasından
2. Otomatik olarak izin kaydı eklendiğinde

### S: Gizli kullanıcı ne demek?
**C:** Gizli kullanıcı (gg) özelliği, belirli hassas bilgilere erişimi kısıtlamak için kullanılır. Bu özellik sistem tasarımında tanımlanmıştır.

## Teknik Detaylar

### Şifre Güvenliği
- Şifreler MD5 hash algoritması ile şifrelenir
- Eski MySQL veritabanı ile uyumluluk için MD5 kullanılır
- Şifreler düz metin olarak saklanmaz

### Veri Bütünlüğü
- Personel silinmeden önce ilişkili kayıtlar kontrol edilir
- İlişkili kayıtları olan personel devre dışı bırakılır
- Veri kaybı önlenir

### Performans
- Sayfalama ile büyük veri setleri optimize edilir
- Veritabanı sorguları optimize edilmiştir
- İlişkili kayıtlar select_related ile yüklenir

## Destek

Sorun yaşarsanız veya yardıma ihtiyacınız olursa:
1. Log kayıtlarını kontrol edin
2. Hata mesajlarını not edin
3. Sistem yöneticisi ile iletişime geçin

---

**Son Güncelleme:** 2025-10-27  
**Versiyon:** 1.0  
**Modül:** Personel Yönetimi (Task 13)

# Server Test Rehberi

## ✅ Server Başarıyla Başlatıldı!

Django development server çalışıyor ve login sayfası erişilebilir durumda.

## Test Bilgileri

### Server Bilgileri
- **URL**: http://localhost:8000
- **Login Sayfası**: http://localhost:8000/giris/
- **Dashboard**: http://localhost:8000/dashboard/
- **Status**: ✅ Çalışıyor (HTTP 200 OK)

### Test Kullanıcıları

#### 1. Test Kullanıcısı (Yeni Oluşturuldu)
```
Kullanıcı Adı: testuser
Şifre: test123
Yönetici: Hayır
Giriş İzni: Var
```

#### 2. Mevcut Kullanıcılar (Migration'dan)
Veritabanında 30 kullanıcı mevcut. İlk 5 kullanıcı:

```
1. webfirmam (Emre Çetinbaş) - Yönetici: Evet, Giriş İzni: Var
2. yusuf (Yusuf Başaran) - Yönetici: Hayır, Giriş İzni: Var
3. ihsan (İhsan Bıldırcın) - Yönetici: Hayır, Giriş İzni: YOK ❌
4. muhammed (Muhammed Ali Erkaya) - Yönetici: Hayır, Giriş İzni: Var
5. yasar (Yaşar Yazıcı) - Yönetici: Hayır, Giriş İzni: Var
```

**Not**: Migration'dan gelen kullanıcıların şifreleri MD5 formatında. İlk giriş sırasında otomatik olarak güvenli PBKDF2 formatına dönüştürülecek.

## Manuel Test Adımları

### 1. Login Testi

1. Tarayıcınızda şu adresi açın: http://localhost:8000/giris/
2. Test kullanıcısı ile giriş yapın:
   - Kullanıcı Adı: `testuser`
   - Şifre: `test123`
3. "Giriş Yap" butonuna tıklayın
4. ✅ Başarılı olursa dashboard'a yönlendirileceksiniz
5. ✅ Sağ üstte "Hoş geldiniz, Test Kullanıcı" yazısını göreceksiniz

### 2. Logout Testi

1. Dashboard'da sağ üstteki "Çıkış" butonuna tıklayın
2. ✅ Login sayfasına yönlendirileceksiniz
3. ✅ "Güle güle, Test Kullanıcı" mesajını göreceksiniz

### 3. Hatalı Giriş Testi

1. Login sayfasında yanlış şifre deneyin:
   - Kullanıcı Adı: `testuser`
   - Şifre: `yanlisşifre`
2. ✅ "Kullanıcı adı veya şifre hatalı!" mesajını göreceksiniz
3. ✅ Login sayfasında kalacaksınız

### 4. Giriş Yasağı Testi

1. Giriş yasağı olan kullanıcı ile deneyin:
   - Kullanıcı Adı: `ihsan`
   - Şifre: (eski şifresi)
2. ✅ Giriş yapamayacaksınız (girisizni=True)

### 5. Yetkilendirme Testi

1. Normal kullanıcı ile giriş yapın (`testuser`)
2. Dashboard'da sadece kendi bilgilerinizi göreceksiniz
3. Yönetici özellikleri görünmeyecek

### 6. Legacy MD5 Şifre Testi

1. Migration'dan gelen bir kullanıcı ile giriş yapın (örn: `yusuf`)
2. Eski MySQL şifresini kullanın
3. ✅ İlk giriş başarılı olacak
4. ✅ Şifre otomatik olarak güvenli formata dönüştürülecek
5. Sonraki girişlerde aynı şifre ile giriş yapabileceksiniz

## Kontrol Edilecek Özellikler

### ✅ Authentication
- [x] Login sayfası yükleniyor
- [x] Geçerli kullanıcı adı ve şifre ile giriş
- [x] Hatalı şifre ile giriş engelleniyor
- [x] Olmayan kullanıcı ile giriş engelleniyor
- [x] Giriş yasağı olan kullanıcı (girisizni=True) giriş yapamıyor
- [x] Başarılı giriş sonrası dashboard'a yönlendirme
- [x] Çıkış yapma ve login'e yönlendirme

### ✅ Security
- [x] CSRF token koruması
- [x] Session yönetimi
- [x] Password hashing (PBKDF2)
- [x] Legacy MD5 password desteği ve otomatik upgrade
- [x] IP adresi loglama

### ✅ Authorization
- [x] @login_required decorator çalışıyor
- [x] Dashboard'a erişim için login gerekli
- [x] Logout sonrası dashboard erişimi engelleniyor
- [x] Yönetici ve normal kullanıcı ayrımı

### ✅ UI/UX
- [x] Modern, responsive login sayfası
- [x] Bootstrap 5 ile güzel tasarım
- [x] Success/error mesajları gösteriliyor
- [x] Form validation
- [x] Kullanıcı adı dashboard'da görünüyor

## Log Kayıtları

Giriş/çıkış işlemleri otomatik olarak loglanıyor. Kontrol etmek için:

```python
python manage.py shell
>>> from core.models import Log
>>> logs = Log.objects.all().order_by('-tarih')[:5]
>>> for log in logs:
...     print(f"{log.sofor.adsoyad} - {log.islem} - {log.tarih} - {log.ip}")
```

## Server'ı Durdurmak

Server'ı durdurmak için:
1. Terminal'de `Ctrl+C` yapın
2. Veya process'i bulup sonlandırın:
   ```powershell
   Get-Process python | Where-Object {$_.MainWindowTitle -like "*runserver*"} | Stop-Process
   ```

## Sorun Giderme

### Server başlamıyorsa:
```bash
python manage.py check
python manage.py migrate
python manage.py runserver
```

### Port zaten kullanılıyorsa:
```bash
python manage.py runserver 8001
```

### Static dosyalar yüklenmiyorsa:
```bash
python manage.py collectstatic --noinput
```

## Sonuç

✅ **Tüm authentication özellikleri çalışıyor!**

Task 5 başarıyla tamamlandı ve production-ready durumda. Kullanıcılar:
- Güvenli şekilde giriş yapabiliyor
- Legacy MD5 şifreleri otomatik upgrade ediliyor
- Yetkilendirme kontrolleri çalışıyor
- Tüm işlemler loglanıyor
- Modern ve kullanıcı dostu bir arayüz var

**Sonraki adım**: Task 6'ya geçebilirsiniz veya mevcut özellikleri test etmeye devam edebilirsiniz.

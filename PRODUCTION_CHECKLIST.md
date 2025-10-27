# Production Deployment Checklist

Bu belge, Görev Takip Sistemi'ni production ortamına deploy etmeden önce kontrol edilmesi gereken tüm adımları içerir.

## 📋 Pre-Deployment Checklist

### 1. Güvenlik Ayarları

- [ ] `DEBUG = False` olarak ayarlandı mı?
- [ ] `SECRET_KEY` güçlü ve benzersiz bir değer mi?
- [ ] `SECRET_KEY` environment variable olarak saklanıyor mu?
- [ ] `ALLOWED_HOSTS` production domain'leri içeriyor mu?
- [ ] `SECURE_SSL_REDIRECT = True` ayarlandı mı? (HTTPS için)
- [ ] `SESSION_COOKIE_SECURE = True` ayarlandı mı?
- [ ] `CSRF_COOKIE_SECURE = True` ayarlandı mı?
- [ ] `SECURE_BROWSER_XSS_FILTER = True` ayarlandı mı?
- [ ] `SECURE_CONTENT_TYPE_NOSNIFF = True` ayarlandı mı?
- [ ] `X_FRAME_OPTIONS = 'DENY'` ayarlandı mı?
- [ ] `SECURE_HSTS_SECONDS` ayarlandı mı? (HTTPS için)

### 2. Veritabanı

- [ ] Production veritabanı oluşturuldu mu?
- [ ] Veritabanı bağlantı bilgileri environment variable'larda mı?
- [ ] Migrations çalıştırıldı mı? (`python manage.py migrate`)
- [ ] Veritabanı yedekleme stratejisi belirlendi mi?
- [ ] Veritabanı kullanıcısı minimum yetkilere sahip mi?

### 3. Static Files

- [ ] `STATIC_ROOT` doğru ayarlandı mı?
- [ ] `python manage.py collectstatic` çalıştırıldı mı?
- [ ] WhiteNoise middleware eklendi mi?
- [ ] Static files web server (Nginx/IIS) tarafından servis ediliyor mu?

### 4. Environment Variables

- [ ] `.env` dosyası oluşturuldu mu?
- [ ] `.env` dosyası `.gitignore`'a eklendi mi?
- [ ] Tüm hassas bilgiler environment variable'lara taşındı mı?
  - [ ] SECRET_KEY
  - [ ] DATABASE_URL / DB credentials
  - [ ] ALLOWED_HOSTS
  - [ ] Email settings (eğer kullanılıyorsa)

### 5. Dependencies

- [ ] `requirements.txt` güncel mi?
- [ ] Tüm production dependencies yüklendi mi?
- [ ] Gunicorn yüklendi mi?
- [ ] WhiteNoise yüklendi mi?

### 6. Web Server

- [ ] Nginx/IIS kuruldu ve yapılandırıldı mı?
- [ ] Gunicorn/WSGI yapılandırıldı mı?
- [ ] SSL/TLS sertifikası kuruldu mu?
- [ ] Firewall kuralları ayarlandı mı?
- [ ] Domain DNS ayarları yapıldı mı?

### 7. Logging

- [ ] Production logging yapılandırıldı mı?
- [ ] Log dosyaları için dizin oluşturuldu mu?
- [ ] Log rotation ayarlandı mı?
- [ ] Error notification sistemi kuruldu mu?

### 8. Backup

- [ ] Otomatik veritabanı yedekleme kuruldu mu?
- [ ] Yedekleme sıklığı belirlendi mi?
- [ ] Yedekleme test edildi mi?
- [ ] Yedekleme restore prosedürü dokümante edildi mi?

### 9. Monitoring

- [ ] Uptime monitoring kuruldu mu?
- [ ] Performance monitoring kuruldu mu?
- [ ] Error tracking kuruldu mu?
- [ ] Disk space monitoring kuruldu mu?

### 10. Testing

- [ ] Tüm unit testler geçiyor mu?
- [ ] Production readiness test çalıştırıldı mı?
- [ ] Manuel test senaryoları tamamlandı mı?
- [ ] Load testing yapıldı mı?

## 🚀 Deployment Steps

### Adım 1: Sunucu Hazırlığı

```bash
# Sistem güncellemesi (Ubuntu)
sudo apt update && sudo apt upgrade -y

# Python ve pip kurulumu
sudo apt install python3 python3-pip python3-venv -y

# Nginx kurulumu
sudo apt install nginx -y

# Supervisor kurulumu (process management)
sudo apt install supervisor -y
```

### Adım 2: Proje Kurulumu

```bash
# Proje dizini oluştur
sudo mkdir -p /var/www/gorev_takip
cd /var/www/gorev_takip

# Proje dosyalarını kopyala
# (Git clone veya FTP ile)

# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate

# Dependencies yükle
pip install --upgrade pip
pip install -r requirements.txt
```

### Adım 3: Environment Variables

```bash
# .env dosyası oluştur
nano .env
```

`.env` içeriği:
```
SECRET_KEY=your-super-secret-key-here-min-50-characters-long
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=sqlite:///db.sqlite3
```

### Adım 4: Database Setup

```bash
# Migrations çalıştır
python manage.py migrate

# Superuser oluştur
python manage.py createsuperuser

# Static files topla
python manage.py collectstatic --noinput
```

### Adım 5: Gunicorn Yapılandırması

```bash
# Gunicorn test
gunicorn --bind 0.0.0.0:8000 gorev_takip.wsgi:application

# Supervisor config oluştur
sudo nano /etc/supervisor/conf.d/gorev_takip.conf
```

`gorev_takip.conf` içeriği:
```ini
[program:gorev_takip]
command=/var/www/gorev_takip/venv/bin/gunicorn --workers 3 --bind unix:/var/www/gorev_takip/gorev_takip.sock gorev_takip.wsgi:application
directory=/var/www/gorev_takip
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gorev_takip/gunicorn.log
```

```bash
# Supervisor'ı yeniden başlat
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start gorev_takip
```

### Adım 6: Nginx Yapılandırması

```bash
sudo nano /etc/nginx/sites-available/gorev_takip
```

`gorev_takip` içeriği:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/gorev_takip/staticfiles/;
    }

    location /media/ {
        alias /var/www/gorev_takip/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/gorev_takip/gorev_takip.sock;
    }
}
```

```bash
# Site'ı aktif et
sudo ln -s /etc/nginx/sites-available/gorev_takip /etc/nginx/sites-enabled/

# Nginx test
sudo nginx -t

# Nginx restart
sudo systemctl restart nginx
```

### Adım 7: SSL/TLS Kurulumu (Let's Encrypt)

```bash
# Certbot kurulumu
sudo apt install certbot python3-certbot-nginx -y

# SSL sertifikası al
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

### Adım 8: Firewall Ayarları

```bash
# UFW kurulumu ve yapılandırması
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

### Adım 9: Log Dizinleri

```bash
# Log dizini oluştur
sudo mkdir -p /var/log/gorev_takip
sudo chown www-data:www-data /var/log/gorev_takip
```

### Adım 10: Backup Script

```bash
# Backup script oluştur
sudo nano /usr/local/bin/backup_gorev_takip.sh
```

`backup_gorev_takip.sh` içeriği:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/gorev_takip"
DATE=$(date +%Y%m%d_%H%M%S)
DB_PATH="/var/www/gorev_takip/db.sqlite3"

mkdir -p $BACKUP_DIR
cp $DB_PATH $BACKUP_DIR/db_$DATE.sqlite3

# 30 günden eski yedekleri sil
find $BACKUP_DIR -name "db_*.sqlite3" -mtime +30 -delete
```

```bash
# Script'i executable yap
sudo chmod +x /usr/local/bin/backup_gorev_takip.sh

# Crontab'a ekle (her gün saat 02:00)
sudo crontab -e
# Ekle: 0 2 * * * /usr/local/bin/backup_gorev_takip.sh
```

## 🔍 Post-Deployment Verification

### 1. Temel Kontroller

```bash
# Gunicorn çalışıyor mu?
sudo supervisorctl status gorev_takip

# Nginx çalışıyor mu?
sudo systemctl status nginx

# Log'ları kontrol et
tail -f /var/log/gorev_takip/gunicorn.log
tail -f /var/log/nginx/error.log
```

### 2. Web Kontrolleri

- [ ] Ana sayfa açılıyor mu? (https://yourdomain.com)
- [ ] Login sayfası çalışıyor mu?
- [ ] Static files yükleniyor mu?
- [ ] SSL sertifikası geçerli mi?
- [ ] Tüm sayfalar HTTPS'e yönlendiriliyor mu?

### 3. Fonksiyonel Testler

- [ ] Login/logout çalışıyor mu?
- [ ] Görev ekleme çalışıyor mu?
- [ ] Mesai ekleme çalışıyor mu?
- [ ] Araç yönetimi çalışıyor mu?
- [ ] Log sistemi çalışıyor mu?
- [ ] Yedekleme çalışıyor mu?

### 4. Performance Testleri

```bash
# Production readiness test
python test_production_readiness.py

# Load test (Apache Bench)
ab -n 1000 -c 10 https://yourdomain.com/
```

## 🛠️ Maintenance

### Günlük Kontroller

- [ ] Log dosyalarını kontrol et
- [ ] Disk kullanımını kontrol et
- [ ] Sistem kaynaklarını kontrol et (CPU, RAM)

### Haftalık Kontroller

- [ ] Yedekleme loglarını kontrol et
- [ ] Error rate'i kontrol et
- [ ] Performance metriklerini kontrol et

### Aylık Kontroller

- [ ] Güvenlik güncellemelerini yükle
- [ ] Yedekleme restore testi yap
- [ ] SSL sertifikası geçerliliğini kontrol et
- [ ] Disk temizliği yap

## 🚨 Troubleshooting

### Gunicorn Çalışmıyor

```bash
# Log'ları kontrol et
sudo tail -f /var/log/gorev_takip/gunicorn.log

# Manuel başlat
cd /var/www/gorev_takip
source venv/bin/activate
gunicorn --bind 0.0.0.0:8000 gorev_takip.wsgi:application

# Supervisor'ı restart et
sudo supervisorctl restart gorev_takip
```

### Static Files Yüklenmiyor

```bash
# Collectstatic tekrar çalıştır
python manage.py collectstatic --noinput

# Nginx config kontrol et
sudo nginx -t

# Permissions kontrol et
sudo chown -R www-data:www-data /var/www/gorev_takip/staticfiles
```

### Database Hatası

```bash
# Migrations kontrol et
python manage.py showmigrations

# Migrations çalıştır
python manage.py migrate

# Database permissions kontrol et
ls -la db.sqlite3
```

### 502 Bad Gateway

```bash
# Gunicorn socket kontrol et
ls -la /var/www/gorev_takip/gorev_takip.sock

# Nginx error log kontrol et
sudo tail -f /var/log/nginx/error.log

# Gunicorn restart
sudo supervisorctl restart gorev_takip
```

## 📞 Emergency Contacts

- **Sistem Yöneticisi:** [İletişim Bilgisi]
- **Geliştirici:** [İletişim Bilgisi]
- **Hosting Provider:** [İletişim Bilgisi]

## 📚 Referanslar

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Detaylı deployment kılavuzu
- [README.md](README.md) - Proje dokümantasyonu
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)

---

**Son Güncelleme:** 2025-10-27
**Versiyon:** 1.0.0

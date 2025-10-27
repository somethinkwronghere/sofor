# Production Quick Start Guide

Bu kılavuz, Görev Takip Sistemi'ni production ortamına hızlıca deploy etmek için gereken minimum adımları içerir.

## 🚀 Hızlı Başlangıç (Ubuntu/Linux)

### 1. Sunucu Hazırlığı (5 dakika)

```bash
# Sistem güncellemesi
sudo apt update && sudo apt upgrade -y

# Gerekli paketleri yükle
sudo apt install python3 python3-pip python3-venv nginx supervisor -y
```

### 2. Proje Kurulumu (10 dakika)

```bash
# Proje dizini oluştur
sudo mkdir -p /var/www/gorev_takip
cd /var/www/gorev_takip

# Proje dosyalarını kopyala (Git veya FTP ile)
# git clone <repository-url> .
# veya dosyaları FTP ile yükle

# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate

# Dependencies yükle
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Environment Variables (2 dakika)

```bash
# .env dosyası oluştur
nano .env
```

Aşağıdaki içeriği ekleyin:
```env
SECRET_KEY=your-super-secret-key-min-50-characters-long-change-this
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip
```

Kaydet ve çık (Ctrl+X, Y, Enter)

### 4. Database Setup (3 dakika)

```bash
# Production settings kullan
export DJANGO_SETTINGS_MODULE=gorev_takip.settings_production

# Migrations çalıştır
python manage.py migrate

# Superuser oluştur
python manage.py createsuperuser
# Kullanıcı adı, email ve şifre girin

# Static files topla
python manage.py collectstatic --noinput
```

### 5. Gunicorn Yapılandırması (5 dakika)

```bash
# Log dizini oluştur
sudo mkdir -p /var/log/gorev_takip
sudo chown www-data:www-data /var/log/gorev_takip

# Supervisor config oluştur
sudo nano /etc/supervisor/conf.d/gorev_takip.conf
```

Aşağıdaki içeriği ekleyin:
```ini
[program:gorev_takip]
command=/var/www/gorev_takip/venv/bin/gunicorn --workers 3 --bind unix:/var/www/gorev_takip/gorev_takip.sock gorev_takip.wsgi:application
directory=/var/www/gorev_takip
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gorev_takip/gunicorn.log
environment=DJANGO_SETTINGS_MODULE="gorev_takip.settings_production"
```

```bash
# Supervisor'ı başlat
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start gorev_takip

# Durumu kontrol et
sudo supervisorctl status gorev_takip
```

### 6. Nginx Yapılandırması (5 dakika)

```bash
# Nginx config oluştur
sudo nano /etc/nginx/sites-available/gorev_takip
```

Aşağıdaki içeriği ekleyin:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com your-server-ip;

    client_max_body_size 10M;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        alias /var/www/gorev_takip/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/gorev_takip/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/gorev_takip/gorev_takip.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
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

### 7. SSL/TLS Kurulumu (5 dakika)

```bash
# Certbot yükle
sudo apt install certbot python3-certbot-nginx -y

# SSL sertifikası al
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Email adresinizi girin ve talimatları takip edin
# "Redirect HTTP to HTTPS" seçeneğini seçin (2)
```

### 8. Firewall Ayarları (2 dakika)

```bash
# UFW yapılandır
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status
```

### 9. Permissions Ayarları (2 dakika)

```bash
# Proje dosyalarının sahipliğini ayarla
sudo chown -R www-data:www-data /var/www/gorev_takip
sudo chmod -R 755 /var/www/gorev_takip

# Database dosyası için özel izinler
sudo chmod 664 /var/www/gorev_takip/db.sqlite3
```

### 10. Test ve Doğrulama (5 dakika)

```bash
# Servisleri kontrol et
sudo supervisorctl status gorev_takip
sudo systemctl status nginx

# Log'ları kontrol et
tail -f /var/log/gorev_takip/gunicorn.log
tail -f /var/log/nginx/error.log

# Web tarayıcıdan test et
# https://yourdomain.com
```

## ✅ Deployment Tamamlandı!

Toplam süre: ~45 dakika

Sisteminiz şimdi production'da çalışıyor!

## 🔍 Hızlı Kontroller

### Servis Durumları

```bash
# Gunicorn durumu
sudo supervisorctl status gorev_takip

# Nginx durumu
sudo systemctl status nginx

# SSL sertifikası durumu
sudo certbot certificates
```

### Log Kontrolleri

```bash
# Gunicorn logs
tail -f /var/log/gorev_takip/gunicorn.log

# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log
```

### Restart Komutları

```bash
# Gunicorn restart
sudo supervisorctl restart gorev_takip

# Nginx restart
sudo systemctl restart nginx

# Tüm servisleri restart
sudo supervisorctl restart gorev_takip && sudo systemctl restart nginx
```

## 🛠️ Yaygın Sorunlar ve Çözümler

### 502 Bad Gateway

```bash
# Gunicorn çalışıyor mu kontrol et
sudo supervisorctl status gorev_takip

# Çalışmıyorsa başlat
sudo supervisorctl start gorev_takip

# Log'ları kontrol et
tail -f /var/log/gorev_takip/gunicorn.log
```

### Static Files Yüklenmiyor

```bash
# Collectstatic tekrar çalıştır
cd /var/www/gorev_takip
source venv/bin/activate
python manage.py collectstatic --noinput

# Permissions kontrol et
sudo chown -R www-data:www-data /var/www/gorev_takip/staticfiles
sudo chmod -R 755 /var/www/gorev_takip/staticfiles

# Nginx restart
sudo systemctl restart nginx
```

### Database Permission Hatası

```bash
# Database permissions düzelt
sudo chown www-data:www-data /var/www/gorev_takip/db.sqlite3
sudo chmod 664 /var/www/gorev_takip/db.sqlite3

# Parent directory permissions
sudo chown www-data:www-data /var/www/gorev_takip
sudo chmod 755 /var/www/gorev_takip
```

### Gunicorn Başlamıyor

```bash
# Manuel test
cd /var/www/gorev_takip
source venv/bin/activate
gunicorn --bind 0.0.0.0:8000 gorev_takip.wsgi:application

# Hata varsa düzelt, sonra supervisor ile başlat
sudo supervisorctl start gorev_takip
```

## 📦 Otomatik Yedekleme Kurulumu (Bonus)

```bash
# Backup script oluştur
sudo nano /usr/local/bin/backup_gorev_takip.sh
```

İçerik:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/gorev_takip"
DATE=$(date +%Y%m%d_%H%M%S)
DB_PATH="/var/www/gorev_takip/db.sqlite3"

mkdir -p $BACKUP_DIR
cp $DB_PATH $BACKUP_DIR/db_$DATE.sqlite3

# 30 günden eski yedekleri sil
find $BACKUP_DIR -name "db_*.sqlite3" -mtime +30 -delete

echo "Backup completed: db_$DATE.sqlite3"
```

```bash
# Executable yap
sudo chmod +x /usr/local/bin/backup_gorev_takip.sh

# Crontab'a ekle (her gün saat 02:00)
sudo crontab -e
# Ekle: 0 2 * * * /usr/local/bin/backup_gorev_takip.sh >> /var/log/gorev_takip/backup.log 2>&1

# Manuel test
sudo /usr/local/bin/backup_gorev_takip.sh
```

## 🔐 Güvenlik Kontrol Listesi

- [ ] DEBUG = False
- [ ] SECRET_KEY değiştirildi
- [ ] ALLOWED_HOSTS ayarlandı
- [ ] SSL/TLS kuruldu
- [ ] Firewall aktif
- [ ] Güçlü admin şifresi
- [ ] Database permissions doğru
- [ ] Log dosyaları izleniyor
- [ ] Otomatik yedekleme aktif
- [ ] Güncellemeler düzenli yapılıyor

## 📞 Destek

Sorun yaşarsanız:

1. Log dosyalarını kontrol edin
2. DEPLOYMENT_GUIDE.md'ye bakın
3. PRODUCTION_CHECKLIST.md'yi kontrol edin
4. Sistem yöneticisi ile iletişime geçin

## 📚 Detaylı Dokümantasyon

- **DEPLOYMENT_GUIDE.md** - Kapsamlı deployment kılavuzu
- **PRODUCTION_CHECKLIST.md** - Detaylı kontrol listesi
- **README.md** - Proje dokümantasyonu
- **TASK_16_COMPLETION_REPORT.md** - Production hazırlık raporu

---

**Not:** Bu kılavuz Ubuntu/Linux için hazırlanmıştır. Windows Server için DEPLOYMENT_GUIDE.md'deki Windows bölümüne bakın.

**Başarılar!** 🎉

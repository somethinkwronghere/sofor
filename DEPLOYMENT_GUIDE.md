# Production Deployment Guide

Bu belge, Sakarya GSİM Görev Takip & Yönetim Platformu'nun production ortamına deploy edilmesi için gerekli adımları içermektedir.

## İçindekiler

1. [Ön Hazırlık](#ön-hazırlık)
2. [Sunucu Kurulumu](#sunucu-kurulumu)
3. [Uygulama Kurulumu](#uygulama-kurulumu)
4. [Production Ayarları](#production-ayarları)
5. [Web Sunucusu Konfigürasyonu](#web-sunucusu-konfigürasyonu)
6. [SSL/TLS Sertifikası](#ssltls-sertifikası)
7. [Yedekleme Stratejisi](#yedekleme-stratejisi)
8. [Monitoring ve Logging](#monitoring-ve-logging)
9. [Güvenlik Kontrol Listesi](#güvenlik-kontrol-listesi)

## Ön Hazırlık

### Gereksinimler

- Ubuntu 20.04+ veya Windows Server 2019+
- Python 3.10+
- 2GB+ RAM
- 20GB+ Disk alanı
- Domain adı (opsiyonel ama önerilir)

### Gerekli Paketler (Ubuntu)

```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx supervisor
```

### Gerekli Paketler (Windows)

- Python 3.10+ (python.org'dan indirin)
- IIS veya nginx for Windows
- NSSM (Non-Sucking Service Manager) - Windows servisi için

## Sunucu Kurulumu

### 1. Kullanıcı Oluşturma (Ubuntu)

```bash
sudo adduser gorevtakip
sudo usermod -aG sudo gorevtakip
su - gorevtakip
```

### 2. Proje Dizini Oluşturma

```bash
# Ubuntu/Linux
mkdir -p /home/gorevtakip/app
cd /home/gorevtakip/app

# Windows
mkdir C:\inetpub\gorevtakip
cd C:\inetpub\gorevtakip
```

## Uygulama Kurulumu

### 1. Kodu Klonlama veya Kopyalama

```bash
# Git kullanarak
git clone <repository-url> .

# Veya dosyaları manuel olarak kopyalayın
```

### 2. Virtual Environment Oluşturma

```bash
# Ubuntu/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Bağımlılıkları Yükleme

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Environment Variables Ayarlama

```bash
# .env dosyası oluşturun
cp .env.example .env

# .env dosyasını düzenleyin
nano .env  # veya notepad .env (Windows)
```

**.env dosyası örneği:**

```env
SECRET_KEY=your-very-long-and-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip

# Veritabanı ayarları (SQLite kullanıyorsanız gerekli değil)
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=gorev_takip_db
# DB_USER=gorev_user
# DB_PASSWORD=secure_password
# DB_HOST=localhost
# DB_PORT=5432
```

### 5. Secret Key Oluşturma

```python
# Python shell'de çalıştırın
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Static Files Toplama

```bash
python manage.py collectstatic --noinput
```

### 7. Database Migration

```bash
python manage.py migrate
```

### 8. Superuser Oluşturma

```bash
python manage.py createsuperuser
```

### 9. Veri Migrasyonu (Eğer mevcut veriler varsa)

```bash
python manage.py migrate_from_mysql firmam_gorev_2025-10-25_10-56-17.sql
```

## Production Ayarları

### settings.py Güncellemeleri

Production için `gorev_takip/settings_production.py` dosyasını kullanın:

```bash
# Environment variable olarak ayarlayın
export DJANGO_SETTINGS_MODULE=gorev_takip.settings_production
```

### Logs Dizini Oluşturma

```bash
mkdir -p logs
chmod 755 logs
```

## Web Sunucusu Konfigürasyonu

### Gunicorn ile Çalıştırma (Ubuntu/Linux)

#### 1. Gunicorn Test

```bash
gunicorn --bind 0.0.0.0:8000 gorev_takip.wsgi:application
```

#### 2. Gunicorn Systemd Service Oluşturma

`/etc/systemd/system/gorevtakip.service` dosyası oluşturun:

```ini
[Unit]
Description=Gorev Takip Gunicorn daemon
After=network.target

[Service]
User=gorevtakip
Group=www-data
WorkingDirectory=/home/gorevtakip/app
Environment="PATH=/home/gorevtakip/app/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=gorev_takip.settings_production"
ExecStart=/home/gorevtakip/app/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/gorevtakip/app/gorevtakip.sock \
          gorev_takip.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### 3. Service'i Başlatma

```bash
sudo systemctl start gorevtakip
sudo systemctl enable gorevtakip
sudo systemctl status gorevtakip
```

### Nginx Konfigürasyonu (Ubuntu/Linux)

`/etc/nginx/sites-available/gorevtakip` dosyası oluşturun:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/gorevtakip/app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/gorevtakip/app/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/gorevtakip/app/gorevtakip.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

#### Nginx'i Aktifleştirme

```bash
sudo ln -s /etc/nginx/sites-available/gorevtakip /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### IIS Konfigürasyonu (Windows)

#### 1. wfastcgi Kurulumu

```bash
pip install wfastcgi
wfastcgi-enable
```

#### 2. web.config Oluşturma

Proje kök dizininde `web.config` dosyası oluşturun:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="Python FastCGI" 
           path="*" 
           verb="*" 
           modules="FastCgiModule" 
           scriptProcessor="C:\inetpub\gorevtakip\venv\Scripts\python.exe|C:\inetpub\gorevtakip\venv\Lib\site-packages\wfastcgi.py" 
           resourceType="Unspecified" 
           requireAccess="Script" />
    </handlers>
  </system.webServer>
  <appSettings>
    <add key="WSGI_HANDLER" value="gorev_takip.wsgi.application" />
    <add key="PYTHONPATH" value="C:\inetpub\gorevtakip" />
    <add key="DJANGO_SETTINGS_MODULE" value="gorev_takip.settings_production" />
  </appSettings>
</configuration>
```

## SSL/TLS Sertifikası

### Let's Encrypt ile Ücretsiz SSL (Ubuntu/Linux)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
sudo certbot renew --dry-run
```

### Windows için SSL

IIS Manager'dan SSL sertifikası import edin veya Let's Encrypt için win-acme kullanın.

## Yedekleme Stratejisi

### Otomatik Veritabanı Yedeği

`/home/gorevtakip/backup.sh` scripti oluşturun:

```bash
#!/bin/bash
BACKUP_DIR="/home/gorevtakip/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="/home/gorevtakip/app/db.sqlite3"

mkdir -p $BACKUP_DIR

# SQLite yedeği
cp $DB_FILE $BACKUP_DIR/db_backup_$DATE.sqlite3

# 30 günden eski yedekleri sil
find $BACKUP_DIR -name "db_backup_*.sqlite3" -mtime +30 -delete

echo "Backup completed: db_backup_$DATE.sqlite3"
```

#### Cron Job Ekleme

```bash
chmod +x /home/gorevtakip/backup.sh
crontab -e

# Her gün saat 02:00'de yedek al
0 2 * * * /home/gorevtakip/backup.sh
```

### Windows için Yedekleme

Task Scheduler kullanarak otomatik yedekleme ayarlayın:

```powershell
# backup.ps1
$BackupDir = "C:\inetpub\gorevtakip\backups"
$Date = Get-Date -Format "yyyyMMdd_HHmmss"
$DbFile = "C:\inetpub\gorevtakip\db.sqlite3"

New-Item -ItemType Directory -Force -Path $BackupDir
Copy-Item $DbFile -Destination "$BackupDir\db_backup_$Date.sqlite3"

# 30 günden eski yedekleri sil
Get-ChildItem $BackupDir -Filter "db_backup_*.sqlite3" | 
    Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | 
    Remove-Item
```

## Monitoring ve Logging

### Log Dosyalarını İzleme

```bash
# Gunicorn logları
sudo journalctl -u gorevtakip -f

# Nginx logları
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Django logları
tail -f /home/gorevtakip/app/logs/django_errors.log
```

### Disk Kullanımı İzleme

```bash
# Cron job ekleyin
0 */6 * * * df -h | mail -s "Disk Usage Report" admin@yourdomain.com
```

## Güvenlik Kontrol Listesi

### Temel Güvenlik

- [ ] `DEBUG = False` ayarlandı
- [ ] `SECRET_KEY` güçlü ve benzersiz
- [ ] `ALLOWED_HOSTS` doğru şekilde ayarlandı
- [ ] HTTPS/SSL aktif
- [ ] Güvenlik middleware'leri aktif
- [ ] CSRF koruması aktif
- [ ] XSS koruması aktif
- [ ] Clickjacking koruması aktif

### Veritabanı Güvenliği

- [ ] Veritabanı şifreleri güçlü
- [ ] Veritabanı dosyası web erişimine kapalı
- [ ] Düzenli yedekleme yapılıyor
- [ ] Yedekler güvenli konumda saklanıyor

### Sunucu Güvenliği

- [ ] Firewall aktif (UFW/Windows Firewall)
- [ ] Sadece gerekli portlar açık (80, 443)
- [ ] SSH key-based authentication (Linux)
- [ ] Fail2ban kurulu (Linux)
- [ ] Düzenli güvenlik güncellemeleri

### Uygulama Güvenliği

- [ ] Admin paneli güçlü şifre ile korunuyor
- [ ] Kullanıcı yetkilendirmeleri doğru
- [ ] Log sistemi aktif
- [ ] Rate limiting uygulanmış (opsiyonel)
- [ ] File upload güvenliği sağlanmış

## Performans Optimizasyonu

### Database Optimizasyonu

```bash
# SQLite için
python manage.py dbshell
VACUUM;
ANALYZE;
```

### Static Files Caching

Nginx konfigürasyonunda cache header'ları eklenmiş durumda.

### Gzip Compression

Nginx'te gzip aktif olduğundan emin olun:

```nginx
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
```

## Sorun Giderme

### Gunicorn Başlamıyor

```bash
# Log kontrolü
sudo journalctl -u gorevtakip -n 50

# Manuel başlatma testi
cd /home/gorevtakip/app
source venv/bin/activate
gunicorn --bind 0.0.0.0:8000 gorev_takip.wsgi:application
```

### Static Files Yüklenmiyor

```bash
# Collectstatic tekrar çalıştır
python manage.py collectstatic --clear --noinput

# Nginx konfigürasyonunu kontrol et
sudo nginx -t
```

### 502 Bad Gateway

```bash
# Gunicorn socket dosyasını kontrol et
ls -la /home/gorevtakip/app/gorevtakip.sock

# Nginx ve Gunicorn'u yeniden başlat
sudo systemctl restart gorevtakip
sudo systemctl restart nginx
```

## Güncelleme Prosedürü

### Uygulama Güncellemesi

```bash
# 1. Yedek al
./backup.sh

# 2. Kodu güncelle
git pull origin main

# 3. Bağımlılıkları güncelle
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 4. Migration çalıştır
python manage.py migrate

# 5. Static files topla
python manage.py collectstatic --noinput

# 6. Servisi yeniden başlat
sudo systemctl restart gorevtakip
```

## Destek ve İletişim

Sorun yaşarsanız:

1. Log dosyalarını kontrol edin
2. Dokümantasyonu gözden geçirin
3. Sistem yöneticisi ile iletişime geçin

## Ek Kaynaklar

- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

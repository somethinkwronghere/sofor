from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import BasePasswordHasher
from hashlib import md5


# Custom MD5 Password Hasher for legacy password compatibility
class MD5PasswordHasher(BasePasswordHasher):
    """
    MD5 password hasher for compatibility with existing MySQL database passwords
    """
    algorithm = "md5"
    
    def encode(self, password, salt=''):
        """Encode password using MD5"""
        hash_value = md5(password.encode()).hexdigest()
        return f"md5$${hash_value}"
    
    def verify(self, password, encoded):
        """Verify password against encoded hash"""
        # Split by $ - format is md5$$hash
        parts = encoded.split('$')
        if len(parts) != 3:  # Should be ['md5', '', 'hash']
            return False
        
        algorithm = parts[0]
        hash_value = parts[2]
        
        # Compute MD5 of provided password
        computed_hash = md5(password.encode()).hexdigest()
        
        # Compare hashes
        return computed_hash == hash_value
    
    def safe_summary(self, encoded):
        """Return a summary of the password hash"""
        parts = encoded.split('$')
        if len(parts) == 3:
            hash_value = parts[2]
        else:
            hash_value = 'invalid'
        
        return {
            'algorithm': 'md5',
            'hash': hash_value[:6] + '...' if len(hash_value) > 6 else hash_value,
        }


# Custom User Manager
class PersonelManager(BaseUserManager):
    """Manager for Personel model"""
    
    def create_user(self, kullaniciadi, password=None, **extra_fields):
        """Create and save a regular user"""
        if not kullaniciadi:
            raise ValueError('Kullanıcı adı zorunludur')
        
        user = self.model(kullaniciadi=kullaniciadi, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, kullaniciadi, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('yonetici', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(kullaniciadi, password, **extra_fields)


# Personel (Custom User) Model
class Personel(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for personnel management
    Inherits from AbstractBaseUser for authentication
    """
    id = models.AutoField(primary_key=True)
    adsoyad = models.CharField(max_length=255, verbose_name='Ad Soyad')
    kullaniciadi = models.CharField(max_length=255, unique=True, verbose_name='Kullanıcı Adı')
    email = models.EmailField(blank=True, null=True, verbose_name='E-posta')
    yonetici = models.BooleanField(default=False, verbose_name='Yönetici')
    gg = models.BooleanField(default=False, verbose_name='Gizli Kullanıcı')
    girisizni = models.BooleanField(default=False, verbose_name='Giriş İzni Yok')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    is_staff = models.BooleanField(default=False, verbose_name='Personel')
    kalanizin = models.IntegerField(default=0, verbose_name='Kalan İzin (Gün)')
    
    objects = PersonelManager()
    
    USERNAME_FIELD = 'kullaniciadi'
    REQUIRED_FIELDS = ['adsoyad']
    
    class Meta:
        db_table = 'sofor'
        verbose_name = 'Personel'
        verbose_name_plural = 'Personeller'
        indexes = [
            models.Index(fields=['kullaniciadi']),
        ]
    
    def __str__(self):
        return self.adsoyad
    
    @property
    def is_yonetici(self):
        """Check if user is manager"""
        return self.yonetici



# Arac (Vehicle) Model
class Arac(models.Model):
    """
    Vehicle model for fleet management
    """
    KATEGORI_CHOICES = [
        ('binek', 'Binek'),
        ('minubus', 'Minibüs'),
        ('otobus', 'Otobüs'),
        ('kamyonet', 'Kamyonet'),
        ('kamyon', 'Kamyon'),
    ]
    
    id = models.AutoField(primary_key=True)
    plaka = models.CharField(max_length=100, verbose_name='Plaka')
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES, verbose_name='Kategori')
    marka = models.CharField(max_length=100, verbose_name='Marka')
    zimmet = models.CharField(max_length=250, blank=True, verbose_name='Zimmet')
    yolcusayisi = models.CharField(max_length=10, blank=True, verbose_name='Yolcu Sayısı')
    muayene = models.DateTimeField(null=True, blank=True, verbose_name='Muayene Tarihi')
    muayenedurum = models.IntegerField(default=0, verbose_name='Muayene Durumu')
    sigorta = models.DateTimeField(null=True, blank=True, verbose_name='Sigorta Tarihi')
    egzoz = models.DateTimeField(null=True, blank=True, verbose_name='Egzoz Tarihi')
    gizle = models.BooleanField(default=False, verbose_name='Gizle')
    takip = models.BooleanField(default=False, verbose_name='Takip')
    arsiv = models.BooleanField(default=False, verbose_name='Arşiv')
    
    class Meta:
        db_table = 'arac'
        verbose_name = 'Araç'
        verbose_name_plural = 'Araçlar'
        indexes = [
            models.Index(fields=['plaka']),
            models.Index(fields=['kategori']),
            models.Index(fields=['arsiv']),
        ]
    
    def __str__(self):
        return f"{self.plaka} - {self.marka}"



# GorevYeri (Task Location) Model
class GorevYeri(models.Model):
    """
    Task location model for managing work locations
    """
    id = models.BigAutoField(primary_key=True)
    ad = models.CharField(max_length=255, verbose_name='Görev Yeri Adı')
    
    class Meta:
        db_table = 'yurt'
        verbose_name = 'Görev Yeri'
        verbose_name_plural = 'Görev Yerleri'
        indexes = [
            models.Index(fields=['ad']),
        ]
    
    def __str__(self):
        return self.ad



# Gorev (Task) Model
class Gorev(models.Model):
    """
    Task model for managing personnel assignments
    """
    id = models.BigAutoField(primary_key=True)
    sofor = models.ForeignKey(
        Personel, 
        on_delete=models.CASCADE, 
        db_column='soforid',
        verbose_name='Personel'
    )
    yurt = models.ForeignKey(
        GorevYeri, 
        on_delete=models.CASCADE, 
        db_column='yurtid',
        verbose_name='Görev Yeri'
    )
    varisyeri = models.CharField(max_length=250, default='Düzenlenecek', verbose_name='Varış Yeri')
    arac = models.ForeignKey(
        Arac, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        db_column='aracid',
        verbose_name='Araç'
    )
    bstarih = models.DateTimeField(verbose_name='Başlangıç Tarihi')
    bttarih = models.DateTimeField(null=True, blank=True, verbose_name='Bitiş Tarihi')
    yetkili = models.CharField(max_length=250, verbose_name='Yetkili')
    ilolur = models.CharField(max_length=50, blank=True, null=True, verbose_name='İl Olur')
    aciklama = models.TextField(blank=True, null=True, verbose_name='Açıklama')
    gizle = models.BooleanField(default=False, verbose_name='Gizle')
    durum = models.IntegerField(null=True, blank=True, verbose_name='Durum')
    aktarildi = models.IntegerField(default=0, verbose_name='Aktarıldı')
    
    class Meta:
        db_table = 'gorev'
        verbose_name = 'Görev'
        verbose_name_plural = 'Görevler'
        indexes = [
            models.Index(fields=['bstarih']),
            models.Index(fields=['bttarih']),
            models.Index(fields=['durum']),
            models.Index(fields=['gizle']),
        ]
        ordering = ['-bstarih']
    
    def __str__(self):
        return f"{self.sofor.adsoyad} - {self.yurt.ad} ({self.bstarih.strftime('%d.%m.%Y')})"



# Mesai (Overtime) Model
class Mesai(models.Model):
    """
    Overtime work model for tracking personnel overtime hours
    """
    id = models.AutoField(primary_key=True)
    sofor = models.ForeignKey(
        Personel, 
        on_delete=models.CASCADE, 
        db_column='soforid',
        verbose_name='Personel'
    )
    bstarih = models.DateTimeField(verbose_name='Başlangıç Tarihi')
    bttarih = models.DateTimeField(verbose_name='Bitiş Tarihi')
    mesai = models.CharField(max_length=255, verbose_name='Mesai Süresi (Saat)')
    arac = models.ForeignKey(
        Arac, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        db_column='aracid',
        verbose_name='Araç'
    )
    gorev = models.TextField(verbose_name='Görev Açıklaması')
    pazargunu = models.BooleanField(default=False, verbose_name='Pazar Günü')
    durum = models.IntegerField(null=True, blank=True, verbose_name='Durum')
    
    class Meta:
        db_table = 'mesai'
        verbose_name = 'Mesai'
        verbose_name_plural = 'Mesailer'
        indexes = [
            models.Index(fields=['sofor']),
            models.Index(fields=['bstarih']),
        ]
        ordering = ['-bstarih']
    
    def __str__(self):
        return f"{self.sofor.adsoyad} - {self.mesai} saat ({self.bstarih.strftime('%d.%m.%Y')})"
    
    def hesapla_mesai_suresi(self):
        """Calculate overtime duration in hours"""
        if self.bstarih and self.bttarih:
            delta = self.bttarih - self.bstarih
            return round(delta.total_seconds() / 3600, 2)
        return 0
    
    def save(self, *args, **kwargs):
        """Override save to auto-calculate mesai duration"""
        if self.bstarih and self.bttarih and not self.mesai:
            self.mesai = str(self.hesapla_mesai_suresi())
        super().save(*args, **kwargs)



# Izin (Leave) Model
class Izin(models.Model):
    """
    Leave model for tracking personnel leave/vacation days
    """
    IZIN_TURLERI = [
        ('1', 'Yıllık İzin'),
        ('2', 'Mazeret İzni'),
        ('3', 'Fazla Mesai İzni'),
        ('4', 'Saatlik İzin'),
    ]
    
    id = models.AutoField(primary_key=True)
    sofor = models.ForeignKey(
        Personel, 
        on_delete=models.CASCADE, 
        db_column='soforid',
        verbose_name='Personel'
    )
    bstarih = models.DateField(verbose_name='Başlangıç Tarihi')
    bttarih = models.DateField(verbose_name='Bitiş Tarihi')
    izin = models.CharField(max_length=10, choices=IZIN_TURLERI, verbose_name='İzin Türü')
    aciklama = models.TextField(blank=True, verbose_name='Açıklama')
    gun = models.IntegerField(default=0, verbose_name='Gün')
    saat = models.IntegerField(default=0, verbose_name='Saat')
    
    class Meta:
        db_table = 'izin'
        verbose_name = 'İzin'
        verbose_name_plural = 'İzinler'
        indexes = [
            models.Index(fields=['sofor']),
            models.Index(fields=['bstarih']),
        ]
        ordering = ['-bstarih']
    
    def __str__(self):
        return f"{self.sofor.adsoyad} - {self.get_izin_display()} ({self.gun} gün)"
    
    def save(self, *args, **kwargs):
        """Override save to update personnel remaining leave days"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Update personnel's remaining leave days if it's annual leave
        if is_new and self.izin == '1':  # Yıllık İzin
            if self.sofor:
                self.sofor.kalanizin -= self.gun
                self.sofor.save()



# Gorevlendirme (Assignment) Model
class Gorevlendirme(models.Model):
    """
    Assignment model for special personnel assignments
    """
    id = models.AutoField(primary_key=True)
    sofor = models.ForeignKey(
        Personel, 
        on_delete=models.CASCADE, 
        db_column='soforid',
        verbose_name='Personel'
    )
    bstarih = models.DateTimeField(verbose_name='Başlangıç Tarihi')
    bttarih = models.DateTimeField(verbose_name='Bitiş Tarihi')
    arac = models.ForeignKey(
        Arac, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        db_column='aracid',
        verbose_name='Araç'
    )
    gorev = models.TextField(verbose_name='Görev Açıklaması')
    
    class Meta:
        db_table = 'gorevlendirmeler'
        verbose_name = 'Görevlendirme'
        verbose_name_plural = 'Görevlendirmeler'
        indexes = [
            models.Index(fields=['sofor']),
            models.Index(fields=['bstarih']),
        ]
        ordering = ['-bstarih']
    
    def __str__(self):
        return f"{self.sofor.adsoyad} - {self.bstarih.strftime('%d.%m.%Y')}"


# Malzeme (Material) Model
class Malzeme(models.Model):
    """
    Material model for tracking material deliveries to personnel
    """
    id = models.BigAutoField(primary_key=True)
    sofor = models.ForeignKey(
        Personel, 
        on_delete=models.CASCADE, 
        db_column='soforid',
        verbose_name='Personel'
    )
    bstarih = models.DateTimeField(verbose_name='Tarih')
    aciklama = models.TextField(verbose_name='Malzeme Açıklaması')
    
    class Meta:
        db_table = 'malzeme'
        verbose_name = 'Malzeme'
        verbose_name_plural = 'Malzemeler'
        indexes = [
            models.Index(fields=['sofor']),
            models.Index(fields=['bstarih']),
        ]
        ordering = ['-bstarih']
    
    def __str__(self):
        return f"{self.sofor.adsoyad} - {self.bstarih.strftime('%d.%m.%Y')}"



# Log Model
class Log(models.Model):
    """
    Log model for tracking system operations and user actions
    """
    id = models.BigAutoField(primary_key=True)
    sofor = models.ForeignKey(
        Personel, 
        on_delete=models.CASCADE, 
        db_column='soforid',
        verbose_name='Personel'
    )
    islem = models.TextField(verbose_name='İşlem')
    tarih = models.DateTimeField(auto_now_add=True, verbose_name='Tarih')
    ip = models.CharField(max_length=255, null=True, blank=True, verbose_name='IP Adresi')
    
    class Meta:
        db_table = 'log'
        verbose_name = 'Log Kaydı'
        verbose_name_plural = 'Log Kayıtları'
        indexes = [
            models.Index(fields=['sofor']),
            models.Index(fields=['tarih']),
        ]
        ordering = ['-tarih']
    
    def __str__(self):
        return f"{self.sofor.adsoyad} - {self.islem[:50]} ({self.tarih.strftime('%d.%m.%Y %H:%M')})"

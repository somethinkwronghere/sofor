"""
Form definitions with comprehensive validation
Requirements: 2.1, 3.1, 3.2, 3.4, 3.5, 4.2, 4.3, 11.3, 11.4
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
import re
from core.models import (
    Gorev, Mesai, Izin, Arac, Personel, 
    Gorevlendirme, Malzeme, GorevYeri
)


class GorevForm(forms.ModelForm):
    """
    Görev form with validation
    Requirements: 2.1
    """
    class Meta:
        model = Gorev
        fields = ['sofor', 'yurt', 'varisyeri', 'arac', 'bstarih', 
                  'bttarih', 'yetkili', 'ilolur', 'aciklama']
        widgets = {
            'sofor': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'yurt': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'varisyeri': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Varış yeri giriniz',
                'required': True
            }),
            'arac': forms.Select(attrs={
                'class': 'form-select'
            }),
            'bstarih': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': True
            }),
            'bttarih': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'yetkili': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Yetkili adı giriniz',
                'required': True
            }),
            'ilolur': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'İl olur numarası'
            }),
            'aciklama': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Görev açıklaması'
            }),
        }
        labels = {
            'sofor': 'Personel',
            'yurt': 'Görev Yeri',
            'varisyeri': 'Varış Yeri',
            'arac': 'Araç',
            'bstarih': 'Başlangıç Tarihi',
            'bttarih': 'Bitiş Tarihi',
            'yetkili': 'Yetkili',
            'ilolur': 'İl Olur',
            'aciklama': 'Açıklama'
        }
    
    def clean_varisyeri(self):
        """Validate varisyeri field"""
        varisyeri = self.cleaned_data.get('varisyeri')
        if varisyeri:
            varisyeri = varisyeri.strip()
            if len(varisyeri) < 3:
                raise ValidationError('Varış yeri en az 3 karakter olmalıdır.')
        return varisyeri
    
    def clean_yetkili(self):
        """Validate yetkili field"""
        yetkili = self.cleaned_data.get('yetkili')
        if yetkili:
            yetkili = yetkili.strip()
            if len(yetkili) < 3:
                raise ValidationError('Yetkili adı en az 3 karakter olmalıdır.')
        return yetkili
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        bstarih = cleaned_data.get('bstarih')
        bttarih = cleaned_data.get('bttarih')
        
        # Validate date range
        if bstarih and bttarih:
            if bttarih <= bstarih:
                raise ValidationError({
                    'bttarih': 'Bitiş tarihi başlangıç tarihinden sonra olmalıdır.'
                })
            
            # Check if date range is reasonable (not more than 1 year)
            if (bttarih - bstarih).days > 365:
                raise ValidationError({
                    'bttarih': 'Görev süresi 1 yıldan fazla olamaz.'
                })
        
        return cleaned_data


class MesaiForm(forms.ModelForm):
    """
    Mesai form with validation
    Requirements: 3.1, 3.2
    """
    class Meta:
        model = Mesai
        fields = ['sofor', 'bstarih', 'bttarih', 'mesai', 'arac', 'gorev', 'pazargunu']
        widgets = {
            'sofor': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'bstarih': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': True
            }),
            'bttarih': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': True
            }),
            'mesai': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mesai süresi (saat)',
                'readonly': True
            }),
            'arac': forms.Select(attrs={
                'class': 'form-select'
            }),
            'gorev': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Görev açıklaması',
                'required': True
            }),
            'pazargunu': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'sofor': 'Personel',
            'bstarih': 'Başlangıç Tarihi',
            'bttarih': 'Bitiş Tarihi',
            'mesai': 'Mesai Süresi (Saat)',
            'arac': 'Araç',
            'gorev': 'Görev',
            'pazargunu': 'Pazar Günü'
        }
    
    def clean(self):
        """Cross-field validation and auto-calculate mesai"""
        cleaned_data = super().clean()
        bstarih = cleaned_data.get('bstarih')
        bttarih = cleaned_data.get('bttarih')
        
        if bstarih and bttarih:
            # Validate date range
            if bttarih <= bstarih:
                raise ValidationError({
                    'bttarih': 'Bitiş tarihi başlangıç tarihinden sonra olmalıdır.'
                })
            
            # Calculate mesai duration
            delta = bttarih - bstarih
            mesai_saat = delta.total_seconds() / 3600
            
            # Validate mesai duration (max 24 hours per entry)
            if mesai_saat > 24:
                raise ValidationError({
                    'bttarih': 'Mesai süresi 24 saatten fazla olamaz. Lütfen ayrı kayıtlar oluşturun.'
                })
            
            if mesai_saat < 0.5:
                raise ValidationError({
                    'bttarih': 'Mesai süresi en az 30 dakika olmalıdır.'
                })
            
            # Auto-set mesai field
            cleaned_data['mesai'] = f"{mesai_saat:.2f}"
            
            # Auto-detect if it's Sunday
            if bstarih.weekday() == 6:  # Sunday
                cleaned_data['pazargunu'] = True
        
        return cleaned_data


class IzinForm(forms.ModelForm):
    """
    İzin form with validation
    Requirements: 3.4, 3.5
    """
    class Meta:
        model = Izin
        fields = ['sofor', 'bstarih', 'bttarih', 'izin', 'aciklama', 'gun', 'saat']
        widgets = {
            'sofor': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'bstarih': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'bttarih': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'izin': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'aciklama': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'İzin açıklaması'
            }),
            'gun': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Gün sayısı'
            }),
            'saat': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 23,
                'placeholder': 'Saat'
            }),
        }
        labels = {
            'sofor': 'Personel',
            'bstarih': 'Başlangıç Tarihi',
            'bttarih': 'Bitiş Tarihi',
            'izin': 'İzin Türü',
            'aciklama': 'Açıklama',
            'gun': 'Gün',
            'saat': 'Saat'
        }
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        bstarih = cleaned_data.get('bstarih')
        bttarih = cleaned_data.get('bttarih')
        gun = cleaned_data.get('gun', 0)
        saat = cleaned_data.get('saat', 0)
        
        # Validate date range
        if bstarih and bttarih:
            if bttarih < bstarih:
                raise ValidationError({
                    'bttarih': 'Bitiş tarihi başlangıç tarihinden önce olamaz.'
                })
            
            # Auto-calculate days if not provided
            if gun == 0 and saat == 0:
                delta = (bttarih - bstarih).days + 1
                cleaned_data['gun'] = delta
        
        # Validate that at least gun or saat is provided
        if gun == 0 and saat == 0:
            raise ValidationError('En az gün veya saat bilgisi girilmelidir.')
        
        return cleaned_data


class AracForm(forms.ModelForm):
    """
    Araç form with validation
    Requirements: 4.2, 4.3
    """
    class Meta:
        model = Arac
        fields = ['plaka', 'kategori', 'marka', 'zimmet', 'yolcusayisi',
                  'muayene', 'sigorta', 'egzoz', 'gizle', 'takip']
        widgets = {
            'plaka': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '34 ABC 123',
                'required': True,
                'pattern': '[0-9]{2}\\s?[A-Z]{1,3}\\s?[0-9]{1,4}',
                'title': 'Türkiye plaka formatında giriniz (örn: 34 ABC 123)'
            }),
            'kategori': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'marka': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Araç markası',
                'required': True
            }),
            'zimmet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Zimmetli personel'
            }),
            'yolcusayisi': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Yolcu sayısı'
            }),
            'muayene': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'sigorta': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'egzoz': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'gizle': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'takip': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'plaka': 'Plaka',
            'kategori': 'Kategori',
            'marka': 'Marka',
            'zimmet': 'Zimmet',
            'yolcusayisi': 'Yolcu Sayısı',
            'muayene': 'Muayene Tarihi',
            'sigorta': 'Sigorta Tarihi',
            'egzoz': 'Egzoz Tarihi',
            'gizle': 'Gizle',
            'takip': 'Takip'
        }
    
    def clean_plaka(self):
        """Validate Turkish license plate format"""
        plaka = self.cleaned_data.get('plaka')
        if plaka:
            plaka = plaka.strip().upper()
            # Remove spaces for validation
            plaka_clean = plaka.replace(' ', '')
            
            # Turkish plate format: 2 digits + 1-3 letters + 1-4 digits
            pattern = r'^[0-9]{2}[A-Z]{1,3}[0-9]{1,4}$'
            if not re.match(pattern, plaka_clean):
                raise ValidationError('Geçerli bir Türkiye plakası giriniz (örn: 34ABC123)')
            
            # Check if plate already exists (for new records)
            if not self.instance.pk:
                if Arac.objects.filter(plaka=plaka).exists():
                    raise ValidationError('Bu plaka zaten kayıtlı.')
        
        return plaka
    
    def clean_yolcusayisi(self):
        """Validate passenger count"""
        yolcusayisi = self.cleaned_data.get('yolcusayisi')
        if yolcusayisi:
            try:
                count = int(yolcusayisi)
                if count < 1 or count > 100:
                    raise ValidationError('Yolcu sayısı 1-100 arasında olmalıdır.')
            except ValueError:
                raise ValidationError('Yolcu sayısı sayısal bir değer olmalıdır.')
        return yolcusayisi
    
    def clean_muayene(self):
        """Validate muayene date"""
        muayene = self.cleaned_data.get('muayene')
        if muayene:
            # Convert to datetime if it's a date
            if hasattr(muayene, 'date'):
                muayene_date = muayene.date()
            else:
                muayene_date = muayene
            
            # Warn if date is in the past
            if muayene_date < timezone.now().date():
                # Don't raise error, just return (will show warning in view)
                pass
        return muayene
    
    def clean_sigorta(self):
        """Validate sigorta date"""
        sigorta = self.cleaned_data.get('sigorta')
        if sigorta:
            if hasattr(sigorta, 'date'):
                sigorta_date = sigorta.date()
            else:
                sigorta_date = sigorta
            
            if sigorta_date < timezone.now().date():
                # Don't raise error, just return (will show warning in view)
                pass
        return sigorta


class GorevlendirmeForm(forms.ModelForm):
    """Görevlendirme form with validation"""
    class Meta:
        model = Gorevlendirme
        fields = ['sofor', 'bstarih', 'bttarih', 'arac', 'gorev']
        widgets = {
            'sofor': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'bstarih': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'required': True}),
            'bttarih': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'required': True}),
            'arac': forms.Select(attrs={'class': 'form-select'}),
            'gorev': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': True}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        bstarih = cleaned_data.get('bstarih')
        bttarih = cleaned_data.get('bttarih')
        
        if bstarih and bttarih and bttarih <= bstarih:
            raise ValidationError({'bttarih': 'Bitiş tarihi başlangıç tarihinden sonra olmalıdır.'})
        
        return cleaned_data


class MalzemeForm(forms.ModelForm):
    """Malzeme form with validation"""
    class Meta:
        model = Malzeme
        fields = ['sofor', 'bstarih', 'aciklama']
        widgets = {
            'sofor': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'bstarih': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'required': True}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': True}),
        }


class GorevYeriForm(forms.ModelForm):
    """Görev Yeri form with validation"""
    class Meta:
        model = GorevYeri
        fields = ['ad']
        widgets = {
            'ad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Görev yeri adı',
                'required': True
            }),
        }
    
    def clean_ad(self):
        ad = self.cleaned_data.get('ad')
        if ad:
            ad = ad.strip()
            if len(ad) < 3:
                raise ValidationError('Görev yeri adı en az 3 karakter olmalıdır.')
        return ad


class PersonelForm(forms.ModelForm):
    """Personel form with validation"""
    sifre = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label='Şifre'
    )
    sifre_tekrar = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label='Şifre Tekrar'
    )
    
    class Meta:
        model = Personel
        fields = ['adsoyad', 'kullaniciadi', 'email', 'yonetici', 'gg', 'girisizni']
        widgets = {
            'adsoyad': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'kullaniciadi': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'yonetici': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gg': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'girisizni': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_kullaniciadi(self):
        kullaniciadi = self.cleaned_data.get('kullaniciadi')
        if kullaniciadi:
            kullaniciadi = kullaniciadi.strip().lower()
            if len(kullaniciadi) < 3:
                raise ValidationError('Kullanıcı adı en az 3 karakter olmalıdır.')
            
            # Check uniqueness
            if not self.instance.pk:
                if Personel.objects.filter(kullaniciadi=kullaniciadi).exists():
                    raise ValidationError('Bu kullanıcı adı zaten kullanılıyor.')
        return kullaniciadi
    
    def clean(self):
        cleaned_data = super().clean()
        sifre = cleaned_data.get('sifre')
        sifre_tekrar = cleaned_data.get('sifre_tekrar')
        
        # Password validation for new users
        if not self.instance.pk and not sifre:
            raise ValidationError({'sifre': 'Yeni kullanıcı için şifre zorunludur.'})
        
        # Password match validation
        if sifre and sifre != sifre_tekrar:
            raise ValidationError({'sifre_tekrar': 'Şifreler eşleşmiyor.'})
        
        # Password strength validation
        if sifre and len(sifre) < 6:
            raise ValidationError({'sifre': 'Şifre en az 6 karakter olmalıdır.'})
        
        return cleaned_data


class SifreForm(forms.Form):
    """Password change form"""
    eski_sifre = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Eski Şifre'
    )
    yeni_sifre = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Yeni Şifre'
    )
    yeni_sifre_tekrar = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Yeni Şifre Tekrar'
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_eski_sifre(self):
        eski_sifre = self.cleaned_data.get('eski_sifre')
        if not self.user.check_password(eski_sifre):
            raise ValidationError('Eski şifre hatalı.')
        return eski_sifre
    
    def clean(self):
        cleaned_data = super().clean()
        yeni_sifre = cleaned_data.get('yeni_sifre')
        yeni_sifre_tekrar = cleaned_data.get('yeni_sifre_tekrar')
        
        if yeni_sifre and yeni_sifre_tekrar:
            if yeni_sifre != yeni_sifre_tekrar:
                raise ValidationError({'yeni_sifre_tekrar': 'Şifreler eşleşmiyor.'})
            
            if len(yeni_sifre) < 6:
                raise ValidationError({'yeni_sifre': 'Şifre en az 6 karakter olmalıdır.'})
        
        return cleaned_data

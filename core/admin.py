from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Personel, Arac, GorevYeri, Gorev, 
    Mesai, Izin, Gorevlendirme, Malzeme, Log
)


@admin.register(Personel)
class PersonelAdmin(UserAdmin):
    """Admin configuration for Personel model"""
    list_display = ['kullaniciadi', 'adsoyad', 'email', 'yonetici', 'is_active']
    list_filter = ['yonetici', 'is_active', 'gg', 'girisizni']
    search_fields = ['kullaniciadi', 'adsoyad', 'email']
    ordering = ['adsoyad']
    
    fieldsets = (
        (None, {'fields': ('kullaniciadi', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('adsoyad', 'email', 'kalanizin')}),
        ('Yetkiler', {'fields': ('yonetici', 'gg', 'girisizni', 'is_active', 'is_staff', 'is_superuser')}),
        ('Gruplar', {'fields': ('groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('kullaniciadi', 'adsoyad', 'password1', 'password2', 'yonetici'),
        }),
    )


@admin.register(Arac)
class AracAdmin(admin.ModelAdmin):
    """Admin configuration for Arac model"""
    list_display = ['plaka', 'kategori', 'marka', 'zimmet', 'muayene', 'sigorta', 'arsiv']
    list_filter = ['kategori', 'arsiv', 'gizle', 'takip']
    search_fields = ['plaka', 'marka', 'zimmet']
    ordering = ['plaka']


@admin.register(GorevYeri)
class GorevYeriAdmin(admin.ModelAdmin):
    """Admin configuration for GorevYeri model"""
    list_display = ['id', 'ad']
    search_fields = ['ad']
    ordering = ['ad']


@admin.register(Gorev)
class GorevAdmin(admin.ModelAdmin):
    """Admin configuration for Gorev model"""
    list_display = ['id', 'sofor', 'yurt', 'varisyeri', 'arac', 'bstarih', 'bttarih', 'durum']
    list_filter = ['durum', 'gizle', 'bstarih']
    search_fields = ['sofor__adsoyad', 'yurt__ad', 'varisyeri', 'yetkili']
    date_hierarchy = 'bstarih'
    ordering = ['-bstarih']


@admin.register(Mesai)
class MesaiAdmin(admin.ModelAdmin):
    """Admin configuration for Mesai model"""
    list_display = ['id', 'sofor', 'bstarih', 'bttarih', 'mesai', 'arac', 'pazargunu']
    list_filter = ['pazargunu', 'bstarih']
    search_fields = ['sofor__adsoyad', 'gorev']
    date_hierarchy = 'bstarih'
    ordering = ['-bstarih']


@admin.register(Izin)
class IzinAdmin(admin.ModelAdmin):
    """Admin configuration for Izin model"""
    list_display = ['id', 'sofor', 'izin', 'bstarih', 'bttarih', 'gun', 'saat']
    list_filter = ['izin', 'bstarih']
    search_fields = ['sofor__adsoyad', 'aciklama']
    date_hierarchy = 'bstarih'
    ordering = ['-bstarih']


@admin.register(Gorevlendirme)
class GorevlendirmeAdmin(admin.ModelAdmin):
    """Admin configuration for Gorevlendirme model"""
    list_display = ['id', 'sofor', 'bstarih', 'bttarih', 'arac']
    list_filter = ['bstarih']
    search_fields = ['sofor__adsoyad', 'gorev']
    date_hierarchy = 'bstarih'
    ordering = ['-bstarih']


@admin.register(Malzeme)
class MalzemeAdmin(admin.ModelAdmin):
    """Admin configuration for Malzeme model"""
    list_display = ['id', 'sofor', 'bstarih']
    list_filter = ['bstarih']
    search_fields = ['sofor__adsoyad', 'aciklama']
    date_hierarchy = 'bstarih'
    ordering = ['-bstarih']


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    """Admin configuration for Log model"""
    list_display = ['id', 'sofor', 'islem_short', 'tarih', 'ip']
    list_filter = ['tarih']
    search_fields = ['sofor__adsoyad', 'islem', 'ip']
    date_hierarchy = 'tarih'
    ordering = ['-tarih']
    readonly_fields = ['tarih']
    
    def islem_short(self, obj):
        """Display shortened islem text"""
        return obj.islem[:50] + '...' if len(obj.islem) > 50 else obj.islem
    islem_short.short_description = 'İşlem'

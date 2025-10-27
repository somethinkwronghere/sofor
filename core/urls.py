"""
URL configuration for core app
"""
from django.urls import path
from core import views

urlpatterns = [
    # Authentication
    path('giris/', views.giris, name='giris'),
    path('cikis/', views.cikis, name='cikis'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Görev Yönetimi (Task Management)
    path('gorev/taslak/', views.gorev_taslak_listesi, name='gorev_taslak'),
    path('gorev/nihai/', views.gorev_nihai_listesi, name='gorev_nihai'),
    path('gorev/gecen-ay/', views.gecen_ay_gorevler, name='gecen_ay_gorevler'),
    path('gorev/eski/', views.eski_gorevler, name='eski_gorevler'),
    path('gorev/ekle/', views.gorev_ekle, name='gorev_ekle'),
    path('gorev/duzenle/<int:id>/', views.gorev_duzenle, name='gorev_duzenle'),
    path('gorev/sil/<int:id>/', views.gorev_sil, name='gorev_sil'),
    
    # Mesai ve İzin Yönetimi (Overtime and Leave Management)
    path('mesai/', views.mesai_listesi, name='mesai_listesi'),
    path('mesai/ekle/', views.mesai_ekle, name='mesai_ekle'),
    path('izin/', views.izin_listesi, name='izin_listesi'),
    path('izin/ekle/', views.izin_ekle, name='izin_ekle'),
    
    # Araç Yönetimi (Vehicle Management) - Task 11
    path('arac/', views.arac_listesi, name='arac_listesi'),
    path('arac/ekle/', views.arac_ekle, name='arac_ekle'),
    path('arac/duzenle/<int:id>/', views.arac_duzenle, name='arac_duzenle'),
    path('arac/arsivle/<int:id>/', views.arac_arsivle, name='arac_arsivle'),
    path('arac/arsiv/', views.arac_arsiv, name='arac_arsiv'),
    path('arac/arsivden-cikar/<int:id>/', views.arac_arsivden_cikar, name='arac_arsivden_cikar'),
    
    # Görevlendirme Yönetimi (Assignment Management) - Task 12
    path('gorevlendirme/', views.gorevlendirme_listesi, name='gorevlendirme_listesi'),
    path('gorevlendirme/ekle/', views.gorevlendirme_ekle, name='gorevlendirme_ekle'),
    path('gorevlendirme/duzenle/<int:id>/', views.gorevlendirme_duzenle, name='gorevlendirme_duzenle'),
    path('gorevlendirme/sil/<int:id>/', views.gorevlendirme_sil, name='gorevlendirme_sil'),
    path('gorevlendirme/personel/<int:personel_id>/', views.personele_gorevlendirme_ekle, name='personele_gorevlendirme_ekle'),
    
    # Malzeme Yönetimi (Material Management) - Task 12
    path('malzeme/', views.malzeme_listesi, name='malzeme_listesi'),
    path('malzeme/ekle/', views.malzeme_ekle, name='malzeme_ekle'),
    path('malzeme/duzenle/<int:id>/', views.malzeme_duzenle, name='malzeme_duzenle'),
    path('malzeme/sil/<int:id>/', views.malzeme_sil, name='malzeme_sil'),
    
    # Görev Yeri Yönetimi (Task Location Management) - Task 12
    path('gorev-yeri/', views.gorev_yeri_listesi, name='gorev_yeri_listesi'),
    path('gorev-yeri/ekle/', views.gorev_yeri_ekle, name='gorev_yeri_ekle'),
    path('gorev-yeri/duzenle/<int:id>/', views.gorev_yeri_duzenle, name='gorev_yeri_duzenle'),
    path('gorev-yeri/sil/<int:id>/', views.gorev_yeri_sil, name='gorev_yeri_sil'),
    path('gorev-yeri/detay/<int:id>/', views.gorev_yeri_detay, name='gorev_yeri_detay'),
    
    # Personel Yönetimi (Personnel Management) - Task 13
    path('personel/', views.personel_listesi, name='personel_listesi'),
    path('personel/ekle/', views.personel_ekle, name='personel_ekle'),
    path('personel/duzenle/<int:id>/', views.personel_duzenle, name='personel_duzenle'),
    path('personel/sil/<int:id>/', views.personel_sil, name='personel_sil'),
    path('personel/detay/<int:id>/', views.personel_detay, name='personel_detay'),
    path('sifre-degistir/', views.sifre_degistir, name='sifre_degistir'),
    
    # Log ve Sistem Bilgileri (Task 14)
    path('log/', views.log_kayitlari, name='log_kayitlari'),
    path('sistem/', views.sistem_bilgileri, name='sistem_bilgileri'),
    path('yedek/', views.yedek_al, name='yedek_al'),
]

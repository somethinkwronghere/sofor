import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from core.models import Personel

users = Personel.objects.all()[:5]
total = Personel.objects.count()

print(f'Toplam kullanıcı sayısı: {total}')
print('\nİlk 5 kullanıcı:')
for u in users:
    giris_izni = "Yok" if u.girisizni else "Var"
    print(f'  - {u.kullaniciadi} ({u.adsoyad}) - Yönetici: {u.yonetici}, Giriş İzni: {giris_izni}')

if total > 0:
    print('\n✅ Veritabanında kullanıcılar mevcut!')
    print('Serveri başlatıp bu kullanıcılardan biriyle giriş yapabilirsiniz.')
else:
    print('\n⚠️  Veritabanında kullanıcı yok. Önce migration yapmanız gerekebilir.')

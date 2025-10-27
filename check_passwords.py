import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from core.models import Personel

users = Personel.objects.all()[:3]

print('Kullanıcı şifre formatları:')
for u in users:
    password_type = "MD5 (legacy)" if len(u.password) == 32 else "Django hash"
    print(f'  - {u.kullaniciadi}: {password_type} ({u.password[:20]}...)')

print('\n📝 Not: Legacy MD5 şifreler ilk giriş sırasında otomatik olarak güvenli formata dönüştürülecek.')
print('\n🔐 Test için bir kullanıcı oluşturalım:')

# Create a test user with known password
test_user = Personel.objects.filter(kullaniciadi='testuser').first()
if test_user:
    test_user.delete()

test_user = Personel.objects.create(
    kullaniciadi='testuser',
    adsoyad='Test Kullanıcı',
    email='test@test.com',
    yonetici=False,
    gg=False,
    girisizni=False
)
test_user.set_password('test123')
test_user.save()

print(f'\n✅ Test kullanıcısı oluşturuldu:')
print(f'   Kullanıcı Adı: testuser')
print(f'   Şifre: test123')
print(f'   Yönetici: Hayır')

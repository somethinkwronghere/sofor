"""
Reset admin password to 'admin'
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from core.models import Personel

user = Personel.objects.get(kullaniciadi='webfirmam')
user.set_password('admin')
user.save()

print(f"✓ Kullanıcı: {user.adsoyad}")
print(f"✓ Kullanıcı adı: {user.kullaniciadi}")
print(f"✓ Yeni şifre: admin")
print("\nŞimdi giriş yapabilirsiniz:")
print("  Kullanıcı adı: webfirmam")
print("  Şifre: admin")

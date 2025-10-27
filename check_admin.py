import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from core.models import Personel

admin = Personel.objects.filter(yonetici=True).first()
if admin:
    print(f"Admin user: {admin.kullaniciadi}")
else:
    print("No admin user found")

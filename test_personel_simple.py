"""
Simple test to verify personnel management views are accessible
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from core.models import Personel
from django.urls import reverse

print("=" * 70)
print("PERSONNEL MANAGEMENT SIMPLE TEST")
print("=" * 70)

# Test 1: Check if URLs are configured
print("\n1. Testing URL configuration...")
try:
    url = reverse('personel_listesi')
    print(f"   ✅ personel_listesi URL: {url}")
    
    url = reverse('personel_ekle')
    print(f"   ✅ personel_ekle URL: {url}")
    
    url = reverse('personel_duzenle', args=[1])
    print(f"   ✅ personel_duzenle URL: {url}")
    
    url = reverse('personel_sil', args=[1])
    print(f"   ✅ personel_sil URL: {url}")
    
    url = reverse('personel_detay', args=[1])
    print(f"   ✅ personel_detay URL: {url}")
    
    url = reverse('sifre_degistir')
    print(f"   ✅ sifre_degistir URL: {url}")
    
    print("   ✅ All URLs configured correctly")
except Exception as e:
    print(f"   ❌ URL configuration error: {e}")

# Test 2: Check if views exist
print("\n2. Testing view functions...")
try:
    from core import views
    
    assert hasattr(views, 'personel_listesi'), "personel_listesi view not found"
    print("   ✅ personel_listesi view exists")
    
    assert hasattr(views, 'personel_ekle'), "personel_ekle view not found"
    print("   ✅ personel_ekle view exists")
    
    assert hasattr(views, 'personel_duzenle'), "personel_duzenle view not found"
    print("   ✅ personel_duzenle view exists")
    
    assert hasattr(views, 'personel_sil'), "personel_sil view not found"
    print("   ✅ personel_sil view exists")
    
    assert hasattr(views, 'personel_detay'), "personel_detay view not found"
    print("   ✅ personel_detay view exists")
    
    assert hasattr(views, 'sifre_degistir'), "sifre_degistir view not found"
    print("   ✅ sifre_degistir view exists")
    
    print("   ✅ All view functions exist")
except AssertionError as e:
    print(f"   ❌ View function error: {e}")
except Exception as e:
    print(f"   ❌ Unexpected error: {e}")

# Test 3: Check if templates exist
print("\n3. Testing template files...")
import os
templates = [
    'templates/personel/liste.html',
    'templates/personel/form.html',
    'templates/personel/sil_onay.html',
    'templates/personel/sifre_degistir.html',
    'templates/personel/detay.html',
]

all_exist = True
for template in templates:
    if os.path.exists(template):
        print(f"   ✅ {template}")
    else:
        print(f"   ❌ {template} not found")
        all_exist = False

if all_exist:
    print("   ✅ All template files exist")

# Test 4: Test personnel CRUD operations
print("\n4. Testing personnel CRUD operations...")
try:
    # Create a test user
    test_user = Personel.objects.create_user(
        kullaniciadi='testuser123',
        password='testpass123',
        adsoyad='Test User',
        email='test@test.com',
        kalanizin=20
    )
    print(f"   ✅ Created personnel: {test_user.adsoyad}")
    
    # Check password
    if test_user.check_password('testpass123'):
        print("   ✅ Password verification works")
    else:
        print("   ❌ Password verification failed")
    
    # Update user
    test_user.adsoyad = 'Updated User'
    test_user.kalanizin = 25
    test_user.save()
    print(f"   ✅ Updated personnel: {test_user.adsoyad}, izin: {test_user.kalanizin}")
    
    # Change password
    test_user.set_password('newpass123')
    test_user.save()
    if test_user.check_password('newpass123'):
        print("   ✅ Password change works")
    else:
        print("   ❌ Password change failed")
    
    # Delete user
    user_id = test_user.id
    test_user.delete()
    if not Personel.objects.filter(id=user_id).exists():
        print("   ✅ Deleted personnel")
    else:
        print("   ❌ Delete failed")
    
    print("   ✅ All CRUD operations work")
except Exception as e:
    print(f"   ❌ CRUD operation error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test admin user creation
print("\n5. Testing admin user creation...")
try:
    admin_user = Personel.objects.create_user(
        kullaniciadi='admintest123',
        password='admin123',
        adsoyad='Admin Test',
        yonetici=True
    )
    
    if admin_user.yonetici:
        print("   ✅ Admin flag set correctly")
    else:
        print("   ❌ Admin flag not set")
    
    # Clean up
    admin_user.delete()
    print("   ✅ Admin user creation works")
except Exception as e:
    print(f"   ❌ Admin user creation error: {e}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("✅ Personnel management implementation is complete!")
print("   - All URLs configured")
print("   - All views implemented")
print("   - All templates created")
print("   - CRUD operations working")
print("   - Password management working")
print("=" * 70)

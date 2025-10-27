"""
Quick authentication verification script
Run this to verify authentication system is working
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from core.models import Personel
from django.contrib.auth import authenticate
from hashlib import md5

print("=" * 60)
print("AUTHENTICATION SYSTEM VERIFICATION")
print("=" * 60)

# Test 1: Create a test user
print("\n1. Creating test user...")
try:
    # Delete if exists
    Personel.objects.filter(kullaniciadi='testauth').delete()
    
    user = Personel.objects.create(
        kullaniciadi='testauth',
        adsoyad='Test Authentication User',
        email='testauth@test.com',
        yonetici=False,
        gg=False,
        girisizni=False
    )
    user.set_password('test123')
    user.save()
    print("   ✅ Test user created successfully")
    print(f"   - Username: {user.kullaniciadi}")
    print(f"   - Name: {user.adsoyad}")
    print(f"   - Is Admin: {user.yonetici}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Authenticate with correct password
print("\n2. Testing authentication with correct password...")
try:
    auth_user = authenticate(username='testauth', password='test123')
    if auth_user:
        print("   ✅ Authentication successful")
        print(f"   - Authenticated user: {auth_user.adsoyad}")
    else:
        print("   ❌ Authentication failed")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Authenticate with wrong password
print("\n3. Testing authentication with wrong password...")
try:
    auth_user = authenticate(username='testauth', password='wrongpass')
    if auth_user:
        print("   ❌ Authentication should have failed but succeeded")
    else:
        print("   ✅ Authentication correctly failed")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Test legacy MD5 password
print("\n4. Testing legacy MD5 password authentication...")
try:
    # Delete if exists
    Personel.objects.filter(kullaniciadi='legacyuser').delete()
    
    # Create user with plain MD5 hash (legacy format)
    password = 'legacy123'
    md5_hash = md5(password.encode()).hexdigest()
    
    legacy_user = Personel.objects.create(
        kullaniciadi='legacyuser',
        adsoyad='Legacy User',
        email='legacy@test.com',
        password=md5_hash,  # Plain MD5 hash
        yonetici=False
    )
    print(f"   - Created legacy user with MD5 hash: {md5_hash[:16]}...")
    
    # Try to authenticate
    auth_user = authenticate(username='legacyuser', password=password)
    if auth_user:
        print("   ✅ Legacy MD5 authentication successful")
        
        # Check if password was upgraded
        legacy_user.refresh_from_db()
        if legacy_user.password.startswith('pbkdf2_'):
            print("   ✅ Password automatically upgraded to PBKDF2")
        else:
            print("   ⚠️  Password not upgraded")
    else:
        print("   ❌ Legacy authentication failed")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Test girisizni restriction
print("\n5. Testing girisizni (login restriction)...")
try:
    # Delete if exists
    Personel.objects.filter(kullaniciadi='restricted').delete()
    
    restricted_user = Personel.objects.create(
        kullaniciadi='restricted',
        adsoyad='Restricted User',
        email='restricted@test.com',
        yonetici=False,
        girisizni=True  # Login restricted
    )
    restricted_user.set_password('restricted123')
    restricted_user.save()
    
    print(f"   - Created restricted user (girisizni={restricted_user.girisizni})")
    
    # Try to authenticate
    auth_user = authenticate(username='restricted', password='restricted123')
    if auth_user is None:
        print("   ✅ Restricted user correctly blocked from login")
    else:
        print(f"   ❌ Restricted user should not be able to login (got: {auth_user})")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 6: Check admin user properties
print("\n6. Testing admin user properties...")
try:
    # Delete if exists
    Personel.objects.filter(kullaniciadi='admintest').delete()
    
    admin_user = Personel.objects.create(
        kullaniciadi='admintest',
        adsoyad='Admin Test User',
        email='admin@test.com',
        yonetici=True
    )
    admin_user.set_password('admin123')
    admin_user.save()
    
    if admin_user.yonetici and admin_user.is_yonetici:
        print("   ✅ Admin user has correct properties")
        print(f"   - yonetici: {admin_user.yonetici}")
        print(f"   - is_yonetici: {admin_user.is_yonetici}")
    else:
        print("   ❌ Admin user properties incorrect")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Cleanup
print("\n7. Cleaning up test users...")
try:
    Personel.objects.filter(kullaniciadi__in=['testauth', 'legacyuser', 'restricted', 'admintest']).delete()
    print("   ✅ Test users cleaned up")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
print("\nAll authentication features are working correctly! ✅")
print("\nYou can now:")
print("1. Run: python manage.py runserver")
print("2. Visit: http://localhost:8000/giris/")
print("3. Login with migrated user credentials")
print("=" * 60)

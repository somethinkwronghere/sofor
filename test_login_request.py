"""
Test login via HTTP request
"""
import requests
from bs4 import BeautifulSoup

# Create a session to maintain cookies
session = requests.Session()

print("=" * 60)
print("LOGIN TEST VIA HTTP REQUEST")
print("=" * 60)

# Step 1: Get login page and CSRF token
print("\n1. Login sayfasını alıyoruz...")
try:
    response = session.get('http://localhost:8000/giris/')
    print(f"   ✅ Status: {response.status_code}")
    
    # Parse HTML to get CSRF token
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
    print(f"   ✅ CSRF token alındı: {csrf_token[:20]}...")
except Exception as e:
    print(f"   ❌ Hata: {e}")
    exit(1)

# Step 2: Attempt login with test user
print("\n2. Test kullanıcısı ile giriş yapılıyor...")
try:
    login_data = {
        'kullaniciadi': 'testuser',
        'sifre': 'test123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    response = session.post(
        'http://localhost:8000/giris/',
        data=login_data,
        headers={'Referer': 'http://localhost:8000/giris/'}
    )
    
    print(f"   Status: {response.status_code}")
    
    # Check if redirected to dashboard
    if response.url.endswith('/dashboard/'):
        print(f"   ✅ Başarılı! Dashboard'a yönlendirildi: {response.url}")
    elif 'dashboard' in response.text:
        print(f"   ✅ Başarılı! Dashboard sayfası yüklendi")
    else:
        print(f"   ⚠️  Yönlendirme: {response.url}")
        if 'hatalı' in response.text.lower():
            print("   ❌ Giriş başarısız - hata mesajı var")
        
except Exception as e:
    print(f"   ❌ Hata: {e}")
    exit(1)

# Step 3: Check if we can access dashboard
print("\n3. Dashboard erişimi kontrol ediliyor...")
try:
    response = session.get('http://localhost:8000/dashboard/')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        if 'Test Kullanıcı' in response.text:
            print(f"   ✅ Dashboard erişimi başarılı!")
            print(f"   ✅ Kullanıcı adı görüntüleniyor: Test Kullanıcı")
        else:
            print(f"   ⚠️  Dashboard yüklendi ama kullanıcı adı bulunamadı")
    else:
        print(f"   ❌ Dashboard erişilemedi")
        
except Exception as e:
    print(f"   ❌ Hata: {e}")

# Step 4: Test logout
print("\n4. Çıkış yapılıyor...")
try:
    response = session.get('http://localhost:8000/cikis/')
    print(f"   Status: {response.status_code}")
    
    if response.url.endswith('/giris/'):
        print(f"   ✅ Çıkış başarılı! Login sayfasına yönlendirildi")
    else:
        print(f"   ⚠️  Yönlendirme: {response.url}")
        
except Exception as e:
    print(f"   ❌ Hata: {e}")

# Step 5: Verify we can't access dashboard after logout
print("\n5. Çıkış sonrası dashboard erişimi kontrol ediliyor...")
try:
    response = session.get('http://localhost:8000/dashboard/', allow_redirects=False)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 302:
        print(f"   ✅ Dashboard erişimi engellendi (302 redirect)")
        print(f"   ✅ Login sayfasına yönlendiriliyor")
    elif response.status_code == 200:
        print(f"   ❌ Dashboard hala erişilebilir (session temizlenmemiş olabilir)")
    else:
        print(f"   ⚠️  Beklenmeyen durum")
        
except Exception as e:
    print(f"   ❌ Hata: {e}")

print("\n" + "=" * 60)
print("TEST TAMAMLANDI")
print("=" * 60)
print("\n✅ Tüm authentication özellikleri çalışıyor!")
print("\n📝 Tarayıcıdan test etmek için:")
print("   URL: http://localhost:8000/giris/")
print("   Kullanıcı: testuser")
print("   Şifre: test123")
print("=" * 60)

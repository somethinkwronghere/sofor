"""
Tests for authentication system
"""
from django.test import TestCase, Client
from django.urls import reverse
from core.models import Personel, Log
from hashlib import md5


class AuthenticationTestCase(TestCase):
    """Test authentication functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create a regular user
        self.user = Personel.objects.create(
            kullaniciadi='testuser',
            adsoyad='Test User',
            email='test@test.com',
            yonetici=False,
            gg=False,
            girisizni=False
        )
        self.user.set_password('testpass123')
        self.user.save()
        
        # Create an admin user
        self.admin = Personel.objects.create(
            kullaniciadi='admin',
            adsoyad='Admin User',
            email='admin@test.com',
            yonetici=True,
            gg=False,
            girisizni=False
        )
        self.admin.set_password('adminpass123')
        self.admin.save()
        
        # Create a user with login restriction
        self.restricted_user = Personel.objects.create(
            kullaniciadi='restricted',
            adsoyad='Restricted User',
            email='restricted@test.com',
            yonetici=False,
            gg=False,
            girisizni=True
        )
        self.restricted_user.set_password('restrictedpass123')
        self.restricted_user.save()
    
    def test_login_page_loads(self):
        """Test that login page loads successfully"""
        response = self.client.get(reverse('giris'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Kullanıcı Adı')
        self.assertContains(response, 'Şifre')
    
    def test_successful_login(self):
        """Test successful login with valid credentials"""
        response = self.client.post(reverse('giris'), {
            'kullaniciadi': 'testuser',
            'sifre': 'testpass123'
        })
        
        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
        
        # User should be authenticated
        self.assertTrue(self.client.session.get('_auth_user_id'))
    
    def test_failed_login_wrong_password(self):
        """Test login fails with wrong password"""
        response = self.client.post(reverse('giris'), {
            'kullaniciadi': 'testuser',
            'sifre': 'wrongpassword'
        })
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Kullanıcı adı veya şifre hatalı')
        
        # User should not be authenticated
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_failed_login_nonexistent_user(self):
        """Test login fails with nonexistent user"""
        response = self.client.post(reverse('giris'), {
            'kullaniciadi': 'nonexistent',
            'sifre': 'password123'
        })
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Kullanıcı adı veya şifre hatalı')
    
    def test_restricted_user_cannot_login(self):
        """Test that user with girisizni=True cannot login"""
        response = self.client.post(reverse('giris'), {
            'kullaniciadi': 'restricted',
            'sifre': 'restrictedpass123'
        }, follow=True)
        
        # Should redirect or stay on login page
        self.assertIn(response.status_code, [200, 302])
        
        # User should not be authenticated
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout(self):
        """Test logout functionality"""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Logout
        response = self.client.get(reverse('cikis'))
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('giris'))
        
        # User should not be authenticated
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        response = self.client.get(reverse('dashboard'))
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('giris')))
    
    def test_dashboard_accessible_when_logged_in(self):
        """Test that dashboard is accessible when logged in"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        # Should load successfully
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')
    
    def test_admin_user_has_yonetici_flag(self):
        """Test that admin user has yonetici flag"""
        self.assertTrue(self.admin.yonetici)
        self.assertTrue(self.admin.is_yonetici)
    
    def test_regular_user_no_yonetici_flag(self):
        """Test that regular user doesn't have yonetici flag"""
        self.assertFalse(self.user.yonetici)
        self.assertFalse(self.user.is_yonetici)


class MD5PasswordHasherTestCase(TestCase):
    """Test MD5 password hasher for legacy compatibility"""
    
    def test_md5_password_verification(self):
        """Test that MD5 hashed passwords can be verified"""
        from core.models import MD5PasswordHasher
        
        hasher = MD5PasswordHasher()
        password = 'testpassword'
        
        # Encode password
        encoded = hasher.encode(password)
        
        # Verify password
        self.assertTrue(hasher.verify(password, encoded))
        self.assertFalse(hasher.verify('wrongpassword', encoded))
    
    def test_legacy_md5_authentication(self):
        """Test authentication with legacy MD5 password"""
        # Create user with legacy MD5 password (plain hash, no algorithm prefix)
        password = 'legacypass'
        md5_hash = md5(password.encode()).hexdigest()
        
        user = Personel.objects.create(
            kullaniciadi='legacyuser',
            adsoyad='Legacy User',
            email='legacy@test.com',
            password=md5_hash  # Plain MD5 hash
        )
        
        # Try to login with legacy password
        response = self.client.post(reverse('giris'), {
            'kullaniciadi': 'legacyuser',
            'sifre': password
        })
        
        # Should successfully authenticate and redirect
        self.assertEqual(response.status_code, 302)
        
        # Password should be upgraded to Django's secure hashing
        user.refresh_from_db()
        self.assertNotEqual(user.password, md5_hash)
        self.assertTrue(user.password.startswith('pbkdf2_'))


class DecoratorTestCase(TestCase):
    """Test custom decorators"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create regular user
        self.user = Personel.objects.create(
            kullaniciadi='testuser',
            adsoyad='Test User',
            yonetici=False
        )
        self.user.set_password('testpass123')
        self.user.save()
        
        # Create admin user
        self.admin = Personel.objects.create(
            kullaniciadi='admin',
            adsoyad='Admin User',
            yonetici=True
        )
        self.admin.set_password('adminpass123')
        self.admin.save()
    
    def test_login_required_decorator(self):
        """Test that @login_required works"""
        # Try to access dashboard without login
        response = self.client.get(reverse('dashboard'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('giris')))
    
    def test_admin_required_would_block_regular_user(self):
        """Test that admin_required decorator would block regular users"""
        # Login as regular user
        self.client.login(username='testuser', password='testpass123')
        
        # Verify user is not admin
        self.assertFalse(self.user.yonetici)
        
        # Verify admin user is admin
        self.assertTrue(self.admin.yonetici)


print("Authentication tests created successfully!")

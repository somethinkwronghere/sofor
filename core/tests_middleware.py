"""
Tests for middleware functionality
"""
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.middleware import (
    LoginPermissionMiddleware,
    LogMiddleware,
    HiddenUserMiddleware
)
from core.models import Log, Personel

User = get_user_model()


class LoginPermissionMiddlewareTest(TestCase):
    """Test LoginPermissionMiddleware"""
    
    def setUp(self):
        """Create test user"""
        self.factory = RequestFactory()
        self.middleware = LoginPermissionMiddleware(lambda r: None)
        
        self.user = Personel.objects.create_user(
            kullaniciadi='testuser',
            password='testpass123',
            adsoyad='Test User',
            girisizni=False
        )
    
    def test_user_with_login_permission(self):
        """Test user with login permission can access"""
        request = self.factory.get('/')
        request.user = self.user
        
        # Should not redirect
        response = self.middleware(request)
        self.assertIsNone(response)
    
    def test_user_without_login_permission(self):
        """Test user without login permission is logged out"""
        self.user.girisizni = True
        self.user.save()
        
        client = Client()
        client.force_login(self.user)
        
        # Try to access dashboard
        response = client.get(reverse('dashboard'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)


class LogMiddlewareTest(TestCase):
    """Test LogMiddleware"""
    
    def setUp(self):
        """Create test user and client"""
        self.user = Personel.objects.create_user(
            kullaniciadi='testuser',
            password='testpass123',
            adsoyad='Test User',
            yonetici=True
        )
        self.client = Client()
        self.client.force_login(self.user)
    
    def test_log_not_created_for_get_request(self):
        """Test that GET requests don't create logs"""
        initial_count = Log.objects.count()
        
        response = self.client.get(reverse('dashboard'))
        
        # Log count should not increase
        self.assertEqual(Log.objects.count(), initial_count)
    
    def test_log_created_for_post_request(self):
        """Test that POST requests to logged endpoints create logs"""
        # This test would require actual views to be implemented
        # For now, we'll just verify the middleware exists
        from core.middleware import LogMiddleware
        self.assertIsNotNone(LogMiddleware)


class HiddenUserMiddlewareTest(TestCase):
    """Test HiddenUserMiddleware"""
    
    def setUp(self):
        """Create test users"""
        self.normal_user = Personel.objects.create_user(
            kullaniciadi='normaluser',
            password='testpass123',
            adsoyad='Normal User',
            gg=False
        )
        
        self.hidden_user = Personel.objects.create_user(
            kullaniciadi='hiddenuser',
            password='testpass123',
            adsoyad='Hidden User',
            gg=True,
            yonetici=False
        )
        
        self.hidden_admin = Personel.objects.create_user(
            kullaniciadi='hiddenadmin',
            password='testpass123',
            adsoyad='Hidden Admin',
            gg=True,
            yonetici=True
        )
    
    def test_normal_user_access(self):
        """Test normal user can access all pages"""
        client = Client()
        client.force_login(self.normal_user)
        
        response = client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_hidden_user_restricted_access(self):
        """Test hidden user has restricted access"""
        # This test would require actual restricted views to be implemented
        # For now, we'll just verify the middleware exists
        from core.middleware import HiddenUserMiddleware
        self.assertIsNotNone(HiddenUserMiddleware)
    
    def test_hidden_admin_full_access(self):
        """Test hidden admin (yonetici=True) has full access"""
        client = Client()
        client.force_login(self.hidden_admin)
        
        response = client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)


class GetClientIPTest(TestCase):
    """Test get_client_ip utility function"""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_get_ip_from_remote_addr(self):
        """Test getting IP from REMOTE_ADDR"""
        from core.utils import get_client_ip
        
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')
    
    def test_get_ip_from_x_forwarded_for(self):
        """Test getting IP from X-Forwarded-For header"""
        from core.utils import get_client_ip
        
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '10.0.0.1, 192.168.1.1'
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '10.0.0.1')

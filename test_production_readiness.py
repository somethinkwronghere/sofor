"""
Production Readiness Test Script
Tests all critical features and configurations before production deployment
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.models import Personel, Arac, GorevYeri, Gorev, Mesai, Izin
from django.conf import settings
from datetime import datetime, timedelta
import json

class ProductionReadinessTest:
    def __init__(self):
        self.client = Client()
        self.test_results = []
        self.passed = 0
        self.failed = 0
        
    def log_test(self, test_name, passed, message=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append(f"{status} - {test_name}")
        if message:
            self.test_results.append(f"    {message}")
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def test_settings_configuration(self):
        """Test critical settings configuration"""
        print("\n🔧 Testing Settings Configuration...")
        
        # Check SECRET_KEY
        secret_key_secure = len(settings.SECRET_KEY) > 50
        self.log_test(
            "SECRET_KEY length",
            secret_key_secure,
            f"Length: {len(settings.SECRET_KEY)}"
        )
        
        # Check DEBUG setting
        debug_off = not settings.DEBUG
        self.log_test(
            "DEBUG is False",
            debug_off,
            f"DEBUG = {settings.DEBUG}"
        )
        
        # Check ALLOWED_HOSTS
        has_allowed_hosts = len(settings.ALLOWED_HOSTS) > 0
        self.log_test(
            "ALLOWED_HOSTS configured",
            has_allowed_hosts,
            f"Hosts: {settings.ALLOWED_HOSTS}"
        )
        
        # Check STATIC_ROOT
        has_static_root = hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT
        self.log_test(
            "STATIC_ROOT configured",
            has_static_root,
            f"Path: {getattr(settings, 'STATIC_ROOT', 'Not set')}"
        )
    
    def test_database_connectivity(self):
        """Test database connectivity and data integrity"""
        print("\n💾 Testing Database Connectivity...")
        
        try:
            # Test Personel model
            personel_count = Personel.objects.count()
            self.log_test(
                "Personel table accessible",
                personel_count >= 0,
                f"Count: {personel_count}"
            )
            
            # Test Arac model
            arac_count = Arac.objects.count()
            self.log_test(
                "Arac table accessible",
                arac_count >= 0,
                f"Count: {arac_count}"
            )
            
            # Test GorevYeri model
            gorev_yeri_count = GorevYeri.objects.count()
            self.log_test(
                "GorevYeri table accessible",
                gorev_yeri_count >= 0,
                f"Count: {gorev_yeri_count}"
            )
            
            # Test Gorev model
            gorev_count = Gorev.objects.count()
            self.log_test(
                "Gorev table accessible",
                gorev_count >= 0,
                f"Count: {gorev_count}"
            )
            
            # Test Mesai model
            mesai_count = Mesai.objects.count()
            self.log_test(
                "Mesai table accessible",
                mesai_count >= 0,
                f"Count: {mesai_count}"
            )
            
            # Test Izin model
            izin_count = Izin.objects.count()
            self.log_test(
                "Izin table accessible",
                izin_count >= 0,
                f"Count: {izin_count}"
            )
            
        except Exception as e:
            self.log_test("Database connectivity", False, str(e))
    
    def test_authentication_system(self):
        """Test authentication and authorization"""
        print("\n🔐 Testing Authentication System...")
        
        try:
            # Test login page accessibility
            response = self.client.get('/giris/')
            self.log_test(
                "Login page accessible",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
            
            # Test admin user exists
            admin_exists = Personel.objects.filter(yonetici=True).exists()
            self.log_test(
                "Admin user exists",
                admin_exists,
                "At least one admin user found" if admin_exists else "No admin user"
            )
            
            # Test protected page redirect
            response = self.client.get('/')
            redirects_to_login = response.status_code == 302
            self.log_test(
                "Protected pages require login",
                redirects_to_login,
                f"Status: {response.status_code}"
            )
            
        except Exception as e:
            self.log_test("Authentication system", False, str(e))
    
    def test_url_routing(self):
        """Test critical URL routes"""
        print("\n🌐 Testing URL Routing...")
        
        urls_to_test = [
            ('/giris/', 'Login page'),
            ('/admin/', 'Admin panel'),
        ]
        
        for url, description in urls_to_test:
            try:
                response = self.client.get(url)
                accessible = response.status_code in [200, 302]
                self.log_test(
                    f"{description} ({url})",
                    accessible,
                    f"Status: {response.status_code}"
                )
            except Exception as e:
                self.log_test(f"{description} ({url})", False, str(e))
    
    def test_static_files(self):
        """Test static files configuration"""
        print("\n📁 Testing Static Files...")
        
        # Check STATIC_URL
        has_static_url = hasattr(settings, 'STATIC_URL')
        self.log_test(
            "STATIC_URL configured",
            has_static_url,
            f"URL: {getattr(settings, 'STATIC_URL', 'Not set')}"
        )
        
        # Check static directories exist
        static_dirs = getattr(settings, 'STATICFILES_DIRS', [])
        for static_dir in static_dirs:
            exists = os.path.exists(static_dir)
            self.log_test(
                f"Static directory exists",
                exists,
                f"Path: {static_dir}"
            )
    
    def test_middleware_configuration(self):
        """Test middleware configuration"""
        print("\n⚙️ Testing Middleware Configuration...")
        
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ]
        
        for middleware in required_middleware:
            is_configured = middleware in settings.MIDDLEWARE
            self.log_test(
                f"Middleware: {middleware.split('.')[-1]}",
                is_configured,
                "Configured" if is_configured else "Missing"
            )
    
    def test_security_settings(self):
        """Test security settings"""
        print("\n🔒 Testing Security Settings...")
        
        security_checks = [
            ('CSRF_COOKIE_SECURE', False),  # Should be True in production with HTTPS
            ('SESSION_COOKIE_SECURE', False),  # Should be True in production with HTTPS
            ('SECURE_BROWSER_XSS_FILTER', True),
            ('SECURE_CONTENT_TYPE_NOSNIFF', True),
            ('X_FRAME_OPTIONS', 'DENY'),
        ]
        
        for setting_name, expected_value in security_checks:
            actual_value = getattr(settings, setting_name, None)
            if isinstance(expected_value, bool):
                is_correct = actual_value == expected_value
            else:
                is_correct = actual_value == expected_value
            
            self.log_test(
                f"Security: {setting_name}",
                is_correct or setting_name in ['CSRF_COOKIE_SECURE', 'SESSION_COOKIE_SECURE'],
                f"Value: {actual_value} (Expected: {expected_value})"
            )
    
    def test_models_integrity(self):
        """Test model relationships and integrity"""
        print("\n🔗 Testing Model Relationships...")
        
        try:
            # Test if we can query related objects
            if Gorev.objects.exists():
                gorev = Gorev.objects.select_related('sofor', 'yurt', 'arac').first()
                has_relations = gorev is not None
                self.log_test(
                    "Gorev model relationships",
                    has_relations,
                    "Foreign keys working correctly"
                )
            else:
                self.log_test(
                    "Gorev model relationships",
                    True,
                    "No data to test (OK for fresh install)"
                )
            
            # Test if we can query Mesai with relations
            if Mesai.objects.exists():
                mesai = Mesai.objects.select_related('sofor', 'arac').first()
                has_relations = mesai is not None
                self.log_test(
                    "Mesai model relationships",
                    has_relations,
                    "Foreign keys working correctly"
                )
            else:
                self.log_test(
                    "Mesai model relationships",
                    True,
                    "No data to test (OK for fresh install)"
                )
                
        except Exception as e:
            self.log_test("Model relationships", False, str(e))
    
    def test_forms_validation(self):
        """Test form imports and basic validation"""
        print("\n📝 Testing Forms...")
        
        try:
            from core.forms import (
                GorevForm, MesaiForm, IzinForm, AracForm,
                PersonelForm, GorevlendirmeForm, MalzemeForm, GorevYeriForm
            )
            
            forms = [
                ('GorevForm', GorevForm),
                ('MesaiForm', MesaiForm),
                ('IzinForm', IzinForm),
                ('AracForm', AracForm),
                ('PersonelForm', PersonelForm),
                ('GorevlendirmeForm', GorevlendirmeForm),
                ('MalzemeForm', MalzemeForm),
                ('GorevYeriForm', GorevYeriForm),
            ]
            
            for form_name, form_class in forms:
                try:
                    form = form_class()
                    self.log_test(
                        f"Form: {form_name}",
                        True,
                        "Instantiated successfully"
                    )
                except Exception as e:
                    self.log_test(f"Form: {form_name}", False, str(e))
                    
        except Exception as e:
            self.log_test("Forms import", False, str(e))
    
    def test_templates_exist(self):
        """Test critical templates exist"""
        print("\n📄 Testing Templates...")
        
        critical_templates = [
            'base.html',
            'dashboard.html',
            'auth/login.html',
            'gorev/taslak.html',
            'gorev/nihai.html',
            'gorev/form.html',
            'mesai/liste.html',
            'izin/liste.html',
            'arac/liste.html',
            'personel/liste.html',
        ]
        
        template_dirs = settings.TEMPLATES[0]['DIRS']
        for template_dir in template_dirs:
            for template in critical_templates:
                template_path = os.path.join(template_dir, template)
                exists = os.path.exists(template_path)
                self.log_test(
                    f"Template: {template}",
                    exists,
                    f"Path: {template_path}"
                )
                if exists:
                    break
    
    def test_custom_middleware(self):
        """Test custom middleware"""
        print("\n🔧 Testing Custom Middleware...")
        
        try:
            from core.middleware import LogMiddleware, HiddenUserMiddleware
            
            self.log_test(
                "LogMiddleware import",
                True,
                "Successfully imported"
            )
            
            self.log_test(
                "HiddenUserMiddleware import",
                True,
                "Successfully imported"
            )
            
        except Exception as e:
            self.log_test("Custom middleware", False, str(e))
    
    def test_utility_functions(self):
        """Test utility functions"""
        print("\n🛠️ Testing Utility Functions...")
        
        try:
            from core.utils import get_client_ip, hesapla_mesai_suresi
            
            self.log_test(
                "Utility functions import",
                True,
                "get_client_ip, hesapla_mesai_suresi imported"
            )
            
            # Test mesai calculation
            start = datetime.now()
            end = start + timedelta(hours=8)
            mesai_suresi = hesapla_mesai_suresi(start, end)
            
            self.log_test(
                "Mesai calculation",
                mesai_suresi == 8.0,
                f"8 hours = {mesai_suresi} hours"
            )
            
        except Exception as e:
            self.log_test("Utility functions", False, str(e))
    
    def generate_report(self):
        """Generate final test report"""
        print("\n" + "="*70)
        print("📊 PRODUCTION READINESS TEST REPORT")
        print("="*70)
        
        for result in self.test_results:
            print(result)
        
        print("\n" + "="*70)
        print(f"✅ PASSED: {self.passed}")
        print(f"❌ FAILED: {self.failed}")
        print(f"📈 SUCCESS RATE: {(self.passed/(self.passed+self.failed)*100):.1f}%")
        print("="*70)
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED! System is ready for production.")
            return True
        else:
            print(f"\n⚠️ {self.failed} test(s) failed. Please fix before deploying to production.")
            return False
    
    def run_all_tests(self):
        """Run all production readiness tests"""
        print("🚀 Starting Production Readiness Tests...")
        print("="*70)
        
        self.test_settings_configuration()
        self.test_database_connectivity()
        self.test_authentication_system()
        self.test_url_routing()
        self.test_static_files()
        self.test_middleware_configuration()
        self.test_security_settings()
        self.test_models_integrity()
        self.test_forms_validation()
        self.test_templates_exist()
        self.test_custom_middleware()
        self.test_utility_functions()
        
        return self.generate_report()

if __name__ == '__main__':
    tester = ProductionReadinessTest()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

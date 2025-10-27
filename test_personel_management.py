"""
Test script for Personnel Management (Task 13)
Tests personnel CRUD operations and password change functionality
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from core.models import Personel, Gorev, Mesai, Izin, Log
from django.contrib.auth.hashers import check_password


class PersonelManagementTest(TestCase):
    """Test personnel management functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create admin user
        self.admin = Personel.objects.create_user(
            kullaniciadi='admin',
            password='admin123',
            adsoyad='Admin User',
            email='admin@test.com',
            yonetici=True,
            is_staff=True
        )
        
        # Create regular user
        self.user = Personel.objects.create_user(
            kullaniciadi='user1',
            password='user123',
            adsoyad='Test User',
            email='user@test.com',
            yonetici=False,
            kalanizin=20
        )
    
    def test_personel_listesi_requires_admin(self):
        """Test that personnel list requires admin access"""
        # Try without login
        response = self.client.get(reverse('personel_listesi'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Try with regular user
        self.client.login(kullaniciadi='user1', password='user123')
        response = self.client.get(reverse('personel_listesi'))
        self.assertEqual(response.status_code, 302)  # Redirect (no admin access)
        
        # Try with admin
        self.client.login(kullaniciadi='admin', password='admin123')
        response = self.client.get(reverse('personel_listesi'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Personel Listesi')
    
    def test_personel_ekle(self):
        """Test adding new personnel"""
        self.client.login(kullaniciadi='admin', password='admin123')
        
        response = self.client.post(reverse('personel_ekle'), {
            'adsoyad': 'New User',
            'kullaniciadi': 'newuser',
            'email': 'newuser@test.com',
            'sifre': 'newpass123',
            'sifre_tekrar': 'newpass123',
            'yonetici': False,
            'gg': False,
            'girisizni': False,
            'is_active': True,
            'kalanizin': 15
        })
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Check personnel was created
        new_user = Personel.objects.get(kullaniciadi='newuser')
        self.assertEqual(new_user.adsoyad, 'New User')
        self.assertEqual(new_user.email, 'newuser@test.com')
        self.assertEqual(new_user.kalanizin, 15)
        self.assertTrue(new_user.check_password('newpass123'))
        
        # Check log was created
        log_exists = Log.objects.filter(
            sofor=self.admin,
            islem__icontains='Yeni personel eklendi'
        ).exists()
        self.assertTrue(log_exists)
    
    def test_personel_ekle_password_mismatch(self):
        """Test password mismatch validation"""
        self.client.login(kullaniciadi='admin', password='admin123')
        
        response = self.client.post(reverse('personel_ekle'), {
            'adsoyad': 'Test User',
            'kullaniciadi': 'testuser',
            'sifre': 'pass123',
            'sifre_tekrar': 'pass456',  # Different password
            'is_active': True,
            'kalanizin': 10
        })
        
        # Should not redirect (form has errors)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'eşleşmiyor')
    
    def test_personel_duzenle(self):
        """Test editing personnel"""
        self.client.login(kullaniciadi='admin', password='admin123')
        
        response = self.client.post(reverse('personel_duzenle', args=[self.user.id]), {
            'adsoyad': 'Updated User',
            'kullaniciadi': 'user1',
            'email': 'updated@test.com',
            'yonetici': True,  # Promote to admin
            'gg': False,
            'girisizni': False,
            'is_active': True,
            'kalanizin': 25
        })
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Refresh from database
        self.user.refresh_from_db()
        self.assertEqual(self.user.adsoyad, 'Updated User')
        self.assertEqual(self.user.email, 'updated@test.com')
        self.assertTrue(self.user.yonetici)
        self.assertTrue(self.user.is_staff)  # Should be set when yonetici=True
        self.assertEqual(self.user.kalanizin, 25)
    
    def test_personel_sil_without_related_records(self):
        """Test deleting personnel without related records"""
        self.client.login(kullaniciadi='admin', password='admin123')
        
        # Create a user without any related records
        test_user = Personel.objects.create_user(
            kullaniciadi='deletetest',
            password='test123',
            adsoyad='Delete Test'
        )
        
        response = self.client.post(reverse('personel_sil', args=[test_user.id]))
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Check user was deleted
        self.assertFalse(Personel.objects.filter(id=test_user.id).exists())
    
    def test_personel_sil_with_related_records(self):
        """Test deleting personnel with related records (should deactivate)"""
        from core.models import GorevYeri, Arac
        
        self.client.login(kullaniciadi='admin', password='admin123')
        
        # Create related records
        yurt = GorevYeri.objects.create(ad='Test Yeri')
        gorev = Gorev.objects.create(
            sofor=self.user,
            yurt=yurt,
            varisyeri='Test',
            bstarih='2025-01-01 10:00:00',
            yetkili='Test'
        )
        
        response = self.client.post(reverse('personel_sil', args=[self.user.id]))
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Check user still exists but is deactivated
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertTrue(self.user.girisizni)
    
    def test_sifre_degistir(self):
        """Test password change functionality"""
        self.client.login(kullaniciadi='user1', password='user123')
        
        response = self.client.post(reverse('sifre_degistir'), {
            'eski_sifre': 'user123',
            'yeni_sifre': 'newpass123',
            'yeni_sifre_tekrar': 'newpass123'
        })
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Refresh from database
        self.user.refresh_from_db()
        
        # Check new password works
        self.assertTrue(self.user.check_password('newpass123'))
        
        # Check old password doesn't work
        self.assertFalse(self.user.check_password('user123'))
        
        # Check log was created
        log_exists = Log.objects.filter(
            sofor=self.user,
            islem__icontains='Şifre değiştirildi'
        ).exists()
        self.assertTrue(log_exists)
    
    def test_sifre_degistir_wrong_old_password(self):
        """Test password change with wrong old password"""
        self.client.login(kullaniciadi='user1', password='user123')
        
        response = self.client.post(reverse('sifre_degistir'), {
            'eski_sifre': 'wrongpass',
            'yeni_sifre': 'newpass123',
            'yeni_sifre_tekrar': 'newpass123'
        })
        
        # Should not redirect (form has errors)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'hatalı')
    
    def test_sifre_degistir_password_mismatch(self):
        """Test password change with mismatched new passwords"""
        self.client.login(kullaniciadi='user1', password='user123')
        
        response = self.client.post(reverse('sifre_degistir'), {
            'eski_sifre': 'user123',
            'yeni_sifre': 'newpass123',
            'yeni_sifre_tekrar': 'different123'
        })
        
        # Should not redirect (form has errors)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'eşleşmiyor')
    
    def test_personel_detay(self):
        """Test personnel detail view"""
        from core.models import GorevYeri
        
        self.client.login(kullaniciadi='admin', password='admin123')
        
        # Create some related records
        yurt = GorevYeri.objects.create(ad='Test Yeri')
        gorev = Gorev.objects.create(
            sofor=self.user,
            yurt=yurt,
            varisyeri='Test',
            bstarih='2025-01-01 10:00:00',
            yetkili='Test'
        )
        
        response = self.client.get(reverse('personel_detay', args=[self.user.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.adsoyad)
        self.assertContains(response, self.user.kullaniciadi)
        self.assertContains(response, 'Test Yeri')
    
    def test_personel_search(self):
        """Test personnel search functionality"""
        self.client.login(kullaniciadi='admin', password='admin123')
        
        response = self.client.get(reverse('personel_listesi'), {'q': 'Test User'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')
        self.assertNotContains(response, 'Admin User')
    
    def test_personel_filter_by_status(self):
        """Test personnel filtering by status"""
        self.client.login(kullaniciadi='admin', password='admin123')
        
        # Create inactive user
        inactive_user = Personel.objects.create_user(
            kullaniciadi='inactive',
            password='test123',
            adsoyad='Inactive User',
            is_active=False
        )
        
        # Filter for active users
        response = self.client.get(reverse('personel_listesi'), {'durum': 'aktif'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')
        self.assertNotContains(response, 'Inactive User')
        
        # Filter for inactive users
        response = self.client.get(reverse('personel_listesi'), {'durum': 'pasif'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inactive User')


def run_tests():
    """Run all tests"""
    import sys
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False, keepdb=False)
    
    # Run tests
    failures = test_runner.run_tests(['__main__'])
    
    if failures:
        print(f"\n❌ {failures} test(s) failed")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)


if __name__ == '__main__':
    print("=" * 70)
    print("PERSONNEL MANAGEMENT TEST (Task 13)")
    print("=" * 70)
    print("\nTesting personnel CRUD operations and password change...")
    print("-" * 70)
    
    run_tests()

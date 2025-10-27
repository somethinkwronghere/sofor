"""
Tests for utility functions
"""
from django.test import TestCase, RequestFactory
from datetime import datetime, date, timedelta
from core.utils import (
    get_client_ip,
    hesapla_mesai_suresi,
    kontrol_muayene_tarihi,
    get_arac_uyarilari,
    hesapla_izin_gunleri,
    format_tarih,
    format_tarih_saat
)
from core.models import Arac, Personel


class GetClientIPTest(TestCase):
    """Test get_client_ip function"""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_get_ip_from_remote_addr(self):
        """Test getting IP from REMOTE_ADDR"""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')
    
    def test_get_ip_from_x_forwarded_for(self):
        """Test getting IP from X-Forwarded-For header"""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '10.0.0.1, 192.168.1.1'
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '10.0.0.1')
    
    def test_get_ip_no_meta(self):
        """Test getting IP when no META data"""
        request = self.factory.get('/')
        
        ip = get_client_ip(request)
        # Django test framework provides a default IP (127.0.0.1)
        self.assertIsNotNone(ip)


class HesaplaMesaiSuresiTest(TestCase):
    """Test hesapla_mesai_suresi function"""
    
    def test_calculate_hours(self):
        """Test calculating hours between two datetimes"""
        baslangic = datetime(2025, 1, 1, 9, 0)
        bitis = datetime(2025, 1, 1, 17, 30)
        
        hours = hesapla_mesai_suresi(baslangic, bitis)
        self.assertEqual(hours, 8.5)
    
    def test_calculate_full_day(self):
        """Test calculating 24 hours"""
        baslangic = datetime(2025, 1, 1, 0, 0)
        bitis = datetime(2025, 1, 2, 0, 0)
        
        hours = hesapla_mesai_suresi(baslangic, bitis)
        self.assertEqual(hours, 24.0)
    
    def test_invalid_order(self):
        """Test when end time is before start time"""
        baslangic = datetime(2025, 1, 1, 17, 0)
        bitis = datetime(2025, 1, 1, 9, 0)
        
        hours = hesapla_mesai_suresi(baslangic, bitis)
        self.assertEqual(hours, 0.0)
    
    def test_none_values(self):
        """Test with None values"""
        hours = hesapla_mesai_suresi(None, None)
        self.assertEqual(hours, 0.0)
        
        hours = hesapla_mesai_suresi(datetime.now(), None)
        self.assertEqual(hours, 0.0)


class KontrolMuayeneTarihiTest(TestCase):
    """Test kontrol_muayene_tarihi function"""
    
    def setUp(self):
        """Create test vehicle"""
        self.arac = Arac.objects.create(
            plaka='34ABC123',
            kategori='binek',
            marka='Test Marka'
        )
    
    def test_no_dates(self):
        """Test vehicle with no inspection dates"""
        warnings = kontrol_muayene_tarihi(self.arac)
        
        self.assertFalse(warnings['has_warning'])
        self.assertIsNone(warnings['muayene'])
        self.assertIsNone(warnings['sigorta'])
        self.assertIsNone(warnings['egzoz'])
    
    def test_approaching_muayene(self):
        """Test vehicle with approaching inspection date"""
        self.arac.muayene = datetime.now() + timedelta(days=15)
        self.arac.save()
        
        warnings = kontrol_muayene_tarihi(self.arac)
        
        self.assertTrue(warnings['has_warning'])
        self.assertIsNotNone(warnings['muayene'])
        self.assertIn('yaklaşıyor', warnings['muayene'])
    
    def test_expired_muayene(self):
        """Test vehicle with expired inspection date"""
        self.arac.muayene = datetime.now() - timedelta(days=10)
        self.arac.save()
        
        warnings = kontrol_muayene_tarihi(self.arac)
        
        self.assertTrue(warnings['has_warning'])
        self.assertIsNotNone(warnings['muayene'])
        self.assertIn('geçti', warnings['muayene'])
    
    def test_approaching_sigorta(self):
        """Test vehicle with approaching insurance date"""
        self.arac.sigorta = datetime.now() + timedelta(days=20)
        self.arac.save()
        
        warnings = kontrol_muayene_tarihi(self.arac)
        
        self.assertTrue(warnings['has_warning'])
        self.assertIsNotNone(warnings['sigorta'])
        self.assertIn('yaklaşıyor', warnings['sigorta'])
    
    def test_multiple_warnings(self):
        """Test vehicle with multiple warnings"""
        self.arac.muayene = datetime.now() + timedelta(days=15)
        self.arac.sigorta = datetime.now() - timedelta(days=5)
        self.arac.egzoz = datetime.now() + timedelta(days=10)
        self.arac.save()
        
        warnings = kontrol_muayene_tarihi(self.arac)
        
        self.assertTrue(warnings['has_warning'])
        self.assertIsNotNone(warnings['muayene'])
        self.assertIsNotNone(warnings['sigorta'])
        self.assertIsNotNone(warnings['egzoz'])


class GetAracUyarilariTest(TestCase):
    """Test get_arac_uyarilari function"""
    
    def setUp(self):
        """Create test vehicles"""
        # Vehicle with warning
        self.arac1 = Arac.objects.create(
            plaka='34ABC123',
            kategori='binek',
            marka='Test Marka 1',
            muayene=datetime.now() + timedelta(days=15)
        )
        
        # Vehicle without warning
        self.arac2 = Arac.objects.create(
            plaka='34XYZ789',
            kategori='binek',
            marka='Test Marka 2',
            muayene=datetime.now() + timedelta(days=60)
        )
        
        # Archived vehicle with warning (should not appear)
        self.arac3 = Arac.objects.create(
            plaka='34DEF456',
            kategori='binek',
            marka='Test Marka 3',
            muayene=datetime.now() + timedelta(days=10),
            arsiv=True
        )
    
    def test_get_warnings(self):
        """Test getting vehicles with warnings"""
        uyarilar = get_arac_uyarilari()
        
        # Should only return arac1 (not arac2 or archived arac3)
        self.assertEqual(len(uyarilar), 1)
        self.assertEqual(uyarilar[0]['arac'].plaka, '34ABC123')
        self.assertTrue(uyarilar[0]['warnings']['has_warning'])


class HesaplaIzinGunleriTest(TestCase):
    """Test hesapla_izin_gunleri function"""
    
    def test_calculate_days(self):
        """Test calculating days between two dates"""
        baslangic = date(2025, 1, 1)
        bitis = date(2025, 1, 5)
        
        days = hesapla_izin_gunleri(baslangic, bitis)
        self.assertEqual(days, 5)
    
    def test_same_day(self):
        """Test same start and end date"""
        baslangic = date(2025, 1, 1)
        bitis = date(2025, 1, 1)
        
        days = hesapla_izin_gunleri(baslangic, bitis)
        self.assertEqual(days, 1)
    
    def test_invalid_order(self):
        """Test when end date is before start date"""
        baslangic = date(2025, 1, 5)
        bitis = date(2025, 1, 1)
        
        days = hesapla_izin_gunleri(baslangic, bitis)
        self.assertEqual(days, 0)
    
    def test_none_values(self):
        """Test with None values"""
        days = hesapla_izin_gunleri(None, None)
        self.assertEqual(days, 0)


class FormatTarihTest(TestCase):
    """Test format_tarih and format_tarih_saat functions"""
    
    def test_format_date(self):
        """Test formatting date"""
        tarih = datetime(2025, 1, 15, 10, 30)
        formatted = format_tarih(tarih)
        
        self.assertEqual(formatted, '15.01.2025')
    
    def test_format_datetime(self):
        """Test formatting datetime"""
        tarih = datetime(2025, 1, 15, 10, 30)
        formatted = format_tarih_saat(tarih)
        
        self.assertEqual(formatted, '15.01.2025 10:30')
    
    def test_format_none(self):
        """Test formatting None"""
        formatted = format_tarih(None)
        self.assertEqual(formatted, '')
        
        formatted = format_tarih_saat(None)
        self.assertEqual(formatted, '')
    
    def test_custom_format(self):
        """Test custom format string"""
        tarih = datetime(2025, 1, 15, 10, 30)
        formatted = format_tarih(tarih, '%Y-%m-%d')
        
        self.assertEqual(formatted, '2025-01-15')

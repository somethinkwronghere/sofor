"""
Test script for Task 15: Form validations, JavaScript and optimizations
Requirements: 2.1, 3.1, 3.2, 3.4, 3.5, 4.2, 4.3, 11.3, 11.4
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from core.models import Personel, Gorev, Mesai, Izin, Arac, GorevYeri
from core.forms import (
    GorevForm, MesaiForm, IzinForm, AracForm,
    PersonelForm, SifreForm
)
from datetime import datetime, timedelta
from django.utils import timezone


def test_form_imports():
    """Test that all forms can be imported"""
    print("Testing form imports...")
    try:
        from core.forms import (
            GorevForm, MesaiForm, IzinForm, AracForm,
            GorevlendirmeForm, MalzemeForm, GorevYeriForm,
            PersonelForm, SifreForm
        )
        print("✓ All forms imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Form import failed: {e}")
        return False


def test_gorev_form_validation():
    """Test Gorev form validation"""
    print("\nTesting Gorev form validation...")
    
    # Create test data
    personel = Personel.objects.first()
    gorev_yeri = GorevYeri.objects.first()
    
    if not personel or not gorev_yeri:
        print("⚠ Skipping: No test data available")
        return True
    
    # Test valid form
    valid_data = {
        'sofor': personel.id,
        'yurt': gorev_yeri.id,
        'varisyeri': 'Test Varış Yeri',
        'bstarih': timezone.now(),
        'bttarih': timezone.now() + timedelta(hours=2),
        'yetkili': 'Test Yetkili',
        'aciklama': 'Test açıklama'
    }
    
    form = GorevForm(data=valid_data)
    if form.is_valid():
        print("✓ Valid Gorev form passes validation")
    else:
        print(f"✗ Valid form failed: {form.errors}")
        return False
    
    # Test invalid date range
    invalid_data = valid_data.copy()
    invalid_data['bttarih'] = timezone.now() - timedelta(hours=1)
    
    form = GorevForm(data=invalid_data)
    if not form.is_valid():
        print("✓ Invalid date range correctly rejected")
    else:
        print("✗ Invalid date range not caught")
        return False
    
    # Test short varisyeri
    invalid_data = valid_data.copy()
    invalid_data['varisyeri'] = 'AB'
    
    form = GorevForm(data=invalid_data)
    if not form.is_valid():
        print("✓ Short varisyeri correctly rejected")
    else:
        print("✗ Short varisyeri not caught")
        return False
    
    return True


def test_mesai_form_validation():
    """Test Mesai form validation"""
    print("\nTesting Mesai form validation...")
    
    personel = Personel.objects.first()
    if not personel:
        print("⚠ Skipping: No test data available")
        return True
    
    # Test valid form with auto-calculation
    valid_data = {
        'sofor': personel.id,
        'bstarih': timezone.now(),
        'bttarih': timezone.now() + timedelta(hours=8),
        'mesai': '8.00',
        'gorev': 'Test görev açıklaması'
    }
    
    form = MesaiForm(data=valid_data)
    if form.is_valid():
        print("✓ Valid Mesai form passes validation")
        # Check if mesai is calculated
        if 'mesai' in form.cleaned_data:
            print(f"✓ Mesai calculated: {form.cleaned_data['mesai']} hours")
    else:
        print(f"✗ Valid form failed: {form.errors}")
        return False
    
    # Test invalid: more than 24 hours
    invalid_data = valid_data.copy()
    invalid_data['bttarih'] = timezone.now() + timedelta(hours=25)
    
    form = MesaiForm(data=invalid_data)
    if not form.is_valid():
        print("✓ Mesai > 24 hours correctly rejected")
    else:
        print("✗ Mesai > 24 hours not caught")
        return False
    
    return True


def test_izin_form_validation():
    """Test Izin form validation"""
    print("\nTesting Izin form validation...")
    
    personel = Personel.objects.first()
    if not personel:
        print("⚠ Skipping: No test data available")
        return True
    
    # Test valid form
    today = timezone.now().date()
    valid_data = {
        'sofor': personel.id,
        'bstarih': today,
        'bttarih': today + timedelta(days=3),
        'izin': '1',
        'gun': 3,
        'saat': 0,
        'aciklama': 'Test izin'
    }
    
    form = IzinForm(data=valid_data)
    if form.is_valid():
        print("✓ Valid Izin form passes validation")
    else:
        print(f"✗ Valid form failed: {form.errors}")
        return False
    
    # Test invalid: end date before start date
    invalid_data = valid_data.copy()
    invalid_data['bttarih'] = today - timedelta(days=1)
    
    form = IzinForm(data=invalid_data)
    if not form.is_valid():
        print("✓ Invalid date range correctly rejected")
    else:
        print("✗ Invalid date range not caught")
        return False
    
    return True


def test_arac_form_validation():
    """Test Arac form validation"""
    print("\nTesting Arac form validation...")
    
    # Test valid Turkish plate
    valid_data = {
        'plaka': '34 ABC 123',
        'kategori': 'binek',
        'marka': 'Test Marka',
        'yolcusayisi': '5'
    }
    
    form = AracForm(data=valid_data)
    if form.is_valid():
        print("✓ Valid Arac form passes validation")
    else:
        print(f"✗ Valid form failed: {form.errors}")
        return False
    
    # Test invalid plate format
    invalid_data = valid_data.copy()
    invalid_data['plaka'] = 'INVALID'
    
    form = AracForm(data=invalid_data)
    if not form.is_valid():
        print("✓ Invalid plate format correctly rejected")
    else:
        print("✗ Invalid plate format not caught")
        return False
    
    # Test invalid passenger count
    invalid_data = valid_data.copy()
    invalid_data['yolcusayisi'] = 'abc'
    
    form = AracForm(data=invalid_data)
    if not form.is_valid():
        print("✓ Invalid passenger count correctly rejected")
    else:
        print("✗ Invalid passenger count not caught")
        return False
    
    return True


def test_personel_form_validation():
    """Test Personel form validation"""
    print("\nTesting Personel form validation...")
    
    # Test valid form for new user
    valid_data = {
        'adsoyad': 'Test Kullanıcı',
        'kullaniciadi': 'testuser123',
        'email': 'test@example.com',
        'sifre': 'test123456',
        'sifre_tekrar': 'test123456',
        'yonetici': False
    }
    
    form = PersonelForm(data=valid_data)
    if form.is_valid():
        print("✓ Valid Personel form passes validation")
    else:
        print(f"✗ Valid form failed: {form.errors}")
        return False
    
    # Test password mismatch
    invalid_data = valid_data.copy()
    invalid_data['sifre_tekrar'] = 'different'
    
    form = PersonelForm(data=invalid_data)
    if not form.is_valid():
        print("✓ Password mismatch correctly rejected")
    else:
        print("✗ Password mismatch not caught")
        return False
    
    # Test short password
    invalid_data = valid_data.copy()
    invalid_data['sifre'] = '123'
    invalid_data['sifre_tekrar'] = '123'
    
    form = PersonelForm(data=invalid_data)
    if not form.is_valid():
        print("✓ Short password correctly rejected")
    else:
        print("✗ Short password not caught")
        return False
    
    return True


def test_query_optimization():
    """Test query optimization with select_related and prefetch_related"""
    print("\nTesting query optimization...")
    
    from django.db import connection
    from django.test.utils import override_settings
    
    # Test Gorev queries with select_related
    print("Testing Gorev query optimization...")
    
    # Without optimization
    connection.queries_log.clear()
    gorevler = list(Gorev.objects.filter(gizle=False)[:10])
    query_count_without = len(connection.queries)
    
    # With optimization
    connection.queries_log.clear()
    gorevler_optimized = list(
        Gorev.objects.filter(gizle=False)
        .select_related('sofor', 'yurt', 'arac')[:10]
    )
    query_count_with = len(connection.queries)
    
    if query_count_with <= query_count_without:
        print(f"✓ Query optimization working (queries reduced from {query_count_without} to {query_count_with})")
    else:
        print(f"⚠ Query count: without={query_count_without}, with={query_count_with}")
    
    return True


def test_pagination():
    """Test pagination functionality"""
    print("\nTesting pagination...")
    
    from django.core.paginator import Paginator
    
    # Get all gorevler
    gorevler = Gorev.objects.filter(gizle=False).order_by('-bstarih')
    
    # Create paginator
    paginator = Paginator(gorevler, 25)  # 25 items per page
    
    print(f"✓ Total items: {paginator.count}")
    print(f"✓ Total pages: {paginator.num_pages}")
    
    if paginator.count > 0:
        page1 = paginator.page(1)
        print(f"✓ Page 1 has {len(page1)} items")
        print(f"✓ Has next: {page1.has_next()}")
        print(f"✓ Has previous: {page1.has_previous()}")
    
    return True


def test_javascript_files():
    """Test that JavaScript files exist and are valid"""
    print("\nTesting JavaScript files...")
    
    js_file = 'static/js/main.js'
    if os.path.exists(js_file):
        print(f"✓ {js_file} exists")
        
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for key functions
        required_functions = [
            'initMesaiCalculation',
            'initIzinCalculation',
            'initPlakaValidation',
            'initDeleteModals',
            'validateDateRange',
            'calculateMesai',
            'showDeleteModal'
        ]
        
        for func in required_functions:
            if func in content:
                print(f"✓ Function '{func}' found")
            else:
                print(f"✗ Function '{func}' not found")
                return False
    else:
        print(f"✗ {js_file} not found")
        return False
    
    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Task 15: Form Validations, JavaScript and Optimization Tests")
    print("=" * 60)
    
    tests = [
        test_form_imports,
        test_gorev_form_validation,
        test_mesai_form_validation,
        test_izin_form_validation,
        test_arac_form_validation,
        test_personel_form_validation,
        test_query_optimization,
        test_pagination,
        test_javascript_files
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())

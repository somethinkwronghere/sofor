"""
Test script for dashboard functionality
Tests the dashboard view and its queries
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from core.models import Gorev, Arac, Personel, Mesai, GorevYeri
from datetime import datetime, timedelta
from django.utils import timezone

def test_dashboard_statistics():
    """Test dashboard statistics calculations"""
    print("\n=== Testing Dashboard Statistics ===")
    
    # Count statistics
    total_gorev = Gorev.objects.filter(gizle=False).count()
    total_personel = Personel.objects.filter(is_active=True, girisizni=False).count()
    total_arac = Arac.objects.filter(arsiv=False, gizle=False).count()
    
    print(f"✓ Total Görev: {total_gorev}")
    print(f"✓ Total Personel: {total_personel}")
    print(f"✓ Total Araç: {total_arac}")
    
    return True

def test_recent_tasks():
    """Test recent tasks query"""
    print("\n=== Testing Recent Tasks Query ===")
    
    recent_gorevler = Gorev.objects.filter(
        gizle=False
    ).select_related('sofor', 'yurt', 'arac').order_by('-bstarih')[:10]
    
    print(f"✓ Found {recent_gorevler.count()} recent tasks")
    
    for gorev in recent_gorevler[:3]:
        print(f"  - {gorev.sofor.adsoyad} -> {gorev.yurt.ad} ({gorev.bstarih.strftime('%d.%m.%Y')})")
    
    return True

def test_vehicle_warnings():
    """Test vehicle inspection/insurance warnings"""
    print("\n=== Testing Vehicle Warnings ===")
    
    now = timezone.now()
    warning_date = now + timedelta(days=30)
    arac_uyarilar = []
    
    for arac in Arac.objects.filter(arsiv=False, gizle=False)[:5]:
        warnings = []
        
        # Check muayene
        if arac.muayene:
            if arac.muayene < now:
                warnings.append(f"Muayene tarihi geçmiş!")
            elif arac.muayene < warning_date:
                days_left = (arac.muayene.date() - now.date()).days
                warnings.append(f"Muayene tarihi yaklaşıyor ({days_left} gün)")
        
        # Check sigorta
        if arac.sigorta:
            if arac.sigorta < now:
                warnings.append(f"Sigorta tarihi geçmiş!")
            elif arac.sigorta < warning_date:
                days_left = (arac.sigorta.date() - now.date()).days
                warnings.append(f"Sigorta tarihi yaklaşıyor ({days_left} gün)")
        
        if warnings:
            arac_uyarilar.append({
                'arac': arac,
                'warnings': warnings
            })
    
    print(f"✓ Found {len(arac_uyarilar)} vehicles with warnings")
    
    for item in arac_uyarilar[:3]:
        print(f"  - {item['arac'].plaka}: {', '.join(item['warnings'])}")
    
    return True

def test_todays_activities():
    """Test today's tasks and overtime queries"""
    print("\n=== Testing Today's Activities ===")
    
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Today's tasks
    bugunun_gorevleri = Gorev.objects.filter(
        gizle=False,
        bstarih__gte=today_start,
        bstarih__lte=today_end
    ).select_related('sofor', 'yurt', 'arac')
    
    print(f"✓ Today's tasks: {bugunun_gorevleri.count()}")
    
    # Today's overtime
    bugunun_mesaileri = Mesai.objects.filter(
        bstarih__gte=today_start,
        bstarih__lte=today_end
    ).select_related('sofor', 'arac')
    
    print(f"✓ Today's overtime: {bugunun_mesaileri.count()}")
    
    return True

def test_dashboard_view():
    """Test dashboard view with authenticated user"""
    print("\n=== Testing Dashboard View ===")
    
    # Get a test user
    try:
        user = Personel.objects.filter(yonetici=True, girisizni=False).first()
        if not user:
            user = Personel.objects.filter(girisizni=False).first()
        
        if not user:
            print("✗ No users with login permission found in database")
            return False
        
        print(f"✓ Testing with user: {user.adsoyad} (girisizni={user.girisizni})")
        
        # Create a test client with SERVER_NAME
        client = Client(SERVER_NAME='localhost')
        
        # Login
        client.force_login(user)
        
        # Access dashboard
        response = client.get('/', HTTP_HOST='localhost', follow=True)
        
        if response.status_code == 200:
            print(f"✓ Dashboard loaded successfully (status: {response.status_code})")
            
            # Check if context variables are present
            context_vars = ['total_gorev', 'total_personel', 'total_arac', 
                          'recent_gorevler', 'arac_uyarilar', 
                          'bugunun_gorevleri', 'bugunun_mesaileri']
            
            for var in context_vars:
                if var in response.context:
                    print(f"  ✓ Context variable '{var}' present")
                else:
                    print(f"  ✗ Context variable '{var}' missing")
            
            return True
        else:
            print(f"✗ Dashboard failed to load (status: {response.status_code})")
            if response.redirect_chain:
                print(f"  Redirect chain: {response.redirect_chain}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing dashboard view: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all dashboard tests"""
    print("=" * 60)
    print("DASHBOARD FUNCTIONALITY TEST")
    print("=" * 60)
    
    tests = [
        test_dashboard_statistics,
        test_recent_tasks,
        test_vehicle_warnings,
        test_todays_activities,
        test_dashboard_view,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with error: {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All dashboard tests passed successfully!")
        return 0
    else:
        print("\n✗ Some tests failed. Please review the output above.")
        return 1

if __name__ == '__main__':
    exit(main())

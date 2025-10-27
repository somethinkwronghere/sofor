"""
Comprehensive verification script for personnel data migration
Verifies that all personnel data was migrated correctly with proper MD5 password hashes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings')
django.setup()

from core.models import Personel
from hashlib import md5

def verify_personel_migration():
    """Verify personnel migration"""
    print("=" * 70)
    print("PERSONEL DATA MIGRATION VERIFICATION")
    print("=" * 70)
    
    # Get all personnel
    personel_list = Personel.objects.all().order_by('id')
    total_count = personel_list.count()
    
    print(f"\nTotal Personnel Records: {total_count}")
    print("-" * 70)
    
    # Verify each record
    valid_count = 0
    invalid_count = 0
    
    print("\nVerifying personnel records:")
    print(f"{'ID':<5} {'Name':<25} {'Username':<15} {'Password Hash':<35} {'Status'}")
    print("-" * 100)
    
    for personel in personel_list:
        # Check required fields
        has_id = personel.id is not None
        has_name = bool(personel.adsoyad)
        has_username = bool(personel.kullaniciadi)
        has_password = bool(personel.password)
        
        # Check password format (should be 32-char MD5 hash)
        password_valid = False
        if has_password:
            # Check if it's a valid MD5 hash (32 hex characters)
            if len(personel.password) == 32:
                try:
                    int(personel.password, 16)  # Try to parse as hex
                    password_valid = True
                except ValueError:
                    password_valid = False
        
        # Overall status
        is_valid = has_id and has_name and has_username and has_password and password_valid
        
        if is_valid:
            valid_count += 1
            status = "✓ OK"
        else:
            invalid_count += 1
            status = "✗ INVALID"
            if not has_password:
                status += " (No password)"
            elif not password_valid:
                status += " (Invalid hash)"
        
        # Display record
        name_display = personel.adsoyad[:24] if len(personel.adsoyad) > 24 else personel.adsoyad
        username_display = personel.kullaniciadi[:14] if len(personel.kullaniciadi) > 14 else personel.kullaniciadi
        password_display = personel.password[:32] if personel.password else "N/A"
        
        print(f"{personel.id:<5} {name_display:<25} {username_display:<15} {password_display:<35} {status}")
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    print(f"Total Records:    {total_count}")
    print(f"Valid Records:    {valid_count}")
    print(f"Invalid Records:  {invalid_count}")
    
    # Additional checks
    print("\n" + "-" * 70)
    print("ADDITIONAL CHECKS")
    print("-" * 70)
    
    # Check for managers
    managers = Personel.objects.filter(yonetici=True)
    print(f"Managers (yonetici=True):  {managers.count()}")
    for mgr in managers:
        print(f"  - {mgr.adsoyad} ({mgr.kullaniciadi})")
    
    # Check for hidden users
    hidden_users = Personel.objects.filter(gg=True)
    print(f"\nHidden Users (gg=True):    {hidden_users.count()}")
    
    # Check for users with login restrictions
    restricted_users = Personel.objects.filter(girisizni=True)
    print(f"Login Restricted (girisizni=True): {restricted_users.count()}")
    
    # Test authentication with known password
    print("\n" + "-" * 70)
    print("AUTHENTICATION TEST")
    print("-" * 70)
    
    # Test with user 'Zeki' (password: 123456, hash: e10adc3949ba59abbe56e057f20f883e)
    try:
        test_user = Personel.objects.get(kullaniciadi='Zeki')
        auth_result = test_user.check_password('123456')
        print(f"Test User: {test_user.adsoyad} ({test_user.kullaniciadi})")
        print(f"Password Hash: {test_user.password}")
        print(f"Authentication Test (password='123456'): {'✓ PASSED' if auth_result else '✗ FAILED'}")
    except Personel.DoesNotExist:
        print("✗ Test user 'Zeki' not found")
    
    print("\n" + "=" * 70)
    if invalid_count == 0:
        print("✓ ALL PERSONNEL DATA MIGRATED SUCCESSFULLY!")
    else:
        print(f"⚠ WARNING: {invalid_count} records have issues")
    print("=" * 70)

if __name__ == '__main__':
    verify_personel_migration()

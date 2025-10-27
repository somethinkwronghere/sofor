"""
Utility functions for the Görev Takip application
"""
from datetime import datetime, timedelta


def get_client_ip(request):
    """
    Get client IP address from request
    
    Args:
        request: Django HttpRequest object
        
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def hesapla_mesai_suresi(baslangic, bitis):
    """
    Calculate overtime duration in hours
    
    Args:
        baslangic: datetime object - Start time
        bitis: datetime object - End time
        
    Returns:
        float: Duration in hours (rounded to 2 decimal places)
        
    Example:
        >>> from datetime import datetime
        >>> baslangic = datetime(2025, 1, 1, 9, 0)
        >>> bitis = datetime(2025, 1, 1, 17, 30)
        >>> hesapla_mesai_suresi(baslangic, bitis)
        8.5
    """
    if not baslangic or not bitis:
        return 0.0
    
    if bitis < baslangic:
        return 0.0
    
    delta = bitis - baslangic
    hours = delta.total_seconds() / 3600
    return round(hours, 2)


def kontrol_muayene_tarihi(arac):
    """
    Check vehicle inspection date and return warning if approaching or expired
    
    Args:
        arac: Arac model instance
        
    Returns:
        dict: Dictionary with warning information
            {
                'muayene': str or None,
                'sigorta': str or None,
                'egzoz': str or None,
                'has_warning': bool
            }
            
    Example:
        >>> arac = Arac.objects.get(id=1)
        >>> warnings = kontrol_muayene_tarihi(arac)
        >>> if warnings['has_warning']:
        ...     print(warnings['muayene'])
    """
    warnings = {
        'muayene': None,
        'sigorta': None,
        'egzoz': None,
        'has_warning': False
    }
    
    today = datetime.now().date()
    warning_days = 30  # Warn 30 days before expiration
    
    # Check muayene (inspection) date
    if arac.muayene:
        muayene_date = arac.muayene.date() if hasattr(arac.muayene, 'date') else arac.muayene
        kalan_gun = (muayene_date - today).days
        
        if kalan_gun < 0:
            warnings['muayene'] = f"Muayene tarihi {abs(kalan_gun)} gün önce geçti!"
            warnings['has_warning'] = True
        elif kalan_gun <= warning_days:
            warnings['muayene'] = f"Muayene tarihi yaklaşıyor! ({kalan_gun} gün kaldı)"
            warnings['has_warning'] = True
    
    # Check sigorta (insurance) date
    if arac.sigorta:
        sigorta_date = arac.sigorta.date() if hasattr(arac.sigorta, 'date') else arac.sigorta
        kalan_gun = (sigorta_date - today).days
        
        if kalan_gun < 0:
            warnings['sigorta'] = f"Sigorta tarihi {abs(kalan_gun)} gün önce geçti!"
            warnings['has_warning'] = True
        elif kalan_gun <= warning_days:
            warnings['sigorta'] = f"Sigorta tarihi yaklaşıyor! ({kalan_gun} gün kaldı)"
            warnings['has_warning'] = True
    
    # Check egzoz (emission test) date
    if arac.egzoz:
        egzoz_date = arac.egzoz.date() if hasattr(arac.egzoz, 'date') else arac.egzoz
        kalan_gun = (egzoz_date - today).days
        
        if kalan_gun < 0:
            warnings['egzoz'] = f"Egzoz muayenesi {abs(kalan_gun)} gün önce geçti!"
            warnings['has_warning'] = True
        elif kalan_gun <= warning_days:
            warnings['egzoz'] = f"Egzoz muayenesi yaklaşıyor! ({kalan_gun} gün kaldı)"
            warnings['has_warning'] = True
    
    return warnings


def get_arac_uyarilari():
    """
    Get all vehicles with approaching or expired inspection dates
    
    Returns:
        list: List of dictionaries containing vehicle and warning information
            [
                {
                    'arac': Arac instance,
                    'warnings': dict from kontrol_muayene_tarihi()
                },
                ...
            ]
    """
    from core.models import Arac
    
    arac_uyarilari = []
    araclar = Arac.objects.filter(arsiv=False, gizle=False)
    
    for arac in araclar:
        warnings = kontrol_muayene_tarihi(arac)
        if warnings['has_warning']:
            arac_uyarilari.append({
                'arac': arac,
                'warnings': warnings
            })
    
    return arac_uyarilari


def hesapla_izin_gunleri(baslangic, bitis):
    """
    Calculate number of leave days between two dates (inclusive)
    
    Args:
        baslangic: date object - Start date
        bitis: date object - End date
        
    Returns:
        int: Number of days (inclusive)
        
    Example:
        >>> from datetime import date
        >>> baslangic = date(2025, 1, 1)
        >>> bitis = date(2025, 1, 5)
        >>> hesapla_izin_gunleri(baslangic, bitis)
        5
    """
    if not baslangic or not bitis:
        return 0
    
    if bitis < baslangic:
        return 0
    
    delta = bitis - baslangic
    return delta.days + 1  # +1 to include both start and end dates


def format_tarih(tarih, format_str='%d.%m.%Y'):
    """
    Format datetime object to Turkish date format
    
    Args:
        tarih: datetime or date object
        format_str: str - Format string (default: '%d.%m.%Y')
        
    Returns:
        str: Formatted date string
        
    Example:
        >>> from datetime import datetime
        >>> tarih = datetime(2025, 1, 15, 10, 30)
        >>> format_tarih(tarih)
        '15.01.2025'
    """
    if not tarih:
        return ''
    
    try:
        return tarih.strftime(format_str)
    except:
        return str(tarih)


def format_tarih_saat(tarih):
    """
    Format datetime object to Turkish date and time format
    
    Args:
        tarih: datetime object
        
    Returns:
        str: Formatted date and time string
        
    Example:
        >>> from datetime import datetime
        >>> tarih = datetime(2025, 1, 15, 10, 30)
        >>> format_tarih_saat(tarih)
        '15.01.2025 10:30'
    """
    return format_tarih(tarih, '%d.%m.%Y %H:%M')

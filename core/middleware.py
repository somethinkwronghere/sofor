"""
Custom middleware for logging and authorization
"""
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from core.models import Log
from core.utils import get_client_ip


class LoginPermissionMiddleware:
    """
    Middleware to check if authenticated users have login permission (girisizni=False)
    If a user's login permission is revoked while they're logged in, log them out
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if user is authenticated and has girisizni flag set
        if request.user.is_authenticated and hasattr(request.user, 'girisizni'):
            if request.user.girisizni:
                # User's login permission has been revoked
                from django.contrib.auth import logout
                messages.error(request, 'Giriş izniniz kaldırılmış. Lütfen yöneticinizle iletişime geçin.')
                logout(request)
                return redirect('giris')
        
        response = self.get_response(request)
        return response


class LogMiddleware:
    """
    Middleware to automatically log important operations
    Logs POST requests to specific endpoints
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Define which URL patterns should be logged
        self.logged_patterns = [
            'gorev_ekle', 'gorev_duzenle', 'gorev_sil',
            'mesai_ekle', 'mesai_duzenle', 'mesai_sil',
            'izin_ekle', 'izin_duzenle', 'izin_sil',
            'arac_ekle', 'arac_duzenle', 'arac_sil',
            'personel_ekle', 'personel_duzenle', 'personel_sil',
            'gorevlendirme_ekle', 'gorevlendirme_duzenle', 'gorevlendirme_sil',
            'malzeme_ekle', 'malzeme_duzenle', 'malzeme_sil',
            'gorev_yeri_ekle', 'gorev_yeri_duzenle', 'gorev_yeri_sil',
        ]
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Log POST requests from authenticated users
        if request.method == 'POST' and request.user.is_authenticated:
            self.log_action(request, response)
        
        return response
    
    def log_action(self, request, response):
        """
        Create log entry for the action
        """
        try:
            # Only log successful operations (2xx status codes)
            if 200 <= response.status_code < 300:
                # Get the URL name
                url_name = request.resolver_match.url_name if request.resolver_match else None
                
                # Check if this URL should be logged
                if url_name and any(pattern in url_name for pattern in self.logged_patterns):
                    # Determine action type
                    action = self.get_action_description(url_name, request)
                    
                    # Create log entry
                    Log.objects.create(
                        sofor=request.user,
                        islem=action,
                        ip=get_client_ip(request)
                    )
        except Exception as e:
            # Don't let logging errors break the application
            pass
    
    def get_action_description(self, url_name, request):
        """
        Generate a human-readable description of the action
        """
        action_map = {
            'ekle': 'ekledi',
            'duzenle': 'düzenledi',
            'sil': 'sildi',
        }
        
        # Extract module and action from URL name
        parts = url_name.split('_')
        if len(parts) >= 2:
            module = parts[0].capitalize()
            action_key = parts[-1]
            action = action_map.get(action_key, 'işlem yaptı')
            
            return f"{module} {action}"
        
        return f"{url_name} işlemi gerçekleştirdi"


class HiddenUserMiddleware:
    """
    Middleware to handle hidden users (gg=True)
    Hidden users have restricted access to certain sensitive information
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Define restricted URL patterns for hidden users
        self.restricted_patterns = [
            'personel_listesi',
            'sistem_bilgileri',
            'log_kayitlari',
        ]
    
    def __call__(self, request):
        # Check if user is authenticated and is a hidden user
        if request.user.is_authenticated and hasattr(request.user, 'gg'):
            if request.user.gg and not request.user.yonetici:
                # Check if accessing restricted content
                url_name = request.resolver_match.url_name if request.resolver_match else None
                
                if url_name in self.restricted_patterns:
                    messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
                    return redirect('dashboard')
        
        response = self.get_response(request)
        return response

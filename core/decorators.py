"""
Custom decorators for authentication and authorization
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def admin_required(view_func):
    """
    Decorator to check if user is an administrator (yonetici=True)
    Requires user to be authenticated and have yonetici flag set to True
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            messages.warning(request, 'Bu sayfaya erişmek için giriş yapmalısınız.')
            return redirect('giris')
        
        # Check if user is administrator
        if not request.user.yonetici:
            messages.error(request, 'Bu sayfaya erişim yetkiniz yok. Sadece yöneticiler erişebilir.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def check_giris_izni(view_func):
    """
    Decorator to check if user has login permission (girisizni=False)
    This is an additional check beyond authentication
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            messages.warning(request, 'Bu sayfaya erişmek için giriş yapmalısınız.')
            return redirect('giris')
        
        # Check if user has login permission
        if request.user.girisizni:
            messages.error(request, 'Giriş izniniz kaldırılmış. Lütfen yöneticinizle iletişime geçin.')
            from django.contrib.auth import logout
            logout(request)
            return redirect('giris')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def yonetici_veya_sahip(view_func):
    """
    Decorator to check if user is administrator or the owner of the resource
    Allows access if user is yonetici OR if they are accessing their own data
    
    Usage: The view should accept a 'personel_id' parameter to check ownership
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            messages.warning(request, 'Bu sayfaya erişmek için giriş yapmalısınız.')
            return redirect('giris')
        
        # If user is administrator, allow access
        if request.user.yonetici:
            return view_func(request, *args, **kwargs)
        
        # Check if user is accessing their own data
        personel_id = kwargs.get('personel_id') or kwargs.get('id')
        if personel_id and int(personel_id) == request.user.id:
            return view_func(request, *args, **kwargs)
        
        # Access denied
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('dashboard')
    
    return wrapper

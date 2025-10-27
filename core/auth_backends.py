"""
Custom authentication backend for legacy MD5 password compatibility
"""
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from core.models import Personel
from hashlib import md5


class MD5AuthenticationBackend(BaseBackend):
    """
    Custom authentication backend that supports both MD5 (legacy) and Django's default password hashing
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user with username and password
        Supports both MD5 legacy passwords and Django's default hashing
        """
        if username is None or password is None:
            return None
        
        try:
            # Get user by username (kullaniciadi field)
            user = Personel.objects.get(kullaniciadi=username)
            
            # Check if user has login permission
            if user.girisizni:
                return None
            
            # Check if user is active
            if not user.is_active:
                return None
            
            # Try Django's check_password first (handles all configured hashers)
            if check_password(password, user.password):
                return user
            
            # If that fails, try direct MD5 comparison for legacy passwords
            # Legacy passwords might be stored as plain MD5 hash without algorithm prefix
            if self._check_md5_password(password, user.password):
                # Update to Django's secure hashing
                user.set_password(password)
                user.save(update_fields=['password'])
                return user
            
            return None
            
        except Personel.DoesNotExist:
            return None
    
    def _check_md5_password(self, password, stored_password):
        """
        Check if password matches a plain MD5 hash (legacy format)
        """
        # Compute MD5 of provided password
        computed_hash = md5(password.encode()).hexdigest()
        
        # Check if stored password is a plain MD5 hash (32 characters, no algorithm prefix)
        if len(stored_password) == 32 and not stored_password.startswith('md5$'):
            return computed_hash == stored_password
        
        return False
    
    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            return Personel.objects.get(pk=user_id)
        except Personel.DoesNotExist:
            return None

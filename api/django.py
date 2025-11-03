import os

# Ensure production settings in Vercel
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gorev_takip.settings_production')

from asgiref.wsgi import WsgiToAsgi
from gorev_takip.wsgi import application as wsgi_application

# ASGI app for Vercel Python runtime
app = WsgiToAsgi(wsgi_application)



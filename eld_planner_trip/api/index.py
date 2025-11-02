# api/index.py
import os
from django.core.wsgi import get_wsgi_application
from django.conf import settings

# Set environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eld_planner_trip.settings")
os.environ.setdefault("DEBUG", "False")

if os.getenv("VERCEL_URL"):
    settings.ALLOWED_HOSTS.append(os.getenv("VERCEL_URL").replace("https://", ""))

application = get_wsgi_application()

# Vercel handler
app = application

# Optional: Explicit OPTIONS handler (backup if WSGI misses it)
def handle_options(environ, start_response):
    if environ.get('REQUEST_METHOD') == 'OPTIONS':
        start_response('200 OK', [
            ('Access-Control-Allow-Origin', '*'),  # or your frontend URL
            ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
            ('Access-Control-Max-Age', '86400'),
            ('Content-Length', '0'),
        ])
        return [b'']
    return application(environ, start_response)

# Export the app
app = handle_options if os.getenv("VERCEL") else application
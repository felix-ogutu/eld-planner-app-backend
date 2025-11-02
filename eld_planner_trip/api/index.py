import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eld_planner_trip.settings")
os.environ.setdefault("DEBUG", "False")

# Allow Vercel dynamic host
if os.getenv("VERCEL_URL"):
    import django.conf
    django.conf.settings.ALLOWED_HOSTS.append(os.getenv("VERCEL_URL").replace("https://", ""))

application = get_wsgi_application()
app = application

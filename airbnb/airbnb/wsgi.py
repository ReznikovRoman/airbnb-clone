import os

from django.core.wsgi import get_wsgi_application

from manage import django_settings_module


os.environ.setdefault('DJANGO_SETTINGS_MODULE', django_settings_module)

application = get_wsgi_application()

import os

from channels.routing import get_default_application

import django

from manage import django_settings_module

os.environ.setdefault('DJANGO_SETTINGS_MODULE', django_settings_module)
django.setup()

application = get_default_application()

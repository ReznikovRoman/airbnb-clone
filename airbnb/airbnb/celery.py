import os

from celery import Celery

from manage import django_settings_module


os.environ.setdefault('DJANGO_SETTINGS_MODULE', django_settings_module)

app = Celery('airbnb')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

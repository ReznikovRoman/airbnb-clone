import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airbnb.settings')

app = Celery('airbnb')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

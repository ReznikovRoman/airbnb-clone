import os

from celery import Celery
from celery.schedules import crontab


settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'airbnb.settings.local')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

app = Celery('airbnb')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


# CELERY PERIODIC TASKS
# https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html
app.conf.beat_schedule = {
    'update_realty_visits_count_from_redis': {
        'task': 'realty.tasks.update_realty_visits_count_from_redis',
        'schedule': crontab(minute='*/5'),  # every 5 minutes
        'options': {
            'queue': 'default',
        },
    },
}

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Callable, ClassVar

from celery import Celery
from celery.app.task import Task as _Task
from celery.schedules import crontab
from celery.utils.log import get_task_logger

from django.core.cache import cache
from django.utils import timezone


if TYPE_CHECKING:
    from celery.result import AsyncResult  # isort: skip
    from common.types import seconds  # isort: skip


settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'airbnb.settings.pro')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

app = Celery(
    main='airbnb',
    task_cls='airbnb.celery:Task',
)
app.config_from_object(obj='django.conf:settings', namespace='CELERY')
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
    'email_subscribers_about_latest_realty': {
        'task': 'subscribers.tasks.email_subscribers_about_latest_realty',
        'schedule': crontab(day_of_week=5, hour=18, minute=0),  # every Friday at 6:00 p.m.
        'options': {
            'queue': 'emails',
        },
    },
}


class Task(_Task):
    # lock's ttl in seconds
    lock_ttl: ClassVar[seconds | None] = None

    # unique lock suffix: None, tuple or callable, that returns a tuple
    lock_suffix: ClassVar[tuple | Callable | None] = None

    log = get_task_logger(__name__)

    def __call__(self, *args, **kwargs):
        self.log.info(f'Starting task {self.request.id}')
        return super().__call__(*args, **kwargs)

    def get_lock_key(self, args, kwargs) -> str:
        if lock_suffix := self.__class__.lock_suffix:
            if callable(lock_suffix):
                lock_suffix = lock_suffix(*args or (), **kwargs or {})
        else:
            lock_suffix = ()
        return ':'.join(('task', self.name, *map(str, lock_suffix), 'lock'))

    def acquire_lock(self, lock_key: str, *, force: bool = False) -> bool:
        timestamp = timezone.now().timestamp()
        if force:
            self.log.debug(f'force=True, ignoring [{lock_key}]')
            cache.set(lock_key, timestamp, self.lock_ttl)
            return True
        elif not cache.add(lock_key, timestamp, self.lock_ttl):
            self.log.debug(f'[{lock_key}] is locked')
            return False
        self.log.debug(f'[{lock_key}] has been acquired')
        return True

    def delay(self, *args, force: bool = False, **kwargs) -> AsyncResult | None:
        if not self.lock_ttl:
            return super().apply_async(args, kwargs)
        lock_key = self.get_lock_key(args, kwargs)
        if self.acquire_lock(lock_key, force=force):
            return super().apply_async(args, kwargs)
        return None

    def apply_async(self, args=None, kwargs=None, *, force: bool = False, **options) -> AsyncResult | None:
        if not self.lock_ttl:
            return super().apply_async(args=args, kwargs=kwargs, **options)
        lock_key = self.get_lock_key(args, kwargs)
        if self.acquire_lock(lock_key, force=force):
            return super().apply_async(args=args, kwargs=kwargs, **options)
        return None

from celery import shared_task

from .services.realty import update_realty_visits_from_redis


@shared_task
def update_realty_visits_count_from_redis():
    """Updates `visits_count` value in DB from Redis."""
    update_realty_visits_from_redis()

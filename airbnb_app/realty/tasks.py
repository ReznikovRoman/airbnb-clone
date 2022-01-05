from airbnb.celery import app

from .services.realty import update_realty_visits_from_redis


@app.task(queue='default')
def update_realty_visits_count_from_redis(*args, **kwargs):
    """Updates `visits_count` value in DB from Redis."""
    update_realty_visits_from_redis()

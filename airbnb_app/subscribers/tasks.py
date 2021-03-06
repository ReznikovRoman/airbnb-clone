from __future__ import annotations

from typing import Optional

from celery_chunkificator.chunkify import Chunk, chunkify_task

from django.contrib.sites.models import Site
from django.db.models import Max, Min
from django.utils import timezone

from airbnb.celery import app
from realty.services.realty import get_available_realty_by_ids, get_n_latest_available_realty_ids

from .models import Subscriber
from .services import send_recommendation_email_to_subscriber


def get_subscribers_initial_chunk(*args, **kwargs):
    """Create a chunk of integers based on max and min primary keys."""
    subscriber_ids = Subscriber.objects.aggregate(Min('pk'), Max('pk'))
    chunk = Chunk(
        start=subscriber_ids['pk__min'] or 0,
        size=1000,
        max=subscriber_ids['pk__max'] or 0,
    )
    return chunk


@app.task(
    queue='emails',
    ignore_result=True,
    time_limit=5,
    soft_time_limit=3,
)
def send_recommendation_email(
        domain: str,
        subscriber_id: int | str,
        latest_realty_ids: list[int | str],
        *args,
        **kwargs,
) -> None:
    latest_realty = get_available_realty_by_ids(ids=latest_realty_ids)
    send_recommendation_email_to_subscriber(
        site_domain=domain,
        subscriber_id=subscriber_id,
        realty_recommendations=latest_realty,
    )


@app.task(
    queue='emails',
    ignore_result=True,
    time_limit=2 * 60 * 60,
    soft_time_limit=60 * 60,
    expires=timezone.now() + timezone.timedelta(days=3),
    lock_ttl=3 * 60 * 60,
)
@chunkify_task(
    sleep_timeout=10,
    initial_chunk=get_subscribers_initial_chunk,
)
def email_subscribers_about_latest_realty(
        chunk: Chunk,
        latest_realty_count: Optional[int] = 3,
        *args,
        **kwargs,
) -> None:
    """Send promo email about new Realty to all Subscribers."""
    domain = Site.objects.get_current().domain
    latest_realty_ids = list(get_n_latest_available_realty_ids(realty_count=latest_realty_count))
    chunked_qs = (
        Subscriber.objects
        .filter(pk__range=chunk.range)
        .values_list("pk", flat=True)
        .order_by("pk")
    )
    for subscriber_id in chunked_qs:
        send_recommendation_email.delay(
            domain=domain,
            subscriber_id=subscriber_id,
            latest_realty_ids=latest_realty_ids,
        )

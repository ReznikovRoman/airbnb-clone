from __future__ import annotations

from typing import List, Optional, Tuple, Union

from django.conf import settings
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import F, QuerySet

from common.session_handler import SessionHandler
from configs.redis_conf import redis_instance
from hosts.models import RealtyHost

from ..constants import REALTY_FORM_SESSION_PREFIX
from ..models import Amenity, Realty


def get_amenity_ids_from_session(session_handler: SessionHandler) -> Optional[QuerySet[int]]:
    amenities = session_handler.get_session().get(f"{REALTY_FORM_SESSION_PREFIX}_amenities", None)
    if amenities:
        amenities = Amenity.objects.filter(name__in=[*amenities]).values_list('id', flat=True)
    return amenities


def get_or_create_realty_host_by_user(user: settings.AUTH_USER_MODEL) -> Tuple[RealtyHost, bool]:
    return RealtyHost.objects.get_or_create(user=user)


def get_all_available_realty() -> 'QuerySet[Realty]':
    return Realty.available.all()


def get_available_realty_by_host(realty_host: RealtyHost) -> 'QuerySet[Realty]':
    return Realty.available.filter(host=realty_host)


def get_available_realty_by_ids(ids: list[int | str]) -> 'QuerySet[Realty]':
    return Realty.available.filter(id__in=ids)


def get_available_realty_by_city_slug(
        city_slug: str,
        realty_qs: Optional['QuerySet[Realty]'] = None,
) -> 'QuerySet[Realty]':
    if realty_qs is not None:
        return realty_qs.filter(location__city_slug=city_slug)
    return Realty.available.filter(location__city_slug=city_slug)


def get_available_realty_filtered_by_type(
        realty_types: Union[List[str], Tuple[str, ...]],
        realty_qs: Optional['QuerySet[Realty]'] = None,
) -> 'QuerySet[Realty]':
    if realty_qs is not None:
        return realty_qs.filter(realty_type__in=realty_types)
    return Realty.available.filter(realty_type__in=realty_types)


def get_last_realty() -> Realty:
    return Realty.objects.last()


def get_n_latest_available_realty(realty_count: int) -> 'QuerySet[Realty]':
    return Realty.available.all()[:realty_count]


def get_n_latest_available_realty_ids(realty_count: int) -> 'QuerySet[Realty]':
    return Realty.available.values_list('id', flat=True)[:realty_count]


def get_available_realty_count_by_city(city: str) -> int:
    return Realty.available.filter(location__city__iexact=city).count()


def get_available_realty_search_results(query: Optional[str] = None) -> 'QuerySet[Realty]':
    """Get all available realty filtered by a `query`.

    If `query` isn't passed, return all available realty objects.

    Args:
        query(Optional[str]): search query

    Returns:
        CustomDeleteQueryset[Realty]: filtered realty
    """
    if query:
        search_vector = (
            SearchVector('name', weight='A') +
            SearchVector('location__city', weight='B') +
            SearchVector('description', weight='B')
        )
        search_query = SearchQuery(query.lower())

        return Realty.available.annotate(
            rank=SearchRank(search_vector, search_query),
        ).filter(rank__gte=0.2).order_by('-rank')
    return Realty.available.all()


def update_realty_visits_count(realty_id: Union[int, str]) -> int:
    return int(redis_instance.incr(f"realty:{str(realty_id)}:views_count"))


def get_cached_realty_visits_count_by_realty_id(realty_id: Union[int, str]) -> int:
    views_count = redis_instance.get(f"realty:{str(realty_id)}:views_count")
    return int(views_count) if views_count is not None else 0


def update_realty_visits_from_redis() -> None:
    for key in redis_instance.scan_iter(match="realty:*:views_count"):
        realty_id = int(key.split(":")[1])
        visits_count = redis_instance.get(name=key)
        Realty.objects.filter(
            id=realty_id,
        ).update(
            visits_count=F('visits_count') + visits_count,
        )
        redis_instance.set(name=key, value=0)

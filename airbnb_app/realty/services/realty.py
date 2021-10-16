from typing import Optional, List, Union, Tuple

from django.conf import settings
from django.db.models import QuerySet
from django.contrib.postgres.search import SearchRank, SearchVector, SearchQuery

from hosts.models import RealtyHost
from configs.redis_conf import r
from common.session_handler import SessionHandler
from ..models import Amenity, Realty, CustomDeleteQueryset
from ..constants import REALTY_FORM_SESSION_PREFIX


def get_amenity_ids_from_session(session_handler: SessionHandler) -> Optional[QuerySet[int]]:
    amenities = session_handler.get_session().get(f"{REALTY_FORM_SESSION_PREFIX}_amenities", None)
    if amenities:
        amenities = Amenity.objects.filter(name__in=[*amenities]).values_list('id', flat=True)
    return amenities


def get_or_create_realty_host_by_user(user: settings.AUTH_USER_MODEL) -> Tuple[RealtyHost, bool]:
    return RealtyHost.objects.get_or_create(user=user)


def get_all_available_realty() -> 'CustomDeleteQueryset[Realty]':
    return Realty.available.all()


def get_available_realty_by_host(realty_host: RealtyHost) -> 'CustomDeleteQueryset[Realty]':
    return Realty.available.filter(host=realty_host)


def get_available_realty_by_city_slug(city_slug: str,
                                      realty_qs: Optional['CustomDeleteQueryset[Realty]'] = None
                                      ) -> 'CustomDeleteQueryset[Realty]':
    if realty_qs is not None:
        return realty_qs.filter(location__city_slug=city_slug)
    return Realty.available.filter(location__city_slug=city_slug)


def get_available_realty_filtered_by_type(realty_types: Union[List[str], Tuple[str, ...]],
                                          realty_qs: Optional['CustomDeleteQueryset[Realty]'] = None
                                          ) -> 'CustomDeleteQueryset[Realty]':
    if realty_qs is not None:
        return realty_qs.filter(realty_type__in=realty_types)
    return Realty.available.filter(realty_type__in=realty_types)


def get_last_realty() -> Realty:
    return Realty.objects.last()


def get_n_latest_available_realty(realty_count: int) -> 'CustomDeleteQueryset[Realty]':
    return Realty.available.all()[:realty_count]


def get_available_realty_count_by_city(city: str) -> int:
    return Realty.available.filter(location__city__iexact=city).count()


def get_available_realty_search_results(query: Optional[str] = None) -> 'CustomDeleteQueryset[Realty]':
    """
    Get all available realty filtered by a `query`.

    If `query` isn't passed, return all available realty objects.

    Args:
        query(Optional[str]): search query

    Returns:
        CustomDeleteQueryset[Realty]: filtered realty
    """
    if query:
        search_vector = SearchVector('location__city', weight='A') + \
                        SearchVector('name', weight='B') + \
                        SearchVector('description', weight='C')
        search_query = SearchQuery(query)

        return Realty.available.annotate(
            rank=SearchRank(search_vector, search_query),
        ).filter(rank__gte=0.3).order_by('-rank')
    return Realty.available.all()


def update_realty_visits_count(realty_id: Union[int, str]) -> int:
    return int(r.incr(f"realty:{str(realty_id)}:views_count"))


def get_cached_realty_visits_count_by_realty_id(realty_id: Union[int, str]) -> int:
    views_count = r.get(f"realty:{str(realty_id)}:views_count")
    return int(views_count) if views_count is not None else 0


def update_realty_visits_from_redis() -> None:
    for key in r.scan_iter("realty:*:views_count"):
        realty_id = int(key.split(":")[1])
        visits_count = r.get(key)
        Realty.objects.filter(id=realty_id).update(visits_count=visits_count)

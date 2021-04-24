from typing import Optional, List, Union, Tuple

from django.conf import settings
from django.db.models import QuerySet

from common.session_handler import SessionHandler
from hosts.models import RealtyHost
from ..models import Amenity, Realty, CustomDeleteQueryset


def get_amenity_ids_from_session(session_handler: SessionHandler) -> Optional[QuerySet[int]]:
    amenities = session_handler.get_session().get('realty_amenities', None)
    if amenities:
        amenities = Amenity.objects.filter(name__in=[*amenities]).values_list('id', flat=True)
    return amenities


def set_realty_host_by_user(realty: Realty, user: settings.AUTH_USER_MODEL) -> None:
    host = RealtyHost.objects.get_or_create(user=user)[0]
    realty.host = host


def get_all_available_realty() -> 'CustomDeleteQueryset[Realty]':
    return Realty.available.all()


def get_available_realty_by_host(realty_host: RealtyHost) -> 'CustomDeleteQueryset[Realty]':
    return Realty.available.filter(host=realty_host)


def get_available_realty_by_city_slug(city_slug: str,
                                      realty_qs: Optional['CustomDeleteQueryset[Realty]'] = None
                                      ) -> 'CustomDeleteQueryset[Realty]':
    if realty_qs is not None:
        return realty_qs.filter(location_city__slug=city_slug)
    return Realty.available.filter(location__city_slug=city_slug)


def get_available_realty_filtered_by_type(realty_types: Union[List[str], Tuple[str, ...]],
                                          realty_qs: Optional['CustomDeleteQueryset[Realty]']
                                          ) -> 'CustomDeleteQueryset[Realty]':
    if realty_qs is not None:
        return realty_qs.filter(realty_type__in=realty_types)
    return Realty.available.filter(realty_type__in=realty_types)


def get_latest_realty() -> Realty:
    return Realty.objects.last()


def get_n_latest_available_realty(realty_count: int) -> 'CustomDeleteQueryset[Realty]':
    return Realty.available.all()[:realty_count]


def get_available_realty_count_by_city(city: str) -> int:
    return Realty.available.filter(location__city__iexact=city).count()

from typing import Optional

from django.conf import settings
from django.db.models import QuerySet

from common.session_handler import SessionHandler
from hosts.models import RealtyHost
from ..models import Amenity, Realty


def get_amenity_ids_from_session(session_handler: SessionHandler) -> Optional[QuerySet[int]]:
    amenities = session_handler.get_session().get('realty_amenities', None)
    if amenities:
        amenities = Amenity.objects.filter(name__in=[*amenities]).values_list('id', flat=True)
    return amenities


def set_realty_host_by_user(realty: Realty, user: settings.AUTH_USER_MODEL) -> None:
    host = RealtyHost.objects.get_or_create(user=user)[0]
    realty.host = host

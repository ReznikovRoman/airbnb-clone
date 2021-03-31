from django.db.models import QuerySet

from common.session_handler import SessionHandler
from ..models import Amenity


def get_amenities_from_session(session_handler: SessionHandler) -> QuerySet:
    amenities = session_handler.get_session().get('realty_amenities', None)
    if amenities:
        amenities = Amenity.objects.filter(name__in=[*amenities]).values_list('id', flat=True)
    return amenities

from django.db.models.query import ValuesQuerySet

from realty.models import Realty


def get_all_realty_cities() -> ValuesQuerySet[Realty, str]:
    return Realty.available.order_by().values_list('location__city', flat=True).distinct()

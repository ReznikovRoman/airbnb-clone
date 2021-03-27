from realty.models import Realty


def get_all_realty_cities():
    return Realty.available.order_by().values_list('location__city', flat=True).distinct()

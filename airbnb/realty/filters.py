import django_filters

from .models import Realty


class RealtyFilter(django_filters.FilterSet):
    """Filter for a Realty model."""
    class Meta:
        model = Realty
        fields = {
            'realty_type': ['iexact'],
            'beds_count': ['exact', 'lt', 'gt'],
            'max_guests_count': ['exact', 'lt', 'gt'],
            'price_per_night': ['exact', 'lt', 'gt']
        }

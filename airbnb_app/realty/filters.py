import django_filters

from .models import Realty


class RealtyFilter(django_filters.FilterSet):
    """Filter for a Realty model."""

    class Meta:
        model = Realty
        fields = [
            'realty_type', 'beds_count', 'max_guests_count', 'price_per_night', 'amenities',
        ]


class RealtyShortFilter(django_filters.FilterSet):
    """Short filter for a Realty model."""

    guests_count = django_filters.NumberFilter(field_name='max_guests_count')

    class Meta:
        model = Realty
        fields = [
            'beds_count', 'guests_count', 'amenities',
        ]

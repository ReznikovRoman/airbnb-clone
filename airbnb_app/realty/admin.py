from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .models import Amenity, Realty, RealtyImage


def make_realty_available(modeladmin: "RealtyAdmin", request: HttpRequest, queryset: QuerySet[Realty]) -> None:
    queryset.update(is_available=True)


make_realty_available.short_description = "Make selected realty available"


def make_realty_unavailable(modeladmin: "RealtyAdmin", request: HttpRequest, queryset: QuerySet[Realty]) -> None:
    queryset.update(is_available=False)


make_realty_unavailable.short_description = "Make selected realty unavailable"


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


class AmenityInline(admin.TabularInline):
    model = Realty.amenities.through


@admin.register(Realty)
class RealtyAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'name', 'realty_type', 'is_available', 'created', 'host')
    search_fields = ('name',)
    list_filter = ('location__city', 'is_available')
    fieldsets = (
        ('General', {
            'fields': ('name', 'slug', 'location', 'host'),
        }),
        ('Realty info', {
            'fields': (
                'description', 'is_available', 'realty_type', 'beds_count', 'max_guests_count', 'price_per_night',
                'visits_count',
            ),
        }),
    )

    inlines = [
        AmenityInline,
    ]

    prepopulated_fields = {
        'slug': ('name',),
    }
    actions = [make_realty_available, make_realty_unavailable]


@admin.register(RealtyImage)
class RealtyImageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'realty')
    search_fields = ('realty__name',)
    list_filter = ('realty',)

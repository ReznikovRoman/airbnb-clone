from django.contrib import admin

from .models import Amenity, Realty, RealtyImage


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


class AmenityInline(admin.TabularInline):
    model = Realty.amenities.through


@admin.register(Realty)
class RealtyAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'name', 'realty_type', 'is_available', 'created', 'host')
    search_fields = ('name',)
    inlines = [
        AmenityInline,
    ]
    prepopulated_fields = {
        'slug': ('name',)
    }


@admin.register(RealtyImage)
class RealtyImageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'realty')
    search_fields = ('realty__name',)

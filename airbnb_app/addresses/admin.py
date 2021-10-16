from django.contrib import admin

from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'country', 'city', 'street')
    list_filter = ('country',)
    exclude = ('city_slug', 'country_slug')

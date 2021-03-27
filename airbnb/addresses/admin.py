from django.contrib import admin

from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('address_link', 'country', 'city', 'street', 'city_slug')
    list_filter = ('country',)
    exclude = ('city_slug', 'country_slug')

    def address_link(self, obj: Address):
        return f"Address #{obj.id}"
    address_link.short_description = 'address'

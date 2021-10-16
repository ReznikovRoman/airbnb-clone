from django.urls import reverse
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import RealtyHost


@admin.register(RealtyHost)
class RealtyHostAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'host_rating', 'get_account_link')

    def get_account_link(self, obj: RealtyHost):
        return mark_safe(
            f"""<a href="{reverse('admin:accounts_customuser_change', args=(obj.user.id,))}">
            {obj.user.first_name}'s account page</a>"""
        )
    get_account_link.short_description = 'account link'

from django.contrib import admin

from .models import RealtyHost


@admin.register(RealtyHost)
class RealtyHostAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'host_rating')

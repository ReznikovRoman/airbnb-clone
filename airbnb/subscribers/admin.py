from django.contrib import admin
from django.shortcuts import reverse
from django.utils.safestring import mark_safe

from .models import Subscriber


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_user_link',)

    def get_user_link(self, obj: Subscriber):
        return mark_safe(
            f"""<a href="{reverse('admin:accounts_customuser_change', args=(obj.user.id,))}">{obj.user.first_name}'s 
            account</a>"""
        )
    get_user_link.short_description = 'user link'

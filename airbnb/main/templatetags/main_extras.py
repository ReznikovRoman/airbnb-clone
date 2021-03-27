from typing import Optional
import datetime

from django import template
from django.utils import timezone


register = template.Library()


@register.simple_tag(name='current_time')
def get_current_time(format_string: Optional[str] = None) -> datetime.datetime:
    if format_string:
        return timezone.now().strftime(format_string)
    return timezone.now()


@register.filter(name='reverse')
def reverse_string(string: str) -> str:
    return string[::-1]


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """Updates url with optional query parameters"""
    query_params = context['request'].GET.copy()
    query_params.pop('page', None)
    query_params.update(kwargs)
    return query_params.urlencode()

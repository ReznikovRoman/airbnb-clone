from django import template
from django.conf import settings

from ..services import get_target_image_url_with_size


register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs) -> str:
    """Update url with optional query parameters."""
    query_params = context['request'].GET.copy()
    query_params.pop('page', None)
    query_params.update(kwargs)
    return query_params.urlencode()


@register.filter(name='has_group')
def has_group(user: settings.AUTH_USER_MODEL, group_name: str) -> bool:
    """Check whether user has the given group or not."""
    return user.groups.filter(name=group_name).exists()


@register.filter(name='image_size')
def image_size(image_url: str, target_size: str) -> str:
    """Return image url with specified size - `target_size`."""
    return get_target_image_url_with_size(image_url=image_url, target_size=target_size)

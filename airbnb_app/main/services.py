from django.conf import settings
from django.db.models import QuerySet

from realty.models import Realty

from .constants import TARGET_IMAGE_SIZE_SEPARATOR


def get_all_realty_cities() -> QuerySet[str]:
    return Realty.available.order_by().values_list('location__city', flat=True).distinct()


def get_target_image_url_with_size(*, image_url: str, target_size: str) -> str:
    """Build url with specific size.

    Args:
        image_url (str): initial image url (e.g., /path/to/image.png).
        target_size (str): target size in special format: <`width`x`height`> (e.g., 300x300).

    Returns:
        str: target url with image size (e.g., /path/to/300x300/image.png).
    """
    if not settings.USE_S3_BUCKET:
        return image_url

    image_prefix, image_filename = image_url.rsplit("/", 1)
    try:
        _, _ = list(map(int, target_size.split(TARGET_IMAGE_SIZE_SEPARATOR)))
    except ValueError:
        return image_url
    image_prefix = image_prefix.replace(settings.MEDIA_URL, settings.RESIZED_MEDIA_URL)
    return f"{image_prefix}/{target_size}/{image_filename}"

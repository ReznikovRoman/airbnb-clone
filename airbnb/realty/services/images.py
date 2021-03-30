from typing import List

from .ordering import ImageOrder
from ..models import RealtyImage, CustomDeleteQueryset


def get_realty_images_by_realty_id(realty_id: int) -> CustomDeleteQueryset:
    return RealtyImage.objects.filter(realty_id=realty_id)


def get_image_by_id(image_id: int) -> CustomDeleteQueryset:
    return RealtyImage.objects.filter(id=image_id)


def update_images_order(new_ordering: List[ImageOrder]) -> None:
    """Update images order with the given ordering"""
    for image_order in new_ordering:
        get_image_by_id(image_order.image_id).update(order=image_order.order)

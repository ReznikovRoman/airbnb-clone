from typing import List, Union

from .order import ImageOrder
from ..models import RealtyImage, CustomDeleteQueryset


def get_images_by_realty_id(realty_id: Union[int, str]) -> 'CustomDeleteQueryset[RealtyImage]':
    return RealtyImage.objects.filter(realty_id=realty_id)


def get_image_by_id(image_id: Union[int, str]) -> 'CustomDeleteQueryset[RealtyImage]':
    return RealtyImage.objects.filter(id=image_id)


def update_images_order(new_order: List[ImageOrder]) -> None:
    """Update images order with the given `new_order`."""
    for image_order in new_order:
        get_image_by_id(image_order.image_id).update(order=image_order.order)

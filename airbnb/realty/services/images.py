from ..models import RealtyImage, CustomDeleteQueryset


def get_realty_images_by_realty_id(realty_id: int) -> CustomDeleteQueryset:
    return RealtyImage.objects.filter(realty_id=realty_id)

# realty.services package

## Submodules

## realty.services.images module


### realty.services.images.get_image_by_id(image_id: int)

### realty.services.images.get_images_by_realty_id(realty_id: int)

### realty.services.images.update_images_order(new_ordering: List[realty.services.ordering.ImageOrder])
Update images order with the given ordering.

## realty.services.ordering module


### class realty.services.ordering.ImageOrder(image_id, order)
Bases: `tuple`


#### image_id(: Union[int, str])
Alias for field number 0


#### order(: int)
Alias for field number 1


### realty.services.ordering.convert_response_to_orders(response: List[Tuple[str, int]])
Convert response to list of ImageOrders.

## realty.services.realty module

## Module contents

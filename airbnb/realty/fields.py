from typing import List, Optional

from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class OrderField(models.PositiveSmallIntegerField):
    """Order field

    Attributes:
        related_fields (Optional[List[str]]): fields, with the respect to which the order is calculated
        (e.g. for each Realty object we start image ordering from 0 and each next image has a larger order)
    """
    def __init__(self, related_fields: Optional[List[str]] = None, *args, **kwargs):
        self.related_fields = related_fields
        super(OrderField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        """Return field's value (order) just before saving."""
        if getattr(model_instance, self.attname) is None:  # if the 'order' is not given
            try:
                model_instances = self.model.objects.all()

                if self.related_fields:
                    # get all values of 'related_fields' (e.g. {'realty': '<Realty object>'}
                    related_fields = {field: getattr(model_instance, field) for field in self.related_fields}

                    # get all models instances filtered by the given related fields
                    model_instances = model_instances.filter(**related_fields)

                last_item = model_instances.latest(self.attname)  # trying to get the last item (e.g. RealtyImage)
                order = last_item.order + 1
            except ObjectDoesNotExist:  # if there are no previous items (e.g. RealtyImages)
                order = 0  # start order from 0

            setattr(model_instance, self.attname, order)
            return order
        else:  # 'order' has been passed manually as an argument
            return super(OrderField, self).pre_save(model_instance, add)

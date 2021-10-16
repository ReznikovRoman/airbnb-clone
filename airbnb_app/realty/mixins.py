from django.urls import reverse_lazy

from common.mixins import SessionDataRequiredMixin


class RealtySessionDataRequiredMixin(SessionDataRequiredMixin):
    """Verify that user has entered all the required data to create new Realty."""

    redirect_url = reverse_lazy('realty:new_realty_info')

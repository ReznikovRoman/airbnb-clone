from typing import Optional

from accounts.models import CustomUser

from .models import RealtyHost


def get_host_or_none_by_user(user: CustomUser) -> Optional[RealtyHost]:
    """Returns a RealtyHost object if host with the given `user` exists.Otherwise returns None."""
    return RealtyHost.objects.filter(user=user).first()

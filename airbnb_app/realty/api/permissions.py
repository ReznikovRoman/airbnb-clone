from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request

from accounts.services import has_user_profile_image

from ..models import Realty


class IsRealtyOwnerOrReadOnly(BasePermission):
    """Allow access to Realty owners (Hosts)."""

    def has_object_permission(self, request: Request, view, obj: Realty):
        if request.method in SAFE_METHODS:
            return True
        return obj.host == request.user.host or request.user.is_superuser


class IsAbleToAddRealty(BasePermission):
    """Allow access to Users with a confirmed email and a non-default profile picture."""

    def has_permission(self, request: Request, view):
        if request.method in SAFE_METHODS:
            return True
        can_add_realty = (
                (has_user_profile_image(user_profile=request.user.profile) and request.user.is_email_confirmed) or
                request.user.is_superuser
        )
        return can_add_realty

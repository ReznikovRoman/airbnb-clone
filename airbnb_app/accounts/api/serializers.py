from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


if TYPE_CHECKING:
    from ..models import CustomUser


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user: CustomUser):
        token = super().get_token(user)

        # custom claims
        token['email'] = user.email
        token['isEmailConfirmed'] = user.is_email_confirmed

        return token

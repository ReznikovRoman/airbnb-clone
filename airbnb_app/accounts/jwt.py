from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken


class UserEmailRefreshToken(RefreshToken):

    @classmethod
    def for_user(cls, user):
        """Adds this token to the outstanding token list."""
        token = super().for_user(user)

        # custom claims
        token['email'] = user.email
        token['isEmailConfirmed'] = user.is_email_confirmed

        jti = token[api_settings.JTI_CLAIM]

        OutstandingToken.objects.filter(
            user=user,
            jti=jti,
        ).update(token=str(token))

        return token

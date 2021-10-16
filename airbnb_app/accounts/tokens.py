import six

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user: settings.AUTH_USER_MODEL, timestamp: str):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_email_confirmed)
        )


account_activation_token = AccountActivationTokenGenerator()

from django.conf import settings

from accounts.models import get_default_profile_image_full_url


def has_user_profile_image(user: settings.AUTH_USER_MODEL) -> bool:
    """Check if the User that wants to become a Host has a profile image."""
    if (
            user.profile.profile_image and
            user.profile.profile_image.url != get_default_profile_image_full_url()
    ):
        return True
    return False

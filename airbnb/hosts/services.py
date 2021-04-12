from django.conf import settings


def has_user_required_data_to_become_host(user: settings.AUTH_USER_MODEL) -> bool:
    """Check if user that wants to become a host has a profile image and a confirmed email address."""
    if user.profile.profile_image.exists() and user.is_email_confirmed:
        return True
    return False

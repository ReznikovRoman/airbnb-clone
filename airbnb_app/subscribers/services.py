from django.conf import settings
from django.db.models import QuerySet

from accounts.models import CustomUser

from .models import Subscriber


def get_subscriber_by_email(email: str) -> QuerySet[Subscriber]:
    return Subscriber.objects.filter(email=email)


def get_subscriber_by_user(user: settings.AUTH_USER_MODEL) -> QuerySet[Subscriber]:
    return Subscriber.objects.filter(user=user)


def set_user_for_subscriber(user: CustomUser) -> bool:
    """Update user field in the Subscriber object if there is subscriber with <user.email> email."""
    subscriber_qs = get_subscriber_by_email(user.email)
    if subscriber_qs.exists():
        return subscriber_qs.update(user=user)
    return False


def update_email_for_subscriber_by_user(user: CustomUser) -> bool:
    """Update subscriber's email if User has changed an email, but there was subscriber with 'previous' email.

    E.g. user has subscribed to the newsletter with email <first@email.com>,
    then he has changed his email to <second@email.com>, now Subscriber's email is <second@gmail.com>
    """
    subscriber_qs = get_subscriber_by_email(user.email_tracker.previous('email'))
    if subscriber_qs.exists():
        return subscriber_qs.update(email=user.email)
    return False

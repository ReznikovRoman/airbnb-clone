from typing import Union

from django.conf import settings
from django.db.models import QuerySet
from django.template.loader import get_template, render_to_string

from accounts.models import CustomUser
from mailings.services import send_email_with_attachments
from realty.models import Realty

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


def send_recommendation_email_to_subscriber(
        *,
        site_domain: str,
        subscriber_id: Union[int, str],
        realty_recommendations: QuerySet[Realty],
) -> None:
    """Sends a promo email about new realty (`realty_recommendations`) to the `subscriber_id` Subscriber."""
    protocol = settings.DEFAULT_PROTOCOL
    subject = 'Check out new realty'
    subscriber = Subscriber.objects.get(id=subscriber_id)
    text_content = render_to_string(
        template_name='subscribers/promo/new_realty.html',
        context={
            'subscriber': subscriber,
            'realty_list': realty_recommendations,
            'protocol': protocol,
            'domain': site_domain,
        },
    )
    html = get_template(template_name='subscribers/promo/new_realty.html')
    html_content = html.render(
        context={
            'subscriber': subscriber,
            'realty_list': realty_recommendations,
            'protocol': protocol,
            'domain': site_domain,
        },
    )
    send_email_with_attachments(
        subject=subject,
        body=text_content,
        email_to=[subscriber.email],
        alternatives=[(html_content, 'text/html')],
    )

from typing import Optional

from django.conf import settings
from django.db.models import QuerySet
from django.template.loader import render_to_string, get_template
from django.contrib.sites.models import Site

from mailings.services import send_email_with_attachments
from realty.models import Realty
from realty.services.realty import get_latest_realty
from accounts.models import CustomUser
from .models import Subscriber


def get_subscriber_by_email(email: str) -> QuerySet[Subscriber]:
    return Subscriber.objects.filter(email=email)


def get_subscriber_by_user(user: settings.AUTH_USER_MODEL) -> QuerySet[Subscriber]:
    return Subscriber.objects.filter(user=user)


def set_user_for_subscriber(user: CustomUser) -> None:
    """Update user field in the Subscriber object if there is subscriber with <user.email> email."""
    subscriber_qs = get_subscriber_by_email(user.email)
    if subscriber_qs.exists():
        subscriber_qs.update(user=user)


def update_email_for_subscriber_by_user(user: CustomUser) -> None:
    """Update subscriber's email if User has changed an email, but there was subscriber with 'previous' email.

    E.g. user has subscribed to the newsletter with email <first@email.com>,
    then he has changed his email to <second@email.com>, now Subscriber's email is <second@gmail.com>
    """
    subscriber_qs = get_subscriber_by_email(user.email_tracker.previous('email'))
    if subscriber_qs.exists():
        subscriber_qs.update(email=user.email)


def email_subscribers(latest_realty: Optional[Realty] = None) -> None:
    """Send promo email about new Realty to all Subscribers."""
    if latest_realty is None:
        latest_realty = get_latest_realty()

    domain = Site.objects.get_current().domain
    protocol = settings.DEFAULT_PROTOCOL
    subject = 'Check out new realty'

    for subscriber in Subscriber.objects.all():
        text_content = render_to_string(
            template_name='subscribers/promo/new_realty.html',
            context={
                'subscriber': subscriber,
                'realty': latest_realty,
                'protocol': protocol,
                'domain': domain,
            }
        )

        html = get_template(template_name='subscribers/promo/new_realty.html')
        html_content = html.render(
            context={
                'subscriber': subscriber,
                'realty': latest_realty,
                'protocol': protocol,
                'domain': domain,
            }
        )

        # TODO: Use Celery to send emails (another milestone)
        send_email_with_attachments(
            subject,
            text_content,
            email_to=[subscriber.email],
            alternatives=[(html_content, 'text/html')]
        )

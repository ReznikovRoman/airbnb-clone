from typing import Optional

from celery import shared_task

from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loader import get_template, render_to_string

from mailings.tasks import send_email_with_attachments
from realty.services.realty import get_n_latest_available_realty

from .models import Subscriber


@shared_task
def email_subscribers_about_latest_realty(latest_realty_count: Optional[int] = 3) -> None:
    """Send promo email about new Realty to all Subscribers."""
    latest_realty = get_n_latest_available_realty(realty_count=latest_realty_count)

    domain = Site.objects.get_current().domain
    protocol = settings.DEFAULT_PROTOCOL
    subject = 'Check out new realty'

    for subscriber in Subscriber.objects.all():
        text_content = render_to_string(
            template_name='subscribers/promo/new_realty.html',
            context={
                'subscriber': subscriber,
                'realty_list': latest_realty,
                'protocol': protocol,
                'domain': domain,
            },
        )

        html = get_template(template_name='subscribers/promo/new_realty.html')
        html_content = html.render(
            context={
                'subscriber': subscriber,
                'realty_list': latest_realty,
                'protocol': protocol,
                'domain': domain,
            },
        )

        send_email_with_attachments.delay(
            subject,
            text_content,
            email_to=[subscriber.email],
            alternatives=[(html_content, 'text/html')],
        )

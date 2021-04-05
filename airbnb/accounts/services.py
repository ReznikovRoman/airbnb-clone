from typing import List

from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string, get_template
from django.contrib.auth.models import User


def send_email_to_user(subject: str, message: str, email_to: List[str], email_from: str = None, fail_silently=False):
    return send_mail(
        subject,
        message,
        email_from,
        email_to,
        fail_silently,
    )


def send_email_with_attachments(subject: str, body: str, email_to: List[str], email_from: str = None,
                                alternatives=None) -> None:
    """Send email with optional alternatives (html files, pdf, etc.)."""
    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=email_from,
        to=email_to,
    )

    if alternatives:
        for alternative_content, alternative_type in alternatives:
            email.attach_alternative(alternative_content, alternative_type)

    email.send()


def send_greeting_email(request: HttpRequest, user: User) -> None:
    """Send greeting email to the given user."""
    current_site = get_current_site(request)
    subject = 'Thanks for signing up'

    text_content = render_to_string(
        template_name='accounts/emails/greeting_email.html',
        context={
            'protocol': request.scheme,
            'domain': current_site.domain,
        }
    )

    html = get_template(template_name='accounts/emails/greeting_email.html')
    html_content = html.render(
        context={
            'protocol': request.scheme,
            'domain': current_site.domain,
        }
    )
    send_email_with_attachments(
        subject,
        text_content,
        email_to=[user.email],
        alternatives=[(html_content, 'text/html')]
    )

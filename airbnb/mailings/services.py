from typing import List

from django.core.mail import EmailMultiAlternatives, send_mail


def _send_email_to_user(subject: str, message: str, email_to: List[str], email_from: str = None, fail_silently=False):
    return send_mail(
        subject,
        message,
        email_from,
        email_to,
        fail_silently,
    )


def _send_email_with_attachments(subject: str, body: str, email_to: List[str], email_from: str = None,
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

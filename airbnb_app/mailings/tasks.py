from typing import List, Optional, Any

from celery import shared_task

from .services import _send_email_with_attachments, _send_email_to_user


@shared_task
def send_email_to_user(
        subject: str,
        message: str,
        email_to: List[str],
        email_from: Optional[str] = None,
        fail_silently: bool = False,
) -> None:
    _send_email_to_user(
        subject=subject,
        message=message,
        email_to=email_to,
        email_from=email_from,
        fail_silently=fail_silently,
    )


@shared_task
def send_email_with_attachments(
        subject: str,
        body: str,
        email_to: List[str],
        email_from: Optional[str] = None,
        alternatives: Optional[List[Any]] = None,
) -> None:
    _send_email_with_attachments(
        subject=subject,
        body=body,
        email_to=email_to,
        email_from=email_from,
        alternatives=alternatives,
    )

from django.conf import settings
from django.http import HttpRequest
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string, get_template
from django.contrib.auth.models import Group
from django.contrib.sites.shortcuts import get_current_site

from mailings.services import send_email_with_attachments
from .models import CustomUser
from .tokens import account_activation_token


def send_greeting_email(request: HttpRequest, user: CustomUser) -> None:
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


def send_verification_link(request: HttpRequest, user: settings.AUTH_USER_MODEL) -> None:
    """Send email verification link."""
    current_site = get_current_site(request)
    subject = 'Activate your account'

    text_content = render_to_string(
        template_name='accounts/registration/account_activation_email.html',
        context={
            'user': user,
            'protocol': request.scheme,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        }
    )

    html = get_template(template_name='accounts/registration/account_activation_email.html')
    html_content = html.render(
        context={
            'user': user,
            'protocol': request.scheme,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        }
    )
    send_email_with_attachments(
        subject,
        text_content,
        email_to=[user.email],
        alternatives=[(html_content, 'text/html')]
    )


def get_user_from_uid(uid) -> CustomUser:
    uid = force_text(urlsafe_base64_decode(force_text(uid)))
    user = CustomUser.objects.get(id=uid)
    return user


def add_user_to_group(user: CustomUser, group_name: str) -> None:
    group = Group.objects.get_or_create(name=group_name)[0]
    user.groups.add(group)

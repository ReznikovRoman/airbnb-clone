import random

from django.conf import settings
from django.http import HttpRequest
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string, get_template
from django.contrib.auth.models import Group
from django.contrib.sites.shortcuts import get_current_site

from common.tasks import send_sms_by_twilio
from mailings.tasks import send_email_with_attachments
from .models import CustomUser, Profile, SMSLog
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
    send_email_with_attachments.delay(
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
    send_email_with_attachments.delay(
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


def generate_random_sms_code() -> str:
    """Generates random 4 digits code (0000-9999)."""
    return str(random.randint(0, 9999)).zfill(4)


def handle_phone_number_change(user_profile: Profile, site_domain: str, new_phone_number: str) -> None:
    """Handles phone number change.
    - Gets or creates a SMSLog object for the given `user_profile`
    - Generates random verification code and saves it to the SMSLog object
    - Sends verification code to the user's new phone number (celery task)

    Args:
        user_profile (Profile): Profile of current user
        site_domain (str): Current site domain (e.g., airbnb, localhost, etc.)
        new_phone_number (str): User's new phone number

    Returns:
        None
    """
    sms_log = SMSLog.objects.get_or_create(profile=user_profile)[0]

    sms_verification_code = generate_random_sms_code()
    sms_log.sms_code = sms_verification_code
    sms_log.save()

    send_sms_by_twilio.delay(
        body=f"Your {site_domain} verification code is: {sms_verification_code}",
        sms_from=settings.TWILIO_PHONE_NUMBER,
        sms_to=new_phone_number,
    )

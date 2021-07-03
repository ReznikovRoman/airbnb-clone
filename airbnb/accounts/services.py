import random
from typing import Dict, Union, Optional

from django.conf import settings
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string, get_template
from django.contrib.auth.models import Group

from common.tasks import send_sms_by_twilio
from mailings.tasks import send_email_with_attachments
from common.services import is_cooldown_ended, set_key_with_timeout
from common.constants import VERIFICATION_CODE_STATUS_FAILED, VERIFICATION_CODE_STATUS_DELIVERED
from configs.redis_conf import r
from common.collections import TwilioShortPayload
from .models import (CustomUser, CustomUserManager, Profile, SMSLog,
                     get_default_profile_image_full_url, get_default_profile_image)
from .tokens import account_activation_token


def send_greeting_email(domain: str, scheme: str, user: CustomUser) -> None:
    """Send greeting email to the given user."""
    subject = 'Thanks for signing up'

    text_content = render_to_string(
        template_name='accounts/emails/greeting_email.html',
        context={
            'protocol': scheme,
            'domain': domain,
        }
    )

    html = get_template(template_name='accounts/emails/greeting_email.html')
    html_content = html.render(
        context={
            'protocol': scheme,
            'domain': domain,
        }
    )
    send_email_with_attachments.delay(
        subject,
        text_content,
        email_to=[user.email],
        alternatives=[(html_content, 'text/html')]
    )


def send_verification_link(domain: str, scheme: str, user: CustomUser) -> None:
    """Send email verification link."""
    user_id = user.pk
    email_sent_key = f"accounts:user:{user_id}:email.sent"
    if not is_cooldown_ended(email_sent_key):
        return

    set_key_with_timeout(email_sent_key, 60, 1)

    subject = 'Activate your account'
    text_content = render_to_string(
        template_name='accounts/registration/account_activation_email.html',
        context={
            'user': user,
            'protocol': scheme,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user_id)),
            'token': account_activation_token.make_token(user),
        }
    )
    html = get_template(template_name='accounts/registration/account_activation_email.html')
    html_content = html.render(
        context={
            'user': user,
            'protocol': scheme,
            'domain': domain,
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


def get_user_by_pk(pk: Union[int, str]) -> Optional[CustomUser]:
    return get_object_or_404(CustomUser, pk=pk)


def get_user_by_email(email: str) -> QuerySet[CustomUser]:
    return CustomUser.objects.filter(email=CustomUserManager.normalize_email(email))


def get_user_from_uid(uid: str) -> CustomUser:
    uid = force_text(urlsafe_base64_decode(force_text(uid)))
    user: CustomUser = CustomUser.objects.get(id=uid)
    return user


def add_user_to_group(user: CustomUser, group_name: str) -> None:
    group = Group.objects.get_or_create(name=group_name)[0]
    user.groups.add(group)


def has_user_profile_image(user_profile: Profile) -> bool:
    """Check that User has a profile image and it is not a default one."""
    if (
            user_profile.profile_image and
            user_profile.profile_image.url != get_default_profile_image_full_url() and
            user_profile.profile_image.url != get_default_profile_image()
    ):
        return True
    return False


def generate_random_sms_code() -> str:
    """Generates random 4 digits code (0000-9999)."""
    return str(random.randint(0, 9999)).zfill(4)


def update_phone_number_confirmation_status(user_profile: Profile, is_phone_number_confirmed: bool) -> None:
    user_profile.is_phone_number_confirmed = is_phone_number_confirmed
    user_profile.save(update_fields=["is_phone_number_confirmed"])


def update_user_email_confirmation_status(user: CustomUser, is_email_confirmed: bool) -> None:
    user.is_email_confirmed = is_email_confirmed
    user.save(update_fields=["is_email_confirmed"])


def handle_phone_number_change(user_profile: Profile, site_domain: str, new_phone_number: str) -> TwilioShortPayload:
    """Handles phone number change.
    - Gets or creates a SMSLog object for the given `user_profile`
    - Generates random verification code and saves it to the SMSLog object
    - Sets `profile.is_phone_number_confirmed` to False
    - Sends verification code to the user's new phone number (celery task)

    Args:
        user_profile (Profile): Profile of current user
        site_domain (str): Current site domain (e.g., airbnb, localhost, etc.)
        new_phone_number (str): User's new phone number

    Returns:
        TwilioShortPayload: Twilio payload
    """
    sms_log = SMSLog.objects.get_or_create(profile=user_profile)[0]

    sms_verification_code = generate_random_sms_code()
    sms_log.sms_code = sms_verification_code
    sms_log.save(update_fields=["sms_code"])

    update_phone_number_confirmation_status(user_profile, is_phone_number_confirmed=False)

    return TwilioShortPayload.parse_raw(send_sms_by_twilio.delay(
        body=f"Your {site_domain} verification code is: {sms_verification_code}",
        sms_from=settings.TWILIO_PHONE_NUMBER,
        sms_to=new_phone_number,
    ).get())


def get_verification_code_from_digits_dict(digits_dict: Dict[str, str]) -> str:
    """Converts dict of digits ({'key': 'digit', ...}) to a verification code."""
    return ''.join([str(digit) for digit in digits_dict.values()])


def is_verification_code_for_profile_valid(user_profile: Profile, verification_code: str) -> bool:
    valid_verification_code = get_object_or_404(SMSLog, profile=user_profile).sms_code
    if valid_verification_code == verification_code:
        return True
    return False


def set_phone_code_status_by_user_id(
        user_id: Union[int, str],
        phone_code_status: Union[VERIFICATION_CODE_STATUS_FAILED, VERIFICATION_CODE_STATUS_DELIVERED]
) -> bool:
    key = f"user:{user_id}:phone_code_status"
    return r.set(key, phone_code_status)


def get_phone_code_status_by_user_id(
        user_id: Union[int, str]
) -> Union[VERIFICATION_CODE_STATUS_FAILED, VERIFICATION_CODE_STATUS_DELIVERED, None]:
    key = f"user:{user_id}:phone_code_status"
    return r.get(key)

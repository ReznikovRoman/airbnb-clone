import random
from typing import Dict, Optional, Union

from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.template.loader import get_template, render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from common.collections import TwilioShortPayload
from common.constants import (
    VERIFICATION_CODE_STATUS_COOLDOWN, VERIFICATION_CODE_STATUS_DELIVERED, VERIFICATION_CODE_STATUS_FAILED,
)
from common.services import is_cooldown_ended, set_key_with_timeout
from common.tasks import send_sms_by_twilio
from configs.redis_conf import redis_instance
from mailings.services import send_email_with_attachments

from .jwt import UserEmailRefreshToken
from .models import (
    CustomUser, CustomUserManager, Profile, SMSLog, get_default_profile_image, get_default_profile_image_full_url,
)
from .tasks import send_email_verification_code
from .tokens import account_activation_token


def _send_password_reset_email(
        *,
        subject_template_name: str,
        email_template_name: str,
        context: dict,
        from_email: str,
        to_email: str,
        html_email_template_name: Optional[str] = None,
) -> None:
    subject = render_to_string(subject_template_name, context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = render_to_string(email_template_name, context)

    html = get_template(html_email_template_name)
    html_content = html.render(context)

    send_email_with_attachments(
        subject=subject,
        body=body,
        email_to=[to_email],
        email_from=from_email,
        alternatives=[(html_content, 'text/html')],
    )


def send_verification_email(*, domain: str, scheme: str, user_id: Union[int, str]) -> None:
    user = CustomUser.objects.get(pk=user_id)
    subject = 'Activate your account'
    text_content = render_to_string(
        template_name='accounts/registration/account_activation_email.html',
        context={
            'user': user,
            'protocol': scheme,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user_id)),
            'token': account_activation_token.make_token(user),
        },
    )
    html = get_template(template_name='accounts/registration/account_activation_email.html')
    html_content = html.render(
        context={
            'user': user,
            'protocol': scheme,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user_id)),
            'token': account_activation_token.make_token(user),
        },
    )
    send_email_with_attachments(
        subject=subject,
        body=text_content,
        email_to=[user.email],
        alternatives=[(html_content, 'text/html')],
    )


def send_verification_link(domain: str, scheme: str, user: CustomUser) -> None:
    """Send email verification link."""
    user_id = user.pk
    email_sent_key = f"accounts:user:{user_id}:email.sent"
    if not is_cooldown_ended(email_sent_key):
        return
    set_key_with_timeout(email_sent_key, 60, 1)

    send_email_verification_code.delay(domain=domain, scheme=scheme, user_id=user_id)


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


def update_user_email_confirmation_status(user: CustomUser, is_email_confirmed: bool) -> CustomUser:
    user.is_email_confirmed = is_email_confirmed
    user.save(update_fields=["is_email_confirmed"])
    return user


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
    phone_number_digits = ''.join(char for char in new_phone_number if char.isdigit())
    sms_sent_key = f"phone:{phone_number_digits}:sms.sent"
    if not is_cooldown_ended(sms_sent_key):
        return TwilioShortPayload(status=VERIFICATION_CODE_STATUS_COOLDOWN, sid=None)
    set_key_with_timeout(sms_sent_key, 60, 1)

    sms_verification_code = generate_random_sms_code()
    sms_log = SMSLog.objects.get_or_create(profile=user_profile)[0]
    sms_log.sms_code = sms_verification_code
    sms_log.save(update_fields=["sms_code"])

    update_phone_number_confirmation_status(user_profile, is_phone_number_confirmed=False)

    # FIXME: do not use AsyncResult here
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
        phone_code_status: Union[VERIFICATION_CODE_STATUS_FAILED, VERIFICATION_CODE_STATUS_DELIVERED],
) -> bool:
    key = f"user:{user_id}:phone_code_status"
    return redis_instance.set(key, phone_code_status)


def get_phone_code_status_by_user_id(
        user_id: Union[int, str],
) -> Union[VERIFICATION_CODE_STATUS_FAILED, VERIFICATION_CODE_STATUS_DELIVERED, None]:
    key = f"user:{user_id}:phone_code_status"
    return redis_instance.get(key)


def create_jwt_token_for_user_with_additional_fields(*, user: CustomUser) -> dict[str, str]:
    refresh = UserEmailRefreshToken.for_user(user=user)
    return refresh

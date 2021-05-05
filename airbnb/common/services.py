import logging
from typing import List

from twilio.base.exceptions import TwilioRestException

from configs.twilio_conf import twilio_client
from .types import AbstractForm
from .constants import VERIFICATION_CODE_STATUS_FAILED
from .collections import FormWithModel, TwilioShortPayload


logger = logging.getLogger(__name__)


def get_field_names_from_form(form: AbstractForm) -> List[str]:
    return list(form.base_fields.keys())


def create_name_with_prefix(name: str, prefix: str) -> str:
    prefix = f"{prefix}_" if not prefix.endswith('_') else prefix
    return f"{prefix}{name}" if not name.startswith(prefix) else name


def get_required_fields_from_form_with_model(forms_with_models: List[FormWithModel]) -> List[str]:
    """Return all required fields (fields that cannot be blank) from form and linked model."""
    required_fields: List[str] = []
    for form_with_model in forms_with_models:
        required_fields.extend([field for field in form_with_model.form.base_fields
                                if not form_with_model.model._meta.get_field(field).blank])
    return required_fields


def get_keys_with_prefixes(names: List[str], prefix: str = '') -> List[str]:
    return [create_name_with_prefix(name, prefix) for name in names]


def _send_sms_by_twilio(body: str, sms_from: str, sms_to: str) -> TwilioShortPayload:
    """Sends SMS message using Twilio provider.

    Args:
        body (str): SMS message text
        sms_from (str): Twilio phone number
        sms_to (str): Recipient's phone number

    Returns:
        TwilioShortPayload: Twilio payload
    """
    try:
        logger.info(
            msg=f"Sending phone number verification message: | "
                f"Body: {body} | "
                f"To: {sms_to} | "
                f"From {sms_from}"
        )
        message = twilio_client.messages.create(
            body=body,
            from_=sms_from,
            to=sms_to,
        )
    except TwilioRestException as twilio_exception:
        logger.error(
            msg=f"ERROR: SMS wasn't send | "
                f"To: {sms_to} | "
                f"Twilio exception message: {twilio_exception}"
        )
        return TwilioShortPayload(status=VERIFICATION_CODE_STATUS_FAILED, sid=None)
    else:
        logger.info(
            msg=f"Verification message has been sent successfully | "
                f"To: {sms_to} |"
                f"Twilio SID: {message.sid}"
        )
        return TwilioShortPayload(status=message.status, sid=message.sid)

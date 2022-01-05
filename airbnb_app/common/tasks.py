from billiard.exceptions import SoftTimeLimitExceeded
from twilio.base.exceptions import TwilioRestException

from django.utils import timezone

from airbnb.celery import app
from common.services import _send_sms_by_twilio


@app.task(
    name='common.send_sms_by_twilio',
    queue='urgent_notifications',
    time_limit=5,
    soft_time_limit=3,
    default_retry_delay=5,
    autoretry_for=(SoftTimeLimitExceeded, TwilioRestException),
    expires=timezone.now() + timezone.timedelta(hours=12),
)
def send_sms_by_twilio(body: str, sms_from: str, sms_to: str, *args, **kwargs) -> None:
    _send_sms_by_twilio(
        body=body,
        sms_from=sms_from,
        sms_to=sms_to,
    )

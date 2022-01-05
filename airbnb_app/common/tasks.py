from airbnb.celery import app
from common.services import _send_sms_by_twilio


@app.task(name='common.send_sms_by_twilio', queue='urgent_notifications')
def send_sms_by_twilio(body: str, sms_from: str, sms_to: str, *args, **kwargs) -> None:
    _send_sms_by_twilio(
        body=body,
        sms_from=sms_from,
        sms_to=sms_to,
    )

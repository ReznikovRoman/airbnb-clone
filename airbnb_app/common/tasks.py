from airbnb.celery import app
from common.services import _send_sms_by_twilio


@app.task(name='common.send_sms_by_twilio')
def send_sms_by_twilio(body: str, sms_from: str, sms_to: str):
    twilio_payload = _send_sms_by_twilio(
        body=body,
        sms_from=sms_from,
        sms_to=sms_to,
    )
    return twilio_payload.json()

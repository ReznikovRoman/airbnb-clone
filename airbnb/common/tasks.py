from airbnb.celery import app
from conf.twilio import twilio_client


@app.task(name='common.send_sms_by_twilio')
def send_sms_by_twilio(body: str, sms_from: str, sms_to: str):
    message = twilio_client.messages.create(
        body=body,
        from_=sms_from,
        to=sms_to,
    )
    return message.sid

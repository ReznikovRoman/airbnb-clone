from airbnb.celery import app
from configs.twilio_conf import twilio_client


@app.task(name='common.send_sms_by_twilio')
def send_sms_by_twilio(body: str, sms_from: str, sms_to: str):
    """Sends SMS message using Twilio provider

    Args:
        body (str): SMS message text
        sms_from (str): Twilio phone number
        sms_to (str): Recipient's phone number

    Returns:
        dict: Twilio message SID
    """
    message = twilio_client.messages.create(
        body=body,
        from_=sms_from,
        to=sms_to,
    )
    return message.sid

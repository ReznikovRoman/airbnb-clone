from django.dispatch import receiver
from django.db.models.signals import post_save

from subscribers.services import email_subscribers
from .models import Realty


@receiver(post_save, sender=Realty)
def email_subscribers_about_new_realty(sender, instance: Realty, created: bool, **kwargs):
    # TODO: Send notification only after Host 'publishes' his Realty (listings dashboard)
    if created:
        email_subscribers(latest_realty=instance)

from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

from subscribers.services import set_user_for_subscriber, update_email_for_subscriber_by_user
from .models import Profile
from .services import add_user_to_group


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def handle_user_sign_up(sender, instance: settings.AUTH_USER_MODEL, created, **kwargs):
    if created:
        add_user_to_group(instance, 'common_users')
        set_user_for_subscriber(instance)

        if not kwargs.get('raw', False):
            Profile.objects.create(user=instance)
            instance.save()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_profile(sender, instance: settings.AUTH_USER_MODEL, created, **kwargs):
    if not created:
        update_email_for_subscriber_by_user(user=instance)
        instance.profile.save()

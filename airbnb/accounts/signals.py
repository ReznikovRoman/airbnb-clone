from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.db.models.signals import post_save

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def add_user_to_group(sender, instance, created, **kwargs):
    if created:
        common_users_group = Group.objects.get_or_create(name='common_users')[0]
        instance.groups.add(common_users_group)
        instance.save()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created and not kwargs.get('raw', False):
        Profile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_profile(sender, instance, created, **kwargs):
    if not created:
        instance.profile.save()

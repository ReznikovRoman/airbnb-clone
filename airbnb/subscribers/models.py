from django.db import models
from django.conf import settings


class Subscriber(models.Model):
    """Subscriber that receives email notifications about new realty."""
    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL,
        verbose_name='subscriber',
        related_name='subscriber',
        on_delete=models.CASCADE,
    )

    # TODO: Add json field to filter realty (Postgres - JSON field, another milestone)

    def __str__(self):
        return f"Subscriber: {self.user.full_name}"

from django.db import models
from django.conf import settings


class Subscriber(models.Model):
    """Subscriber that receives email notifications about new realty."""
    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL,
        verbose_name='subscriber',
        related_name='subscriber',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    email = models.EmailField(unique=True)

    # TODO: Add json field to filter realty (Postgres - JSON field, another milestone)

    class Meta:
        verbose_name = 'subscriber'
        verbose_name_plural = 'subscribers'

    def __str__(self):
        return f"Subscriber: {self.email}"

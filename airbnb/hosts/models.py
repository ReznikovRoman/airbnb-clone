from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import Group


class RealtyHost(models.Model):
    """Realty host."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='host',
    )
    host_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='rating',
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5),
        ]
    )

    class Meta:
        verbose_name = 'realty host'
        verbose_name_plural = 'realty hosts'

    def __str__(self):
        return f"Host: {self.user.first_name} {self.user.last_name}"

    def save(self, *args, **kwargs):
        hosts_group = Group.objects.get_or_create(name='hosts')[0]
        self.user.groups.add(hosts_group)
        super(RealtyHost, self).save(*args, **kwargs)

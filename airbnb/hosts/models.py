from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class RealtyHost(models.Model):
    """Realty host"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(verbose_name='host description')
    host_rating = models.PositiveSmallIntegerField(
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
        # TODO: fields from CustomUser model (another milestone)
        return f"Host: {self.user.first_name} {self.user.last_name}"

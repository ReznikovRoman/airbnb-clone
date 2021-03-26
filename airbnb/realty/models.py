from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from addresses.models import Address
from hosts.models import RealtyHost


class Amenity(models.Model):
    """Realty amenity"""
    name = models.CharField(verbose_name='name', max_length=100)

    class Meta:
        verbose_name = 'amenity'
        verbose_name_plural = 'amenities'

    def __str__(self):
        return self.name


class Realty(models.Model):
    """Realty in an online marketplace (airbnb)"""
    HOUSE = 'House'
    HOTEL = 'Hotel'
    APARTMENTS = 'Apartments'
    REALTY_CHOICES = (
        (HOUSE, 'House'),
        (HOTEL, 'Hotel Room'),
        (APARTMENTS, 'Apartments'),
    )

    name = models.CharField(verbose_name="title", max_length=255)
    slug = models.SlugField(verbose_name="slug", max_length=255)
    description = models.TextField(verbose_name="description")
    is_available = models.BooleanField(default=True)
    created = models.DateTimeField(verbose_name="creation date", auto_now_add=True)
    updated = models.DateTimeField(verbose_name="update date", auto_now=True)
    realty_type = models.CharField(
        verbose_name="type of the realty",
        max_length=31,
        choices=REALTY_CHOICES,
        default=APARTMENTS,
    )
    beds_count = models.PositiveSmallIntegerField(
        verbose_name='beds count',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(8),
        ]
    )
    max_guests_count = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
        ]
    )
    price_per_night = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
        ]
    )
    location = models.OneToOneField(Address, on_delete=models.CASCADE, verbose_name='location')
    host = models.ForeignKey(RealtyHost, on_delete=models.CASCADE, related_name='realty', verbose_name='realty host')
    amenities = models.ManyToManyField(Amenity, related_name='realty', blank=True, verbose_name='amenities')

    class Meta:
        verbose_name = 'realty'
        verbose_name_plural = 'realty'
        ordering = ('-created',)

    def __str__(self):
        return self.name


def get_realty_image_upload_path(instance: "RealtyImage", filename: str):
    return f"upload/images/realty/{instance.realty.id}/{filename}"


class RealtyImage(models.Model):
    """Image of a realty"""
    image = models.ImageField(upload_to=get_realty_image_upload_path, verbose_name='image')
    realty = models.ForeignKey(
        Realty,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='realty',
    )
    # TODO: order - custom model field (another milestone)

    class Meta:
        verbose_name = 'Realty image'
        verbose_name_plural = 'Realty images'

    def __str__(self):
        return f"Image #{self.id} for {self.realty.name}"

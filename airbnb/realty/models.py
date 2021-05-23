from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

from hosts.models import RealtyHost
from addresses.models import Address
from .fields import OrderField


class Amenity(models.Model):
    """Realty amenity."""
    name = models.CharField(verbose_name='name', max_length=100)

    class Meta:
        verbose_name = 'amenity'
        verbose_name_plural = 'amenities'

    def __str__(self):
        return self.name


class CustomDeleteQueryset(models.query.QuerySet):
    def delete(self):
        # have to call .delete() method when deleting a Realty queryset (e.g. on the Admin panel)
        for obj in self:
            obj.delete()


class RealtyManager(models.Manager):
    def get_queryset(self):
        return CustomDeleteQueryset(self.model, using=self._db)


class AvailableRealtyManager(models.Manager):
    """Manager for all realty that is available."""
    def get_queryset(self):
        base_qs = super(AvailableRealtyManager, self).get_queryset()
        return base_qs.filter(is_available=True)


class RealtyTypeChoices(models.TextChoices):
    HOUSE = 'House', 'House'
    HOTEL = 'Hotel', 'Hotel'
    APARTMENTS = 'Apartments', 'Apartments'


class Realty(models.Model):
    """Realty in an online marketplace (airbnb)."""
    name = models.CharField(verbose_name="name", max_length=255)
    slug = models.SlugField(verbose_name="slug", max_length=255)
    description = models.TextField(verbose_name="description")
    is_available = models.BooleanField(verbose_name='is realty available', default=False)
    created = models.DateTimeField(verbose_name="creation date", auto_now_add=True)
    updated = models.DateTimeField(verbose_name="update date", auto_now=True)
    realty_type = models.CharField(
        verbose_name="type of the realty",
        max_length=31,
        choices=RealtyTypeChoices.choices,
        default=RealtyTypeChoices.APARTMENTS,
    )
    beds_count = models.PositiveSmallIntegerField(
        verbose_name='beds count',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(8),
        ]
    )
    max_guests_count = models.PositiveSmallIntegerField(
        verbose_name='maximum guests amount',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
        ]
    )
    price_per_night = models.PositiveSmallIntegerField(
        verbose_name='price per night',
        validators=[
            MinValueValidator(1),
        ]
    )
    location = models.OneToOneField(Address, on_delete=models.CASCADE, verbose_name='location')
    host = models.ForeignKey(RealtyHost, on_delete=models.CASCADE, related_name='realty', verbose_name='realty host')
    amenities = models.ManyToManyField(Amenity, related_name='realty', blank=True, verbose_name='amenities')

    objects = RealtyManager()
    available = AvailableRealtyManager()

    class Meta:
        verbose_name = 'realty'
        verbose_name_plural = 'realty'
        ordering = ('-created',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Realty, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('realty:detail', kwargs={"pk": self.id, "slug": self.slug})

    def delete(self, using=None, keep_parents=False):
        self.location.delete()
        super(Realty, self).delete(using, keep_parents)


class RealtyView(models.Model):
    """Postgres View"""
    id = models.PositiveBigIntegerField(primary_key=True)
    name = models.CharField(verbose_name="name", max_length=255)
    description = models.TextField(verbose_name="description")
    is_available = models.BooleanField(verbose_name='is realty available', default=False)
    realty_type = models.CharField(
        verbose_name="type of the realty",
        max_length=31,
        choices=RealtyTypeChoices.choices,
        default=RealtyTypeChoices.APARTMENTS,
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

    country = models.CharField(verbose_name='location country', max_length=255)
    city = models.CharField(verbose_name='location city', max_length=255)
    street = models.CharField(verbose_name='location street', max_length=255)

    email = models.EmailField(
        verbose_name='host email',
        max_length=60,
        unique=True,
    )
    first_name = models.CharField(verbose_name='host first name', max_length=40)
    last_name = models.CharField(verbose_name='host last name', max_length=40)

    class Meta:
        managed = False
        db_table = 'realty_view'


RealtyImageModelManager = models.Manager.from_queryset(CustomDeleteQueryset)


def get_realty_image_upload_path(instance: "RealtyImage", filename: str) -> str:
    return f"upload/images/realty/{instance.realty.id}/{filename}"


class RealtyImage(models.Model):
    """Image of a realty."""
    image = models.ImageField(upload_to=get_realty_image_upload_path, verbose_name='image')
    realty = models.ForeignKey(
        Realty,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='realty',
    )
    order = OrderField(blank=True, null=True, related_fields=['realty'])

    objects = RealtyImageModelManager()

    class Meta:
        verbose_name = 'Realty image'
        verbose_name_plural = 'Realty images'
        ordering = ('order',)

    def __str__(self):
        return f"Image #{self.id} for {self.realty.name}"

    def delete(self, using=None, keep_parents=False):
        # get realty images that go after the current one (that will be deleted)
        next_realty_images: CustomDeleteQueryset[RealtyImage] = RealtyImage.objects.\
                                                                      filter(realty=self.realty)[(self.order+1):]

        if next_realty_images.exists():
            for realty_image in next_realty_images:
                realty_image.order -= 1
                realty_image.save()

        super(RealtyImage, self).delete(using, keep_parents)

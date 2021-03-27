from django.db import models
from django.utils.text import slugify


class Address(models.Model):
    """Address"""
    country = models.CharField(verbose_name='country', max_length=255)
    city = models.CharField(verbose_name='city', max_length=255)
    street = models.CharField(verbose_name='street', max_length=255)
    city_slug = models.SlugField(verbose_name='city slug', max_length=255)
    country_slug = models.SlugField(verbose_name='country slug', max_length=255)

    class Meta:
        verbose_name = 'address'
        verbose_name_plural = 'addresses'

    def __str__(self):
        return f"Address #{self.id}"

    def save(self, *args, **kwargs):
        self.city_slug = slugify(self.city)
        self.country_slug = slugify(self.country)
        super(Address, self).save(*args, **kwargs)

    def get_full_address(self):
        return f"{self.country}, {self.city}: {self.street}"

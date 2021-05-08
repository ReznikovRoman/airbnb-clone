# Generated by Django 3.1.7 on 2021-05-03 14:16

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realty', '0006_auto_20210422_1940'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='realty',
            name='amenities',
        ),
        migrations.AddField(
            model_name='realty',
            name='amenities',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100, verbose_name='amenity'), blank=True, null=True, size=16),
        ),
    ]

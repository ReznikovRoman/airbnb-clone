# Generated by Django 3.1.7 on 2021-03-27 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0002_auto_20210327_1754'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='city_slug',
            field=models.SlugField(editable=False, max_length=255, verbose_name='city slug'),
        ),
        migrations.AlterField(
            model_name='address',
            name='country_slug',
            field=models.SlugField(editable=False, max_length=255, verbose_name='country slug'),
        ),
    ]

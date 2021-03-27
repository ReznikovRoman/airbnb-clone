# Generated by Django 3.1.7 on 2021-03-27 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0003_auto_20210327_1827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='city_slug',
            field=models.SlugField(max_length=255, verbose_name='city slug'),
        ),
        migrations.AlterField(
            model_name='address',
            name='country_slug',
            field=models.SlugField(max_length=255, verbose_name='country slug'),
        ),
    ]
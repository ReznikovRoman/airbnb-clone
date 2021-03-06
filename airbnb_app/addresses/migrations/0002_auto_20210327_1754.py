# Generated by Django 3.1.7 on 2021-03-27 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='city_slug',
            field=models.SlugField(default='', editable=False, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='address',
            name='country_slug',
            field=models.SlugField(default='', editable=False, max_length=255),
            preserve_default=False,
        ),
    ]

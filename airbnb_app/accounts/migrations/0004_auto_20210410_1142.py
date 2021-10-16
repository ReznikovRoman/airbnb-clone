# Generated by Django 3.1.7 on 2021-04-10 08:42

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_image',
            field=models.ImageField(blank=True, default=accounts.models.get_default_profile_image, null=True, upload_to=accounts.models.get_profile_image_upload_path, verbose_name='profile image'),
        ),
    ]
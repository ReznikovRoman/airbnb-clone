# Generated by Django 3.1.13 on 2021-10-30 10:31

import common.utils
from django.db import migrations, models
import realty.models


class Migration(migrations.Migration):

    dependencies = [
        ('realty', '0013_realty_visits_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='realtyimage',
            name='image',
            field=models.ImageField(storage=common.utils.select_file_storage, upload_to=realty.models.get_realty_image_upload_path, verbose_name='image'),
        ),
    ]

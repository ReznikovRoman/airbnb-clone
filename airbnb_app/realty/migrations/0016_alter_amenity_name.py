# Generated by Django 3.2.9 on 2021-11-29 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realty', '0015_enable_trigram_extension'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amenity',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='name'),
        ),
    ]

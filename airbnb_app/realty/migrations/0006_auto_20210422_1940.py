# Generated by Django 3.1.7 on 2021-04-22 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realty', '0005_auto_20210330_2314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='realty',
            name='is_available',
            field=models.BooleanField(default=False, verbose_name='is realty available'),
        ),
    ]
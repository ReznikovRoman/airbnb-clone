# Generated by Django 3.1.7 on 2021-04-13 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribers', '0002_auto_20210413_2141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriber',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]

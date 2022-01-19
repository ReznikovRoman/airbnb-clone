import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0006_auto_20210411_2002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='realtyhost',
            name='host_rating',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='host rating'),
        ),
    ]

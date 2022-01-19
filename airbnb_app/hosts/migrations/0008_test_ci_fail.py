from django.contrib.postgres.operations import CryptoExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0007_test_ci_migration'),
    ]

    operations = [
        CryptoExtension(),
    ]

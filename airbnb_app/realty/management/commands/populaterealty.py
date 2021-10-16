from model_bakery import baker

from django.core.management.base import ArgumentParser, BaseCommand

from accounts.models import CustomUser
from hosts.models import RealtyHost


class Command(BaseCommand):
    """Custom management command that creates `realty_count` realty objects."""

    help = "Creates `realty_count` realty objects"

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('realty_count', nargs='+', type=int, help='Indicates how many realty fixtures to create')

    def handle(self, *args, **options):
        realty_count: int = options['realty_count'][0]

        if realty_count < 1:
            raise ValueError("`realty_count` should be greater than or equal to 1")

        try:
            fixture_host = RealtyHost.objects.get(user__email='test_fixture@airbnb.com')
        except RealtyHost.DoesNotExist:
            self.stdout.write(self.style.WARNING("Creating new realty host for realty fixtures..."))

            fixture_user: CustomUser = baker.make(
                'CustomUser',
                email='test_fixture@airbnb.com',
                is_email_confirmed=True,
            )
            fixture_user.profile.profile_image = 'fixture_image.png'
            fixture_user.profile.save()

            fixture_host = RealtyHost.objects.create(user=fixture_user)

        baker.make(
            'Realty',
            _quantity=realty_count,
            host=fixture_host,
        )

        self.stdout.write(self.style.SUCCESS("Successfully created %s realty" % (realty_count,)))

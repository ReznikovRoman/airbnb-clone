from io import StringIO

from model_bakery import baker

from django.test import TestCase
from django.core.management import call_command, color_style, load_command_class

from hosts.models import RealtyHost
from realty.models import Realty
from accounts.models import CustomUser
from realty.management.commands.populaterealty import Command


class PopulateRealtyTests(TestCase):
    def setUp(self) -> None:
        new_user: CustomUser = baker.make(
            'CustomUser',
            email='test_fixture@airbnb.com',
            is_email_confirmed=True,
        )
        new_user.profile.profile_image = 'fixture_image.png'
        new_user.profile.save()

        RealtyHost.objects.create(user=new_user)

    def test_command_help_output(self):
        """Test command help text."""
        expected_help_text = "Creates `realty_count` realty objects"
        command: Command = load_command_class('realty', 'populaterealty')

        self.assertEqual(expected_help_text, command.help)

    def test_command_output_if_host_exists(self):
        """If there is a RealtyHost, command prints info only about creation of new Realty objects."""
        output = StringIO()
        color_styles = color_style(force_color=True)
        expected_output = color_styles.SUCCESS("Successfully created 2 realty")

        call_command('populaterealty', 2, stdout=output)

        self.assertIn(expected_output, output.getvalue())

    def test_command_output_if_host_does_not_exist(self):
        """If there is no RealtyHost yet, command prints info about both the creation of new Host and new Realty."""
        CustomUser.objects.first().delete()

        output = StringIO()
        color_styles = color_style(force_color=True)
        expected_output = f'{color_styles.WARNING("Creating new realty host for realty fixtures...")}\n' \
                          f'{color_styles.SUCCESS("Successfully created 2 realty")}'

        call_command('populaterealty', 2, stdout=output)

        self.assertIn(expected_output, output.getvalue())

    def test_realty_successfully_created_with_existing_host(self):
        """If there is a RealtyHost, `2` realty objects will be created."""
        output = StringIO()
        call_command('populaterealty', 2, stdout=output)

        self.assertEqual(Realty.objects.count(), 2)

    def test_realty_successfully_created_with_new_host(self):
        """If there is no RealtyHost yet, `2` realty objects will also be created."""
        CustomUser.objects.first().delete()

        output = StringIO()
        call_command('populaterealty', 2, stdout=output)

        self.assertEqual(Realty.objects.count(), 2)

    def test_no_additional_host_created_if_host_already_exists(self):
        """If there is a RealtyHost, no more new RealtyHosts should be created."""
        output = StringIO()
        call_command('populaterealty', 2, stdout=output)

        self.assertEqual(RealtyHost.objects.count(), 1)
        self.assertTrue(RealtyHost.objects.filter(user__email='test_fixture@airbnb.com'))

    def test_raises_exception_if_realty_count_less_then_one(self):
        """If `realty_count` is less than 1, a ValueError should be raised."""
        output = StringIO()

        with self.assertRaises(ValueError):
            call_command('populaterealty', 0, stdout=output)

from model_bakery import baker

from django.test import TestCase

from accounts.models import CustomUser
from ..services import has_user_profile_image


class AccountsServicesTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_users = baker.make('CustomUser', _quantity=3)

        test_users[0].profile.profile_image = 'image.png'
        test_users[0].save()

    def test_has_user_profile_image_valid_image(self):
        """has_user_profile_image() returns True if user has a profile image and it is not a default one."""
        result = has_user_profile_image(CustomUser.objects.all()[0].profile)
        self.assertTrue(result)

    def test_has_user_profile_image_default_image(self):
        """has_user_profile_image() returns False if user doesn't have a profile image."""
        result = has_user_profile_image(CustomUser.objects.all()[1].profile)
        self.assertFalse(result)

    def test_has_user_profile_image_no_image(self):
        """has_user_profile_image() returns False if user has a default profile image."""
        result = has_user_profile_image(CustomUser.objects.all()[2].profile)
        self.assertFalse(result)

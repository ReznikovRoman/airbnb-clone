from typing import List

from model_bakery import baker

from django.test import TestCase

from accounts.models import CustomUser
from ..services import has_user_profile_image


class AccountsServicesTests(TestCase):
    def setUp(self):
        self.test_users: List[CustomUser] = baker.make('CustomUser', _quantity=3)

        self.test_users[0].profile.profile_image = 'image.png'
        self.test_users[0].save()

    def test_has_user_profile_image_valid_image(self):
        """has_user_profile_image() returns True if user has a profile image and it is not a default one."""
        result = has_user_profile_image(self.test_users[0].profile)
        self.assertTrue(result)

    def test_has_user_profile_image_default_image(self):
        """has_user_profile_image() returns False if user doesn't have a profile image."""
        result = has_user_profile_image(self.test_users[1].profile)
        self.assertFalse(result)

    def test_has_user_profile_image_no_image(self):
        """has_user_profile_image() returns False if user has a default profile image."""
        result = has_user_profile_image(self.test_users[2].profile)
        self.assertFalse(result)

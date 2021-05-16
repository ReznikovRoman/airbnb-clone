from django.test import TestCase
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import Permission, ContentType

from ..models import (CustomUser, Profile, ProfileGenderChoices, SMSLog,
                      get_default_profile_image, get_profile_image_upload_path)


class CustomUserModelTests(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email="user1@gmail.com",
            first_name="John",
            last_name="Doe",
            password="test",
        )

        user2 = CustomUser.objects.create_user(
            email="user2@gmail.com",
            first_name="Peter",
            last_name="Williams",
            password="test",
        )
        user2.is_email_confirmed = True
        user2.save()

        CustomUser.objects.create_superuser(
            email="user3@gmail.com",
            first_name="Frank",
            last_name="Smith",
            password="test",
        )

    def test_model_verbose_name_single(self):
        """Test that model verbose name is set correctly."""
        self.assertEqual(CustomUser._meta.verbose_name, 'user')

    def test_model_verbose_name_plural(self):
        """Test that model verbose name (in plural) is set correctly."""
        self.assertEqual(CustomUser._meta.verbose_name_plural, 'users')

    def test_email_verbose_name(self):
        """Test that email verbose name is set correctly."""
        test_user: CustomUser = CustomUser.objects.first()
        email_verbose_name = test_user._meta.get_field('email').verbose_name
        self.assertEqual(email_verbose_name, 'email')

    def test_first_name_verbose_name(self):
        """Test that first_name verbose name is set correctly."""
        test_user: CustomUser = CustomUser.objects.first()
        first_name_verbose_name = test_user._meta.get_field('first_name').verbose_name
        self.assertEqual(first_name_verbose_name, 'first name')

    def test_last_name_verbose_name(self):
        """Test that last_name verbose name is set correctly."""
        test_user: CustomUser = CustomUser.objects.first()
        last_name_verbose_name = test_user._meta.get_field('last_name').verbose_name
        self.assertEqual(last_name_verbose_name, 'last name')

    def test_is_email_confirmed_verbose_name(self):
        """Test that is_email_confirmed verbose name is set correctly."""
        test_user: CustomUser = CustomUser.objects.first()
        is_email_confirmed_verbose_name = test_user._meta.get_field('is_email_confirmed').verbose_name
        self.assertEqual(is_email_confirmed_verbose_name, 'email confirmed')

    def test_date_joined_verbose_name(self):
        """Test that date_joined verbose name is set correctly."""
        test_user: CustomUser = CustomUser.objects.first()
        date_joined_verbose_name = test_user._meta.get_field('date_joined').verbose_name
        self.assertEqual(date_joined_verbose_name, 'date joined')

    def test_last_login_verbose_name(self):
        """Test that last_login verbose name is set correctly."""
        test_user: CustomUser = CustomUser.objects.first()
        last_login_verbose_name = test_user._meta.get_field('last_login').verbose_name
        self.assertEqual(last_login_verbose_name, 'last login')

    def test_is_email_confirmed_is_false_by_default(self):
        """Test that is_email_confirmed is set to False by default."""
        test_user: CustomUser = CustomUser.objects.first()
        self.assertFalse(test_user.is_email_confirmed)

    def test_is_admin_confirmed_is_false_by_default(self):
        """Test that is_admin is set to False by default."""
        test_user: CustomUser = CustomUser.objects.first()
        self.assertFalse(test_user.is_admin)

    def test_is_staff_confirmed_is_false_by_default(self):
        """Test that is_staff is set to False by default."""
        test_user: CustomUser = CustomUser.objects.first()
        self.assertFalse(test_user.is_staff)

    def test_is_superuser_confirmed_is_false_by_default(self):
        """Test that is_superuser is set to False by default."""
        test_user: CustomUser = CustomUser.objects.first()
        self.assertFalse(test_user.is_superuser)

    def test_is_active_confirmed_is_false_by_default(self):
        """Test that is_active is set to True by default."""
        test_user: CustomUser = CustomUser.objects.first()
        self.assertTrue(test_user.is_active)

    def test_object_name_is_email(self):
        """Test that CustomUser object name is set up properly."""
        test_user: CustomUser = CustomUser.objects.first()
        self.assertEqual(str(test_user), str(test_user.email))

    def test_full_name_is_first_name_space_last_name(self):
        """Test that full_name is set up properly."""
        test_user: CustomUser = CustomUser.objects.first()
        self.assertEqual(test_user.full_name, f"{test_user.first_name} {test_user.last_name}")

    def test_login_parameter_is_email(self):
        """Test that USERNAME_FIELD is set to `email`."""
        self.assertEqual(CustomUser.USERNAME_FIELD, 'email')

    def test_required_fields_include_first_and_last_name(self):
        """Test that `first_name` and `last_name` are in the REQUIRED_FIELDS."""
        self.assertListEqual(CustomUser.REQUIRED_FIELDS, ['first_name', 'last_name'])

    def test_activated_manager_returns_users_with_confirmed_email(self):
        """Test that `activated` manager returns only users with a confirmed email."""
        self.assertEqual(CustomUser.activated.count(), 1)
        self.assertEqual(CustomUser.activated.first().email, 'user2@gmail.com')

    def test_has_perm_superuser(self):
        """Test that superusers have all available permissions."""
        perm1 = Permission.objects.create(
            codename="perm1",
            name="Perm 1",
            content_type=ContentType.objects.get(app_label='accounts', model='customuser')
        )
        superuser = CustomUser.objects.get(email='user3@gmail.com')

        self.assertTrue(superuser.has_perm(perm1))
        self.assertSetEqual(superuser.get_all_permissions(), Permission.objects.all())

    def test_has_perm_no_permission(self):
        """Test that common users don't have all permissions."""
        perm1 = Permission.objects.create(
            codename="perm1",
            name="Perm 1",
            content_type=ContentType.objects.get(app_label='accounts', model='customuser')
        )
        user = CustomUser.objects.get(email='user1@gmail.com')

        self.assertFalse(user.has_perm(perm1))

    def test_create_staffuser_updates_is_staff_field(self):
        """Test that create_staffuser() creates new `staff` user (is_staff is set to True)."""
        user = CustomUser.objects.create_staffuser(
            email='staff1@gmail.com',
            first_name='Test',
            last_name='Test',
            password='test',
        )

        self.assertTrue(user.is_staff)

    def test_create_superuser_updates_admin_related_fields(self):
        """Test that create_superuser() creates new `superuser`."""
        user = CustomUser.objects.create_superuser(
            email='staff1@gmail.com',
            first_name='Test',
            last_name='Test',
            password='test',
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_superuser)

    def test_get_or_create_get_existing_user(self):
        """Test that get_or_create() returns CustomUser object if it already exists."""
        user, created = CustomUser.objects.get_or_create(
            email="user1@gmail.com",
            first_name="John",
            last_name="Doe",
            password="test",
        )

        self.assertEqual(user, CustomUser.objects.first())
        self.assertFalse(created)

    def test_get_or_create_create_new_user(self):
        """Test that get_or_create() creates new CustomUser object if it doesn't already exist."""
        user, created = CustomUser.objects.get_or_create(
            email="new123@gmail.com",
            first_name="John",
            last_name="Doe",
            password="test",
        )

        self.assertNotEqual(user, CustomUser.objects.first())
        self.assertEqual(user, CustomUser.objects.get(email="new123@gmail.com"))
        self.assertTrue(created)


class ProfileModelTests(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )

    def test_profile_image_verbose_name(self):
        """Test that profile_image verbose name is set correctly."""
        test_profile: Profile = CustomUser.objects.first().profile
        self.assertEqual(test_profile._meta.get_field('profile_image').verbose_name, 'profile image')

    def test_date_of_birth_verbose_name(self):
        """Test that date_of_birth verbose name is set correctly."""
        test_profile: Profile = CustomUser.objects.first().profile
        self.assertEqual(test_profile._meta.get_field('date_of_birth').verbose_name, 'date of birth')

    def test_gender_verbose_name(self):
        """Test that gender verbose name is set correctly."""
        test_profile: Profile = CustomUser.objects.first().profile
        self.assertEqual(test_profile._meta.get_field('gender').verbose_name, 'gender')

    def test_phone_number_verbose_name(self):
        """Test that phone_number verbose name is set correctly."""
        test_profile: Profile = CustomUser.objects.first().profile
        self.assertEqual(test_profile._meta.get_field('phone_number').verbose_name, 'phone number')

    def test_is_phone_number_confirmed_verbose_name(self):
        """Test that is_phone_number_confirmed verbose name is set correctly."""
        test_profile: Profile = CustomUser.objects.first().profile
        self.assertEqual(test_profile._meta.get_field('is_phone_number_confirmed').verbose_name,
                         'is phone number confirmed')

    def test_description_verbose_name(self):
        """Test that description verbose name is set correctly."""
        test_profile: Profile = CustomUser.objects.first().profile
        self.assertEqual(test_profile._meta.get_field('description').verbose_name, 'description')

    def test_model_verbose_name_single(self):
        """Test that model verbose name is set up correctly."""
        self.assertEqual(Profile._meta.verbose_name, 'profile')

    def test_model_verbose_name_plural(self):
        """Test that model verbose name (in plural) is set up correctly."""
        self.assertEqual(Profile._meta.verbose_name_plural, 'profiles')

    def test_object_name_has_user_object_name(self):
        """Test that Profile object name is set up properly."""
        test_profile: Profile = CustomUser.objects.first().profile
        self.assertEqual(str(test_profile), f"Profile for {test_profile.user}")

    def test_gender_field_params(self):
        """Test that gender has all required parameters (can be blank, max_length, choices)."""
        test_profile: Profile = CustomUser.objects.first().profile
        gender_field = test_profile._meta.get_field('gender')

        self.assertTrue(gender_field.blank)
        self.assertEqual(gender_field.max_length, 2)
        self.assertEqual(gender_field.choices, ProfileGenderChoices.choices)

    def test_gender_choices(self):
        """Test that ProfileGenderChoices has correct choices."""
        self.assertEqual(ProfileGenderChoices.names, ['MALE', 'FEMALE', 'OTHER'])
        self.assertEqual(ProfileGenderChoices.values, ['M', 'F', 'O'])
        self.assertEqual(ProfileGenderChoices.labels, ['Male', 'Female', 'Other'])

    def test_profile_image_field_params(self):
        """Test that profile_image has all required parameters (can be blank, upload_to, default)."""
        test_profile: Profile = CustomUser.objects.first().profile
        profile_image_field = test_profile._meta.get_field('profile_image')

        self.assertTrue(profile_image_field.blank)
        self.assertTrue(profile_image_field.null)
        self.assertEqual(profile_image_field.upload_to, get_profile_image_upload_path)
        self.assertEqual(profile_image_field.default, get_default_profile_image)

    def test_phone_number_params(self):
        """Test that phone_number has all required parameters (can be blank, is unique)."""
        test_profile: Profile = CustomUser.objects.first().profile
        phone_number_field = test_profile._meta.get_field('phone_number')

        self.assertTrue(phone_number_field.blank)
        self.assertTrue(phone_number_field.null)
        self.assertTrue(phone_number_field.unique)


class SMSLogModelTests(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )

    def test_sms_code_verbose_name(self):
        """Test that sms_code verbose name is set up correctly."""
        sms_log: SMSLog = SMSLog.objects.create(sms_code='1234', profile=CustomUser.objects.first().profile)
        self.assertEqual(sms_log._meta.get_field('sms_code').verbose_name, '4 digits sms code')

    def test_model_verbose_name_single(self):
        """Test that model verbose name is set correctly."""
        self.assertEqual(SMSLog._meta.verbose_name, 'sms log')

    def test_model_verbose_name_plural(self):
        """Test that model verbose name (in plural) is set correctly."""
        self.assertEqual(SMSLog._meta.verbose_name_plural, 'sms logs')

    def test_object_name_has_sms_code_and_user_email(self):
        """Test that SMSLog object name is set up properly."""
        sms_log: SMSLog = SMSLog.objects.create(sms_code='1234', profile=CustomUser.objects.first().profile)
        self.assertEqual(str(sms_log), f"Code `{sms_log.sms_code}` for {sms_log.profile.user}")

    def test_sms_code_validators(self):
        """Test that sms_code has all required validators (max length, min length, not blank)."""
        sms_log: SMSLog = SMSLog.objects.create(sms_code='1234', profile=CustomUser.objects.first().profile)
        sms_code_field = sms_log._meta.get_field('sms_code')

        self.assertTrue(sms_code_field.blank)
        self.assertEqual(sms_code_field.max_length, 4)
        self.assertIn(MinLengthValidator(4), sms_code_field.validators)

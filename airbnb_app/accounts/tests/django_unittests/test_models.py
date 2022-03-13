from django.contrib.auth.models import ContentType, Permission
from django.core.validators import MinLengthValidator
from django.test import TestCase

from accounts.models import (
    CustomUser, Profile, ProfileGenderChoices, SMSLog, get_default_profile_image, get_profile_image_upload_path,
)


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
        """`CustomUser` verbose name is set correctly."""
        self.assertEqual(CustomUser._meta.verbose_name, 'user')

    def test_model_verbose_name_plural(self):
        """`CustomUser` verbose name (in plural) is set correctly."""
        self.assertEqual(CustomUser._meta.verbose_name_plural, 'users')

    def test_email_field_params(self):
        """`email` field has all required parameters."""
        email_field = CustomUser._meta.get_field('email')

        self.assertEqual(email_field.verbose_name, 'email')
        self.assertEqual(email_field.max_length, 60)
        self.assertTrue(email_field.unique)

    def test_first_name_field_params(self):
        """`first_name` field has all required parameters."""
        first_name_field = CustomUser._meta.get_field('first_name')

        self.assertEqual(first_name_field.verbose_name, 'first name')
        self.assertEqual(first_name_field.max_length, 40)

    def test_last_name_field_params(self):
        """`last_name` field has all required parameters."""
        last_name_field = CustomUser._meta.get_field('last_name')

        self.assertEqual(last_name_field.verbose_name, 'last name')
        self.assertEqual(last_name_field.max_length, 40)

    def test_is_email_confirmed_field_params(self):
        """`is_email_confirmed` field has all required parameters."""
        is_email_confirmed_field = CustomUser._meta.get_field('is_email_confirmed')

        self.assertEqual(is_email_confirmed_field.verbose_name, 'email confirmed')
        self.assertFalse(is_email_confirmed_field.default)

    def test_date_joined_field_params(self):
        """`date_joined` field has all required parameters."""
        date_joined_field = CustomUser._meta.get_field('date_joined')

        self.assertEqual(date_joined_field.verbose_name, 'date joined')
        self.assertTrue(date_joined_field.auto_now_add)

    def test_last_login_field_params(self):
        """`last_login` field has all required parameters."""
        last_login_field = CustomUser._meta.get_field('last_login')

        self.assertEqual(last_login_field.verbose_name, 'last login')
        self.assertTrue(last_login_field.auto_now)

    def test_is_admin_field_params(self):
        """`is_admin` field has all required parameters."""
        is_admin_field = CustomUser._meta.get_field('is_admin')
        self.assertFalse(is_admin_field.default)

    def test_is_staff_field_params(self):
        """`is_staff` field has all required parameters."""
        is_staff_field = CustomUser._meta.get_field('is_staff')
        self.assertFalse(is_staff_field.default)

    def test_is_superuser_field_params(self):
        """`is_superuser` field has all required parameters."""
        is_superuser_field = CustomUser._meta.get_field('is_superuser')
        self.assertFalse(is_superuser_field.default)

    def test_is_active_field_params(self):
        """`is_active` field has all required parameters."""
        is_active_field = CustomUser._meta.get_field('is_active')
        self.assertTrue(is_active_field.default)

    def test_object_name_is_email(self):
        """`CustomUser` object name is set up properly."""
        test_user: CustomUser = CustomUser.objects.first()
        self.assertEqual(str(test_user), str(test_user.email))

    def test_full_name_is_first_name_space_last_name(self):
        """`full_name` is set up properly."""
        test_user: CustomUser = CustomUser.objects.first()
        self.assertEqual(test_user.full_name, f"{test_user.first_name} {test_user.last_name}")

    def test_login_parameter_is_email(self):
        """`USERNAME_FIELD` is set to `email`."""
        self.assertEqual(CustomUser.USERNAME_FIELD, 'email')

    def test_required_fields_include_first_and_last_name(self):
        """`first_name` and `last_name` are in `REQUIRED_FIELDS`."""
        self.assertListEqual(CustomUser.REQUIRED_FIELDS, ['first_name', 'last_name'])

    def test_activated_manager_returns_users_with_confirmed_email(self):
        """`activated` manager returns only users with confirmed emails."""
        self.assertEqual(CustomUser.activated.count(), 1)
        self.assertEqual(CustomUser.activated.first().email, 'user2@gmail.com')

    def test_has_perm_superuser(self):
        """Superusers have all available permissions."""
        perm1 = Permission.objects.create(
            codename="perm1",
            name="Perm 1",
            content_type=ContentType.objects.get(app_label='accounts', model='customuser'),
        )
        superuser = CustomUser.objects.get(email='user3@gmail.com')

        self.assertTrue(superuser.has_perm(perm1))
        self.assertSetEqual(superuser.get_all_permissions(), Permission.objects.all())

    def test_has_perm_no_permission(self):
        """Common users don't have all permissions."""
        perm1 = Permission.objects.create(
            codename="perm1",
            name="Perm 1",
            content_type=ContentType.objects.get(app_label='accounts', model='customuser'),
        )
        user = CustomUser.objects.get(email='user1@gmail.com')

        self.assertFalse(user.has_perm(perm1))

    def test_create_staffuser_updates_is_staff_field(self):
        """create_staffuser() creates new `staff` user (is_staff is set to True)."""
        user = CustomUser.objects.create_staffuser(
            email='staff1@gmail.com',
            first_name='Test',
            last_name='Test',
            password='test',
        )

        self.assertTrue(user.is_staff)

    def test_create_superuser_updates_admin_related_fields(self):
        """create_superuser() creates new `superuser`."""
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
        """get_or_create() returns CustomUser object if it already exists."""
        user, created = CustomUser.objects.get_or_create(
            email="user1@gmail.com",
            first_name="John",
            last_name="Doe",
            password="test",
        )

        self.assertEqual(user, CustomUser.objects.first())
        self.assertFalse(created)

    def test_get_or_create_create_new_user(self):
        """get_or_create() creates new CustomUser object if it doesn't already exist."""
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

    def test_model_verbose_name_single(self):
        """Profile verbose name is set correctly."""
        self.assertEqual(Profile._meta.verbose_name, 'profile')

    def test_model_verbose_name_plural(self):
        """Profile verbose name (in plural) is set correctly."""
        self.assertEqual(Profile._meta.verbose_name_plural, 'profiles')

    def test_profile_image_field_params(self):
        """`profile_image` field has all required parameters."""
        profile_image_field = Profile._meta.get_field('profile_image')

        self.assertEqual(profile_image_field.verbose_name, 'profile image')
        self.assertTrue(profile_image_field.blank)
        self.assertTrue(profile_image_field.null)
        self.assertEqual(profile_image_field.upload_to, get_profile_image_upload_path)
        self.assertEqual(profile_image_field.default, get_default_profile_image)

    def test_date_of_birth_verbose_name(self):
        """`date_of_birth` verbose name is set correctly."""
        test_profile: Profile = CustomUser.objects.first().profile
        self.assertEqual(test_profile._meta.get_field('date_of_birth').verbose_name, 'date of birth')

    def test_date_of_birth_field_params(self):
        """`date_of_birth` field has all required parameters."""
        date_of_birth_field = Profile._meta.get_field('date_of_birth')

        self.assertEqual(date_of_birth_field.verbose_name, 'date of birth')
        self.assertTrue(date_of_birth_field.blank)
        self.assertTrue(date_of_birth_field.null)

    def test_gender_field_params(self):
        """`gender` field has all required parameters."""
        gender_field = Profile._meta.get_field('gender')

        self.assertEqual(gender_field.verbose_name, 'gender')
        self.assertTrue(gender_field.blank)
        self.assertEqual(gender_field.max_length, 2)
        self.assertEqual(gender_field.choices, ProfileGenderChoices.choices)

    def test_phone_number_field_params(self):
        """`phone_number` field has all required parameters."""
        phone_number_field = Profile._meta.get_field('phone_number')

        self.assertEqual(phone_number_field.verbose_name, 'phone number')
        self.assertTrue(phone_number_field.blank)
        self.assertTrue(phone_number_field.null)
        self.assertTrue(phone_number_field.unique)

    def test_is_phone_number_confirmed_field_params(self):
        """`is_phone_number_confirmed` field has all required parameters."""
        is_phone_number_confirmed_field = Profile._meta.get_field('is_phone_number_confirmed')

        self.assertEqual(is_phone_number_confirmed_field.verbose_name, 'is phone number confirmed')
        self.assertFalse(is_phone_number_confirmed_field.default)

    def test_description_field_params(self):
        """`description` field has all required parameters."""
        description_field = Profile._meta.get_field('description')

        self.assertEqual(description_field.verbose_name, 'description')
        self.assertTrue(description_field.blank)

    def test_object_name_has_user_object_name(self):
        """Profile object name is set up properly."""
        test_profile: Profile = CustomUser.objects.first().profile
        self.assertEqual(str(test_profile), f"Profile for {test_profile.user}")

    def test_gender_choices(self):
        """`ProfileGenderChoices` has correct choices."""
        self.assertEqual(ProfileGenderChoices.names, ['MALE', 'FEMALE', 'OTHER'])
        self.assertEqual(ProfileGenderChoices.values, ['M', 'F', 'O'])
        self.assertEqual(ProfileGenderChoices.labels, ['Male', 'Female', 'Other'])


class SMSLogModelTests(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )

    def test_model_verbose_name_single(self):
        """`SMSLog` verbose name is set correctly."""
        self.assertEqual(SMSLog._meta.verbose_name, 'sms log')

    def test_model_verbose_name_plural(self):
        """`SMSLog` verbose name (in plural) is set correctly."""
        self.assertEqual(SMSLog._meta.verbose_name_plural, 'sms logs')

    def test_sms_code_field_params(self):
        """`sms_code` field has all required parameters."""
        sms_code_field = SMSLog._meta.get_field('sms_code')

        self.assertEqual(sms_code_field.verbose_name, '4 digits sms code')
        self.assertTrue(sms_code_field.blank)
        self.assertEqual(sms_code_field.max_length, 4)
        self.assertIn(MinLengthValidator(4), sms_code_field.validators)

    def test_object_name_has_sms_code_and_user_email(self):
        """`SMSLog` object name is set up properly."""
        sms_log: SMSLog = SMSLog.objects.create(sms_code='1234', profile=CustomUser.objects.first().profile)
        self.assertEqual(str(sms_log), f"Code `{sms_log.sms_code}` for {sms_log.profile.user}")

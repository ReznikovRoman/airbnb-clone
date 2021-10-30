from model_utils import FieldTracker
from phonenumber_field.modelfields import PhoneNumberField

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission, PermissionsMixin
from django.core.validators import MinLengthValidator
from django.db import models

from common.utils import select_file_storage


class CustomUserManager(BaseUserManager):
    """Manager for CustomUser model."""

    def create_user(self, email: str, first_name: str, last_name: str, password: str = None):
        if not email:
            raise ValueError('Users must have an email address.')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email: str, first_name: str, last_name: str, password: str):
        user = self.create_user(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, first_name: str, last_name: str, password: str):
        user = self.create_user(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def get_or_create(self, email: str, first_name: str = None, last_name: str = None, password: str = None):
        created = True
        try:
            user = self.get(
                email=self.normalize_email(email),
            )
            created = False
        except CustomUser.DoesNotExist:
            user = self.create_user(
                email=self.normalize_email(email),
                first_name=first_name,
                last_name=last_name,
                password=password,
            )
            user.save(using=self._db)
        return user, created


class ActivatedAccountsManager(CustomUserManager):
    """Manager for all users that have confirmed their email."""

    def get_queryset(self):
        base_qs = super(ActivatedAccountsManager, self).get_queryset()
        return base_qs.filter(is_email_confirmed=True)


class CustomUser(AbstractUser, PermissionsMixin):
    """Custom user model."""

    profile: "Profile"
    username = None
    email = models.EmailField(
        verbose_name='email',
        max_length=60,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='first name',
        max_length=40,
    )
    last_name = models.CharField(
        verbose_name='last name',
        max_length=40,
    )
    is_email_confirmed = models.BooleanField(verbose_name='email confirmed', default=False)
    date_joined = models.DateTimeField(
        verbose_name='date joined',
        auto_now_add=True,
    )
    last_login = models.DateTimeField(
        verbose_name='last login',
        auto_now=True,
    )
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()
    activated = ActivatedAccountsManager()

    # login parameter
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    # email field tracker
    email_tracker = FieldTracker(fields=['email'])

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email

    def get_all_permissions(self, obj=None):
        if self.is_active and self.is_superuser:
            return Permission.objects.all()
        return Permission.objects.filter(user=self)

    def has_perm(self, perm, obj=None):
        if perm in self.get_all_permissions() or perm in self.get_group_permissions():
            return True
        return False

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


def get_profile_image_upload_path(instance: "Profile", filename: str) -> str:
    return f"upload/users/{instance.user.email}/profile/{filename}"


def get_default_profile_image() -> str:
    return "default/profile/default_profile_image.png"


def get_default_profile_image_full_url() -> str:
    return f"{settings.MEDIA_URL}{get_default_profile_image()}"


class ProfileGenderChoices(models.TextChoices):
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    OTHER = 'O', 'Other'


class Profile(models.Model):
    """Profile for CustomUser."""

    profile_image = models.ImageField(
        verbose_name='profile image',
        blank=True,
        null=True,
        storage=select_file_storage,
        upload_to=get_profile_image_upload_path,
        default=get_default_profile_image,
    )
    date_of_birth = models.DateField(
        verbose_name='date of birth',
        blank=True,
        null=True,
    )
    gender = models.CharField(
        verbose_name='gender',
        blank=True,
        max_length=2,
        choices=ProfileGenderChoices.choices,
    )
    phone_number = PhoneNumberField(
        verbose_name='phone number',
        blank=True,
        null=True,
        unique=True,
    )
    is_phone_number_confirmed = models.BooleanField(
        verbose_name='is phone number confirmed',
        default=False,
    )
    description = models.TextField(
        verbose_name='description',
        blank=True,
    )
    user: CustomUser = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='profile',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'

    def __str__(self):
        return f"Profile for {self.user}"


class SMSLog(models.Model):
    """Log of sms message that is sent to User to verify his phone number."""

    sms_code = models.CharField(
        verbose_name='4 digits sms code',
        blank=True,
        max_length=4,
        validators=[
            MinLengthValidator(4),
        ],
    )
    profile = models.OneToOneField(
        Profile,
        related_name='sms_log',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'sms log'
        verbose_name_plural = 'sms logs'

    def __str__(self):
        return f"Code `{self.sms_code}` for {self.profile.user}"

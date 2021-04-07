from django.db import models
from django.contrib.auth.models import (AbstractUser, BaseUserManager,
                                        PermissionsMixin, Permission)


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
                email=self.normalize_email(email)
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


class CustomUser(AbstractUser, PermissionsMixin):
    """Custom user model."""
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

    # login parameter
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'custom user'
        verbose_name_plural = 'custom users'

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
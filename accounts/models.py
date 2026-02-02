from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


COUNTRY_CHOICES = [
    ("GB", "United Kingdom"),
    ("IE", "Ireland"),
]


class UserManager(BaseUserManager):
    """
    Configures Django User model to use email as the unique identifier.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("An email address must be provided.")
        if not password:
            raise ValueError("A password must be provided.")

        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Simplified custom user model with email as login.
    Includes optional delivery details for checkout autofill.
    Optional personal details can be added in the My Account page.
    """

    email = models.EmailField(unique=True)

    # Optional personal details (for checkout autofill)
    first_name = models.CharField(max_length=35, blank=True)
    last_name = models.CharField(max_length=35, blank=True)

    # Optional delivery details (for checkout autofill)
    phone_number = models.CharField(max_length=20, blank=True)
    address_line_1 = models.CharField(max_length=80, blank=True)
    address_line_2 = models.CharField(max_length=80, blank=True)
    town_or_city = models.CharField(max_length=40, blank=True)
    county = models.CharField(max_length=40, blank=True)
    postcode = models.CharField(max_length=12, blank=True)
    country = models.CharField(
        max_length=2,
        choices=COUNTRY_CHOICES,
        blank=True
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

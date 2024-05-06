from typing import ClassVar

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models import CharField, EmailField
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class EncryptedUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Default custom user model for backend.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    USER_TYPE_CHOICES = [
        ("Administrator", "Administrator"),
        ("User", "User"),
        ("Developer", "Developer"),
        ("Investor", "Investor"),
    ]

    # First and last name do not cover name patterns around the globe
    fullname = CharField(max_length=255, default="John Doe")
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = models.CharField(_("firstName of User"), blank=True, max_length=100)
    last_name = models.CharField(_("lastName of User"), blank=True, max_length=100)
    user_type = CharField(max_length=50, choices=USER_TYPE_CHOICES, default="User")
    phoneNumber = models.CharField(
        _("phone Number of User"), blank=True, max_length=255
    )
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]
    profile_info = models.TextField(blank=True)
    user_image = models.ImageField(upload_to="media/user_images", null=True, blank=True)
    mail_verify_statu = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})

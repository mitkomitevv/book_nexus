from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from book_nexus.accounts.choices import GenderChoices
from book_nexus.accounts.managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
    )

    full_name = models.CharField(max_length=50)

    date_joined = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return self.email


UserModel = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(
        to=UserModel,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    interests = models.TextField(
        blank=True,
        null=True,
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True,
    )

    country = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    gender = models.CharField(
        choices=GenderChoices.choices,
        blank=True,
        null=True,
    )

    profile_picture = CloudinaryField("image", blank=True, null=True)

    def __str__(self):
        return self.user.full_name


class Follow(models.Model):
    follower = models.ForeignKey(
        to=UserModel, on_delete=models.CASCADE, related_name="following"
    )
    followed_user = models.ForeignKey(
        to=UserModel, on_delete=models.CASCADE, related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "followed_user")

    def __str__(self):
        return f"{self.follower.full_name} follows {self.followed_user.full_name}"

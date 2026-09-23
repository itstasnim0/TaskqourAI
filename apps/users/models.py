from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import CIEmailField
from django.db import models

from apps.common.models import UUIDModel

from .managers import CustomUserManager


class CustomUser(UUIDModel, AbstractBaseUser, PermissionsMixin):
    """Use email and stable UUID identity from the first project migration."""

    email = CIEmailField(unique=True)
    email.system_check_removed_details = None
    phone = models.CharField(max_length=20, null=True, blank=True)
    full_name = models.CharField(max_length=150)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    email_verified_at = models.DateTimeField(null=True, blank=True)
    locale = models.CharField(max_length=8, default="fa")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        ordering = ["email"]
        db_table = "users_user"

    def __str__(self) -> str:
        return self.email

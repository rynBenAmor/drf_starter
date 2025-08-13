from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from .managers import UserManager

class User(AbstractUser):
    username = None
    USERNAME_FIELD = 'email'
    email = models.EmailField(_("email address"), blank=False, null=False, unique=True)
    REQUIRED_FIELDS = []

    objects = UserManager()

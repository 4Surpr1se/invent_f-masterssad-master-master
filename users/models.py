from django.db import models

from django.contrib.auth.models import AbstractUser

from users.managers import UserManager
from core.models import Mol


class User(AbstractUser):
    """creating new User model inherited from AbstractUser,
     redefining objects"""

    Mol = models.ForeignKey(Mol, null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.username

    objects = UserManager()

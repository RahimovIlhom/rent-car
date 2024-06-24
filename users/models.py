from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    fullname = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ism-familiya")
    phone = models.CharField(max_length=255, blank=True, null=True, verbose_name="Telefon raqam")

    REQUIRED_FIELDS = ['fullname', 'phone']

    def __str__(self):
        return self.fullname

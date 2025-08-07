import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from phonenumber_field.modelfields import PhoneNumberField

from apps.common.models import BaseModel
from apps.user.fields import EncryptedTextField


class Role(models.IntegerChoices):
    CLIENT = 0, "Client"
    MODERATOR = 1, "Moderator"
    ADMIN = 2, "Admin"


class Gender(models.IntegerChoices):
    FEMALE = 0, "Female"
    MALE = 1, "Male"


class User(AbstractUser, BaseModel):
    middle_name = models.CharField(max_length=150, blank=True)

    primary_phone = PhoneNumberField(null=True, db_index=True)
    secondary_phone = PhoneNumberField(null=True, db_index=True)

    avatar = models.ForeignKey('common.Media', on_delete=models.SET_NULL, null=True, blank=True)

    tg_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    tg_username = models.CharField(max_length=70, null=True, blank=True, db_index=True)

    gender = models.IntegerField(choices=Gender.choices, null=True, blank=True)
    role = models.IntegerField(choices=Role.choices, default=Role.CLIENT)

    country = models.ForeignKey('common.Country', on_delete=models.SET_NULL, null=True, blank=True)
    region = models.ForeignKey('common.Region', on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey('common.District', on_delete=models.SET_NULL, null=True, blank=True)

    bio = CKEditor5Field(validators=[MaxLengthValidator(500)], null=True, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name} {self.middle_name or ''}".strip()

    class Meta:
        ordering = ("last_name", "first_name")
        verbose_name = "User"
        verbose_name_plural = "Users"


class UserDevice(BaseModel):
    user = models.ForeignKey("user.User", on_delete=models.SET_NULL, null=True, related_name="devices")
    device_name = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    refresh_token = EncryptedTextField()
    last_login = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user or 'Unknown'} - {self.device_name}"

    class Meta:
        verbose_name = "User Device"
        verbose_name_plural = "User Devices"

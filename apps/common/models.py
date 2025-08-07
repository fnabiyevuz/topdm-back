import mimetypes
import uuid

from django.db import models

from apps.common.managers import SoftDeleteManager


class Project(models.IntegerChoices):
    ESTATE = 1, 'Real Estate'
    VEHICLE = 2, 'Vehicle'
    PHONE = 3, 'Phone'
    ELECTRONIC = 4, 'Electronic'
    WORKER = 5, 'Worker'
    SERVICE = 6, 'Service'


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ('-created_at',)
        indexes = (
            models.Index(fields=['-created_at']),
        )

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save(update_fields=["is_deleted"])

    def restore(self):
        self.is_deleted = False
        self.save(update_fields=["is_deleted"])

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)


class Country(BaseModel):
    legacy_id = models.PositiveSmallIntegerField(null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Region(BaseModel):
    legacy_id = models.PositiveSmallIntegerField(null=True, blank=True)
    pk = models.PositiveSmallIntegerField(null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="regions")
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("country", "name")

    def __str__(self):
        return self.name


class District(BaseModel):
    legacy_id = models.PositiveSmallIntegerField(null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="districts")
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("region", "name")

    def __str__(self):
        return self.name


class Neighborhood(BaseModel):
    legacy_id = models.PositiveSmallIntegerField(null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="neighborhoods")
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("district", "name")

    def __str__(self):
        return self.name


class FileType(models.IntegerChoices):
    IMAGE = 1, 'Image'
    VIDEO = 2, 'Video'
    DOCUMENT = 3, 'Document'
    AUDIO = 4, 'Audio'
    OTHER = 5, 'Other'


def upload_to(instance, filename):
    return f"media/{instance.file_type}/{uuid.uuid4()}_{filename}"


class Media(BaseModel):
    file = models.FileField(upload_to=upload_to)
    file_type = models.IntegerField(choices=FileType.choices, default=FileType.OTHER)
    file_name = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = self.file_name or self.file.name

            content_type, _ = mimetypes.guess_type(self.file.name)
            main_type = content_type.split('/')[0] if content_type else None

            self.file_type = {
                'image': FileType.IMAGE,
                'video': FileType.VIDEO,
                'audio': FileType.AUDIO,
                'application': FileType.DOCUMENT,
                'text': FileType.DOCUMENT,
            }.get(main_type, FileType.OTHER)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.file_name or self.file.name

    class Meta:
        verbose_name = "Media File"
        verbose_name_plural = "Media Files"

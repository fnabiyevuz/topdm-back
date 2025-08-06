import mimetypes
import uuid

from django.db import models

from apps.common.managers import SoftDeleteManager


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ('-created_at',)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)


class Country(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Region(BaseModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="regions")
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("country", "name")

    def __str__(self):
        return f"{self.name}, {self.country.name}"


class District(BaseModel):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="districts")
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("region", "name")

    def __str__(self):
        return f"{self.name}, {self.region.name}"


class Neighborhood(BaseModel):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="neighborhoods")
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("district", "name")

    def __str__(self):
        return f"{self.name}, {self.district.name}"


class FileType(models.IntegerChoices):
    IMAGE = 1, 'Image'
    VIDEO = 2, 'Video'
    DOCUMENT = 3, 'Document'
    AUDIO = 4, 'Audio'
    OTHER = 5, 'Other'


class Media(BaseModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    file = models.FileField(upload_to='media/')
    file_type = models.IntegerField(choices=FileType.choices, default=FileType.OTHER)
    file_name = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Set file_name if empty
        if self.file and not self.file_name:
            self.file_name = self.file.name

        # Determine file_type from MIME type
        if self.file:
            content_type, _ = mimetypes.guess_type(self.file.name)
            if content_type:
                main_type = content_type.split('/')[0]
                if main_type == 'image':
                    self.file_type = FileType.IMAGE
                elif main_type == 'video':
                    self.file_type = FileType.VIDEO
                elif main_type == 'audio':
                    self.file_type = FileType.AUDIO
                elif main_type in ['application', 'text']:
                    self.file_type = FileType.DOCUMENT
                else:
                    self.file_type = FileType.OTHER
            else:
                self.file_type = FileType.OTHER

        super().save(*args, **kwargs)

    def __str__(self):
        return self.file_name or self.file.name

    class Meta:
        verbose_name = "Media File"
        verbose_name_plural = "Media Files"

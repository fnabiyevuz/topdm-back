from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.common.models import BaseModel, Project


class Currency(models.IntegerChoices):
    UZS = 1, 'UZS'
    USD = 2, 'USD'


class AdsStatus(models.IntegerChoices):
    CREATED = 1, 'Created'
    MODERATION = 2, 'On Moderation'
    ACTIVE = 3, 'Active'
    MODERATOR_DEACTIVE = 4, 'Deactivated by Moderator'
    OWNER_DEACTIVE = 5, 'Deactivated by Owner'
    TIME_DEACTIVE = 6, 'Expired'
    ARCHIVE = 7, 'Archived'


class PaymentStatus(models.IntegerChoices):
    NOT_PAID = 0, 'Not paid'
    PAID = 1, 'Paid'


class Ads(BaseModel):
    owner = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name="ads")

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=500, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    currency = models.IntegerField(choices=Currency.choices, default=Currency.UZS)
    status = models.IntegerField(choices=AdsStatus.choices, default=AdsStatus.CREATED)
    payment_status = models.IntegerField(choices=PaymentStatus.choices, default=PaymentStatus.NOT_PAID)

    country = models.ForeignKey('common.Country', on_delete=models.SET_NULL, null=True, blank=True)
    region = models.ForeignKey('common.Region', on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey('common.District', on_delete=models.SET_NULL, null=True, blank=True)
    neighborhood = models.ForeignKey('common.Neighborhood', on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=256, null=True, blank=True)

    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    is_vip = models.BooleanField(default=False)
    is_top = models.BooleanField(default=False)
    vip_expiry_date = models.DateTimeField(null=True, blank=True)
    top_expiry_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)


class GenericBaseModel(BaseModel):
    project = models.IntegerField(choices=Project.choices, null=True)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, db_index=True)
    object_id = models.PositiveBigIntegerField(db_index=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["user", "content_type", "object_id"]),
        ]


class Image(GenericBaseModel):
    image = models.ForeignKey("common.Media", on_delete=models.CASCADE)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Image on {self.content_type.model} for (ID {self.object_id})"


class Comment(GenericBaseModel):
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    comment = models.TextField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Commented by {self.user} on {self.content_type.model} (ID {self.object_id})"


class Like(GenericBaseModel):

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"],
                name="unique_like_per_user_object"
            )
        ]

    def __str__(self):
        return f"Liked by {self.user} on {self.content_type.model} (ID {self.object_id})"


class View(GenericBaseModel):
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"],
                name="unique_view_per_user_object"
            )
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Viewed by {self.user} on {self.content_type.model} (ID {self.object_id})"


class Bookmark(GenericBaseModel):

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"],
                name="unique_bookmark_per_user_object"
            )
        ]

    def __str__(self):
        return f"Bookmarked by {self.user} on {self.content_type.model} (ID {self.object_id})"


class ReportReason(models.IntegerChoices):
    SPAM = 0, 'Spam'
    FRAUD = 1, 'Scam or Fraud'
    WRONG_INFO = 2, 'Wrong Information'
    INAPPROPRIATE = 3, 'Inappropriate Content'
    DUPLICATE = 4, 'Duplicate Ad'
    OTHER = 5, 'Other'


class Report(GenericBaseModel):
    reason = models.IntegerField(choices=ReportReason.choices, default=ReportReason.OTHER)
    description = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"],
                name="unique_report_per_user_object"
            )
        ]

    def __str__(self):
        return f"Report by {self.user} on {self.content_type.model} (ID {self.object_id})"


class Rating(GenericBaseModel):
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"],
                name="unique_rating_per_user_object"
            )
        ]

    def __str__(self):
        return f"Rating by {self.user} on {self.content_type.model} (ID {self.object_id})"

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from apps.ads.models import Ads


class EstateType(models.IntegerChoices):
    APARTMENT = 1, "Apartment"
    HOUSE = 2, "House"
    COMMERCIAL = 3, "Commercial"
    LAND = 4, "Land"


class EstatePurpose(models.IntegerChoices):
    SALE = 1, "Sale"
    RENT_DAILY = 2, "Rent (Daily)"
    RENT_LONG_TERM = 3, "Rent (Long-term)"


class EstateCondition(models.IntegerChoices):
    NEW = 1, "New"
    SECONDARY = 2, "Secondary"


class EstateRepair(models.IntegerChoices):
    NO_NEED = 0, "No Need"
    REQUIRED = 1, "Required"
    GOOD = 2, "Good"
    COSMETIC = 3, "Cosmetic"
    EURO = 4, "Euro"
    DESIGN = 5, "Design"
    CAPITAL = 6, "Capital"


class EstateQuality(models.IntegerChoices):
    NULL = 0, "Not specified"
    ECONOMY = 1, "Economy"
    STANDARD = 2, "Standard"
    BUSINESS = 3, "Business"
    LUX = 4, "Lux"


class EstateAdvantage(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Estate(Ads):
    type = models.IntegerField(choices=EstateType.choices, null=True, blank=True)
    purpose = models.IntegerField(choices=EstatePurpose.choices, null=True, blank=True)
    condition = models.IntegerField(choices=EstateCondition.choices, null=True, blank=True)
    repair = models.IntegerField(choices=EstateRepair.choices, null=True, blank=True)
    quality = models.IntegerField(choices=EstateQuality.choices, null=True, blank=True)

    room_count = models.PositiveSmallIntegerField(null=True, blank=True)
    area = models.PositiveSmallIntegerField(null=True, blank=True)
    floor_number = models.PositiveSmallIntegerField(null=True, blank=True)
    floors_count = models.PositiveSmallIntegerField(null=True, blank=True)

    facilities = models.ManyToManyField(EstateAdvantage, blank=True)

    images = GenericRelation("Image")
    comments = GenericRelation("Comment")
    likes = GenericRelation("Like")
    views = GenericRelation("View")
    shares = GenericRelation("Share")
    bookmark = GenericRelation("Bookmark")
    report = GenericRelation("Report")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Estate"
        verbose_name_plural = "Estates"

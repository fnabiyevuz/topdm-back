from django.db import models

from apps.common.models import BaseModel


class Profession(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class MasterProfile(BaseModel):
    user = models.OneToOneField("user.User", on_delete=models.SET_NULL, null=True)
    profession = models.ForeignKey(Profession, on_delete=models.SET_NULL, null=True, blank=True)
    skills = models.ManyToManyField(Skill, related_name="masters", blank=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.profession}"

    class Meta:
        verbose_name = "Master Profile"
        verbose_name_plural = "Master Profiles"


class WorkingDay(models.IntegerChoices):
    MONDAY = 0, "Monday"
    TUESDAY = 1, "Tuesday"
    WEDNESDAY = 2, "Wednesday"
    THURSDAY = 3, "Thursday"
    FRIDAY = 4, "Friday"
    SATURDAY = 5, "Saturday"
    SUNDAY = 6, "Sunday"


class MasterWorkingHour(BaseModel):
    master = models.ForeignKey("master.MasterProfile", on_delete=models.CASCADE, related_name="working_hours")
    day_of_week = models.IntegerField(choices=WorkingDay.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_day_off = models.BooleanField(default=False)

    class Meta:
        unique_together = ("master", "day_of_week")
        verbose_name = "Working Hour"
        verbose_name_plural = "Working Hours"

    def __str__(self):
        return f"{self.master} - {self.day_of_week} ({self.start_time} - {self.end_time})"

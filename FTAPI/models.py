from django.db import models  # type: ignore
from django.contrib.auth.models import AbstractUser # type: ignore

# Create your models here.

class User(AbstractUser): # type: ignore
    pass


class File(models.Model):
    filename = models.CharField(
        name="filename",
        max_length=250,
    )
    suffix = models.CharField(
        name="suffix",
        max_length=15,
    )
    file = models.FileField(
        name="file",
        upload_to="files/%Y/%m/%d/", 
        max_length=250,
    )
    size = models.BigIntegerField(
        name="size",
    )
    url = models.URLField(
        name="url",
    )
    uploaded_date = models.DateField(
        name="uploaded_date",
        auto_now_add=True,
    )
    uploaded_time = models.TimeField(
        name="uploaded_time",
        auto_now_add=True,
    )
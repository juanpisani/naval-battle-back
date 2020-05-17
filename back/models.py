from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import django
from server import settings
# Create your models here.


class BaseModel(models.Model):

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   editable=False, related_name="+", on_delete=models.PROTECT)

    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   editable=False, related_name="+", on_delete=models.PROTECT)

    created_at = models.DateTimeField(default=django.utils.timezone.now,
                                      editable=False)
    updated_at = models.DateTimeField(auto_now=True,
                                      editable=False)

    class Meta:
        abstract = True


class User(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

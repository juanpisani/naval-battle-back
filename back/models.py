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
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)


class WaitingUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class GameSession(BaseModel):
    player_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_1')
    player_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_2')
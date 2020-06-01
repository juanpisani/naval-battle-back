import json

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import django
from model_utils import Choices

from server import settings
# Create your models here.

LETTERS = Choices('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
NUMBERS = Choices('1', '2', '3', '4', '5', '6', '7', '8', '9', '10')


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
    game_session_id = models.CharField(max_length=10)


class GameSession(BaseModel):
    player_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_1', null=True)
    player_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_2', null=True)
    player_1_connected = models.BooleanField()
    player_2_connected = models.BooleanField()
    player_1_board = None
    player_2_board = None

    def set_up_player_board(self, user_id, board):
        if self.player_1.id == user_id:
            self.player_1_board = board
        elif self.player_2.id == user_id:
            self.player_2_board = board


class Cell:
    boat = False

    def __init__(self, boat):
        self.boat = boat

    def __str__(self):
        return self.boat

    def toJSON(self):
        return {"boat": self.boat}
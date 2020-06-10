# chat/consumers.py
import json
import random

from channels.generic.websocket import AsyncWebsocketConsumer

from back.engine import GameEngine
from back.models import GameSession
from back.utils import dict_to_board
#
#
# class GameSessionConsumer(AsyncWebsocketConsumer):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if self.groups is None:
#             self.groups = []
#
#     async def connect(self):
#         self.scope['session']['game'] = Game()
#         self.room_name = self.scope['url_route']['kwargs']['session_id']
#         self.room_group_name = 'game_%s' % self.room_name
#         # self._game = GameSession.objects.get(id=self.scope['url_route']['kwargs']['session_id'])
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name,
#         )
#         await self.accept()
#
#     # todo disconnect
#
#     async def receive(self, text_data=None, bytes_data=None):
#         text_data_json = json.loads(text_data)
#         command = text_data_json['command']
#
#         if command == 'connected':
#             session_id = text_data_json['roomId']
#             user_id = text_data_json['userId']
#             if self.scope['session']['game']._player_1_id is None:
#                 self.scope['session']['game']._player_1_id = user_id
#             elif self.scope['session']['game']._player_2_id is None:
#                 if self.scope['session']['game']._player_1_id is not user_id:
#                     self.scope['session']['game']._player_2_id = user_id
#             await self.receive_player(session_id=session_id, user_id=user_id)
#
#         if command == 'boards':
#             session_id = text_data_json['roomId']
#             user_id = text_data_json['userId']
#             board_json = text_data_json['board']
#             await self.receive_board(session_id=session_id, user_id=user_id, board_json=board_json)
#
#     # todo borrar el session id
#     async def receive_board(self, session_id, user_id, board_json):
#         board = dict_to_board(board_json)
#         self.scope['session']['game'].set_up_player_board(user_id, board)
#         self.scope["session"].save()
#         try:
#             if self.scope['session']['game']._player_1_board is not None and self.scope['session']['game']._player_2_board is not None:
#                 # todo not send group, set
#                 await self.channel_layer.group_send(
#                     self.room_group_name,
#                     {
#                         'type': 'boards_ready',
#                         'message': 'Start game both players have filled their boards',
#                         'player_1_board': self.scope['session']['game']._player_1_board,
#                         'player_1_id': self.scope['session']['game']._player_1_id,
#                         'player_2_board': self.scope['session']['game']._player_2_board,
#                         'player_2_id': self.scope['session']['game']._player_2_id,
#                     }
#                 )
#             else:
#                 await self.channel_layer.group_send(
#                     self.room_group_name,
#                     {
#                         'type': 'waiting',
#                         'message': 'Waiting for players to fill their boards'
#                     }
#                 )
#         except AttributeError:
#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     'type': 'waiting',
#                     'message': 'Waiting for players to fill their boards'
#                 }
#             )
#
#     async def receive_player(self, session_id, user_id):
#         session = GameSession.objects.get(id=session_id)
#         if session.player_1 and session.player_1.id == user_id:
#             session.player_1_connected = True
#             session.save()
#         elif session.player_2 and session.player_2.id == user_id:
#             session.player_2_connected = True
#             session.save()
#         if session.player_1 is not None and session.player_2 is not None:
#             if session.player_1_connected and session.player_2_connected:
#                 await self.channel_layer.group_send(
#                     self.room_group_name,
#                     {
#                         'type': 'game_start',
#                         'message': 'Start game',
#                         'player_1': {
#                             'id': session.player_1.id,
#                             'email': session.player_1.email,
#                         },
#                         'player_2': {
#                             'id': session.player_2.id,
#                             'email': session.player_2.email,
#                         }
#                     }
#                 )
#             else:
#                 await self.channel_layer.group_send(
#                     self.room_group_name,
#                     {
#                         'type': 'waiting',
#                         'message': 'Waiting for session to be full'
#                     }
#                 )
#         else:
#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     'type': 'waiting',
#                     'message': 'Waiting for session to be full'
#                 }
#             )
#
#     async def game_start(self, event):
#         message = event['message']
#         type = event['type']
#         player_1 = event['player_1']
#         player_2 = event['player_2']
#
#         await self.send(text_data=json.dumps({
#             'command': type,
#             'message': message,
#             'player_1': player_1,
#             'player_2': player_2,
#         }))
#
#     async def waiting(self, event):
#         message = event['message']
#         type = event['type']
#
#         await self.send(text_data=json.dumps({
#             'command': type,
#             'message': message
#         }))
#
#     async def boards_ready(self, event):
#         message = event['message']
#         type = event['type']
#         player_1_board = event['player_1_board']
#         player_2_board = event['player_2_board']
#
#         await self.send(text_data=json.dumps({
#             'command': type,
#             'message': message,
#             'player_1_board': player_1_board,
#             'player_2_board': player_2_board,
#         }))
#
#
# class Game():
#     def __init__(self):
#         self._player_1_board = None
#         self._player_1_id = None
#         self._player_2_board = None
#         self._player_2_id = None
#
#     def set_up_player_board(self, user_id, board):
#         if self._player_1_id and self._player_1_id == user_id:
#             self._player_1_board = board
#         elif self._player_2_id and self._player_2_id == user_id:
#             self._player_2_board = board

import json
import logging

from channels.consumer import SyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer

log = logging.getLogger(__name__)


class PlayerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        log.info("Connect")
        self.group_name = "game_%s" % self.scope['url_route']['kwargs']['session_id']
        self.game = None
        self.user_id = None
        log.info("User Connected")

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        log.info("Disconnect: %s", close_code)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def join(self, msg: dict):
        user_id = msg["userId"]
        if "userId" not in self.scope["session"]:
            self.scope["session"]["userId"] = user_id
            self.scope["session"].save()
        self.user_id = self.scope["session"]["userId"]
        log.info("User %s: Joining game", self.user_id)
        await self.channel_layer.send(
            "game_engine",
            {"type": "player.new", "player": self.user_id, "channel": self.channel_name},
        )

    # todo user movements
    # shoot
    # setup pieces
    async def shoot(self, msg: dict):
        if not self.user_id:
            log.info("Attempting to shoot without joining the game")
            return

        log.info("User %s shooting", self.user_id)
        await self.channel_layer.send(
            "game_engine",
            {"type": "player.shoot", "player": self.user_id, "shoot": msg["shoot"]},
        )

    async def set_pieces(self, msg: dict):
        if not self.user_id:
            log.info("Attempting to set pieces without joining the game")
            return

        log.info("User %s seting pieces", self.user_id)
        await self.channel_layer.send(
            "game_engine",
            {"type": "player.set_pieces", "player": self.user_id, "pieces": msg["pieces"]},
        )

    # Receive message from Websocket
    async def receive(self, text_data=None, bytes_data=None):
        content = json.loads(text_data)
        msg_type = content["type"]
        msg = content["msg"]
        if msg_type == "shoot":
            return await self.shoot(msg)
        elif msg_type == "set_pieces":
            return await self.set_pieces(msg)
        elif msg_type == "join":
            return await self.join(msg)
        else:
            log.warning("Incoming msg %s is unknown", msg_type)

    # Send game data to room group after a Tick is processed
    async def game_update(self, event):
        log.info("Game Update: %s", event)
        # Send message to WebSocket
        state = event["state"]
        await self.send(json.dumps(state))


class GameConsumer(SyncConsumer):
    def __init__(self, *args, **kwargs):
        """
        Created on demand when the first player joins.
        """
        log.info("Game Consumer: %s %s", args, kwargs)
        super().__init__(*args, **kwargs)
        self.group_name = "battleships"
        self.engine = GameEngine(self.group_name)
        self.engine.start()

    def player_new(self, event):
        log.info("Player Joined: %s", event["player"])
        self.engine.join_queue(event["player"])

    def shoot(self, event):
        log.info("Player shooting: %s", event['player'])
        shoot = event.get("shoot", None)
        # check if shoot is in A-J 1-10 ?
        if shoot:
            self.engine.shoot(event["player"], shoot)

    def set_pieces(self, event):
        log.info("Player setting pieces: %s", event['player'])
        pieces = event.get("pieces", None)
        if pieces:
            _, list_cells_with_boats_pieces = dict_to_board(pieces)
            self.engine.set_pieces(event["player"], list_cells_with_boats_pieces)

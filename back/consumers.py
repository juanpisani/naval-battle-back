import json
import logging

from channels.consumer import SyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer

from back.engine import GameEngine
from back.utils import dict_to_board

log = logging.getLogger(__name__)


class PlayerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        log.debug("Connect")
        self.group_name = "game_%s" % self.scope['url_route']['kwargs']['session_id']
        self.game = None
        self.user_id = None
        log.debug("User Connected")

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        log.debug("Disconnect: %s", close_code)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def join(self, message: dict):
        user_id = message["userId"]
        if "userId" not in self.scope["session"]:
            self.scope["session"]["userId"] = user_id
            self.scope["session"].save()
        self.user_id = self.scope["session"]["userId"]
        log.debug("User %s: Joining game", self.user_id)
        await self.channel_layer.send(
            "battleships",
            {"type": "player.new", "player": self.user_id, "channel": self.channel_name},
        )

    async def receive_shoot(self, message: dict):
        if not self.user_id:
            log.debug("Attempting to shoot without joining the game")
            return

        log.debug("User %s shooting", self.user_id)
        await self.channel_layer.send(
            "battleships",
            {"type": "player.receive_shoot", "player": self.user_id, "shoot": message["shoot"]},
        )

    async def receive_board(self, message: dict):
        if not self.user_id:
            log.debug("Attempting to set pieces without joining the game")
            return

        log.debug("User %s seting pieces", self.user_id)
        await self.channel_layer.send(
            "battleships",
            {"type": "player.receive_board", "player": self.user_id, "pieces": message["pieces"]},
        )

    # Send game data to room group after a shoot is processed
    # Advance to next turn
    async def game_update(self, event):
        log.debug("Game Update: %s", event)
        # Send message to WebSocket
        state = event["state"]
        await self.send(json.dumps(state))


    # Receive message from Websocket
    async def receive(self, text_data=None, bytes_data=None):
        content = json.loads(text_data)
        command = content["command"]
        message = content["message"]
        if command == "receive_shoot":
            return await self.receive_shoot(message)
        elif command == "receive_board":
            return await self.receive_board(message)
        elif command == "join":
            return await self.join(message)
        elif command == 'connected':
            await self.join(message)
        else:
            log.warning("Incoming message %s is unknown", command)

    # async def receive_player(self, message:dict):
    #
    #     # session = GameSession.objects.get(id=session_id)
    #     # if session.player_1 and session.player_1.id == user_id:
    #     #     session.player_1_connected = True
    #     #     session.save()
    #     # elif session.player_2 and session.player_2.id == user_id:
    #     #     session.player_2_connected = True
    #     #     session.save()
    #     # if session.player_1 is not None and session.player_2 is not None:
    #     #     if session.player_1_connected and session.player_2_connected:
    #     #         await self.channel_layer.group_send(
    #     #             self.room_group_name,
    #     #             {
    #     #                 'type': 'game_start',
    #     #                 'message': 'Start game',
    #     #                 'player_1': {
    #     #                     'id': session.player_1.id,
    #     #                     'email': session.player_1.email,
    #     #                 },
    #     #                 'player_2': {
    #     #                     'id': session.player_2.id,
    #     #                     'email': session.player_2.email,
    #     #                 }
    #     #             }
    #     #         )
    #     #     else:
    #     #         await self.channel_layer.group_send(
    #     #             self.room_group_name,
    #     #             {
    #     #                 'type': 'waiting',
    #     #                 'message': 'Waiting for session to be full'
    #     #             }
    #     #         )
    #     # else:
    #     #     await self.channel_layer.group_send(
    #     #         self.room_group_name,
    #     #         {
    #     #             'type': 'waiting',
    #     #             'message': 'Waiting for session to be full'
    #     #         }
    #     #     )

    # todo cambiar a que reciba un message y las cosas este ahi adentro
    async def game_start(self, event):
        message = event['message']
        type = event['type']
        player_1 = event['player_1']
        player_2 = event['player_2']

        await self.send(text_data=json.dumps({
            'command': type,
            'message': message,
            'player_1': player_1,
            'player_2': player_2,
        }))


class GameConsumer(SyncConsumer):
    def __init__(self, *args, **kwargs):
        log.debug("Game Consumer: %s %s", args, kwargs)
        super().__init__(*args, **kwargs)
        self.group_name = "battleships"
        self.engine = GameEngine(self.group_name)
        self.engine.start()

    def player_new(self, event):
        log.debug("Player Joined: %s", event["player"])
        self.engine.join_queue(event["player"])

    def receive_shoot(self, event):
        log.debug("Player shooting: %s", event['player'])
        shoot = event.get("shoot", None)
        # check if shoot is in A-J 1-10 ?
        if shoot:
            self.engine.shoot(event["player"], shoot)

    def receive_board(self, event):
        log.debug("Player setting pieces: %s", event['player'])
        pieces = event.get("pieces", None)
        if pieces:
            _, list_cells_with_boats_pieces = dict_to_board(pieces)
            self.engine.receive_board(event["player"], list_cells_with_boats_pieces)

#     todo enviar mensajes desde el engine, aca los recibimos y se los enviamos a los players

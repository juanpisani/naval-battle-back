# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

from back.models import GameSession


class GameSessionConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = 'game_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    # todo disconnect

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        command = text_data_json['command']

        if command == 'connected':
            session_id = text_data_json['roomId']
            user_id = text_data_json['userId']
            await self.receive_player(session_id=session_id, user_id=user_id)

    async def receive_player(self, session_id, user_id):
        session = GameSession.objects.get(id=session_id)
        if session.player_1 and session.player_1.id == user_id:
            session.player_1_connected = True
            session.save()
        elif session.player_2 and session.player_2.id == user_id:
            session.player_2_connected = True
            session.save()
        if session.player_1 is not None and session.player_2 is not None:
            if session.player_1_connected and session.player_2_connected:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_start',
                        'message': 'Start game',
                        'player_1': {
                            'id': session.player_1.id,
                            'email': session.player_1.email,
                        },
                        'player_2': {
                            'id': session.player_2.id,
                            'email': session.player_2.email,
                        }
                    }
                )
            else:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'waiting',
                        'message': 'Waiting for session to be full'
                    }
                )
        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'waiting',
                    'message': 'Waiting for session to be full'
                }
            )

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

    async def waiting(self, event):
        message = event['message']
        type = event['type']

        await self.send(text_data=json.dumps({
            'command': type,
            'message': message
        }))

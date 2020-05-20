# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

from back.models import GameSession


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class GameSessionConsumer(AsyncWebsocketConsumer):

    def __init__(self):
        pass

    async def connect(self, data=None):
        self.session_id = data['session_id']

        await self.channel_layer.group_add(
            self.session_id
        )

        await self.accept()

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
                    session_id,
                    {
                        'type': 'game_start',
                        'message': 'Start game'
                    }
                )
        else:
            await self.channel_layer.group_send(
                session_id,
                {
                    'type': 'waiting',
                    'message': 'Waiting for session to be full'
                }
            )

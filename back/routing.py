from channels.routing import ProtocolTypeRouter
from django.urls import re_path

from back import consumers

websocket_urlpatterns = [
    re_path(r'api/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer),
    re_path(r'api/game/(?P<session_id>\w+)/$', consumers.GameSessionConsumer)
]
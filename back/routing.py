from channels.routing import ProtocolTypeRouter
from django.urls import re_path

from back import consumers

websocket_urlpatterns = [
    re_path(r'api/game/(?P<session_id>\w+)/$', consumers.PlayerConsumer),
    re_path(r'api/battleships/(?P<session_id>\w+)/$', consumers.GameConsumer)

]
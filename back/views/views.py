import django_filters
from asgiref.sync import sync_to_async

from django.contrib.auth import get_user_model
from django_filters import FilterSet

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from back.consumers import GameSessionConsumer
from back.models import WaitingUser, GameSession
from back.serializers import UserSerializer, WaitingUserSerializer, GameSessionSerializer
from back.utils import CustomPageNumberPagination
from django.http import Http404

from django.shortcuts import render

User = get_user_model()


class UserFilter(FilterSet):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name'
        )


class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all().filter(is_active=1, is_superuser=0)
    pagination_class = CustomPageNumberPagination
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    search_fields = ('first_name', 'last_name')
    filter_class = UserFilter

    def destroy(self, request, pk=None, **kwargs):
        try:
            user = self.get_object()
            user.is_active = False
            user.save()
        except Http404:
            return Response("User does not exist", 404)

        return Response("User deleted", 204)


class WaitingUserView(viewsets.ModelViewSet):
    serializer_class = WaitingUserSerializer
    queryset = WaitingUser.objects.all()

    def create(self, request, *args, **kwargs):
        if WaitingUser.objects.exists():
            waiting = WaitingUser.objects.first()
            try:
                if waiting.user.id == request.user.id:
                    waiting.delete()
                    GameSession.objects.get(id=waiting.game_session_id).delete()
                else:
                    session = GameSession.objects.get(id=waiting.game_session_id)
                    session.player_2 = request.user
                    session.save()
                    waiting.delete()
                    # consumer = GameSessionConsumer()
                    # sync_to_async(consumer.connect(data={'session_id': session.id}))
                    return Response({
                        'game_session_id': session.id
                    }, 200)
            except GameSession.DoesNotExist:
                return Response({
                    'message': 'Game session does not exist'
                }, 400)
        session_serializer = GameSessionSerializer(data={'player_1': request.user.id}, context={'request': request})
        if session_serializer.is_valid():
            session_serializer.save()
        request.data['user'] = request.user.id
        request.data['game_session_id'] = session_serializer.instance.id
        # consumer = GameSessionConsumer()
        # sync_to_async(consumer.connect(data={'session_id': request.data['game_session_id']}))
        super(WaitingUserView, self).create(request, *args, **kwargs)
        return Response({
            'game_session_id': session_serializer.instance.id
        }, 200)


class GameSessionView(viewsets.ModelViewSet):
    serializer_class = GameSessionSerializer
    queryset = GameSession.objects.filter(is_active=True)


def index(request):
    return render(request, 'index.html')


def room(request, room_name):
    return render(request, 'room.html', {
        'room_name': room_name
    })

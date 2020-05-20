import django_filters

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

    async def create(self, request, *args, **kwargs):
        # if WaitingUser.objects.exists():
        #     try:
        #         old = WaitingUser.objects.get(user__id=request.user.id)
        #         old.delete()
        #     except WaitingUser.DoesNotExist:
        #         waiting_user = WaitingUser.objects.first()
        #         data = {
        #             'player_1': request.user.id,
        #             'player_2': waiting_user.user.id
        #         }
        #         session = GameSessionSerializer(data=data, context={'request': self.request})
        #         if session.is_valid():
        #             session.save()
        #             waiting_user.delete()
        #             return Response({
        #                 'game_session': session.data
        #             }, 200)
        #         else:
        #             return Response({
        #                 'error': 'Could not create game session',
        #                 'detail': session.errors
        #             }, 400)
        # request.data['user'] = request.user.id
        if WaitingUser.objects.exists():
            waiting = WaitingUser.objects.first()
            try:
                session = GameSession.objects.get(id=waiting.game_session_id)
                session.player_2 = request.user
                session.save()
                waiting.delete()
                consumer = GameSessionConsumer()
                await consumer.connect(data={'session_id': session.id})
                return Response({
                    'game_session': session.data
                }, 200)
            except GameSession.DoesNotExist:
                return Response({
                    'message': 'Game session does not exist'
                }, 400)
        else:
            session_serializer = GameSessionSerializer(data={'player_1': request.user.id}, context={'request': request})
            if session_serializer.is_valid():
                session_serializer.save()
        request.data['user'] = request.user.id
        request.data['game_session_id'] = session_serializer.instance.id
        response = super(WaitingUserView, self).create(request, *args, **kwargs)
        consumer = GameSessionConsumer()
        await consumer.connect(data={'session_id': session_serializer.id})
        return response


class GameSessionView(viewsets.ModelViewSet):
    serializer_class = GameSessionSerializer
    queryset = GameSession.objects.filter(is_active=True)


def index(request):
    return render(request, 'index.html')


def room(request, room_name):
    return render(request, 'room.html', {
        'room_name': room_name
    })

from datetime import datetime, timezone
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.contrib.auth import get_user_model  # If used custom user model
from rest_framework.validators import UniqueValidator

from back.models import WaitingUser, GameSession
from back.utils import get_default_admin_user

UserModel = get_user_model()


class BaseSerializer(serializers.ModelSerializer):
    read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',)

    class Meta:
        abstract = True

    def create(self, validated_data):

        user = self.context['request'].user
        if user.is_anonymous:
            user = get_default_admin_user()
        if 'request' in self.context:
            validated_data['created_by'] = user
            validated_data['updated_by'] = user

        return super(BaseSerializer, self).create(validated_data)

    def update(self, instance, validated_data):

        if 'request' in self.context:
            user = self.context['request'].user
            if user.is_anonymous:
                user = get_default_admin_user()
            validated_data['updated_by'] = user

        return super(BaseSerializer, self).update(instance, validated_data)


class CurrentUserSerializer(BaseSerializer):
    class Meta:
        model = UserModel
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    email = serializers.CharField(max_length=100, validators=[UniqueValidator(queryset=UserModel.objects.filter(is_active=True))])
    username = serializers.CharField(max_length=100, validators=[UniqueValidator(queryset=UserModel.objects.filter(is_active=True))])

    def create(self, validated_data):
        if UserModel.objects.filter(is_active=False, username=validated_data['username']).exists():
            UserModel.objects.filter(username=validated_data['username']).update(**validated_data, is_active=True)
            return UserModel.objects.get(username=validated_data['username'])

        user = UserModel.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).update(instance, validated_data)

    class Meta:
        model = UserModel
        fields = ("id", "email", "username", "password", "first_name", "last_name")
        read_only_fields = ('id',)


class UsernameSerializer(BaseSerializer):
    class Meta:
        model = UserModel
        fields = ('username',)

        extra_kwargs = {
            'username': {'validators': []},
        }


class GoogleSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True)


class WaitingUserSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.filter(is_active=True), required=False)
    game_session_id = serializers.CharField(max_length=10, required=False)

    def validate(self, attrs):
        try:
            old = WaitingUser.objects.filter(user__id=attrs['user'].id)
            old.delete()
        except WaitingUser.DoesNotExist:
            pass
        return attrs

    class Meta:
        model = WaitingUser
        fields = '__all__'


class GameSessionSerializer(BaseSerializer):
    player_1 = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.filter(is_active=True), required=False)
    player_2 = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.filter(is_active=True), required=False)
    player_1_connected = serializers.BooleanField(required=False, default=False)
    player_2_connected = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = GameSession
        fields = '__all__'


class CellSerializer(serializers.Serializer):
    boat = serializers.BooleanField()

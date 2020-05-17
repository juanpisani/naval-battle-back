from calendar import timegm
from datetime import datetime

import jwt
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.serializers import RefreshJSONWebTokenSerializer
from rest_framework_jwt.views import ObtainJSONWebToken, JSONWebTokenAPIView
import requests
from rest_framework import viewsets


from back.models import User
from back.serializers import CurrentUserSerializer, UserSerializer, GoogleSerializer
from back.utils import LogUtilMixin, random_string

from django.contrib.auth import get_user_model

from server import settings

UserModel = get_user_model()


class MyObtainJSONWebToken(ObtainJSONWebToken, LogUtilMixin):

    def post(self, request, *args, **kwargs):
        response = super(MyObtainJSONWebToken, self).post(request, args, kwargs)

        if response.status_code == status.HTTP_200_OK:
            user = UserModel.objects.get(username=request.data['username'])
            response.data['user'] = CurrentUserSerializer(user).data
        return response


class RefreshJSONWebToken(JSONWebTokenAPIView):
    """
    API View that returns a refreshed token (with new expiration) based on
    existing token

    If 'orig_iat' field (original issued-at-time) is found, will first check
    if it's within expiration window, then copy it to the new token
    """
    serializer_class = RefreshJSONWebTokenSerializer


class GoogleLogin(ObtainJSONWebToken):

    def get_serializer(self, *args, **kwargs):
        return GoogleSerializer()

    def post(self, request, *args, **kwargs):

        id_token = request.data['id_token']

        if id_token:
            decoded = jwt.decode(id_token, '', verify=False)
            try:

                my_user = User.objects.get(email=decoded['email'])

            except User.DoesNotExist:
                user_data = {
                    'username': decoded['email'],
                    'password': random_string(8),
                    'email': decoded['email'],
                    'first_name': decoded['given_name'],
                    'last_name': decoded['family_name']
                }
                user_instance = UserSerializer(data=user_data, context={'request': self.request})
                if user_instance.is_valid():
                    my_user = user_instance.save()
                else:
                    return Response(user_instance.errors, 400)

            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(my_user)

            # Include original issued at time for a brand new token,
            # to allow token refresh
            if api_settings.JWT_ALLOW_REFRESH:
                payload['orig_iat'] = timegm(
                    datetime.utcnow().utctimetuple()
                )

            return Response({
                'token': jwt_encode_handler(payload),
                'user': CurrentUserSerializer(instance=my_user).data
            }, 200)
        return Response("invalid Token", 400)


obtain_jwt_token = MyObtainJSONWebToken.as_view()
google_login = GoogleLogin.as_view()
refresh_jwt_token = RefreshJSONWebToken.as_view()


from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers, permissions
from rest_framework.documentation import include_docs_urls

from back.views import views
from back.views.authviews import obtain_jwt_token, google_login

router = routers.DefaultRouter()
router.register(r'users', views.UserView)
router.register(r'waiting_user', views.WaitingUserView)
router.register(r'game_session', views.GameSessionView)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^docs/', include_docs_urls(
        title='Naval Battle Back API',
        description='An API to interact with the Naval Battle App',
        permission_classes=[permissions.AllowAny],
    )),
    url(r'auth/login/', obtain_jwt_token),
    url(r'google/login/', google_login),
    path('chat/', views.index, name='index'),
    path('chat/<str:room_name>/', views.room, name='room'),

]

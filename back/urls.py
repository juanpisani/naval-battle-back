from django.conf.urls import url, include
from rest_framework import routers, permissions
from rest_framework.documentation import include_docs_urls

from back.views import views
from back.views.authviews import obtain_jwt_token, google_login

router = routers.DefaultRouter()
router.register(r'users', views.UserView)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^docs/', include_docs_urls(
        title='Naval Battle Back API',
        description='An API to interact with the Naval Battle App',
        permission_classes=[permissions.AllowAny],
    )),
    url(r'auth/login/', obtain_jwt_token),
    url(r'google/login/', google_login),

]

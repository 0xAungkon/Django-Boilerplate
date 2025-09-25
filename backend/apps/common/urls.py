from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.common.controllers.PlatformApi.PlatformAPI import APITokenModelViewSet
from .controllers.Authentication.LoginController import LoginAPIView
from .controllers.Authentication.RegistrationController import RegisterAPIView
from .controllers.Common.ProfileController import ProfileAPIView

# from .controllers.PlatformApi

router = DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("auth/login", LoginAPIView.as_view(), name="login"),
    path("auth/register", RegisterAPIView.as_view(), name="registration"),
    path("common/profile", ProfileAPIView.as_view(), name="login"),
    path("", include("common.routers.RouterEnvelop")),  # include the second router
]

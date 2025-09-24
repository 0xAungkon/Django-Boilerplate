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
    path(
        "plartform/api/",
        APITokenModelViewSet.as_view({"get": "list", "post": "create"}),
        name="envelop-document-list",
    ),
    path(
        "plartform/api/<int:pk>/",
        APITokenModelViewSet.as_view({"patch": "partial_update", "delete": "destroy"}),
        name="envelop-document-detail",
    ),
    # path('platform_api/token',APITokenModelViewSet.as_view(), name="platform_apis" ),
    path("", include("common.routers.RouterEnvelop")),  # include the second router
]

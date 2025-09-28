from django.urls import path, include
from apps.common.controllers.PlatformApi.PlatformAPI import APITokenModelViewSet
from .controllers.Authentication.LoginController import LoginAPIView
from .controllers.Authentication.RegistrationController import RegisterAPIView
from .controllers.Common.ProfileController import ProfileAPIView
from .controllers.Common.VaultController import VaultViewSet
from .controllers.Common.SSHCredsController import SSHCredsViewSet
from .controllers.Common.SSHServersController import SSHServersViewSet

urlpatterns = [
    # Auth endpoints
    path("auth/login", LoginAPIView.as_view(), name="login"),
    path("auth/register", RegisterAPIView.as_view(), name="registration"),
    path("common/profile", ProfileAPIView.as_view(), name="profile"),

    # Vault endpoints
    path(
        "vaults/",
        VaultViewSet.as_view({"get": "list", "post": "create"}),
        name="vault-list",
    ),
    path(
        "vaults/<uuid:pk>/",
        VaultViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"}),
        name="vault-detail",
    ),

    # SSH Credentials endpoints
    path(
        "ssh-credentials/",
        SSHCredsViewSet.as_view({"get": "list", "post": "create"}),
        name="sshcreds-list",
    ),
    path(
        "ssh-credentials/<uuid:pk>/",
        SSHCredsViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"}),
        name="sshcreds-detail",
    ),

    # SSH Servers endpoints
    path(
        "ssh-servers/",
        SSHServersViewSet.as_view({"get": "list", "post": "create"}),
        name="sshservers-list",
    ),
    path(
        "ssh-servers/<uuid:pk>/",
        SSHServersViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"}),
        name="sshservers-detail",
    ),

    # Platform API endpoints
    path(
        "platform/api/",
        APITokenModelViewSet.as_view({"get": "list", "post": "create"}),
        name="envelop-document-list",
    ),
    path(
        "platform/api/<uuid:pk>/",
        APITokenModelViewSet.as_view({"patch": "partial_update", "delete": "destroy"}),
        name="envelop-document-detail",
    ),
]

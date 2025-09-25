from rest_framework.routers import DefaultRouter
from django.urls import path
from apps.common.controllers.PlatformApi.PlatformAPI import APITokenModelViewSet

router = DefaultRouter()

urlpatterns = [
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
]


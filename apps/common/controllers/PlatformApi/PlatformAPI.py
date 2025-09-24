import secrets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets, serializers
from common.models.PlatformApi import APITokenModel


class APITokenModelSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    is_deleted = serializers.BooleanField(read_only=True)
    deleted_at = serializers.DateTimeField(read_only=True)
    token = serializers.CharField(read_only=True)
    user = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")
        if request and request.method == "POST":
            return representation

        token = representation.get("token", "")
        if token:
            representation["token"] = "*" * (len(token) - 2) + token[-2:]
        return representation

    class Meta:
        model = APITokenModel
        fields = "__all__"


class APITokenModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = APITokenModelSerializer
    queryset = APITokenModel.objects.all().filter(is_deleted=False)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if request.is_plartform:
            raise PermissionDenied(
                "You do not have permission to access this resource."
            )

    def perform_create(self, serializer):
        random_token = f"wsign_{secrets.token_urlsafe(32)}"
        serializer.save(token=random_token, user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save(update_fields=["is_deleted", "deleted_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)

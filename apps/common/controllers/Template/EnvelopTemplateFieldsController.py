from rest_framework import viewsets, permissions, serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from common.models import EnvelopFieldTemplateModel
from django.utils import timezone
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from common.controllers.Envelop.EnvelopFieldsController import (
    EnvelopFieldItemSerializer as EnvelopTemplateFieldItemSerializer,
)


class EnvelopTemplateFieldGroupSerializer(serializers.Serializer):
    field_recipent_id = serializers.CharField()
    fields = serializers.ListField(
        child=EnvelopTemplateFieldItemSerializer(),
        allow_empty=True,
        required=False,
    )


class EnvelopTemplateFieldsMetaSerializer(serializers.ModelSerializer):
    field_data = serializers.ListField(
        child=EnvelopTemplateFieldGroupSerializer(),
    )

    class Meta:
        model = EnvelopFieldTemplateModel
        fields = ["uid", "envelop", "field_data"]


class EnvelopTemplateFieldsViewSet(viewsets.ModelViewSet):
    queryset = EnvelopFieldTemplateModel.objects.all()
    serializer_class = EnvelopTemplateFieldsMetaSerializer
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["created_at"]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()
        return Response(status=204)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

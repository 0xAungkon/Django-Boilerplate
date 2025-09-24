from rest_framework import viewsets, permissions, serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from common.models import EnvelopTemplateModel
from django.utils import timezone
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend


class EnvelopTemplateRecipientSerializer(serializers.Serializer):
    R_TYPE = (
        ("signer", "Signer"),
        ("copier", "Copier"),
        ("view", "View"),
    )
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    r_type = serializers.ChoiceField(choices=R_TYPE)
    message = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    access_code = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )


class EnvelopTemplateSerializer(serializers.ModelSerializer):
    recipients = serializers.DictField(
        child=EnvelopTemplateRecipientSerializer(),
        help_text="Dictionary with integer keys and recipient details as values",
    )

    class Meta:
        model = EnvelopTemplateModel
        fields = ["uid", "document_id", "recipients", "message_subject", "message_body"]


class EnvelopTemplateRecipentsViewSet(viewsets.ModelViewSet):
    queryset = EnvelopTemplateModel.objects.all()
    serializer_class = EnvelopTemplateSerializer
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["created_at"]
    lookup_field = "uid"  # Set lookup field to uid for UUID retrieval

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()
        return Response(status=204)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, user=self.request.user)

    def use_template(self, request, pk=None):
        try:
            instance = EnvelopTemplateModel.objects.get(uid=pk, is_deleted=False)
        except EnvelopTemplateModel.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)

        return Response({"detail": f"Template {pk} used successfully."}, status=200)

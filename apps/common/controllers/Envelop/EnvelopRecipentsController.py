from rest_framework import viewsets, permissions, serializers
from common.models import EnvelopModel
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from common.controllers.Envelop.EnvelopFieldsController import (
    EnvelopFieldsMetaSerializer,
)
from common.controllers.Envelop.EnvelopValuesController import (
    EnvelopValuesMetaSerializer,
)
from rest_framework import status


class EnvelopRecipientSerializer(serializers.Serializer):
    R_TYPE = (
        ("signer", "Signer"),
        ("copier", "Copier"),
        ("view", "View"),
    )

    order = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.EmailField()
    r_type = serializers.ChoiceField(choices=R_TYPE)
    message = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    access_code = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )

class BaseEnvelopSerializerMeta:
    model = EnvelopModel
    read_only_fields = ["status","created_by"]

class EnvelopSerializer(serializers.ModelSerializer):
    recipients = serializers.DictField(
        child=EnvelopRecipientSerializer(),
        help_text="Dictionary with recipient email as keys and recipient details as values",
    )
    user_envelope_status = serializers.SerializerMethodField(
        read_only=True,
        method_name="get_user_envelope_status",
        help_text="Returns the current user's status for this recipient.",
    )

    def get_user_envelope_status(self, obj: EnvelopModel):
        """
        Returns the current user's status for this recipient.
        This is a placeholder method; actual implementation may vary.
        """
        # Example logic, replace with actual status retrieval logic
        user_mail = self.context.get("request").user.email
        return obj.get_current_stage_for_user_mail(user_mail)

    def validate_recipients(self, value):
        # Ensure keys are valid emails and match the email in the value
        for email, recipient in value.items():
            if email != recipient.get("email"):
                raise serializers.ValidationError(
                    f"Key '{email}' does not match recipient email '{recipient.get('email')}'"
                )
        return value

    class Meta(BaseEnvelopSerializerMeta):
        # model = EnvelopModel
        exclude = [
            # "user",
            "message_body",
            # "user",
            "updated_at",
        ]
        # read_only_fields = ["status","created_by"]


class EnvelopeDetailSerializer(EnvelopSerializer):
    values = EnvelopValuesMetaSerializer(many=True, read_only=True)
    field = EnvelopFieldsMetaSerializer(read_only=True)

    class Meta(BaseEnvelopSerializerMeta):
        # model = EnvelopModel
        exclude = [
            # "user",
            "updated_at",
        ]
        # read_only_fields = ["status","created_by"]


class EnvelopeListSerializer(EnvelopSerializer):
    class Meta(BaseEnvelopSerializerMeta):
        # model = EnvelopModel
        exclude = [
            # "user",
            "message_body",
            "updated_at",
        ]
        # read_only_fields = ["status","created_by"]


class EnvelopModelFilter(filters.FilterSet):
    box_type = filters.CharFilter(method="filter_box_type")

    def filter_box_type(self, queryset, name, value):
        user = self.request.user
        if value == "inbox":
            return EnvelopModel.get_envelop_by_recipients_mail(user.email, queryset)
        elif value == "sent":
            return EnvelopModel.get_envelop_by_user(user, queryset)
        return (
            EnvelopModel.get_envelop_by_recipients_mail(user.email, queryset)
            | EnvelopModel.get_envelop_by_user(user, queryset)
        ).distinct()

    class Meta:
        model = EnvelopModel
        fields = ["box_type"]


class EnvelopRecipentsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EnvelopModelFilter

    def get_serializer_class(self):
        if self.action == "list":
            return EnvelopeListSerializer
        return EnvelopeDetailSerializer

    def get_queryset(self):
        """
        Applies box_type filtering via FilterSet, defaults to inbox + sent.
        """
        print()
        return EnvelopModel.get_envelop_by_user(
            self.request.user
        ) | EnvelopModel.get_envelop_by_recipients_mail(
            self.request.user.email
        )  # Default fallback; real filtering is in FilterSet

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="box_type",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Filter by box type: inbox, sent, or both",
                required=False,
                enum=["inbox", "sent"],
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete: Only creator can delete their envelopes.
        """
        instance: EnvelopModel = self.get_object()
        if instance.created_by != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

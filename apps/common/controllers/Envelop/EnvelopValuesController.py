from rest_framework import viewsets, permissions, serializers
from common.models import EnvelopValueModel
from django.utils import timezone
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError


class EnvelopFieldValueSerializer(serializers.Serializer):
    field_id = serializers.CharField()
    field_value = (
        serializers.JSONField()
    )  # Assuming field_value can be any JSON serializable data type


class EnvelopValuesMetaSerializer(serializers.ModelSerializer):
    field_data = serializers.ListField(
        child=EnvelopFieldValueSerializer(),
    )

    class Meta:
        model = EnvelopValueModel
        fields = ["uid", "envelop", "field_data"]


class EnvelopValuesViewSet(viewsets.ModelViewSet):
    queryset = EnvelopValueModel.objects.all()
    serializer_class = EnvelopValuesMetaSerializer
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        validated_data = serializer.validated_data

        envelop = validated_data.get("envelop")
        field_data = validated_data.get("field_data")

        # Check if user has permission to access the envelope
        permitted_envelopes = envelop.get_envelops_by_recipients_mail_or_user(
            user
        ).values_list("uid", flat=True)

        if envelop.uid not in permitted_envelopes:
            raise ValidationError(
                "You do not have permission to add values to this envelope."
            )

        # Check if user is at the correct signing order stage
        # field_meta_data = envelop.field.field_data
        # todo: implementing restrictions

        # user_order = field_meta_data.get(user.email, {}).get("order")
        # if int(envelop.status) != user_order:
        #     raise ValidationError("You cannot add values to this envelope at this stage.")

        # Validate each field_data item
        for item in field_data:
            if not item.get("field_id"):
                raise ValidationError("Field ID is required.")
            if item.get("field_value") is None:
                raise ValidationError("Field value is required.")

        # TODO: this needs to implemented correctly
        # NOTE: THIS IS ONLY UPDATING FROM CURRENT USER. [This will implement after descussion]
        # envelop.update_current_stage(
        #     str(
        #         int(
        #              .recipients.get(user.email, {}).get("order", 1)
        #             + 1  # Incrementing the order by 1
        #             + 1  # for zero indexing
        #         )
        #     )
        # )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

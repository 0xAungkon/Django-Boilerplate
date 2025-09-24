from rest_framework import viewsets, permissions, serializers
from common.models import EnvelopFieldModel
from django.utils import timezone
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal


class EnvelopFieldItemSerializer(serializers.Serializer):
    FIELD_TYPE_CHOICES = [
        ("text", "Text"),
        ("number", "Number"),
        ("email", "Email"),
        ("password", "Password"),
        ("checkbox", "Checkbox"),
        ("textarea", "Textarea"),
        ("select", "Select"),
        ("date", "Date"),
        ("tel", "Telephone"),
        ("url", "URL"),
        ("signature", "Signature"),
        ("file", "File"),
    ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        for key, value in ret.items():
            if isinstance(value, Decimal):
                ret[key] = str(value)
        return ret

    field_uuid = serializers.CharField(required=True)
    attr_required = serializers.BooleanField(default=False)
    attr_value = serializers.JSONField()
    attr_page = serializers.IntegerField(default=1, min_value=1)
    attr_pos_x = serializers.FloatField(
        # decimal_places=10,
        # max_digits=20,
        allow_null=True,
        required=False,
    )
    attr_pos_y = serializers.FloatField(
        # decimal_places=10,
        # max_digits=20,
        allow_null=True,
        required=False,
    )
    attr_width = serializers.FloatField(
        # decimal_places=10,
        # max_digits=20,
        allow_null=True,
        required=False,
    )
    attr_height = serializers.FloatField(
        # decimal_places=10,
        # max_digits=20,
        allow_null=True,
        required=False,
    )
    attr_type = serializers.ChoiceField(
        choices=FIELD_TYPE_CHOICES,
        allow_blank=False,
        allow_null=False,
    )
    attr_placeholder = serializers.CharField(
        allow_null=True,
        allow_blank=True,
        required=False,
    )
    attr_options = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
        required=False,
    )
    attr_style = serializers.DictField(
        child=serializers.CharField(),
        allow_empty=True,
        required=False,
    )


class EnvelopFieldGroupSerializer(serializers.Serializer):
    fields = serializers.ListField(
        child=EnvelopFieldItemSerializer(),
        allow_empty=True,
        required=False,
    )


class EnvelopFieldsMetaSerializer(serializers.ModelSerializer):
    field_data = serializers.DictField(
        child=EnvelopFieldGroupSerializer(),
    )

    class Meta:
        model = EnvelopFieldModel
        fields = ["uid", "envelop", "field_data"]


class EnvelopFieldsViewSet(viewsets.ModelViewSet):
    queryset = EnvelopFieldModel.objects.all()
    serializer_class = EnvelopFieldsMetaSerializer
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

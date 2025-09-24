from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import permissions, serializers
from django_filters.rest_framework import DjangoFilterBackend
from common.models import EnvelopDocumentModel
from django.http import FileResponse


class EnvelopDocumentSerializer(serializers.ModelSerializer):
    file_path = serializers.FileField(read_only=True)

    class Meta:
        model = EnvelopDocumentModel
        fields = ["uid", "file_name", "file_size", "status", "file_path"]


class EnvelopDocumentUploadSerializer(serializers.Serializer):
    document = serializers.FileField()
    file_name = serializers.CharField(max_length=255, required=False)


class EnvelopDocumentViewSet(viewsets.ModelViewSet):
    queryset = EnvelopDocumentModel.objects.all().order_by("-created_at")
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["created_at"]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == "create":
            return EnvelopDocumentUploadSerializer
        return EnvelopDocumentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data["document"]
        file_name = serializer.validated_data.get("file_name") or uploaded_file.name
        file_size = uploaded_file.size

        # Save file using the model's DocumentField (S3 or local, as configured)
        doc = EnvelopDocumentModel.objects.create(
            file_name=file_name,
            file_size=file_size,
            uploaded_by=request.user,
            status=True,
            created_by=request.user,
            file_path=uploaded_file,
        )

        return Response(
            {"uid": doc.uid, "file_path": doc.file_path.url if doc.file_path else None},
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.file_path:
            response = FileResponse(
                instance.file_path, as_attachment=True, filename=instance.file_name
            )
            return response
        return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)

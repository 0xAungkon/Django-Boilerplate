# Import necessary libraries
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import serializers
from django.utils import timezone
from common.models.Workspace import WorkspaceModel


# Serializer for workspace information
class WorkspaceSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = WorkspaceModel
        fields = ['uid', 'name', 'is_active', 'user', 'created_at', 'updated_at']
        read_only_fields = ['uid', 'user', 'created_at', 'updated_at']


# Serializer for creating/updating workspace
class WorkspaceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceModel
        fields = ['name', 'is_active']
        
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Workspace name cannot be empty.")
        return value.strip()


# ViewSet for workspace CRUD operations
class WorkspaceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = WorkspaceModel.objects.filter(is_deleted=False)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return WorkspaceCreateUpdateSerializer
        return WorkspaceSerializer
    
    def get_queryset(self):
        # Filter to only show user's own workspaces
        return WorkspaceModel.objects.filter(
            user=self.request.user, 
            is_deleted=False
        ).order_by('-created_at')
    
    @swagger_auto_schema(
        operation_description="List all workspaces for the authenticated user",
        responses={200: WorkspaceSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new workspace",
        request_body=WorkspaceCreateUpdateSerializer,
        responses={
            201: WorkspaceSerializer(),
            400: openapi.Response('Bad Request')
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Set the user to the current authenticated user
            workspace = serializer.save(user=request.user)
            response_serializer = WorkspaceSerializer(workspace)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Retrieve a specific workspace",
        responses={
            200: WorkspaceSerializer(),
            404: openapi.Response('Not Found')
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update a workspace",
        request_body=WorkspaceCreateUpdateSerializer,
        responses={
            200: WorkspaceSerializer(),
            400: openapi.Response('Bad Request'),
            404: openapi.Response('Not Found')
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update a workspace",
        request_body=WorkspaceCreateUpdateSerializer,
        responses={
            200: WorkspaceSerializer(),
            400: openapi.Response('Bad Request'),
            404: openapi.Response('Not Found')
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Soft delete a workspace",
        responses={
            204: openapi.Response('No Content'),
            404: openapi.Response('Not Found')
        }
    )
    def destroy(self, request, *args, **kwargs):
        # Soft delete implementation
        instance = self.get_object()
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['is_deleted', 'deleted_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)
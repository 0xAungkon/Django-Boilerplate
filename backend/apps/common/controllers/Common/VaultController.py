# Import necessary libraries
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import serializers
from django.utils import timezone
from common.models.Vault import VaultModel
from common.models.Workspace import WorkspaceModel


# Serializer for vault information
class VaultSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    
    class Meta:
        model = VaultModel
        fields = [
            'uid', 'device_uid', 'workspace', 'workspace_name', 'meta_data', 
            'os_hostname', 'os_user', 'os_base', 'vault_name', 'is_active', 
            'user', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uid', 'user', 'workspace_name', 'created_at', 'updated_at']


# Serializer for creating/updating vault
class VaultCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaultModel
        fields = [
            'device_uid', 'workspace', 'meta_data', 'os_hostname', 
            'os_user', 'os_base', 'vault_name', 'is_active'
        ]
        
    def validate_vault_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Vault name cannot be empty.")
        return value.strip()
    
    def validate_os_hostname(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("OS hostname cannot be empty.")
        return value.strip()
    
    def validate_os_user(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("OS user cannot be empty.")
        return value.strip()
    
    def validate_workspace(self, value):
        # Ensure the workspace belongs to the current user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if value.user != request.user:
                raise serializers.ValidationError("You can only create vaults in your own workspaces.")
        return value


# ViewSet for vault CRUD operations
class VaultViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = VaultModel.objects.filter(is_deleted=False)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return VaultCreateUpdateSerializer
        return VaultSerializer
    
    def get_queryset(self):
        # Filter to only show user's own vaults
        return VaultModel.objects.filter(
            user=self.request.user, 
            is_deleted=False
        ).select_related('workspace', 'user').order_by('-created_at')
    
    @swagger_auto_schema(
        operation_description="List all vaults for the authenticated user",
        responses={200: VaultSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new vault",
        request_body=VaultCreateUpdateSerializer,
        responses={
            201: VaultSerializer(),
            400: openapi.Response('Bad Request')
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Set the user to the current authenticated user
            vault = serializer.save(user=request.user)
            response_serializer = VaultSerializer(vault)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Retrieve a specific vault",
        responses={
            200: VaultSerializer(),
            404: openapi.Response('Not Found')
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update a vault",
        request_body=VaultCreateUpdateSerializer,
        responses={
            200: VaultSerializer(),
            400: openapi.Response('Bad Request'),
            404: openapi.Response('Not Found')
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update a vault",
        request_body=VaultCreateUpdateSerializer,
        responses={
            200: VaultSerializer(),
            400: openapi.Response('Bad Request'),
            404: openapi.Response('Not Found')
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Soft delete a vault",
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
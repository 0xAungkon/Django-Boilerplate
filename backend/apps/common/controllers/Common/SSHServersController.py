# Import necessary libraries
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import serializers
from django.utils import timezone
from common.models.SSHServers import SSHServersModel
from common.models.Vault import VaultModel
from common.models.SSHCreds import SSHCredsModel


# Serializer for SSH server information
class SSHServersSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)
    vault_name = serializers.CharField(source='vault.vault_name', read_only=True)
    creds_name = serializers.CharField(source='creds.name', read_only=True)
    # Mask the private key in responses for security
    private_key = serializers.SerializerMethodField()
    
    class Meta:
        model = SSHServersModel
        fields = [
            'uid', 'server_host', 'server_port', 'server_user', 'private_key',
            'metadata', 'creds', 'creds_name', 'user', 'vault', 'vault_name',
            'alias', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uid', 'user', 'vault_name', 'creds_name', 'created_at', 'updated_at']
    
    def get_private_key(self, obj):
        # Mask the private key for security - only show first and last few characters
        if obj.private_key:
            if len(obj.private_key) > 20:
                return obj.private_key[:10] + "..." + obj.private_key[-10:]
            else:
                return "*" * len(obj.private_key)
        return None


# Serializer for creating/updating SSH servers
class SSHServersCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SSHServersModel
        fields = [
            'server_host', 'server_port', 'server_user', 'private_key',
            'metadata', 'creds', 'vault', 'alias', 'is_active'
        ]
        
    def validate_server_host(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Server host cannot be empty.")
        return value.strip()
    
    def validate_server_user(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Server user cannot be empty.")
        return value.strip()
    
    def validate_server_port(self, value):
        if value is not None and (value < 1 or value > 65535):
            raise serializers.ValidationError("Server port must be between 1 and 65535.")
        return value
    
    def validate_vault(self, value):
        # Ensure the vault belongs to the current user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if value.user != request.user:
                raise serializers.ValidationError("You can only create SSH servers in your own vaults.")
        return value
    
    def validate_creds(self, value):
        # Ensure the credentials belong to the current user (if provided)
        if value is not None:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                if value.user != request.user:
                    raise serializers.ValidationError("You can only use your own SSH credentials.")
        return value
    
    def validate(self, data):
        # Ensure either creds or private_key is provided, but not both
        creds = data.get('creds')
        private_key = data.get('private_key')
        
        if not creds and not private_key:
            raise serializers.ValidationError(
                "Either SSH credentials or private key must be provided."
            )
        
        if creds and private_key:
            raise serializers.ValidationError(
                "Cannot specify both SSH credentials and private key. Choose one."
            )
        
        return data


# Serializer for listing SSH servers without sensitive data
class SSHServersListSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)
    vault_name = serializers.CharField(source='vault.vault_name', read_only=True)
    creds_name = serializers.CharField(source='creds.name', read_only=True)
    has_private_key = serializers.SerializerMethodField()
    
    class Meta:
        model = SSHServersModel
        fields = [
            'uid', 'server_host', 'server_port', 'server_user', 'has_private_key',
            'creds', 'creds_name', 'user', 'vault', 'vault_name',
            'alias', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uid', 'user', 'vault_name', 'creds_name', 'created_at', 'updated_at']
    
    def get_has_private_key(self, obj):
        return bool(obj.private_key)


# ViewSet for SSH servers CRUD operations
class SSHServersViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = SSHServersModel.objects.filter(is_deleted=False)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SSHServersCreateUpdateSerializer
        elif self.action == 'list':
            return SSHServersListSerializer
        return SSHServersSerializer
    
    def get_queryset(self):
        # Filter to only show user's own SSH servers
        return SSHServersModel.objects.filter(
            user=self.request.user, 
            is_deleted=False
        ).select_related('vault', 'creds', 'user').order_by('-created_at')
    
    @swagger_auto_schema(
        operation_description="List all SSH servers for the authenticated user (without sensitive data)",
        responses={200: SSHServersListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new SSH server",
        request_body=SSHServersCreateUpdateSerializer,
        responses={
            201: SSHServersSerializer(),
            400: openapi.Response('Bad Request')
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Set the user to the current authenticated user
            ssh_server = serializer.save(user=request.user)
            response_serializer = SSHServersSerializer(ssh_server)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Retrieve a specific SSH server (with masked private key)",
        responses={
            200: SSHServersSerializer(),
            404: openapi.Response('Not Found')
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update an SSH server",
        request_body=SSHServersCreateUpdateSerializer,
        responses={
            200: SSHServersSerializer(),
            400: openapi.Response('Bad Request'),
            404: openapi.Response('Not Found')
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update an SSH server",
        request_body=SSHServersCreateUpdateSerializer,
        responses={
            200: SSHServersSerializer(),
            400: openapi.Response('Bad Request'),
            404: openapi.Response('Not Found')
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Soft delete an SSH server",
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
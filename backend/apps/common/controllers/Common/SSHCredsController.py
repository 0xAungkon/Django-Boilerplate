# Import necessary libraries
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import serializers
from django.utils import timezone
from common.models.SSHCreds import SSHCredsModel


# Serializer for SSH credentials information
class SSHCredsSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)
    # Mask the private key in responses for security
    private_key = serializers.SerializerMethodField()
    
    class Meta:
        model = SSHCredsModel
        fields = [
            'uid', 'public_key', 'private_key', 'name', 'user', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uid', 'user', 'created_at', 'updated_at']
    
    def get_private_key(self, obj):
        # Mask the private key for security - only show first and last few characters
        if obj.private_key:
            if len(obj.private_key) > 20:
                return obj.private_key[:10] + "..." + obj.private_key[-10:]
            else:
                return "*" * len(obj.private_key)
        return None


# Serializer for creating/updating SSH credentials
class SSHCredsCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SSHCredsModel
        fields = ['public_key', 'private_key', 'name', 'is_active']
        
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("SSH credential name cannot be empty.")
        return value.strip()
    
    def validate_public_key(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Public key cannot be empty.")
        # Basic validation for SSH public key format
        if not any(value.strip().startswith(prefix) for prefix in ['ssh-rsa', 'ssh-ed25519', 'ssh-dss']):
            raise serializers.ValidationError("Invalid SSH public key format.")
        return value.strip()
    
    def validate_private_key(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Private key cannot be empty.")
        # Basic validation for SSH private key format
        if not ('-----BEGIN' in value and '-----END' in value):
            raise serializers.ValidationError("Invalid SSH private key format.")
        return value.strip()


# Serializer for retrieving SSH credentials without private key
class SSHCredsListSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SSHCredsModel
        fields = [
            'uid', 'public_key', 'name', 'user', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uid', 'user', 'created_at', 'updated_at']


# ViewSet for SSH credentials CRUD operations
class SSHCredsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = SSHCredsModel.objects.filter(is_deleted=False)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SSHCredsCreateUpdateSerializer
        elif self.action == 'list':
            return SSHCredsListSerializer
        return SSHCredsSerializer
    
    def get_queryset(self):
        # Filter to only show user's own SSH credentials
        return SSHCredsModel.objects.filter(
            user=self.request.user, 
            is_deleted=False
        ).order_by('-created_at')
    
    @swagger_auto_schema(
        operation_description="List all SSH credentials for the authenticated user (without private keys)",
        responses={200: SSHCredsListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create new SSH credentials",
        request_body=SSHCredsCreateUpdateSerializer,
        responses={
            201: SSHCredsSerializer(),
            400: openapi.Response('Bad Request')
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Set the user to the current authenticated user
            ssh_creds = serializer.save(user=request.user)
            response_serializer = SSHCredsSerializer(ssh_creds)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Retrieve specific SSH credentials (with masked private key)",
        responses={
            200: SSHCredsSerializer(),
            404: openapi.Response('Not Found')
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update SSH credentials",
        request_body=SSHCredsCreateUpdateSerializer,
        responses={
            200: SSHCredsSerializer(),
            400: openapi.Response('Bad Request'),
            404: openapi.Response('Not Found')
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update SSH credentials",
        request_body=SSHCredsCreateUpdateSerializer,
        responses={
            200: SSHCredsSerializer(),
            400: openapi.Response('Bad Request'),
            404: openapi.Response('Not Found')
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Soft delete SSH credentials",
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
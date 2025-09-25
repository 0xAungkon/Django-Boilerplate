# import necessary libraries
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.models import User

# from apps.common.models.Profile import ProfileModel
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

# import perser
from rest_framework.parsers import MultiPartParser, FormParser


# Define serializers for user profile information and updates
class ProfileInfoSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


# Define serializer for updating user profile information
class ProfileUpdateSerializer(serializers.ModelSerializer):
    signature_image = serializers.ImageField(
        source="profile.signature_img", required=False, allow_null=True
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "signature_image"]

    def update(self, instance, validated_data):
        # Update User fields
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.save()

        # Update Profile signature_img if present
        profile_data = validated_data.get("profile", {})
        signature_img = profile_data.get("signature_img", None)
        if signature_img is not None:
            profile = getattr(instance, "profile", None)
            if profile is not None:
                profile.signature_img = signature_img
                profile.save()
        return instance


# ProfileAPIView handles user profile operations such as retrieving and updating user information
class ProfileAPIView(APIView):
    # Set authentication and permission classes
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    # Define schema for the API view
    @swagger_auto_schema(
        operation_description="Get User Profile",
        responses={200: ProfileInfoSerializer()},
    )
    # GET method to retrieve user profile information
    def get(self, request):
        serializer = ProfileInfoSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PUT method to update user profile information
    @swagger_auto_schema(
        operation_description="Update User Profile",
        request_body=ProfileUpdateSerializer,
        responses={200: ProfileUpdateSerializer()},
    )
    def put(self, request):
        serializer = ProfileUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            info_serializer = ProfileInfoSerializer(request.user)
            return Response(info_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from utils.Microfunctions import is_valid_email
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema

# get the user model
User = get_user_model()


# Serializer for user login
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    # Override the validate method to check credentials
    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if is_valid_email(username):
            user = User.objects.filter(email=username).first()
            if not user:
                raise serializers.ValidationError({"detail": "Invalid email"})
            username = user.username

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError({"detail": "Invalid credentials"})

        attrs["user"] = user
        return attrs


class LoginAPIView(APIView):
    @swagger_auto_schema(
        request_body=LoginSerializer, operation_description="Login API"
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "accessToken": str(refresh.access_token),
                    "refreshToken": str(refresh),
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

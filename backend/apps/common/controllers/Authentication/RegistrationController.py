# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError

# get the user model
User = get_user_model()


# Serializer for user registration
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ("email", "password", "first_name", "last_name")

    # Override the create method to handle user creation
    def create(self, validated_data):

        if User.objects.filter(email=validated_data["email"]).exists():
            raise ValidationError(
                {"email": "User with this email already exists."},
                code=status.HTTP_409_CONFLICT,
            )

        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
        )
        return user


# APIView for user registration
class RegisterAPIView(APIView):
    @swagger_auto_schema(
        request_body=RegisterSerializer, operation_description="User Registration"
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Registration successful"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

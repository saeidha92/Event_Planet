from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer used when a new user signs up."""

    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role"]

    def create(self, validated_data):
        # create_user() takes care of hashing the password for us
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            role=validated_data.get("role", User.Role.PARTICIPANT),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """Small serializer just to show basic user info (used inside other serializers)."""

    class Meta:
        model = User
        fields = ["id", "username", "role"]

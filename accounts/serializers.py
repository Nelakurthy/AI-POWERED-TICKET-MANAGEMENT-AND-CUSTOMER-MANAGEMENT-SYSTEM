from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone_number",
                  "role", "is_active", "date_joined")
        read_only_fields = ("id", "role", "is_active", "date_joined")

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False,
                                     style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone_number", "password")
        read_only_fields = ("id",)

    def validate_email(self, value):
        value = User.objects.normalize_email(value).strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_password(self, value):
        try:
            password_validation.validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        # Public registration can never grant privileged roles.
        return User.objects.create_user(password=password, role=User.Role.CUSTOMER,
                                        is_staff=False, is_superuser=False, **validated_data)

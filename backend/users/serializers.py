from rest_framework import serializers
from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import User
from django.contrib.auth.hashers import make_password


class RegisterSerializer(DocumentSerializer):
    id = serializers.SerializerMethodField(read_only=True)  # ✅ Output id as string
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['id', 'full_name', 'username', 'email', 'password']
        read_only_fields = ('id',)
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'full_name': {'required': True},
        }

    def get_id(self, obj):
        return str(obj.id)  # ✅ Convert ObjectId to string
    
    def validate_email(self, value):
        value = value.lower()
        if User.objects(email=value).first():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_username(self, value):
        if User.objects(username=value).first():
            raise serializers.ValidationError("Username already exists")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.password = make_password(password)
        user.save()
        return user


# ✅ Add below for forgot + reset password

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

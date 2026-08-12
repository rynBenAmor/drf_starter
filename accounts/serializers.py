from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email")



class RegisteredUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password")
        extra_kwargs = {"password": {"write_only":True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        user = authenticate(
                    request=self.context.get('request'),
                    email=attrs['email'],
                    password=attrs['password']
                )
        if not user and not user.is_active:
            raise serializers.ValidationError("Invalid credentials")

        attrs["user"] = user
        return attrs

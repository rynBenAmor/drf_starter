from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from django.contrib.auth import authenticate, login
from .models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "username")



class RegisteredUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "username", "password")
        extra_kwargs = {"password": {"write_only":True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = authenticate(
                    request=self.context.get('request'),
                    email=data['email'],
                    password=data['password']
                )
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User

import os
from dotenv import load_dotenv

from shared.utils.helpers import build_absolute_uri_https

load_dotenv()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        # expires_at_utc = datetime.fromtimestamp(data["exp"], tz=timezone.utc)
        # expires_at_gmt1 = expires_at_utc + timedelta(hours=1)  # Convertir a GMT+1

        # data["expires_at"] = expires_at_gmt1.isoformat()

        data.update({
            'id': user.id,
            'username': user.username if user.username else '',
            'phone_number': user.phone_number if user.phone_number else '',
            'first_name': user.first_name if user.first_name else '',
            'last_name': user.last_name if user.last_name else '',
            'role'  : user.role.name if user.role else ''
        })

        return data
        

        
class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = RefreshToken(attrs['refresh'])

        data['access'] = str(refresh.access_token)

        return data
    
# Serializer completo (creación / admin)
class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        exclude = ['is_superuser', 'is_staff', 'user_permissions', 'groups']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    
    
    def to_representation(self, instance):
        """Override to force HTTPS for file fields"""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # Force HTTPS for photo field
        if data.get('photo'):
            data['photo'] = build_absolute_uri_https(request, data['photo'])
        
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


# Serializer limitado (solo update / partial_update)
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'photo', 'city', 'gender']
        extra_kwargs = {
            'username': {'required': False},
            'password': {'required': False}
        }
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'phone_number', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            phone_number=validated_data.get('phone_number', ''),
            password=validated_data['password'],
            is_active=True,
        )

        return user

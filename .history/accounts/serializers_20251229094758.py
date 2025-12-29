from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ShopkeeperProfile, WholesalerProfile, RiderProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'phone_number', 'user_type', 'is_verified', 'created_at',
        ]
        read_only_fields = ['id', 'is_verified', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'password_confirm', 'user_type']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class ShopkeeperProfileSerializer(serializers.ModelSerializer):
    """Serializer for Shopkeeper Profile"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ShopkeeperProfile
        fields = '__all__'


class WholesalerProfileSerializer(serializers.ModelSerializer):
    """Serializer for Wholesaler Profile"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = WholesalerProfile
        fields = '__all__'


class RiderProfileSerializer(serializers.ModelSerializer):
    """Serializer for Rider Profile"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = RiderProfile
        fields = '__all__'

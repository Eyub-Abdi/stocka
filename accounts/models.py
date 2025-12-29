from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with user type support"""
    
    class UserType(models.TextChoices):
        SHOPKEEPER = 'SHOPKEEPER', 'Shopkeeper'
        WHOLESALER = 'WHOLESALER', 'Wholesaler'
        RIDER = 'RIDER', 'Delivery Rider'
        ADMIN = 'ADMIN', 'Administrator'
    
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.SHOPKEEPER
    )
    phone_number = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class ShopkeeperProfile(models.Model):
    """Profile for shopkeepers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shopkeeper_profile')
    shop_name = models.CharField(max_length=200)
    shop_address = models.TextField()
    shop_location = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    business_registration = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profiles/shopkeepers/', null=True, blank=True)
    
    def __str__(self):
        return self.shop_name


class WholesalerProfile(models.Model):
    """Profile for wholesalers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wholesaler_profile')
    business_name = models.CharField(max_length=200)
    business_address = models.TextField()
    business_location = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    business_registration = models.CharField(max_length=100)
    tax_id = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profiles/wholesalers/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_orders = models.IntegerField(default=0)
    
    def __str__(self):
        return self.business_name


class RiderProfile(models.Model):
    """Profile for delivery riders"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='rider_profile')
    full_name = models.CharField(max_length=200)
    id_number = models.CharField(max_length=50)
    vehicle_type = models.CharField(max_length=50)
    vehicle_registration = models.CharField(max_length=50)
    profile_image = models.ImageField(upload_to='profiles/riders/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_deliveries = models.IntegerField(default=0)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    def __str__(self):
        return self.full_name

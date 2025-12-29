from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ShopkeeperProfile, WholesalerProfile, RiderProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'user_type', 'is_verified', 'created_at']
    list_filter = ['user_type', 'is_verified', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('user_type', 'phone_number', 'is_verified')}),
    )


@admin.register(ShopkeeperProfile)
class ShopkeeperProfileAdmin(admin.ModelAdmin):
    list_display = ['shop_name', 'user', 'shop_location']
    search_fields = ['shop_name', 'shop_location']


@admin.register(WholesalerProfile)
class WholesalerProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'is_verified', 'rating', 'total_orders']
    list_filter = ['is_verified']
    search_fields = ['business_name', 'business_location']


@admin.register(RiderProfile)
class RiderProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'is_available', 'rating', 'total_deliveries']
    list_filter = ['is_available']
    search_fields = ['full_name', 'vehicle_registration']

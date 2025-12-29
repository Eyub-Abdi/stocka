from rest_framework import serializers
from django.utils import timezone
from .models import Delivery, DeliveryTracking, DeliveryStatusHistory
from accounts.serializers import RiderProfileSerializer
from orders.serializers import OrderDetailSerializer


class DeliveryTrackingSerializer(serializers.ModelSerializer):
    """Serializer for delivery tracking updates"""
    class Meta:
        model = DeliveryTracking
        fields = ['id', 'latitude', 'longitude', 'status', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class DeliveryStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for delivery status history"""
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)
    
    class Meta:
        model = DeliveryStatusHistory
        fields = ['id', 'status', 'notes', 'latitude', 'longitude', 'changed_by_name', 'created_at']


class DeliveryListSerializer(serializers.ModelSerializer):
    """Serializer for delivery listing"""
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    rider_name = serializers.CharField(source='rider.full_name', read_only=True)
    shopkeeper_name = serializers.CharField(source='order.shopkeeper.shop_name', read_only=True)
    wholesaler_name = serializers.CharField(source='order.wholesaler.business_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Delivery
        fields = [
            'id', 'order_number', 'rider_name', 'shopkeeper_name', 'wholesaler_name',
            'status', 'status_display', 'delivery_address', 'estimated_delivery_time',
            'actual_delivery_time', 'created_at'
        ]


class DeliveryDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for deliveries"""
    order = OrderDetailSerializer(read_only=True)
    rider = RiderProfileSerializer(read_only=True)
    tracking_updates = DeliveryTrackingSerializer(many=True, read_only=True)
    status_history = DeliveryStatusHistorySerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Delivery
        fields = [
            'id', 'order', 'rider', 'status', 'status_display',
            'pickup_address', 'pickup_latitude', 'pickup_longitude',
            'pickup_contact_name', 'pickup_contact_phone',
            'delivery_address', 'delivery_latitude', 'delivery_longitude',
            'delivery_contact_name', 'delivery_contact_phone', 'delivery_notes',
            'estimated_pickup_time', 'estimated_delivery_time',
            'actual_pickup_time', 'actual_delivery_time',
            'delivery_photo', 'delivery_signature', 'delivery_notes_completed',
            'rider_rating', 'rider_feedback', 'tracking_updates', 'status_history',
            'created_at', 'updated_at'
        ]


class DeliveryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating deliveries"""
    class Meta:
        model = Delivery
        fields = [
            'order', 'pickup_address', 'pickup_latitude', 'pickup_longitude',
            'pickup_contact_name', 'pickup_contact_phone',
            'delivery_address', 'delivery_latitude', 'delivery_longitude',
            'delivery_contact_name', 'delivery_contact_phone', 'delivery_notes',
            'estimated_pickup_time', 'estimated_delivery_time'
        ]


class RiderAssignmentSerializer(serializers.Serializer):
    """Serializer for assigning rider to delivery"""
    rider_id = serializers.IntegerField()
    estimated_pickup_time = serializers.DateTimeField(required=False)
    estimated_delivery_time = serializers.DateTimeField(required=False)


class DeliveryStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating delivery status"""
    status = serializers.ChoiceField(choices=Delivery.DeliveryStatus.choices)
    notes = serializers.CharField(required=False, allow_blank=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    delivery_photo = serializers.ImageField(required=False)
    delivery_signature = serializers.ImageField(required=False)


class RiderRatingSerializer(serializers.Serializer):
    """Serializer for rating rider"""
    rating = serializers.IntegerField(min_value=1, max_value=5)
    feedback = serializers.CharField(required=False, allow_blank=True)

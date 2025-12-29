from django.contrib import admin
from .models import Delivery, DeliveryTracking, DeliveryStatusHistory


class DeliveryTrackingInline(admin.TabularInline):
    model = DeliveryTracking
    extra = 0
    readonly_fields = ['created_at']


class DeliveryStatusHistoryInline(admin.TabularInline):
    model = DeliveryStatusHistory
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'rider', 'status', 'estimated_delivery_time',
        'actual_delivery_time', 'rider_rating', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'rider__full_name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [DeliveryTrackingInline, DeliveryStatusHistoryInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('order', 'rider', 'status')
        }),
        ('Pickup Details', {
            'fields': (
                'pickup_address', 'pickup_latitude', 'pickup_longitude',
                'pickup_contact_name', 'pickup_contact_phone'
            )
        }),
        ('Delivery Details', {
            'fields': (
                'delivery_address', 'delivery_latitude', 'delivery_longitude',
                'delivery_contact_name', 'delivery_contact_phone', 'delivery_notes'
            )
        }),
        ('Timing', {
            'fields': (
                'estimated_pickup_time', 'estimated_delivery_time',
                'actual_pickup_time', 'actual_delivery_time'
            )
        }),
        ('Completion', {
            'fields': (
                'delivery_photo', 'delivery_signature', 'delivery_notes_completed',
                'rider_rating', 'rider_feedback'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = ['delivery', 'status', 'latitude', 'longitude', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['delivery__order__order_number']

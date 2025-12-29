from django.db import models
from accounts.models import RiderProfile
from orders.models import Order


class Delivery(models.Model):
    """Delivery assignments for orders"""
    
    class DeliveryStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Assignment'
        ASSIGNED = 'ASSIGNED', 'Assigned to Rider'
        PICKED_UP = 'PICKED_UP', 'Picked Up'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
        DELIVERED = 'DELIVERED', 'Delivered'
        FAILED = 'FAILED', 'Failed Delivery'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='delivery'
    )
    rider = models.ForeignKey(
        RiderProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING
    )
    
    # Pickup details
    pickup_address = models.TextField()
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    pickup_contact_name = models.CharField(max_length=200)
    pickup_contact_phone = models.CharField(max_length=15)
    
    # Delivery details
    delivery_address = models.TextField()
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_contact_name = models.CharField(max_length=200)
    delivery_contact_phone = models.CharField(max_length=15)
    delivery_notes = models.TextField(blank=True)
    
    # Tracking
    estimated_pickup_time = models.DateTimeField(null=True, blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    actual_pickup_time = models.DateTimeField(null=True, blank=True)
    actual_delivery_time = models.DateTimeField(null=True, blank=True)
    
    # Delivery proof
    delivery_photo = models.ImageField(upload_to='deliveries/proof/', null=True, blank=True)
    delivery_signature = models.ImageField(upload_to='deliveries/signatures/', null=True, blank=True)
    delivery_notes_completed = models.TextField(blank=True)
    
    # Ratings
    rider_rating = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    rider_feedback = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Deliveries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['rider', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Delivery for {self.order.order_number}"


class DeliveryTracking(models.Model):
    """Real-time tracking updates for deliveries"""
    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.CASCADE,
        related_name='tracking_updates'
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    status = models.CharField(max_length=20, choices=Delivery.DeliveryStatus.choices)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Delivery tracking updates'
    
    def __str__(self):
        return f"Tracking for {self.delivery.order.order_number} at {self.created_at}"


class DeliveryStatusHistory(models.Model):
    """Track delivery status changes"""
    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    status = models.CharField(max_length=20, choices=Delivery.DeliveryStatus.choices)
    notes = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    changed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Delivery status histories'
    
    def __str__(self):
        return f"{self.delivery.order.order_number} - {self.status}"

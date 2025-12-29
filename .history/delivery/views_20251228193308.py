from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Avg
from .models import Delivery, DeliveryTracking, DeliveryStatusHistory
from .serializers import (
    DeliveryListSerializer,
    DeliveryDetailSerializer,
    DeliveryCreateSerializer,
    RiderAssignmentSerializer,
    DeliveryStatusUpdateSerializer,
    DeliveryTrackingSerializer,
    RiderRatingSerializer
)
from accounts.models import RiderProfile
from accounts.serializers import RiderProfileSerializer
from orders.models import Order


class DeliveryListCreateView(generics.ListCreateAPIView):
    """List deliveries or create new delivery"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'rider']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DeliveryCreateSerializer
        return DeliveryListSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Riders see their assigned deliveries
        if hasattr(user, 'rider_profile'):
            return Delivery.objects.filter(
                rider=user.rider_profile
            ).select_related('order', 'rider')
        
        # Wholesalers see deliveries for their orders
        elif hasattr(user, 'wholesaler_profile'):
            return Delivery.objects.filter(
                order__wholesaler=user.wholesaler_profile
            ).select_related('order', 'rider')
        
        # Shopkeepers see deliveries for their orders
        elif hasattr(user, 'shopkeeper_profile'):
            return Delivery.objects.filter(
                order__shopkeeper=user.shopkeeper_profile
            ).select_related('order', 'rider')
        
        # Admins see all deliveries
        elif user.is_staff:
            return Delivery.objects.all().select_related('order', 'rider')
        
        return Delivery.objects.none()


class DeliveryDetailView(generics.RetrieveAPIView):
    """Retrieve delivery details"""
    serializer_class = DeliveryDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if hasattr(user, 'rider_profile'):
            return Delivery.objects.filter(rider=user.rider_profile)
        elif hasattr(user, 'wholesaler_profile'):
            return Delivery.objects.filter(order__wholesaler=user.wholesaler_profile)
        elif hasattr(user, 'shopkeeper_profile'):
            return Delivery.objects.filter(order__shopkeeper=user.shopkeeper_profile)
        elif user.is_staff:
            return Delivery.objects.all()
        
        return Delivery.objects.none()


class AssignRiderView(APIView):
    """Assign rider to delivery"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            delivery = Delivery.objects.get(pk=pk)
            
            # Only wholesalers and admins can assign riders
            if not (hasattr(request.user, 'wholesaler_profile') or request.user.is_staff):
                return Response(
                    {"error": "You don't have permission to assign riders"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if wholesaler owns the order
            if hasattr(request.user, 'wholesaler_profile'):
                if delivery.order.wholesaler != request.user.wholesaler_profile:
                    return Response(
                        {"error": "You can only assign riders to your own orders"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            serializer = RiderAssignmentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            rider_id = serializer.validated_data['rider_id']
            rider = RiderProfile.objects.get(id=rider_id)
            
            # Check if rider is available
            if not rider.is_available:
                return Response(
                    {"error": "Rider is not available"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Assign rider
            delivery.rider = rider
            delivery.status = Delivery.DeliveryStatus.ASSIGNED
            
            if 'estimated_pickup_time' in serializer.validated_data:
                delivery.estimated_pickup_time = serializer.validated_data['estimated_pickup_time']
            if 'estimated_delivery_time' in serializer.validated_data:
                delivery.estimated_delivery_time = serializer.validated_data['estimated_delivery_time']
            
            delivery.save()
            
            # Update order status
            delivery.order.status = Order.OrderStatus.OUT_FOR_DELIVERY
            delivery.order.save()
            
            # Create status history
            DeliveryStatusHistory.objects.create(
                delivery=delivery,
                status=Delivery.DeliveryStatus.ASSIGNED,
                notes=f"Assigned to rider {rider.full_name}",
                changed_by=request.user
            )
            
            return Response(
                DeliveryDetailSerializer(delivery).data,
                status=status.HTTP_200_OK
            )
            
        except Delivery.DoesNotExist:
            return Response(
                {"error": "Delivery not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except RiderProfile.DoesNotExist:
            return Response(
                {"error": "Rider not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class UpdateDeliveryStatusView(APIView):
    """Update delivery status"""
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, pk):
        try:
            delivery = Delivery.objects.get(pk=pk)
            
            # Only assigned rider or admins can update status
            if hasattr(request.user, 'rider_profile'):
                if delivery.rider != request.user.rider_profile:
                    return Response(
                        {"error": "You can only update your own deliveries"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            elif not request.user.is_staff:
                return Response(
                    {"error": "You don't have permission to update deliveries"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = DeliveryStatusUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            new_status = serializer.validated_data['status']
            notes = serializer.validated_data.get('notes', '')
            latitude = serializer.validated_data.get('latitude')
            longitude = serializer.validated_data.get('longitude')
            
            # Update delivery status
            old_status = delivery.status
            delivery.status = new_status
            
            # Update timestamps
            if new_status == Delivery.DeliveryStatus.PICKED_UP:
                delivery.actual_pickup_time = timezone.now()
            elif new_status == Delivery.DeliveryStatus.DELIVERED:
                delivery.actual_delivery_time = timezone.now()
                
                # Update order status
                delivery.order.status = Order.OrderStatus.DELIVERED
                delivery.order.delivered_at = timezone.now()
                delivery.order.save()
                
                # Update rider stats
                delivery.rider.total_deliveries += 1
                delivery.rider.save()
                
                # Handle delivery proof uploads
                if 'delivery_photo' in request.FILES:
                    delivery.delivery_photo = request.FILES['delivery_photo']
                if 'delivery_signature' in request.FILES:
                    delivery.delivery_signature = request.FILES['delivery_signature']
            
            delivery.save()
            
            # Create status history
            DeliveryStatusHistory.objects.create(
                delivery=delivery,
                status=new_status,
                notes=notes or f"Status changed from {old_status} to {new_status}",
                latitude=latitude,
                longitude=longitude,
                changed_by=request.user
            )
            
            # Create tracking update if location provided
            if latitude and longitude:
                DeliveryTracking.objects.create(
                    delivery=delivery,
                    latitude=latitude,
                    longitude=longitude,
                    status=new_status,
                    notes=notes
                )
            
            return Response(
                DeliveryDetailSerializer(delivery).data,
                status=status.HTTP_200_OK
            )
            
        except Delivery.DoesNotExist:
            return Response(
                {"error": "Delivery not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class DeliveryTrackingView(APIView):
    """Get real-time tracking for a delivery"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            delivery = Delivery.objects.get(pk=pk)
            
            # Check permissions
            user = request.user
            if hasattr(user, 'rider_profile'):
                if delivery.rider != user.rider_profile:
                    return Response(
                        {"error": "You don't have permission to track this delivery"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            elif hasattr(user, 'wholesaler_profile'):
                if delivery.order.wholesaler != user.wholesaler_profile:
                    return Response(
                        {"error": "You don't have permission to track this delivery"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            elif hasattr(user, 'shopkeeper_profile'):
                if delivery.order.shopkeeper != user.shopkeeper_profile:
                    return Response(
                        {"error": "You don't have permission to track this delivery"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            elif not user.is_staff:
                return Response(
                    {"error": "You don't have permission to track deliveries"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            tracking_updates = delivery.tracking_updates.all()
            serializer = DeliveryTrackingSerializer(tracking_updates, many=True)
            
            return Response({
                'delivery_id': delivery.id,
                'order_number': delivery.order.order_number,
                'status': delivery.status,
                'tracking_updates': serializer.data
            })
            
        except Delivery.DoesNotExist:
            return Response(
                {"error": "Delivery not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class RateRiderView(APIView):
    """Rate a rider after delivery"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            delivery = Delivery.objects.get(pk=pk)
            
            # Only shopkeeper who received the order can rate
            if not hasattr(request.user, 'shopkeeper_profile'):
                return Response(
                    {"error": "Only shopkeepers can rate riders"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if delivery.order.shopkeeper != request.user.shopkeeper_profile:
                return Response(
                    {"error": "You can only rate deliveries for your orders"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if delivery is completed
            if delivery.status != Delivery.DeliveryStatus.DELIVERED:
                return Response(
                    {"error": "You can only rate completed deliveries"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = RiderRatingSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            delivery.rider_rating = serializer.validated_data['rating']
            delivery.rider_feedback = serializer.validated_data.get('feedback', '')
            delivery.save()
            
            # Update rider's average rating
            rider = delivery.rider
            completed_deliveries = Delivery.objects.filter(
                rider=rider,
                status=Delivery.DeliveryStatus.DELIVERED,
                rider_rating__isnull=False
            )
            avg_rating = completed_deliveries.aggregate(Avg('rider_rating'))['rider_rating__avg']
            if avg_rating:
                rider.rating = round(avg_rating, 2)
                rider.save()
            
            return Response(
                {"message": "Rating submitted successfully"},
                status=status.HTTP_200_OK
            )
            
        except Delivery.DoesNotExist:
            return Response(
                {"error": "Delivery not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class AvailableRidersView(generics.ListAPIView):
    """List available riders"""
    serializer_class = RiderProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only wholesalers and admins can see available riders
        if not (hasattr(self.request.user, 'wholesaler_profile') or self.request.user.is_staff):
            return RiderProfile.objects.none()
        
        return RiderProfile.objects.filter(is_available=True).select_related('user')

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q
from .models import Order, OrderStatusHistory
from .serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer
)


class OrderListCreateView(generics.ListCreateAPIView):
    """List orders or create new order"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'payment_status', 'wholesaler']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderListSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Shopkeepers see their orders
        if hasattr(user, 'shopkeeper_profile'):
            return Order.objects.filter(
                shopkeeper=user.shopkeeper_profile
            ).select_related('wholesaler', 'shopkeeper')
        
        # Wholesalers see orders for their business
        elif hasattr(user, 'wholesaler_profile'):
            return Order.objects.filter(
                wholesaler=user.wholesaler_profile
            ).select_related('wholesaler', 'shopkeeper')
        
        # Admins see all orders
        elif user.is_staff:
            return Order.objects.all().select_related('wholesaler', 'shopkeeper')
        
        return Order.objects.none()


class OrderDetailView(generics.RetrieveAPIView):
    """Retrieve order details"""
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if hasattr(user, 'shopkeeper_profile'):
            return Order.objects.filter(shopkeeper=user.shopkeeper_profile)
        elif hasattr(user, 'wholesaler_profile'):
            return Order.objects.filter(wholesaler=user.wholesaler_profile)
        elif user.is_staff:
            return Order.objects.all()
        
        return Order.objects.none()


class OrderStatusUpdateView(APIView):
    """Update order status"""
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            
            # Check permissions
            if hasattr(request.user, 'wholesaler_profile'):
                if order.wholesaler != request.user.wholesaler_profile:
                    return Response(
                        {"error": "You don't have permission to update this order"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            elif hasattr(request.user, 'shopkeeper_profile'):
                # Shopkeepers can only cancel their own pending orders
                if order.shopkeeper != request.user.shopkeeper_profile:
                    return Response(
                        {"error": "You don't have permission to update this order"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                if request.data.get('status') != Order.OrderStatus.CANCELLED:
                    return Response(
                        {"error": "Shopkeepers can only cancel orders"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            elif not request.user.is_staff:
                return Response(
                    {"error": "You don't have permission to update orders"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = OrderStatusUpdateSerializer(
                data=request.data,
                context={'order': order}
            )
            serializer.is_valid(raise_exception=True)
            
            new_status = serializer.validated_data['status']
            notes = serializer.validated_data.get('notes', '')
            
            # Update order status
            old_status = order.status
            order.status = new_status
            
            # Update timestamps
            if new_status == Order.OrderStatus.CONFIRMED:
                order.confirmed_at = timezone.now()
            elif new_status == Order.OrderStatus.DELIVERED:
                order.delivered_at = timezone.now()
                order.payment_status = Order.PaymentStatus.PAID  # Auto-mark as paid on delivery
            
            order.save()
            
            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                notes=notes or f"Status changed from {old_status} to {new_status}",
                changed_by=request.user
            )
            
            # Update product stock if order is confirmed
            if new_status == Order.OrderStatus.CONFIRMED:
                for item in order.items.all():
                    product = item.product
                    product.stock_quantity -= item.quantity
                    product.save()
            
            return Response(
                OrderDetailSerializer(order).data,
                status=status.HTTP_200_OK
            )
            
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class ShopkeeperOrdersView(generics.ListAPIView):
    """List all orders for authenticated shopkeeper"""
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'payment_status']
    
    def get_queryset(self):
        if not hasattr(self.request.user, 'shopkeeper_profile'):
            return Order.objects.none()
        return Order.objects.filter(
            shopkeeper=self.request.user.shopkeeper_profile
        ).select_related('wholesaler')


class WholesalerOrdersView(generics.ListAPIView):
    """List all orders for authenticated wholesaler"""
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'payment_status']
    
    def get_queryset(self):
        if not hasattr(self.request.user, 'wholesaler_profile'):
            return Order.objects.none()
        return Order.objects.filter(
            wholesaler=self.request.user.wholesaler_profile
        ).select_related('shopkeeper')


class OrderCancelView(APIView):
    """Cancel an order"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            
            # Check permissions - only shopkeeper or wholesaler can cancel
            if hasattr(request.user, 'shopkeeper_profile'):
                if order.shopkeeper != request.user.shopkeeper_profile:
                    return Response(
                        {"error": "You don't have permission to cancel this order"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            elif hasattr(request.user, 'wholesaler_profile'):
                if order.wholesaler != request.user.wholesaler_profile:
                    return Response(
                        {"error": "You don't have permission to cancel this order"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                return Response(
                    {"error": "You don't have permission to cancel orders"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if order can be cancelled
            if order.status not in [Order.OrderStatus.PENDING, Order.OrderStatus.CONFIRMED]:
                return Response(
                    {"error": f"Cannot cancel order with status {order.status}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Restore stock if order was confirmed
            if order.status == Order.OrderStatus.CONFIRMED:
                for item in order.items.all():
                    product = item.product
                    product.stock_quantity += item.quantity
                    product.save()
            
            # Update order status
            order.status = Order.OrderStatus.CANCELLED
            order.save()
            
            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status=Order.OrderStatus.CANCELLED,
                notes=request.data.get('reason', 'Order cancelled'),
                changed_by=request.user
            )
            
            return Response(
                {"message": "Order cancelled successfully"},
                status=status.HTTP_200_OK
            )
            
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )

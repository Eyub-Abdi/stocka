from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem, OrderStatusHistory
from products.models import Product
from products.serializers import ProductListSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_details = ProductListSerializer(source='product', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_details',
            'quantity', 'unit_price', 'total_price'
        ]
        read_only_fields = ['id', 'total_price']


class OrderItemCreateSerializer(serializers.Serializer):
    """Serializer for creating order items"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for order status history"""
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)
    
    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'notes', 'changed_by_name', 'created_at']


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for order listing"""
    shopkeeper_name = serializers.CharField(source='shopkeeper.shop_name', read_only=True)
    wholesaler_name = serializers.CharField(source='wholesaler.business_name', read_only=True)
    items_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'shopkeeper_name', 'wholesaler_name',
            'status', 'status_display', 'payment_method', 'payment_status',
            'subtotal', 'delivery_fee', 'total_amount', 'items_count',
            'created_at', 'updated_at'
        ]
    
    def get_items_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for orders"""
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    shopkeeper_name = serializers.CharField(source='shopkeeper.shop_name', read_only=True)
    shopkeeper_phone = serializers.CharField(source='shopkeeper.user.phone_number', read_only=True)
    wholesaler_name = serializers.CharField(source='wholesaler.business_name', read_only=True)
    wholesaler_phone = serializers.CharField(source='wholesaler.user.phone_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'shopkeeper_name', 'shopkeeper_phone',
            'wholesaler_name', 'wholesaler_phone', 'status', 'status_display',
            'delivery_address', 'delivery_location', 'delivery_notes',
            'delivery_latitude', 'delivery_longitude', 'payment_method',
            'payment_status', 'subtotal', 'delivery_fee', 'total_amount',
            'items', 'status_history', 'created_at', 'updated_at',
            'confirmed_at', 'delivered_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'subtotal', 'total_amount',
            'created_at', 'updated_at', 'confirmed_at', 'delivered_at'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders"""
    items = OrderItemCreateSerializer(many=True, write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'wholesaler', 'delivery_address', 'delivery_location',
            'delivery_notes', 'delivery_latitude', 'delivery_longitude',
            'payment_method', 'items'
        ]
    
    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Order must contain at least one item")
        return items
    
    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Get shopkeeper from request user
        request = self.context.get('request')
        if not hasattr(request.user, 'shopkeeper_profile'):
            raise serializers.ValidationError("Only shopkeepers can create orders")
        
        # Create order
        order = Order.objects.create(
            shopkeeper=request.user.shopkeeper_profile,
            **validated_data
        )
        
        # Create order items
        total = 0
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            
            # Validate product belongs to the wholesaler
            if product.wholesaler != order.wholesaler:
                raise serializers.ValidationError(
                    f"Product {product.name} does not belong to the selected wholesaler"
                )
            
            # Check stock availability
            if product.stock_quantity < item_data['quantity']:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}. Available: {product.stock_quantity}"
                )
            
            # Check minimum order quantity
            if item_data['quantity'] < product.minimum_order_quantity:
                raise serializers.ValidationError(
                    f"Minimum order quantity for {product.name} is {product.minimum_order_quantity}"
                )
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                unit_price=product.wholesale_price
            )
            
            total += item_data['quantity'] * product.wholesale_price
        
        # Update order totals
        order.subtotal = total
        order.total_amount = total + order.delivery_fee
        order.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status=order.status,
            notes="Order created",
            changed_by=request.user
        )
        
        return order


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating order status"""
    status = serializers.ChoiceField(choices=Order.OrderStatus.choices)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_status(self, value):
        order = self.context.get('order')
        current_status = order.status
        
        # Define allowed status transitions
        allowed_transitions = {
            Order.OrderStatus.PENDING: [Order.OrderStatus.CONFIRMED, Order.OrderStatus.CANCELLED],
            Order.OrderStatus.CONFIRMED: [Order.OrderStatus.PROCESSING, Order.OrderStatus.CANCELLED],
            Order.OrderStatus.PROCESSING: [Order.OrderStatus.READY, Order.OrderStatus.CANCELLED],
            Order.OrderStatus.READY: [Order.OrderStatus.OUT_FOR_DELIVERY],
            Order.OrderStatus.OUT_FOR_DELIVERY: [Order.OrderStatus.DELIVERED],
        }
        
        if value not in allowed_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot change status from {current_status} to {value}"
            )
        
        return value

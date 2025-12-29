"""
Admin dashboard views and analytics endpoints
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, ShopkeeperProfile, WholesalerProfile, RiderProfile
from products.models import Product, Category
from orders.models import Order
from delivery.models import Delivery


class DashboardStatsView(APIView):
    """Get overall dashboard statistics"""
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        # Get time period from query params (default: last 30 days)
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # User statistics
        total_users = User.objects.count()
        total_shopkeepers = ShopkeeperProfile.objects.count()
        total_wholesalers = WholesalerProfile.objects.count()
        total_riders = RiderProfile.objects.count()
        new_users_period = User.objects.filter(created_at__gte=start_date).count()
        
        # Product statistics
        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_available=True).count()
        out_of_stock = Product.objects.filter(stock_quantity=0).count()
        
        # Order statistics
        total_orders = Order.objects.count()
        orders_period = Order.objects.filter(created_at__gte=start_date)
        pending_orders = Order.objects.filter(status=Order.OrderStatus.PENDING).count()
        processing_orders = Order.objects.filter(
            status__in=[Order.OrderStatus.CONFIRMED, Order.OrderStatus.PROCESSING, Order.OrderStatus.READY]
        ).count()
        completed_orders = Order.objects.filter(status=Order.OrderStatus.DELIVERED).count()
        cancelled_orders = Order.objects.filter(status=Order.OrderStatus.CANCELLED).count()
        
        # Revenue statistics
        total_revenue = Order.objects.filter(
            status=Order.OrderStatus.DELIVERED
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        period_revenue = orders_period.filter(
            status=Order.OrderStatus.DELIVERED
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Delivery statistics
        total_deliveries = Delivery.objects.count()
        active_deliveries = Delivery.objects.filter(
            status__in=[
                Delivery.DeliveryStatus.ASSIGNED,
                Delivery.DeliveryStatus.PICKED_UP,
                Delivery.DeliveryStatus.IN_TRANSIT
            ]
        ).count()
        completed_deliveries = Delivery.objects.filter(
            status=Delivery.DeliveryStatus.DELIVERED
        ).count()
        
        return Response({
            'users': {
                'total': total_users,
                'shopkeepers': total_shopkeepers,
                'wholesalers': total_wholesalers,
                'riders': total_riders,
                'new_in_period': new_users_period
            },
            'products': {
                'total': total_products,
                'active': active_products,
                'out_of_stock': out_of_stock
            },
            'orders': {
                'total': total_orders,
                'in_period': orders_period.count(),
                'pending': pending_orders,
                'processing': processing_orders,
                'completed': completed_orders,
                'cancelled': cancelled_orders
            },
            'revenue': {
                'total': float(total_revenue),
                'period': float(period_revenue)
            },
            'deliveries': {
                'total': total_deliveries,
                'active': active_deliveries,
                'completed': completed_deliveries
            }
        })


class OrderAnalyticsView(APIView):
    """Get order analytics and trends"""
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Orders by status
        orders_by_status = Order.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Orders by day (for trend chart)
        orders_by_day = Order.objects.filter(
            created_at__gte=start_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id'),
            revenue=Sum('total_amount')
        ).order_by('date')
        
        # Top wholesalers by order count
        top_wholesalers = Order.objects.values(
            'wholesaler__business_name'
        ).annotate(
            order_count=Count('id'),
            total_revenue=Sum('total_amount')
        ).order_by('-order_count')[:10]
        
        # Top shopkeepers by order count
        top_shopkeepers = Order.objects.values(
            'shopkeeper__shop_name'
        ).annotate(
            order_count=Count('id'),
            total_spent=Sum('total_amount')
        ).order_by('-order_count')[:10]
        
        # Average order value
        avg_order_value = Order.objects.filter(
            status=Order.OrderStatus.DELIVERED
        ).aggregate(avg=Avg('total_amount'))['avg'] or 0
        
        return Response({
            'orders_by_status': list(orders_by_status),
            'orders_by_day': list(orders_by_day),
            'top_wholesalers': list(top_wholesalers),
            'top_shopkeepers': list(top_shopkeepers),
            'average_order_value': float(avg_order_value)
        })


class ProductAnalyticsView(APIView):
    """Get product analytics"""
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        # Products by category
        products_by_category = Category.objects.annotate(
            product_count=Count('products', filter=Q(products__is_available=True))
        ).values('name', 'product_count').order_by('-product_count')
        
        # Top selling products
        from orders.models import OrderItem
        top_products = OrderItem.objects.values(
            'product__name',
            'product__category__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('total_price'),
            order_count=Count('order', distinct=True)
        ).order_by('-total_quantity')[:20]
        
        # Products needing restock
        low_stock_products = Product.objects.filter(
            stock_quantity__lte=10,
            is_available=True
        ).values(
            'name',
            'wholesaler__business_name',
            'stock_quantity',
            'minimum_order_quantity'
        ).order_by('stock_quantity')[:20]
        
        # Average product price by category
        avg_price_by_category = Product.objects.values(
            'category__name'
        ).annotate(
            avg_price=Avg('price'),
            avg_wholesale_price=Avg('wholesale_price')
        ).order_by('category__name')
        
        return Response({
            'products_by_category': list(products_by_category),
            'top_products': list(top_products),
            'low_stock_products': list(low_stock_products),
            'avg_price_by_category': list(avg_price_by_category)
        })


class DeliveryAnalyticsView(APIView):
    """Get delivery analytics"""
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Deliveries by status
        deliveries_by_status = Delivery.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Deliveries by day
        deliveries_by_day = Delivery.objects.filter(
            created_at__gte=start_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Top riders by delivery count
        top_riders = Delivery.objects.filter(
            rider__isnull=False
        ).values(
            'rider__full_name',
            'rider__rating'
        ).annotate(
            delivery_count=Count('id'),
            completed_count=Count('id', filter=Q(status=Delivery.DeliveryStatus.DELIVERED)),
            avg_rating=Avg('rider_rating')
        ).order_by('-delivery_count')[:10]
        
        # Average delivery time (for completed deliveries)
        from django.db.models import F, ExpressionWrapper, DurationField
        completed_deliveries = Delivery.objects.filter(
            status=Delivery.DeliveryStatus.DELIVERED,
            actual_pickup_time__isnull=False,
            actual_delivery_time__isnull=False
        ).annotate(
            delivery_duration=ExpressionWrapper(
                F('actual_delivery_time') - F('actual_pickup_time'),
                output_field=DurationField()
            )
        )
        
        avg_delivery_time_seconds = None
        if completed_deliveries.exists():
            total_seconds = sum(
                [d.delivery_duration.total_seconds() for d in completed_deliveries]
            )
            avg_delivery_time_seconds = total_seconds / completed_deliveries.count()
        
        return Response({
            'deliveries_by_status': list(deliveries_by_status),
            'deliveries_by_day': list(deliveries_by_day),
            'top_riders': list(top_riders),
            'avg_delivery_time_minutes': round(avg_delivery_time_seconds / 60, 2) if avg_delivery_time_seconds else None
        })


class UserGrowthAnalyticsView(APIView):
    """Get user growth analytics"""
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        days = int(request.query_params.get('days', 90))
        start_date = timezone.now() - timedelta(days=days)
        
        # User registrations by day
        registrations_by_day = User.objects.filter(
            created_at__gte=start_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date', 'user_type').annotate(
            count=Count('id')
        ).order_by('date', 'user_type')
        
        # User distribution by type
        users_by_type = User.objects.values('user_type').annotate(
            count=Count('id')
        ).order_by('user_type')
        
        # Verified vs unverified users
        verification_stats = {
            'verified': User.objects.filter(is_verified=True).count(),
            'unverified': User.objects.filter(is_verified=False).count()
        }
        
        # Active users (users who have placed/received orders in the last 30 days)
        recent_date = timezone.now() - timedelta(days=30)
        active_shopkeepers = Order.objects.filter(
            created_at__gte=recent_date
        ).values('shopkeeper').distinct().count()
        
        active_wholesalers = Order.objects.filter(
            created_at__gte=recent_date
        ).values('wholesaler').distinct().count()
        
        return Response({
            'registrations_by_day': list(registrations_by_day),
            'users_by_type': list(users_by_type),
            'verification_stats': verification_stats,
            'active_users': {
                'shopkeepers': active_shopkeepers,
                'wholesalers': active_wholesalers
            }
        })


class RevenueAnalyticsView(APIView):
    """Get revenue analytics"""
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        days = int(request.query_params.get('days', 90))
        start_date = timezone.now() - timedelta(days=days)
        
        # Revenue by day
        revenue_by_day = Order.objects.filter(
            created_at__gte=start_date,
            status=Order.OrderStatus.DELIVERED
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            revenue=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('date')
        
        # Revenue by month
        revenue_by_month = Order.objects.filter(
            created_at__gte=start_date,
            status=Order.OrderStatus.DELIVERED
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            revenue=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('month')
        
        # Revenue by payment method
        revenue_by_payment = Order.objects.filter(
            status=Order.OrderStatus.DELIVERED
        ).values('payment_method').annotate(
            revenue=Sum('total_amount'),
            count=Count('id')
        ).order_by('-revenue')
        
        # Revenue by wholesaler
        revenue_by_wholesaler = Order.objects.filter(
            status=Order.OrderStatus.DELIVERED
        ).values(
            'wholesaler__business_name'
        ).annotate(
            revenue=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('-revenue')[:10]
        
        return Response({
            'revenue_by_day': list(revenue_by_day),
            'revenue_by_month': list(revenue_by_month),
            'revenue_by_payment': list(revenue_by_payment),
            'revenue_by_wholesaler': list(revenue_by_wholesaler)
        })

"""
URL configuration for Stocka project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .admin_views import (
    DashboardStatsView,
    OrderAnalyticsView,
    ProductAnalyticsView,
    DeliveryAnalyticsView,
    UserGrowthAnalyticsView,
    RevenueAnalyticsView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/delivery/', include('delivery.urls')),
    
    path('api/admin/dashboard/', DashboardStatsView.as_view(), name='admin-dashboard'),
    path('api/admin/analytics/orders/', OrderAnalyticsView.as_view(), name='admin-order-analytics'),
    path('api/admin/analytics/products/', ProductAnalyticsView.as_view(), name='admin-product-analytics'),
    path('api/admin/analytics/deliveries/', DeliveryAnalyticsView.as_view(), name='admin-delivery-analytics'),
    path('api/admin/analytics/users/', UserGrowthAnalyticsView.as_view(), name='admin-user-analytics'),
    path('api/admin/analytics/revenue/', RevenueAnalyticsView.as_view(), name='admin-revenue-analytics'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

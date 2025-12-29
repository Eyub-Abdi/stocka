from django.urls import path
from .views import (
    OrderListCreateView,
    OrderDetailView,
    OrderStatusUpdateView,
    ShopkeeperOrdersView,
    WholesalerOrdersView,
    OrderCancelView,
)

urlpatterns = [
    # Orders
    path('', OrderListCreateView.as_view(), name='order-list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('<int:pk>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
    
    # User-specific orders
    path('shopkeeper/orders/', ShopkeeperOrdersView.as_view(), name='shopkeeper-orders'),
    path('wholesaler/orders/', WholesalerOrdersView.as_view(), name='wholesaler-orders'),
]

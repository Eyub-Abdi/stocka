from django.urls import path
from .views import (
    DeliveryListCreateView,
    DeliveryDetailView,
    AssignRiderView,
    UpdateDeliveryStatusView,
    DeliveryTrackingView,
    RateRiderView,
    AvailableRidersView,
)

urlpatterns = [
    # Deliveries
    path('', DeliveryListCreateView.as_view(), name='delivery-list'),
    path('<int:pk>/', DeliveryDetailView.as_view(), name='delivery-detail'),
    path('<int:pk>/assign-rider/', AssignRiderView.as_view(), name='assign-rider'),
    path('<int:pk>/status/', UpdateDeliveryStatusView.as_view(), name='delivery-status-update'),
    path('<int:pk>/tracking/', DeliveryTrackingView.as_view(), name='delivery-tracking'),
    path('<int:pk>/rate-rider/', RateRiderView.as_view(), name='rate-rider'),
    
    # Riders
    path('available-riders/', AvailableRidersView.as_view(), name='available-riders'),
]

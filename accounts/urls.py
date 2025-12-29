from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    UserProfileView,
    ShopkeeperProfileView,
    WholesalerProfileView,
    RiderProfileView
)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profiles
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/shopkeeper/', ShopkeeperProfileView.as_view(), name='shopkeeper-profile'),
    path('profile/wholesaler/', WholesalerProfileView.as_view(), name='wholesaler-profile'),
    path('profile/rider/', RiderProfileView.as_view(), name='rider-profile'),
]

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import ShopkeeperProfile, WholesalerProfile, RiderProfile
from stocka.utils.responses import api_response
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    ShopkeeperProfileSerializer,
    WholesalerProfileSerializer,
    RiderProfileSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        data = {
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return api_response(
            data=data,
            message="User registered successfully",
            status_code=status.HTTP_201_CREATED,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ShopkeeperProfileView(generics.RetrieveUpdateAPIView):
    """Get and update shopkeeper profile"""

    serializer_class = ShopkeeperProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = ShopkeeperProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile


class WholesalerProfileView(generics.RetrieveUpdateAPIView):
    """Get and update wholesaler profile"""

    serializer_class = WholesalerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = WholesalerProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile


class RiderProfileView(generics.RetrieveUpdateAPIView):
    """Get and update rider profile"""

    serializer_class = RiderProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = RiderProfile.objects.get_or_create(user=self.request.user)
        return profile

from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg
from .models import Category, Product, ProductImage, ProductReview
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductImageSerializer,
    ProductReviewSerializer
)
from .permissions import IsWholesalerOrReadOnly, IsShopkeeper


class CategoryListView(generics.ListCreateAPIView):
    """List all categories or create new one (admin only)"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return super().get_permissions()


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a category (admin only for modifications)"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()


class ProductListCreateView(generics.ListCreateAPIView):
    """List all products or create new product (wholesaler only)"""
    queryset = Product.objects.filter(is_available=True).select_related('wholesaler', 'category')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'wholesaler', 'is_featured']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['price', 'created_at', 'stock_quantity']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductDetailSerializer
        return ProductListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by wholesaler location proximity (simplified)
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(
                Q(wholesaler__business_location__icontains=location)
            )
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filter by stock availability
        in_stock = self.request.query_params.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)
        
        return queryset
    
    def perform_create(self, serializer):
        # Ensure user is a wholesaler
        if not hasattr(self.request.user, 'wholesaler_profile'):
            raise permissions.PermissionDenied("Only wholesalers can create products")
        serializer.save(wholesaler=self.request.user.wholesaler_profile)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a product"""
    queryset = Product.objects.all().select_related('wholesaler', 'category')
    serializer_class = ProductDetailSerializer
    permission_classes = [IsWholesalerOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Only show available products to non-owners
        if not self.request.user.is_staff:
            if hasattr(self.request.user, 'wholesaler_profile'):
                return queryset.filter(
                    Q(wholesaler=self.request.user.wholesaler_profile) | Q(is_available=True)
                )
            return queryset.filter(is_available=True)
        return queryset


class WholesalerProductListView(generics.ListAPIView):
    """List all products for the authenticated wholesaler"""
    serializer_class = ProductListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not hasattr(self.request.user, 'wholesaler_profile'):
            return Product.objects.none()
        return Product.objects.filter(
            wholesaler=self.request.user.wholesaler_profile
        ).select_related('category')


class ProductImageUploadView(APIView):
    """Upload images for a product"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            
            # Check if user owns the product
            if not hasattr(request.user, 'wholesaler_profile') or \
               product.wholesaler != request.user.wholesaler_profile:
                return Response(
                    {"error": "You don't have permission to add images to this product"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            image = request.FILES.get('image')
            is_primary = request.data.get('is_primary', False)
            
            if not image:
                return Response(
                    {"error": "No image provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # If setting as primary, unset other primary images
            if is_primary:
                ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)
            
            product_image = ProductImage.objects.create(
                product=product,
                image=image,
                is_primary=is_primary
            )
            
            serializer = ProductImageSerializer(product_image, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class ProductReviewListCreateView(generics.ListCreateAPIView):
    """List reviews for a product or create a new review"""
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return ProductReview.objects.filter(product_id=product_id)
    
    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_id')
        
        # Ensure user is a shopkeeper
        if not hasattr(self.request.user, 'shopkeeper_profile'):
            raise permissions.PermissionDenied("Only shopkeepers can review products")
        
        serializer.save(
            product_id=product_id,
            shopkeeper=self.request.user.shopkeeper_profile
        )


class ProductReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a review"""
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only modify their own reviews
        if hasattr(self.request.user, 'shopkeeper_profile'):
            return ProductReview.objects.filter(shopkeeper=self.request.user.shopkeeper_profile)
        return ProductReview.objects.none()

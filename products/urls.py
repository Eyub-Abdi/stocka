from django.urls import path
from .views import (
    CategoryListView,
    CategoryDetailView,
    ProductListCreateView,
    ProductDetailView,
    WholesalerProductListView,
    ProductImageUploadView,
    ProductReviewListCreateView,
    ProductReviewDetailView,
)

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    
    # Products
    path('', ProductListCreateView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('my-products/', WholesalerProductListView.as_view(), name='wholesaler-products'),
    
    # Product Images
    path('<int:product_id>/images/', ProductImageUploadView.as_view(), name='product-image-upload'),
    
    # Reviews
    path('<int:product_id>/reviews/', ProductReviewListCreateView.as_view(), name='product-reviews'),
    path('reviews/<int:pk>/', ProductReviewDetailView.as_view(), name='review-detail'),
]

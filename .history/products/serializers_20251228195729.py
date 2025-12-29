from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductReview
from accounts.serializers import WholesalerProfileSerializer


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories"""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'is_active', 'product_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_product_count(self, obj):
        return obj.products.filter(is_available=True).count()


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images"""
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product listing"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    wholesaler_name = serializers.CharField(source='wholesaler.business_name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'sku', 'price', 'wholesale_price',
            'minimum_order_quantity', 'stock_quantity', 'unit', 'expiry_date', 'is_available',
            'is_featured', 'category_name', 'wholesaler_name', 'primary_image',
            'average_rating', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
        return None
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return round(sum(r.rating for r in reviews) / len(reviews), 2)
        return 0


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for product"""
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    wholesaler = WholesalerProfileSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'wholesaler', 'category', 'category_id', 'name', 'description',
            'sku', 'price', 'wholesale_price', 'minimum_order_quantity',
            'stock_quantity', 'unit', 'expiry_date', 'is_available', 'is_featured',
            'images', 'reviews', 'average_rating', 'review_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_reviews(self, obj):
        reviews = obj.reviews.all()[:5]  # Latest 5 reviews
        return ProductReviewSerializer(reviews, many=True).data
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return round(sum(r.rating for r in reviews) / len(reviews), 2)
        return 0
    
    def get_review_count(self, obj):
        return obj.reviews.count()


class ProductReviewSerializer(serializers.ModelSerializer):
    """Serializer for product reviews"""
    shopkeeper_name = serializers.CharField(source='shopkeeper.shop_name', read_only=True)
    
    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'shopkeeper_name', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'shopkeeper_name', 'created_at', 'updated_at']

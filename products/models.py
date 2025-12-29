from django.db import models
from accounts.models import WholesalerProfile


class Category(models.Model):
    """Product categories"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """Products listed by wholesalers"""

    wholesaler = models.ForeignKey(
        WholesalerProfile, on_delete=models.CASCADE, related_name="products"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    sku = models.CharField(max_length=100, unique=True)

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    wholesale_price = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Price for bulk orders"
    )
    minimum_order_quantity = models.IntegerField(default=1)

    # Inventory
    stock_quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=50, default="pieces")  # pieces, kg, liters, etc.

    # Expiry
    expiry_date = models.DateField(null=True, blank=True)

    # Status
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["wholesaler", "is_available"]),
            models.Index(fields=["category", "is_available"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.wholesaler.business_name}"

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0


class ProductImage(models.Model):
    """Product images"""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/")
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_primary", "created_at"]

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductReview(models.Model):
    """Product reviews from shopkeepers"""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    shopkeeper = models.ForeignKey(
        "accounts.ShopkeeperProfile",
        on_delete=models.CASCADE,
        related_name="product_reviews",
    )
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["product", "shopkeeper"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.shopkeeper.shop_name} - {self.product.name} ({self.rating}★)"

"""
Management command to create sample data for testing
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import ShopkeeperProfile, WholesalerProfile, RiderProfile
from products.models import Category, Product, ProductImage
from orders.models import Order, OrderItem
from delivery.models import Delivery
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for testing the Stocka platform'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@stocka.com',
                password='admin123',
                phone_number='+254700000000',
                user_type=User.UserType.ADMIN
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        # Create wholesalers
        wholesalers = []
        for i in range(3):
            user = User.objects.create_user(
                username=f'wholesaler{i+1}',
                email=f'wholesaler{i+1}@stocka.com',
                password='password123',
                phone_number=f'+25470000{i+1}000',
                user_type=User.UserType.WHOLESALER,
                is_verified=True
            )
            profile = WholesalerProfile.objects.create(
                user=user,
                business_name=f'Wholesale Business {i+1}',
                business_address=f'{i+1}23 Industrial Area, Nairobi',
                business_location='Nairobi',
                business_registration=f'WB{i+1}23456',
                is_verified=True,
                rating=Decimal(random.uniform(4.0, 5.0))
            )
            wholesalers.append(profile)
        self.stdout.write(self.style.SUCCESS(f'Created {len(wholesalers)} wholesalers'))
        
        # Create shopkeepers
        shopkeepers = []
        for i in range(5):
            user = User.objects.create_user(
                username=f'shopkeeper{i+1}',
                email=f'shopkeeper{i+1}@stocka.com',
                password='password123',
                phone_number=f'+25471000{i+1}000',
                user_type=User.UserType.SHOPKEEPER,
                is_verified=True
            )
            profile = ShopkeeperProfile.objects.create(
                user=user,
                shop_name=f'Duka {i+1}',
                shop_address=f'Shop {i+1}, Main Street',
                shop_location='Nairobi',
            )
            shopkeepers.append(profile)
        self.stdout.write(self.style.SUCCESS(f'Created {len(shopkeepers)} shopkeepers'))
        
        # Create riders
        riders = []
        for i in range(4):
            user = User.objects.create_user(
                username=f'rider{i+1}',
                email=f'rider{i+1}@stocka.com',
                password='password123',
                phone_number=f'+25472000{i+1}000',
                user_type=User.UserType.RIDER,
                is_verified=True
            )
            profile = RiderProfile.objects.create(
                user=user,
                full_name=f'Rider {i+1}',
                id_number=f'ID{i+1}234567',
                vehicle_type='Motorcycle',
                vehicle_registration=f'KCA {i+1}23X',
                is_available=True,
                rating=Decimal(random.uniform(4.0, 5.0))
            )
            riders.append(profile)
        self.stdout.write(self.style.SUCCESS(f'Created {len(riders)} riders'))
        
        # Create categories
        categories_data = [
            'Beverages', 'Snacks', 'Groceries', 'Household', 'Personal Care'
        ]
        categories = []
        for cat_name in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_name,
                defaults={'description': f'{cat_name} products'}
            )
            categories.append(category)
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))
        
        # Create products
        product_names = [
            'Coca Cola 500ml', 'Fanta Orange 500ml', 'Sprite 500ml',
            'Potato Crisps', 'Chocolate Bar', 'Biscuits Pack',
            'Rice 2kg', 'Sugar 1kg', 'Cooking Oil 1L',
            'Detergent 500g', 'Soap Bar', 'Toilet Paper 4pk',
            'Toothpaste', 'Shampoo 200ml', 'Body Lotion'
        ]
        
        products = []
        for i, name in enumerate(product_names):
            wholesaler = random.choice(wholesalers)
            category = categories[i % len(categories)]
            
            product = Product.objects.create(
                wholesaler=wholesaler,
                category=category,
                name=name,
                description=f'Quality {name} at wholesale prices',
                sku=f'SKU{i+1:04d}',
                price=Decimal(random.uniform(50, 500)),
                wholesale_price=Decimal(random.uniform(40, 400)),
                minimum_order_quantity=random.choice([1, 5, 10, 20]),
                stock_quantity=random.randint(50, 500),
                is_available=True
            )
            products.append(product)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(products)} products'))
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Wholesalers: wholesaler1-3 / password123')
        self.stdout.write('Shopkeepers: shopkeeper1-5 / password123')
        self.stdout.write('Riders: rider1-4 / password123')

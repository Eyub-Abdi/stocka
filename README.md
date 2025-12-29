# Stocka - Restock Made Easy

A B2B marketplace platform connecting shopkeepers with wholesalers for seamless restocking.

## Features

- **Multi-user authentication** - Shopkeepers, Wholesalers, Riders, and Admins
- **Product catalog management** - Browse, search, and filter products
- **Order management** - Place orders, track status, manage fulfillment
- **Delivery coordination** - Assign riders, track deliveries in real-time
- **Real-time order status updates** - Keep all parties informed
- **User profiles and ratings** - Build trust through reviews and ratings
- **Admin dashboard** - Comprehensive analytics and reporting

## Tech Stack

- **Backend Framework**: Django 5.0
- **API**: Django REST Framework 3.14
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework-simplejwt)
- **File Uploads**: Pillow
- **CORS**: django-cors-headers

## Setup Instructions

### Prerequisites

- Python 3.10+
- PostgreSQL 12+
- pip and virtualenv

### 1. Clone the repository

```bash
git clone <repository-url>
cd stocka
```

### 2. Create and activate virtual environment

```bash
python -m venv venv

# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=stocka_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 5. Create PostgreSQL database

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE stocka_db;

# Exit PostgreSQL
\q
```

### 6. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create superuser

```bash
python manage.py createsuperuser
```

### 8. (Optional) Create sample data

```bash
python manage.py create_sample_data
```

This will create:
- 1 admin user (admin/admin123)
- 3 wholesalers (wholesaler1-3/password123)
- 5 shopkeepers (shopkeeper1-5/password123)
- 4 riders (rider1-4/password123)
- Sample categories and products

### 9. Run development server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

### 10. Access Django Admin

Visit `http://localhost:8000/admin/` and login with your superuser credentials.

## API Documentation

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed API endpoints and usage.

### Quick API Overview

#### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get JWT token
- `POST /api/auth/token/refresh/` - Refresh access token

#### Products
- `GET /api/products/` - List products with filters
- `POST /api/products/` - Create product (wholesaler only)
- `GET /api/products/{id}/` - Get product details
- `PUT /api/products/{id}/` - Update product (owner only)

#### Orders
- `GET /api/orders/` - List orders
- `POST /api/orders/` - Create new order (shopkeeper)
- `GET /api/orders/{id}/` - Get order details
- `PATCH /api/orders/{id}/status/` - Update order status
- `POST /api/orders/{id}/cancel/` - Cancel order

#### Deliveries
- `GET /api/delivery/` - List deliveries
- `POST /api/delivery/{id}/assign-rider/` - Assign rider
- `PATCH /api/delivery/{id}/status/` - Update delivery status
- `GET /api/delivery/{id}/tracking/` - Track delivery
- `POST /api/delivery/{id}/rate-rider/` - Rate rider

#### Admin Analytics
- `GET /api/admin/dashboard/` - Dashboard statistics
- `GET /api/admin/analytics/orders/` - Order analytics
- `GET /api/admin/analytics/products/` - Product analytics
- `GET /api/admin/analytics/deliveries/` - Delivery analytics
- `GET /api/admin/analytics/users/` - User growth analytics
- `GET /api/admin/analytics/revenue/` - Revenue analytics

## Project Structure

```
stocka/
├── accounts/              # User authentication and profiles
│   ├── models.py         # User, ShopkeeperProfile, WholesalerProfile, RiderProfile
│   ├── serializers.py    # User serializers
│   ├── views.py          # Auth and profile endpoints
│   └── urls.py           # Auth routes
├── products/             # Product catalog
│   ├── models.py        # Product, Category, ProductImage, ProductReview
│   ├── serializers.py   # Product serializers
│   ├── views.py         # Product CRUD endpoints
│   └── urls.py          # Product routes
├── orders/              # Order management
│   ├── models.py       # Order, OrderItem, OrderStatusHistory
│   ├── serializers.py  # Order serializers
│   ├── views.py        # Order endpoints
│   └── urls.py         # Order routes
├── delivery/           # Delivery coordination
│   ├── models.py      # Delivery, DeliveryTracking, DeliveryStatusHistory
│   ├── serializers.py # Delivery serializers
│   ├── views.py       # Delivery endpoints
│   └── urls.py        # Delivery routes
├── stocka/            # Project settings
│   ├── settings.py   # Django settings
│   ├── urls.py       # Main URL configuration
│   └── admin_views.py # Admin analytics endpoints
├── manage.py         # Django management script
└── requirements.txt  # Python dependencies
```

## User Roles

### Shopkeeper
- Browse products and wholesalers
- Place orders for restocking
- Track order and delivery status
- Review products and rate riders

### Wholesaler
- Manage product catalog
- Receive and process orders
- Assign deliveries to riders
- Track sales and inventory

### Rider
- View assigned deliveries
- Update delivery status
- Upload delivery proof
- Navigate to delivery locations

### Admin
- Monitor platform activity
- View analytics and reports
- Manage users and verifications
- Handle disputes and issues

## Development

### Running Tests

```bash
python manage.py test
```

### Making Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files

```bash
python manage.py collectstatic
```

## Deployment

For production deployment:

1. Set `DEBUG=False` in settings
2. Configure proper `ALLOWED_HOSTS`
3. Use a production database
4. Set up proper static file serving
5. Configure HTTPS
6. Use environment variables for secrets
7. Set up proper CORS origins

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub or contact support.

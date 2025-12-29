# Stocka API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### Authentication Endpoints

> All JSON responses are wrapped in a standard envelope:
>
> ```json
> {
>   "success": true,
>   "message": "...",
>   "data": { ... },
>   "errors": null,
>   "meta": { ... } // optional
> }
> ```

#### Register User
```http
POST /auth/register/
Content-Type: application/json

{
  "username": "shopkeeper1",
  "email": "shop@example.com",
  "phone_number": "+254712345678",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "user_type": "SHOPKEEPER"
}

Response: 201 Created
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": { ... },
    "access": "eyJ...",
    "refresh": "eyJ..."
  },
  "errors": null
}
```

#### Login
```http
POST /auth/login/
Content-Type: application/json

{
  "username": "shopkeeper1" // or email "shop@example.com",
  "password": "securepass123"
}

Response: 200 OK
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access": "eyJ...",
    "refresh": "eyJ..."
  },
  "errors": null
}
```

#### Refresh Token
```http
POST /auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ..."
}

Response: 200 OK
{
  "success": true,
  "message": "Token refreshed",
  "data": {
    "access": "eyJ..."
  },
  "errors": null
}
```

## User Profiles

#### Get User Profile
```http
GET /auth/profile/
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "message": "",
  "data": {
    "id": 1,
    "username": "shopkeeper1",
    "first_name": "Ayub",
    "last_name": "Abdi",
    "email": "shop@example.com",
    "phone_number": "+254712345678",
    "user_type": "SHOPKEEPER",
    "is_verified": true,
    "created_at": "2024-01-01 00:00:00"
  },
  "errors": null
}
```

#### Get Shopkeeper Profile
```http
GET /auth/profile/shopkeeper/
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "message": "",
  "data": {
    "id": 1,
    "user": {
      "id": 1,
      "username": "shopkeeper1",
      "first_name": "Ayub",
      "last_name": "Abdi",
      "email": "shop@example.com",
      "phone_number": "+254712345678",
      "user_type": "SHOPKEEPER",
      "is_verified": true,
      "created_at": "2024-01-01 00:00:00"
    },
    "shop_name": "Duka La Mama",
    "shop_address": "123 Main Street",
    "shop_location": "Nairobi",
    ...
  },
  "errors": null
}
```

## Products

#### List Products
```http
GET /products/?category=1&location=Nairobi&min_price=100&max_price=1000&in_stock=true
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "message": "",
  "data": {
    "count": 50,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Coca Cola 500ml",
        "description": "...",
        "sku": "SKU001",
        "price": "50.00",
        "wholesale_price": "40.00",
        "minimum_order_quantity": 10,
        "stock_quantity": 100,
        "unit": "pieces",
        "expiry_date": "2026-01-31",
        "is_available": true,
        "is_featured": false,
        "category_name": "Beverages",
        "wholesaler_name": "Wholesale Co.",
        "primary_image": "http://...",
        "average_rating": 4.5,
        "created_at": "2024-01-01 00:00:00"
      }
    ]
  },
  "errors": null
}
```

#### Get Product Details
```http
GET /products/1/
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "message": "",
  "data": {
    "id": 1,
    "wholesaler": { ... },
    "category": { ... },
    "name": "Coca Cola 500ml",
    "description": "...",
    "sku": "SKU001",
    "price": "50.00",
    "wholesale_price": "40.00",
    "minimum_order_quantity": 10,
    "stock_quantity": 100,
    "unit": "pieces",
    "expiry_date": "2026-01-31",
    "is_available": true,
    "is_featured": false,
    "images": [...],
    "reviews": [...],
    "average_rating": 4.5,
    "review_count": 10,
    "created_at": "2024-01-01 00:00:00",
    "updated_at": "2024-01-02 00:00:00"
  },
  "errors": null
}
```

#### Create Product (Wholesaler Only)
```http
POST /products/
Authorization: Bearer <token>
Content-Type: application/json

{
  "category_id": 1,
  "name": "New Product",
  "description": "Product description",
  "sku": "SKU001",
  "price": "100.00",
  "wholesale_price": "80.00",
  "minimum_order_quantity": 10,
  "stock_quantity": 500,
  "unit": "pieces"
}

Response: 201 Created
```

## Orders

#### Create Order
```http
POST /orders/
Authorization: Bearer <token>
Content-Type: application/json

{
  "wholesaler": 1,
  "delivery_address": "123 Main St",
  "delivery_location": "Nairobi",
  "payment_method": "COD",
  "items": [
    {
      "product_id": 1,
      "quantity": 20
    },
    {
      "product_id": 2,
      "quantity": 10
    }
  ]
}

Response: 201 Created
```

#### List Orders
```http
GET /orders/?status=PENDING
Authorization: Bearer <token>

Response: 200 OK
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "order_number": "ORD-ABC123",
      "status": "PENDING",
      "total_amount": "1500.00",
      ...
    }
  ]
}
```

#### Get Order Details
```http
GET /orders/1/
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "order_number": "ORD-ABC123",
  "items": [...],
  "status_history": [...],
  ...
}
```

#### Update Order Status (Wholesaler Only)
```http
PATCH /orders/1/status/
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "CONFIRMED",
  "notes": "Order confirmed, preparing items"
}

Response: 200 OK
```

#### Cancel Order
```http
POST /orders/1/cancel/
Authorization: Bearer <token>
Content-Type: application/json

{
  "reason": "Changed my mind"
}

Response: 200 OK
```

## Deliveries

#### List Deliveries
```http
GET /delivery/?status=IN_TRANSIT
Authorization: Bearer <token>

Response: 200 OK
```

#### Assign Rider to Delivery
```http
POST /delivery/1/assign-rider/
Authorization: Bearer <token>
Content-Type: application/json

{
  "rider_id": 1,
  "estimated_pickup_time": "2024-01-01T10:00:00Z",
  "estimated_delivery_time": "2024-01-01T12:00:00Z"
}

Response: 200 OK
```

#### Update Delivery Status (Rider Only)
```http
PATCH /delivery/1/status/
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "PICKED_UP",
  "notes": "Picked up from warehouse",
  "latitude": -1.2921,
  "longitude": 36.8219
}

Response: 200 OK
```

#### Track Delivery
```http
GET /delivery/1/tracking/
Authorization: Bearer <token>

Response: 200 OK
{
  "delivery_id": 1,
  "order_number": "ORD-ABC123",
  "status": "IN_TRANSIT",
  "tracking_updates": [...]
}
```

#### Rate Rider (Shopkeeper Only)
```http
POST /delivery/1/rate-rider/
Authorization: Bearer <token>
Content-Type: application/json

{
  "rating": 5,
  "feedback": "Excellent service!"
}

Response: 200 OK
```

## Admin Analytics

All admin endpoints require admin privileges.

#### Dashboard Stats
```http
GET /admin/dashboard/?days=30
Authorization: Bearer <admin_token>

Response: 200 OK
{
  "users": {...},
  "products": {...},
  "orders": {...},
  "revenue": {...},
  "deliveries": {...}
}
```

#### Order Analytics
```http
GET /admin/analytics/orders/?days=30
Authorization: Bearer <admin_token>

Response: 200 OK
{
  "orders_by_status": [...],
  "orders_by_day": [...],
  "top_wholesalers": [...],
  "top_shopkeepers": [...],
  "average_order_value": 1250.50
}
```

#### Product Analytics
```http
GET /admin/analytics/products/
Authorization: Bearer <admin_token>

Response: 200 OK
{
  "products_by_category": [...],
  "top_products": [...],
  "low_stock_products": [...],
  "avg_price_by_category": [...]
}
```

#### Delivery Analytics
```http
GET /admin/analytics/deliveries/?days=30
Authorization: Bearer <admin_token>

Response: 200 OK
{
  "deliveries_by_status": [...],
  "deliveries_by_day": [...],
  "top_riders": [...],
  "avg_delivery_time_minutes": 45.5
}
```

#### User Growth Analytics
```http
GET /admin/analytics/users/?days=90
Authorization: Bearer <admin_token>

Response: 200 OK
{
  "registrations_by_day": [...],
  "users_by_type": [...],
  "verification_stats": {...},
  "active_users": {...}
}
```

#### Revenue Analytics
```http
GET /admin/analytics/revenue/?days=90
Authorization: Bearer <admin_token>

Response: 200 OK
{
  "revenue_by_day": [...],
  "revenue_by_month": [...],
  "revenue_by_payment": [...],
  "revenue_by_wholesaler": [...]
}
```

## Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## User Types

- `SHOPKEEPER` - Shop owners who place orders
- `WHOLESALER` - Businesses that sell products
- `RIDER` - Delivery personnel
- `ADMIN` - Platform administrators

## Order Status Flow

```
PENDING → CONFIRMED → PROCESSING → READY → OUT_FOR_DELIVERY → DELIVERED
         ↓
      CANCELLED (can be cancelled at PENDING or CONFIRMED)
```

## Delivery Status Flow

```
PENDING → ASSIGNED → PICKED_UP → IN_TRANSIT → DELIVERED
         ↓
      CANCELLED or FAILED

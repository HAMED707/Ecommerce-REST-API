# E-commerce REST API

A Django REST API for e-commerce with JWT authentication, product management, shopping cart, orders, and payments.

This project follows the **Service Layer Pattern** with clear separation:

- **API Layer** ([api/](backend/api/)) - Handles HTTP requests/responses
- **Business Logic** ([services.py](backend/accounts/services.py)) - Core business rules
- **Data Layer** ([models.py](backend/accounts/models.py)) - Database models

## Project Structure

```
backend/
├── accounts/           # User management (models, services)
├── products/           # Product catalog (models, services)
├── cart/              # Shopping cart logic
├── orders/            # Order processing
├── payments/          # Payment handling
└── api/               # API Layer (separated)
    ├── accounts_api/  # Auth endpoints
    ├── products_api/  # Product endpoints
    ├── cart_api/      # Cart endpoints
    ├── orders_api/    # Order endpoints
    └── payments_api/  # Payment endpoints
```

## Testing with Postman

**Collection:** [API.postman_collection.json](API.postman_collection.json)

Import the collection into Postman and run the **"Complete E2E Test Scenario"** folder.

### Test Flow
**Register** → **Login** → **Browse Products** → **Add to Cart** → **View Cart** → **Create Shipping Address** → **Create Order** → **Process Payment** → **View Order History**


[https://github.com/HAMED707/Ecommerce-REST-API/blob/main/assets/api-test.mp4](https://private-user-images.githubusercontent.com/125318517/531507311-dd5fe132-d4ee-44c3-9d90-2fef2e8c9220.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjczNjk1ODcsIm5iZiI6MTc2NzM2OTI4NywicGF0aCI6Ii8xMjUzMTg1MTcvNTMxNTA3MzExLWRkNWZlMTMyLWQ0ZWUtNDRjMy05ZDkwLTJmZWYyZThjOTIyMC5tcDQ_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwMTAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDEwMlQxNTU0NDdaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0zZTMxNzE4MTVhOWRkNDY2Yjk3ZDY0NzUyYTE5ZjcyZTZmNWY5MWI5YWYyNTBmNGE4M2I0YTgwZDI3MmY1MTFjJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.szfE3__ghNN08JJRkm0iz-Saqq-JeS4cSeOPriWelcg)



## API Endpoints

| Category | Endpoint | Method | Auth |
|----------|----------|--------|------|
| **Auth** | `/api/auth/register/` | POST | ❌ |
| | `/api/auth/login/` | POST | ❌ |
| | `/api/auth/refresh/` | POST | ❌ |
| | `/api/auth/profile/` | GET/PUT | ✅ |
| **Products** | `/api/products/` | GET | ❌ |
| | `/api/products/{id}/` | GET | ❌ |
| | `/api/products/{id}/reviews/` | POST/GET | ✅/❌ |
| **Cart** | `/api/cart/` | GET | ✅ |
| | `/api/cart/add/` | POST | ✅ |
| | `/api/cart/items/{product_id}/` | PUT/DELETE | ✅ |
| **Orders** | `/api/orders/` | GET | ✅ |
| | `/api/orders/create/` | POST | ✅ |
| | `/api/orders/{id}/` | GET/PUT | ✅ |
| | `/api/orders/shipping-addresses/` | GET/POST | ✅ |
| **Payments** | `/api/payments/` | GET | ✅ |
| | `/api/payments/create/` | POST | ✅ |
| | `/api/payments/{id}/` | GET | ✅ |

---


## Installation

```bash
# Clone and navigate
git clone <repository-url>
cd RESTAPI_Project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
## Database Setup (PostgreSQL)

```bash
chmod +x setup_db.sh
./setup_db.sh
```


## Sample Data Setup

**Option 1: Load fixtures (offline data)**
```bash
python manage.py loaddata products/fixtures/sample_data.json
```

**Option 2: Fetch from fake API (online data)**
```bash
python manage.py populate_products
```


## Running

```bash
cd backend
python manage.py runserver
```
API: `http://localhost:8000/api`  
Admin: `http://localhost:8000/admin`




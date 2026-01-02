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

https://github.com/user-attachments/assets/5cd01cc9-e9c2-48e7-ad12-85db2c2fdda1

The collection includes automated tests and token management for seamless testing.

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




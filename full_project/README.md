# Production FastAPI Project

A complete, industry-structured REST API covering all real-world scenarios.

## Project Structure

```
full_project/
├── app/
│   ├── api/                  ← Route handlers (controllers)
│   │   ├── auth.py           → Register, Login, JWT, Change password
│   │   ├── users.py          → User CRUD (admin protected)
│   │   └── products.py       → Product CRUD with pagination & search
│   ├── models/               ← SQLAlchemy DB models
│   │   ├── user.py
│   │   └── product.py
│   ├── schemas/              ← Pydantic validation schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── product.py
│   ├── services/             ← Business logic layer
│   │   ├── user_service.py
│   │   └── product_service.py
│   ├── core/                 ← Config, DB, Security
│   │   ├── config.py         → Loads .env settings
│   │   ├── database.py       → SQLAlchemy engine + session
│   │   └── security.py       → JWT + password hashing
│   ├── middleware/
│   │   ├── logging.py        → Request logging middleware
│   │   └── errors.py         → Global error handlers
│   └── main.py               ← App entry point
├── tests/
│   └── test_api.py
├── .env
├── .gitignore
└── requirements.txt
```

## Setup & Run

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate          # Mac/Linux
venv\Scripts\activate             # Windows

# 2. Install all libraries
pip install -r requirements.txt

# 3. Run the server
uvicorn app.main:app --reload
```

Server: http://localhost:8000
Swagger Docs: http://localhost:8000/docs

## Test in Postman (step by step)

### Step 1 — Health check
GET http://localhost:8000/

### Step 2 — Register a user
POST http://localhost:8000/api/v1/auth/register
Body (JSON):
{
  "name": "Raj Patel",
  "email": "raj@example.com",
  "password": "password123"
}

### Step 3 — Login and get token
POST http://localhost:8000/api/v1/auth/login
Body (JSON):
{
  "email": "raj@example.com",
  "password": "password123"
}
→ Copy the access_token from the response

### Step 4 — Use the token
For all protected routes, add header:
Authorization: Bearer <paste token here>

### Step 5 — Get your profile
GET http://localhost:8000/api/v1/auth/me
(add Authorization header)

### Step 6 — Create a product
POST http://localhost:8000/api/v1/products/
(add Authorization header)
Body (JSON):
{
  "name": "iPhone 15",
  "description": "Latest Apple phone",
  "price": 79999,
  "stock": 50
}

### Step 7 — List products (public, no token needed)
GET http://localhost:8000/api/v1/products/
GET http://localhost:8000/api/v1/products/?search=iphone
GET http://localhost:8000/api/v1/products/?min_price=100&max_price=1000
GET http://localhost:8000/api/v1/products/?page=1&per_page=5

### Step 8 — Update a product
PATCH http://localhost:8000/api/v1/products/1
(add Authorization header)
Body (JSON):
{
  "price": 74999,
  "stock": 45
}

### Step 9 — Delete a product
DELETE http://localhost:8000/api/v1/products/1
(add Authorization header)

### Step 10 — Change password
PATCH http://localhost:8000/api/v1/auth/change-password
(add Authorization header)
Body (JSON):
{
  "current_password": "password123",
  "new_password": "newpass456"
}

## Run Tests

```bash
pytest tests/ -v
```

## API Endpoints Summary

| Method | URL                              | Auth     | Description               |
|--------|----------------------------------|----------|---------------------------|
| GET    | /                                | No       | Health check              |
| POST   | /api/v1/auth/register            | No       | Register new user         |
| POST   | /api/v1/auth/login               | No       | Login, get JWT token      |
| GET    | /api/v1/auth/me                  | User     | Get my profile            |
| PATCH  | /api/v1/auth/change-password     | User     | Change password           |
| GET    | /api/v1/users/                   | Admin    | List all users            |
| GET    | /api/v1/users/{id}               | Admin    | Get user by ID            |
| PATCH  | /api/v1/users/me                 | User     | Update my profile         |
| DELETE | /api/v1/users/{id}               | Admin    | Delete a user             |
| PATCH  | /api/v1/users/{id}/deactivate    | Admin    | Deactivate a user         |
| GET    | /api/v1/products/                | No       | List products (paginated) |
| GET    | /api/v1/products/{id}            | No       | Get product by ID         |
| POST   | /api/v1/products/                | User     | Create product            |
| PATCH  | /api/v1/products/{id}            | Owner    | Update product            |
| DELETE | /api/v1/products/{id}            | Owner    | Delete product            |

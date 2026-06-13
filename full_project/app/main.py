from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.database import create_tables
from app.api import auth, users, products, images
from app.middleware.logging import log_requests
from app.middleware.errors import (
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler,
)

# ─── Create FastAPI app ────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## Production-ready FastAPI project

### Features covered:
- **Auth** — Register, Login, JWT tokens, protected routes
- **Roles** — Admin vs User role-based access control
- **Users** — Full CRUD, deactivate, change password
- **Products** — Full CRUD, pagination, search, price filtering
- **Validation** — Pydantic schemas on all inputs
- **Error handling** — Global handlers, consistent JSON errors
- **Middleware** — CORS, request logging with timing
- **Database** — SQLAlchemy ORM with SQLite (swap to PostgreSQL easily)

### How to test:
1. Register → `POST /api/v1/auth/register`
2. Login → `POST /api/v1/auth/login` → copy the token
3. Click **Authorize** (top right) → paste token
4. Try protected routes
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── Create DB tables on startup ──────────────────────────────────────────────
@app.on_event("startup")
def startup():
    create_tables()

# ─── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # In production: replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request logging middleware ────────────────────────────────────────────────
app.middleware("http")(log_requests)

# ─── Global error handlers ────────────────────────────────────────────────────
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# ─── Routers ──────────────────────────────────────────────────────────────────
PREFIX = "/api/v1"
app.include_router(auth.router,     prefix=PREFIX)
app.include_router(users.router,    prefix=PREFIX)
app.include_router(products.router, prefix=PREFIX)
app.include_router(images.router,   prefix=PREFIX)


# ─── Health check ─────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def health_check():
    """
    GET / — Quick health check.
    First thing to test in Postman: confirms server is running.
    """
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "endpoints": {
            "auth":     "/api/v1/auth",
            "users":    "/api/v1/users",
            "products": "/api/v1/products",
        },
    }

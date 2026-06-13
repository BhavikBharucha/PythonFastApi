import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

# ─── Test DB setup (uses in-memory SQLite — never touches real DB) ─────────────
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def register_and_login(email="test@test.com", password="password123", name="Test User"):
    client.post("/api/v1/auth/register", json={"name": name, "email": email, "password": password})
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return r.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ─── Health check ─────────────────────────────────────────────────────────────
def test_health_check():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ─── Auth ─────────────────────────────────────────────────────────────────────
def test_register_success():
    r = client.post("/api/v1/auth/register", json={
        "name": "Raj", "email": "raj@test.com", "password": "pass123"
    })
    assert r.status_code == 201
    assert r.json()["email"] == "raj@test.com"
    assert "hashed_password" not in r.json()       # never exposed


def test_register_duplicate_email():
    client.post("/api/v1/auth/register", json={"name": "A", "email": "x@x.com", "password": "pass123"})
    r = client.post("/api/v1/auth/register", json={"name": "B", "email": "x@x.com", "password": "pass123"})
    assert r.status_code == 409


def test_login_success():
    client.post("/api/v1/auth/register", json={"name": "Raj", "email": "raj@test.com", "password": "pass123"})
    r = client.post("/api/v1/auth/login", json={"email": "raj@test.com", "password": "pass123"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password():
    client.post("/api/v1/auth/register", json={"name": "Raj", "email": "raj@test.com", "password": "pass123"})
    r = client.post("/api/v1/auth/login", json={"email": "raj@test.com", "password": "wrong"})
    assert r.status_code == 401


def test_get_me():
    token = register_and_login()
    r = client.get("/api/v1/auth/me", headers=auth_headers(token))
    assert r.status_code == 200
    assert r.json()["email"] == "test@test.com"


def test_get_me_no_token():
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401


# ─── Products ─────────────────────────────────────────────────────────────────
def test_list_products_public():
    r = client.get("/api/v1/products/")
    assert r.status_code == 200
    assert "items" in r.json()


def test_create_product():
    token = register_and_login()
    r = client.post("/api/v1/products/", headers=auth_headers(token), json={
        "name": "Laptop", "price": 999.99, "stock": 10
    })
    assert r.status_code == 201
    assert r.json()["name"] == "Laptop"


def test_create_product_no_auth():
    r = client.post("/api/v1/products/", json={"name": "X", "price": 10, "stock": 1})
    assert r.status_code == 401


def test_get_product_not_found():
    r = client.get("/api/v1/products/999")
    assert r.status_code == 404


def test_update_product_owner():
    token = register_and_login()
    h = auth_headers(token)
    product_id = client.post("/api/v1/products/", headers=h, json={
        "name": "Phone", "price": 500.0, "stock": 5
    }).json()["id"]
    r = client.patch(f"/api/v1/products/{product_id}", headers=h, json={"price": 450.0})
    assert r.status_code == 200
    assert r.json()["price"] == 450.0


def test_delete_product_owner():
    token = register_and_login()
    h = auth_headers(token)
    product_id = client.post("/api/v1/products/", headers=h, json={
        "name": "Tablet", "price": 300.0, "stock": 3
    }).json()["id"]
    r = client.delete(f"/api/v1/products/{product_id}", headers=h)
    assert r.status_code == 204


def test_validation_error():
    token = register_and_login()
    r = client.post("/api/v1/products/", headers=auth_headers(token), json={
        "name": "X",
        "price": -10,    # invalid — must be > 0
        "stock": 5
    })
    assert r.status_code == 422

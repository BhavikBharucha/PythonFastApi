from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    """POST /products — create a new product"""
    name:        str   = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price:       float = Field(..., gt=0)
    stock:       int   = Field(0, ge=0)


class ProductUpdate(BaseModel):
    """PATCH /products/{id} — partial update"""
    name:        Optional[str]   = Field(None, min_length=2, max_length=200)
    description: Optional[str]   = None
    price:       Optional[float] = Field(None, gt=0)
    stock:       Optional[int]   = Field(None, ge=0)
    is_active:   Optional[bool]  = None


class ProductResponse(BaseModel):
    id:          int
    name:        str
    description: Optional[str]
    price:       float
    stock:       int
    is_active:   bool
    owner_id:    int
    created_at:  datetime

    class Config:
        from_attributes = True


class PaginatedProducts(BaseModel):
    """Paginated list response"""
    total:    int
    page:     int
    per_page: int
    items:    list[ProductResponse]

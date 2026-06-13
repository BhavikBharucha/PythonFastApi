import os
from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, PaginatedProducts
)
from app.services import product_service, image_service
from app.core.helpers import save_upload_file

router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "/",
    response_model=PaginatedProducts,
    summary="Get all products with pagination, search & price filter",
)
def list_products(
    page: int       = Query(1, ge=1, description="Page number"),
    per_page: int   = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str]   = Query(None, description="Search by product name"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    db: Session = Depends(get_db),
):
    """
    Public endpoint — no login required.
    Supports: ?page=1&per_page=10&search=phone&min_price=100&max_price=500
    """
    skip = (page - 1) * per_page
    items, total = product_service.get_all_products(
        db, skip=skip, limit=per_page,
        search=search, min_price=min_price, max_price=max_price,
    )
    return PaginatedProducts(total=total, page=page, per_page=per_page, items=items)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get a single product by ID",
)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Public endpoint — no login required."""
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a product (login required)",
)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Creates a product owned by the currently logged-in user."""
    return product_service.create_product(db, data, owner_id=current_user.id)


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update a product (owner only)",
)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Only the product's owner can update it."""
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not your product")
    return product_service.update_product(db, product, data)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a product (owner or admin)",
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not your product")
    
    images = image_service.get_images_by_product_id(db, product_id)

    for image in images:

        filepath = os.path.join(
            "uploads",
            "products",
            image.filename
        )

        if os.path.exists(filepath):
            os.remove(filepath)
        
        image_service.delete_images_by_product_id(db, product_id)

    return product_service.delete_product(db, product, message="Product deleted successfully")


# @router.post("/{product_id}/images")
# def upload_product_images(
#     product_id: int,
#     files: list[UploadFile] = File(...),
#     db: Session = Depends(get_db)
# ):
#     product = product_service.get_product_by_id(
#         db,
#         product_id
#     )

#     if not product:
#         raise HTTPException(
#             status_code=404,
#             detail="Product not found"
#         )

#     uploaded_files = []

#     for file in files:

#         filename = save_upload_file(file)

#         image = image_service.create_image(
#             db=db,
#             product_id=product.id,
#             filename=filename
#         )

#         uploaded_files.append(
#             {
#                 "id": image.id,
#                 "filename": image.filename
#             }
#         )

#     return {
#         "status": "success",
#         "images": uploaded_files
#     }

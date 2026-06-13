from typing import Optional
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.image import Image
from app.schemas.product import ProductCreate, ProductUpdate


def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()


def get_all_products(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> tuple[list[Product], int]:
    query = db.query(Product).filter(Product.is_active == True)

    # Search filter
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    # Price range filter
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def create_product(db: Session, data: ProductCreate, owner_id: int) -> Product:
    product = Product(**data.model_dump(), owner_id=owner_id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, data: ProductUpdate) -> Product:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product, message: str) -> dict:
    db.delete(product)
    db.commit()
    return {"status": "success", "message": message}


# def create_image(db: Session, product_id: int, filename: str) -> Image:
#     image = Image(product_id=product_id, filename=filename)
#     db.add(image)
#     db.commit()
#     db.refresh(image)
#     return image


# def get_images_by_product(
#     db: Session,
#     product_id: int
# ):
#     return (
#         db.query(Image)
#         .filter(Image.product_id == product_id)
#         .all()
#     )


# def get_image_by_id(
#     db: Session,
#     image_id: int
# ):
#     return (
#         db.query(Image)
#         .filter(Image.id == image_id)
#         .first()
#     )


# def delete_image(
#     db: Session,
#     image: Image
# ):
#     db.delete(image)
#     db.commit()
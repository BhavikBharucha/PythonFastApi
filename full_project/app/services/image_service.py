from sqlalchemy.orm import Session

from app.models.image import Image

def create_image(db: Session, product_id: int, filename: str) -> Image:
    image = Image(product_id=product_id, filename=filename)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


def get_images_by_product_id(
    db: Session,
    product_id: int
):
    return (
        db.query(Image)
        .filter(Image.product_id == product_id)
        .all()
    )


def get_image_by_id(
    db: Session,
    image_id: int
):
    return (
        db.query(Image)
        .filter(Image.id == image_id)
        .first()
    )


def delete_image(
    db: Session,
    image: Image
):
    db.delete(image)
    db.commit()

def delete_images_by_product_id(
    db: Session,
    product_id: int
):
    images = get_images_by_product_id(db, product_id)
    for image in images:
        delete_image(db, image)
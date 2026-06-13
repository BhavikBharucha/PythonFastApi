from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

router = APIRouter()
from app.core.database import get_db
from app.services import product_service, image_service
from app.core.helpers import save_upload_file
from app.schemas.image import ProductImageRequest

router = APIRouter(prefix="/images", tags=["Images"])

@router.post("/upload")
def upload_product_images(
    product_id: int = Form(...),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    product = product_service.get_product_by_id(
        db,
        product_id
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    uploaded_files = []

    for file in files:

        filename = save_upload_file(file)

        image = image_service.create_image(
            db=db,
            product_id=product.id,
            filename=filename
        )

        uploaded_files.append(
            {
                "id": image.id,
                "filename": image.filename
            }
        )

    return {
        "status": "success",
        "images": uploaded_files
    }


@router.post("/retrieve")
def get_product_images(
    payload: ProductImageRequest,
    db: Session = Depends(get_db)
):
    product = product_service.get_product_by_id(
        db,
        payload.product_id
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    images = image_service.get_images_by_product_id(
        db,
        payload.product_id
    )

    return {
        "status": "success",
        "images": images
    }

@router.delete("/delete/{image_id}")
def delete_product_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    image = image_service.get_image_by_id(
        db,
        image_id
    )

    if not image:
        raise HTTPException(
            status_code=404,
            detail="Image not found"
        )

    image_service.delete_image(db, image)

    return {
        "status": "success",
        "message": "Image deleted successfully"
    }
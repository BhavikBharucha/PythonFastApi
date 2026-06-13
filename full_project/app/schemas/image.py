from pydantic import BaseModel

class ProductImageRequest(BaseModel):
    product_id: int
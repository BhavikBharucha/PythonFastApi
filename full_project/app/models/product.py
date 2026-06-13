from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(200), nullable=False, index=True)
    description = Column(String(1000), nullable=True)
    price       = Column(Float, nullable=False)
    stock       = Column(Integer, default=0)
    is_active   = Column(Boolean, default=True)
    owner_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    image       = Column(String(255), nullable=True)
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))
    images = relationship(
        "Image",
        back_populates="product",
        cascade="all, delete-orphan"
    )

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from src.database.database import BaseModel

class Product(BaseModel):
    __tablename__ = "products"

    company_id = Column(Integer, ForeignKey("company_profiles.id"), nullable=False)

    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    long_description = Column(Text, nullable=True)
    video_pitch_url = Column(String, nullable=True)

    price_range = Column(String, nullable=True)

    company = relationship("CompanyProfile", back_populates="products")
    images = relationship("ProductImage", back_populates="product")

class ProductImage(BaseModel):
    __tablename__ = "product_images"

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    url = Column(String, nullable=False)

    product = relationship("Product", back_populates="images")

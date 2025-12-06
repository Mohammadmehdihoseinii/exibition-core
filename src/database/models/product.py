from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from src.database.database import BaseModel


# -------------------- Many-to-Many Table --------------------

product_tag_association = Table(
    "product_tag_association",
    BaseModel.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("product_tags.id"), primary_key=True),
)


# -------------------- PRODUCT MODEL --------------------

class Product(BaseModel):
    __tablename__ = "products"

    company_id = Column(Integer, ForeignKey("company_profiles.id"), nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    long_description = Column(Text, nullable=True)

    video_pitch_url = Column(String, nullable=True)
    price_range = Column(String, nullable=True)

    company = relationship("CompanyProfile", back_populates="products")
    images = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    brochures = relationship(
        "ProductBrochure",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    tags = relationship(
        "ProductTag",
        secondary=product_tag_association,
        back_populates="products"
    )


class ProductImage(BaseModel):
    __tablename__ = "product_images"

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    url = Column(String, nullable=False)
    orginal_name = Column(String, nullable=False)
    is_primary = Column(Integer, default=0)

    product = relationship("Product", back_populates="images")

class ProductBrochure(BaseModel):
    __tablename__ = "product_brochures"

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    title = Column(String, nullable=True)
    orginal_name = Column(String, nullable=False)
    url = Column(String, nullable=False)

    product = relationship("Product", back_populates="brochures")

class ProductTag(BaseModel):
    __tablename__ = "product_tags"

    name = Column(String, unique=True, nullable=False)

    products = relationship(
        "Product",
        secondary=product_tag_association,  # همین جدول میانه
        back_populates="tags"
    )
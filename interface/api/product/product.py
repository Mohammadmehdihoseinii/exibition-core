from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from src.database.db_manager import db_manager

router = APIRouter(prefix="/products", tags=["Products"])

# -------------------- Schemas --------------------
class ProductCreateSchema(BaseModel):
    title: str
    summary: Optional[str]
    long_description: Optional[str]

class ProductUpdateSchema(BaseModel):
    title: Optional[str]
    summary: Optional[str]
    long_description: Optional[str]

class ProductImageSchema(BaseModel):
    url: str
    is_primary: Optional[bool] = False

class ProductResponse(BaseModel):
    id: int
    company_id: int
    title: str
    summary: Optional[str]
    long_description: Optional[str]
    images: List[str] = []


# -------------------- API Endpoints --------------------
@router.post("/", response_model=ProductResponse)
def create_product(company_id: int, req: ProductCreateSchema):
    product = db_manager.product.create(company_id=company_id, **req.dict())
    return ProductResponse(
        id=product.id,
        company_id=product.company_id,
        title=product.title,
        summary=product.summary,
        long_description=product.long_description,
        images=[]
    )

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, with_images: bool = False):
    product = db_manager.product.get_by_id(product_id, with_images=with_images)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    images = [img.url for img in getattr(product, "images", [])] if with_images else []
    return ProductResponse(
        id=product.id,
        company_id=product.company_id,
        title=product.title,
        summary=product.summary,
        long_description=product.long_description,
        images=images
    )

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, req: ProductUpdateSchema):
    product = db_manager.product.update(product_id, **req.dict(exclude_unset=True))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    images = [img.url for img in getattr(product, "images", [])]
    return ProductResponse(
        id=product.id,
        company_id=product.company_id,
        title=product.title,
        summary=product.summary,
        long_description=product.long_description,
        images=images
    )

@router.delete("/{product_id}", response_model=dict)
def delete_product(product_id: int):
    deleted = db_manager.product.delete(product_id)
    return {"deleted": deleted}

@router.post("/{product_id}/images", response_model=dict)
def add_product_image(product_id: int, req: ProductImageSchema):
    image = db_manager.product.add_image(product_id, req.url, req.is_primary)
    return {"id": image.id, "product_id": image.product_id, "url": image.url}

@router.get("/{product_id}/images", response_model=List[str])
def get_product_images(product_id: int):
    images = db_manager.product.get_images(product_id)
    return [img.url for img in images]

@router.delete("/images/{image_id}", response_model=dict)
def remove_product_image(image_id: int):
    deleted = db_manager.product.remove_image(image_id)
    return {"deleted": deleted}

@router.get("/", response_model=List[ProductResponse])
def search_products(
    query: Optional[str] = None,
    company_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0
):
    products = db_manager.product.search(query=query, company_id=company_id, limit=limit, offset=offset)
    result = []
    for p in products:
        images = [img.url for img in getattr(p, "images", [])]
        result.append(ProductResponse(
            id=p.id,
            company_id=p.company_id,
            title=p.title,
            summary=p.summary,
            long_description=p.long_description,
            images=images
        ))
    return result

@router.get("/company/{company_id}", response_model=List[ProductResponse])
def get_company_products(company_id: int):
    products = db_manager.product.get_by_company(company_id)
    if not products:
        raise HTTPException(status_code=404, detail="No products found for this company")
    
    result = []
    for p in products:
        images = [img.url for img in getattr(p, "images", [])]

        result.append(ProductResponse(
            id=p.id,
            company_id=p.company_id,
            title=p.title,
            summary=p.summary,
            long_description=p.long_description,
            images=images
        ))
    return result

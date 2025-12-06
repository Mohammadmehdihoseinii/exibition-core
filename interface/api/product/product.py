from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from typing import List, Optional
from src.database.db_manager import db_manager
from interface.api.product import Schema as Schema_product
import uuid, os
from sqlalchemy.orm import joinedload
router = APIRouter(prefix="/products", tags=["Products"])

upload_dir_product_images = "uploads/products/image"
upload_dir_product_brochure = "uploads/products/brochure"

os.makedirs(upload_dir_product_images, exist_ok=True) 
os.makedirs(upload_dir_product_brochure, exist_ok=True) 

@router.post("/", response_model=Schema_product.ProductResponse)
def create_product(company_id: int, req: Schema_product.ProductCreateSchema):
    product_data = {
        "title": req.title,
        "summary": req.summary,
        "long_description": req.long_description,
        "video_pitch_url": req.video_pitch_url,
        "price_range": req.price_range,
        "tags": req.tags
    }

    product = db_manager.product.create(company_id=company_id, **product_data)
    # product = db_manager.product.get_by_id(product.id)
    if product:
        tags = [tag['name'] for tag in db_manager.product.get_tags_for_product(product.id)]
    else:
        raise ValueError("Product not found")
    
    return {
        "id": product.id,
        "company_id": product.company_id,
        "title": product.title,
        "summary": product.summary,
        "long_description": product.long_description,
        "video_pitch_url": product.video_pitch_url,
        "price_range": product.price_range,
        "tags": tags,
    }

@router.get("/company/{company_id}")
def get_products_by_company(company_id: int):
    try:
        products = db_manager.product.search(company_id=company_id)

        if not products:
            return []

        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}", response_model=Schema_product.ProductResponse)
def get_product(product_id: int):
    product = db_manager.product.get_by_id(product_id)

    if not product:
        raise HTTPException(404, "Product not found")
    tags = [
        tag['name'] 
        for tag in db_manager.product.get_tags_for_product(product.id)]

    images = [
        Schema_product.ProductImageSchema(url=image.url, orginal_name=image.orginal_name, id=image.id)
        for image in db_manager.product.list_image(product.id)]

    brochures = [
        Schema_product.ProductBrochureSchema(url=brochure.url, orginal_name=brochure.orginal_name, title=brochure.title)
        for brochure in db_manager.product.list_brochure(product.id)]
    
    
    return Schema_product.ProductResponse(
        id=product.id,
        company_id=product.company_id,
        title=product.title,
        summary=product.summary,
        long_description=product.long_description,
        video_pitch_url=product.video_pitch_url,
        price_range=product.price_range,
        tags = tags,
        images=images, 
        brochures=brochures
    )

@router.put("/{product_id}", response_model=Schema_product.ProductResponse)
def update_product(product_id: int, req: Schema_product.ProductUpdateSchema):
    product = db_manager.product.update(product_id, **req.dict(exclude_unset=True))
    if not product:
        raise HTTPException(404, "Product not found")
    product = db_manager.product.get_by_id(product_id)
    return Schema_product.ProductResponse(
        id=product.id,
        company_id=product.company_id,
        title=product.title,
        summary=product.summary,
        long_description=product.long_description,
        video_pitch_url=product.video_pitch_url,
        price_range=product.price_range,
        tags = [tag['name'] for tag in db_manager.product.get_tags_for_product(product.id)],
    )

@router.delete("/{product_id}", response_model=dict)
def delete_product(product_id: int):
    deleted = db_manager.product.delete(product_id)
    return {"deleted": deleted}

@router.post("/{product_id}/images", response_model=dict)
async def add_product_image(product_id: int, file: UploadFile = File(...), is_primary: int = 0):
    """
    آپلود یک تصویر برای محصول.
    بعد از آپلود، مسیر فایل در دیتابیس ذخیره می‌شود.
    """
    try:
        ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"

        file_location = os.path.join(upload_dir_product_images, unique_filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())

        image = db_manager.product.add_image(
            product_id,
            url=file_location,
            orginal_name=file.filename,
            is_primary=is_primary
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"id": image.id, "url": image.url}

@router.delete("/images/{image_id}", response_model=dict)
def remove_product_image(image_id: int):
    return {"deleted": db_manager.product.remove_image(image_id)}

@router.post("/{product_id}/brochures", response_model=dict)
async def add_brochure(
        product_id: int,
        title: str = Form(...),
        file: UploadFile = File(...)
    ):
    try:
        if file is None:
            print("❌ No file received!")
            raise HTTPException(status_code=400, detail="No file received")

        if file.filename == "" or file.size == 0:
            print("❌ File received but is empty!")
            raise HTTPException(status_code=400, detail="Empty file received")

        print("test")
        ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"

        file_location = os.path.join(upload_dir_product_brochure, unique_filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())

        brochure = db_manager.product.add_brochure(
            product_id,
            title=title,
            orginal_name=file.filename,
            url=file_location
        )
        return {"id": brochure.id, "url": brochure.url}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/brochures/{brochure_id}", response_model=dict)
def remove_brochure(brochure_id: int):
    return {"deleted": db_manager.product.remove_brochure(brochure_id)}

@router.post("/{product_id}/tags/{tag_name}", response_model=dict)
def add_tag(product_id: int, tag_name: str):
    db_manager.product.add_tag(product_id, tag_name)
    return {"added": True}

@router.delete("/{product_id}/tags/{tag_name}", response_model=dict)
def remove_tag(product_id: int, tag_name: str):
    db_manager.product.remove_tag(product_id, tag_name)
    return {"removed": True}

@router.get("/", response_model=List[Schema_product.ProductResponse])
def search_products(
    query: Optional[str] = None,
    company_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0
):
    products = db_manager.product.search(query=query, company_id=company_id, limit=limit, offset=offset)

    return [
        Schema_product.ProductResponse(
            id=p.id,
            company_id=p.company_id,
            title=p.title,
            summary=p.summary,
            long_description=p.long_description,
            video_pitch_url=p.video_pitch_url,
            price_range=p.price_range,
            tags=[t.name for t in p.tags],
            images=[Schema_product.ProductImageSchema(
                url=img.url,
                orginal_name=img.orginal_name,
                id=img.id
            ) for img in p.images],
            brochures=[Schema_product.ProductBrochureSchema(
                title=b.title,
                orginal_name=b.orginal_name,
                url=b.url
            ) for b in p.brochures]
        )
        for p in products
    ]

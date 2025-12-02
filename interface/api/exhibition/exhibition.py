from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from src.database.db_manager import db_manager
from src.database.models import ExhibitionTag, ExhibitionMedia, VipLevelEnum, ExpoStatusEnum
router = APIRouter(prefix="/exhibition", tags=["exhibition"])

# -------------------- Schemas --------------------
class ExhibitionCreateSchema(BaseModel):
    name: str
    description: Optional[str]
    start_date: datetime
    end_date: datetime
    year: Optional[int]
    category_level: Optional[str]

class ExhibitionUpdateSchema(BaseModel):
    name: Optional[str]
    description: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    year: Optional[int]
    category_level: Optional[str]
    status: Optional[str]

class TagSchema(BaseModel):
    tag: str

class MediaSchema(BaseModel):
    media_url: str

class CompanyRegisterSchema(BaseModel):
    company_id: int
    booth_number: Optional[str]
    hall_name: Optional[str]
    vip_level: Optional[VipLevelEnum] = VipLevelEnum.normal


# -------------------- API Endpoints --------------------
@router.post("/", response_model=dict)
def create_exhibition(organizer_id: int, req: ExhibitionCreateSchema):
    exhibition = db_manager.exhibition.create(organizer_id=organizer_id, **req.dict())
    return {"id": exhibition.id, "name": exhibition.name}

@router.get("/{exhibition_id}", response_model=dict)
def get_exhibition(exhibition_id: int):
    exhibition = db_manager.exhibition.get_by_id(exhibition_id)
    if not exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    return {
        "id": exhibition.id,
        "name": exhibition.name,
        "description": exhibition.description,
        "start_date": exhibition.start_date,
        "end_date": exhibition.end_date,
        "year": exhibition.year,
        "category_level": exhibition.category_level,
        "status": exhibition.status
    }

@router.get("/", response_model=List[dict])
def list_exhibitions(
        query: Optional[str] = None,
        category: Optional[str] = None,
        year: Optional[int] = None,
        status: Optional[ExpoStatusEnum] = Query(None)
    ):
    exhibitions = db_manager.exhibition.search(
        query=query,
        category=category,
        year=year,
        status=status.value if status else None

    )
    return [
        {
            "id": e.id,
            "name": e.name,
            "description": e.description,
            "status": e.status.value,
            "year": e.year
        } for e in exhibitions
    ]

@router.put("/{exhibition_id}", response_model=dict)
def update_exhibition(exhibition_id: int, req: ExhibitionUpdateSchema):
    exhibition = db_manager.exhibition.update(exhibition_id, **req.dict(exclude_unset=True))
    if not exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    return {
        "id": exhibition.id,
        "name": exhibition.name,
        "status": exhibition.status.value
    }

@router.post("/{exhibition_id}/tags")
def add_tag(exhibition_id: int, req: TagSchema):
    tag_obj = db_manager.exhibition.add_tag(exhibition_id, req.tag)
    return {"id": tag_obj.id, "tag": tag_obj.tag}

@router.delete("/{exhibition_id}/tags/{tag_id}")
def remove_tag(exhibition_id: int, tag_id: int):
    session = db_manager.exhibition.get_session()
    tag = session.query(ExhibitionTag).filter(
        ExhibitionTag.id == tag_id,
        ExhibitionTag.exhibition_id == exhibition_id
    ).first()
    if not tag:
        session.close()
        raise HTTPException(status_code=404, detail="Tag not found")
    session.delete(tag)
    session.commit()
    session.close()
    return {"msg": "Tag removed successfully"}

@router.post("/{exhibition_id}/media")
def add_media(exhibition_id: int, req: MediaSchema):
    media_obj = db_manager.exhibition.add_media(exhibition_id, req.media_url)
    return {"id": media_obj.id, "media_url": media_obj.media_url}

@router.delete("/{exhibition_id}/media/{media_id}")
def remove_media(exhibition_id: int, media_id: int):
    session = db_manager.exhibition.get_session()
    media = session.query(ExhibitionMedia).filter(
        ExhibitionMedia.id == media_id,
        ExhibitionMedia.exhibition_id == exhibition_id
    ).first()
    if not media:
        session.close()
        raise HTTPException(status_code=404, detail="Media not found")
    session.delete(media)
    session.commit()
    session.close()
    return {"msg": "Media removed successfully"}

@router.post("/{exhibition_id}/companies")
def register_company(exhibition_id: int, req: CompanyRegisterSchema):
    company = db_manager.expo_company.register_company(
        exhibition_id=exhibition_id,
        company_id=req.company_id,
        booth_number=req.booth_number,
        hall_name=req.hall_name,
        vip_level=req.vip_level
    )
    return {
        "id": company.id,
        "company_id": company.company_id,
        "booth_number": company.booth_number,
        "hall_name": company.hall_name,
        "vip_level": company.vip_level
    }

@router.get("/{exhibition_id}/companies")
def list_companies(exhibition_id: int):
    companies = db_manager.expo_company.get_by_exhibition(exhibition_id)
    return [
        {
            "id": c.id,
            "company_id": c.company_id,
            "booth_number": c.booth_number,
            "hall_name": c.hall_name,
            "vip_level": c.vip_level
        } for c in companies
    ]

@router.put("/companies/{expo_company_id}")
def update_company_info(expo_company_id: int, req: CompanyRegisterSchema):
    company = db_manager.expo_company.update_booth_info(
        expo_company_id=expo_company_id,
        booth_number=req.booth_number,
        hall_name=req.hall_name,
        vip_level=req.vip_level
    )
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return {
        "id": company.id,
        "company_id": company.company_id,
        "booth_number": company.booth_number,
        "hall_name": company.hall_name,
        "vip_level": company.vip_level
    }

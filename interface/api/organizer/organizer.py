from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from src.database.db_manager import db_manager
from src.database.models import ExpoStatusEnum, VipLevelEnum

router = APIRouter(prefix="/organizer", tags=["Organizer"])

# -------------------- Schemas --------------------
class OrganizerCreateSchema(BaseModel):
    organization_name: str
    country: Optional[str]

class OrganizerResponse(BaseModel):
    id: int
    user_id: int
    organization_name: str
    verified: bool
    country: Optional[str]

class ExhibitionCreateSchema(BaseModel):
    name: str
    description: Optional[str]
    category_level: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    status: Optional[ExpoStatusEnum] = ExpoStatusEnum.draft
    year: Optional[int]

class ExhibitionResponse(BaseModel):
    id: int
    name: str
    description: str
    status: str
    year: int

class ExpoCompanyActionSchema(BaseModel):
    company_id: int
    booth_number: Optional[str]
    hall_name: Optional[str]
    vip_level: Optional[VipLevelEnum] = VipLevelEnum.normal
    approve: Optional[bool] = None  # برای تایید/رد

# -------------------- API Endpoints --------------------
@router.post("/", response_model=OrganizerResponse)
def create_organizer(user_id: int, req: OrganizerCreateSchema):
    organizer = db_manager.organizer.create(
        user_id=user_id,
        organization_name=req.organization_name,
        country=req.country,
    )
    return OrganizerResponse(
        id=organizer.id,
        user_id=organizer.user_id,
        organization_name=organizer.organization_name,
        verified=organizer.verified,
        country=organizer.country,
    )

@router.get("/{organizer_id}", response_model=OrganizerResponse)
def get_organizer(organizer_id: int):
    organizer = db_manager.organizer.get_by_id(organizer_id)
    if not organizer:
        raise HTTPException(status_code=404, detail="Organizer not found")
    return OrganizerResponse(
        id=organizer.id,
        user_id=organizer.user_id,
        organization_name=organizer.organization_name,
        verified=organizer.verified,
        country=organizer.country,
    )

@router.put("/{organizer_id}/verify", response_model=OrganizerResponse)
def verify_organizer(organizer_id: int):
    organizer = db_manager.organizer.verify_organizer(organizer_id)
    if not organizer:
        raise HTTPException(status_code=404, detail="Organizer not found")
    return OrganizerResponse(
        id=organizer.id,
        user_id=organizer.user_id,
        organization_name=organizer.organization_name,
        verified=organizer.verified,
        country=organizer.country,
    )

@router.post("/{organizer_id}/exhibition", response_model=ExhibitionResponse)
def create_exhibition(organizer_id: int, req: ExhibitionCreateSchema):
    exhibition = db_manager.exhibition.create(
        organizer_id=organizer_id,
        **req.dict(exclude_unset=True)
    )
    return ExhibitionResponse(
        id=exhibition.id,
        name=exhibition.name,
        description=exhibition.description,
        status=exhibition.status.value,
        year=exhibition.year
    )

@router.get("/{organizer_id}/exhibitions", response_model=List[ExhibitionResponse])
def list_exhibitions(organizer_id: int):
    exhibitions = db_manager.exhibition.get_by_organizer(organizer_id)
    return [
        ExhibitionResponse(
            id=e.id,
            name=e.name,
            description=e.description,
            status=e.status.value,
            year=e.year
        ) for e in exhibitions
    ]
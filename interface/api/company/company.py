from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from src.database.db_manager import db_manager
from src.database.models import ApprovalStatusEnum

router = APIRouter(prefix="/company", tags=["Company"])

# -------------------- Schemas --------------------
class CompanyCreateSchema(BaseModel):
    company_name: str
    logo: Optional[str]
    website: Optional[str]
    industry_category: Optional[str]
    description: Optional[str]
    approval_status: Optional[ApprovalStatusEnum] = ApprovalStatusEnum.pending

class CompanyUpdateSchema(BaseModel):
    company_name: Optional[str]
    logo: Optional[str]
    website: Optional[str]
    industry_category: Optional[str]
    description: Optional[str]
    approval_status: Optional[ApprovalStatusEnum]

class CompanyDocumentSchema(BaseModel):
    name: str
    url: str

class CompanyResponse(BaseModel):
    id: int
    company_name: str
    user_id: int
    approval_status: str

# -------------------- API Endpoints --------------------
@router.post("/", response_model=dict)
def create_company(user_id: int, req: CompanyCreateSchema):
    try:
        company = db_manager.company.create(
            user_id=user_id,
            company_name=req.company_name,
            logo=req.logo,
            website=req.website,
            industry_category=req.industry_category,
            description=req.description,
            approval_status=req.approval_status
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {
        "id": company.id,
        "user_id": company.user_id,
        "company_name": company.company_name,
        "logo": company.logo,
        "website": company.website,
        "industry_category": company.industry_category,
        "description": company.description,
        "approval_status": company.approval_status.value,
        "created_at": company.created_at
    }

@router.get("/pending", response_model=List[CompanyResponse])
def list_pending_companies():
    companies = db_manager.company.get_pending_companies()
    return [
        CompanyResponse(
            id=c.id,
            company_name=c.company_name,
            user_id=c.user_id,
            approval_status=c.approval_status.value
        )
        for c in companies
    ]

@router.get("/approved", response_model=List[dict])
def list_approved_companies():
    companies = db_manager.company.get_approved_companies()
    return [
        {
            "id": c.id,
            "company_name": c.company_name,
            "user_id": c.user_id,
            "approval_status": c.approval_status.value
        } for c in companies
    ]

@router.get("/{company_id}", response_model=dict)
def get_company(company_id: int):
    company = db_manager.company.get_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return {
        "id": company.id,
        "user_id": company.user_id,
        "company_name": company.company_name,
        "logo": company.logo,
        "website": company.website,
        "industry_category": company.industry_category,
        "description": company.description,
        "approval_status": company.approval_status.value,
        "created_at": company.created_at
    }

@router.get("/user/{user_id}", response_model=dict)
def get_company_by_user(user_id: int):
    company = db_manager.company.get_by_user_id(user_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return {
        "id": company.id,
        "user_id": company.user_id,
        "company_name": company.company_name,
        "logo": company.logo,
        "website": company.website,
        "industry_category": company.industry_category,
        "description": company.description,
        "approval_status": company.approval_status.value,
        "created_at": company.created_at
    }

@router.put("/{company_id}", response_model=dict)
def update_company(company_id: int, req: CompanyUpdateSchema):
    try:
        company = db_manager.company.update(company_id, **req.dict(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {
        "id": company.id,
        "company_name": company.company_name,
        "approval_status": company.approval_status.value
    }

@router.post("/{company_id}/document", response_model=dict)
def add_company_document(company_id: int, doc: CompanyDocumentSchema):
    document = db_manager.company.add_document(company_id, name=doc.name, url=doc.url)
    return {
        "id": document.id,
        "company_profile_id": document.company_profile_id,
        "name": document.name,
        "url": document.url
    }

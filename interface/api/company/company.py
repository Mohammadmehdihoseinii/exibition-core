from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from src.database.db_manager import db_manager
from src.database.models import ApprovalStatusEnum
import os
import uuid
router = APIRouter(prefix="/company", tags=["Company"])

upload_dir_logo = "./uploads/logos"
upload_dir_brochure = "uploads/brochure"
upload_dir_video = "uploads/video"

os.makedirs(upload_dir_logo, exist_ok=True) 
os.makedirs(upload_dir_brochure, exist_ok=True) 
os.makedirs(upload_dir_video, exist_ok=True)

# -------------------- Schemas --------------------
class CompanyCreateSchema(BaseModel):
    company_name: str
    logo: Optional[str] = None
    industry_category: Optional[str] = None
    description: Optional[str] = None
    approval_status: Optional[ApprovalStatusEnum] = ApprovalStatusEnum.pending


class CompanyUpdateSchema(BaseModel):
    company_name: Optional[str] = None
    logo: Optional[str] = None
    industry_category: Optional[str] = None
    description: Optional[str] = None
    approval_status: Optional[ApprovalStatusEnum] = None


class CompanyDocumentSchema(BaseModel):
    name: str
    url: str


class CompanyTagSchema(BaseModel):
    tag: str


class CompanyWebsiteSchema(BaseModel):
    name: str
    url: str


class CompanyAddressSchema(BaseModel):
    name: str
    address: str


class CompanyPhoneSchema(BaseModel):
    name: str
    phone_number: str


class CompanyVideoSchema(BaseModel):
    name: str
    video_url: str


class CompanyBrochureSchema(BaseModel):
    name: str
    file_url: str


class CompanyKnowledgeFileSchema(BaseModel):
    title: str
    file_url: str

class CompanyLogoSchema(BaseModel):
    logo: str

# -------------------------
# Helpers
# -------------------------
def _safe_val(obj, attr, default=None):
    return getattr(obj, attr) if hasattr(obj, attr) else default


def serialize_company(company) -> Dict[str, Any]:
    """
    Build a JSON-serializable dict for a company instance.
    Assumes relationship attributes:
      - websites, addresses, phones, tags, videos, brochures, knowledge_files, documents
    """
    if company is None:
        return {}

    def _serialize_list(rows, fields):
        out = []
        for r in rows or []:
            item = {}
            for f in fields:
                item[f] = _safe_val(r, f)
            # always include id if present
            if hasattr(r, "id"):
                item["id"] = r.id
            out.append(item)
        return out

    data = {
        "id": company.id if hasattr(company, "id") else None,
        "user_id": company.user_id if hasattr(company, "user_id") else None,
        "company_name": company.company_name if hasattr(company, "company_name") else None,
        "logo": company.logo if hasattr(company, "logo") else None,
        "industry_category": company.industry_category if hasattr(company, "industry_category") else None,
        "description": company.description if hasattr(company, "description") else None,
        "approval_status": getattr(company.approval_status, "value", company.approval_status) if hasattr(company, "approval_status") else None,
        "created_at": getattr(company, "created_at", None),
        "updated_at": getattr(company, "updated_at", None),
        # children
        "websites": _serialize_list(getattr(company, "websites", []), ["name", "url"]),
        "addresses": _serialize_list(getattr(company, "addresses", []), ["name", "address"]),
        "phones": _serialize_list(getattr(company, "phones", []), ["name", "phone_number"]),
        "tags": _serialize_list(getattr(company, "tags", []), ["tag"]),
        "videos": _serialize_list(getattr(company, "videos", []), ["name", "video_url"]),
        "brochures": _serialize_list(getattr(company, "brochures", []), ["name", "file_url"]),
        "knowledge_files": _serialize_list(getattr(company, "knowledge_files", []), ["title", "file_url"]),
        "documents": _serialize_list(getattr(company, "documents", []), ["name", "url"]),
    }
    return data


# -------------------- API Endpoints --------------------
@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_company(user_id: int, req: CompanyCreateSchema):
    try:
        company = db_manager.company.create(user_id=user_id, **req.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Company created", "company": serialize_company(company)}


@router.get("/{company_id}", response_model=dict)
def get_company(company_id: int):
    company = db_manager.company.get_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return serialize_company(company)


@router.get("/user/{user_id}", response_model=dict)
def get_company_by_user(user_id: int):
    company = db_manager.company.get_by_user_id(user_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return serialize_company(company)


@router.put("/{company_id}", response_model=dict)
def update_company(company_id: int, req: CompanyUpdateSchema):
    data = req.dict(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")

    try:
        db_manager.company.update(company_id, **data)  # فقط آپدیت
        # حالا دوباره company را load کن تا session به آن متصل باشد
        company = db_manager.company.get_by_id(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Company updated", "company": serialize_company(company)}

@router.delete("/{company_id}", response_model=dict)
def delete_company(company_id: int):
    try:
        # assuming db_manager.company has a delete method; if not, implement in manager
        deleted = db_manager.company.delete(company_id)
    except AttributeError:
        # fallback: get and delete via manager's session-level methods if available
        try:
            c = db_manager.company.get_by_id(company_id)
            if not c:
                raise HTTPException(status_code=404, detail="Company not found")
            # If ManagerBase provides delete_child style for main entity, use it; else raise
            db_manager.company._delete_main(company_id)  # optional internal method
            deleted = True
        except Exception:
            raise HTTPException(status_code=501, detail="Delete not implemented in CompanyManager")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Company deleted", "deleted": bool(deleted)}

@router.post("/{company_id}/document", response_model=dict, status_code=status.HTTP_201_CREATED)
def add_document(company_id: int, payload: CompanyDocumentSchema):
    try:
        doc = db_manager.company.add_document(company_id, name=payload.name, url=payload.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Document added", "document": {"id": doc.id, "company_profile_id": getattr(doc, "company_profile_id", None), "name": doc.name, "url": doc.url}}


@router.get("/{company_id}/documents", response_model=List[dict])
def list_documents(company_id: int):
    docs = db_manager.company.list_documents(company_id)
    return [{"id": d.id, "name": d.name, "url": d.url} for d in docs]

@router.delete("/document/{document_id}", response_model=dict)
def delete_document(document_id: int):
    try:
        db_manager.company.delete_document(document_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Document deleted"}

@router.post("/{company_id}/tag", response_model=dict, status_code=status.HTTP_201_CREATED)
def add_tag(company_id: int, payload: CompanyTagSchema):
    try:
        t = db_manager.company.add_tag(company_id, tag=payload.tag)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Tag added", "tag": {"id": t.id, "tag": t.tag}}

@router.get("/{company_id}/tags", response_model=List[dict])
def list_tags(company_id: int):
    tags = db_manager.company.list_tags(company_id)
    return [{"id": t.id, "tag": t.tag} for t in tags]

@router.delete("/tag/{tag_id}", response_model=dict)
def delete_tag(tag_id: int):
    try:
        db_manager.company.delete_tag(tag_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Tag deleted"}

@router.post("/{company_id}/website", response_model=dict, status_code=status.HTTP_201_CREATED)
def add_website(company_id: int, payload: CompanyWebsiteSchema):
    try:
        w = db_manager.company.add_website(company_id, name=payload.name, url=payload.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Website added", "website": {"id": w.id, "name": w.name, "url": w.url}}

@router.get("/{company_id}/websites", response_model=List[dict])
def list_websites(company_id: int):
    sites = db_manager.company.list_websites(company_id)
    return [{"id": s.id, "name": s.name, "url": s.url} for s in sites]

@router.delete("/website/{website_id}", response_model=dict)
def delete_website(website_id: int):
    try:
        db_manager.company.delete_website(website_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Website deleted"}

@router.post("/{company_id}/address", response_model=dict, status_code=status.HTTP_201_CREATED)
def add_address(company_id: int, payload: CompanyAddressSchema):
    try:
        a = db_manager.company.add_address(company_id, name=payload.name, address=payload.address)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Address added", "address": {"id": a.id, "name": a.name, "address": a.address}}

@router.get("/{company_id}/addresses", response_model=List[dict])
def list_addresses(company_id: int):
    addresses = db_manager.company.list_addresses(company_id)
    return [{"id": a.id, "name": a.name, "address": a.address} for a in addresses]


@router.delete("/address/{address_id}", response_model=dict)
def delete_address(address_id: int):
    try:
        db_manager.company.delete_address(address_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Address deleted"}

@router.put("/{company_id}/logo", response_model=dict)
async def update_logo(company_id: int, file: UploadFile = File(...)):
    """
    آپلود یا به‌روزرسانی لوگوی شرکت.
    بعد از آپلود، مسیر فایل در فیلد logo ذخیره می‌شود.
    """
    try:
        ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"

        file_location = os.path.join(upload_dir_logo, unique_filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())

        relative_url = f"/uploads/logos/{unique_filename}"
        company = db_manager.company.update(company_id, logo=relative_url)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Logo updated", "logo": company.logo}

@router.delete("/{company_id}/logo", response_model=dict)
def delete_logo(company_id: int):
    """
    حذف لوگوی شرکت (فیلد logo را null می‌کند)
    """
    try:
        company = db_manager.company.update(company_id, logo=None)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Logo deleted", "logo": company.logo}

@router.post("/{company_id}/phone", response_model=dict, status_code=status.HTTP_201_CREATED)
def add_phone(company_id: int, payload: CompanyPhoneSchema):
    try:
        p = db_manager.company.add_phone(company_id, name=payload.name, phone_number=payload.phone_number)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Phone added", "phone": {"id": p.id, "name": p.name, "phone_number": p.phone_number}}

@router.get("/{company_id}/phones", response_model=List[dict])
def list_phones(company_id: int):
    phones = db_manager.company.list_phones(company_id)
    return [{"id": p.id, "name": p.name, "phone_number": p.phone_number} for p in phones]

@router.delete("/phone/{phone_id}", response_model=dict)
def delete_phone(phone_id: int):
    try:
        db_manager.company.delete_phone(phone_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Phone deleted"}

@router.post("/{company_id}/video", response_model=dict)
async def add_video(company_id: int, file: UploadFile = File(...)):
    try:
        ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_location = os.path.join(upload_dir_video, unique_filename)

        content = await file.read()
        with open(file_location, "wb") as f:
            f.write(content)

        b = db_manager.company.add_video(
            company_id,
            title=file.filename,
            orginal_name=file.filename,
            video_url=file_location
        )
        return {"message": "Video uploaded", "video": {"id": b.id, "title": b.title, "file_url": b.video_url}}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{company_id}/videos", response_model=List[dict])
def list_videos(company_id: int):
    videos = db_manager.company.list_videos(company_id)
    return [{"id": v.id, "name": v.name, "video_url": v.video_url} for v in videos]

@router.delete("/video/{video_id}", response_model=dict)
def delete_video(video_id: int):
    try:
        db_manager.company.delete_video(video_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Video deleted"}

@router.post("/{company_id}/brochure", response_model=dict, status_code=201)
async def add_brochure(
        company_id: int,
        title: str = Form(...),
        file: UploadFile = File(...)
    ):
    try:
        ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_location = os.path.join(upload_dir_brochure, unique_filename)

        with open(file_location, "wb") as f:
            f.write(await file.read())


        b = db_manager.company.add_brochure(
            company_id=company_id,
            title=title,
            file_url=file_location,
            orginal_name=file.filename
        )        
        print(f"company_id = {company_id} / name = {title} / file saved as {unique_filename}")
        return {
            "message": "Brochure added",
            "brochure": {
                "id": b.id,
                "title": b.title,
                "original_name": b.orginal_name,
                "file_url": b.file_url
            }
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{company_id}/brochures", response_model=List[dict])
def list_brochures(company_id: int):
    bros = db_manager.company.list_brochures(company_id)
    return [{"id": b.id, "title": b.title, "file_url": b.file_url} for b in bros]

@router.delete("/brochure/{brochure_id}", response_model=dict)
def delete_brochure(brochure_id: int):
    try:
        db_manager.company.delete_brochure(brochure_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Brochure deleted"}

@router.post("/{company_id}/knowledge", response_model=dict, status_code=status.HTTP_201_CREATED)
def add_knowledge_file(company_id: int, payload: CompanyKnowledgeFileSchema):
    try:
        k = db_manager.company.add_knowledge_file(company_id, title=payload.title, file_url=payload.file_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Knowledge file added", "knowledge_file": {"id": k.id, "title": k.title, "file_url": k.file_url}}


@router.get("/{company_id}/knowledge", response_model=List[dict])
def list_knowledge_files(company_id: int):
    files = db_manager.company.list_knowledge_files(company_id)
    return [{"id": f.id, "title": f.title, "file_url": f.file_url} for f in files]

@router.delete("/knowledge/{knowledge_id}", response_model=dict)
def delete_knowledge_file(knowledge_id: int):
    try:
        db_manager.company.delete_knowledge_file(knowledge_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Knowledge file deleted"}

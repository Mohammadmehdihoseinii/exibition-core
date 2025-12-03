from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel, EmailStr
from typing import Optional
from src.database.models import RoleEnum
from src.database.db_manager import db_manager
from interface.api.users import auth
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/auth", tags=["auth"])


# ----------------- Schemas -----------------

class LoginSchema(BaseModel):
    username_or_email: str
    password: str


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str


# -------------------- API Endpoints --------------------
@router.post("/register")
async def register(
        email: str = Form(...),
        password: str = Form(...),
        role: RoleEnum = Form(...),
        username: str = Form(...),
        companyName: str | None = Form(None),
        industry: str | None = Form(None),
        contactPhone: str | None = Form(None),
        responsiblePerson: str | None = Form(None),
        verificationDoc: UploadFile | None = File(None)
    ):
    try:
        user = db_manager.user.create(
            username=username,
            email=email,
            password=password,
            role=role.value
        )
        token = auth.create_access_token(user_id=user.id)

        if role.value == RoleEnum.exhibitor:
            db_manager.company.create(
                user_id=user.id,
                company_name=companyName,
                industry_category=industry,
            )
            db_manager.user.update(user.id,mobilephone=contactPhone)

        if role.value == RoleEnum.organizer:
            verification_url = None
            if verificationDoc:
                verification_doc_record = db_manager.verification.save_file(
                    user_id=user.id,
                    uploaded_file=verificationDoc
                )
                verification_url = verification_doc_record.file_url

            db_manager.organizer.create(
                user_id=user.id,
                organization_name=username,
                responsible_person=responsiblePerson or "",
                verification_doc=verification_url
            )

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "user": {"id": user.id, "email": user.email, "role": user.role.name,"token":token},
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
def login(req: LoginSchema):
    user = db_manager.user.login(req.username_or_email, req.password)
    if not user:
        return {
            "success": False,
            "error": "Incorrect username or password"
        }

    token = auth.create_access_token(user_id=user.id)

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }


@router.get("/me")
def me(current_user = Depends(auth.get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": getattr(current_user, "role", None),
        "last_login": current_user.last_login
    }

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordSchema):
    user = db_manager.user.get_by_username_or_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = auth.create_password_reset_token(user.id)

    # مثال لینک: https://your-app/reset-password?token=...
    return {"msg": "Password reset token created", "reset_token": token}

@router.post("/reset-password")
def reset_password(req: ResetPasswordSchema):
    user = auth.verify_password_reset_token(req.token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    auth.update_user_password(user, req.new_password)
    return {"msg": "Password updated successfully"}

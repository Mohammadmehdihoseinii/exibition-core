from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional

from src.database.db_manager import db_manager
from interface.api.users import auth

router = APIRouter(prefix="/auth", tags=["auth"])


# ----------------- Schemas -----------------
class RegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginSchema(BaseModel):
    username_or_email: str
    password: str


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str


# ----------------- Register -----------------
@router.post("/register")
def register(req: RegisterSchema):
    try:
        user = db_manager.user.create(
            username=req.username,
            email=req.email,
            password=req.password,
        )
        return {"msg": "User created", "id": user.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------- Login -----------------
@router.post("/login")
def login(req: LoginSchema):
    user = db_manager.user.login(req.username_or_email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token(user_id=user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "email": user.email}
    }


# ----------------- Me -----------------
@router.get("/me")
def me(current_user = Depends(auth.get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": getattr(current_user, "role", None),
        "last_login": current_user.last_login
    }


# ----------------- Forgot Password -----------------
@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordSchema):
    user = db_manager.user.get_by_username_or_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = auth.create_password_reset_token(user.id)

    # مثال لینک: https://your-app/reset-password?token=...
    return {"msg": "Password reset token created", "reset_token": token}


# ----------------- Reset Password -----------------
@router.post("/reset-password")
def reset_password(req: ResetPasswordSchema):
    user = auth.verify_password_reset_token(req.token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    auth.update_user_password(user, req.new_password)
    return {"msg": "Password updated successfully"}

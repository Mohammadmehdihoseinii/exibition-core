import os
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt

from src.database.db_manager import db_manager

# ============================================
# Config
# ============================================
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_KEY")
RESET_SECRET_KEY = os.getenv("RESET_SECRET_KEY", "CHANGE_THIS_RESET_KEY")
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 12))
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", 30))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ============================================
# Access Token - Create
# ============================================
def create_access_token(user_id: int, expires_delta: timedelta | None = None) -> str:
    now = datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp())
    }

    try:
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        print("Generated JWT:", token)     # پرینت توکن برای تست
        return token
    except Exception as e:
        print("Error creating token:", e)
        raise HTTPException(status_code=500, detail="Failed to generate access token")

# ============================================
# Access Token - Decode
# ============================================
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



# ============================================
# Password Reset Token - Create
# ============================================
def create_password_reset_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    try:
        return jwt.encode(payload, RESET_SECRET_KEY, algorithm=ALGORITHM)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to generate reset token")


# ============================================
# Password Reset Token - Verify
# ============================================
def verify_password_reset_token(token: str):
    try:
        payload = jwt.decode(token, RESET_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if not user_id:
            return None

        return db_manager.user.get_by_id(int(user_id))

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None

    except Exception:
        return None


# ============================================
# Update User Password
# ============================================
def update_user_password(user, new_password: str):
    hashed = db_manager.user.hash_password(new_password)

    if hashed is None:
        raise HTTPException(status_code=500, detail="Password hashing failed")

    session = db_manager.get_session()

    try:
        user.password = hashed
        session.add(user)
        session.commit()
    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to update password")
    finally:
        session.close()


# ============================================
# FastAPI Dependency: Current User
# ============================================
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    raw_user_id = payload.get("sub")
    if not raw_user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    try:
        user_id = int(raw_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user id in token")
    user = db_manager.user.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

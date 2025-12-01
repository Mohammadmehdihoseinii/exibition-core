from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from src.database.database import BaseModel
from datetime import datetime, timedelta

class Token(BaseModel):
    __tablename__ = "tokens"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    token_type = Column(String, nullable=False)  # انواع:
        # - "access": برای دسترسی به API
        # - "refresh": برای تمدید توکن
        # - "reset": برای بازنشانی رمز عبور
        # - "verify": برای تأیید ایمیل/موبایل
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="tokens")

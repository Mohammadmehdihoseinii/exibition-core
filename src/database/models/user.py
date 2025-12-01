from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime

from src.database.database import BaseModel
from src.database.models.enums import RoleEnum

class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(100), nullable=True)
    email = Column(String, unique=True, nullable=True)
    mobilephone = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.visitor, nullable=False)
    is_active = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)

    tokens = relationship("Token", back_populates="user")
    sessions = relationship("TrackingSession", back_populates="user")

    user_profile = relationship("UserProfile", back_populates="user", uselist=False)
    company_profile = relationship("CompanyProfile", back_populates="user", uselist=False)
    organizer_profile = relationship("OrganizerProfile", back_populates="user", uselist=False)

    favorites = relationship("UserFavorite", back_populates="user")

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from src.database.database import BaseModel
from src.database.models.enums import ApprovalStatusEnum

class UserProfile(BaseModel):
    __tablename__ = "user_profiles"

    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    full_name = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)

    user = relationship("User", back_populates="user_profile")
    preferred_categories = relationship("UserPreferredCategory", back_populates="user_profile")
    social_links = relationship("UserSocialLink", back_populates="user_profile")


class UserPreferredCategory(BaseModel):
    __tablename__ = "user_preferred_categories"

    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    category_name = Column(String, nullable=False)

    user_profile = relationship("UserProfile", back_populates="preferred_categories")


class UserSocialLink(BaseModel):
    __tablename__ = "user_social_links"

    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    platform = Column(String, nullable=False)
    url = Column(String, nullable=False)

    user_profile = relationship("UserProfile", back_populates="social_links")

class OrganizerProfile(BaseModel):
    __tablename__ = "organizers"

    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    organization_name = Column(String, nullable=False)
    website = Column(String, nullable=True)
    country = Column(String, nullable=True)
    verified = Column(Boolean, default=False)
    
    responsible_person = Column(String, nullable=True)
    verification_doc = Column(String, nullable=True)

    user = relationship("User", back_populates="organizer_profile")
    exhibitions = relationship("Exhibition", back_populates="organizer")

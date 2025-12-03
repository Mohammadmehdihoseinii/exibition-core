from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship

from src.database.database import BaseModel
from src.database.models.enums import ExpoStatusEnum, VipLevelEnum
import enum

class VerificationStatusEnum(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class Exhibition(BaseModel):
    __tablename__ = "exhibitions"

    organizer_id = Column(Integer, ForeignKey("organizers.id"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    year = Column(Integer, default=2025)

    category_level = Column(String, nullable=True)
    status = Column(Enum(ExpoStatusEnum), default=ExpoStatusEnum.draft)
    banner_image = Column(String, nullable=True)

    organizer = relationship("OrganizerProfile", back_populates="exhibitions")
    companies = relationship("ExpoCompany", back_populates="exhibition")
    tags = relationship("ExhibitionTag", back_populates="exhibition")
    media_gallery = relationship("ExhibitionMedia", back_populates="exhibition")

class ExhibitionTag(BaseModel):
    __tablename__ = "exhibition_tags"

    exhibition_id = Column(Integer, ForeignKey("exhibitions.id"), nullable=False)
    tag = Column(String, nullable=False)

    exhibition = relationship("Exhibition", back_populates="tags")

class ExhibitionMedia(BaseModel):
    __tablename__ = "exhibition_media"

    exhibition_id = Column(Integer, ForeignKey("exhibitions.id"), nullable=False)
    media_url = Column(String, nullable=False)

    exhibition = relationship("Exhibition", back_populates="media_gallery")

class ExpoCompany(BaseModel):
    __tablename__ = "expo_companies"

    exhibition_id = Column(Integer, ForeignKey("exhibitions.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("company_profiles.id"), nullable=False)

    booth_number = Column(String, nullable=True)
    hall_name = Column(String, nullable=True)
    vip_level = Column(Enum(VipLevelEnum), default=VipLevelEnum.normal)

    exhibition = relationship("Exhibition", back_populates="companies")
    company = relationship("CompanyProfile", back_populates="exhibitions_participated")

class VerificationDocument(BaseModel):
    __tablename__ = "verification_documents"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    status = Column(Enum(VerificationStatusEnum), default=VerificationStatusEnum.pending)

    user = relationship("User", back_populates="verification_documents")

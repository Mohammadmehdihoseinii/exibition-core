from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime

from src.database.database import BaseModel
from src.database.models.enums import ApprovalStatusEnum

class CompanyProfile(BaseModel):
    __tablename__ = "company_profiles"

    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    company_name = Column(String, nullable=False)
    logo = Column(String, nullable=True)
    website = Column(String, nullable=True)
    industry_category = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    approval_status = Column(Enum(ApprovalStatusEnum), default=ApprovalStatusEnum.pending)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="company_profile")
    products = relationship("Product", back_populates="company")
    exhibitions_participated = relationship("ExpoCompany", back_populates="company")
    documents = relationship("CompanyDocument", back_populates="company_profile")

class CompanyDocument(BaseModel):
    __tablename__ = "company_documents"

    company_profile_id = Column(Integer, ForeignKey("company_profiles.id"), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)

    company_profile = relationship("CompanyProfile", back_populates="documents")

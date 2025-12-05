from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime

from src.database.database import BaseModel
from src.database.models.enums import ApprovalStatusEnum


class CompanyProfile(BaseModel):
    __tablename__ = "company_profiles"

    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    company_name = Column(String, nullable=False)
    logo = Column(String, nullable=True)
    industry_category = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    approval_status = Column(Enum(ApprovalStatusEnum), default=ApprovalStatusEnum.pending)

    user = relationship("User", back_populates="company_profile")
    websites = relationship("CompanyWebsite", back_populates="company", cascade="all, delete-orphan")
    addresses = relationship("CompanyAddress", back_populates="company", cascade="all, delete-orphan")
    phones = relationship("CompanyPhone", back_populates="company", cascade="all, delete-orphan")
    tags = relationship("CompanyTag", back_populates="company", cascade="all, delete-orphan")
    videos = relationship("CompanyVideo", back_populates="company", cascade="all, delete-orphan")
    brochures = relationship("CompanyBrochure", back_populates="company", cascade="all, delete-orphan")
    knowledge_files = relationship("CompanyKnowledgeFile", back_populates="company", cascade="all, delete-orphan")
    documents = relationship("CompanyDocument", back_populates="company_profile")
    products = relationship("Product", back_populates="company")
    exhibitions_participated = relationship("ExpoCompany", back_populates="company")

class CompanyWebsite(BaseModel):
    __tablename__ = "company_websites"

    company_id = Column(Integer, ForeignKey("company_profiles.id"), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)

    company = relationship("CompanyProfile", back_populates="websites")

class CompanyAddress(BaseModel):
    __tablename__ = "company_addresses"

    company_id = Column(Integer, ForeignKey("company_profiles.id"), nullable=False)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)

    company = relationship("CompanyProfile", back_populates="addresses")

class CompanyPhone(BaseModel):
    __tablename__ = "company_phones"

    company_id = Column(Integer, ForeignKey("company_profiles.id"), nullable=False)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)

    company = relationship("CompanyProfile", back_populates="phones")

class CompanyTag(BaseModel):
    __tablename__ = "company_tags"

    company_id = Column(Integer, ForeignKey("company_profiles.id"), nullable=False)
    tag = Column(String, nullable=False)

    company = relationship("CompanyProfile", back_populates="tags")

class CompanyVideo(BaseModel):
    __tablename__ = "company_videos"

    company_id = Column(Integer, ForeignKey("company_profiles.id"), nullable=False)
    title = Column(String, nullable=False)
    orginal_name = Column(String, nullable=False)
    video_url = Column(String, nullable=False)

    company = relationship("CompanyProfile", back_populates="videos")

class CompanyBrochure(BaseModel):
    __tablename__ = "company_brochures"

    company_id = Column(Integer, ForeignKey("company_profiles.id"), nullable=False)
    title = Column(String, nullable=False)
    orginal_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)

    company = relationship("CompanyProfile", back_populates="brochures")


class CompanyKnowledgeFile(BaseModel):
    __tablename__ = "company_knowledge_files"

    company_id = Column(Integer, ForeignKey("company_profiles.id"), nullable=False)
    title = Column(String, nullable=True)
    orginal_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)

    company = relationship("CompanyProfile", back_populates="knowledge_files")


class CompanyDocument(BaseModel):
    __tablename__ = "company_documents"

    company_profile_id = Column(Integer, ForeignKey("company_profiles.id"), nullable=False)
    title = Column(String, nullable=False)
    orginal_name = Column(String, nullable=False)
    url = Column(String, nullable=False)

    company_profile = relationship("CompanyProfile", back_populates="documents")

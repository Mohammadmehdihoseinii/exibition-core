from .base import ManagerBase
from src.database.models import (
    CompanyProfile, CompanyDocument, 
    ApprovalStatusEnum, Product, ProductImage
)
from sqlalchemy import or_

class CompanyManager(ManagerBase):
    def create(self, user_id, **kwargs):
        session = self.get_session()
        company = CompanyProfile(user_id=user_id, **kwargs)
        return self.save(session, company)

    def get_by_id(self, company_id):
        session = self.get_session()
        company = session.query(CompanyProfile).filter(CompanyProfile.id == company_id).first()
        session.close()
        return company

    def get_by_user_id(self, user_id):
        session = self.get_session()
        company = session.query(CompanyProfile).filter(CompanyProfile.user_id == user_id).first()
        session.close()
        return company

    def update_status(self, company_id, status):
        session = self.get_session()
        company = self.get_by_id(company_id)
        if company:
            company.approval_status = status
            session.commit()
        session.close()
        return company

    def get_pending_companies(self):
        session = self.get_session()
        companies = session.query(CompanyProfile).filter(
            CompanyProfile.approval_status == ApprovalStatusEnum.pending
        ).all()
        session.close()
        return companies

    def get_approved_companies(self):
        session = self.get_session()
        companies = session.query(CompanyProfile).filter(
            CompanyProfile.approval_status == ApprovalStatusEnum.approved
        ).all()
        session.close()
        return companies

    def add_document(self, company_id, name, url):
        session = self.get_session()
        document = CompanyDocument(
            company_profile_id=company_id,
            name=name,
            url=url
        )
        return self.save(session, document)

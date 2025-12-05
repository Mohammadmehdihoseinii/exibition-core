from .base import ManagerBase
from sqlalchemy.orm import selectinload

from src.database.models import (
    CompanyProfile, CompanyDocument,
    CompanyWebsite, CompanyAddress, CompanyPhone,
    CompanyTag, CompanyVideo, CompanyBrochure,
    CompanyKnowledgeFile,
    ApprovalStatusEnum
)


class CompanyManager(ManagerBase):
    def create(self, user_id, **kwargs):
        session = self.get_session()
        company = CompanyProfile(user_id=user_id, **kwargs)
        return self.save(session, company)

    def get_by_id(self, company_id):
        session = self.get_session()
        return (
            session.query(CompanyProfile)
            .options(
                selectinload(CompanyProfile.websites),
                selectinload(CompanyProfile.addresses),
                selectinload(CompanyProfile.phones),
                selectinload(CompanyProfile.tags),
                selectinload(CompanyProfile.videos),
                selectinload(CompanyProfile.brochures),
                selectinload(CompanyProfile.knowledge_files),
            )
            .filter(CompanyProfile.id == company_id)
            .first()
        )

    def get_by_user_id(self, user_id: int):
        session = self.get_session()
        return (
            session.query(CompanyProfile)
            .options(
                selectinload(CompanyProfile.websites),
                selectinload(CompanyProfile.addresses),
                selectinload(CompanyProfile.phones),
                selectinload(CompanyProfile.tags),
                selectinload(CompanyProfile.videos),
                selectinload(CompanyProfile.brochures),
                selectinload(CompanyProfile.knowledge_files),
            )
            .filter(CompanyProfile.user_id == user_id)
            .first()
        )

    def update(self, company_id, **kwargs):
        session = self.get_session()

        company = session.query(CompanyProfile).filter(
            CompanyProfile.id == company_id
        ).first()

        if not company:
            raise ValueError(f"Company with id {company_id} does not exist")

        for key, value in kwargs.items():
            if hasattr(company, key):
                setattr(company, key, value)

        return self.save(session, company, add=False)

    def get_pending_companies(self):
        session = self.get_session()
        return session.query(CompanyProfile).filter(
            CompanyProfile.approval_status == ApprovalStatusEnum.pending
        ).all()

    def get_approved_companies(self):
        session = self.get_session()
        return session.query(CompanyProfile).filter(
            CompanyProfile.approval_status == ApprovalStatusEnum.approved
        ).all()

    def add_child(self, model, company_id, **kwargs):
        session = self.get_session()
        item = model(company_id=company_id, **kwargs)
        return self.save(session, item)

    def delete_child(self, model, item_id):
        session = self.get_session()
        item = session.query(model).filter(model.id == item_id).first()
        print(item)
        if not item:
            raise ValueError(f"Item with id {item_id} does not exist")

        session.delete(item)
        session.commit()
        return True

    def get_child_list(self, model, company_id):
        session = self.get_session()
        return session.query(model).filter(
            model.company_id == company_id
        ).all()

    def get_child_by_id(self, model, item_id):
        session = self.get_session()
        return session.query(model).filter(model.id == item_id).first()

    def add_document(self, company_id, name, url):
        return self.add_child(CompanyDocument, company_id, name=name, url=url)

    def delete_document(self, document_id):
        return self.delete_child(CompanyDocument, document_id)

    def list_documents(self, company_id):
        return self.get_child_list(CompanyDocument, company_id)

    def add_website(self, company_id, name, url):
        return self.add_child(CompanyWebsite, company_id, name=name, url=url)

    def delete_website(self, website_id):
        return self.delete_child(CompanyWebsite, website_id)

    def list_websites(self, company_id):
        return self.get_child_list(CompanyWebsite, company_id)

    def add_address(self, company_id, name, address):
        return self.add_child(CompanyAddress, company_id, name=name, address=address)

    def delete_address(self, address_id):
        return self.delete_child(CompanyAddress, address_id)

    def list_addresses(self, company_id):
        return self.get_child_list(CompanyAddress, company_id)

    def add_phone(self, company_id, name, phone_number):
        return self.add_child(CompanyPhone, company_id, name=name, phone_number=phone_number)

    def delete_phone(self, phone_id):
        return self.delete_child(CompanyPhone, phone_id)

    def list_phones(self, company_id):
        return self.get_child_list(CompanyPhone, company_id)

    def add_tag(self, company_id, tag):
        return self.add_child(CompanyTag, company_id, tag=tag)

    def delete_tag(self, tag_id):
        return self.delete_child(CompanyTag, tag_id)

    def list_tags(self, company_id):
        return self.get_child_list(CompanyTag, company_id)

    def add_video(self, company_id, title, orginal_name, video_url):
        return self.add_child(
            CompanyVideo,
            company_id,
            title=title,
            orginal_name=orginal_name,
            video_url=video_url
        )


    def delete_video(self, video_id):
        return self.delete_child(CompanyVideo, video_id)

    def list_videos(self, company_id):
        return self.get_child_list(CompanyVideo, company_id)

    def add_brochure(self, company_id, title, orginal_name, file_url):
        return self.add_child(CompanyBrochure, company_id, title=title, orginal_name=orginal_name, file_url=file_url)

    def delete_brochure(self, brochure_id):
        return self.delete_child(CompanyBrochure, brochure_id)

    def list_brochures(self, company_id):
        return self.get_child_list(CompanyBrochure, company_id)

    def add_knowledge_file(self, company_id, title, file_url):
        return self.add_child(CompanyKnowledgeFile, company_id, title=title, file_url=file_url)

    def delete_knowledge_file(self, knowledge_file_id):
        return self.delete_child(CompanyKnowledgeFile, knowledge_file_id)

    def list_knowledge_files(self, company_id):
        return self.get_child_list(CompanyKnowledgeFile, company_id)

from .base import ManagerBase
from src.database.models import (
    Exhibition, ExhibitionTag, ExhibitionMedia, 
    ExpoCompany, ExpoStatusEnum, VipLevelEnum,
    OrganizerProfile, CompanyProfile
)
from sqlalchemy import or_, and_
from datetime import datetime

class ExhibitionManager(ManagerBase):
    def create(self, organizer_id, **kwargs):
        session = self.get_session()
        exhibition = Exhibition(organizer_id=organizer_id, **kwargs)
        return self.save(session, exhibition)
    
    def get_by_id(self, exhibition_id):
        session = self.get_session()
        exhibition = session.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
        session.close()
        return exhibition

    def get_by_organizer(self, organizer_id):
        session = self.get_session()
        exhibitions = session.query(Exhibition).filter(
            Exhibition.organizer_id == organizer_id
        ).all()
        session.close()
        return exhibitions

    def update(self, exhibition_id: int, **kwargs):
        """
        بروزرسانی فیلدهای یک نمایشگاه.
        kwargs می‌تواند شامل هر فیلدی مثل name, description, status, year و ... باشد.
        """
        session = self.get_session()
        exhibition = session.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
        if not exhibition:
            session.close()
            return None

        if "status" in kwargs and kwargs["status"] is not None:
            try:
                kwargs["status"] = ExpoStatusEnum(kwargs["status"])
            except ValueError:
                kwargs.pop("status")

        for key, value in kwargs.items():
            setattr(exhibition, key, value)

        return self.save(session, exhibition)

    def get_upcoming_exhibitions(self):
        session = self.get_session()
        now = datetime.utcnow()
        exhibitions = session.query(Exhibition).filter(
            Exhibition.status == ExpoStatusEnum.draft,
            Exhibition.start_date > now
        ).all()
        session.close()
        return exhibitions

    def add_tag(self, exhibition_id, tag):
        session = self.get_session()
        exhibition_tag = ExhibitionTag(exhibition_id=exhibition_id, tag=tag)
        return self.save(session, exhibition_tag)

    def add_media(self, exhibition_id, media_url):
        session = self.get_session()
        media = ExhibitionMedia(exhibition_id=exhibition_id, media_url=media_url)
        return self.save(session, media)

    def search(self, query=None, category=None, year=None, status=None):
        session = self.get_session()
        q = session.query(Exhibition)
        if query and not None:
            q = q.filter(
                or_(
                    Exhibition.name.ilike(f"%{query}%"),
                    Exhibition.description.ilike(f"%{query}%")
                )
            )
        
        if category and not None:
            q = q.filter(Exhibition.category_level == category)
        
        if year and not None:
            q = q.filter(Exhibition.year == year)
        
        if status:
            try:
                status_enum = ExpoStatusEnum(status)
                q = q.filter(Exhibition.status == status_enum)
            except ValueError:
                pass

        exhibitions = q.all()
        session.close()
        return exhibitions

class ExpoCompanyManager(ManagerBase):
    def register_company(self, exhibition_id, company_id, booth_number=None, hall_name=None, vip_level=VipLevelEnum.normal):
        session = self.get_session()
        
        exhibition = session.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
        if not exhibition:
            session.close()
            raise ValueError(f"Exhibition with id {exhibition_id} does not exist")
        
        company = session.query(CompanyProfile).filter(CompanyProfile.id == company_id).first()
        if not company:
            session.close()
            raise ValueError(f"Company with id {company_id} does not exist")
        
        expo_company = ExpoCompany(
            exhibition_id=exhibition_id,
            company_id=company_id,
            booth_number=booth_number,
            hall_name=hall_name,
            vip_level=vip_level
        )
        return self.save(session, expo_company)


    def get_by_exhibition(self, exhibition_id):
        session = self.get_session()
        companies = session.query(ExpoCompany).filter(
            ExpoCompany.exhibition_id == exhibition_id
        ).all()
        session.close()
        return companies

    def get_by_company(self, company_id):
        session = self.get_session()
        exhibitions = session.query(ExpoCompany).filter(
            ExpoCompany.company_id == company_id
        ).all()
        session.close()
        return exhibitions

    def update_booth_info(self, expo_company_id, booth_number=None, hall_name=None, vip_level=None):
        session = self.get_session()
        expo_company = session.query(ExpoCompany).filter(
            ExpoCompany.id == expo_company_id
        ).first()
        
        if expo_company:
            if booth_number:
                expo_company.booth_number = booth_number
            if hall_name:
                expo_company.hall_name = hall_name
            if vip_level:
                expo_company.vip_level = vip_level
            
            session.commit()
            session.refresh(expo_company)
        
        session.close()
        return expo_company

    def get_companies_in_hall(self, exhibition_id, hall_name):
        session = self.get_session()
        companies = session.query(ExpoCompany).filter(
            and_(
                ExpoCompany.exhibition_id == exhibition_id,
                ExpoCompany.hall_name == hall_name
            )
        ).all()
        session.close()
        return companies
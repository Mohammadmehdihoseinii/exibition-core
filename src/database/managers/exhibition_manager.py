from .base import ManagerBase
from src.database.models import (
    Exhibition, ExhibitionTag, ExhibitionMedia, 
    ExpoCompany, ExpoStatusEnum, VipLevelEnum,
    VerificationDocument, CompanyProfile
)
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload
from datetime import datetime
import os

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

        return self.save(session, exhibition, add=False)

    def get_upcoming_exhibitions(self):
        session = self.get_session()
        now = datetime.utcnow()
        exhibitions = session.query(Exhibition).filter(
            Exhibition.status == ExpoStatusEnum.draft,
            Exhibition.start_date > now
        ).all()
        session.close()
        return exhibitions

    def add_tag(self, exhibition_id, tag_name):
        session = self.get_session()
        exhibition = session.query(Exhibition).filter_by(id=exhibition_id).first()
        if not exhibition:
            session.close()
            return None

        self._add_tag_to_exhibition(session, exhibition, tag_name)
        session.commit()
        session.close()
        return True

    def remove_tag(self, exhibition_id, tag_name):
        session = self.get_session()
        exhibition = session.query(Exhibition).filter_by(id=exhibition_id).first()
        if not exhibition:
            session.close()
            return None

        tag = session.query(ExhibitionTag).filter_by(name=tag_name).first()
        if tag and tag in exhibition.tags:
            exhibition.tags.remove(tag)

        session.commit()
        session.close()
        return True

    def _add_tag_to_exhibition(self, session, exhibition, tag_name):
        tag = session.query(ExhibitionTag).filter_by(name=tag_name).first()
        if not tag:
            tag = ExhibitionTag(name=tag_name)
            session.add(tag)
            session.flush()
        if tag not in exhibition.tags:
            exhibition.tags.append(tag)

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
    
    def list_exhibition_years(self):
        session = self.get_session()
        exhibitions = session.query(Exhibition).all()

        year_counts = {}

        for expo in exhibitions:
            start_year = expo.start_date.year
            end_year = expo.end_date.year

            for year in range(start_year, end_year + 1):
                year_counts[year] = year_counts.get(year, 0) + 1

        result = [
            {"year": year, "count": count}
            for year, count in sorted(year_counts.items())
        ]
        session.close()
        return result

    def list_categories(self):
        session = self.get_session()

        categories = (
            session.query(Exhibition.category_level)
            .filter(Exhibition.category_level.isnot(None))
            .distinct()
            .all()
        )

        session.close()

        return [c[0] for c in categories]


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
    
    def list_companies_with_details(self, exhibition_id):
        """
        لیست شرکت‌های یک نمایشگاه همراه با اطلاعات غرفه و پروفایل شرکت.
        """
        session = self.get_session()
        try:
            companies = session.query(ExpoCompany).options(
                joinedload(ExpoCompany.company)
            ).filter(
                ExpoCompany.exhibition_id == exhibition_id
            ).all()

            result = []
            for expo_company in companies:
                company = expo_company.company
                result.append({
                    "id": expo_company.id,
                    "company_id": company.id,
                    "name": company.company_name,
                    "logo": company.logo or "/static/default-logo-exhibition.jpg",
                    "description": company.description,
                    "category_level2": company.industry_category,
                    "category_level3": company.industry_category,
                    "quick_intro_video": None,
                    "booth_number": expo_company.booth_number,
                    "hall_name": expo_company.hall_name,
                    "vip_level": expo_company.vip_level.value if expo_company.vip_level else "normal"
                })

            return result
        finally:
            session.close()
    
class VerificationManager(ManagerBase):
    
    def save_file(self, user_id: int, uploaded_file) -> VerificationDocument:
        """
        ذخیره فایل آپلود شده و ایجاد رکورد در جدول VerificationDocument
        :param user_id: شناسه کاربر یا سازمان
        :param uploaded_file: فایل آپلود شده (UploadFile)
        :return: نمونه VerificationDocument ذخیره شده
        """
        session = self.get_session()
        try:
            # پوشه ذخیره فایل
            upload_dir = "uploads/verification_docs"
            os.makedirs(upload_dir, exist_ok=True)

            # ساخت نام یکتا برای فایل
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            filename = f"{user_id}_{timestamp}_{uploaded_file.filename}"
            file_path = os.path.join(upload_dir, filename)

            # نوشتن فایل روی دیسک
            with open(file_path, "wb") as f:
                f.write(uploaded_file.file.read())  # اگر از FastAPI UploadFile است

            # ساخت رکورد در دیتابیس
            verification_doc = VerificationDocument(
                user_id=user_id,
                filename=uploaded_file.filename,
                file_url=file_path
            )
            session.add(verification_doc)
            session.commit()
            session.refresh(verification_doc)

            return verification_doc

        except Exception as e:
            session.rollback()
            print("❌ Error saving verification document:", e)
            raise e

        finally:
            session.close()
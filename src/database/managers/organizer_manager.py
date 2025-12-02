from .base import ManagerBase
from src.database.models import OrganizerProfile

class OrganizerManager(ManagerBase):
    def create(self, user_id, **kwargs):
        session = self.get_session()
        organizer = OrganizerProfile(user_id=user_id, **kwargs)
        return self.save(session, organizer)

    def get_by_user_id(self, user_id):
        session = self.get_session()
        organizer = session.query(OrganizerProfile).filter(
            OrganizerProfile.user_id == user_id
        ).first()
        session.close()
        return organizer

    def get_by_id(self, organizer_id):
        session = self.get_session()
        organizer = session.query(OrganizerProfile).filter(
            OrganizerProfile.id == organizer_id
        ).first()
        session.close()
        return organizer

    def verify_organizer(self, organizer_id):
        session = self.get_session()

        organizer = session.query(OrganizerProfile).filter(
            OrganizerProfile.id == organizer_id
        ).first()

        if organizer:
            organizer.verified = True
            session.commit()
            session.refresh(organizer)

        session.close()
        return organizer


    def search_organizers(self, query=None, country=None):
        session = self.get_session()
        q = session.query(OrganizerProfile)
        
        if query:
            q = q.filter(
                OrganizerProfile.organization_name.ilike(f"%{query}%")
            )
        
        if country:
            q = q.filter(OrganizerProfile.country == country)
        
        organizers = q.all()
        session.close()
        return organizers
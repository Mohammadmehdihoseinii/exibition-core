from .base import ManagerBase
from src.database.models import User, UserProfile, UserPreferredCategory, UserSocialLink
from sqlalchemy import or_

class UserManager(ManagerBase):
    def create(self, **kwargs):
        session = self.get_session()
        user = User(**kwargs)
        return self.save(session, user)

    def get_by_id(self, user_id):
        session = self.get_session()
        user = session.query(User).filter(User.id == user_id).first()
        session.close()
        return user

    def get_by_email(self, email):
        session = self.get_session()
        user = session.query(User).filter(User.email == email).first()
        session.close()
        return user

    def get_by_username_or_email(self, username_or_email):
        session = self.get_session()
        user = session.query(User).filter(
            or_(
                User.username == username_or_email,
                User.email == username_or_email
            )
        ).first()
        session.close()
        return user

    def update_last_login(self, user_id):
        session = self.get_session()
        from datetime import datetime
        session.query(User).filter(User.id == user_id).update(
            {"last_login": datetime.utcnow()}
        )
        session.commit()
        session.close()

    def activate_user(self, user_id):
        session = self.get_session()
        session.query(User).filter(User.id == user_id).update(
            {"is_active": True}
        )
        session.commit()
        session.close()

    def get_by_role(self, role):
        session = self.get_session()
        users = session.query(User).filter(User.role == role).all()
        session.close()
        return users


class UserProfileManager(ManagerBase):
    def get_by_user_id(self, user_id):
        session = self.get_session()
        profile = session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        session.close()
        return profile

    def create_or_update(self, user_id, **kwargs):
        session = self.get_session()
        profile = self.get_by_user_id(user_id)
        
        if profile:
            for key, value in kwargs.items():
                setattr(profile, key, value)
        else:
            profile = UserProfile(user_id=user_id, **kwargs)
            session.add(profile)
        
        session.commit()
        session.refresh(profile)
        session.close()
        return profile

    def add_preferred_category(self, user_id, category_name):
        session = self.get_session()
        profile = self.get_by_user_id(user_id)
        if profile:
            category = UserPreferredCategory(
                user_profile_id=profile.id,
                category_name=category_name
            )
            session.add(category)
            session.commit()
            session.close()
            return category
        session.close()
        return None

    def add_social_link(self, user_id, platform, url):
        session = self.get_session()
        profile = self.get_by_user_id(user_id)
        if profile:
            social_link = UserSocialLink(
                user_profile_id=profile.id,
                platform=platform,
                url=url
            )
            session.add(social_link)
            session.commit()
            session.close()
            return social_link
        session.close()
        return None
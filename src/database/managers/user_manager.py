from src.database.managers.base import ManagerBase
from src.database.models import User, UserProfile, UserPreferredCategory, UserSocialLink
from sqlalchemy import or_
from passlib.context import CryptContext

class UserManager(ManagerBase):
    def __init__(self, db):
        self.db = db
        self.pwd_context = CryptContext(
            schemes=["argon2"], 
            deprecated="auto"
        )

    def hash_password(self, password: str):
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            print("❌ Error hashing password:", e)
            return None

    def verify_password(self, password: str, hashed: str):
        try:
            return self.pwd_context.verify(password, hashed)
        except Exception as e:
            print("❌ Error verifying password:", e)
            return False

    def create(self, **kwargs):
        session = self.get_session()

        try:
            if "email" in kwargs:
                exists = session.query(User).filter(User.email == kwargs["email"]).first()
                if exists:
                    raise ValueError("Email already registered")

            if "password" in kwargs:
                kwargs["password"] = self.hash_password(kwargs["password"])
                if not kwargs["password"]:
                    raise ValueError("Password hashing failed")

            user = User(**kwargs)
            saved = self.save(session, user)
            return saved

        except Exception as e:
            session.rollback()
            print("❌ Error in create user:", e)
            raise e

        finally:
            session.close()

    def get_by_id(self, user_id):
        session = self.get_session()
        user = session.query(User).filter(User.id == user_id).first()
        session.close()
        return user
    
    def get_by_username_or_email(self, value):
        session = self.get_session()
        user = session.query(User).filter(
            or_(User.username == value,
                 User.email == value
            )
        ).first()
        session.close()
        return user
    
    def update(self, user_id: int, **kwargs):
        """
        به‌روزرسانی اطلاعات کاربر بر اساس user_id.
        اگر پسورد تغییر کند، هش می‌شود.
        سایر فیلدها مستقیماً آپدیت می‌شوند.
        """
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User with id {user_id} not found")

            # هش کردن پسورد در صورت وجود
            if "password" in kwargs:
                hashed = self.hash_password(kwargs["password"])
                if not hashed:
                    raise ValueError("Password hashing failed")
                kwargs["password"] = hashed

            # بروزرسانی بقیه فیلدها
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
                else:
                    print(f"⚠ Skipping unknown field: {key}")

            session.commit()
            session.refresh(user)
            return user

        except Exception as e:
            session.rollback()
            print("❌ Error updating user:", e)
            raise e

        finally:
            session.close()

    
    
    def login(self, username_or_email: str, password: str):
        user = self.get_by_username_or_email(username_or_email)
        if not user:
            return None

        if not self.verify_password(password, user.password):
            return None

        return user
    


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
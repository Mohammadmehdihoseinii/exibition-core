import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)

class Database:
    def __init__(self, db_url: str = None):

        if db_url is None:
            db_url = os.getenv("DATABASE_URL", "sqlite:///./db.sqlite3")

        self.engine = create_engine(
            db_url,
            echo=False,
            future=True
        )

        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )

    def create_tables(self):
        """
        تمام مدل‌ها را import می‌کنیم تا SQLAlchemy آنها را register کند
        """
        from src.database.models.user import User
        from src.database.models.profiles import (
            UserProfile, UserPreferredCategory, UserSocialLink,
            OrganizerProfile
        )
        from src.database.models.company import CompanyProfile, CompanyDocument
        from src.database.models.exhibition import Exhibition, ExhibitionTag, ExhibitionMedia, ExpoCompany
        from src.database.models.product import Product, ProductImage
        from src.database.models.misc import UserFavorite, UserView

        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        return self.SessionLocal()

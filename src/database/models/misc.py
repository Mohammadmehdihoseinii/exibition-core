from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from src.database.database import BaseModel
from src.database.models.enums import FavoriteTypeEnum, ViewTargetEnum


class UserFavorite(BaseModel):
    __tablename__ = "user_favorites"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    favorite_type = Column(Enum(FavoriteTypeEnum), nullable=False)
    target_id = Column(Integer, nullable=False)

    user = relationship("User", back_populates="favorites")

    __table_args__ = (
        UniqueConstraint("user_id", "favorite_type", "target_id"),
    )

class UserView(BaseModel):
    __tablename__ = "user_views"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    target_type = Column(Enum(ViewTargetEnum), nullable=False)
    target_id = Column(Integer, nullable=False)

    viewed_at = Column(DateTime, default=datetime.utcnow, index=True)
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)

    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("user_id", "target_type", "target_id", "viewed_at"),
    )
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from src.database.database import BaseModel
from datetime import datetime, timedelta

class TrackingSession(BaseModel):
    __tablename__ = "tracking_sessions"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) 
    session_id = Column(String, unique=True, nullable=False)
    device_type = Column(String, nullable=True)
    browser = Column(String, nullable=True)
    os = Column(String, nullable=True)
    ip_address = Column(String(45), nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, default=datetime.utcnow)
    page_views_count = Column(Integer, default=0)
    
    user = relationship("User", back_populates="sessions")
    page_views = relationship("TrackingPageView", back_populates="session")


class TrackingPageView(BaseModel):
    __tablename__ = "tracking_page_views"

    session_id = Column(Integer, ForeignKey("tracking_sessions.id"))
    page_url = Column(String)
    viewed_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("TrackingSession", back_populates="page_views")

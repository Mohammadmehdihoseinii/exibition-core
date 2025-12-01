from .base import ManagerBase
from src.database.models import UserView, ViewTargetEnum

class ViewManager(ManagerBase):
    def add_view(self, user_id, target_type, target_id, ip=None, ua=None):
        session = self.get_session()
        view = UserView(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
            ip_address=ip,
            user_agent=ua
        )
        return self.save(session, view)

    def count(self, target_type, target_id):
        session = self.get_session()
        count = (
            session.query(UserView)
            .filter(
                UserView.target_type == target_type,
                UserView.target_id == target_id
            )
            .count()
        )
        session.close()
        return count

    def get_recent_views(self, user_id=None, limit=20):
        session = self.get_session()
        query = session.query(UserView).order_by(UserView.viewed_at.desc())
        
        if user_id:
            query = query.filter(UserView.user_id == user_id)
        
        views = query.limit(limit).all()
        session.close()
        return views

    def get_popular_items(self, target_type, limit=10):
        session = self.get_session()
        from sqlalchemy import func
        
        popular = (
            session.query(
                UserView.target_id,
                func.count(UserView.id).label('view_count')
            )
            .filter(UserView.target_type == target_type)
            .group_by(UserView.target_id)
            .order_by(func.count(UserView.id).desc())
            .limit(limit)
            .all()
        )
        session.close()
        return popular

    def get_views_by_period(self, target_type, target_id, days=30):
        session = self.get_session()
        from datetime import datetime, timedelta
        from sqlalchemy import func, extract
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        views = (
            session.query(
                func.date(UserView.viewed_at).label('view_date'),
                func.count(UserView.id).label('count')
            )
            .filter(
                UserView.target_type == target_type,
                UserView.target_id == target_id,
                UserView.viewed_at >= start_date
            )
            .group_by(func.date(UserView.viewed_at))
            .order_by(func.date(UserView.viewed_at))
            .all()
        )
        session.close()
        return views
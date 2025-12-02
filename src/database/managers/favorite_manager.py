from .base import ManagerBase
from src.database.models import UserFavorite, FavoriteTypeEnum

class FavoriteManager(ManagerBase):
    def add_favorite(self, user_id, favorite_type, target_id):
        session = self.get_session()
        
        existing = session.query(UserFavorite).filter(
            UserFavorite.user_id == user_id,
            UserFavorite.favorite_type == favorite_type,
            UserFavorite.target_id == target_id
        ).first()
        
        if existing:
            session.close()
            return existing
        
        favorite = UserFavorite(
            user_id=user_id,
            favorite_type=favorite_type,
            target_id=target_id
        )
        return self.save(session, favorite)

    def remove_favorite(self, user_id, favorite_type, target_id):
        session = self.get_session()
        favorite = session.query(UserFavorite).filter(
            UserFavorite.user_id == user_id,
            UserFavorite.favorite_type == favorite_type,
            UserFavorite.target_id == target_id
        ).first()
        
        if favorite:
            session.delete(favorite)
            session.commit()
        
        session.close()
        return favorite is not None

    def get_user_favorites(self, user_id, favorite_type=None):
        session = self.get_session()
        query = session.query(UserFavorite).filter(
            UserFavorite.user_id == user_id
        )
        
        if favorite_type:
            query = query.filter(UserFavorite.favorite_type == favorite_type)
        
        favorites = query.all()
        session.close()
        return favorites

    def count_favorites(self, favorite_type, target_id):
        session = self.get_session()
        count = session.query(UserFavorite).filter(
            UserFavorite.favorite_type == favorite_type,
            UserFavorite.target_id == target_id
        ).count()
        session.close()
        return count
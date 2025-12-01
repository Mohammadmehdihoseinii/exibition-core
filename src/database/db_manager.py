from src.database.database import Database
from src.database.managers.user_manager import UserManager, UserProfileManager
from src.database.managers.view_manager import ViewManager
from src.database.managers.exhibition_manager import ExhibitionManager, ExpoCompanyManager
from src.database.managers.company_manager import CompanyManager
from src.database.managers.product_manager import ProductManager
from src.database.managers.organizer_manager import OrganizerManager
from src.database.managers.favorite_manager import FavoriteManager

class DBManager:
    def __init__(self, db_url=None):
        """
        مدیریت اصلی دیتابیس که تمام Managerها را یکجا فراهم می‌کند
        
        Args:
            db_url (str): آدرس دیتابیس (اختیاری)
        """
        self.db = Database(db_url)
        self.db.create_tables()

        # مقداردهی تمام Managerها
        self.user = UserManager(self.db)
        self.user_profile = UserProfileManager(self.db)
        self.view = ViewManager(self.db)
        self.exhibition = ExhibitionManager(self.db)
        self.expo_company = ExpoCompanyManager(self.db)
        self.company = CompanyManager(self.db)
        self.product = ProductManager(self.db)
        self.organizer = OrganizerManager(self.db)
        self.favorite = FavoriteManager(self.db)
        
        # برای backward compatibility
        self.company_manager = self.company
        self.product_manager = self.product
        self.exhibition_manager = self.exhibition
        self.favorite_manager = self.favorite

    def get_session(self):
        """دریافت یک session از دیتابیس"""
        return self.db.get_session()

    def close_all_sessions(self):
        """بستن تمام sessionهای باز"""
        self.db.close_all()

    def drop_tables(self):
        """پاک کردن تمام جداول (برای تست)"""
        self.db.drop_tables()

    def recreate_tables(self):
        """ایجاد مجدد جداول"""
        self.db.drop_tables()
        self.db.create_tables()

    def test_connection(self):
        """تست اتصال به دیتابیس"""
        try:
            session = self.get_session()
            # اجرای یک کوئری ساده
            result = session.execute("SELECT 1")
            session.close()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    def get_stats(self):
        """دریافت آمار کلی دیتابیس"""
        stats = {}
        session = self.get_session()
        
        try:
            # تعداد کاربران
            from src.database.models import User
            stats['total_users'] = session.query(User).count()
            
            # تعداد شرکت‌ها
            from src.database.models import CompanyProfile
            stats['total_companies'] = session.query(CompanyProfile).count()
            
            # تعداد نمایشگاه‌ها
            from src.database.models import Exhibition
            stats['total_exhibitions'] = session.query(Exhibition).count()
            
            # تعداد محصولات
            from src.database.models import Product
            stats['total_products'] = session.query(Product).count()
            
            # تعداد بازدیدها
            from src.database.models import UserView
            stats['total_views'] = session.query(UserView).count()
            
        finally:
            session.close()
        
        return stats


# Singleton instance برای استفاده آسان در سراسر برنامه
_db_manager_instance = None

def get_db_manager(db_url=None):
    """
    دریافت instance منحصربه‌فرد DBManager (Singleton pattern)
    
    Args:
        db_url (str): آدرس دیتابیس (فقط در اولین بار استفاده)
    
    Returns:
        DBManager: instance اصلی
    """
    global _db_manager_instance
    
    if _db_manager_instance is None:
        _db_manager_instance = DBManager(db_url)
    
    return _db_manager_instance


def reset_db_manager(db_url=None):
    """
    بازنشانی instance DBManager (برای تست)
    
    Args:
        db_url (str): آدرس دیتابیس جدید
    
    Returns:
        DBManager: instance جدید
    """
    global _db_manager_instance
    
    if _db_manager_instance:
        _db_manager_instance.close_all_sessions()
    
    _db_manager_instance = DBManager(db_url)
    return _db_manager_instance

db_manager = get_db_manager()
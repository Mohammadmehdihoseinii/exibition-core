from .base import ManagerBase
from src.database.models import Product, ProductImage
from sqlalchemy import or_, desc
from datetime import datetime

class ProductManager(ManagerBase):
    def create(self, company_id, **kwargs):
        """ایجاد محصول جدید"""
        session = self.get_session()
        product = Product(company_id=company_id, **kwargs)
        return self.save(session, product)

    def get_by_id(self, product_id, with_images=False):
        """دریافت محصول با ID"""
        session = self.get_session()
        product = session.query(Product).filter(Product.id == product_id).first()
        
        if with_images and product:
            # برای بارگذاری eager images اگر نیاز باشد
            session.expire_on_commit = False
            _ = product.images
        
        session.close()
        return product

    def get_by_company(self, company_id, limit=None):
        """دریافت محصولات یک شرکت"""
        session = self.get_session()
        query = session.query(Product).filter(Product.company_id == company_id)
        
        if limit:
            query = query.limit(limit)
        
        products = query.all()
        session.close()
        return products

    def update(self, product_id, **kwargs):
        """بروزرسانی محصول"""
        session = self.get_session()
        product = self.get_by_id(product_id)
        
        if product:
            for key, value in kwargs.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            
            product.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(product)
        
        session.close()
        return product

    def delete(self, product_id):
        """حذف محصول"""
        session = self.get_session()
        product = self.get_by_id(product_id)
        
        if product:
            session.delete(product)
            session.commit()
            deleted = True
        else:
            deleted = False
        
        session.close()
        return deleted

    def add_image(self, product_id, url, is_primary=False):
        """افزودن تصویر به محصول"""
        session = self.get_session()
        image = ProductImage(product_id=product_id, url=url)
        
        # اگر اولین تصویر باشد یا primary مشخص شده
        if is_primary:
            # می‌توانید منطق primary image را اینجا پیاده کنید
            pass
        
        return self.save(session, image)

    def get_images(self, product_id):
        """دریافت تصاویر محصول"""
        session = self.get_session()
        images = session.query(ProductImage).filter(
            ProductImage.product_id == product_id
        ).all()
        session.close()
        return images

    def remove_image(self, image_id):
        """حذف تصویر"""
        session = self.get_session()
        image = session.query(ProductImage).filter(ProductImage.id == image_id).first()
        
        if image:
            session.delete(image)
            session.commit()
            deleted = True
        else:
            deleted = False
        
        session.close()
        return deleted

    def search(self, query=None, company_id=None, category=None, limit=50, offset=0):
        """جستجوی محصولات"""
        session = self.get_session()
        q = session.query(Product)
        
        if query:
            q = q.filter(
                or_(
                    Product.title.ilike(f"%{query}%"),
                    Product.summary.ilike(f"%{query}%"),
                    Product.long_description.ilike(f"%{query}%")
                )
            )
        
        if company_id:
            q = q.filter(Product.company_id == company_id)
        
        if category:
            # اگر category فیلد داشته باشید
            pass
        
        products = q.order_by(desc(Product.created_at)).offset(offset).limit(limit).all()
        
        # بارگذاری تصاویر برای هر محصول
        for product in products:
            _ = product.images
        
        session.close()
        return products

    def count_by_company(self, company_id):
        """شمردن محصولات یک شرکت"""
        session = self.get_session()
        count = session.query(Product).filter(
            Product.company_id == company_id
        ).count()
        session.close()
        return count

    def get_featured_products(self, limit=10):
        """دریافت محصولات ویژه (می‌توانید منطق خود را اضافه کنید)"""
        session = self.get_session()
        
        # مثال: محصولات شرکت‌های تایید شده
        from src.database.models import CompanyProfile, ApprovalStatusEnum
        
        products = (
            session.query(Product)
            .join(CompanyProfile, Product.company_id == CompanyProfile.id)
            .filter(CompanyProfile.approval_status == ApprovalStatusEnum.approved)
            .order_by(desc(Product.created_at))
            .limit(limit)
            .all()
        )
        
        session.close()
        return products

    def get_products_with_images(self, product_ids):
        """دریافت چند محصول با تصاویرشان"""
        session = self.get_session()
        
        products = (
            session.query(Product)
            .filter(Product.id.in_(product_ids))
            .all()
        )
        
        # بارگذاری تصاویر
        for product in products:
            _ = product.images
        
        session.close()
        return products
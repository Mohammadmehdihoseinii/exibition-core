from .base import ManagerBase
from sqlalchemy import or_, desc
from datetime import datetime
from sqlalchemy.orm import joinedload

from src.database.models import (
    Product,
    ProductImage,
    ProductBrochure,
    ProductTag,
)

class ProductManager(ManagerBase):
    def create(self, company_id, **data):
        session = self.get_session()

        tags_data = data.pop("tags", [])
        images_data = data.pop("images", [])
        brochures_data = data.pop("brochures", [])

        product = Product(company_id=company_id, **data)
        session.add(product)
        session.commit()

        # اضافه کردن تگ‌ها
        for t in tags_data:
            self._add_tag_to_product(session, product, t)

        # تصاویر
        for img in images_data:
            session.add(ProductImage(product_id=product.id, **img))

        # بروشورها
        for b in brochures_data:
            session.add(ProductBrochure(product_id=product.id, **b))

        session.commit()
        session.refresh(product)
        session.close()
        return product

    def get_by_id(self, product_id):
        session = self.get_session()
        product = session.query(Product).filter(Product.id == product_id).first()
        session.close()
        return product

    def update(self, product_id, **data):
        session = self.get_session()
        product = session.query(Product).filter(Product.id == product_id).first()

        if not product:
            session.close()
            return None
        tags_data = data.pop("tags", None)
        images_data = data.pop("images", None)
        brochures_data = data.pop("brochures", None)

        for key, value in data.items():
            if hasattr(product, key):
                setattr(product, key, value)

        product.updated_at = datetime.utcnow()

        if tags_data is not None:
            product.tags.clear()
            for name in tags_data:
                self._add_tag_to_product(session, product, name)

        session.commit()
        session.refresh(product)

        session.close()
        return product


    def delete(self, product_id):
        session = self.get_session()
        product = session.query(Product).filter_by(id=product_id).first()
        if not product:
            session.close()
            return False
        session.delete(product)
        session.commit()
        session.close()
        return True

    def add_image(self, product_id, url, orginal_name, is_primary=0):
        session = self.get_session()
        if is_primary:
            session.query(ProductImage).filter_by(product_id=product_id).update({"is_primary": 0})
        image = ProductImage(product_id=product_id, url=url, orginal_name=orginal_name, is_primary=is_primary)
        session.add(image)
        session.commit()
        session.refresh(image)
        session.close()
        return image


    def remove_image(self, image_id):
        session = self.get_session()
        image = session.query(ProductImage).filter_by(id=image_id).first()
        if not image:
            session.close()
            return False
        session.delete(image)
        session.commit()
        session.close()
        return True

    def list_image(self, product_id):
        session = self.get_session()
        image = session.query(ProductImage).filter_by(id=product_id).all()
        session.close()
        return image
    
    def add_brochure(self, product_id, title, orginal_name, url):
        session = self.get_session()
        try:
            brochure = ProductBrochure(
                product_id=product_id,
                title=title,
                orginal_name=orginal_name,
                url=url
            )
            session.add(brochure)
            session.commit()
            session.refresh(brochure)
            return brochure

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


    def remove_brochure(self, brochure_id):
        session = self.get_session()
        brochure = session.query(ProductBrochure).filter_by(id=brochure_id).first()
        if not brochure:
            session.close()
            return False
        session.delete(brochure)
        session.commit()
        session.close()
        return True
    
    def list_brochure(self, product_id):
        session = self.get_session()
        brochure = session.query(ProductBrochure).filter(ProductBrochure.product_id == product_id).all()
        session.close()
        return brochure

    def add_tag(self, product_id, tag_name):
        session = self.get_session()
        product = session.query(Product).filter_by(id=product_id).first()
        if not product:
            session.close()
            return None
        self._add_tag_to_product(session, product, tag_name)
        session.commit()
        session.close()
        return True

    def remove_tag(self, product_id, tag_name):
        session = self.get_session()
        product = session.query(Product).filter_by(id=product_id).first()
        if not product:
            session.close()
            return None
        tag = session.query(ProductTag).filter_by(name=tag_name).first()
        if tag and tag in product.tags:
            product.tags.remove(tag)
        session.commit()
        session.close()
        return True
    
    def get_tags_for_product(self, product_id):
        session = self.get_session()
        
        # پیدا کردن محصول بر اساس product_id
        product = session.query(Product).filter_by(id=product_id).first()
        
        if not product:
            session.close()
            return None  # محصول پیدا نشد
        
        # گرفتن تمام تگ‌های محصول به صورت یک لیست از دیکشنری‌ها
        tags = [{"id": tag.id, "name": tag.name} for tag in product.tags]
        
        session.close()
        return tags  # برگرداندن لیست تگ‌ها

    def search(self, query=None, company_id=None, limit=50, offset=0):
        session = self.get_session()
        q = session.query(Product).options(joinedload(Product.images))
        if query:
            q = q.filter(or_(
                Product.title.ilike(f"%{query}%"),
                Product.summary.ilike(f"%{query}%"),
                Product.long_description.ilike(f"%{query}%")
            ))
        if company_id:
            q = q.filter(Product.company_id == company_id)
        products = q.order_by(desc(Product.created_at)).offset(offset).limit(limit).all()
        session.close()
        return products

    def _add_tag_to_product(self, session, product, tag_name):
        tag = session.query(ProductTag).filter_by(name=tag_name).first()
        if not tag:
            tag = ProductTag(name=tag_name)
            session.add(tag)
            session.flush()
        if tag not in product.tags:
            product.tags.append(tag)

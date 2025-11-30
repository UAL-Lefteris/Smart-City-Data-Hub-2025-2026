from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ....core.models.property import Property
from models import ScrapedProperty


class PropertyRepository:

    def __init__(self, session: Session):
        self.session = session

    def create(self, item: ScrapedProperty) -> Property:
        property_obj = Property.from_scraped_item(item)
        self.session.add(property_obj)
        self.session.commit()
        self.session.refresh(property_obj)
        return property_obj

    def bulk_create(self, items: List[ScrapedProperty]) -> int:
        properties = [Property.from_scraped_item(item) for item in items]
        self.session.bulk_save_objects(properties)
        self.session.commit()
        return len(properties)

    def upsert(self, item: ScrapedProperty) -> Property:
        existing = self.get_by_id(item.id)

        if existing:
            existing.state = item.state
            existing.search_location = item.search_location
            existing.address = item.address
            existing.zip_code = item.zip_code
            existing.price = item.price
            existing.slur = item.slur
            existing.description = item.description
            existing.beds = item.beds
            existing.baths = item.baths
            existing.receptions = item.receptions
            existing.epc_rating = item.epc_rating
            existing.image = item.image
            existing.tags = item.tags
            self.session.commit()
            self.session.refresh(existing)
            return existing
        else:
            return self.create(item)

    def bulk_upsert(self, items: List[ScrapedProperty]) -> dict:
        created = 0
        updated = 0

        for item in items:
            existing = self.get_by_id(item.id)
            if existing:
                existing.price = item.price
                existing.state = item.state
                existing.address = item.address
                existing.zip_code = item.zip_code
                existing.slur = item.slur
                existing.description = item.description
                existing.beds = item.beds
                existing.baths = item.baths
                existing.receptions = item.receptions
                existing.epc_rating = item.epc_rating
                existing.tags = item.tags
                updated += 1
            else:
                property_obj = Property.from_scraped_item(item)
                self.session.add(property_obj)
                created += 1

        self.session.commit()
        return {"created": created, "updated": updated}

    def get_by_id(self, property_id: str) -> Optional[Property]:
        return self.session.query(Property).filter(Property.id == property_id).first()

    def get_by_url(self, url: str) -> Optional[Property]:
        return self.session.query(Property).filter(Property.url == url).first()

    def get_all(self, limit: int = None) -> List[Property]:
        query = self.session.query(Property)
        if limit:
            query = query.limit(limit)
        return query.all()

    def get_by_location(self, location: str) -> List[Property]:
        return self.session.query(Property).filter(
            Property.search_location == location
        ).all()

    def get_by_price_range(self, min_price: int, max_price: int) -> List[Property]:
        return self.session.query(Property).filter(
            and_(Property.price >= min_price, Property.price <= max_price)
        ).all()

    def get_by_beds(self, beds: int) -> List[Property]:
        return self.session.query(Property).filter(Property.beds == beds).all()

    def search(
        self,
        location: str = None,
        min_price: int = None,
        max_price: int = None,
        beds: int = None,
        limit: int = None
    ) -> List[Property]:
        query = self.session.query(Property)

        if location:
            query = query.filter(Property.search_location == location)
        if min_price:
            query = query.filter(Property.price >= min_price)
        if max_price:
            query = query.filter(Property.price <= max_price)
        if beds:
            query = query.filter(Property.beds == beds)

        if limit:
            query = query.limit(limit)

        return query.all()

    def get_statistics(self) -> dict:
        total = self.session.query(func.count(Property.id)).scalar()
        avg_price = self.session.query(func.avg(Property.price)).scalar()
        min_price = self.session.query(func.min(Property.price)).scalar()
        max_price = self.session.query(func.max(Property.price)).scalar()

        locations = self.session.query(
            Property.search_location,
            func.count(Property.id)
        ).group_by(Property.search_location).all()

        return {
            "total_properties": total,
            "average_price": float(avg_price) if avg_price else 0,
            "min_price": min_price or 0,
            "max_price": max_price or 0,
            "locations": dict(locations),
        }

    def delete_by_id(self, property_id: str) -> bool:
        property_obj = self.get_by_id(property_id)
        if property_obj:
            self.session.delete(property_obj)
            self.session.commit()
            return True
        return False

    def mark_inactive(self, property_id: str) -> bool:
        property_obj = self.get_by_id(property_id)
        if property_obj:
            property_obj.state = "inactive"
            self.session.commit()
            return True
        return False

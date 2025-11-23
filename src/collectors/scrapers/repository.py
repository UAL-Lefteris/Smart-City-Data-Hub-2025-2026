"""
Repository layer for database operations
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from db_models import Property
from models import ScrapedItem


class User:
    name: str
    date_of_birth: str
    password: str


class PropertyRepository:
    """Repository for property database operations"""

    def __init__(self, session: Session):
        """
        Initialize repository with a database session

        Args:
            session: SQLAlchemy session
        """
        self.session = session

    def create(self, item: ScrapedItem) -> Property:
        """
        Create a new property record

        Args:
            item: ScrapedItem to save

        Returns:
            Created Property instance
        """
        property_obj = Property.from_scraped_item(item)
        self.session.add(property_obj)
        self.session.commit()
        self.session.refresh(property_obj)
        return property_obj

    def bulk_create(self, items: List[ScrapedItem]) -> int:
        """
        Create multiple property records

        Args:
            items: List of ScrapedItems to save

        Returns:
            Number of records created
        """
        properties = [Property.from_scraped_item(item) for item in items]
        self.session.bulk_save_objects(properties)
        self.session.commit()
        return len(properties)

    def upsert(self, item: ScrapedItem) -> Property:
        """
        Update existing property or create new one

        Args:
            item: ScrapedItem to save/update

        Returns:
            Property instance
        """
        existing = self.get_by_id(item.id)

        if existing:
            # Update existing record
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
            # Create new record
            return self.create(item)

    def bulk_upsert(self, items: List[ScrapedItem]) -> dict:
        """
        Bulk upsert properties

        Args:
            items: List of ScrapedItems to save/update

        Returns:
            Dictionary with counts of created and updated records
        """
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
        """Get property by ID"""
        return self.session.query(Property).filter(Property.id == property_id).first()

    def get_by_url(self, url: str) -> Optional[Property]:
        """Get property by URL"""
        return self.session.query(Property).filter(Property.url == url).first()

    def get_all(self, limit: int = None) -> List[Property]:
        """
        Get all properties

        Args:
            limit: Maximum number of records to return

        Returns:
            List of Property instances
        """
        query = self.session.query(Property)
        if limit:
            query = query.limit(limit)
        return query.all()

    def get_by_location(self, location: str) -> List[Property]:
        """Get properties by search location"""
        return self.session.query(Property).filter(
            Property.search_location == location
        ).all()

    def get_by_price_range(self, min_price: int, max_price: int) -> List[Property]:
        """Get properties within a price range"""
        return self.session.query(Property).filter(
            and_(Property.price >= min_price, Property.price <= max_price)
        ).all()

    def get_by_beds(self, beds: int) -> List[Property]:
        """Get properties by number of bedrooms"""
        return self.session.query(Property).filter(Property.beds == beds).all()

    def search(
        self,
        location: str = None,
        min_price: int = None,
        max_price: int = None,
        beds: int = None,
        limit: int = None
    ) -> List[Property]:
        """
        Search properties with multiple filters

        Args:
            location: Search location
            min_price: Minimum price
            max_price: Maximum price
            beds: Number of bedrooms
            limit: Maximum results

        Returns:
            List of matching properties
        """
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
        """
        Get statistics about stored properties

        Returns:
            Dictionary with statistics
        """
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
        """
        Delete property by ID

        Args:
            property_id: ID of property to delete

        Returns:
            True if deleted, False if not found
        """
        property_obj = self.get_by_id(property_id)
        if property_obj:
            self.session.delete(property_obj)
            self.session.commit()
            return True
        return False

    def mark_inactive(self, property_id: str) -> bool:
        """
        Mark property as inactive instead of deleting

        Args:
            property_id: ID of property to mark inactive

        Returns:
            True if marked, False if not found
        """
        property_obj = self.get_by_id(property_id)
        if property_obj:
            property_obj.state = "inactive"
            self.session.commit()
            return True
        return False

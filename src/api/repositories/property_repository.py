from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.core.models.property import Property
from src.api.schemas.property import PropertyCreate, PropertyUpdate


class PropertyRepository:

    @staticmethod
    def create(db: Session, property_data: PropertyCreate) -> Property:
        property_dict = property_data.model_dump()
        db_property = Property(**property_dict)

        db.add(db_property)
        db.commit()
        db.refresh(db_property)

        return db_property

    @staticmethod
    def get_by_id(db: Session, property_id: str) -> Optional[Property]:
        return db.query(Property).filter(Property.id == property_id).first()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Property]:
        return db.query(Property).offset(skip).limit(limit).all()

    @staticmethod
    def get_count(db: Session) -> int:
        return db.query(Property).count()

    @staticmethod
    def search(
        db: Session,
        search_location: Optional[str] = None,
        zip_code: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        beds: Optional[int] = None,
        baths: Optional[int] = None,
        state: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Property]:

        query = db.query(Property)

        filters = []

        if search_location:
            filters.append(Property.search_location.ilike(f"%{search_location}%"))

        if zip_code:
            filters.append(Property.zip_code.ilike(f"%{zip_code}%"))

        if min_price is not None:
            filters.append(Property.price >= min_price)

        if max_price is not None:
            filters.append(Property.price <= max_price)

        if beds is not None:
            filters.append(Property.beds == beds)

        if baths is not None:
            filters.append(Property.baths == baths)

        if state:
            filters.append(Property.state.ilike(f"%{state}%"))

        if filters:
            query = query.filter(and_(*filters))

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def search_count(
        db: Session,
        search_location: Optional[str] = None,
        zip_code: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        beds: Optional[int] = None,
        baths: Optional[int] = None,
        state: Optional[str] = None,
    ) -> int:
        query = db.query(Property)

        filters = []

        if search_location:
            filters.append(Property.search_location.ilike(f"%{search_location}%"))

        if zip_code:
            filters.append(Property.zip_code.ilike(f"%{zip_code}%"))

        if min_price is not None:
            filters.append(Property.price >= min_price)

        if max_price is not None:
            filters.append(Property.price <= max_price)

        if beds is not None:
            filters.append(Property.beds == beds)

        if baths is not None:
            filters.append(Property.baths == baths)

        if state:
            filters.append(Property.state.ilike(f"%{state}%"))

        if filters:
            query = query.filter(and_(*filters))

        return query.count()

    @staticmethod
    def update(
        db: Session,
        property_id: str,
        property_data: PropertyUpdate
    ) -> Optional[Property]:
        db_property = PropertyRepository.get_by_id(db, property_id)

        if db_property is None:
            return None

        update_data = property_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_property, field, value)

        db.commit()
        db.refresh(db_property)

        return db_property

    @staticmethod
    def delete(db: Session, property_id: str) -> bool:
        db_property = PropertyRepository.get_by_id(db, property_id)

        if db_property is None:
            return False

        db.delete(db_property)
        db.commit()

        return True

    @staticmethod
    def get_search_locations(db: Session) -> List[str]:
        locations = db.query(Property.search_location).filter(
            Property.search_location.isnot(None)
        ).distinct().all()
        return sorted([loc[0] for loc in locations if loc[0]])

    @staticmethod
    def get_states(db: Session) -> List[str]:
        states = db.query(Property.state).distinct().all()
        return sorted([state[0] for state in states if state[0]])

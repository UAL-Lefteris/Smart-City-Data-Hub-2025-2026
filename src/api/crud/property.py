from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.api.models.property import Property
from src.api.schemas.property import PropertyCreate, PropertyUpdate


class PropertyCRUD:
    """
    CRUD operations for Property model.

    This class implements the Repository pattern, providing
    a clean interface to database operations.
    """

    @staticmethod
    def create(db: Session, property_data: PropertyCreate) -> Property:
        """
        Create a new property in the database.

        Args:
            db: Database session
            property_data: Property data from request

        Returns:
            Property: Newly created property

        Example:
            new_property = PropertyCRUD.create(
                db,
                PropertyCreate(
                    address="123 High St",
                    borough="Westminster",
                    price=450000,
                    bedrooms=2,
                    property_type="Flat"
                )
            )
        """
        property_dict = property_data.model_dump()

        db_property = Property(**property_dict)

        db.add(db_property)
        db.commit()
        db.refresh(db_property)

        return db_property

    @staticmethod
    def get_by_id(db: Session, property_id: int) -> Optional[Property]:
        """
        Get a single property by ID.

        Args:
            db: Database session
            property_id: Property ID to retrieve

        Returns:
            Property: Property if found, None otherwise

        Example:
            property = PropertyCRUD.get_by_id(db, 1)
            if property is None:
                raise HTTPException(status_code=404)
        """
        return db.query(Property).filter(Property.id == property_id).first()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Property]:
        """
        Get all properties with pagination.

        Args:
            db: Database session
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            List[Property]: List of properties

        Example:
            # Get first 10 properties
            properties = PropertyCRUD.get_all(db, skip=0, limit=10)

            # Get next 10 properties
            properties = PropertyCRUD.get_all(db, skip=10, limit=10)
        """
        return db.query(Property).offset(skip).limit(limit).all()

    @staticmethod
    def get_count(db: Session) -> int:
        """
        Get total count of properties.

        Args:
            db: Database session

        Returns:
            int: Total number of properties

        Example:
            total = PropertyCRUD.get_count(db)
            print(f"Total properties: {total}")
        """
        return db.query(Property).count()

    @staticmethod
    def search(
        db: Session,
        borough: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        bedrooms: Optional[int] = None,
        property_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Property]:
        """
        Search properties with filters.

        Args:
            db: Database session
            borough: Filter by borough name (case-insensitive)
            min_price: Minimum price filter
            max_price: Maximum price filter
            bedrooms: Exact number of bedrooms
            property_type: Filter by property type
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Property]: Filtered list of properties

        Example:
            # Find 2-bedroom flats in Westminster under £500k
            results = PropertyCRUD.search(
                db,
                borough="Westminster",
                max_price=500000,
                bedrooms=2,
                property_type="Flat"
            )
        """
        query = db.query(Property)

        filters = []

        if borough:
            filters.append(Property.borough.ilike(f"%{borough}%"))

        if min_price is not None:
            filters.append(Property.price >= min_price)

        if max_price is not None:
            filters.append(Property.price <= max_price)

        if bedrooms is not None:
            filters.append(Property.bedrooms == bedrooms)

        if property_type:
            filters.append(Property.property_type.ilike(f"%{property_type}%"))

        if filters:
            query = query.filter(and_(*filters))

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def search_count(
        db: Session,
        borough: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        bedrooms: Optional[int] = None,
        property_type: Optional[str] = None,
    ) -> int:
        """
        Get count of properties matching search criteria.

        Args:
            db: Database session
            borough: Filter by borough
            min_price: Minimum price
            max_price: Maximum price
            bedrooms: Number of bedrooms
            property_type: Property type

        Returns:
            int: Count of matching properties
        """
        query = db.query(Property)

        filters = []

        if borough:
            filters.append(Property.borough.ilike(f"%{borough}%"))

        if min_price is not None:
            filters.append(Property.price >= min_price)

        if max_price is not None:
            filters.append(Property.price <= max_price)

        if bedrooms is not None:
            filters.append(Property.bedrooms == bedrooms)

        if property_type:
            filters.append(Property.property_type.ilike(f"%{property_type}%"))

        if filters:
            query = query.filter(and_(*filters))

        return query.count()

    @staticmethod
    def update(
        db: Session,
        property_id: int,
        property_data: PropertyUpdate
    ) -> Optional[Property]:
        """
        Update an existing property.

        Args:
            db: Database session
            property_id: ID of property to update
            property_data: New property data (only provided fields are updated)

        Returns:
            Property: Updated property if found, None otherwise

        Example:
            updated = PropertyCRUD.update(
                db,
                property_id=1,
                PropertyUpdate(price=475000, description="Price reduced!")
            )
        """
        db_property = PropertyCRUD.get_by_id(db, property_id)

        if db_property is None:
            return None

        update_data = property_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_property, field, value)

        db.commit()
        db.refresh(db_property)

        return db_property

    @staticmethod
    def delete(db: Session, property_id: int) -> bool:
        """
        Delete a property.

        Args:
            db: Database session
            property_id: ID of property to delete

        Returns:
            bool: True if property was deleted, False if not found

        Example:
            if PropertyCRUD.delete(db, 1):
                print("Property deleted")
            else:
                raise HTTPException(status_code=404)
        """
        db_property = PropertyCRUD.get_by_id(db, property_id)

        if db_property is None:
            return False

        db.delete(db_property)
        db.commit()

        return True

    @staticmethod
    def get_boroughs(db: Session) -> List[str]:
        """
        Get list of unique boroughs.

        Args:
            db: Database session

        Returns:
            List[str]: Sorted list of unique borough names

        Example:
            boroughs = PropertyCRUD.get_boroughs(db)
            print(f"Available boroughs: {', '.join(boroughs)}")
        """
        boroughs = db.query(Property.borough).distinct().all()
        return sorted([borough[0] for borough in boroughs])

    @staticmethod
    def get_property_types(db: Session) -> List[str]:
        """
        Get list of unique property types.

        Args:
            db: Database session

        Returns:
            List[str]: Sorted list of unique property types

        Example:
            types = PropertyCRUD.get_property_types(db)
        """
        types = db.query(Property.property_type).distinct().all()
        return sorted([ptype[0] for ptype in types])

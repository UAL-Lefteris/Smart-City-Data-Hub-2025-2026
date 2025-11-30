from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.api.repositories.property_repository import PropertyRepository
from src.api.schemas.property import PropertyCreate, PropertyUpdate
from src.core.models.property import Property
from src.api.exceptions import PropertyNotFoundException


class PropertyService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = PropertyRepository

    def get_property(self, property_id: str) -> Property:
        property_obj = self.repository.get_by_id(self.db, property_id)

        if property_obj is None:
            raise PropertyNotFoundException(property_id)

        return property_obj

    def list_properties(self, skip: int = 0, limit: int = 100) -> List[Property]:
        return self.repository.get_all(self.db, skip=skip, limit=limit)

    def create_property(self, property_data: PropertyCreate) -> Property:
        return self.repository.create(self.db, property_data)

    def update_property(
        self,
        property_id: str,
        property_data: PropertyUpdate
    ) -> Property:
        updated_property = self.repository.update(
            self.db,
            property_id,
            property_data
        )

        if updated_property is None:
            raise PropertyNotFoundException(property_id)

        return updated_property

    def delete_property(self, property_id: str) -> None:
        success = self.repository.delete(self.db, property_id)

        if not success:
            raise PropertyNotFoundException(property_id)

    def search_properties(
        self,
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
        return self.repository.search(
            self.db,
            search_location=search_location,
            zip_code=zip_code,
            min_price=min_price,
            max_price=max_price,
            beds=beds,
            baths=baths,
            state=state,
            skip=skip,
            limit=limit,
        )

    def get_property_count(self) -> int:
        return self.repository.get_count(self.db)

    def get_search_count(
        self,
        search_location: Optional[str] = None,
        zip_code: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        beds: Optional[int] = None,
        baths: Optional[int] = None,
        state: Optional[str] = None,
    ) -> int:
        return self.repository.search_count(
            self.db,
            search_location=search_location,
            zip_code=zip_code,
            min_price=min_price,
            max_price=max_price,
            beds=beds,
            baths=baths,
            state=state,
        )

    def get_search_locations(self) -> List[str]:
        return self.repository.get_search_locations(self.db)

    def get_states(self) -> List[str]:
        return self.repository.get_states(self.db)

    def get_property_statistics(self) -> Dict[str, Any]:
        total_count = self.get_property_count()
        locations = self.get_search_locations()
        states = self.get_states()

        return {
            "total_properties": total_count,
            "unique_locations": len(locations),
            "locations": locations,
            "states": states,
        }

from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from src.api.database.session import get_db
from src.api.schemas.property import (
    PropertyCreate,
    PropertyUpdate,
    PropertyResponse,
)
from src.api.services.property_service import PropertyService


router = APIRouter()


def get_property_service(db: Session = Depends(get_db)) -> PropertyService:
    return PropertyService(db)


@router.get(
    "/",
    response_model=List[PropertyResponse],
    status_code=status.HTTP_200_OK,
    summary="List all properties",
    description="""
    Retrieve a list of all properties with pagination support.

    **Pagination:**
    - Use `skip` to offset results (default: 0)
    - Use `limit` to control page size (default: 100, max: 1000)

    **Example:**
    - `/properties?skip=0&limit=10` - First 10 properties
    - `/properties?skip=10&limit=10` - Next 10 properties
    """,
)
def list_properties(
    skip: int = Query(
        0,
        ge=0,
        description="Number of records to skip (for pagination)"
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximum number of records to return"
    ),
    service: PropertyService = Depends(get_property_service),
):
    return service.list_properties(skip=skip, limit=limit)


@router.get(
    "/search",
    response_model=List[PropertyResponse],
    status_code=status.HTTP_200_OK,
    summary="Search properties",
    description="""
    Search and filter properties using query parameters.

    **Available filters:**
    - `search_location` - Filter by search location (partial match, case-insensitive)
    - `zip_code` - Filter by postcode
    - `min_price` - Minimum price in GBP
    - `max_price` - Maximum price in GBP
    - `beds` - Exact number of bedrooms
    - `baths` - Exact number of bathrooms
    - `state` - Property state

    **Pagination:**
    - `skip` - Number of results to skip (default: 0)
    - `limit` - Maximum results to return (default: 100)

    **Examples:**
    - `/properties/search?search_location=Westminster&beds=2`
    - `/properties/search?min_price=300000&max_price=500000`

    All filters can be combined for precise searches.
    """,
)
def search_properties(
    search_location: str = Query(None, description="Filter by search location"),
    zip_code: str = Query(None, description="Filter by postcode"),
    min_price: int = Query(None, ge=0, description="Minimum price"),
    max_price: int = Query(None, ge=0, description="Maximum price"),
    beds: int = Query(None, ge=0, description="Number of bedrooms"),
    baths: int = Query(None, ge=0, description="Number of bathrooms"),
    state: str = Query(None, description="Property state"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: PropertyService = Depends(get_property_service),
):
    if min_price is not None and max_price is not None:
        if max_price < min_price:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail="max_price must be greater than or equal to min_price"
            )

    return service.search_properties(
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


@router.get(
    "/stats/locations",
    response_model=List[str],
    status_code=status.HTTP_200_OK,
    summary="Get list of search locations",
    description="Retrieve a sorted list of all unique search locations in the database.",
)
def get_search_locations(service: PropertyService = Depends(get_property_service)):
    return service.get_search_locations()


@router.get(
    "/stats/states",
    response_model=List[str],
    status_code=status.HTTP_200_OK,
    summary="Get list of property states",
    description="Retrieve a sorted list of all unique property states in the database.",
)
def get_states(service: PropertyService = Depends(get_property_service)):
    return service.get_states()


@router.get(
    "/stats/count",
    status_code=status.HTTP_200_OK,
    summary="Get total property count",
    description="Get the total number of properties in the database.",
)
def get_property_count(service: PropertyService = Depends(get_property_service)):
    count = service.get_property_count()
    return {"total": count}


@router.get(
    "/stats/overview",
    status_code=status.HTTP_200_OK,
    summary="Get property statistics overview",
    description="Get aggregated statistics about properties in the database.",
)
def get_property_statistics(service: PropertyService = Depends(get_property_service)):
    return service.get_property_statistics()


@router.post(
    "/",
    response_model=PropertyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new property",
    description="""
    Create a new property listing.

    **Required fields:**
    - url (string)

    **Optional fields:**
    - All other property fields
    """,
    responses={
        201: {
            "description": "Property created successfully",
        },
        422: {
            "description": "Validation error",
        },
    },
)
def create_property(
    property_data: PropertyCreate,
    service: PropertyService = Depends(get_property_service),
):
    return service.create_property(property_data)


@router.get(
    "/{property_id}",
    response_model=PropertyResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single property",
    description="Retrieve detailed information about a specific property by ID.",
    responses={
        200: {
            "description": "Property found and returned",
        },
        404: {
            "description": "Property not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Not Found",
                        "message": "Property with id 123 not found",
                    }
                }
            },
        },
    },
)
def get_property(
    property_id: str,
    service: PropertyService = Depends(get_property_service),
):
    return service.get_property(property_id)


@router.put(
    "/{property_id}",
    response_model=PropertyResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a property",
    description="""
    Update an existing property.

    **All fields are optional** - only provide fields you want to update.

    The updated_at timestamp will be automatically set to the current time.
    """,
    responses={
        200: {
            "description": "Property updated successfully",
        },
        404: {
            "description": "Property not found",
        },
        422: {
            "description": "Validation error",
        },
    },
)
def update_property(
    property_id: str,
    property_data: PropertyUpdate,
    service: PropertyService = Depends(get_property_service),
):
    return service.update_property(property_id, property_data)


@router.delete(
    "/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a property",
    description="Delete a property from the database.",
    responses={
        204: {
            "description": "Property deleted successfully (no content returned)",
        },
        404: {
            "description": "Property not found",
        },
    },
)
def delete_property(
    property_id: str,
    service: PropertyService = Depends(get_property_service),
):
    service.delete_property(property_id)
    return None

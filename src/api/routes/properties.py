from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from src.api.database.session import get_db
from src.api.schemas.property import (
    PropertyCreate,
    PropertyUpdate,
    PropertyResponse,
)
from src.api.crud.property import PropertyCRUD
from src.api.exceptions import PropertyNotFoundException


router = APIRouter()


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
    db: Session = Depends(get_db),
):
    """
    **List all properties with pagination.**

    This endpoint returns a paginated list of all properties
    in the database. Use skip and limit parameters to control
    pagination.

    Returns:
        List[PropertyResponse]: List of property objects
    """
    properties = PropertyCRUD.get_all(db, skip=skip, limit=limit)
    return properties


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
    property_id: int,
    db: Session = Depends(get_db),
):
    """
    **Get a single property by ID.**

    Args:
        property_id: Unique identifier of the property

    Returns:
        PropertyResponse: Property details

    Raises:
        PropertyNotFoundException: If property doesn't exist
    """
    property_obj = PropertyCRUD.get_by_id(db, property_id)

    if property_obj is None:
        raise PropertyNotFoundException(property_id)

    return property_obj


@router.post(
    "/",
    response_model=PropertyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new property",
    description="""
    Create a new property listing.

    **Required fields:**
    - address (string)
    - borough (string)
    - property_type (string)
    - bedrooms (integer, >= 0)
    - price (float, > 0)

    **Optional fields:**
    - postcode
    - latitude
    - longitude
    - description
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
    db: Session = Depends(get_db),
):
    """
    **Create a new property.**

    This endpoint creates a new property record in the database.
    All required fields must be provided and pass validation.

    Args:
        property_data: Property data from request body

    Returns:
        PropertyResponse: Newly created property with generated ID and timestamps
    """
    new_property = PropertyCRUD.create(db, property_data)
    return new_property


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
    property_id: int,
    property_data: PropertyUpdate,
    db: Session = Depends(get_db),
):
    """
    **Update an existing property.**

    Only the fields provided in the request body will be updated.
    Other fields remain unchanged.

    Args:
        property_id: ID of property to update
        property_data: Updated property data (partial updates allowed)

    Returns:
        PropertyResponse: Updated property

    Raises:
        PropertyNotFoundException: If property doesn't exist
    """
    updated_property = PropertyCRUD.update(db, property_id, property_data)

    if updated_property is None:
        raise PropertyNotFoundException(property_id)

    return updated_property


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
    property_id: int,
    db: Session = Depends(get_db),
):
    """
    **Delete a property.**

    This permanently removes the property from the database.

    Args:
        property_id: ID of property to delete

    Returns:
        None (204 No Content)

    Raises:
        PropertyNotFoundException: If property doesn't exist
    """
    success = PropertyCRUD.delete(db, property_id)

    if not success:
        raise PropertyNotFoundException(property_id)

    return None


@router.get(
    "/search/",
    response_model=List[PropertyResponse],
    status_code=status.HTTP_200_OK,
    summary="Search properties",
    description="""
    Search and filter properties using query parameters.

    **Available filters:**
    - `borough` - Filter by borough name (partial match, case-insensitive)
    - `min_price` - Minimum price in GBP
    - `max_price` - Maximum price in GBP
    - `bedrooms` - Exact number of bedrooms
    - `property_type` - Property type (partial match, case-insensitive)

    **Pagination:**
    - `skip` - Number of results to skip (default: 0)
    - `limit` - Maximum results to return (default: 100)

    **Examples:**
    - `/properties/search?borough=Westminster&bedrooms=2`
    - `/properties/search?min_price=300000&max_price=500000`
    - `/properties/search?property_type=Flat&borough=Camden`

    All filters can be combined for precise searches.
    """,
)
def search_properties(
    borough: str = Query(None, description="Filter by borough name"),
    min_price: float = Query(None, ge=0, description="Minimum price"),
    max_price: float = Query(None, ge=0, description="Maximum price"),
    bedrooms: int = Query(None, ge=0, description="Number of bedrooms"),
    property_type: str = Query(None, description="Property type"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
):
    """
    **Search properties with filters.**

    Combine multiple filters to find specific properties.
    All filters are optional and can be used together.

    Args:
        borough: Filter by borough (case-insensitive)
        min_price: Minimum price filter
        max_price: Maximum price filter
        bedrooms: Filter by number of bedrooms
        property_type: Filter by property type (case-insensitive)
        skip: Pagination offset
        limit: Maximum results

    Returns:
        List[PropertyResponse]: Filtered list of properties
    """
    # Validate price range
    if min_price is not None and max_price is not None:
        if max_price < min_price:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail="max_price must be greater than or equal to min_price"
            )

    properties = PropertyCRUD.search(
        db,
        borough=borough,
        min_price=min_price,
        max_price=max_price,
        bedrooms=bedrooms,
        property_type=property_type,
        skip=skip,
        limit=limit,
    )

    return properties


@router.get(
    "/stats/boroughs",
    response_model=List[str],
    status_code=status.HTTP_200_OK,
    summary="Get list of boroughs",
    description="Retrieve a sorted list of all unique borough names in the database.",
)
def get_boroughs(db: Session = Depends(get_db)):
    """
    **Get list of unique boroughs.**

    Returns a sorted list of all boroughs that have properties.
    Useful for populating dropdown filters in UI.

    Returns:
        List[str]: Sorted list of borough names
    """
    return PropertyCRUD.get_boroughs(db)


@router.get(
    "/stats/property-types",
    response_model=List[str],
    status_code=status.HTTP_200_OK,
    summary="Get list of property types",
    description="Retrieve a sorted list of all unique property types in the database.",
)
def get_property_types(db: Session = Depends(get_db)):
    """
    **Get list of unique property types.**

    Returns a sorted list of all property types.
    Useful for populating dropdown filters in UI.

    Returns:
        List[str]: Sorted list of property types
    """
    return PropertyCRUD.get_property_types(db)


@router.get(
    "/stats/count",
    status_code=status.HTTP_200_OK,
    summary="Get total property count",
    description="Get the total number of properties in the database.",
)
def get_property_count(db: Session = Depends(get_db)):
    """
    **Get total property count.**

    Returns:
        dict: Object containing total count
    """
    count = PropertyCRUD.get_count(db)
    return {"total": count}

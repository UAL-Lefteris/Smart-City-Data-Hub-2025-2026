from fastapi import APIRouter, Depends, Query, status, Body
from typing import Optional, List, Dict, Any
from pymongo.database import Database

from src.api.database.session import get_mongo_db
from src.api.services.carbon_service import CarbonService


router = APIRouter()


def get_carbon_service(mongo_db: Database = Depends(get_mongo_db)) -> CarbonService:
    return CarbonService(mongo_db)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="List all carbon intensity data",
    description="""
    Retrieve a list of all carbon intensity data with pagination support.

    **Pagination:**
    - Use `skip` to offset results (default: 0)
    - Use `limit` to control page size (default: 100, max: 1000)

    **Example:**
    - `/carbon?skip=0&limit=10` - First 10 records
    - `/carbon?skip=10&limit=10` - Next 10 records
    """
)
async def list_carbon_data(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    service: CarbonService = Depends(get_carbon_service)
):
    return service.get_all_carbon_data(skip=skip, limit=limit)


@router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    summary="Search carbon intensity data",
    description="""
    Search and filter carbon intensity data using query parameters.

    **Available filters:**
    - `region_id` - Filter by specific region ID
    - `postcode` - Filter by postcode (case-insensitive)
    - `min_intensity` - Minimum carbon intensity forecast value
    - `max_intensity` - Maximum carbon intensity forecast value
    - `intensity_index` - Filter by intensity level (low, moderate, high, very high)
    - `min_renewable` - Minimum renewable percentage (0-100)
    - `max_renewable` - Maximum renewable percentage (0-100)

    **Pagination:**
    - `skip` - Number of results to skip (default: 0)
    - `limit` - Maximum results to return (default: 100)

    **Examples:**
    - `/carbon/search?intensity_index=low`
    - `/carbon/search?min_intensity=50&max_intensity=150`
    - `/carbon/search?region_id=13&min_renewable=50`

    All filters can be combined for precise searches.
    """
)
async def search_carbon_data(
    region_id: Optional[int] = Query(None, description="Filter by region ID"),
    postcode: Optional[str] = Query(None, description="Filter by postcode"),
    min_intensity: Optional[int] = Query(None, ge=0, description="Minimum carbon intensity"),
    max_intensity: Optional[int] = Query(None, ge=0, description="Maximum carbon intensity"),
    intensity_index: Optional[str] = Query(None, description="Intensity level (low, moderate, high, very high)"),
    min_renewable: Optional[float] = Query(None, ge=0, le=100, description="Minimum renewable percentage"),
    max_renewable: Optional[float] = Query(None, ge=0, le=100, description="Maximum renewable percentage"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: CarbonService = Depends(get_carbon_service)
):
    return service.search_carbon_data(
        region_id=region_id,
        postcode=postcode,
        min_intensity=min_intensity,
        max_intensity=max_intensity,
        intensity_index=intensity_index,
        min_renewable=min_renewable,
        max_renewable=max_renewable,
        skip=skip,
        limit=limit
    )


@router.get(
    "/stats/regions",
    response_model=List[int],
    status_code=status.HTTP_200_OK,
    summary="Get list of region IDs",
    description="Retrieve a sorted list of all unique region IDs in the database."
)
async def get_regions(service: CarbonService = Depends(get_carbon_service)):
    return service.get_regions()


@router.get(
    "/stats/postcodes",
    response_model=List[str],
    status_code=status.HTTP_200_OK,
    summary="Get list of postcodes",
    description="Retrieve a sorted list of all unique postcodes in the database."
)
async def get_postcodes(service: CarbonService = Depends(get_carbon_service)):
    return service.get_postcodes()


@router.get(
    "/stats/shortnames",
    response_model=List[str],
    status_code=status.HTTP_200_OK,
    summary="Get list of region shortnames",
    description="Retrieve a sorted list of all unique region shortnames in the database."
)
async def get_shortnames(service: CarbonService = Depends(get_carbon_service)):
    return service.get_shortnames()


@router.get(
    "/stats/intensity_indices",
    response_model=List[str],
    status_code=status.HTTP_200_OK,
    summary="Get list of intensity index values",
    description="Retrieve a sorted list of all unique intensity index values (low, moderate, high, very high)."
)
async def get_intensity_indices(service: CarbonService = Depends(get_carbon_service)):
    return service.get_intensity_indices()


@router.get(
    "/stats/count",
    status_code=status.HTTP_200_OK,
    summary="Get total record count",
    description="Get the total number of carbon intensity records in the database."
)
async def get_carbon_count(service: CarbonService = Depends(get_carbon_service)):
    total = service.repository.count_all()
    return {"total": total}


@router.get(
    "/stats/overview",
    status_code=status.HTTP_200_OK,
    summary="Get carbon data statistics overview",
    description="""
    Get comprehensive aggregated statistics about carbon intensity data.

    Includes:
    - Total number of records
    - Unique regions and postcodes count
    - Latest data timestamp
    - Average carbon intensity
    - Average renewable percentage
    - Distribution by intensity index
    """
)
async def get_overview_statistics(service: CarbonService = Depends(get_carbon_service)):
    return service.get_overview_statistics()


@router.get(
    "/stats",
    status_code=status.HTTP_200_OK,
    summary="Get basic carbon data statistics",
    description="Get basic aggregated statistics about carbon intensity data (legacy endpoint)."
)
async def get_carbon_statistics(service: CarbonService = Depends(get_carbon_service)):
    return service.get_carbon_statistics()


@router.get(
    "/latest",
    status_code=status.HTTP_200_OK,
    summary="Get latest carbon intensity data",
    description="Retrieve the most recent carbon intensity data record.",
    responses={
        200: {"description": "Latest carbon data found and returned"},
        404: {"description": "No carbon data found"}
    }
)
async def get_latest_carbon_data(service: CarbonService = Depends(get_carbon_service)):
    return service.get_latest_carbon_data()


@router.get(
    "/regions",
    status_code=status.HTTP_200_OK,
    summary="Get carbon data by region IDs",
    description="""
    Get carbon data filtered by region IDs (comma-separated).

    **Example:**
    - `/carbon/regions?region_ids=10,11,13`
    """
)
async def get_carbon_by_regions(
    region_ids: Optional[str] = Query(None, description="Comma-separated region IDs (e.g., '10,11,13')"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: CarbonService = Depends(get_carbon_service)
):
    return service.get_carbon_by_regions(
        region_ids=region_ids,
        skip=skip,
        limit=limit
    )


@router.get(
    "/postcodes",
    status_code=status.HTTP_200_OK,
    summary="Get carbon data by postcodes",
    description="""
    Get carbon data filtered by postcodes (comma-separated).

    **Example:**
    - `/carbon/postcodes?postcodes=SW1A,E1,WC2N`
    """
)
async def get_carbon_by_postcodes(
    postcodes: Optional[str] = Query(None, description="Comma-separated postcodes (e.g., 'SW1A,E1,WC2N')"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: CarbonService = Depends(get_carbon_service)
):
    return service.get_carbon_by_postcodes(
        postcodes=postcodes,
        skip=skip,
        limit=limit
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new carbon intensity record",
    description="""
    Create a new carbon intensity record in the database.

    **Example:**
    ```json
    {
        "region_id": 13,
        "shortname": "London",
        "postcode": "SW1A",
        "intensity_forecast": 150,
        "intensity_index": "moderate",
        "renewable_percentage": 45.5,
        "from": "2024-01-15T10:00:00Z",
        "to": "2024-01-15T10:30:00Z"
    }
    ```
    """,
    responses={
        201: {"description": "Carbon record created successfully"},
        400: {"description": "Validation error"},
        422: {"description": "Request validation error"}
    }
)
async def create_carbon_record(
    carbon_data: Dict[str, Any] = Body(...),
    service: CarbonService = Depends(get_carbon_service)
):
    return service.create_carbon_record(carbon_data)


@router.get(
    "/{record_id}",
    status_code=status.HTTP_200_OK,
    summary="Get a single carbon intensity record",
    description="Retrieve detailed information about a specific carbon intensity record by MongoDB ID.",
    responses={
        200: {"description": "Carbon record found and returned"},
        404: {
            "description": "Carbon record not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Carbon record with id 507f1f77bcf86cd799439011 not found"
                    }
                }
            }
        }
    }
)
async def get_carbon_record(
    record_id: str,
    service: CarbonService = Depends(get_carbon_service)
):
    return service.get_carbon_record(record_id)


@router.put(
    "/{record_id}",
    status_code=status.HTTP_200_OK,
    summary="Update a carbon intensity record",
    description="""
    Update an existing carbon intensity record.

    **All fields are optional** - only provide fields you want to update.

    **Example:**
    ```json
    {
        "intensity_forecast": 180,
        "intensity_index": "high",
        "renewable_percentage": 40.0
    }
    ```
    """,
    responses={
        200: {"description": "Carbon record updated successfully"},
        400: {"description": "Validation error"},
        404: {"description": "Carbon record not found"},
        422: {"description": "Request validation error"}
    }
)
async def update_carbon_record(
    record_id: str,
    carbon_data: Dict[str, Any] = Body(...),
    service: CarbonService = Depends(get_carbon_service)
):
    return service.update_carbon_record(record_id, carbon_data)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a carbon intensity record",
    description="Delete a carbon intensity record from the database.",
    responses={
        204: {"description": "Carbon record deleted successfully (no content returned)"},
        404: {"description": "Carbon record not found"}
    }
)
async def delete_carbon_record(
    record_id: str,
    service: CarbonService = Depends(get_carbon_service)
):
    service.delete_carbon_record(record_id)
    return None

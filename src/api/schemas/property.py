from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class PropertyBase(BaseModel):

    url: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Property listing URL",
        examples=["https://example.com/property/12345"],
    )

    state: str = Field(
        default="active",
        max_length=20,
        description="Property state (active, sold, removed)",
        examples=["active", "sold"],
    )

    search_location: Optional[str] = Field(
        None,
        max_length=200,
        description="Search location used to find property",
        examples=["London", "Westminster"],
    )

    address: Optional[str] = Field(
        None,
        max_length=500,
        description="Full street address of the property",
        examples=["123 High Street, London"],
    )

    zip_code: Optional[str] = Field(
        None,
        max_length=20,
        description="UK postcode/zip code",
        examples=["SW1A 1AA"],
    )

    price: Optional[int] = Field(
        None,
        description="Property price in GBP",
        examples=[450000],
    )

    slur: Optional[str] = Field(
        None,
        max_length=500,
        description="Property title/slug",
        examples=["2-bedroom-flat-in-westminster"],
    )

    description: Optional[str] = Field(
        None,
        description="Property description",
        examples=["Spacious 2-bedroom flat with modern kitchen"],
    )

    beds: Optional[int] = Field(
        None,
        ge=0,
        description="Number of bedrooms",
        examples=[2],
    )

    baths: Optional[int] = Field(
        None,
        ge=0,
        description="Number of bathrooms",
        examples=[1],
    )

    receptions: Optional[int] = Field(
        None,
        ge=0,
        description="Number of reception rooms",
        examples=[1],
    )

    epc_rating: Optional[str] = Field(
        None,
        max_length=5,
        description="Energy Performance Certificate rating",
        examples=["C", "B"],
    )

    image: Optional[str] = Field(
        None,
        description="Property image URL",
    )

    tags: Optional[List[str]] = Field(
        default=[],
        description="Property tags/features",
        examples=[["garden", "parking"]],
    )

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[int]) -> Optional[int]:
        """Validate that price is positive and reasonable."""
        if v is not None:
            if v <= 0:
                raise ValueError("Price must be greater than 0")
            if v > 100_000_000:
                raise ValueError("Price seems unreasonably high")
        return v

    @field_validator("zip_code")
    @classmethod
    def validate_zip_code(cls, v: Optional[str]) -> Optional[str]:
        """Normalize UK postcode to uppercase."""
        if v:
            return v.strip().upper()
        return v


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):

    url: Optional[str] = Field(None, max_length=500)
    state: Optional[str] = Field(None, max_length=20)
    search_location: Optional[str] = Field(None, max_length=200)
    address: Optional[str] = Field(None, max_length=500)
    zip_code: Optional[str] = Field(None, max_length=20)
    price: Optional[int] = Field(None, gt=0)
    slur: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None)
    beds: Optional[int] = Field(None, ge=0)
    baths: Optional[int] = Field(None, ge=0)
    receptions: Optional[int] = Field(None, ge=0)
    epc_rating: Optional[str] = Field(None, max_length=5)
    image: Optional[str] = Field(None)
    tags: Optional[List[str]] = Field(None)

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[int]) -> Optional[int]:
        """Validate price if provided."""
        if v is not None:
            if v <= 0:
                raise ValueError("Price must be greater than 0")
            if v > 100_000_000:
                raise ValueError("Price seems unreasonably high")
        return v


class PropertyResponse(PropertyBase):

    id: str = Field(
        ...,
        description="Unique property identifier",
        examples=["abc123def456"],
    )

    scraped_date: Optional[datetime] = Field(
        None,
        description="Timestamp when property was scraped",
    )

    updated_date: Optional[datetime] = Field(
        None,
        description="Timestamp when property was last updated",
    )

    class Config:
        """Pydantic configuration."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "abc123def456",
                "url": "https://example.com/property/12345",
                "state": "active",
                "address": "123 High Street, London",
                "search_location": "Westminster",
                "zip_code": "SW1A 1AA",
                "price": 450000,
                "beds": 2,
                "baths": 1,
                "description": "Spacious 2-bedroom flat",
                "scraped_date": "2024-01-15T10:30:00Z",
                "updated_date": "2024-01-15T10:30:00Z",
            }
        }


class PropertySearchParams(BaseModel):

    search_location: Optional[str] = Field(
        None,
        description="Filter by search location",
        examples=["Westminster", "London"],
    )

    zip_code: Optional[str] = Field(
        None,
        description="Filter by postcode",
        examples=["SW1A"],
    )

    min_price: Optional[int] = Field(
        None,
        ge=0,
        description="Minimum price in GBP",
        examples=[300000],
    )

    max_price: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum price in GBP",
        examples=[500000],
    )

    beds: Optional[int] = Field(
        None,
        ge=0,
        description="Exact number of bedrooms",
        examples=[2],
    )

    baths: Optional[int] = Field(
        None,
        ge=0,
        description="Exact number of bathrooms",
        examples=[1],
    )

    state: Optional[str] = Field(
        None,
        description="Filter by property state",
        examples=["active", "sold"],
    )

    @field_validator("max_price")
    @classmethod
    def validate_price_range(cls, v: Optional[int], info) -> Optional[int]:
        min_price = info.data.get("min_price")
        if v is not None and min_price is not None:
            if v < min_price:
                raise ValueError("max_price must be greater than or equal to min_price")
        return v

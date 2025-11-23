from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class PropertyBase(BaseModel):
    """
    Base property schema with common fields.

    This schema contains fields that are shared across
    create, update, and response schemas.
    """

    address: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Full street address of the property",
        examples=["123 High Street, London"],
    )

    borough: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="London borough name",
        examples=["Westminster", "Camden", "Hackney"],
    )

    postcode: Optional[str] = Field(
        None,
        max_length=10,
        description="UK postcode",
        examples=["SW1A 1AA"],
    )

    property_type: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Type of property",
        examples=["Flat", "House", "Terraced", "Semi-Detached", "Detached"],
    )

    bedrooms: int = Field(
        ...,
        ge=0,
        le=20,
        description="Number of bedrooms (0-20)",
        examples=[2],
    )

    price: float = Field(
        ...,
        gt=0,
        description="Property price in GBP (must be positive)",
        examples=[450000.00],
    )

    latitude: Optional[float] = Field(
        None,
        ge=-90,
        le=90,
        description="Geographic latitude (-90 to 90)",
        examples=[51.5074],
    )

    longitude: Optional[float] = Field(
        None,
        ge=-180,
        le=180,
        description="Geographic longitude (-180 to 180)",
        examples=[-0.1278],
    )

    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Additional property details",
        examples=["Spacious 2-bedroom flat with modern kitchen"],
    )

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        """
        Validate that price is positive and reasonable.

        Args:
            v: Price value to validate

        Returns:
            float: Validated price

        Raises:
            ValueError: If price is not positive or too large
        """
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        if v > 100_000_000:  # £100 million
            raise ValueError("Price seems unreasonably high")
        return round(v, 2)  # Round to 2 decimal places

    @field_validator("bedrooms")
    @classmethod
    def validate_bedrooms(cls, v: int) -> int:
        """
        Validate number of bedrooms.

        Args:
            v: Number of bedrooms

        Returns:
            int: Validated bedroom count

        Raises:
            ValueError: If bedrooms is negative
        """
        if v < 0:
            raise ValueError("Number of bedrooms cannot be negative")
        return v

    @field_validator("borough")
    @classmethod
    def validate_borough(cls, v: str) -> str:
        """
        Normalize borough name (title case).

        Args:
            v: Borough name

        Returns:
            str: Normalized borough name
        """
        return v.strip().title()

    @field_validator("postcode")
    @classmethod
    def validate_postcode(cls, v: Optional[str]) -> Optional[str]:
        """
        Normalize UK postcode to uppercase.

        Args:
            v: Postcode string

        Returns:
            str: Normalized postcode
        """
        if v:
            return v.strip().upper()
        return v


class PropertyCreate(PropertyBase):
    """
    Schema for creating a new property.

    Inherits all fields from PropertyBase.
    All required fields must be provided.

    Example:
        {
            "address": "123 High Street, London",
            "borough": "Westminster",
            "property_type": "Flat",
            "bedrooms": 2,
            "price": 450000.00,
            "postcode": "SW1A 1AA",
            "latitude": 51.5074,
            "longitude": -0.1278
        }
    """

    pass


class PropertyUpdate(BaseModel):
    """
    Schema for updating an existing property.

    All fields are optional - only provide fields you want to update.

    Example:
        {
            "price": 475000.00,
            "description": "Price reduced!"
        }
    """

    address: Optional[str] = Field(
        None,
        min_length=5,
        max_length=500,
        description="Full street address",
    )

    borough: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="London borough",
    )

    postcode: Optional[str] = Field(
        None,
        max_length=10,
        description="UK postcode",
    )

    property_type: Optional[str] = Field(
        None,
        min_length=2,
        max_length=50,
        description="Type of property",
    )

    bedrooms: Optional[int] = Field(
        None,
        ge=0,
        le=20,
        description="Number of bedrooms",
    )

    price: Optional[float] = Field(
        None,
        gt=0,
        description="Property price in GBP",
    )

    latitude: Optional[float] = Field(
        None,
        ge=-90,
        le=90,
        description="Geographic latitude",
    )

    longitude: Optional[float] = Field(
        None,
        ge=-180,
        le=180,
        description="Geographic longitude",
    )

    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Property description",
    )

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[float]) -> Optional[float]:
        """Validate price if provided."""
        if v is not None:
            if v <= 0:
                raise ValueError("Price must be greater than 0")
            if v > 100_000_000:
                raise ValueError("Price seems unreasonably high")
            return round(v, 2)
        return v

    @field_validator("bedrooms")
    @classmethod
    def validate_bedrooms(cls, v: Optional[int]) -> Optional[int]:
        """Validate bedrooms if provided."""
        if v is not None and v < 0:
            raise ValueError("Number of bedrooms cannot be negative")
        return v


class PropertyResponse(PropertyBase):
    """
    Schema for property responses.

    Includes all property data plus:
    - id: Database identifier
    - created_at: When property was created
    - updated_at: When property was last updated

    This is what clients receive when requesting property data.
    """

    id: int = Field(
        ...,
        description="Unique property identifier",
        examples=[1],
    )

    created_at: datetime = Field(
        ...,
        description="Timestamp when property was created",
    )

    updated_at: datetime = Field(
        ...,
        description="Timestamp when property was last updated",
    )

    class Config:
        """Pydantic configuration."""

        from_attributes = True  # Enable ORM mode for SQLAlchemy models
        json_schema_extra = {
            "example": {
                "id": 1,
                "address": "123 High Street, London",
                "borough": "Westminster",
                "postcode": "SW1A 1AA",
                "property_type": "Flat",
                "bedrooms": 2,
                "price": 450000.00,
                "latitude": 51.5074,
                "longitude": -0.1278,
                "description": "Spacious 2-bedroom flat",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            }
        }


class PropertySearchParams(BaseModel):
    """
    Schema for property search query parameters.

    All parameters are optional - combine them to filter results.

    Example:
        /properties/search?borough=Westminster&min_price=300000&max_price=500000&bedrooms=2
    """

    borough: Optional[str] = Field(
        None,
        description="Filter by borough name",
        examples=["Westminster"],
    )

    min_price: Optional[float] = Field(
        None,
        ge=0,
        description="Minimum price in GBP",
        examples=[300000],
    )

    max_price: Optional[float] = Field(
        None,
        ge=0,
        description="Maximum price in GBP",
        examples=[500000],
    )

    bedrooms: Optional[int] = Field(
        None,
        ge=0,
        description="Exact number of bedrooms",
        examples=[2],
    )

    property_type: Optional[str] = Field(
        None,
        description="Filter by property type",
        examples=["Flat"],
    )

    @field_validator("max_price")
    @classmethod
    def validate_price_range(cls, v: Optional[float], info) -> Optional[float]:
        """
        Validate that max_price >= min_price.

        Args:
            v: Maximum price
            info: Validation context with other field values

        Returns:
            float: Validated max price

        Raises:
            ValueError: If max_price < min_price
        """
        min_price = info.data.get("min_price")
        if v is not None and min_price is not None:
            if v < min_price:
                raise ValueError("max_price must be greater than or equal to min_price")
        return v

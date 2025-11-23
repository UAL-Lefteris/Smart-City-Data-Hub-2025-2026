from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from datetime import datetime

from src.api.database.connection import Base


class Property(Base):
    """
    Property model representing a London property listing.

    Attributes:
        id: Primary key, auto-incrementing
        address: Full property address
        borough: London borough name
        price: Property price in GBP
        bedrooms: Number of bedrooms
        property_type: Type of property (e.g., 'Flat', 'House', 'Terraced')
        postcode: UK postcode
        latitude: Geographic latitude
        longitude: Geographic longitude
        description: Additional property details
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """

    __tablename__ = "properties"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Unique identifier for the property",
    )

    address = Column(
        String(500),
        nullable=False,
        comment="Full street address of the property",
    )

    borough = Column(
        String(100),
        nullable=False,
        index=True,
        comment="London borough where property is located",
    )

    postcode = Column(
        String(10),
        nullable=True,
        comment="UK postcode",
    )

    property_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Type of property (Flat, House, Terraced, etc.)",
    )

    bedrooms = Column(
        Integer,
        nullable=False,
        index=True,
        comment="Number of bedrooms",
    )

    price = Column(
        Float,
        nullable=False,
        index=True,
        comment="Property price in GBP",
    )

    latitude = Column(
        Float,
        nullable=True,
        comment="Geographic latitude coordinate",
    )

    longitude = Column(
        Float,
        nullable=True,
        comment="Geographic longitude coordinate",
    )

    description = Column(
        Text,
        nullable=True,
        comment="Additional property description or notes",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when property was added to database",
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when property was last updated",
    )

    def __repr__(self) -> str:
        """
        String representation of Property object.

        Returns:
            str: Human-readable property description
        """
        return (
            f"<Property(id={self.id}, "
            f"address='{self.address}', "
            f"borough='{self.borough}', "
            f"price=£{self.price:,.2f})>"
        )

    def to_dict(self) -> dict:
        """
        Convert Property object to dictionary.

        Returns:
            dict: Dictionary representation of property

        Note:
            This is useful for JSON serialization and debugging
        """
        return {
            "id": self.id,
            "address": self.address,
            "borough": self.borough,
            "postcode": self.postcode,
            "property_type": self.property_type,
            "bedrooms": self.bedrooms,
            "price": self.price,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

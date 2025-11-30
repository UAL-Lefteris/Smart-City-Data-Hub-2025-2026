from sqlalchemy import Column, String, Integer, Text, DateTime, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Property(Base):
    __tablename__ = "properties"

    # Primary key
    id = Column(String(32), primary_key=True, index=True)

    # URLs and metadata
    url = Column(String(500), unique=True, nullable=False, index=True)
    state = Column(String(20), default="active", index=True)
    scraped_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())

    # Location information
    search_location = Column(String(200), index=True)
    address = Column(String(500))
    zip_code = Column(String(20), index=True)

    # Property details
    price = Column(Integer, index=True)
    slur = Column(String(500))
    description = Column(Text)

    # Room counts
    beds = Column(Integer, index=True)
    baths = Column(Integer)
    receptions = Column(Integer)

    # Additional details
    epc_rating = Column(String(5))
    image = Column(Text)

    # Tags
    tags = Column(ARRAY(String), default=[])

    def __repr__(self):
        """String representation"""
        return f"<Property(id='{self.id}', slur='{self.slur}', price={self.price})>"

    @classmethod
    def from_scraped_item(cls, item):
        """
        Create a Property instance from a ScrapedItem

        Args:
            item: ScrapedItem instance

        Returns:
            Property instance
        """
        return cls(
            id=item.id,
            url=item.url,
            state=item.state,
            search_location=item.search_location,
            address=item.address,
            zip_code=item.zip_code,
            price=item.price,
            slur=item.slur,
            description=item.description,
            beds=item.beds,
            baths=item.baths,
            receptions=item.receptions,
            epc_rating=item.epc_rating,
            image=item.image,
            tags=item.tags,
        )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'url': self.url,
            'state': self.state,
            'scraped_date': self.scraped_date.isoformat() if self.scraped_date else None,
            'updated_date': self.updated_date.isoformat() if self.updated_date else None,
            'search_location': self.search_location,
            'address': self.address,
            'zip_code': self.zip_code,
            'price': self.price,
            'slur': self.slur,
            'description': self.description,
            'beds': self.beds,
            'baths': self.baths,
            'receptions': self.receptions,
            'epc_rating': self.epc_rating,
            'image': self.image,
            'tags': self.tags,
        }
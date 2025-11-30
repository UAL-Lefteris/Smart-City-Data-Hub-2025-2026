from dataclasses import dataclass, field
from typing import List


@dataclass
class ScrapedProperty:
    id: str = ""
    url: str = ""
    state: str = "active"
    date: str = ""
    search_location: str = ""
    address: str = ""
    zip_code: str = ""
    price: int = 0
    slur: str = ""
    description: str = ""
    beds: int = 0
    baths: int = 0
    receptions: int = 0
    epc_rating: str = ""
    image: str = ""
    tags: List[str] = field(default_factory=list)

    def __str__(self):
        return (
            f"ScrapedItem(slur='{self.slur}', price=£{self.price:,}, "
            f"beds={self.beds}, location='{self.search_location}')"
        )

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'state': self.state,
            'date': self.date,
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

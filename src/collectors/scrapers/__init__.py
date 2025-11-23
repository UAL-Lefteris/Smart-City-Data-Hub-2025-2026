"""
Property Web Scraper Package

A web scraper for property listings from Zoopla.
"""

from .models import ScrapedItem
from .scraper import PropertyScraper
from .config import LONDON_AREAS

__version__ = "1.0.0"
__all__ = ["ScrapedItem", "PropertyScraper", "LONDON_AREAS"]

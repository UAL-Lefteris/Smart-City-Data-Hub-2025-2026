"""
Utility functions for the property scraper
"""

from typing import List
from models import ScrapedItem


def print_summary(items: List[ScrapedItem], locations: List[str]):
    """
    Print a summary of scraped items

    Args:
        items: List of ScrapedItem objects
        locations: List of locations that were scraped
    """
    if not items:
        print("\n" + "=" * 60)
        print("SCRAPING SUMMARY")
        print("=" * 60)
        print(f"No items were scraped")
        print("=" * 60 + "\n")
        return

    # Calculate statistics
    total_items = len(items)
    items_with_price = [item for item in items if item.price > 0]

    avg_price = sum(item.price for item in items_with_price) / len(items_with_price) if items_with_price else 0
    min_price = min((item.price for item in items_with_price), default=0)
    max_price = max((item.price for item in items_with_price), default=0)

    # Count by location
    location_counts = {}
    for item in items:
        loc = item.search_location
        location_counts[loc] = location_counts.get(loc, 0) + 1

    # Count by bedrooms
    bedroom_counts = {}
    for item in items:
        beds = item.beds if item.beds > 0 else "Unknown"
        bedroom_counts[beds] = bedroom_counts.get(beds, 0) + 1

    # Print summary
    print("\n" + "=" * 60)
    print("SCRAPING SUMMARY")
    print("=" * 60)
    print(f"Total locations scraped: {len(locations)}")
    print(f"Total properties found: {total_items}")
    print(f"\nPrice Statistics:")
    print(f"  Average price: £{avg_price:,.0f}")
    print(f"  Min price: £{min_price:,}")
    print(f"  Max price: £{max_price:,}")

    print(f"\nTop 10 Locations by Property Count:")
    sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
    for loc, count in sorted_locations[:10]:
        print(f"  {loc}: {count} properties")

    print(f"\nProperty Distribution by Bedrooms:")
    sorted_bedrooms = sorted(bedroom_counts.items(), key=lambda x: (x[0] if isinstance(x[0], int) else 999))
    for beds, count in sorted_bedrooms:
        print(f"  {beds} bed{'s' if beds != 1 else ''}: {count} properties")

    print("=" * 60 + "\n")


def format_price(price: int) -> str:
    """
    Format a price as GBP currency

    Args:
        price: Price in pounds

    Returns:
        Formatted price string
    """
    return f"£{price:,}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length

    Args:
        text: Text to truncate
        max_length: Maximum length (default: 100)

    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

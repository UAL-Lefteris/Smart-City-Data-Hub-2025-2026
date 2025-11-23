"""
Web scraper for property listings

This is the main entry point for the scraper.
"""

from scraper import PropertyScraper
from config import LONDON_AREAS, DATABASE_URL
from database import Database
from repository import PropertyRepository
import json


def main(save_to_db: bool = True):
    """
    Main function to run the scraper

    Args:
        save_to_db: Whether to save results to database (default: True)

    Returns:
        List of scraped items
    """

    # Initialize scraper
    print("Initializing scraper...")
    scraper = PropertyScraper(headless=True)

    # Initialize database if needed
    db = None
    if save_to_db:
        print(f"Connecting to database...")
        db = Database(DATABASE_URL)
        db.create_tables()
        print("Database connection established\n")

    # Scrape all areas
    items = scraper.scrape_all_areas(LONDON_AREAS)

    # Save to database
    if save_to_db and db and items:
        print(f"\n{'='*60}")
        print("Saving to database...")
        print(f"{'='*60}\n")

        with db.session_scope() as session:
            repo = PropertyRepository(session)
            result = repo.bulk_upsert(items)

            print(f"Database save complete:")
            print(f"  - Created: {result['created']} properties")
            print(f"  - Updated: {result['updated']} properties")
            print(f"  - Total: {result['created'] + result['updated']} properties")

            # Print database statistics
            stats = repo.get_statistics()
            print(f"\nDatabase Statistics:")
            print(f"  - Total properties in DB: {stats['total_properties']}")
            print(f"  - Average price: £{stats['average_price']:,.0f}")
            print(f"  - Price range: £{stats['min_price']:,} - £{stats['max_price']:,}")

    with open("output.json", "w") as f:
        json.dump([item.to_dict() for item in items], f)

    return items


if __name__ == "__main__":
    main(save_to_db=False)

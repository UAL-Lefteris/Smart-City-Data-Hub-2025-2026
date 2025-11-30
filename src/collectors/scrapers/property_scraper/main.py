from scraper import PropertyScraper
from config import LONDON_AREAS
from repository import PropertyRepository
import json

from ....database.database import database


def main(create_tables: bool = False, save_to_db: bool = True):
    scraper = PropertyScraper(headless=True)

    if save_to_db and create_tables:
        database.create_tables()

    items = scraper.scrape_all_areas(LONDON_AREAS)

    if save_to_db and items:
        print(f"\n{'='*60}")
        print("Saving to database...")
        print(f"{'='*60}\n")

        with database.connect() as session:
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
    else:
        with open("output.json", "w") as f:
            json.dump([item.to_dict() for item in items], f)

    return items


if __name__ == "__main__":
    main(save_to_db=False)

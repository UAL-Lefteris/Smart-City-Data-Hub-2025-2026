import os
import random
import hashlib
import base64

from faker import Faker
from datetime import datetime, timedelta

from ...models.property import Property
from ....database.database import database

# Configuration
fake = Faker('en_GB')
NUM_ENTRIES = 1000


# Values
STATES = ['active', 'inactive', 'pending', 'sold']

SEARCH_LOCATIONS = [
    "Holborn, London",
    "Shoreditch, London",
    "Camden, London",
    "Islington, London",
    "Hackney, London",
    "Bethnal Green, London",
    "Clerkenwell, London",
    "Farringdon, London",
    "Kings Cross, London",
    "Angel, London",
    "Bloomsbury, London",
    "Fitzrovia, London",
    "Marylebone, London",
    "Mayfair, London",
    "Soho, London",
    "Covent Garden, London",
    "Westminster, London",
    "Pimlico, London",
    "Belgravia, London",
    "Chelsea, London",
    "Kensington, London",
    "Notting Hill, London",
    "Paddington, London",
    "Bayswater, London",
    "Hammersmith, London",
    "Fulham, London",
    "Battersea, London",
    "Clapham, London",
    "Brixton, London",
    "Kennington, London",
    "Vauxhall, London",
    "Waterloo, London",
    "Southwark, London",
    "Bermondsey, London",
    "London Bridge, London",
    "Tower Bridge, London",
    "Wapping, London",
    "Canary Wharf, London",
    "Limehouse, London",
    "Whitechapel, London",
    "Stratford, London",
    "Greenwich, London",
    "Deptford, London",
    "New Cross, London",
    "Peckham, London",
    "Dulwich, London",
    "Stockwell, London",
    "Oval, London",
    "Camberwell, London",
]

EPC_RATINGS = ['A', 'B', 'C', 'D', 'E']

PROPERTY_TAGS = ['garden', 'parking', 'balcony', 'new_build', 'period_property',
                 'garage', 'terrace', 'near_transport', 'schools_nearby', 'quiet_area']



#region Utility Functions
def generate_property_id(url):
    return hashlib.md5(url.encode()).hexdigest()


def random_date(start_days_ago=365, end_days_ago=0):
    start = datetime.now() - timedelta(days=start_days_ago)
    end = datetime.now() - timedelta(days=end_days_ago)
    return start + (end - start) * random.random()


def generate_base64_string(length_kb=50):
    random_bytes = os.urandom(length_kb * 1024)
    base64_string = base64.b64encode(random_bytes).decode('utf-8')

    return base64_string


def generate_property():
    search_location = random.choice(SEARCH_LOCATIONS)
    street_address = fake.street_address()

    slug = f"{street_address.lower().replace(' ', '-').replace(',', '')}-{fake.uuid4()[:8]}"
    url = f"https://www.zoopla.co.uk/properties/{slug}"

    scraped = random_date(90, 0)
    updated = random_date(30, 0) if random.random() > 0.3 else None

    tags = random.sample(PROPERTY_TAGS, k=random.randint(0, 5))

    image_base64 = generate_base64_string(length_kb=random.randint(20, 100))

    return Property(
        id=generate_property_id(url),
        url=url,
        state=random.choice(STATES),
        scraped_date=scraped,
        updated_date=updated,
        search_location=search_location,
        address=f"{street_address}, {search_location}",
        zip_code=fake.postcode(),
        price=random.randint(150000, 2000000) // 5000 * 5000,
        slur=slug,
        description=fake.text(max_nb_chars=300),
        beds=random.randint(1, 6),
        baths=random.randint(1, 4),
        receptions=random.randint(1, 3),
        epc_rating=random.choice(EPC_RATINGS),
        image=image_base64,
        tags=tags
    )


def populate_database(num_entries=NUM_ENTRIES, create_tables=False):
    try:
        session = database.connect()

        if create_tables:
            database.create_tables()

        properties = []
        for i in range(num_entries):
            prop = generate_property(as_dict=False)
            session.add(prop)
            properties.append({
                'price': prop.price,
                'search_location': prop.search_location
            })

            if (i + 1) % 100 == 0:
                session.commit()
                print(f"  Inserted {i + 1}/{num_entries} properties...")

        session.commit()

        session.close()

    except Exception as e:
        print(f"Error: {e}")
        raise

#endregion Utility Functions


def main():
    populate_database(NUM_ENTRIES, create_tables=False)


if __name__ == "__main__":
    main()
# Timing settings
BASE_WAIT_DURATION = 1

MAX_PAGES_PER_AREA = None
MAX_LISTINGS_PER_AREA = None

# Browser settings
HEADLESS = True
BROWSER_ARGS = [
    '--disable-blink-features=AutomationControlled',
    '--disable-dev-shm-usage',
    '--no-sandbox'
]

VIEWPORT = {
    'width': 1920,
    'height': 1080
}

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Selectors
SELECTORS = {
    'cookie_accept': '#accept',
    'search_input': '._1xvvvlo0.fjlmpi8',
    'search_button': '._1co9d006._1co9d007._1co9d008._1co9d00e._1co9d00m._1co9d000._1co9d001.fjlmpi8.fjlmpid',
    'for_sale_button': '.v5ylzz1.v5ylzz4.v5ylzz9',
    'listing_card': '.dkr2t86',
    'pagination': 'ol.jx0me43 li a',

    'address': 'address._1olqsf98',
    'price': 'p.fjlmpi3.r4q9to1',
    'title': 'h1.fjlmpi8._1olqsf97',
    'description': '#detailed-desc',
    'room_details': 'ul._1wmbmfq1 li p.fjlmpi8._1wmbmfq3',
    'epc_rating': 'li._1olqsf9a p.fjlmpi8.w9r0350',
    'image': 'img.tnabq05.tnabq06._14l7d4c2',
    'tags': 'ul._1wz55u80 li',
}

# URLs
BASE_URL = 'https://www.zoopla.co.uk'

# Timeout settings
TIMEOUT_SHORT = 5000
TIMEOUT_MEDIUM = 10000
TIMEOUT_LONG = 30000

# London areas to scrape
LONDON_AREAS = [
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

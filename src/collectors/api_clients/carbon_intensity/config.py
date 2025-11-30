import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parents[4] / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    MONGODB_URI = os.getenv("MONGODB_URL")
    MONGODB_DATABASE = os.getenv("MONGODB_NAME")
    MONGODB_COLLECTION = 'carbon_data'

    CARBON_API_BASE_URL = 'https://api.carbonintensity.org.uk'

    LONDON_REGION_IDS = [10, 11, 12, 13]
    LONDON_POSTCODES = [
        'SW1A', 'E1', 'WC2N',
        'W1', 'WC1', 'EC1',
        'E2', 'E3', 'E14',
        'W2', 'W6', 'W8', 'W11',
        'N1', 'N7', 'NW1', 'NW3',
        'SW3', 'SW7', 'SE1', 'SE10',
        'BR1', 'HA1', 'IG1', 'TW9', 'CR0'
    ]

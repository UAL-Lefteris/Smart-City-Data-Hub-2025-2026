class Config:
    MONGODB_URI = 'mongodb://localhost:27017/'
    MONGODB_DATABASE = 'carbon_intensity_db'
    MONGODB_COLLECTION = 'carbon_data'

    CARBON_API_BASE_URL = 'https://api.carbonintensity.org.uk'

    LONDON_REGION_IDS = [10, 11, 13]
    LONDON_POSTCODES = ['SW1A', 'E1', 'WC2N']

import requests
from datetime import datetime
from config import Config


class CarbonIntensityExtractor:
    def __init__(self):
        self.base_url = Config.CARBON_API_BASE_URL

    def get_current_intensity(self):
        endpoint = f"{self.base_url}/intensity"
        response = requests.get(endpoint)
        return response.json()

    def get_regional_data_by_postcode(self, postcode):
        url_postcode = postcode.replace(' ', '')
        endpoint = f"{self.base_url}/regional/postcode/{url_postcode}"
        response = requests.get(endpoint)
        data = response.json()
        data['postcode_queried'] = postcode
        return data

    def get_regional_data_by_region_id(self, region_id):
        endpoint = f"{self.base_url}/regional/regionid/{region_id}"
        response = requests.get(endpoint)
        data = response.json()
        data['region_id_queried'] = region_id
        return data

    def get_london_data(self):
        results = {
            'london_regions': [],
            'london_postcodes': []
        }

        for region_id in Config.LONDON_REGION_IDS:
            data = self.get_regional_data_by_region_id(region_id)
            results['london_regions'].append(data)

        for postcode in Config.LONDON_POSTCODES:
            data = self.get_regional_data_by_postcode(postcode)
            results['london_postcodes'].append(data)

        return results

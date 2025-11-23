from extract import CarbonIntensityExtractor
from transform import CarbonIntensityTransformer
from load import CarbonIntensityLoader

print("EXTRACT: Fetching data from API...")
extractor = CarbonIntensityExtractor()
raw_data = extractor.get_london_data()

print("TRANSFORM: Processing data...")
transformer = CarbonIntensityTransformer()
all_records = []

for region_data in raw_data['london_regions']:
    records = transformer.transform_regional_data(region_data)
    all_records.extend(records)

for postcode_data in raw_data['london_postcodes']:
    records = transformer.transform_regional_data(postcode_data)
    all_records.extend(records)

print(f"LOAD: Saving {len(all_records)} records to MongoDB...")
loader = CarbonIntensityLoader()
loader.insert_records(all_records)
loader.close()

print("Done!")

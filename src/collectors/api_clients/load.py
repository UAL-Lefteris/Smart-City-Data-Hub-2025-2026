from pymongo import MongoClient
from config import Config


class CarbonIntensityLoader:
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URI)
        self.db = self.client[Config.MONGODB_DATABASE]
        self.collection = self.db[Config.MONGODB_COLLECTION]

    def insert_records(self, records):
        if records:
            self.collection.insert_many(records, ordered=False)
            return len(records)
        return 0

    def get_all_records(self):
        return list(self.collection.find())

    def close(self):
        self.client.close()

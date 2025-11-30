from typing import List, Dict, Any, Optional
from pymongo.database import Database
from bson import ObjectId


class CarbonRepository:

    def __init__(self, mongo_db: Database):
        self.mongo_db = mongo_db
        self.collection = mongo_db['carbon_data']

    def find_all(self, skip: int = 0, limit: int = 100) -> tuple[List[Dict], int]:
        cursor = self.collection.find().skip(skip).limit(limit)
        data = list(cursor)
        total_count = self.collection.count_documents({})

        return data, total_count

    def find_by_regions(
        self,
        region_ids: List[int],
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Dict], int]:
        query = {"london_regions.region_id_queried": {"$in": region_ids}}

        cursor = self.collection.find(query).skip(skip).limit(limit)
        data = list(cursor)
        total_count = self.collection.count_documents(query)

        return data, total_count

    def find_by_postcodes(
        self,
        postcodes: List[str],
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Dict], int]:
        query = {"london_postcodes.postcode_queried": {"$in": postcodes}}

        cursor = self.collection.find(query).skip(skip).limit(limit)
        data = list(cursor)
        total_count = self.collection.count_documents(query)

        return data, total_count

    def find_latest(self) -> Optional[Dict]:
        return self.collection.find_one(sort=[("timestamp", -1)])

    def count_all(self) -> int:
        return self.collection.count_documents({})

    def get_distinct_regions(self) -> List[int]:
        return self.collection.distinct("london_regions.region_id_queried")

    def get_distinct_postcodes(self) -> List[str]:
        return self.collection.distinct("london_postcodes.postcode_queried")

    def search(
        self,
        region_id: Optional[int] = None,
        postcode: Optional[str] = None,
        min_intensity: Optional[int] = None,
        max_intensity: Optional[int] = None,
        intensity_index: Optional[str] = None,
        min_renewable: Optional[float] = None,
        max_renewable: Optional[float] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Dict], int]:
        query = {}

        if region_id is not None:
            query["region_id"] = region_id

        if postcode:
            query["postcode"] = postcode.upper()

        if min_intensity is not None or max_intensity is not None:
            query["intensity_forecast"] = {}
            if min_intensity is not None:
                query["intensity_forecast"]["$gte"] = min_intensity
            if max_intensity is not None:
                query["intensity_forecast"]["$lte"] = max_intensity

        if intensity_index:
            query["intensity_index"] = intensity_index.lower()

        if min_renewable is not None or max_renewable is not None:
            query["renewable_percentage"] = {}
            if min_renewable is not None:
                query["renewable_percentage"]["$gte"] = min_renewable
            if max_renewable is not None:
                query["renewable_percentage"]["$lte"] = max_renewable

        cursor = self.collection.find(query).skip(skip).limit(limit)
        data = list(cursor)
        total_count = self.collection.count_documents(query)

        return data, total_count

    def get_distinct_shortnames(self) -> List[str]:
        return self.collection.distinct("shortname")

    def get_distinct_intensity_indices(self) -> List[str]:
        return self.collection.distinct("intensity_index")

    def get_average_intensity(self) -> Optional[float]:
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "avg_intensity": {"$avg": "$intensity_forecast"}
                }
            }
        ]
        result = list(self.collection.aggregate(pipeline))
        return result[0]["avg_intensity"] if result else None

    def get_average_renewable_percentage(self) -> Optional[float]:
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "avg_renewable": {"$avg": "$renewable_percentage"}
                }
            }
        ]
        result = list(self.collection.aggregate(pipeline))
        return result[0]["avg_renewable"] if result else None

    def get_intensity_distribution(self) -> Dict[str, int]:
        pipeline = [
            {
                "$group": {
                    "_id": "$intensity_index",
                    "count": {"$sum": 1}
                }
            }
        ]
        result = list(self.collection.aggregate(pipeline))
        return {item["_id"]: item["count"] for item in result}

    def create(self, carbon_data: Dict[str, Any]) -> Dict:
        result = self.collection.insert_one(carbon_data)
        created_doc = self.collection.find_one({"_id": result.inserted_id})
        return created_doc

    def get_by_id(self, record_id: str) -> Optional[Dict]:
        try:
            return self.collection.find_one({"_id": ObjectId(record_id)})
        except Exception:
            return None

    def update(self, record_id: str, update_data: Dict[str, Any]) -> Optional[Dict]:
        try:
            update_data = {k: v for k, v in update_data.items() if v is not None}

            if not update_data:
                return self.get_by_id(record_id)

            result = self.collection.find_one_and_update(
                {"_id": ObjectId(record_id)},
                {"$set": update_data},
                return_document=True
            )
            return result
        except Exception:
            return None

    def delete(self, record_id: str) -> bool:
        try:
            result = self.collection.delete_one({"_id": ObjectId(record_id)})
            return result.deleted_count > 0
        except Exception:
            return False

from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from pymongo.database import Database

from src.api.repositories.carbon_repository import CarbonRepository
from src.api.cache.cache_manager import cached

class CarbonService:

    def __init__(self, mongo_db: Database):
        self.repository = CarbonRepository(mongo_db)

    def _serialize_mongo_data(self, data: List[Dict]) -> List[Dict]:
        for item in data:
            if '_id' in item:
                item['_id'] = str(item['_id'])
        return data

    def get_all_carbon_data(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        try:
            data, total_count = self.repository.find_all(skip=skip, limit=limit)
            data = self._serialize_mongo_data(data)

            return {
                "data": data,
                "total": total_count,
                "skip": skip,
                "limit": limit
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving carbon data: {str(e)}"
            )

    def get_carbon_by_regions(
        self,
        region_ids: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        try:
            region_list = None

            if region_ids:
                region_list = [int(rid.strip()) for rid in region_ids.split(',')]
                data, total_count = self.repository.find_by_regions(
                    region_ids=region_list,
                    skip=skip,
                    limit=limit
                )
            else:
                # No filter, get all
                data, total_count = self.repository.find_all(skip=skip, limit=limit)

            data = self._serialize_mongo_data(data)

            return {
                "data": data,
                "total": total_count,
                "skip": skip,
                "limit": limit,
                "filters": {"region_ids": region_list}
            }
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid region IDs format: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving carbon data: {str(e)}"
            )

    def get_carbon_by_postcodes(
        self,
        postcodes: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        try:
            postcode_list = None

            if postcodes:
                postcode_list = [pc.strip().upper() for pc in postcodes.split(',')]
                data, total_count = self.repository.find_by_postcodes(
                    postcodes=postcode_list,
                    skip=skip,
                    limit=limit
                )
            else:
                data, total_count = self.repository.find_all(skip=skip, limit=limit)

            data = self._serialize_mongo_data(data)

            return {
                "data": data,
                "total": total_count,
                "skip": skip,
                "limit": limit,
                "filters": {"postcodes": postcode_list}
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving carbon data: {str(e)}"
            )

    def get_latest_carbon_data(self) -> Dict[str, Any]:
        try:
            latest = self.repository.find_latest()

            if not latest:
                raise HTTPException(
                    status_code=404,
                    detail="No carbon data found"
                )

            if '_id' in latest:
                latest['_id'] = str(latest['_id'])

            return latest
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving latest carbon data: {str(e)}"
            )

    def get_carbon_statistics(self) -> Dict[str, Any]:
        try:
            total_records = self.repository.count_all()
            latest = self.repository.find_latest()
            unique_regions = self.repository.get_distinct_regions()
            unique_postcodes = self.repository.get_distinct_postcodes()

            return {
                "total_records": total_records,
                "unique_regions": len(unique_regions) if unique_regions else 0,
                "unique_postcodes": len(unique_postcodes) if unique_postcodes else 0,
                "latest_timestamp": latest.get("timestamp") if latest else None,
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error calculating statistics: {str(e)}"
            )

    def search_carbon_data(
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
    ) -> Dict[str, Any]:
        try:
            if intensity_index:
                valid_indices = ['low', 'moderate', 'high', 'very high']
                if intensity_index.lower() not in valid_indices:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid intensity_index. Must be one of: {', '.join(valid_indices)}"
                    )

            if min_intensity is not None and max_intensity is not None:
                if max_intensity < min_intensity:
                    raise HTTPException(
                        status_code=400,
                        detail="max_intensity must be greater than or equal to min_intensity"
                    )

            if min_renewable is not None and max_renewable is not None:
                if max_renewable < min_renewable:
                    raise HTTPException(
                        status_code=400,
                        detail="max_renewable must be greater than or equal to min_renewable"
                    )

            data, total_count = self.repository.search(
                region_id=region_id,
                postcode=postcode,
                min_intensity=min_intensity,
                max_intensity=max_intensity,
                intensity_index=intensity_index,
                min_renewable=min_renewable,
                max_renewable=max_renewable,
                skip=skip,
                limit=limit
            )

            data = self._serialize_mongo_data(data)

            return {
                "data": data,
                "total": total_count,
                "skip": skip,
                "limit": limit,
                "filters": {
                    "region_id": region_id,
                    "postcode": postcode,
                    "min_intensity": min_intensity,
                    "max_intensity": max_intensity,
                    "intensity_index": intensity_index,
                    "min_renewable": min_renewable,
                    "max_renewable": max_renewable,
                }
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error searching carbon data: {str(e)}"
            )

    @cached(key_prefix="carbon:regions", ttl=600)
    def get_regions(self) -> List[int]:
        try:
            regions = self.repository.get_distinct_regions()
            return sorted(regions) if regions else []
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving regions: {str(e)}"
            )

    @cached(key_prefix="carbon:postcodes", ttl=600)
    def get_postcodes(self) -> List[str]:
        try:
            postcodes = self.repository.get_distinct_postcodes()
            return sorted(postcodes) if postcodes else []
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving postcodes: {str(e)}"
            )

    def get_shortnames(self) -> List[str]:
        try:
            shortnames = self.repository.get_distinct_shortnames()
            return sorted([s for s in shortnames if s]) if shortnames else []
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving shortnames: {str(e)}"
            )

    def get_intensity_indices(self) -> List[str]:
        try:
            indices = self.repository.get_distinct_intensity_indices()
            return sorted(indices) if indices else []
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving intensity indices: {str(e)}"
            )

    def get_overview_statistics(self) -> Dict[str, Any]:
        try:
            total_records = self.repository.count_all()
            latest = self.repository.find_latest()
            unique_regions = self.repository.get_distinct_regions()
            unique_postcodes = self.repository.get_distinct_postcodes()
            avg_intensity = self.repository.get_average_intensity()
            avg_renewable = self.repository.get_average_renewable_percentage()
            intensity_dist = self.repository.get_intensity_distribution()

            return {
                "total_records": total_records,
                "unique_regions": len(unique_regions) if unique_regions else 0,
                "unique_postcodes": len(unique_postcodes) if unique_postcodes else 0,
                "latest_timestamp": latest.get("from") if latest else None,
                "average_intensity": round(avg_intensity, 2) if avg_intensity else None,
                "average_renewable_percentage": round(avg_renewable, 2) if avg_renewable else None,
                "intensity_distribution": intensity_dist,
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error calculating overview statistics: {str(e)}"
            )

    def create_carbon_record(self, carbon_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if 'intensity_index' in carbon_data and carbon_data['intensity_index']:
                valid_indices = ['low', 'moderate', 'high', 'very high']
                if carbon_data['intensity_index'].lower() not in valid_indices:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid intensity_index. Must be one of: {', '.join(valid_indices)}"
                    )
                carbon_data['intensity_index'] = carbon_data['intensity_index'].lower()

            if 'postcode' in carbon_data and carbon_data['postcode']:
                carbon_data['postcode'] = carbon_data['postcode'].strip().upper()

            if 'renewable_percentage' in carbon_data and carbon_data['renewable_percentage'] is not None:
                if carbon_data['renewable_percentage'] < 0 or carbon_data['renewable_percentage'] > 100:
                    raise HTTPException(
                        status_code=400,
                        detail="renewable_percentage must be between 0 and 100"
                    )

            created = self.repository.create(carbon_data)

            if not created:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create carbon record"
                )

            if '_id' in created:
                created['_id'] = str(created['_id'])

            return created

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating carbon record: {str(e)}"
            )

    def get_carbon_record(self, record_id: str) -> Dict[str, Any]:
        try:
            record = self.repository.get_by_id(record_id)

            if not record:
                raise HTTPException(
                    status_code=404,
                    detail=f"Carbon record with id {record_id} not found"
                )

            if '_id' in record:
                record['_id'] = str(record['_id'])

            return record

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving carbon record: {str(e)}"
            )

    def update_carbon_record(
        self,
        record_id: str,
        carbon_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            if 'intensity_index' in carbon_data and carbon_data['intensity_index']:
                valid_indices = ['low', 'moderate', 'high', 'very high']
                if carbon_data['intensity_index'].lower() not in valid_indices:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid intensity_index. Must be one of: {', '.join(valid_indices)}"
                    )

                carbon_data['intensity_index'] = carbon_data['intensity_index'].lower()

            if 'postcode' in carbon_data and carbon_data['postcode']:
                carbon_data['postcode'] = carbon_data['postcode'].strip().upper()

            if 'renewable_percentage' in carbon_data and carbon_data['renewable_percentage'] is not None:
                if carbon_data['renewable_percentage'] < 0 or carbon_data['renewable_percentage'] > 100:
                    raise HTTPException(
                        status_code=400,
                        detail="renewable_percentage must be between 0 and 100"
                    )

            updated = self.repository.update(record_id, carbon_data)

            if not updated:
                raise HTTPException(
                    status_code=404,
                    detail=f"Carbon record with id {record_id} not found"
                )

            # Serialize and return
            if '_id' in updated:
                updated['_id'] = str(updated['_id'])

            return updated

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error updating carbon record: {str(e)}"
            )

    def delete_carbon_record(self, record_id: str) -> None:
        try:
            success = self.repository.delete(record_id)

            if not success:
                raise HTTPException(
                    status_code=404,
                    detail=f"Carbon record with id {record_id} not found"
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting carbon record: {str(e)}"
            )
